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
from motor_learning.artifacts import validate_shadow_report, validate_confidence_artifact, mining_evidence_manifest
from motor_learning.paths import assert_paths_disjoint
from motor_learning.hashutil import content_hash

FIX = ROOT / "fixtures" / "motor_learning_w1"

def _entity_with_prior(entity, compiled=None, prior_id=None):
    e = dict(entity)
    e["prior_id"] = prior_id or (compiled or {}).get("prior_id") or f"prior-{e['candidate_id']}"
    return e



def _mine_hash(obs):
    _, h = mining_evidence_manifest(obs["entity"], obs["mining_events_normalized"])
    return h


def _pph(compiled, entity, status="active", state="RATIFIED"):
    from motor_learning.artifacts import compute_prior_payload_hash
    if compiled.get("prior_payload_hash"):
        return compiled["prior_payload_hash"]
    return compute_prior_payload_hash(
        candidate=entity, prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
        status=status, state=state,
    )


def _compile_and_validate(obs, template):
    compiled = fixture_compile_ecqr(
        template, candidate=obs["entity"], shadow=obs["shadow_report"], confidence=obs["confidence"],
        mining_event_ids=list(obs["entity"]["source_event_ids"]),
        shadow_event_ids=list(obs["shadow_report"]["shadow_event_ids"]),
        shadow_events=obs["shadow_events_normalized"],
        confidence_inputs=obs["confidence_inputs"],
        mining_events=obs["mining_events_normalized"],
    )
    vecqr = validate_ecqr_decision(
        compiled, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
        shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"],
    )
    return compiled, vecqr



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
        compiled, vecqr = _compile_and_validate(obs, template)
        return obs, compiled, vecqr

    def test_E_F_G_H_receipt_hash_mismatches_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = self._ready_bundle(td)
        entity = obs["entity"]
        # Build correct receipt then tamper each binding
        from motor_learning.artifacts import candidate_content_hash
        receipt = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
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
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        entity2 = transition(
            _entity_with_prior(entity, compiled), RATIFIED, actor=compiled["reviewer"], reason=compiled["rationale"],
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
            mining_events=obs["mining_events_normalized"],
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
                decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
                candidate_id=entity["candidate_id"], reviewer=compiled2["reviewer"],
                rationale=compiled2["rationale"], evidence_links=list(compiled2["evidence_reviewed"]),
                confidence_before=obs2["confidence"]["confidence_before"],
                confidence_after=obs2["confidence"]["confidence_after"],
                affected_loops=list(compiled2["affected_loops"]),
                applicable_runways=list(compiled2["applicable_runways"]),
                repositories=list(compiled2.get("repositories") or []),
                origin_event=entity["source_event_ids"][0],
                decision_timestamp=compiled2["effective_at"],
                shadow_id=obs2["shadow_report"]["shadow_id"],
                shadow_hash=obs2["shadow_report"]["content_hash"],
                shadow_evidence_manifest_hash=obs2["shadow_report"]["evidence_manifest_hash"],
                confidence_hash=obs2["confidence"]["content_hash"],
                ecqr_decision_hash=vecqr2.decision_hash,
                candidate_hash=candidate_content_hash(entity),
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
            )
            # Tamper after build by reconstructing with wrong field via validate bypass attempt
            body = dict(r)
            body[field] = bad
            # identity will also break — force through ValidatedReceipt-like path by rebuilding integrity wrongly
            # commit must revalidate receipt first — invalid identity fails at validate_and_mint
            store2 = PriorStore(td2 / "store", create=True, store_kind="w1_reference", allow_persist=True)
            ent = transition(
                _entity_with_prior(entity, compiled), RATIFIED, actor=compiled2["reviewer"], reason=compiled2["rationale"],
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
                repositories=list(compiled2.get("repositories") or []),
                origin_event=entity["source_event_ids"][0],
                decision_timestamp=compiled2["effective_at"],
                shadow_id=obs2["shadow_report"]["shadow_id"],
                shadow_hash=obs2["shadow_report"]["content_hash"] if field != "shadow_hash" else "0" * 64,
                shadow_evidence_manifest_hash=obs2["shadow_report"]["evidence_manifest_hash"] if field != "shadow_evidence_manifest_hash" else "0" * 64,
                confidence_hash=obs2["confidence"]["content_hash"] if field != "confidence_hash" else "0" * 64,
                ecqr_decision_hash=vecqr2.decision_hash if field != "ecqr_decision_hash" else "0" * 64,
                candidate_hash=candidate_content_hash(entity) if field != "candidate_hash" else "0" * 64,
                mining_evidence_manifest_hash=_mine_hash(obs2),
                prior_payload_hash=_pph(compiled2, entity),
            )
            # transition with bad receipt still validates structurally but bindings wrong at persist
            ent_bad = transition(
                _entity_with_prior(entity, compiled), RATIFIED,
                actor=compiled2["reviewer"], reason=compiled2["rationale"],
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
                mining_events=obs2["mining_events_normalized"],
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
                                        confidence_inputs=obs["confidence_inputs"],
                                        mining_events=obs["mining_events_normalized"])
        vecqr = validate_ecqr_decision(
            compiled, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"],
        )
        from motor_learning.artifacts import candidate_content_hash
        entity = obs["entity"]
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}", candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        ent = transition(_entity_with_prior(entity, compiled), RATIFIED,
                         actor=compiled["reviewer"], reason=compiled["rationale"], evidence=compiled["evidence_reviewed"],
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
            mining_events=obs["mining_events_normalized"],
            expected_version=1,
        )
        mid = store_tree_hash(td / "store")
        receipt_count = len(list((td / "store" / "receipts").glob("*.json")))
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"],
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
                                        confidence_inputs=obs["confidence_inputs"],
                                        mining_events=obs["mining_events_normalized"])
        vecqr = validate_ecqr_decision(
            compiled, confidence=obs["confidence"], shadow=obs["shadow_report"], candidate=obs["entity"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"],
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
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        # Create existing prior version 1 nonterminal then try terminal with expected 99
        pid = compiled["prior_id"]
        store._persist_nonterminal({
            "prior_id": pid, "status": "shadow",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
        }, allow_duplicate=False, expected_version=None)
        before = store_tree_hash(td / "store")
        # Rebuild receipt bound to same prior_id as ECQR/entity
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=pid, candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        ent = transition(_entity_with_prior(entity, compiled), RATIFIED,
                         actor=compiled["reviewer"], reason=compiled["rationale"], evidence=compiled["evidence_reviewed"],
                         learning_receipt=r, timestamp=compiled["effective_at"])
        prior = {
            "prior_id": pid, "status": "active", "state": "RATIFIED",
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
            mining_events=obs["mining_events_normalized"],
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
                                        confidence_inputs=obs["confidence_inputs"],
                                        mining_events=obs["mining_events_normalized"])
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
                                        confidence_inputs=obs["confidence_inputs"],
                                        mining_events=obs["mining_events_normalized"])
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
            {"from_state": "OBSERVED", "to_state": "RATIFIED", "actor": "x", "timestamp": "2026-07-10T12:00:00Z",
             "reason": "illegal", "evidence": ["e"], "learning_receipt_id": "lr-x",
             "prior_id": "p-x", "candidate_id": "c-x"},
        ]
        with self.assertRaises(GovernanceBlock):
            validate_transition_history(bad_hist, entity_status="active")
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
            candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
            rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
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
            mining_events=obs["mining_events_normalized"],
                expected_version=1,
            )
        shutil.rmtree(td)

    def test_discontinuous_transition_history_blocked(self):
        from motor_learning.lifecycle import validate_transition_history
        hist = [
            {"from_state": "OBSERVED", "to_state": "PROPOSED", "actor": "a", "timestamp": "2026-07-10T10:00:00Z",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "SHADOW", "to_state": "RATIFIED", "actor": "a", "timestamp": "2026-07-10T12:00:00Z",
             "reason": "r", "evidence": ["e"], "learning_receipt_id": "lr",
             "prior_id": "p1", "candidate_id": "c1"},
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
            mining_events=obs["mining_events_normalized"],
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
            mining_events=obs["mining_events_normalized"],
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
            mining_events=obs["mining_events_normalized"],
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
        ecqr["rollback_target_prior_content_hash"] = body["content_hash"]
        ecqr["rollback_target_version"] = 3
        ecqr["prior_ratification_receipt_id"] = body["learning_receipt_id"]
        ecqr["repositories"] = list(ecqr.get("repositories") or [])
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
            applicable_runways=list(ed.as_dict()["applicable_runways"]),
            repositories=list(ed.as_dict().get("repositories") or []),
            origin_event=ed.as_dict()["evidence_reviewed"][0],
            decision_timestamp=ed.as_dict()["effective_at"],
            rollback_target=body["prior_id"], snapshot_id=body["prior_id"],
            ecqr_decision_hash=ed.decision_hash,
            rollback_target_prior_content_hash=body["content_hash"],
            rollback_target_version=3,
            prior_ratification_receipt_id=body["learning_receipt_id"],
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



class TestGap1LifecycleAnchor(unittest.TestCase):
    def test_new_prior_shadow_to_ratified_only_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        entity = obs["entity"]
        from motor_learning.artifacts import candidate_content_hash
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
            candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
            rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]), repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        bad_hist = [{
            "from_state": "SHADOW", "to_state": "RATIFIED", "actor": compiled["reviewer"],
            "timestamp": compiled["effective_at"], "reason": compiled["rationale"],
            "evidence": list(compiled["evidence_reviewed"]), "learning_receipt_id": r["receipt_id"],
            "prior_id": r["prior_id"], "candidate_id": entity["candidate_id"],
        }]
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
                mining_events=obs["mining_events_normalized"], expected_version=1,
            )
        shutil.rmtree(td)

    def test_rollback_ratified_only_no_prefix_blocked(self):
        from motor_learning.lifecycle import validate_transition_history
        # New prior must start at OBSERVED — RATIFIED→ROLLED_BACK alone is incomplete
        with self.assertRaises(GovernanceBlock):
            validate_transition_history(
                [{
                    "from_state": "RATIFIED", "to_state": "ROLLED_BACK", "actor": "a",
                    "timestamp": "2026-07-11T12:00:00Z", "reason": "r", "evidence": ["e"],
                    "learning_receipt_id": "lr-x", "prior_id": "p-x", "candidate_id": "c-x",
                }],
                entity_status="rolled_back",
                require_observed_origin=True,
            )
        # Explicit update without stored prefix
        with self.assertRaises(GovernanceBlock):
            validate_transition_history(
                [{
                    "from_state": "RATIFIED", "to_state": "ROLLED_BACK", "actor": "a",
                    "timestamp": "2026-07-11T12:00:00Z", "reason": "r", "evidence": ["e"],
                    "learning_receipt_id": "lr-x", "prior_id": "p-x", "candidate_id": "c-x",
                }],
                entity_status="rolled_back",
                existing_history=[],
                existing_state="RATIFIED",
            )

    def test_truncated_and_modified_prefix_blocked(self):
        from motor_learning.lifecycle import assert_history_prefix_preserved
        base = [
            {"from_state": "OBSERVED", "to_state": "PROPOSED", "actor": "a", "timestamp": "2026-07-10T10:00:00Z",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "PROPOSED", "to_state": "SHADOW", "actor": "a", "timestamp": "2026-07-10T11:00:00Z",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "SHADOW", "to_state": "RATIFIED", "actor": "a", "timestamp": "2026-07-10T12:00:00Z",
             "reason": "r", "evidence": ["e"], "learning_receipt_id": "lr-1",
             "prior_id": "p1", "candidate_id": "c1"},
        ]
        truncated = base[:-1] + [{
            "from_state": "RATIFIED", "to_state": "ROLLED_BACK", "actor": "a",
            "timestamp": "2026-07-11T12:00:00Z", "reason": "rb", "evidence": ["e"],
            "learning_receipt_id": "lr-2", "prior_id": "p1", "candidate_id": "c1",
        }]
        # truncated drops last ratified — prefix mismatch
        with self.assertRaises(GovernanceBlock):
            assert_history_prefix_preserved(base, truncated, existing_state="RATIFIED")
        modified = [dict(base[0], reason="CHANGED")] + base[1:] + [{
            "from_state": "RATIFIED", "to_state": "ROLLED_BACK", "actor": "a",
            "timestamp": "2026-07-11T12:00:00Z", "reason": "rb", "evidence": ["e"],
            "learning_receipt_id": "lr-2", "prior_id": "p1", "candidate_id": "c1",
        }]
        with self.assertRaises(GovernanceBlock):
            assert_history_prefix_preserved(base, modified, existing_state="RATIFIED")

    def test_active_overwrite_with_new_ratification_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        entity = obs["entity"]
        from motor_learning.artifacts import candidate_content_hash
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
            candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
            rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]), repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        ent = transition(_entity_with_prior(entity, compiled), RATIFIED, actor=compiled["reviewer"], reason=compiled["rationale"],
                         evidence=compiled["evidence_reviewed"], learning_receipt=r, timestamp=compiled["effective_at"])
        prior = {
            "prior_id": r["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"], "fingerprint": entity["fingerprint"],
            "evidence_refs": entity["evidence_refs"], "source_event_ids": entity["source_event_ids"],
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        store.commit_terminal_bundle(
            prior=prior, learning_receipt=r, ecqr_decision=vecqr,
            candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"], expected_version=1,
        )
        # Fresh short history overwrite attempt
        fresh = [{
            "from_state": "SHADOW", "to_state": "RATIFIED", "actor": compiled["reviewer"],
            "timestamp": compiled["effective_at"], "reason": "overwrite",
            "evidence": list(compiled["evidence_reviewed"]), "learning_receipt_id": r["receipt_id"],
            "prior_id": r["prior_id"], "candidate_id": entity["candidate_id"],
        }]
        prior2 = dict(prior)
        prior2["transition_history"] = fresh
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=prior2, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
                mining_events=obs["mining_events_normalized"],
                allow_duplicate=True, expected_version=1,
            )
        shutil.rmtree(td)

    def test_exact_prefix_plus_one_legal_transition_pass(self):
        from motor_learning.lifecycle import assert_history_prefix_preserved
        base = [
            {"from_state": "OBSERVED", "to_state": "PROPOSED", "actor": "a", "timestamp": "2026-07-10T10:00:00Z",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "PROPOSED", "to_state": "SHADOW", "actor": "a", "timestamp": "2026-07-10T11:00:00Z",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "SHADOW", "to_state": "RATIFIED", "actor": "a", "timestamp": "2026-07-10T12:00:00Z",
             "reason": "r", "evidence": ["e"], "learning_receipt_id": "lr-1",
             "prior_id": "p1", "candidate_id": "c1"},
        ]
        new = base + [{
            "from_state": "RATIFIED", "to_state": "ROLLED_BACK", "actor": "a",
            "timestamp": "2026-07-11T12:00:00Z", "reason": "rb", "evidence": ["e"],
            "learning_receipt_id": "lr-2", "prior_id": "p1", "candidate_id": "c1",
        }]
        assert_history_prefix_preserved(base, new, existing_state="RATIFIED")


class TestGap2RollbackMetadata(unittest.TestCase):
    def _active_store(self, td):
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        entity = obs["entity"]
        from motor_learning.artifacts import candidate_content_hash
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
            candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
            rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]), repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        ent = transition(_entity_with_prior(entity, compiled), RATIFIED, actor=compiled["reviewer"], reason=compiled["rationale"],
                         evidence=compiled["evidence_reviewed"], learning_receipt=r, timestamp=compiled["effective_at"])
        prior = {
            "prior_id": r["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"], "fingerprint": entity["fingerprint"],
            "evidence_refs": entity["evidence_refs"], "source_event_ids": entity["source_event_ids"],
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        stored = store.commit_terminal_bundle(
            prior=prior, learning_receipt=r, ecqr_decision=vecqr,
            candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"], expected_version=1,
        )
        return store, stored, compiled

    def _rb_bundle(self, stored, compiled, **over):
        from motor_learning.ecqr import ECQR_DECISION_SCHEMA
        ed = {
            "schema": ECQR_DECISION_SCHEMA, "kind": "ECQR_DECISION",
            "decision": "ROLLED_BACK",
            "candidate_id": stored["candidate_id"],
            "prior_id": stored["prior_id"],
            "reviewer": "test_reviewer:rollback",
            "rationale": "rollback after regression",
            "evidence_reviewed": ["rollback-evidence"],
            "shadow_result_ref": "shadow:rollback",
            "confidence_before": 0.8, "confidence_after": 0.4,
            "affected_loops": list(compiled["affected_loops"]),
            "applicable_runways": list(compiled["applicable_runways"]),
            "repositories": list(compiled.get("repositories") or []),
            "effective_at": "2026-07-11T12:00:00Z",
            "policy_versions": {"organ": "NF-MOTOR-LEARNING-ORGAN-V1"},
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        }
        ed.update(over)
        return ed

    def test_wrong_target_hash_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._active_store(td)
        ed = self._rb_bundle(stored, compiled, rollback_target_prior_content_hash="WRONG-HASH")
        entity = {"state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
                  "candidate_id": stored["candidate_id"],
                  "transition_history": list(stored["transition_history"])}
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"], evidence_links=ed["evidence_reviewed"],
            confidence_before=ed["confidence_before"], confidence_after=ed["confidence_after"],
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=ed["repositories"], origin_event=ed["evidence_reviewed"][0],
            decision_timestamp=ed["effective_at"], rollback_target=stored["prior_id"],
            snapshot_id=stored["prior_id"], ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash="WRONG-HASH",
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        ent = transition(entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
                         evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"])
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"], "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"], "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": "WRONG-HASH",
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                allow_duplicate=True, expected_version=int(stored["version"]),
            )
        shutil.rmtree(td)

    def test_wrong_target_version_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._active_store(td)
        ed = self._rb_bundle(stored, compiled, rollback_target_version=999)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"], evidence_links=ed["evidence_reviewed"],
            confidence_before=ed["confidence_before"], confidence_after=ed["confidence_after"],
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=ed["repositories"], origin_event=ed["evidence_reviewed"][0],
            decision_timestamp=ed["effective_at"], rollback_target=stored["prior_id"],
            snapshot_id=stored["prior_id"], ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=999,
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {"state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
                  "candidate_id": stored["candidate_id"],
                  "transition_history": list(stored["transition_history"])}
        ent = transition(entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
                         evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"])
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"], "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"], "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": 999,
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                allow_duplicate=True, expected_version=int(stored["version"]),
            )
        shutil.rmtree(td)

    def test_wrong_prior_receipt_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._active_store(td)
        ed = self._rb_bundle(stored, compiled, prior_ratification_receipt_id="WRONG-RECEIPT")
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"], evidence_links=ed["evidence_reviewed"],
            confidence_before=ed["confidence_before"], confidence_after=ed["confidence_after"],
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=ed["repositories"], origin_event=ed["evidence_reviewed"][0],
            decision_timestamp=ed["effective_at"], rollback_target=stored["prior_id"],
            snapshot_id=stored["prior_id"], ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id="WRONG-RECEIPT",
        )
        entity = {"state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
                  "candidate_id": stored["candidate_id"],
                  "transition_history": list(stored["transition_history"])}
        ent = transition(entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
                         evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"])
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"], "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"], "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": "WRONG-RECEIPT",
        })
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                allow_duplicate=True, expected_version=int(stored["version"]),
            )
        shutil.rmtree(td)

    def test_correct_target_bundle_pass(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._active_store(td)
        ed = self._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"], evidence_links=ed["evidence_reviewed"],
            confidence_before=ed["confidence_before"], confidence_after=ed["confidence_after"],
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=ed["repositories"], origin_event=ed["evidence_reviewed"][0],
            decision_timestamp=ed["effective_at"], rollback_target=stored["prior_id"],
            snapshot_id=stored["prior_id"], ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {"state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
                  "candidate_id": stored["candidate_id"],
                  "transition_history": list(stored["transition_history"])}
        ent = transition(entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
                         evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"])
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"], "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"], "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        out = store.commit_terminal_bundle(
            prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
            allow_duplicate=True, expected_version=int(stored["version"]),
        )
        self.assertEqual(out["status"], "rolled_back")
        self.assertFalse(out["live_consumable"])
        shutil.rmtree(td)


class TestGap3EvidenceDerivation(unittest.TestCase):
    def test_identical_mining_shadow_ids_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        # Force overlapping IDs
        mine = list(obs["mining_events_normalized"])
        shadow = [dict(e, event_id=mine[i % len(mine)]["event_id"]) for i, e in enumerate(obs["shadow_events_normalized"])]
        with self.assertRaises(MotorLearningError):
            # Build receipt/prior normally then commit with overlapping shadow events
            entity = obs["entity"]
            from motor_learning.artifacts import candidate_content_hash
            r = build_learning_receipt(
                decision="RATIFIED", prior_id=compiled.get("prior_id") or f"prior-{entity['candidate_id']}",
                candidate_id=entity["candidate_id"], reviewer=compiled["reviewer"],
                rationale=compiled["rationale"], evidence_links=list(compiled["evidence_reviewed"]),
                confidence_before=obs["confidence"]["confidence_before"],
                confidence_after=obs["confidence"]["confidence_after"],
                affected_loops=list(compiled["affected_loops"]),
                applicable_runways=list(compiled["applicable_runways"]), repositories=list(compiled.get("repositories") or []),
                origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
                shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
                shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
                confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
                candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
            )
            ent = transition(_entity_with_prior(entity, compiled), RATIFIED, actor=compiled["reviewer"], reason=compiled["rationale"],
                             evidence=compiled["evidence_reviewed"], learning_receipt=r, timestamp=compiled["effective_at"])
            prior = {
                "prior_id": r["prior_id"], "status": "active", "state": "RATIFIED",
                "action_attempted": entity["fingerprint"].get("action_attempted"),
                "recommended_action": entity["recommended_action"], "scope": entity["scope"],
                "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
                "transition_history": ent["transition_history"], "fingerprint": entity["fingerprint"],
                "evidence_refs": entity["evidence_refs"], "source_event_ids": entity["source_event_ids"],
            }
            store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=shadow, confidence_inputs=obs["confidence_inputs"],
                mining_events=mine, expected_version=1,
            )
        shutil.rmtree(td)

    def test_phantom_confidence_ids_and_inflated_occurrence_blocked(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        bad = dict(obs["confidence_inputs"])
        bad["mining_evidence_ids"] = ["phantom-m1", "phantom-m2", "phantom-m3"]
        with self.assertRaises(GovernanceBlock):
            from motor_learning.artifacts import assert_confidence_inputs_canonical
            assert_confidence_inputs_canonical(bad, candidate=obs["entity"], shadow=obs["shadow_report"])
        bad2 = dict(obs["confidence_inputs"])
        bad2["shadow_evidence_ids"] = ["phantom-s1"]
        with self.assertRaises(GovernanceBlock):
            from motor_learning.artifacts import assert_confidence_inputs_canonical
            assert_confidence_inputs_canonical(bad2, candidate=obs["entity"], shadow=obs["shadow_report"])
        bad3 = dict(obs["confidence_inputs"])
        bad3["occurrence_count"] = int(obs["entity"]["occurrence_count"]) + 10
        with self.assertRaises(GovernanceBlock):
            from motor_learning.artifacts import assert_confidence_inputs_canonical
            assert_confidence_inputs_canonical(bad3, candidate=obs["entity"], shadow=obs["shadow_report"])
        bad4 = dict(obs["confidence_inputs"])
        bad4["outcomes_seen"] = ["failure"]
        with self.assertRaises(GovernanceBlock):
            from motor_learning.artifacts import assert_confidence_inputs_canonical
            assert_confidence_inputs_canonical(bad4, candidate=obs["entity"], shadow=obs["shadow_report"])
        # canonical pass
        from motor_learning.artifacts import assert_confidence_inputs_canonical
        assert_confidence_inputs_canonical(
            obs["confidence_inputs"], candidate=obs["entity"], shadow=obs["shadow_report"]
        )
        shutil.rmtree(td)

    def test_same_evidence_renamed_ids_blocked(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        shadow = json.loads((FIX / "01_repeated_success_ratify" / "shadow_events.json").read_text())
        # Clone mining evidence refs into renamed shadow events
        renamed = []
        for i, ev in enumerate(shadow):
            e = dict(ev)
            e["event_id"] = f"renamed-{i}"
            e["evidence_refs"] = list(events[i % len(events)].get("evidence_refs") or events[i % len(events)].get("evidence_ref") or [])
            if not e["evidence_refs"]:
                # copy raw if present
                src = events[i % len(events)]
                if src.get("raw_evidence_ref"):
                    e["raw_evidence_ref"] = src["raw_evidence_ref"]
            renamed.append(e)
        store = PriorStore(td / "e", create=True)
        # observe with overlapping evidence should block
        obs = observe_phase(events=events, shadow_events=renamed, store=store,
                            out_dir=td / "out", ledger_path=td / "out" / "l.json")
        self.assertTrue(obs.get("blocked_reason"))
        shutil.rmtree(td)


class TestGap4TerminalReceiptECQR(unittest.TestCase):
    def test_rejected_mismatches_blocked(self):
        td = Path(tempfile.mkdtemp())
        # Minimal REJECTED path via fixture 06 then tamper receipt vs ECQR at commit
        s = run_from_fixture_dir(FIX / "06_rejected_candidate", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(s.get("ecqr_decision"), "REJECTED")
        # Direct commit with mismatched evidence
        from motor_learning.ecqr import ECQR_DECISION_SCHEMA, validate_ecqr_decision
        ed = {
            "schema": ECQR_DECISION_SCHEMA, "kind": "ECQR_DECISION",
            "decision": "REJECTED", "candidate_id": "c-rej", "prior_id": "p-rej",
            "reviewer": "test_reviewer:x", "rationale": "ecqr-rationale",
            "evidence_reviewed": ["ecqr-only"], "shadow_result_ref": "shadow:x",
            "confidence_before": 0.9, "confidence_after": 0.1,
            "affected_loops": ["motor_learning_organ_v1"],
            "applicable_runways": ["Software Repair"], "repositories": [],
            "effective_at": "2026-07-10T12:00:00Z", "policy_versions": {"organ": "X"},
        }
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        # evidence mismatch
        r = build_learning_receipt(
            decision="REJECTED", prior_id="p-rej", candidate_id="c-rej",
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=["receipt-only"], confidence_before=0.9, confidence_after=0.1,
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=[], origin_event="ecqr-only", decision_timestamp=ed["effective_at"],
            ecqr_decision_hash=vecqr.decision_hash,
        )
        hist = [
            {"from_state": "OBSERVED", "to_state": "PROPOSED", "actor": "a", "timestamp": "2026-07-10T10:00:00Z",
             "reason": "r", "evidence": [], "learning_receipt_id": None},
            {"from_state": "PROPOSED", "to_state": "REJECTED", "actor": ed["reviewer"],
             "timestamp": ed["effective_at"], "reason": ed["rationale"], "evidence": ed["evidence_reviewed"],
             "learning_receipt_id": r["receipt_id"], "prior_id": "p-rej", "candidate_id": "c-rej"},
        ]
        prior = {
            "prior_id": "p-rej", "status": "rejected", "state": "REJECTED",
            "action_attempted": "x", "recommended_action": "y", "scope": {"loop_id": "motor_learning_organ_v1"},
            "candidate_id": "c-rej", "learning_receipt_id": r["receipt_id"],
            "transition_history": hist,
        }
        store = PriorStore(td / "s2", create=True, store_kind="w1_reference", allow_persist=True)
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(prior=prior, learning_receipt=r, ecqr_decision=vecqr, expected_version=1)
        # confidence mismatch
        r2 = build_learning_receipt(
            decision="REJECTED", prior_id="p-rej", candidate_id="c-rej",
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=ed["evidence_reviewed"], confidence_before=0.2, confidence_after=0.2,
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=[], origin_event="ecqr-only", decision_timestamp=ed["effective_at"],
            ecqr_decision_hash=vecqr.decision_hash,
        )
        hist2 = list(hist)
        hist2[-1] = dict(hist2[-1], learning_receipt_id=r2["receipt_id"])
        prior2 = dict(prior, learning_receipt_id=r2["receipt_id"], transition_history=hist2)
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(prior=prior2, learning_receipt=r2, ecqr_decision=vecqr, expected_version=1)
        # rationale mismatch
        r3 = build_learning_receipt(
            decision="REJECTED", prior_id="p-rej", candidate_id="c-rej",
            reviewer=ed["reviewer"], rationale="different-rationale",
            evidence_links=ed["evidence_reviewed"], confidence_before=0.9, confidence_after=0.1,
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=[], origin_event="ecqr-only", decision_timestamp=ed["effective_at"],
            ecqr_decision_hash=vecqr.decision_hash,
        )
        hist3 = list(hist)
        hist3[-1] = dict(hist3[-1], learning_receipt_id=r3["receipt_id"], reason="different-rationale")
        prior3 = dict(prior, learning_receipt_id=r3["receipt_id"], transition_history=hist3)
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(prior=prior3, learning_receipt=r3, ecqr_decision=vecqr, expected_version=1)
        shutil.rmtree(td)

    def test_rollback_evidence_mismatch_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = TestGap2RollbackMetadata()._active_store(td)
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=["receipt-only"],  # mismatch
            confidence_before=ed["confidence_before"], confidence_after=ed["confidence_after"],
            affected_loops=ed["affected_loops"], applicable_runways=ed["applicable_runways"],
            repositories=ed["repositories"], origin_event="rollback-evidence",
            decision_timestamp=ed["effective_at"], rollback_target=stored["prior_id"],
            snapshot_id=stored["prior_id"], ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {"state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
                  "candidate_id": stored["candidate_id"],
                  "transition_history": list(stored["transition_history"])}
        ent = transition(entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
                         evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"])
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"], "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"], "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                allow_duplicate=True, expected_version=int(stored["version"]),
            )
        shutil.rmtree(td)



class TestPublicBoundaryGapsAQ(unittest.TestCase):
    """Founder adversarial probes A–Q for public-boundary hardening."""

    def _commit_active(self, td):
        store, stored, compiled = TestGap2RollbackMetadata()._active_store(td)
        return store, stored, compiled

    def test_A_active_to_shadow_via_update_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, _ = self._commit_active(td)
        before = store_tree_hash(td / "store")
        body = dict(stored)
        body["status"] = "shadow"
        body["state"] = "SHADOW"
        body["transition_history"] = []
        with self.assertRaises(GovernanceBlock):
            store.update(body)
        self.assertEqual(before, store_tree_hash(td / "store"))
        self.assertEqual(store.get(stored["prior_id"])["status"], "active")
        shutil.rmtree(td)

    def test_B_active_to_observed_via_update_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, _ = self._commit_active(td)
        body = dict(stored)
        body["status"] = "observed"
        body["state"] = "OBSERVED"
        with self.assertRaises(GovernanceBlock):
            store.update(body)
        shutil.rmtree(td)

    def test_C_rejected_to_proposed_via_update_blocked(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        # Seed rejected via fixture-style direct write is blocked on w1_reference;
        # use nonterminal then forge rejected file for update probe only.
        store.create({
            "prior_id": "prior-rej", "status": "proposed", "state": "PROPOSED",
            "action_attempted": "a", "recommended_action": "b",
            "scope": {"loop_id": "motor_learning_organ_v1"},
        })
        # Force rejected status on disk to exercise rewrite block (update path)
        p = store.get("prior-rej")
        p["status"] = "rejected"
        p["state"] = "REJECTED"
        store._prior_path("prior-rej").write_text(json.dumps(p, sort_keys=True) + "\n")
        idx = store._read_index()
        idx["priors"]["prior-rej"]["status"] = "rejected"
        store._write_index(idx)
        body = dict(store.get("prior-rej"))
        body["status"] = "proposed"
        body["state"] = "PROPOSED"
        with self.assertRaises(GovernanceBlock):
            store.update(body)
        shutil.rmtree(td)

    def test_D_rolled_back_to_observed_via_update_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._commit_active(td)
        # Perform legal rollback first
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=list(ed["evidence_reviewed"]),
            confidence_before=float(ed["confidence_before"]),
            confidence_after=float(ed["confidence_after"]),
            affected_loops=list(ed["affected_loops"]),
            applicable_runways=list(ed["applicable_runways"]),
            repositories=list(ed.get("repositories") or []),
            origin_event=ed["evidence_reviewed"][0], decision_timestamp=ed["effective_at"],
            rollback_target=stored["prior_id"], snapshot_id=stored["prior_id"],
            ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {
            "state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
            "candidate_id": stored["candidate_id"],
            "transition_history": list(stored["transition_history"]),
        }
        ent = transition(
            entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
            evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"],
        )
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"],
            "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"],
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        store.commit_terminal_bundle(
            prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
            allow_duplicate=True, expected_version=int(stored["version"]),
        )
        rb = store.get(stored["prior_id"])
        self.assertEqual(rb["status"], "rolled_back")
        body = dict(rb)
        body["status"] = "observed"
        body["state"] = "OBSERVED"
        with self.assertRaises(GovernanceBlock):
            store.update(body)
        shutil.rmtree(td)

    def test_E_existing_update_without_expected_version_blocked(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        store.create({
            "prior_id": "prior-nt", "status": "proposed", "state": "PROPOSED",
            "action_attempted": "a", "recommended_action": "b",
            "scope": {"loop_id": "motor_learning_organ_v1"},
        })
        body = store.get("prior-nt")
        body["status"] = "shadow"
        # create/update path blocks existing entirely; also _persist requires expected_version
        with self.assertRaises(GovernanceBlock):
            store.create(body, expected_version=None)
        with self.assertRaises(GovernanceBlock):
            store._persist_nonterminal(body, allow_duplicate=True, expected_version=None)
        shutil.rmtree(td)

    def test_F_ghost_rollback_no_existing_blocked(self):
        td = Path(tempfile.mkdtemp())
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        prior = {
            "prior_id": "prior-ghost", "status": "rolled_back", "state": "ROLLED_BACK",
            "action_attempted": "a", "recommended_action": "b",
            "scope": {"loop_id": "motor_learning_organ_v1"},
            "candidate_id": "c-ghost",
            "rollback_target_prior_content_hash": "made-up-hash",
            "rollback_target_version": 7,
            "prior_ratification_receipt_id": "lr-made-up-ratification",
            "transition_history": [{
                "from_state": "RATIFIED", "to_state": "ROLLED_BACK", "actor": "a",
                "timestamp": "2026-07-11T12:00:00Z", "reason": "r", "evidence": ["e"],
                "learning_receipt_id": "lr-rb", "prior_id": "prior-ghost", "candidate_id": "c-ghost",
            }],
            "learning_receipt_id": "lr-rb",
        }
        ed = {
            "schema": "nf_motor_learning_ecqr_decision_v1", "kind": "ECQR_DECISION",
            "decision": "ROLLED_BACK", "candidate_id": "c-ghost", "prior_id": "prior-ghost",
            "reviewer": "test_reviewer:x", "rationale": "because evidence",
            "evidence_reviewed": ["e1"], "shadow_result_ref": "s",
            "confidence_before": 0.2, "confidence_after": 0.8,
            "affected_loops": ["motor_learning_organ_v1"],
            "applicable_runways": ["Software Repair"],
            "repositories": ["sina-governance-SSOT"],
            "effective_at": "2026-07-10T12:00:00Z",
            "policy_versions": {"organ": "NF-MOTOR-LEARNING-ORGAN-V1"},
            "rollback_target": "prior-ghost",
            "rollback_target_prior_content_hash": "made-up-hash",
            "rollback_target_version": 7,
            "prior_ratification_receipt_id": "lr-made-up-ratification",
        }
        ghost_receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id="prior-ghost", candidate_id="c-ghost",
            reviewer="test_reviewer:x", rationale="because evidence", evidence_links=["e1"],
            confidence_before=0.2, confidence_after=0.8,
            affected_loops=["motor_learning_organ_v1"],
            applicable_runways=["Software Repair"],
            repositories=["sina-governance-SSOT"],
            origin_event="e1", decision_timestamp="2026-07-10T12:00:00Z",
            rollback_target="prior-ghost", snapshot_id="prior-ghost",
            ecqr_decision_hash="pending",
            rollback_target_prior_content_hash="made-up-hash",
            rollback_target_version=7,
            prior_ratification_receipt_id="lr-made-up-ratification",
        )
        prior["learning_receipt_id"] = ghost_receipt["receipt_id"]
        prior["transition_history"][0]["learning_receipt_id"] = ghost_receipt["receipt_id"]
        with self.assertRaises((GovernanceBlock, MotorLearningError)) as cm:
            store.commit_terminal_bundle(
                prior=prior,
                learning_receipt=ghost_receipt,
                ecqr_decision=ed,
                expected_version=1,
            )
        self.assertIn("existing", str(cm.exception).lower())
        shutil.rmtree(td)

    def test_G_rollback_missing_prior_ratification_receipt_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._commit_active(td)
        # Delete ratification receipt from ledger
        rpath = store.receipts_dir / f"{stored['learning_receipt_id']}.json"
        self.assertTrue(rpath.exists())
        rpath.unlink()
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=list(ed["evidence_reviewed"]),
            confidence_before=float(ed["confidence_before"]),
            confidence_after=float(ed["confidence_after"]),
            affected_loops=list(ed["affected_loops"]),
            applicable_runways=list(ed["applicable_runways"]),
            repositories=list(ed.get("repositories") or []),
            origin_event=ed["evidence_reviewed"][0], decision_timestamp=ed["effective_at"],
            rollback_target=stored["prior_id"], snapshot_id=stored["prior_id"],
            ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {
            "state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
            "candidate_id": stored["candidate_id"],
            "transition_history": list(stored["transition_history"]),
        }
        ent = transition(
            entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
            evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"],
        )
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"],
            "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"],
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        with self.assertRaises(MotorLearningError) as cm:
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                allow_duplicate=True, expected_version=int(stored["version"]),
            )
        self.assertIn("receipt", str(cm.exception).lower())
        shutil.rmtree(td)

    def test_valid_existing_target_rollback_pass(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._commit_active(td)
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=list(ed["evidence_reviewed"]),
            confidence_before=float(ed["confidence_before"]),
            confidence_after=float(ed["confidence_after"]),
            affected_loops=list(ed["affected_loops"]),
            applicable_runways=list(ed["applicable_runways"]),
            repositories=list(ed.get("repositories") or []),
            origin_event=ed["evidence_reviewed"][0], decision_timestamp=ed["effective_at"],
            rollback_target=stored["prior_id"], snapshot_id=stored["prior_id"],
            ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {
            "state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
            "candidate_id": stored["candidate_id"],
            "transition_history": list(stored["transition_history"]),
        }
        ent = transition(
            entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
            evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"],
        )
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"],
            "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"],
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        out = store.commit_terminal_bundle(
            prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
            allow_duplicate=True, expected_version=int(stored["version"]),
        )
        self.assertEqual(out["status"], "rolled_back")
        self.assertEqual(int(out["version"]), int(stored["version"]) + 1)
        shutil.rmtree(td)

    def _tamper_candidate_commit(self, td, mutator):
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        entity = dict(obs["entity"])
        mutator(entity)
        from motor_learning.artifacts import candidate_content_hash
        # Recompute content_hash after tamper so artifact unwrap does not short-circuit first
        entity.pop("content_hash", None)
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled["prior_id"], candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=(entity.get("source_event_ids") or ["x"])[0],
            decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity) if entity.get("fingerprint") else "x",
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        ent = transition(
            _entity_with_prior(entity, compiled), RATIFIED,
            actor=compiled["reviewer"], reason=compiled["rationale"],
            evidence=compiled["evidence_reviewed"], learning_receipt=r, timestamp=compiled["effective_at"],
        )
        prior = {
            "prior_id": compiled["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": (entity.get("fingerprint") or {}).get("action_attempted"),
            "recommended_action": entity.get("recommended_action"), "scope": entity.get("scope"),
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"],
            "fingerprint": entity.get("fingerprint"), "evidence_refs": entity.get("evidence_refs"),
            "source_event_ids": entity.get("source_event_ids"),
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        with self.assertRaises((GovernanceBlock, MotorLearningError, SchemaError)):
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
                mining_events=obs["mining_events_normalized"], expected_version=1,
            )

    def test_H_candidate_ids_differ_from_mining_blocked(self):
        td = Path(tempfile.mkdtemp())
        self._tamper_candidate_commit(td, lambda e: e.update({"source_event_ids": ["c1", "c2", "c3"]}))
        shutil.rmtree(td)

    def test_I_candidate_evidence_refs_differ_blocked(self):
        td = Path(tempfile.mkdtemp())
        self._tamper_candidate_commit(td, lambda e: e.update({"evidence_refs": ["totally-other-ref"]}))
        shutil.rmtree(td)

    def test_J_candidate_action_recovery_differ_blocked(self):
        td = Path(tempfile.mkdtemp())
        def mut(e):
            fp = dict(e.get("fingerprint") or {})
            fp["action_attempted"] = "totally-different-action"
            fp["recovery_path"] = "totally-different-recovery"
            e["fingerprint"] = fp
            e["recommended_action"] = "totally-different-action"
        self._tamper_candidate_commit(td, mut)
        shutil.rmtree(td)

    def test_canonical_rederived_candidate_pass(self):
        from motor_learning.artifacts import assert_candidate_derived_from_mining
        td = Path(tempfile.mkdtemp())
        obs, _, _ = TestExactCrossBind()._ready_bundle(td)
        out = assert_candidate_derived_from_mining(obs["entity"], obs["mining_events_normalized"])
        self.assertEqual(sorted(out["source_event_ids"]), sorted(e["event_id"] for e in obs["mining_events_normalized"]))
        shutil.rmtree(td)

    def _transition_mismatch(self, td, field, bad_value):
        obs, compiled, vecqr = TestExactCrossBind()._ready_bundle(td)
        entity = obs["entity"]
        from motor_learning.artifacts import candidate_content_hash
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled["prior_id"], candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        kwargs = dict(
            actor=compiled["reviewer"], reason=compiled["rationale"],
            evidence=compiled["evidence_reviewed"], learning_receipt=r, timestamp=compiled["effective_at"],
        )
        kwargs[field] = bad_value
        ent = transition(_entity_with_prior(entity, compiled), RATIFIED, **kwargs)
        prior = {
            "prior_id": compiled["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"],
            "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
            "source_event_ids": entity["source_event_ids"],
        }
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr,
                candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
                shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
                mining_events=obs["mining_events_normalized"], expected_version=1,
            )

    def test_K_terminal_transition_actor_mismatch_blocked(self):
        td = Path(tempfile.mkdtemp())
        self._transition_mismatch(td, "actor", "evil-actor")
        shutil.rmtree(td)

    def test_L_terminal_transition_reason_mismatch_blocked(self):
        td = Path(tempfile.mkdtemp())
        self._transition_mismatch(td, "reason", "evil-reason")
        shutil.rmtree(td)

    def test_M_terminal_transition_evidence_mismatch_blocked(self):
        td = Path(tempfile.mkdtemp())
        self._transition_mismatch(td, "evidence", ["evil-evidence"])
        shutil.rmtree(td)

    def test_N_terminal_transition_timestamp_mismatch_blocked(self):
        td = Path(tempfile.mkdtemp())
        self._transition_mismatch(td, "timestamp", "1999-01-01T00:00:00Z")
        shutil.rmtree(td)

    def test_O_same_ecqr_hash_second_prior_id_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._commit_active(td)
        obs, compiled2, vecqr = TestExactCrossBind()._ready_bundle(td / "b2")
        # Force same decision hash by reusing original ECQR body with new prior_id attempt
        # Use stored index binding: commit again with different prior_id but same vecqr
        entity = obs["entity"]
        # Build a second prior using THE SAME ecqr decision hash from first commit
        first_hash = json.loads((td / "store" / "index.json").read_text())["ecqr_decisions"]
        self.assertTrue(first_hash)
        # Re-open first bundle ECQR by reading receipt
        rid = stored["learning_receipt_id"]
        receipt0 = json.loads((td / "store" / "receipts" / f"{rid}.json").read_text())
        dhash = receipt0["ecqr_decision_hash"]
        # Craft second prior id
        from motor_learning.artifacts import candidate_content_hash
        # Need valid ECQR with same hash — only identical body produces same hash.
        # Load original compiled from first active store path via reconstructing from receipt fields
        # Simpler: call commit with allow_duplicate and different prior using same ValidatedECQR from first
        obs1, compiled1, vecqr1 = TestExactCrossBind()._ready_bundle(td / "b1")
        # Re-commit path: take vecqr1, change prior_id in body/receipt/transition but keep decision_hash by
        # using ValidatedECQR wrapper — validate_ecqr recomputes hash from body, so prior_id change changes hash.
        # Instead poke index and try commit that maps different prior to already-bound hash via injecting
        # into commit after validation — the check uses vecqr.decision_hash.
        # Strategy: seed index ecqr_decisions[hash]=prior-one, then commit prior-two with freshly compiled
        # decision that we force-equal by writing index with the NEW decision hash already mapped to prior-one.
        entity = obs1["entity"]
        r = build_learning_receipt(
            decision="RATIFIED", prior_id="prior-two", candidate_id=entity["candidate_id"],
            reviewer=compiled1["reviewer"], rationale=compiled1["rationale"],
            evidence_links=list(compiled1["evidence_reviewed"]),
            confidence_before=obs1["confidence"]["confidence_before"],
            confidence_after=obs1["confidence"]["confidence_after"],
            affected_loops=list(compiled1["affected_loops"]),
            applicable_runways=list(compiled1["applicable_runways"]),
            repositories=list(compiled1.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled1["effective_at"],
            shadow_id=obs1["shadow_report"]["shadow_id"], shadow_hash=obs1["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs1["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs1["confidence"]["content_hash"], ecqr_decision_hash=vecqr1.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs1),
            prior_payload_hash=_pph(compiled1, entity),
        )
        # Pre-bind this decision hash to a different prior_id
        idx = store._read_index()
        idx.setdefault("ecqr_decisions", {})[vecqr1.decision_hash] = "prior-one"
        store._write_index(idx)
        compiled1 = dict(compiled1)
        compiled1["prior_id"] = "prior-two"
        from motor_learning.artifacts import compute_prior_payload_hash
        compiled1["prior_payload_hash"] = compute_prior_payload_hash(
            candidate=entity, prior_id="prior-two", status="active", state="RATIFIED",
        )
        # Revalidate ECQR with prior-two
        vecqr2 = validate_ecqr_decision(
            compiled1, confidence=obs1["confidence"], shadow=obs1["shadow_report"], candidate=entity,
            shadow_events=obs1["shadow_events_normalized"], confidence_inputs=obs1["confidence_inputs"],
            mining_events=obs1["mining_events_normalized"],
        )
        # If prior_id is in hash, hashes differ — rebind using vecqr2.decision_hash
        idx = store._read_index()
        idx["ecqr_decisions"][vecqr2.decision_hash] = "prior-one"
        store._write_index(idx)
        r = build_learning_receipt(
            decision="RATIFIED", prior_id="prior-two", candidate_id=entity["candidate_id"],
            reviewer=compiled1["reviewer"], rationale=compiled1["rationale"],
            evidence_links=list(compiled1["evidence_reviewed"]),
            confidence_before=obs1["confidence"]["confidence_before"],
            confidence_after=obs1["confidence"]["confidence_after"],
            affected_loops=list(compiled1["affected_loops"]),
            applicable_runways=list(compiled1["applicable_runways"]),
            repositories=list(compiled1.get("repositories") or []),
            origin_event=entity["source_event_ids"][0], decision_timestamp=compiled1["effective_at"],
            shadow_id=obs1["shadow_report"]["shadow_id"], shadow_hash=obs1["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs1["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs1["confidence"]["content_hash"], ecqr_decision_hash=vecqr2.decision_hash,
            candidate_hash=candidate_content_hash(entity), mining_evidence_manifest_hash=_mine_hash(obs1),
            prior_payload_hash=_pph(compiled1, entity),
        )
        ent = transition(
            _entity_with_prior(entity, compiled1, prior_id="prior-two"), RATIFIED,
            actor=compiled1["reviewer"], reason=compiled1["rationale"],
            evidence=compiled1["evidence_reviewed"], learning_receipt=r, timestamp=compiled1["effective_at"],
        )
        prior = {
            "prior_id": "prior-two", "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"], "scope": entity["scope"],
            "candidate_id": entity["candidate_id"], "learning_receipt_id": r["receipt_id"],
            "transition_history": ent["transition_history"],
            "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
            "source_event_ids": entity["source_event_ids"],
        }
        with self.assertRaises(MotorLearningError) as cm:
            store.commit_terminal_bundle(
                prior=prior, learning_receipt=r, ecqr_decision=vecqr2,
                candidate=entity, shadow=obs1["shadow_report"], confidence=obs1["confidence"],
                shadow_events=obs1["shadow_events_normalized"], confidence_inputs=obs1["confidence_inputs"],
                mining_events=obs1["mining_events_normalized"], expected_version=1,
            )
        self.assertIn("already bound", str(cm.exception).lower())
        shutil.rmtree(td)

    def test_deterministic_prior_id(self):
        td = Path(tempfile.mkdtemp())
        obs, compiled, _ = TestExactCrossBind()._ready_bundle(td)
        self.assertEqual(compiled["prior_id"], f"prior-{obs['entity']['candidate_id']}")
        shutil.rmtree(td)

    def test_P_cross_run_event_collision_different_out_dirs(self):
        td = Path(tempfile.mkdtemp())
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        # First persist registers durable ledger
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        from motor_learning.event_registry import EventRegistry
        from motor_learning.normalize import normalize_many
        norm, _dups = normalize_many(events)
        # Seed durable ledger with first event
        e0 = norm[0]
        ledger = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {
            e0["event_id"]: {
                "content_hash": e0["content_hash"],
                "provenance_fingerprint": e0.get("provenance_fingerprint") or e0["content_hash"],
            }
        }}
        (td / "store" / "event_identity_ledger.json").write_text(json.dumps(ledger, sort_keys=True) + "\n")
        # Second out_dir: same event_id, different provenance must fail during observe/normalize register
        bad = dict(e0)
        # mutate raw so provenance differs but keep event_id
        raw_events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        raw_events[0] = dict(raw_events[0])
        raw_events[0]["outcome"] = "failure"  # change content
        # Separate out_dir: load durable ledger then collide on same event_id
        import shutil as _sh
        (td / "out2").mkdir(parents=True)
        _sh.copy2(td / "store" / "event_identity_ledger.json", td / "out2" / "ledger.json")
        reg = EventRegistry(td / "out2" / "ledger.json")
        n2, _ = normalize_many(raw_events)
        with self.assertRaises(GovernanceBlock):
            for ev in n2:
                reg.register(ev["event_id"], ev["content_hash"], provenance=ev.get("provenance_fingerprint"))
        # Separate-run duplicate (same provenance) is idempotent
        (td / "out3").mkdir(parents=True, exist_ok=True)
        _sh.copy2(td / "store" / "event_identity_ledger.json", td / "out3" / "ledger.json")
        reg2 = EventRegistry(td / "out3" / "ledger.json")
        n_ok, _ = normalize_many(events)
        for ev in n_ok:
            # only first event is in durable ledger; registering same is ok
            if ev["event_id"] == e0["event_id"]:
                self.assertEqual(reg2.register(ev["event_id"], ev["content_hash"],
                                               provenance=ev.get("provenance_fingerprint") or ev["content_hash"]),
                                 "duplicate")
        shutil.rmtree(td)

    def test_failed_transaction_ledger_restoration(self):
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._commit_active(td)
        before_ledger = None
        lp = td / "store" / "event_identity_ledger.json"
        if lp.exists():
            before_ledger = lp.read_text()
        else:
            before_ledger = ""
            lp.write_text(json.dumps({"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {}}) + "\n")
            before_ledger = lp.read_text()
        before_hash = store_tree_hash(td / "store")
        # Attempt rollback with inject failure after index (includes ledger stage)
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=list(ed["evidence_reviewed"]),
            confidence_before=float(ed["confidence_before"]),
            confidence_after=float(ed["confidence_after"]),
            affected_loops=list(ed["affected_loops"]),
            applicable_runways=list(ed["applicable_runways"]),
            repositories=list(ed.get("repositories") or []),
            origin_event=ed["evidence_reviewed"][0], decision_timestamp=ed["effective_at"],
            rollback_target=stored["prior_id"], snapshot_id=stored["prior_id"],
            ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {
            "state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
            "candidate_id": stored["candidate_id"],
            "transition_history": list(stored["transition_history"]),
        }
        ent = transition(
            entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
            evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"],
        )
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"],
            "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"],
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        evil_ledger = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {"evil": {"content_hash": "x", "provenance_fingerprint": "x"}}}
        with self.assertRaises(MotorLearningError):
            store.commit_terminal_bundle(
                prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                allow_duplicate=True, expected_version=int(stored["version"]),
                event_ledger_update=evil_ledger,
                inject_failure_after="after_index",
            )
        self.assertEqual(before_hash, store_tree_hash(td / "store"))
        self.assertEqual(lp.read_text(), before_ledger)
        shutil.rmtree(td)

    def test_Q_concurrent_same_version_one_success(self):
        import threading
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = self._commit_active(td)
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=list(ed["evidence_reviewed"]),
            confidence_before=float(ed["confidence_before"]),
            confidence_after=float(ed["confidence_after"]),
            affected_loops=list(ed["affected_loops"]),
            applicable_runways=list(ed["applicable_runways"]),
            repositories=list(ed.get("repositories") or []),
            origin_event=ed["evidence_reviewed"][0], decision_timestamp=ed["effective_at"],
            rollback_target=stored["prior_id"], snapshot_id=stored["prior_id"],
            ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {
            "state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
            "candidate_id": stored["candidate_id"],
            "transition_history": list(stored["transition_history"]),
        }
        ent = transition(
            entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
            evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"],
        )
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"],
            "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"],
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        results = []
        barrier = threading.Barrier(2)

        def worker(label):
            barrier.wait()
            try:
                store.commit_terminal_bundle(
                    prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                    allow_duplicate=True, expected_version=int(stored["version"]),
                )
                results.append((label, "success"))
            except Exception as exc:
                results.append((label, f"fail:{exc}"))

        t1 = threading.Thread(target=worker, args=("A",))
        t2 = threading.Thread(target=worker, args=("B",))
        t1.start(); t2.start(); t1.join(); t2.join()
        successes = [r for r in results if r[1] == "success"]
        fails = [r for r in results if r[1] != "success"]
        self.assertEqual(len(successes), 1, results)
        self.assertEqual(len(fails), 1, results)
        final = store.get(stored["prior_id"])
        self.assertEqual(int(final["version"]), int(stored["version"]) + 1)
        shutil.rmtree(td)


class TestMaturityPromotionGate(unittest.TestCase):
    def test_maturity_rows_match_probe_closure(self):
        lock = json.loads((ROOT / "data" / "nf_motor_learning_organ_v1_LOCKED.json").read_text())
        m = lock["implementation_maturity"]
        required = {
            "executable_reference_pipeline": "IMPLEMENTED",
            "lifecycle_anchoring_in_terminal_commit": "IMPLEMENTED",
            "immutable_history_across_public_apis": "IMPLEMENTED",
            "rollback_existing_target_requirement": "IMPLEMENTED",
            "candidate_mining_derivation": "IMPLEMENTED",
            "terminal_transition_ecqr_receipt_binding": "IMPLEMENTED",
            "ecqr_prior_identity_binding": "IMPLEMENTED",
            "durable_cross_run_event_identity": "IMPLEMENTED",
            "concurrent_cas_enforcement": "IMPLEMENTED",
            "w1_live_consumable": "FORBIDDEN",
            "reviewer_authentication": "NOT_IMPLEMENTED",
            "w2_activation": "NOT_IMPLEMENTED",
            "model_learning": "FORBIDDEN",
            "data_runway": "HOLD",
        }
        for k, v in required.items():
            self.assertEqual(m.get(k), v, f"maturity.{k}")



class TestFreshnessPatchSetSix(unittest.TestCase):
    """Required probes for canonical identity, prior payload, provenance, ledger, missing-store, lock."""

    def _ready(self, td):
        return TestExactCrossBind()._ready_bundle(td)

    def _commit_kwargs(self, obs, compiled, vecqr, entity, prior, receipt):
        return dict(
            prior=prior, learning_receipt=receipt, ecqr_decision=vecqr,
            candidate=entity, shadow=obs["shadow_report"], confidence=obs["confidence"],
            shadow_events=obs["shadow_events_normalized"], confidence_inputs=obs["confidence_inputs"],
            mining_events=obs["mining_events_normalized"], expected_version=1,
        )

    def _build_active_attempt(self, td, mut_prior=None):
        obs, compiled, vecqr = self._ready(td)
        entity = obs["entity"]
        from motor_learning.artifacts import candidate_content_hash
        r = build_learning_receipt(
            decision="RATIFIED", prior_id=compiled["prior_id"], candidate_id=entity["candidate_id"],
            reviewer=compiled["reviewer"], rationale=compiled["rationale"],
            evidence_links=list(compiled["evidence_reviewed"]),
            confidence_before=obs["confidence"]["confidence_before"],
            confidence_after=obs["confidence"]["confidence_after"],
            affected_loops=list(compiled["affected_loops"]),
            applicable_runways=list(compiled["applicable_runways"]),
            repositories=list(compiled.get("repositories") or []),
            origin_event=entity["source_event_ids"][0],
            decision_timestamp=compiled["effective_at"],
            shadow_id=obs["shadow_report"]["shadow_id"], shadow_hash=obs["shadow_report"]["content_hash"],
            shadow_evidence_manifest_hash=obs["shadow_report"]["evidence_manifest_hash"],
            confidence_hash=obs["confidence"]["content_hash"], ecqr_decision_hash=vecqr.decision_hash,
            candidate_hash=candidate_content_hash(entity),
            mining_evidence_manifest_hash=_mine_hash(obs),
            prior_payload_hash=_pph(compiled, entity),
        )
        ent = transition(
            _entity_with_prior(entity, compiled), RATIFIED,
            actor=compiled["reviewer"], reason=compiled["rationale"],
            evidence=compiled["evidence_reviewed"], learning_receipt=r, timestamp=compiled["effective_at"],
        )
        prior = {
            "prior_id": compiled["prior_id"], "status": "active", "state": "RATIFIED",
            "action_attempted": entity["fingerprint"].get("action_attempted"),
            "recommended_action": entity["recommended_action"],
            "scope": entity["scope"], "candidate_id": entity["candidate_id"],
            "learning_receipt_id": r["receipt_id"], "transition_history": ent["transition_history"],
            "fingerprint": entity["fingerprint"], "evidence_refs": entity["evidence_refs"],
            "source_event_ids": entity["source_event_ids"],
        }
        if mut_prior:
            mut_prior(prior)
        store = PriorStore(td / "store", create=True, store_kind="w1_reference", allow_persist=True)
        return store, obs, compiled, vecqr, entity, prior, r

    def test_renamed_canonical_candidate_blocked(self):
        from motor_learning.artifacts import assert_candidate_derived_from_mining
        td = Path(tempfile.mkdtemp())
        obs, compiled, vecqr = self._ready(td)
        entity = dict(obs["entity"])
        entity["candidate_id"] = "cand-RENAMED-ATTACKER"
        with self.assertRaises(GovernanceBlock) as cm:
            assert_candidate_derived_from_mining(entity, obs["mining_events_normalized"])
        self.assertIn("not among derived", str(cm.exception))
        store, _o, _c, _v, _e, prior, r = self._build_active_attempt(td / "ok")
        with self.assertRaises((GovernanceBlock, MotorLearningError)):
            store.commit_terminal_bundle(**self._commit_kwargs(obs, compiled, vecqr, entity, prior, r))
        shutil.rmtree(td)

    def test_alternate_candidate_id_same_pattern_blocked(self):
        from motor_learning.artifacts import assert_candidate_derived_from_mining
        td = Path(tempfile.mkdtemp())
        obs, _, _ = self._ready(td)
        bad = dict(obs["entity"])
        bad["candidate_id"] = "cand-" + ("0" * 16)
        with self.assertRaises(GovernanceBlock) as cm:
            assert_candidate_derived_from_mining(bad, obs["mining_events_normalized"])
        self.assertIn("not among derived", str(cm.exception))
        shutil.rmtree(td)

    def test_modified_prior_recommended_action_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, obs, compiled, vecqr, entity, prior, r = self._build_active_attempt(
            td, mut_prior=lambda p: p.update({"recommended_action": "EVIL_OVERRIDE"}),
        )
        with self.assertRaises(MotorLearningError) as cm:
            store.commit_terminal_bundle(**self._commit_kwargs(obs, compiled, vecqr, entity, prior, r))
        self.assertIn("recommended_action", str(cm.exception).lower())
        shutil.rmtree(td)

    def test_modified_prior_state_status_blocked(self):
        td = Path(tempfile.mkdtemp())
        store, obs, compiled, vecqr, entity, prior, r = self._build_active_attempt(
            td, mut_prior=lambda p: p.update({"state": "PROPOSED", "status": "active"}),
        )
        with self.assertRaises(MotorLearningError) as cm:
            store.commit_terminal_bundle(**self._commit_kwargs(obs, compiled, vecqr, entity, prior, r))
        self.assertIn("state", str(cm.exception).lower())
        shutil.rmtree(td)

    def test_stale_content_hash_after_field_change_blocked(self):
        from motor_learning.artifacts import assert_normalized_event_provenance
        td = Path(tempfile.mkdtemp())
        obs, _, _ = self._ready(td)
        ev = dict(obs["mining_events_normalized"][0])
        ev["action_attempted"] = "totally-different-action"
        with self.assertRaises(GovernanceBlock) as cm:
            assert_normalized_event_provenance(ev, label="mining")
        self.assertIn("stale", str(cm.exception).lower())
        shutil.rmtree(td)

    def test_stale_provenance_fingerprint_blocked(self):
        from motor_learning.artifacts import assert_normalized_event_provenance
        td = Path(tempfile.mkdtemp())
        obs, _, _ = self._ready(td)
        ev = dict(obs["shadow_events_normalized"][0])
        ev["recovery_path"] = "evil-recovery"
        with self.assertRaises(GovernanceBlock):
            assert_normalized_event_provenance(ev, label="shadow")
        shutil.rmtree(td)

    def test_ledger_update_removing_history_blocked(self):
        from motor_learning.artifacts import merge_event_identity_ledger
        durable = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {
            "e1": {"content_hash": "a", "provenance_fingerprint": "a"},
            "e2": {"content_hash": "b", "provenance_fingerprint": "b"},
        }}
        update = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {
            "e1": {"content_hash": "a", "provenance_fingerprint": "a"},
        }}
        with self.assertRaises(GovernanceBlock) as cm:
            merge_event_identity_ledger(durable, update)
        self.assertIn("removes", str(cm.exception).lower())

    def test_ledger_update_changing_historic_identity_blocked(self):
        from motor_learning.artifacts import merge_event_identity_ledger
        durable = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {
            "e1": {"content_hash": "a", "provenance_fingerprint": "a"},
        }}
        update = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {
            "e1": {"content_hash": "CHANGED", "provenance_fingerprint": "CHANGED"},
        }}
        with self.assertRaises(GovernanceBlock) as cm:
            merge_event_identity_ledger(durable, update)
        self.assertIn("historic", str(cm.exception).lower())

    def test_concurrent_distinct_prior_ledger_union(self):
        import threading
        import time
        td = Path(tempfile.mkdtemp())
        store_root = td / "store"
        store = PriorStore(store_root, create=True, store_kind="w1_reference", allow_persist=True)
        (store_root / "event_identity_ledger.json").write_text(json.dumps({
            "schema": "nf_motor_learning_event_identity_ledger_v1",
            "events": {"seed": {"content_hash": "s", "provenance_fingerprint": "s"}},
        }, sort_keys=True) + "\n")
        from motor_learning.artifacts import merge_event_identity_ledger
        results = []
        barrier = threading.Barrier(2)

        def worker(eid):
            barrier.wait()
            lf = None
            for _ in range(200):
                try:
                    lf = store._acquire_writer_lock()
                    break
                except GovernanceBlock:
                    time.sleep(0.01)
            assert lf is not None
            try:
                durable2 = json.loads((store_root / "event_identity_ledger.json").read_text())
                upd = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {
                    **durable2["events"],
                    eid: {"content_hash": eid, "provenance_fingerprint": eid},
                }}
                merged2 = merge_event_identity_ledger(durable2, upd)
                (store_root / "event_identity_ledger.json").write_text(json.dumps(merged2, sort_keys=True) + "\n")
                results.append(eid)
            finally:
                store._release_writer_lock(lf)

        t1 = threading.Thread(target=worker, args=("a1",))
        t2 = threading.Thread(target=worker, args=("b2",))
        t1.start(); t2.start(); t1.join(); t2.join()
        final = json.loads((store_root / "event_identity_ledger.json").read_text())["events"]
        self.assertIn("seed", final)
        self.assertIn("a1", final)
        self.assertIn("b2", final)
        shutil.rmtree(td)

    def test_failed_direct_commit_missing_store_stays_missing(self):
        td = Path(tempfile.mkdtemp())
        store_path = td / "never-created-store"
        store = PriorStore(store_path, create=False, store_kind="w1_reference", allow_persist=True)
        self.assertFalse(store_path.exists())
        with self.assertRaises((GovernanceBlock, MotorLearningError, SchemaError)):
            store.commit_terminal_bundle(
                prior={"prior_id": "p", "status": "active", "state": "RATIFIED",
                       "transition_history": [], "candidate_id": "c"},
                learning_receipt={"receipt_id": "x"},
                ecqr_decision={"decision": "RATIFIED"},
                expected_version=1,
            )
        self.assertFalse(store_path.exists(), "store must remain nonexistent")
        kids = list(store_path.parent.glob("never-created-store*"))
        self.assertEqual(kids, [])
        shutil.rmtree(td)

    def test_writer_B_after_root_swap_before_release_blocked(self):
        import threading
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = TestGap2RollbackMetadata()._active_store(td)
        lf = store._acquire_writer_lock()
        live_tmp = Path(str(store.root) + ".mlo_replacing")
        store.root.rename(live_tmp)
        staging = Path(tempfile.mkdtemp(prefix="mlo-stage-"))
        shutil.copytree(live_tmp, staging, dirs_exist_ok=True)
        staging.rename(store.root)
        shutil.rmtree(live_tmp)
        results = []

        def try_b():
            try:
                store._acquire_writer_lock()
                results.append("acquired")
            except Exception as exc:
                results.append(f"blocked:{exc}")

        t = threading.Thread(target=try_b)
        t.start(); t.join()
        store._release_writer_lock(lf)
        self.assertTrue(results and results[0].startswith("blocked"), results)
        self.assertEqual(store._lock_path(), store.root.parent / f".{store.root.name}.mlo-writer.lock")
        shutil.rmtree(td)

    def test_same_prior_concurrency_one_version_increment(self):
        import threading
        td = Path(tempfile.mkdtemp())
        store, stored, compiled = TestGap2RollbackMetadata()._active_store(td)
        ed = TestGap2RollbackMetadata()._rb_bundle(stored, compiled)
        from motor_learning.ecqr import validate_ecqr_decision
        vecqr = validate_ecqr_decision(ed, require_bound_artifacts=False)
        receipt = build_learning_receipt(
            decision="ROLLED_BACK", prior_id=stored["prior_id"], candidate_id=stored["candidate_id"],
            reviewer=ed["reviewer"], rationale=ed["rationale"],
            evidence_links=list(ed["evidence_reviewed"]),
            confidence_before=float(ed["confidence_before"]),
            confidence_after=float(ed["confidence_after"]),
            affected_loops=list(ed["affected_loops"]),
            applicable_runways=list(ed["applicable_runways"]),
            repositories=list(ed.get("repositories") or []),
            origin_event=ed["evidence_reviewed"][0], decision_timestamp=ed["effective_at"],
            rollback_target=stored["prior_id"], snapshot_id=stored["prior_id"],
            ecqr_decision_hash=vecqr.decision_hash,
            rollback_target_prior_content_hash=stored["content_hash"],
            rollback_target_version=int(stored["version"]),
            prior_ratification_receipt_id=stored["learning_receipt_id"],
        )
        entity = {
            "state": "RATIFIED", "status": "active", "prior_id": stored["prior_id"],
            "candidate_id": stored["candidate_id"],
            "transition_history": list(stored["transition_history"]),
        }
        ent = transition(
            entity, ROLLED_BACK, actor=ed["reviewer"], reason=ed["rationale"],
            evidence=ed["evidence_reviewed"], learning_receipt=receipt, timestamp=ed["effective_at"],
        )
        updated = dict(stored)
        updated.update({
            "state": ent["state"], "status": ent["status"],
            "transition_history": ent["transition_history"],
            "learning_receipt_id": receipt["receipt_id"],
            "rollback_target": stored["prior_id"],
            "rollback_target_prior_content_hash": stored["content_hash"],
            "rollback_target_version": int(stored["version"]),
            "prior_ratification_receipt_id": stored["learning_receipt_id"],
        })
        results = []
        barrier = threading.Barrier(2)

        def worker(label):
            barrier.wait()
            try:
                store.commit_terminal_bundle(
                    prior=updated, learning_receipt=receipt, ecqr_decision=vecqr,
                    allow_duplicate=True, expected_version=int(stored["version"]),
                )
                results.append((label, "success"))
            except Exception as exc:
                results.append((label, f"fail:{exc}"))

        t1 = threading.Thread(target=worker, args=("A",))
        t2 = threading.Thread(target=worker, args=("B",))
        t1.start(); t2.start(); t1.join(); t2.join()
        self.assertEqual(sum(1 for r in results if r[1] == "success"), 1, results)
        self.assertEqual(int(store.get(stored["prior_id"])["version"]), int(stored["version"]) + 1)
        shutil.rmtree(td)


class TestMaturityFreshnessSix(unittest.TestCase):
    def test_maturity_six_patch_rows(self):
        lock = json.loads((ROOT / "data" / "nf_motor_learning_organ_v1_LOCKED.json").read_text())
        m = lock["implementation_maturity"]
        required = {
            "canonical_candidate_identity": "IMPLEMENTED",
            "prior_payload_candidate_binding": "IMPLEMENTED",
            "normalized_event_provenance_validation": "IMPLEMENTED",
            "event_ledger_monotonicity": "IMPLEMENTED",
            "failed_direct_commit_restoration": "IMPLEMENTED",
            "stable_cross_root_writer_lock": "IMPLEMENTED",
            "concurrent_cas_enforcement": "IMPLEMENTED",
            "w1_live_consumable": "FORBIDDEN",
            "reviewer_authentication": "NOT_IMPLEMENTED",
            "w2_activation": "NOT_IMPLEMENTED",
            "model_learning": "FORBIDDEN",
            "data_runway": "HOLD",
        }
        for k, v in required.items():
            self.assertEqual(m.get(k), v, f"maturity.{k}")

if __name__ == "__main__":
    unittest.main()
