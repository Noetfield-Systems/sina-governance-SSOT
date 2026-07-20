#!/usr/bin/env python3
"""Motor Learning Organ W1 — governance boundary + adversarial probes A–Q."""
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
from motor_learning.ecqr import validate_ecqr_decision, fixture_compile_ecqr, is_ecqr_template
from motor_learning.receipt import build_learning_receipt, validate_learning_receipt, validate_and_mint_receipt
from motor_learning.prior_store import PriorStore, store_tree_hash, live_consumable_for_status
from motor_learning.orchestrator import run_from_fixture_dir, run_pipeline, rollback_prior, observe_phase
from motor_learning.event_registry import EventRegistry
from motor_learning.errors import IllegalTransition, GovernanceBlock, SchemaError, MotorLearningError
from motor_learning.shadow import evaluate_shadow, assert_shadow_independence
from motor_learning.validated import ValidatedReceipt, ValidatedECQR
from motor_learning.artifacts import validate_shadow_report, validate_confidence_artifact
from motor_learning.paths import assert_paths_disjoint
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


class TestFabricatedWrappers(unittest.TestCase):
    def test_A_fabricated_validated_receipt_blocked(self):
        """Public/internal construction of wrapper around invalid body fails at transition."""
        fake = ValidatedReceipt(
            receipt_id="lr-fake",
            payload={
                "receipt_id": "lr-fake",
                "learning_receipt_id": "lr-fake",
                "decision": "accepted",
                "decision_timestamp": "2026-07-10T12:00:00Z",
                "prior_id": "p1",
                "candidate_id": "c1",
                "evidence_links": ["e1"],
                "confidence_before": 0.2,
                "confidence_after": 0.8,
                "reviewer": "test_reviewer:x",
                "rationale": "x",
                "why_accepted_or_rejected": "x",
                "affected_loops": ["motor_learning_organ_v1"],
                "applicable_runways": ["Software Repair"],
                "repositories": [],
                "expiry": None,
                "supersedes": None,
                "schema_versions": {},
                "algorithm_versions": {},
                "integrity_hash": "not-valid",
                "origin_event": "e",
                "ratified_at": "2026-07-10T12:00:00Z",
                "snapshot_id": "p1",
                "shadow_id": "s",
                "shadow_hash": "invented",
                "shadow_evidence_manifest_hash": "invented",
                "confidence_hash": "invented",
                "ecqr_decision_hash": "invented",
                "candidate_hash": "invented",
            },
            integrity_hash="not-valid",
        )
        e = transition({"state": PROPOSED, "evidence_refs": ["e"]}, SHADOW, actor="t", reason="shadow")
        with self.assertRaises(GovernanceBlock):
            transition(e, RATIFIED, actor="t", reason="ratify", learning_receipt=fake)

    def test_B_fabricated_validated_ecqr_blocked(self):
        fake = ValidatedECQR(
            decision="RATIFIED",
            payload={
                "decision": "RATIFIED",
                "candidate_id": "c",
                "reviewer": "test_reviewer:x",
                "rationale": "x",
                "evidence_reviewed": ["e"],
                "shadow_result_ref": "shadow:x",
                "shadow_hash": "not-real",
                "shadow_evidence_manifest_hash": "not-real",
                "confidence_before": 0.9,
                "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"],
                "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z",
                "policy_versions": {"organ": "X"},
                "algorithm_versions": {"pipeline": "motor_learning_w1_v1", "confidence": "component_weighted_v1"},
            },
            decision_hash="fake",
        )
        with self.assertRaises((GovernanceBlock, SchemaError)):
            validate_ecqr_decision(
                fake,
                shadow={
                    "schema": "nf_motor_learning_shadow_report_v1",
                    "shadow_id": "x", "candidate_id": "c", "successes": 3, "failures": 0,
                    "abstentions": 0, "total": 3, "evaluated": 3, "coverage": 1.0,
                    "success_rate": 1.0, "result": "success", "ratifiable": True,
                    "details": [], "shadow_event_ids": ["s1", "s2", "s3"],
                    "evidence_refs": ["e"], "evidence_manifest": {},
                    "evidence_manifest_hash": "mh", "content_hash": "not-a-real-shadow-hash",
                    "production_change": False,
                },
                confidence={
                    "schema": "nf_motor_learning_confidence_v1",
                    "algorithm_version": "component_weighted_v1",
                    "confidence_before": 0.0, "confidence_after": 0.99,
                    "component_contributions": {"x": {"value": 1, "weight": 1, "contribution": 0.99}},
                    "threshold_references": {"ratify_min": 0.7},
                    "meets_ratify_threshold": True,
                    "evidence_ids": ["e"], "mining_evidence_ids": ["e"], "shadow_evidence_ids": ["s1"],
                    "content_hash": "not-a-real-confidence-hash",
                },
                candidate={"candidate_id": "c", "fingerprint": {}, "recommended_action": "r",
                           "source_event_ids": ["e"], "evidence_refs": ["e"]},
            )


class TestSyntheticArtifacts(unittest.TestCase):
    def test_C_synthetic_shadow_blocked(self):
        with self.assertRaises(GovernanceBlock):
            validate_shadow_report({
                "schema": "nf_motor_learning_shadow_report_v1",
                "shadow_id": "x", "candidate_id": "c", "successes": 3, "failures": 0,
                "abstentions": 0, "total": 3, "evaluated": 3, "coverage": 1.0,
                "success_rate": 1.0, "result": "success", "ratifiable": True,
                "details": [], "shadow_event_ids": ["s1", "s2", "s3"],
                "evidence_refs": ["e"], "evidence_manifest": {
                    "shadow_event_ids": ["s1", "s2", "s3"], "evidence_refs": ["e"],
                    "normalized_event_hashes": [], "successes": 3, "failures": 0,
                    "abstentions": 0, "evaluated": 3, "coverage": 1.0, "success_rate": 1.0,
                },
                "evidence_manifest_hash": "wrong",
                "content_hash": "not-a-real-shadow-hash",
                "production_change": False,
            })

    def test_D_synthetic_confidence_blocked(self):
        with self.assertRaises(GovernanceBlock):
            validate_confidence_artifact({
                "schema": "nf_motor_learning_confidence_v1",
                "algorithm_version": "component_weighted_v1",
                "confidence_before": 0.0, "confidence_after": 0.99,
                "component_contributions": {"x": {"value": 1, "weight": 1, "contribution": 0.99}},
                "threshold_references": {"ratify_min": 0.7},
                "meets_ratify_threshold": True,
                "evidence_ids": ["e"], "mining_evidence_ids": ["e"], "shadow_evidence_ids": ["s"],
                "content_hash": "not-a-real-confidence-hash",
            })


class TestExactCrossBind(unittest.TestCase):
    def _ready_bundle(self, td: Path):
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        template = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_template.json").read_text())
        store = PriorStore(td / "ephem", create=True)
        obs = observe_phase(
            events=events, shadow_events=shadow, store=store, out_dir=td / "out",
            ledger_path=td / "out" / "ledger.json",
        )
        compiled = fixture_compile_ecqr(
            template, candidate=obs["entity"], shadow=obs["shadow_report"], confidence=obs["confidence"],
            mining_event_ids=list(obs["entity"]["source_event_ids"]),
            shadow_event_ids=list(obs["shadow_report"]["shadow_event_ids"]),
            shadow_events=obs["shadow_events_normalized"],
            confidence_inputs=obs["confidence_inputs"],
        )
        vecqr = validate_ecqr_decision(
            compiled, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
        )
        return obs, compiled, vecqr

    def test_E_F_G_H_receipt_hash_mismatches_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = self._ready_bundle(td)
        entity = obs["entity"]
        # Build correct receipt then tamper each binding
        from motor_learning.artifacts import candidate_content_hash
        receipt = build_learning_receipt(
            decision="RATIFIED", prior_id=f"prior-{entity['candidate_id']}",
            candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
            rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0],
            decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"],
            shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"],
            ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
        )
        entity2 = transition(
            dict(entity), RATIFIED, actor=compiled["reviewer"], reason=compiled["rationale"],
            evidence=compiled["evidence_reviewed"], learning_receipt=receipt, timestamp=compiled["effective_at"],
        )
        prior = {
            "prior_id": receipt["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"],
            "scope": entity["scope"], "candidate_id": entity["candidate_id"],
            "learning_receipt_id": receipt["receipt_id"],
            "transition_history": entity2["transition_history"],
            "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
            "source_event_ids": entity["source_event_ids"],
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        # Exact equal path succeeds
        store.commit_terminal_bundle(
            prior=prior, learning_receipt=receipt, ecqr_decision=vecqr,
            candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
           shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            expected_version=1,
        )
        # Remake store and tamper each field
        for field, bad in (
            ("shadow_hash", "bad-shadow"),
            ("confidence_hash", "bad-conf"),
            ("ecqr_decision_hash", "bad-ecqr"),
            ("candidate_hash", "bad-cand"),
            ("shadow_evidence_manifest_hash", "bad-manifest"),
        ):
            td2 = Path(tempfile.mkdtemp())
            obs2, compiled2, vecqr2 = self._ready_bundle(td2)
            entity = obs2["entity"]
            r = build_learning_receipt(
                decision="RATIFIED", prior_id=f"prior-{entity['candidate_id']}",
                candidate_id=entity["candidate_id"], reviewer=compiled2["reviewer"],
                rationale=compiled2["rationale"], evidence_links=list(compiled2["evidence_reviewed"]),
                confidence_before=obs2["confidence"]["confidence_before"],
                confidence_after=obs2["confidence"]["confidence_after"],
                affected_loops=list(compiled2["affected_loops"]),
                applicable_runways=list(compiled2["applicable_runways"]),
                repositories=[],
                origin_event=entity["source_event_ids"][0],
                decision_timestamp=compiled2["effective_at"],
                shadow_id=obs2["shadow_report"]["shadow_id"],
                shadow_hash=obs2["shadow_report"]["content_hash"],
                shadow_evidence_manifest_hash=obs2["shadow_report"]["evidence_manifest_hash"],
                confidence_hash=obs2["confidence"]["content_hash"],
                ecqr_decision_hash=vecqr2.decision_hash,
                candidate_hash=candidate_content_hash(entity),
            )
            # Tamper after build by reconstructing with wrong field via validate bypass attempt
            body = dict(r)
            body[field] = bad
            # identity will also break — force through ValidatedReceipt-like path by rebuilding integrity wrongly
            # commit must revalidate receipt first — invalid identity fails at validate_and_mint
            store2 = PriorStore(td2 / "store", create=True, store_kind="w1_reference", allow_persist=True)
            ent = transition(
                dict(entity), RATIFIED, actor=compiled2["reviewer"], reason="ok",
                evidence=compiled2["evidence_reviewed"], learning_receipt=r, timestamp=compiled2["effective_at"],
            )
            prior2 = {
                "prior_id": r["prior_id"], "status": "active", "state": "RATIFIED",
                "action_attempted": entity["fingerprint"].get("action_attempted"),
                "recommended_action": entity["recommended_action"], "scope": entity["scope"],
                "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
                "transition_history": ent["transition_history"],
                "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
                "source_event_ids": entity["source_event_ids"],
            }
            # Mutate receipt dict after valid mint by passing dict with wrong hash but valid identity fields
            # Use internal path: pass receipt with wrong binding that still has matching receipt_id derivation
            bad_receipt = build_learning_receipt(
                decision="RATIFIED", prior_id=r["prior_id"],
                candidate_id=entity["candidate_id"], reviewer=compiled2["reviewer"],
                rationale=compiled2["rationale"] + " ",  # change rationale so we can set wrong hash fields with new id
                evidence_links=list(compiled2["evidence_reviewed"]),
                confidence_before=obs2["confidence"]["confidence_before"],
                confidence_after=obs2["confidence"]["confidence_after"],
                affected_loops=list(compiled2["affected_loops"]),
                applicable_runways=list(compiled2["applicable_runways"]),
                repositories=[],
                origin_event=entity["source_event_ids"][0],
                decision_timestamp=compiled2["effective_at"],
                shadow_id=obs2["shadow_report"]["shadow_id"],
                shadow_hash=obs2["shadow_report"]["content_hash"] if field != "shadow_hash" else "0" * 64,
                shadow_evidence_manifest_hash=obs2["shadow_report"]["evidence_manifest_hash"] if field != "shadow_evidence_manifest_hash" else "0" * 64,
                confidence_hash=obs2["confidence"]["content_hash"] if field != "confidence_hash" else "0" * 64,
                ecqr_decision_hash=vecqr2.decision_hash if field != "ecqr_decision_hash" else "0" * 64,
                candidate_hash=candidate_content_hash(entity) if field != "candidate_hash" else "0" * 64,
            )
            # transition with bad receipt still validates structurally but bindings wrong at persist
            ent_bad = transition(
                {**entity, "state": SHADOW, "transition_history": []}, RATIFIED,
                actor=compiled2["reviewer"], reason="ok",
                evidence=compiled2["evidence_reviewed"], learning_receipt=bad_receipt,
                timestamp=compiled2["effective_at"],
            )
            prior_bad = {
                **prior2, "learning_receipt_id": bad_receipt["receipt_id"],
                "transition_history": ent_bad["transition_history"],
            }
            with self.assertRaises((GovernanceBlock, MotorLearningError)):
                store2.commit_terminal_bundle(
                    prior=prior_bad, learning_receipt=bad_receipt, ecqr_decision=vecqr2,
                    candidate=entity, shadow=obs2["shadow_report"], confidence=obs2["confidence"],
                shadow_events=obs2["shadow_events_normalized"], confidence_inputs=obs2["confidence_inputs"],
                    expected_version=1,
                )
            shutil.rmtree(td2)
        shutil.rmtree(td)


class TestAtomicPriorStore(unittest.TestCase):
    def test_I_duplicate_leaves_no_orphan_receipt(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        template = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_template.json").read_text())
        obs = observe_phase(events=events, shadow_events=shadow, store=PriorStore(td / "e", create=True),
                            out_dir=td / "o", ledger_path=td / "o" / "l.json")
        compiled = fixture_compile_ecqr(template, candidate=obs["entity"], shadow=obs["shadow_report"], confidence=obs["confidence"],
                                        mining_event_ids=list(obs["entity"]["source_event_ids"]),
                                        shadow_event_ids=list(obs["shadow_report"]["shadow_event_ids"]),
                                        shadow_events=obs["shadow_events_normalized"],
                                        confidence_inputs=obs["confidence_inputs"])
        vecqr = validate_ecqr_decision(
            compiled, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
        )
        from motor_learning.artifacts import candidate_content_hash
        entity = obs["entity"]
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=f"prior-{entity['candidate_id']}", candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]), repositories=[],
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
        )
        ent = transition({**entity, "state": SHADOW, "transition_history": []}, RATIFIED,
                         actor=compiled["reviewer"], reason="ok", evidence=compiled["evidence_reviewed"],
                         learning_receipt=r, timestamp=compiled["effective_at"])
        prior = {
            "prior_id": r["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"],
            "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
            "source_event_ids": entity["source_event_ids"],
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        store.commit_terminal_bundle(
            prior=prior, learning_receipt=r, ecqr_decision=vecqr,
            candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
           shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            expected_version=1,
        )
        mid = store_tree_hash(td / "store")
        receipt_count = len(list((td / "store" / "receipts").glob("*.json")))
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
                allow_duplicate=False, expected_version=1,
            )
        after = store_tree_hash(td / "store")
        self.assertEqual(mid, after)
        self.assertEqual(len(list((td / "store" / "receipts").glob("*.json"))), receipt_count)
        shutil.rmtree(td)

    def test_J_CAS_failure_no_orphan(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        # seed nonterminal then try terminal commit with wrong expected_version via direct API
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        template = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_template.json").read_text())
        obs = observe_phase(events=events, shadow_events=shadow, store=PriorStore(td / "e", create=True),
                            out_dir=td / "o", ledger_path=td / "o" / "l.json")
        compiled = fixture_compile_ecqr(template, candidate=obs["entity"], shadow=obs["shadow_report"], confidence=obs["confidence"],
                                        mining_event_ids=list(obs["entity"]["source_event_ids"]),
                                        shadow_event_ids=list(obs["shadow_report"]["shadow_event_ids"]),
                                        shadow_events=obs["shadow_events_normalized"],
                                        confidence_inputs=obs["confidence_inputs"])
        vecqr = validate_ecqr_decision(
            compiled, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
        )
        from motor_learning.artifacts import candidate_content_hash
        entity = obs["entity"]
        r = build_learning_receipt(
            decision="RATIFIED", prior_id="prior-cas", candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]), repositories=[],
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
        )
        # Create existing prior version 1 nonterminal then try terminal with expected 99
        store._persist_nonterminal({
            "prior_id": "prior-cas", "status": "shadow",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
        }, allow_duplicate=False, expected_version=None)
        before = store_tree_hash(td / "store")
        ent = transition({**entity, "state": SHADOW, "transition_history": []}, RATIFIED,
                         actor=compiled["reviewer"], reason="ok", evidence=compiled["evidence_reviewed"],
                         learning_receipt=r, timestamp=compiled["effective_at"])
        prior = {
            "prior_id": "prior-cas", "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"],
            "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
            "source_event_ids": entity["source_event_ids"],
        }
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
                allow_duplicate=True, expected_version=99,
            )
        after = store_tree_hash(td / "store")
        self.assertEqual(before, after)
        self.assertEqual(list((td / "store" / "receipts").glob("*.json")), [])
        shutil.rmtree(td)


class TestECQRImmutability(unittest.TestCase):
    def test_L_template_rejected_by_governed_run(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        template = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_template.json").read_text())
        self.assertTrue(is_ecqr_template(template))
        with self.assertRaises(GovernanceBlock):
            run_pipeline(
                events=events, shadow_events=shadow, store_dir=td / "store", out_dir=td / "out",
                ecqr_decision=template, dry_run=True,
            )
        shutil.rmtree(td)

    def test_M_rollback_cannot_rewrite_decision(self):
        td = Path(tempfile.mkdtemp())
        # seed active in fixture store
        fs = PriorStore(td / "fix", create=True, store_kind="fixture")
        fs.seed_fixture({
            "prior_id": "prior-to-rollback", "status": "active",
            "action_attempted": "x", "recommended_action": "y",
            "scope": {"loop_id": "motor_learning_organ_v1", "runway": "Software Repair"},
            "candidate_id": "c",
        }, allow_terminal_seed=True)
        bad = {
            "decision": "RATIFIED",  # wrong — must not be rewritten to ROLLED_BACK
            "candidate_id": "c", "reviewer": "test_reviewer:x", "rationale": "r",
            "evidence_reviewed": ["e1"], "shadow_result_ref": "shadow:x",
            "confidence_before": 0.8, "confidence_after": 0.4,
            "affected_loops": ["motor_learning_organ_v1"], "applicable_runways": ["Software Repair"],
            "effective_at": "2026-07-11T12:00:00Z", "policy_versions": {"organ": "X"},
            "rollback_target": "prior-to-rollback",
        }
        with self.assertRaises(GovernanceBlock):
            rollback_prior(
                prior_id="prior-to-rollback", store_dir=td / "fs", out_dir=td / "out",
                ecqr_decision=bad, dry_run=True,
            )
        shutil.rmtree(td)

    def test_fixture_bytes_unchanged(self):
        td = Path(tempfile.mkdtemp())
        path = FIX / "01_repeated_success_ratify" / "ecqr_template.json"
        before = path.read_bytes()
        run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(before, path.read_bytes())
        shutil.rmtree(td)


class TestFixtureIsolation(unittest.TestCase):
    def test_N_fixture_absent_from_governed_search(self):
        td = Path(tempfile.mkdtemp())
        fs = PriorStore(td / "fixture", create=True, store_kind="fixture")
        fs.seed_fixture({
            "prior_id": "p-fix-active", "status": "active",
            "action_attempted": "ci_retry_deploy", "recommended_action": "route_B_retry",
            "scope": {"loop_id": "motor_learning_organ_v1"},
            "fingerprint": {"action_attempted": "ci_retry_deploy", "outcome": "success"},
        }, allow_terminal_seed=True)
        # Fixture store search without include returns []
        self.assertEqual(fs.search(status="active"), [])
        self.assertEqual(len(fs.search(status="active", include_fixtures=True)), 1)
        # w1 store rejects seed_fixture
        ref = PriorStore(td / "ref", create=True, store_kind="w1_reference")
        with self.assertRaises(GovernanceBlock):
            ref.seed_fixture({
                "prior_id": "x", "status": "proposed",
                "action_attempted": "a", "recommended_action": "b", "scope": {},
            })
        # 04 near-dup with only fixture seed must NOT veto (RATIFY)
        s = run_from_fixture_dir(FIX / "04_near_duplicate_prior", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(s.get("ecqr_decision"), "RATIFIED")
        self.assertNotEqual(s.get("blocked_reason"), "DUPLICATE_CONFLICT_REVIEW_REQUIRED")
        shutil.rmtree(td)


class TestPathDisjointness(unittest.TestCase):
    def test_O_path_overlaps_fail_before_write(self):
        td = Path(tempfile.mkdtemp())
        store = td / "store"
        with self.assertRaises(GovernanceBlock):
            assert_paths_disjoint(store_dir=store, out_dir=store)
        with self.assertRaises(GovernanceBlock):
            assert_paths_disjoint(store_dir=store, out_dir=store / "out")
        with self.assertRaises(GovernanceBlock):
            assert_paths_disjoint(store_dir=store / "nested", out_dir=store)
        with self.assertRaises(GovernanceBlock):
            assert_paths_disjoint(store_dir=store, out_dir=td / "out", event_ledger_path=store / "ledger.json")
        # nonexistent store + failed commit remains nonexistent
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        template = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_template.json").read_text())
        obs = observe_phase(events=events, shadow_events=shadow, store=PriorStore(td / "e", create=True),
                            out_dir=td / "o", ledger_path=td / "o" / "l.json")
        compiled = fixture_compile_ecqr(template, candidate=obs["entity"], shadow=obs["shadow_report"], confidence=obs["confidence"],
                                        mining_event_ids=list(obs["entity"]["source_event_ids"]),
                                        shadow_event_ids=list(obs["shadow_report"]["shadow_event_ids"]),
                                        shadow_events=obs["shadow_events_normalized"],
                                        confidence_inputs=obs["confidence_inputs"])
        missing_store = td / "never-created-store"
        self.assertFalse(missing_store.exists())
        with self.assertRaises(MotorLearningError):
            run_pipeline(
                events=events, shadow_events=shadow, store_dir=missing_store, out_dir=td / "out2",
                ecqr_decision=compiled, dry_run=False, allow_store_persist=True,
                inject_failure_after="receipt_staging",
            )
        self.assertFalse(missing_store.exists())
        shutil.rmtree(td)


class TestPipelineFixtures(unittest.TestCase):
    def test_01_ratify(self):
        td = Path(tempfile.mkdtemp())
        (td / "store").mkdir()
        before = store_tree_hash(td / "store")
        s = run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(s["ecqr_decision"], "RATIFIED")
        self.assertFalse(json.loads((td / "out" / "prior.dry_run_preview.json").read_text())["live_consumable"])
        self.assertEqual(store_tree_hash(td / "store"), before)
        shutil.rmtree(td)

    def test_06_reject(self):
        td = Path(tempfile.mkdtemp())
        s = run_from_fixture_dir(FIX / "06_rejected_candidate", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(s["ecqr_decision"], "REJECTED")
        shutil.rmtree(td)

    def test_07_rollback(self):
        td = Path(tempfile.mkdtemp())
        s = run_from_fixture_dir(FIX / "07_rollback", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(s["final_state"], ROLLED_BACK)
        shutil.rmtree(td)

    def test_08_overlap(self):
        td = Path(tempfile.mkdtemp())
        s = run_from_fixture_dir(FIX / "08_shadow_overlap_blocked", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertIn("overlap", s.get("blocked_reason") or "")
        shutil.rmtree(td)

    def test_I_programmatic_persist_gate(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        template = json.loads((FIX / "01_repeated_success_ratify" / "ecqr_template.json").read_text())
        obs = observe_phase(events=events, shadow_events=shadow, store=PriorStore(td / "e", create=True),
                            out_dir=td / "o", ledger_path=td / "o" / "l.json")
        compiled = fixture_compile_ecqr(template, candidate=obs["entity"], shadow=obs["shadow_report"], confidence=obs["confidence"],
                                        mining_event_ids=list(obs["entity"]["source_event_ids"]),
                                        shadow_event_ids=list(obs["shadow_report"]["shadow_event_ids"]),
                                        shadow_events=obs["shadow_events_normalized"],
                                        confidence_inputs=obs["confidence_inputs"])
        with self.assertRaises(GovernanceBlock):
            run_pipeline(events=events, shadow_events=shadow, store_dir=td / "s", out_dir=td / "out",
                         ecqr_decision=compiled, dry_run=False)
        s = run_pipeline(events=events, shadow_events=shadow, store_dir=td / "s2", out_dir=td / "out2",
                         ecqr_decision=compiled, dry_run=False, allow_store_persist=True)
        self.assertEqual(s["ecqr_decision"], "RATIFIED")
        prior = json.loads((td / "out2" / "prior.json").read_text())
        self.assertFalse(prior["live_consumable"])
        shutil.rmtree(td)


class TestLiveConsumableMatrix(unittest.TestCase):
    def test_all_false(self):
        for st in ("active", "rejected", "rolled_back", "expired", "superseded"):
            self.assertFalse(live_consumable_for_status(st))


class TestScopeGuard(unittest.TestCase):
    def test_Q_landing_site_unchanged(self):
        r = subprocess.run(["git", "diff", "--name-only", "origin/main...HEAD"], cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode != 0:
            mb = subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=str(ROOT), capture_output=True, text=True)
            if mb.returncode != 0:
                self.skipTest("no merge-base")
            r = subprocess.run(["git", "diff", "--name-only", f"{mb.stdout.strip()}...HEAD"], cwd=str(ROOT), capture_output=True, text=True)
        for line in r.stdout.splitlines():
            self.assertFalse(line.startswith("landing-site/"), line)


class TestNormalize(unittest.TestCase):
    def test_basic(self):
        with self.assertRaises(SchemaError):
            normalize_event({"event_id": "x"})



class TestLifecycleReplayProbes(unittest.TestCase):
    def test_illegal_observed_to_ratified_history_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        entity = obs["entity"]
        from motor_learning.artifacts import candidate_content_hash
        from motor_learning.lifecycle import validate_transition_history
        bad_hist = [
            {"from_state": "OBSERVED", "to_state": "RATIFIED", "actor": "x", "timestamp": "t",
             "reason": "illegal", "evidence": ["e"], "learning_receipt_id": "lr-x"},
        ]
        with self.assertRaises(GovernanceBlock):
            validate_transition_history(bad_hist, entity_status="active")
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=f"prior-{entity['candidate_id']}",
            candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
            rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]), repositories=[],
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
        )
        prior = {
            "prior_id": r["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": bad_hist, "fingerprint": entity["fingerprint"],
            "evidence_refs": entity["evidence_refs"], "source_event_ids": entity["source_event_ids"],
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
               shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
                expected_version=1,
            )
        shutil.rmtree(td)

    def test_discontinuous_transition_history_blocked(self):
        from motor_learning.lifecycle import validate_transition_history
        hist = [
            {"from_state": "OBSERVED", "to_state": "PROPOSED", "actor": "a", "timestamp": "t1",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "SHADOW", "to_state": "RATIFIED", "actor": "a", "timestamp": "t2",
             "reason": "r", "evidence": [], "learning_receipt_id": "lr"},
        ]
        with self.assertRaises(GovernanceBlock) as cm:
            validate_transition_history(hist, entity_status="active")
        self.assertIn("discontinuous", str(cm.exception))


class TestDerivationProvenanceProbes(unittest.TestCase):
    def test_self_consistent_synthetic_shadow_blocked(self):
        """Correct self-hash alone is never proof — events required."""
        fake = {
            "schema": "nf_motor_learning_shadow_report_v1",
            "shadow_id": "shadow-synthetic",
            "candidate_id": "c",
            "successes": 3, "failures": 0, "abstentions": 0, "total": 3,
            "evaluated": 3, "coverage": 1.0, "success_rate": 1.0,
            "result": "success", "ratifiable": True, "details": [],
            "shadow_event_ids": ["s1", "s2", "s3"],
            "evidence_refs": ["er1", "er2", "er3"],
            "evidence_manifest": {
                "shadow_event_ids": ["s1", "s2", "s3"], "evidence_refs": ["er1", "er2", "er3"],
                "normalized_event_hashes": ["h1", "h2", "h3"],
                "successes": 3, "failures": 0, "abstentions": 0,
                "evaluated": 3, "coverage": 1.0, "success_rate": 1.0,
            },
            "production_change": False,
        }
        fake["evidence_manifest_hash"] = content_hash(fake["evidence_manifest"])
        body = {k: fake[k] for k in sorted(fake) if k != "content_hash"}
        fake["content_hash"] = content_hash(body)
        with self.assertRaises(GovernanceBlock) as cm:
            validate_shadow_report(fake)  # no candidate/events
        msg = str(cm.exception)
        self.assertTrue("shadow_events" in msg or "candidate" in msg or "derivation" in msg, msg)

    def test_shadow_from_different_event_stream_blocked(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow_a = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        store = PriorStore(td / "e", create=True)
        obs = observe_phase(events=events, shadow_events=shadow_a, store=store,
                            out_dir=td / "out", ledger_path=td / "out" / "l.json")
        # Mutate a concrete alternate stream (different outcomes / IDs)
        from motor_learning.normalize import normalize_many
        from motor_learning.event_registry import EventRegistry
        alt = []
        for i, ev in enumerate(shadow_a):
            e = dict(ev)
            e["event_id"] = f"alt-shadow-{i}"
            e["outcome"] = "failure"
            e["evidence_refs"] = [f"alt-ev-{i}"]
            alt.append(e)
        sh_b, _ = normalize_many(alt, event_registry=EventRegistry(td / "out" / "reg_b.json"))
        with self.assertRaises(GovernanceBlock):
            validate_shadow_report(
                obs["shadow_report"], candidate=obs["entity"],
                shadow_events=sh_b, require_derivation=True,
            )
        shutil.rmtree(td)

    def test_fabricated_confidence_components_blocked(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        obs = observe_phase(events=events, shadow_events=shadow, store=PriorStore(td / "e", create=True),
                            out_dir=td / "out", ledger_path=td / "out" / "l.json")
        fake = dict(obs["confidence"])
        # Self-consistent: invent components that sum to same score, rehash
        comps = dict(fake["component_contributions"])
        # reweight evidence_count
        comps["evidence_count"] = dict(comps["evidence_count"])
        comps["evidence_count"]["weight"] = 0.99
        comps["evidence_count"]["contribution"] = 0.99
        fake["component_contributions"] = comps
        fake.pop("content_hash", None)
        fake["content_hash"] = content_hash({k: fake[k] for k in sorted(fake) if k != "content_hash"})
        with self.assertRaises(GovernanceBlock):
            validate_confidence_artifact(
                fake, shadow=obs["shadow_report"],
                confidence_inputs=obs["confidence_inputs"], require_derivation=True,
            )
        shutil.rmtree(td)


class TestFullyBoundECQRProbes(unittest.TestCase):
    def _base_bound(self, obs, compiled):
        d = dict(compiled)
        return d

    def test_ratified_missing_candidate_hash_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, _ = TestExactCrossBind()._ready_bundle(td)
        d = dict(compiled)
        d.pop("candidate_hash", None)
        d.pop("decision_hash", None)
        with self.assertRaises(GovernanceBlock) as cm:
            validate_ecqr_decision(
                d, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            )
        self.assertIn("candidate_hash", str(cm.exception))
        shutil.rmtree(td)

    def test_ratified_missing_shadow_id_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, _ = TestExactCrossBind()._ready_bundle(td)
        d = dict(compiled)
        d.pop("shadow_id", None)
        d.pop("decision_hash", None)
        with self.assertRaises(GovernanceBlock) as cm:
            validate_ecqr_decision(
                d, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            )
        self.assertIn("shadow_id", str(cm.exception))
        shutil.rmtree(td)

    def test_ratified_missing_confidence_hash_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, _ = TestExactCrossBind()._ready_bundle(td)
        d = dict(compiled)
        d.pop("confidence_hash", None)
        d.pop("decision_hash", None)
        with self.assertRaises(GovernanceBlock) as cm:
            validate_ecqr_decision(
                d, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            )
        self.assertIn("confidence_hash", str(cm.exception))
        shutil.rmtree(td)


class TestPathFailBeforeWriteProbes(unittest.TestCase):
    def test_rollback_nested_path_no_directory_created(self):
        td = Path(tempfile.mkdtemp())
        store = td / "store"
        # nested out under store — must fail before mkdir
        out = store / "nested" / "out"
        parent_before = list(td.iterdir())
        with self.assertRaises(GovernanceBlock):
            rollback_prior(
                prior_id="p", store_dir=store, out_dir=out,
                ecqr_decision={"decision": "ROLLED_BACK", "rollback_target": "p",
                               "candidate_id": "c", "reviewer": "test_reviewer:x", "rationale": "r",
                               "evidence_reviewed": ["e"], "shadow_result_ref": "shadow:x",
                               "confidence_before": 0.1, "confidence_after": 0.1,
                               "affected_loops": ["motor_learning_organ_v1"],
                               "applicable_runways": ["Software Repair"],
                               "effective_at": "2026-07-11T12:00:00Z",
                               "policy_versions": {"organ": "X"}},
                dry_run=True,
            )
        self.assertFalse(store.exists())
        self.assertFalse(out.exists())
        self.assertEqual(sorted(p.name for p in td.iterdir()), sorted(p.name for p in parent_before))
        shutil.rmtree(td)

    def test_equal_nonexistent_store_out_remains_nonexistent(self):
        td = Path(tempfile.mkdtemp())
        same = td / "same-path"
        self.assertFalse(same.exists())
        with self.assertRaises(GovernanceBlock):
            run_pipeline(
                events=[], shadow_events=[], store_dir=same, out_dir=same, dry_run=True,
            )
        self.assertFalse(same.exists())
        with self.assertRaises(GovernanceBlock):
            rollback_prior(
                prior_id="p", store_dir=same, out_dir=same,
                ecqr_decision={"decision": "ROLLED_BACK", "rollback_target": "p",
                               "candidate_id": "c", "reviewer": "test_reviewer:x", "rationale": "r",
                               "evidence_reviewed": ["e"], "shadow_result_ref": "shadow:x",
                               "confidence_before": 0.1, "confidence_after": 0.1,
                               "affected_loops": ["motor_learning_organ_v1"],
                               "applicable_runways": ["Software Repair"],
                               "effective_at": "2026-07-11T12:00:00Z",
                               "policy_versions": {"organ": "X"}},
                dry_run=True,
            )
        self.assertFalse(same.exists())
        shutil.rmtree(td)


class TestRollbackBindingProbes(unittest.TestCase):
    def _seed_active(self, td: Path):
        fs = PriorStore(td / "ref", create=True, store_kind="w1_reference", allow_persist=True)
        # Use fixture seed content into a reference store via direct non-terminal then... 
        # For rollback we need active prior — seed via fixture store then copy? 
        # Simpler: write prior file into w1 store using seed on fixture then open as fixture for dry-run get.
        # Persist path needs w1_reference. Build minimal active prior with learning_receipt_id.
        prior = json.loads((FIX / "07_rollback" / "seed_priors" / "prior-to-rollback.json").read_text())
        prior["store_kind"] = "w1_reference"
        prior["fixture_seeded"] = False
        # Use create=False path: write via _persist_nonterminal is blocked for terminal.
        # Put via commit is heavy — for dry-run rollback, fixture store works for get().
        fx = PriorStore(td / "fx", create=True, store_kind="fixture")
        fx.seed_fixture(prior, allow_terminal_seed=True)
        return td / "fx", prior

    def test_rollback_target_different_from_prior_id_blocked(self):
        td = Path(tempfile.mkdtemp())
        store_dir, prior = self._seed_active(td)
        ecqr = json.loads((FIX / "07_rollback" / "ecqr_decision.json").read_text())
        ecqr["rollback_target"] = "other-prior"
        with self.assertRaises(GovernanceBlock) as cm:
            rollback_prior(
                prior_id=prior["prior_id"], store_dir=store_dir, out_dir=td / "out",
                ecqr_decision=ecqr, dry_run=True,
            )
        self.assertIn("different from prior_id", str(cm.exception))
        shutil.rmtree(td)

    def test_regression_evidence_mismatch_blocked(self):
        td = Path(tempfile.mkdtemp())
        store_dir, prior = self._seed_active(td)
        ecqr = json.loads((FIX / "07_rollback" / "ecqr_decision.json").read_text())
        with self.assertRaises(GovernanceBlock) as cm:
            rollback_prior(
                prior_id=prior["prior_id"], store_dir=store_dir, out_dir=td / "out",
                ecqr_decision=ecqr, dry_run=True,
                regression_evidence=["wrong-evidence"],
            )
        self.assertIn("regression evidence mismatch", str(cm.exception))
        shutil.rmtree(td)

    def test_stale_rollback_version_blocked(self):
        td = Path(tempfile.mkdtemp())
        # Persist active prior into w1 reference, then try rollback with wrong expected_version
        prior = json.loads((FIX / "07_rollback" / "seed_priors" / "prior-to-rollback.json").read_text())
        # First place via fixture then manually copy into w1 by writing files — use commit of rolled_back after ratify is hard.
        # Instead: create w1 store, write prior JSON + index directly for this probe of CAS on rollback persist.
        store = PriorStore(td / "ref", create=True, store_kind="w1_reference", allow_persist=True)
        body = dict(prior)
        body["store_kind"] = "w1_reference"
        body["fixture_seeded"] = False
        body["version"] = 3
        # Bypass terminal gate by writing files (probe targets CAS at commit, not seed)
        store._ensure_dirs()
        body.pop("content_hash", None)
        body["content_hash"] = content_hash({k: body[k] for k in sorted(body)})
        store._prior_path(body["prior_id"]).write_text(json.dumps(body, indent=2, sort_keys=True) + "\n")
        idx = store._read_index()
        idx["priors"][body["prior_id"]] = {
            "status": "active", "path": store._prior_path(body["prior_id"]).name,
            "content_hash": body["content_hash"], "version": 3, "live_consumable": False, "fixture_seeded": False,
        }
        store._write_index(idx)
        ecqr = json.loads((FIX / "07_rollback" / "ecqr_decision.json").read_text())
        # dry_run uses expected from loaded prior — inject failure by calling commit with wrong version after building
        # Public API: rollback_prior uses loaded version. Force stale by mutating store version after load path:
        # Call commit_terminal_bundle directly simulating rollback with expected_version=1 while store has 3.
        from motor_learning.receipt import build_learning_receipt, validate_and_mint_receipt
        from motor_learning.ecqr import validate_ecqr_decision
        from motor_learning.lifecycle import transition as tr
        ed = validate_ecqr_decision(ecqr, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=body["prior_id"], candidate_id=ed.as_dict()["candidate_id"],
            reviewer=ed.as_dict()["reviewer"], rationale=ed.as_dict()["rationale"],
            evidence_links=list(ed.as_dict()["evidence_reviewed"]),
            confidence_before=float(ed.as_dict()["confidence_before"]),
            confidence_after=float(ed.as_dict()["confidence_after"]),
            affected_loops=list(ed.as_dict()["affected_loops"]),
            applicable_runways=list(ed.as_dict()["applicable_runways"]), repositories=[],
            origin_event=ed.as_dict()["evidence_reviewed"][0],
            decision_timestamp=ed.as_dict()["effective_at"],
            rollback_target=body["prior_id"], snapshot_id=body["prior_id"],
            ecqr_decision_hash=ed.decision_hash,
        )
        vr = validate_and_mint_receipt(receipt)
        entity = {"state": "RATIFIED", "status": "active", "prior_id": body["prior_id"],
                  "candidate_id": body["candidate_id"],
                  "transition_history": list(body.get("transition_history") or [])}
        entity = tr(entity, ROLLED_BACK, actor=ed.as_dict()["reviewer"], reason="r",
                    evidence=ed.as_dict()["evidence_reviewed"], learning_receipt=vr,
                    timestamp=ed.as_dict()["effective_at"])
        updated = dict(body)
        updated.update({"state": entity["state"], "status": entity["status"],
                        "transition_history": entity["transition_history"],
                        "learning_receipt_id": receipt["receipt_id"],
                        "rollback_target": body["prior_id"],
                        "rollback_target_prior_content_hash": body["content_hash"],
                        "rollback_target_version": 3,
                        "prior_ratification_receipt_id": body["learning_receipt_id"]})
        with self.assertRaises(MotorLearningError) as cm:
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=vr, ecqr_decision=ed,
                allow_duplicate=True, expected_version=1,  # stale
            )
        self.assertIn("CAS", str(cm.exception))
        shutil.rmtree(td)


class TestStoreIdentityProbes(unittest.TestCase):
    def test_fixture_store_reopened_as_reference_blocked(self):
        td = Path(tempfile.mkdtemp())
        fx = PriorStore(td / "fx", create=True, store_kind="fixture")
        fx.seed_fixture({
            "prior_id": "p1", "status": "proposed",
            "action_attempted": "a", "recommended_action": "b",
            "scope": {"loop_id": "motor_learning_organ_v1"},
        })
        with self.assertRaises(GovernanceBlock) as cm:
            PriorStore(td / "fx", create=False, store_kind="w1_reference")
        self.assertIn("store identity mismatch", str(cm.exception))
        shutil.rmtree(td)


if __name__ == "__main__":
    unittest.main()
