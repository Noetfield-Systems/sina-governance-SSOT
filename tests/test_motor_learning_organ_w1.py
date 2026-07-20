#!/usr/bin/env python3
"""Motor Learning Organ W1 — governance boundary + adversarial tests."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from motor_learning.normalize import normalize_event, normalize_many
from motor_learning.extract import extract_signal
from motor_learning.similarity import compare
from motor_learning.confidence import compute_confidence
from motor_learning.lifecycle import (
    transition, OBSERVED, PROPOSED, SHADOW, RATIFIED, REJECTED, ROLLED_BACK,
)
from motor_learning.ecqr import validate_ecqr_decision, fixture_compile_ecqr
from motor_learning.receipt import build_learning_receipt, validate_learning_receipt, derive_receipt_id
from motor_learning.prior_store import PriorStore, store_tree_hash, live_consumable_for_status
from motor_learning.orchestrator import run_from_fixture_dir, run_pipeline, rollback_prior
from motor_learning.event_registry import EventRegistry
from motor_learning.errors import IllegalTransition, GovernanceBlock, SchemaError, MotorLearningError
from motor_learning.shadow import evaluate_shadow, assert_shadow_independence
from motor_learning.validated import mint_w1_reference_store_capability, ValidatedECQR
from motor_learning.hashutil import content_hash

FIX = ROOT / "fixtures" / "motor_learning_w1"


def _receipt(**over):
    base = dict(
        decision="RATIFIED",
        prior_id="p1",
        candidate_id="c1",
        reviewer="test_reviewer:x",
        rationale="because evidence",
        evidence_links=["e1"],
        confidence_before=0.2,
        confidence_after=0.8,
        affected_loops=["motor_learning_organ_v1"],
        applicable_runways=["Software Repair"],
        repositories=["sina-governance-SSOT"],
        origin_event="evt-001",
        decision_timestamp="2026-07-10T12:00:00Z",
        shadow_id="shadow-abc",
        shadow_hash="deadbeef",
        shadow_evidence_manifest_hash="manifestbeef",
        confidence_hash="cafebabe",
        ecqr_decision_hash="ecqrhash",
        candidate_hash="candhash",
    )
    base.update(over)
    return build_learning_receipt(**base)


class TestNormalize(unittest.TestCase):
    def test_rejects_malformed(self):
        with self.assertRaises(SchemaError):
            normalize_event({"event_id": "x"})

    def test_duplicate_idempotent(self):
        events = json.loads((FIX / "10_duplicate_event" / "events.json").read_text())
        td = Path(tempfile.mkdtemp())
        reg = EventRegistry(td / "reg.json")
        accepted, dups = normalize_many(events, event_registry=reg)
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(accepted), 3)
        shutil.rmtree(td)

    def test_identity_collision_hard_fail(self):
        td = Path(tempfile.mkdtemp())
        reg = EventRegistry(td / "reg.json")
        e1 = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())[0]
        normalize_many([e1], event_registry=reg)
        e2 = dict(e1)
        e2["outcome"] = "failure"
        with self.assertRaises(GovernanceBlock):
            normalize_many([e2], event_registry=reg)
        shutil.rmtree(td)

    def test_K_provenance_collision_evidence_refs(self):
        td = Path(tempfile.mkdtemp())
        ledger = td / "ledger.json"
        reg = EventRegistry(ledger)
        e1 = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())[0]
        normalize_many([e1], event_registry=reg)
        e2 = dict(e1)
        e2["evidence_refs"] = ["receipts/other/changed.json"]
        with self.assertRaises(GovernanceBlock):
            normalize_many([e2], event_registry=reg)
        # Cross-invocation via durable ledger
        reg2 = EventRegistry(ledger)
        e3 = dict(e1)
        e3["raw_evidence_ref"] = "raw://changed"
        with self.assertRaises(GovernanceBlock):
            normalize_many([e3], event_registry=reg2)
        e4 = dict(e1)
        e4["actor"] = "different_actor"
        with self.assertRaises(GovernanceBlock):
            normalize_many([e4], event_registry=EventRegistry(ledger))
        e5 = dict(e1)
        e5["provider"] = "different_provider"
        with self.assertRaises(GovernanceBlock):
            normalize_many([e5], event_registry=EventRegistry(ledger))
        shutil.rmtree(td)


class TestLifecycleReceiptNonBypassable(unittest.TestCase):
    def test_A_fake_receipt_id_alone_cannot_transition(self):
        e = transition({"state": PROPOSED, "evidence_refs": ["e"]}, SHADOW, actor="t", reason="shadow")
        with self.assertRaises(GovernanceBlock):
            transition(
                e, RATIFIED,
                actor="t", reason="ratify",
                learning_receipt_id="fake-unvalidated-id",
            )

    def test_require_receipt_false_cannot_ratify(self):
        e = transition({"state": PROPOSED, "evidence_refs": ["e"]}, SHADOW, actor="t", reason="shadow")
        with self.assertRaises(GovernanceBlock):
            transition(e, RATIFIED, actor="t", reason="ratify", require_receipt=False)

    def test_ratify_with_validated_receipt(self):
        e = transition({"state": PROPOSED, "evidence_refs": ["e"]}, SHADOW, actor="t", reason="shadow")
        r = _receipt()
        e = transition(e, RATIFIED, actor="t", reason="ok", learning_receipt=r, evidence=["e"])
        self.assertEqual(e["state"], RATIFIED)

    def test_illegal_observed_to_ratified(self):
        with self.assertRaises(IllegalTransition):
            transition({"state": OBSERVED}, RATIFIED, actor="t", reason="nope", learning_receipt=_receipt())


class TestPriorStoreGovernance(unittest.TestCase):
    def test_direct_create_active_fails(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td)
        with self.assertRaises(GovernanceBlock):
            store.create({
                "prior_id": "p-hack",
                "status": "active",
                "action_attempted": "x",
                "recommended_action": "y",
                "scope": {"loop_id": "motor_learning_organ_v1"},
            })
        shutil.rmtree(td)

    def test_B_forged_artifacts_bound_cannot_persist(self):
        td = Path(tempfile.mkdtemp())
        cap = mint_w1_reference_store_capability()
        store = PriorStore(td, store_capability=cap, allow_persist=True)
        forged = {
            "decision": "RATIFIED",
            "candidate_id": "c",
            "reviewer": "test_reviewer:x",
            "rationale": "x",
            "evidence_reviewed": ["e"],
            "shadow_result_ref": "shadow:x",
            "confidence_before": 0.9,
            "confidence_after": 0.9,
            "affected_loops": ["motor_learning_organ_v1"],
            "applicable_runways": ["Software Repair"],
            "effective_at": "2026-07-10T12:00:00Z",
            "policy_versions": {"organ": "X"},
            "_artifacts_bound": True,
        }
        with self.assertRaises(GovernanceBlock):
            store.create({
                "prior_id": "p-forge",
                "status": "active",
                "action_attempted": "x",
                "recommended_action": "y",
                "scope": {"loop_id": "motor_learning_organ_v1"},
                "candidate_id": "c",
                "transition_history": [{"to_state": "RATIFIED", "learning_receipt_id": "lr-x"}],
            }, ecqr_decision=forged, learning_receipt=_receipt(prior_id="p-forge", candidate_id="c"))
        shutil.rmtree(td)

    def test_C_D_live_consumable_matrix(self):
        for status in ("active", "rejected", "rolled_back", "expired", "superseded", "shadow", "proposed"):
            self.assertFalse(live_consumable_for_status(status))
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td)
        for status, allow_term in (
            ("rejected", True),
            ("rolled_back", True),
            ("expired", False),
            ("superseded", False),
            ("active", True),
        ):
            p = store.seed_fixture({
                "prior_id": f"p-{status}",
                "status": status if status != "expired" else "expired",
                "action_attempted": "x",
                "recommended_action": "y",
                "scope": {"loop_id": "motor_learning_organ_v1"},
            }, allow_terminal_seed=allow_term or status in ("expired", "superseded"))
            self.assertFalse(p["live_consumable"], status)
        live = store.search(live_consumable_only=True)
        self.assertEqual(live, [])
        shutil.rmtree(td)

    def test_seed_fixture_tagged_not_consumable(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td)
        with self.assertRaises(GovernanceBlock):
            store.seed_fixture({
                "prior_id": "p-seed-blocked",
                "status": "active",
                "action_attempted": "x",
                "recommended_action": "y",
                "scope": {"loop_id": "motor_learning_organ_v1"},
            })
        p = store.seed_fixture({
            "prior_id": "p-seed",
            "status": "active",
            "action_attempted": "x",
            "recommended_action": "y",
            "scope": {"loop_id": "motor_learning_organ_v1"},
            "fingerprint": {"action_attempted": "x", "outcome": "success"},
        }, allow_terminal_seed=True)
        self.assertTrue(p["fixture_seeded"])
        self.assertFalse(p["live_consumable"])
        shutil.rmtree(td)

    def test_L_test_reviewer_no_activation_authority(self):
        """W1 ratified reference from test_reviewer is never activatable."""
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(
            FIX / "01_repeated_success_ratify",
            out_dir=td / "out", store_dir=td / "store", dry_run=True,
        )
        self.assertEqual(summary["ecqr_decision"], "RATIFIED")
        preview = json.loads((td / "out" / "prior.dry_run_preview.json").read_text())
        self.assertFalse(preview["live_consumable"])
        self.assertFalse(preview.get("activation_authority", True) if "activation_authority" in preview else False)
        self.assertFalse(preview["live_consumable"])
        bundle = json.loads((td / "out" / "reference_bundle.json").read_text())
        self.assertFalse(bundle["live_consumable"])
        shutil.rmtree(td)

    def test_expiry_as_of(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td)
        store.seed_fixture({
            "prior_id": "p-exp",
            "status": "active",
            "expires_at": "2026-01-01T00:00:00Z",
            "action_attempted": "ci_retry_deploy",
            "recommended_action": "route_B_retry",
            "scope": {"loop_id": "motor_learning_organ_v1", "runway": "Software Repair", "repository": "sina-governance-SSOT"},
            "fingerprint": {"action_attempted": "ci_retry_deploy", "outcome": "success"},
        }, allow_terminal_seed=True)
        active = store.search(status="active", as_of="2026-07-01T00:00:00Z")
        self.assertEqual(active, [])
        expired = store.search(status="expired", include_expired=True, as_of="2026-07-01T00:00:00Z")
        self.assertEqual(len(expired), 1)
        shutil.rmtree(td)

    def test_cas_version(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td)
        p = store.seed_fixture({
            "prior_id": "p-cas",
            "status": "proposed",
            "action_attempted": "x",
            "recommended_action": "y",
            "scope": {"loop_id": "l"},
        })
        self.assertEqual(p["version"], 1)
        with self.assertRaises(GovernanceBlock):
            store.create({**p, "recommended_action": "z", "status": "proposed"}, allow_duplicate=True, expected_version=99)
        shutil.rmtree(td)


class TestECQRImmutability(unittest.TestCase):
    def test_E_wrong_candidate_id_fails(self):
        shadow = {
            "shadow_id": "abc", "content_hash": "hhh", "candidate_id": "c", "result": "success",
            "ratifiable": True, "evidence_refs": ["e"], "shadow_event_ids": ["s1"],
            "evidence_manifest_hash": "mh",
        }
        conf = {
            "confidence_before": 0.0, "confidence_after": 0.9, "meets_ratify_threshold": True,
            "evidence_ids": ["e"], "algorithm_version": "component_weighted_v1", "content_hash": "ch",
        }
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED",
                "candidate_id": "WRONG",
                "reviewer": "test_reviewer:x",
                "rationale": "x",
                "evidence_reviewed": ["e", "s1"],
                "shadow_result_ref": "shadow:abc",
                "shadow_hash": "hhh",
                "confidence_before": 0.0,
                "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"],
                "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z",
                "policy_versions": {"organ": "X"},
                "algorithm_versions": {"pipeline": "motor_learning_w1_v1", "confidence": "component_weighted_v1"},
            }, shadow=shadow, confidence=conf, candidate={"candidate_id": "c", "evidence_refs": ["e"], "source_event_ids": ["e"]})

    def test_E_wrong_shadow_hash_fails(self):
        shadow = {
            "shadow_id": "abc", "content_hash": "hhh", "candidate_id": "c", "result": "success",
            "ratifiable": True, "evidence_refs": ["e"], "shadow_event_ids": ["s1"],
            "evidence_manifest_hash": "mh",
        }
        conf = {
            "confidence_before": 0.0, "confidence_after": 0.9, "meets_ratify_threshold": True,
            "evidence_ids": ["e"], "content_hash": "ch",
        }
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED", "candidate_id": "c", "reviewer": "test_reviewer:x",
                "rationale": "x", "evidence_reviewed": ["e", "s1"],
                "shadow_result_ref": "shadow:abc", "shadow_hash": "WRONG",
                "confidence_before": 0.0, "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"], "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z", "policy_versions": {"organ": "X"},
                "algorithm_versions": {"pipeline": "motor_learning_w1_v1", "confidence": "component_weighted_v1"},
            }, shadow=shadow, confidence=conf, candidate={"candidate_id": "c", "evidence_refs": ["e"], "source_event_ids": ["e"]})

    def test_E_wrong_confidence_fails(self):
        shadow = {
            "shadow_id": "abc", "content_hash": "hhh", "candidate_id": "c", "result": "success",
            "ratifiable": True, "evidence_refs": ["e"], "shadow_event_ids": ["s1"],
            "evidence_manifest_hash": "mh",
        }
        conf = {
            "confidence_before": 0.0, "confidence_after": 0.9, "meets_ratify_threshold": True,
            "evidence_ids": ["e"], "content_hash": "ch",
        }
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED", "candidate_id": "c", "reviewer": "test_reviewer:x",
                "rationale": "x", "evidence_reviewed": ["e", "s1"],
                "shadow_result_ref": "shadow:abc", "shadow_hash": "hhh",
                "confidence_before": 0.0, "confidence_after": 0.5,
                "affected_loops": ["motor_learning_organ_v1"], "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z", "policy_versions": {"organ": "X"},
                "algorithm_versions": {"pipeline": "motor_learning_w1_v1", "confidence": "component_weighted_v1"},
            }, shadow=shadow, confidence=conf, candidate={"candidate_id": "c", "evidence_refs": ["e"], "source_event_ids": ["e"]})

    def test_E_missing_manifest_fails(self):
        shadow = {
            "shadow_id": "abc", "content_hash": "hhh", "candidate_id": "c", "result": "success",
            "ratifiable": True, "evidence_refs": ["e"], "shadow_event_ids": ["s1"],
        }
        conf = {
            "confidence_before": 0.0, "confidence_after": 0.9, "meets_ratify_threshold": True,
            "evidence_ids": ["e"], "content_hash": "ch",
        }
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED", "candidate_id": "c", "reviewer": "test_reviewer:x",
                "rationale": "x", "evidence_reviewed": ["e", "s1"],
                "shadow_result_ref": "shadow:abc", "shadow_hash": "hhh",
                "confidence_before": 0.0, "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"], "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z", "policy_versions": {"organ": "X"},
                "algorithm_versions": {"pipeline": "motor_learning_w1_v1", "confidence": "component_weighted_v1"},
            }, shadow=shadow, confidence=conf, candidate={"candidate_id": "c", "evidence_refs": ["e"], "source_event_ids": ["e"]})

    def test_E_fixture_byte_unchanged(self):
        td = Path(tempfile.mkdtemp())
        ecqr_path = FIX / "01_repeated_success_ratify" / "ecqr_decision.json"
        before = ecqr_path.read_bytes()
        run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        after = ecqr_path.read_bytes()
        self.assertEqual(before, after)
        shutil.rmtree(td)

    def test_validate_returns_opaque(self):
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED",
                "candidate_id": "c",
                "reviewer": "test_reviewer:x",
                "rationale": "x",
                "evidence_reviewed": ["e"],
                "shadow_result_ref": "shadow:foo",
                "confidence_before": 0.9,
                "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"],
                "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z",
                "policy_versions": {"organ": "NF-MOTOR-LEARNING-ORGAN-V1"},
            }, shadow=None, confidence={"confidence_before": 0.9, "confidence_after": 0.9, "meets_ratify_threshold": True})


class TestShadowIndependence(unittest.TestCase):
    def test_F_renamed_clones_rejected(self):
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        mine = [normalize_event(e) for e in events]
        clones = []
        for e in mine:
            c = dict(e)
            c["event_id"] = "shadow-" + e["event_id"]
            clones.append(c)
        cand = {"source_event_ids": [e["event_id"] for e in mine], "evidence_refs": mine[0]["evidence_refs"]}
        with self.assertRaises(GovernanceBlock):
            assert_shadow_independence(candidate=cand, mining_events=mine, shadow_events=clones)

    def test_F_same_evidence_refs_new_ids_rejected(self):
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        mine = [normalize_event(e) for e in events]
        shadow = []
        for e in mine:
            s = dict(e)
            s["event_id"] = "shadow-" + e["event_id"]
            s["raw_evidence_ref"] = "raw://shadow/" + e["event_id"]
            # keep same evidence_refs → must fail
            shadow.append(s)
        cand = {"source_event_ids": [e["event_id"] for e in mine], "evidence_refs": [r for e in mine for r in e["evidence_refs"]]}
        with self.assertRaises(GovernanceBlock):
            assert_shadow_independence(candidate=cand, mining_events=mine, shadow_events=shadow)

    def test_G_missing_shadow_blocks(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        ecqr = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_decision.json").read_text())
        summary = run_pipeline(
            events=events, shadow_events=None, store_dir=td / "store", out_dir=td / "out",
            ecqr_decision=ecqr, dry_run=True,
        )
        self.assertEqual(summary.get("blocked_reason"), "shadow_events_required")
        self.assertIsNone(summary.get("receipt_id"))
        shutil.rmtree(td)

    def test_one_success_many_abstentions_not_ratifiable(self):
        cand = {
            "candidate_id": "c",
            "fingerprint": {"action_attempted": "ci_retry_deploy", "error_class": "cloudflare_timeout"},
            "recommended_action": "route_B_retry",
            "evidence_refs": ["mine/1"],
        }
        events = [
            {"event_id": "s1", "action_attempted": "ci_retry_deploy", "error_class": "cloudflare_timeout",
             "recovery_path": "route_B_retry", "outcome": "success", "evidence_refs": ["sh/1"], "content_hash": "h1"},
            {"event_id": "s2", "action_attempted": "other", "outcome": "success", "evidence_refs": ["sh/2"], "content_hash": "h2"},
            {"event_id": "s3", "action_attempted": "other", "outcome": "success", "evidence_refs": ["sh/3"], "content_hash": "h3"},
            {"event_id": "s4", "action_attempted": "other", "outcome": "success", "evidence_refs": ["sh/4"], "content_hash": "h4"},
        ]
        report = evaluate_shadow(cand, events)
        self.assertFalse(report["ratifiable"])
        self.assertEqual(report["successes"], 1)


class TestReceiptIdentity(unittest.TestCase):
    def test_J_content_changes_receipt_id(self):
        base = _receipt()
        e1 = _receipt(evidence_links=["e1", "e2"])
        c1 = _receipt(confidence_after=0.81)
        s1 = _receipt(shadow_hash="otherhash")
        self.assertNotEqual(base["receipt_id"], e1["receipt_id"])
        self.assertNotEqual(base["receipt_id"], c1["receipt_id"])
        self.assertNotEqual(base["receipt_id"], s1["receipt_id"])
        # collision: same id different body rejected
        body = dict(base)
        body["rationale"] = "changed rationale"
        body["why_accepted_or_rejected"] = "changed rationale"
        # keep old id → validate fails
        with self.assertRaises(GovernanceBlock):
            validate_learning_receipt(body)

    def test_missing_confidence_hash_blocks(self):
        with self.assertRaises(SchemaError):
            build_learning_receipt(
                decision="RATIFIED", prior_id="p", candidate_id="c", reviewer="test_reviewer:x",
                rationale="r", evidence_links=["e"], confidence_before=0.1, confidence_after=0.9,
                affected_loops=["motor_learning_organ_v1"], applicable_runways=["Software Repair"],
                origin_event="e", decision_timestamp="2026-07-10T12:00:00Z",
                shadow_id="s", shadow_hash="h", shadow_evidence_manifest_hash="m",
                confidence_hash=None, ecqr_decision_hash="e", candidate_hash="c",
            )


class TestDryRunImmutability(unittest.TestCase):
    def test_store_hash_unchanged(self):
        td = Path(tempfile.mkdtemp())
        store = td / "store"
        store.mkdir()
        PriorStore(store).seed_fixture({
            "prior_id": "p-pre",
            "status": "proposed",
            "action_attempted": "ci_retry_deploy",
            "recommended_action": "route_B_retry",
            "scope": {"loop_id": "motor_learning_organ_v1"},
        })
        before = store_tree_hash(store)
        run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=store, dry_run=True)
        after = store_tree_hash(store)
        self.assertEqual(before, after)
        shutil.rmtree(td)


class TestPipeline(unittest.TestCase):
    def test_01_ratify_dry_run(self):
        td = Path(tempfile.mkdtemp())
        (td / "store").mkdir(exist_ok=True)
        before = store_tree_hash(td / "store")
        summary = run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "RATIFIED")
        self.assertTrue(summary["store_unchanged"])
        self.assertEqual(store_tree_hash(td / "store"), before)
        self.assertTrue(list((td / "out").glob("learning_receipt-*.json")))
        preview = json.loads((td / "out" / "prior.dry_run_preview.json").read_text())
        self.assertFalse(preview["live_consumable"])
        shutil.rmtree(td)

    def test_02_insufficient(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "02_insufficient_evidence", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertIsNone(summary["receipt_id"])
        shutil.rmtree(td)

    def test_03_contradiction(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "03_contradictory_evidence", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertNotEqual(summary.get("ecqr_decision"), "RATIFIED")
        shutil.rmtree(td)

    def test_04_near_duplicate_preserves_reviewer_decision(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "04_near_duplicate_prior", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary.get("blocked_reason"), "DUPLICATE_CONFLICT_REVIEW_REQUIRED")
        self.assertEqual(summary.get("reviewer_decision_preserved"), "RATIFIED")
        self.assertIsNotNone(summary.get("machine_policy_veto"))
        self.assertNotEqual(summary.get("ecqr_decision"), "REJECTED")
        shutil.rmtree(td)

    def test_05_expired(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "05_expired_prior", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        if summary.get("blocked_reason") == "DUPLICATE_CONFLICT_REVIEW_REQUIRED":
            self.fail("expired prior must not act as active conflict")
        self.assertEqual(summary.get("ecqr_decision"), "RATIFIED")
        shutil.rmtree(td)

    def test_06_reject(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "06_rejected_candidate", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "REJECTED")
        self.assertIsNotNone(summary["receipt_id"])
        preview = json.loads((td / "out" / "prior.dry_run_preview.json").read_text())
        self.assertFalse(preview["live_consumable"])
        shutil.rmtree(td)

    def test_07_rollback_e2e(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "07_rollback", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary["final_state"], ROLLED_BACK)
        self.assertIsNotNone(summary["receipt_id"])
        self.assertTrue(summary["store_unchanged"])
        shutil.rmtree(td)

    def test_08_shadow_overlap_blocks(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "08_shadow_overlap_blocked", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertTrue(
            "overlap" in (summary.get("blocked_reason") or "")
            or "shadow_mining" in (summary.get("blocked_reason") or "")
        )
        self.assertIsNone(summary.get("receipt_id"))
        shutil.rmtree(td)


class TestPersistGate(unittest.TestCase):
    def test_I_programmatic_persist_requires_capability(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        ecqr = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_decision.json").read_text())
        with self.assertRaises(GovernanceBlock):
            run_pipeline(
                events=events, shadow_events=shadow, store_dir=td / "any-non-blacklisted-path",
                out_dir=td / "out", ecqr_decision=ecqr, dry_run=False,
            )
        # With capability: still live_consumable=false
        cap = mint_w1_reference_store_capability()
        summary = run_pipeline(
            events=events, shadow_events=shadow, store_dir=td / "refstore",
            out_dir=td / "out2", ecqr_decision=ecqr, dry_run=False,
            store_capability=cap, allow_store_persist=True,
        )
        self.assertEqual(summary.get("ecqr_decision"), "RATIFIED")
        prior = json.loads((td / "out2" / "prior.json").read_text())
        self.assertFalse(prior["live_consumable"])
        stored = PriorStore(td / "refstore").get(prior["prior_id"])
        self.assertIsNotNone(stored)
        self.assertFalse(stored["live_consumable"])
        shutil.rmtree(td)


class TestAtomicCommit(unittest.TestCase):
    def _run_inject(self, stage: str):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        ecqr = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_decision.json").read_text())
        store = td / "store"
        store.mkdir()
        before = store_tree_hash(store)
        cap = mint_w1_reference_store_capability()
        with self.assertRaises(MotorLearningError):
            run_pipeline(
                events=events, shadow_events=shadow, store_dir=store, out_dir=td / "out",
                ecqr_decision=ecqr, dry_run=False, store_capability=cap, allow_store_persist=True,
                inject_failure_after=stage,
            )
        after = store_tree_hash(store)
        self.assertEqual(before, after, stage)
        self.assertEqual(list((td / "out").glob("learning_receipt-*.json")), [])
        self.assertTrue(list((td / "out").glob("failed_attempt-*.json")))
        # CLI nonzero
        proc = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "motor_learning_organ_w1_run.py"),
                "--events", str(FIX / "01_repeated_success_ratify" / "events.json"),
                "--shadow-events", str(FIX / "01_repeated_success_ratify" / "shadow_events.json"),
                "--ecqr", str(FIX / "01_repeated_success_ratify" / "ecqr_decision.json"),
                "--out", str(td / "cli-out"),
                "--store", str(td / "cli-store"),
                "--no-dry-run", "--allow-store-persist",
                "--inject-failure-after", stage,
            ],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        out = json.loads(proc.stdout)
        self.assertFalse(out.get("ok"))
        shutil.rmtree(td)
        return before, after, proc.returncode

    def test_H_inject_after_receipt_staging(self):
        self._run_inject("receipt_staging")

    def test_H_inject_after_prior_staging(self):
        self._run_inject("prior_staging")

    def test_H_inject_before_index_commit(self):
        self._run_inject("before_index_commit")


class TestSimilarityConfidence(unittest.TestCase):
    def test_exact_and_no_promo(self):
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        sig = extract_signal(normalize_event(events[0]))
        prior = {"prior_id": "p1", "fingerprint": dict(sig["fingerprint"]), "scope": sig["scope"]}
        r = compare(sig, prior)
        self.assertFalse(r["promotion_authority"])
        self.assertGreaterEqual(r["total_score"], 0.9)

    def test_confidence_overlap_blocks_threshold(self):
        c = compute_confidence(
            occurrence_count=5, outcomes_seen=["success"], evidence_refs=["a"],
            shadow_report={"success_rate": 1.0, "result": "success", "successes": 5, "failures": 0, "total": 5, "evaluated": 5, "ratifiable": True},
            scope={"loop_id": "x", "runway": "y", "repository": "z"},
            mining_evidence_ids=["a", "b"],
            shadow_evidence_ids=["a", "c"],
        )
        self.assertTrue(c["shadow_contaminated_by_mining_overlap"])
        self.assertFalse(c["meets_ratify_threshold"])


class TestScopeGuard(unittest.TestCase):
    def test_M_landing_site_unchanged_in_diff(self):
        r = subprocess.run(
            ["git", "diff", "--name-only", "origin/main...HEAD"],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        if r.returncode != 0:
            mb = subprocess.run(
                ["git", "merge-base", "HEAD", "origin/main"],
                cwd=str(ROOT), capture_output=True, text=True,
            )
            if mb.returncode != 0:
                self.skipTest("no merge-base with origin/main")
            r = subprocess.run(
                ["git", "diff", "--name-only", f"{mb.stdout.strip()}...HEAD"],
                cwd=str(ROOT), capture_output=True, text=True,
            )
        for line in r.stdout.splitlines():
            self.assertFalse(line.startswith("landing-site/"), line)


if __name__ == "__main__":
    unittest.main()
