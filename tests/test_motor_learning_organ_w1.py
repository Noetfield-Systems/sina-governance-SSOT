#!/usr/bin/env python3
"""Motor Learning Organ W1 — governance boundary + adversarial tests."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from motor_learning.normalize import normalize_event, normalize_many
from motor_learning.extract import extract_signal
from motor_learning.similarity import compare
from motor_learning.confidence import compute_confidence, RATIFY_THRESHOLD
from motor_learning.lifecycle import (
    transition, OBSERVED, PROPOSED, SHADOW, RATIFIED, REJECTED, ROLLED_BACK,
)
from motor_learning.ecqr import validate_ecqr_decision
from motor_learning.receipt import build_learning_receipt, validate_learning_receipt
from motor_learning.prior_store import PriorStore, store_tree_hash
from motor_learning.orchestrator import run_from_fixture_dir, run_pipeline, rollback_prior
from motor_learning.event_registry import EventRegistry
from motor_learning.errors import IllegalTransition, GovernanceBlock, SchemaError
from motor_learning.shadow import evaluate_shadow

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
        confidence_hash="cafebabe",
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
        e2["outcome"] = "failure"  # same id, different content
        with self.assertRaises(GovernanceBlock):
            normalize_many([e2], event_registry=reg)
        shutil.rmtree(td)

    def test_modified_reuse_cannot_inflate(self):
        """Same event_id with altered content cannot be re-accepted to inflate counts."""
        td = Path(tempfile.mkdtemp())
        reg = EventRegistry(td / "reg.json")
        e1 = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())[0]
        a1, _ = normalize_many([e1], event_registry=reg)
        self.assertEqual(len(a1), 1)
        e2 = dict(e1)
        e2["recovery_path"] = "route_Z"
        with self.assertRaises(GovernanceBlock):
            normalize_many([e2], event_registry=reg)
        shutil.rmtree(td)


class TestLifecycleReceiptNonBypassable(unittest.TestCase):
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
        live = store.search(status="active", live_consumable_only=True)
        self.assertEqual(live, [])
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
        # seed_fixture path uses expected_version None; simulate CAS via _persist governed non-terminal
        with self.assertRaises(GovernanceBlock):
            store.create({**p, "recommended_action": "z", "status": "proposed"}, allow_duplicate=True, expected_version=99)
        shutil.rmtree(td)


class TestECQRFailClosed(unittest.TestCase):
    def test_ratify_requires_shadow_object(self):
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

    def test_shadow_ref_must_bind(self):
        shadow = {"shadow_id": "abc", "content_hash": "hhh", "candidate_id": "c", "result": "success", "evidence_refs": ["e"]}
        conf = {
            "confidence_before": 0.0, "confidence_after": 0.9, "meets_ratify_threshold": True,
            "evidence_ids": ["e"], "algorithm_version": "component_weighted_v1",
        }
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED",
                "candidate_id": "c",
                "reviewer": "test_reviewer:x",
                "rationale": "x",
                "evidence_reviewed": ["e"],
                "shadow_result_ref": "shadow:WRONG",
                "confidence_before": 0.0,
                "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"],
                "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z",
                "policy_versions": {"organ": "X"},
                "algorithm_versions": {"pipeline": "motor_learning_w1_v1", "confidence": "component_weighted_v1"},
            }, shadow=shadow, confidence=conf, candidate={"candidate_id": "c", "evidence_refs": ["e"], "source_event_ids": ["e"]})


class TestReceipt(unittest.TestCase):
    def test_valid(self):
        validate_learning_receipt(_receipt())

    def test_id_consistency(self):
        r = _receipt()
        r["learning_receipt_id"] = "other"
        with self.assertRaises(GovernanceBlock):
            validate_learning_receipt(r)

    def test_rollback_requires_target(self):
        with self.assertRaises(SchemaError):
            _receipt(decision="ROLLED_BACK", rollback_target=None, shadow_id=None, shadow_hash=None, confidence_hash=None)


class TestDryRunImmutability(unittest.TestCase):
    def test_store_hash_unchanged(self):
        td = Path(tempfile.mkdtemp())
        store = td / "store"
        store.mkdir()
        # seed something
        PriorStore(store).seed_fixture({
            "prior_id": "p-pre",
            "status": "proposed",
            "action_attempted": "ci_retry_deploy",
            "recommended_action": "route_B_retry",
            "scope": {"loop_id": "motor_learning_organ_v1"},
        })
        before = store_tree_hash(store)
        run_from_fixture_dir(
            FIX / "01_repeated_success_ratify",
            out_dir=td / "out",
            store_dir=store,
            dry_run=True,
        )
        after = store_tree_hash(store)
        self.assertEqual(before, after)
        shutil.rmtree(td)


class TestPipeline(unittest.TestCase):
    def test_01_ratify_dry_run(self):
        td = Path(tempfile.mkdtemp())
        before = store_tree_hash(td / "store") if (td / "store").exists() else store_tree_hash(td / "store")
        (td / "store").mkdir(exist_ok=True)
        before = store_tree_hash(td / "store")
        summary = run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "RATIFIED")
        self.assertTrue(summary["store_unchanged"])
        self.assertEqual(store_tree_hash(td / "store"), before)
        self.assertTrue(list((td / "out").glob("learning_receipt-*.json")))
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
        self.assertNotEqual(summary.get("ecqr_decision"), "REJECTED")  # not rewritten
        shutil.rmtree(td)

    def test_05_expired(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "05_expired_prior", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        # expired seed should not force duplicate veto; may ratify
        self.assertIn(summary.get("ecqr_decision"), ("RATIFIED", None))
        if summary.get("blocked_reason") == "DUPLICATE_CONFLICT_REVIEW_REQUIRED":
            self.fail("expired prior must not act as active conflict")
        self.assertEqual(summary.get("ecqr_decision"), "RATIFIED")
        shutil.rmtree(td)

    def test_06_reject(self):
        td = Path(tempfile.mkdtemp())
        summary = run_from_fixture_dir(FIX / "06_rejected_candidate", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "REJECTED")
        self.assertIsNotNone(summary["receipt_id"])
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
        self.assertIn("shadow_mining_event_overlap", summary.get("blocked_reason") or "")
        self.assertIsNone(summary.get("receipt_id"))
        shutil.rmtree(td)

    def test_failed_transition_no_orphan_receipt_in_store(self):
        """Failed terminal leave no store mutation; out_dir may be cleaned on rollback failure."""
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td / "store")
        store.seed_fixture({
            "prior_id": "prior-to-rollback",
            "status": "proposed",  # wrong state → rollback fails
            "action_attempted": "x",
            "recommended_action": "y",
            "scope": {"loop_id": "motor_learning_organ_v1", "runway": "Software Repair"},
        })
        before = store_tree_hash(td / "store")
        ecqr = json.loads((FIX / "07_rollback" / "ecqr_decision.json").read_text())
        with self.assertRaises(GovernanceBlock):
            rollback_prior(
                prior_id="prior-to-rollback",
                store_dir=td / "store",
                out_dir=td / "out",
                ecqr_decision=ecqr,
                regression_evidence=["e1"],
                dry_run=True,
            )
        self.assertEqual(store_tree_hash(td / "store"), before)
        # no leftover receipts after failed rollback
        self.assertEqual(list((td / "out").glob("learning_receipt-*.json")), [])
        shutil.rmtree(td)


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
            shadow_report={"success_rate": 1.0, "result": "success", "successes": 5, "failures": 0, "total": 5},
            scope={"loop_id": "x", "runway": "y", "repository": "z"},
            mining_evidence_ids=["a", "b"],
            shadow_evidence_ids=["a", "c"],
        )
        self.assertTrue(c["shadow_contaminated_by_mining_overlap"])
        self.assertFalse(c["meets_ratify_threshold"])



class TestPersistGate(unittest.TestCase):
    def test_no_dry_run_requires_allow_persist(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "motor_learning_organ_w1_run",
            ROOT / "scripts" / "motor_learning_organ_w1_run.py",
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with self.assertRaises(GovernanceBlock):
            mod._assert_persist_allowed(Path("/tmp/mlo-store"), False)
        mod._assert_persist_allowed(Path("/tmp/mlo-store"), True)
        with self.assertRaises(GovernanceBlock):
            mod._assert_persist_allowed(Path("/tmp/production/priors"), True)


if __name__ == "__main__":
    unittest.main()
