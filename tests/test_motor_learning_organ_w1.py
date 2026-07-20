#!/usr/bin/env python3
"""Motor Learning Organ W1 — unit + fixture governance tests."""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from motor_learning.normalize import normalize_event, normalize_many  # noqa: E402
from motor_learning.extract import extract_signal  # noqa: E402
from motor_learning.mine import mine_patterns  # noqa: E402
from motor_learning.similarity import compare, rank  # noqa: E402
from motor_learning.confidence import compute_confidence, RATIFY_THRESHOLD  # noqa: E402
from motor_learning.lifecycle import (  # noqa: E402
    transition, OBSERVED, PROPOSED, SHADOW, RATIFIED, REJECTED, ROLLED_BACK,
)
from motor_learning.shadow import evaluate_shadow  # noqa: E402
from motor_learning.ecqr import validate_ecqr_decision  # noqa: E402
from motor_learning.receipt import build_learning_receipt, validate_learning_receipt  # noqa: E402
from motor_learning.prior_store import PriorStore  # noqa: E402
from motor_learning.orchestrator import run_from_fixture_dir, run_pipeline  # noqa: E402
from motor_learning.errors import IllegalTransition, GovernanceBlock, SchemaError  # noqa: E402

FIX = ROOT / "fixtures" / "motor_learning_w1"


def _load(name: str):
    return json.loads((FIX / name).read_text()) if (FIX / name).exists() else None


class TestNormalize(unittest.TestCase):
    def test_rejects_malformed(self):
        with self.assertRaises(SchemaError):
            normalize_event({"event_id": "x"})

    def test_deterministic_hash(self):
        raw = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())[0]
        a = normalize_event(raw)
        b = normalize_event(raw)
        self.assertEqual(a["content_hash"], b["content_hash"])
        self.assertEqual(a["idempotency_key"], b["idempotency_key"])

    def test_duplicate_idempotent(self):
        events = json.loads((FIX / "10_duplicate_event" / "events.json").read_text())
        accepted, dups = normalize_many(events)
        self.assertEqual(len(dups), 1)
        self.assertEqual(len(accepted), 3)


class TestSimilarity(unittest.TestCase):
    def setUp(self):
        events = json.loads((FIX / "01_repeated_success_ratify" / "events.json").read_text())
        from motor_learning.normalize import normalize_event
        from motor_learning.extract import extract_signal
        self.sig = extract_signal(normalize_event(events[0]))
        self.prior = {
            "prior_id": "p1",
            "fingerprint": dict(self.sig["fingerprint"]),
            "scope": self.sig["scope"],
        }

    def test_exact_match(self):
        r = compare(self.sig, self.prior)
        self.assertGreaterEqual(r["total_score"], 0.9)
        self.assertTrue(r["passes_threshold"])
        self.assertFalse(r["promotion_authority"])

    def test_near_match(self):
        prior = dict(self.prior)
        prior["fingerprint"] = dict(self.sig["fingerprint"])
        prior["fingerprint"]["stage"] = "other_stage"
        r = compare(self.sig, prior)
        self.assertGreater(r["total_score"], 0.5)
        self.assertLess(r["total_score"], 1.0)

    def test_materially_different(self):
        prior = dict(self.prior)
        prior["fingerprint"] = {
            "action_attempted": "totally_other",
            "outcome": "failure",
            "error_class": "other",
            "recovery_path": "x",
            "runway": "Video",
            "repository": "other",
            "stage": "x",
            "loop_id": "other",
        }
        r = compare(self.sig, prior)
        self.assertLess(r["total_score"], 0.3)

    def test_contradictory_outcome(self):
        prior = dict(self.prior)
        prior["fingerprint"] = dict(self.sig["fingerprint"])
        prior["fingerprint"]["outcome"] = "failure"
        r = compare(self.sig, prior)
        self.assertIn("outcome", r["conflicting_fields"])
        self.assertFalse(r["passes_threshold"])

    def test_deterministic_repeat(self):
        a = compare(self.sig, self.prior)
        b = compare(self.sig, self.prior)
        self.assertEqual(a["total_score"], b["total_score"])
        self.assertEqual(a["explanation"], b["explanation"])


class TestConfidence(unittest.TestCase):
    def test_insufficient_evidence(self):
        c = compute_confidence(occurrence_count=1, outcomes_seen=["success"], evidence_refs=["e1"])
        self.assertLess(c["confidence_after"], RATIFY_THRESHOLD)
        self.assertFalse(c["meets_ratify_threshold"])
        self.assertFalse(c["promotion_authority"])

    def test_contradictory(self):
        c = compute_confidence(occurrence_count=4, outcomes_seen=["success", "failure"], evidence_refs=["a", "b"])
        self.assertFalse(c["meets_ratify_threshold"])

    def test_expired_evidence(self):
        c = compute_confidence(occurrence_count=5, outcomes_seen=["success"], evidence_refs=["a"], expired_evidence=True)
        self.assertFalse(c["meets_ratify_threshold"])

    def test_repeated_success_with_shadow(self):
        shadow = {"success_rate": 1.0, "result": "success", "successes": 4, "failures": 0, "total": 4}
        c = compute_confidence(
            occurrence_count=4, outcomes_seen=["success"], evidence_refs=["a", "b", "c", "d"],
            shadow_report=shadow, scope={"loop_id": "x", "runway": "y", "repository": "z"},
        )
        self.assertGreaterEqual(c["confidence_after"], RATIFY_THRESHOLD)
        self.assertTrue(c["meets_ratify_threshold"])

    def test_decrease_after_failure(self):
        before = 0.8
        c = compute_confidence(
            occurrence_count=4, outcomes_seen=["success"], evidence_refs=["a"],
            shadow_report={"result": "failure", "success_rate": 0.1, "successes": 0, "failures": 3, "total": 3},
            confidence_before=before,
        )
        self.assertLessEqual(c["confidence_after"], before)

    def test_range(self):
        c = compute_confidence(occurrence_count=100, outcomes_seen=["success"], evidence_refs=["a"] * 10,
                               shadow_report={"success_rate": 1.0, "result": "success", "successes": 10, "failures": 0, "total": 10})
        self.assertGreaterEqual(c["confidence_after"], 0.0)
        self.assertLessEqual(c["confidence_after"], 1.0)

    def test_deterministic(self):
        kwargs = dict(occurrence_count=3, outcomes_seen=["success"], evidence_refs=["a", "b", "c"])
        self.assertEqual(compute_confidence(**kwargs)["confidence_after"], compute_confidence(**kwargs)["confidence_after"])


class TestLifecycle(unittest.TestCase):
    def test_illegal_observed_to_ratified(self):
        with self.assertRaises(IllegalTransition):
            transition({"state": OBSERVED}, RATIFIED, actor="t", reason="nope", learning_receipt_id="x")

    def test_illegal_proposed_to_ratified(self):
        with self.assertRaises(IllegalTransition):
            transition({"state": PROPOSED}, RATIFIED, actor="t", reason="nope", learning_receipt_id="x")

    def test_ratify_requires_receipt(self):
        e = transition({"state": PROPOSED, "evidence_refs": []}, SHADOW, actor="t", reason="shadow", require_receipt=False)
        with self.assertRaises(GovernanceBlock):
            transition(e, RATIFIED, actor="t", reason="ratify")

    def test_happy_path_with_receipt(self):
        e = {"state": PROPOSED, "evidence_refs": ["e"]}
        e = transition(e, SHADOW, actor="t", reason="shadow", require_receipt=False)
        e = transition(e, RATIFIED, actor="t", reason="ok", learning_receipt_id="lr-1", evidence=["e"])
        self.assertEqual(e["state"], RATIFIED)


class TestReceipt(unittest.TestCase):
    def _valid(self, **over):
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
        )
        base.update(over)
        return build_learning_receipt(**base)

    def test_valid_receipt(self):
        r = self._valid()
        validate_learning_receipt(r)

    def test_invalid_missing_reviewer(self):
        r = self._valid()
        r["reviewer"] = ""
        with self.assertRaises(GovernanceBlock):
            validate_learning_receipt(r)

    def test_invalid_missing_evidence(self):
        with self.assertRaises(SchemaError):
            self._valid(evidence_links=[])

    def test_reject_and_rollback_receipts(self):
        for d in ("REJECTED", "ROLLED_BACK"):
            r = self._valid(decision=d, rollback_target="p1" if d == "ROLLED_BACK" else None)
            validate_learning_receipt(r)
            self.assertIn(r["decision"], ("rejected", "rolled_back"))


class TestPipelineFixtures(unittest.TestCase):
    def _run(self, case: str):
        td = Path(tempfile.mkdtemp(prefix="mlo-w1-"))
        try:
            fixture = FIX / case
            store = td / "store"
            store.mkdir()
            seed = fixture / "seed_priors"
            if seed.exists():
                for f in seed.glob("*.json"):
                    prior = json.loads(f.read_text())
                    PriorStore(store).create(prior, allow_duplicate=True)
            out = td / "out"
            summary = run_from_fixture_dir(fixture, out_dir=out, store_dir=store, dry_run=True)
            return summary, out, store
        finally:
            pass  # keep for assertions; cleaned by OS tmp — explicit cleanup below in each test via td

    def test_01_ratify(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-01-"))
        fixture = FIX / "01_repeated_success_ratify"
        store = td / "store"
        out = td / "out"
        summary = run_from_fixture_dir(fixture, out_dir=out, store_dir=store, dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "RATIFIED")
        self.assertEqual(summary["final_state"], RATIFIED)
        self.assertIsNotNone(summary["receipt_id"])
        self.assertFalse(summary["live_promotion"])
        receipts = list(out.glob("learning_receipt-*.json"))
        self.assertTrue(receipts)
        validate_learning_receipt(json.loads(receipts[0].read_text()))
        shutil.rmtree(td)

    def test_02_insufficient(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-02-"))
        summary = run_from_fixture_dir(FIX / "02_insufficient_evidence", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertIsNone(summary["receipt_id"])
        self.assertIn(summary["blocked_reason"], ("insufficient_evidence", "candidate_not_ready", "no_ecqr_decision_or_blocked"))
        # candidates may be observed
        self.assertTrue(any(c["state"] == OBSERVED or c["n"] < 3 for c in summary["candidates"]))
        shutil.rmtree(td)

    def test_03_contradiction_blocks_ratify(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-03-"))
        summary = run_from_fixture_dir(FIX / "03_contradictory_evidence", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertNotEqual(summary.get("ecqr_decision"), "RATIFIED")
        self.assertIsNone(summary.get("receipt_id"))
        shutil.rmtree(td)

    def test_04_near_duplicate_rejects(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-04-"))
        fixture = FIX / "04_near_duplicate_prior"
        store = td / "store"
        store.mkdir()
        for f in (fixture / "seed_priors").glob("*.json"):
            PriorStore(store).create(json.loads(f.read_text()), allow_duplicate=True)
        summary = run_from_fixture_dir(fixture, out_dir=td / "out", store_dir=store, dry_run=True)
        self.assertIsNotNone(summary.get("near_duplicate") or summary.get("similarity_top"))
        # should reject as near duplicate
        self.assertEqual(summary.get("ecqr_decision"), "REJECTED")
        self.assertIsNotNone(summary.get("receipt_id"))
        shutil.rmtree(td)

    def test_05_expired_not_blocking_new(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-05-"))
        fixture = FIX / "05_expired_prior"
        store = td / "store"
        store.mkdir()
        for f in (fixture / "seed_priors").glob("*.json"):
            PriorStore(store).create(json.loads(f.read_text()), allow_duplicate=True)
        # expired not in active search by default
        active = PriorStore(store).search(status="active")
        self.assertEqual(active, [])
        expired = PriorStore(store).search(status="expired", include_expired=True)
        self.assertEqual(len(expired), 1)
        summary = run_from_fixture_dir(fixture, out_dir=td / "out", store_dir=store, dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "RATIFIED")
        shutil.rmtree(td)

    def test_06_reject_requires_receipt(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-06-"))
        summary = run_from_fixture_dir(FIX / "06_rejected_candidate", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertEqual(summary["ecqr_decision"], "REJECTED")
        self.assertIsNotNone(summary["receipt_id"])
        shutil.rmtree(td)

    def test_07_rollback_requires_receipt(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-07-"))
        store = PriorStore(td / "store")
        prior = json.loads((FIX / "07_rollback" / "seed_priors" / "prior-to-rollback.json").read_text())
        store.create(prior, allow_duplicate=True)
        # Build rollback receipt and transition
        receipt = build_learning_receipt(
            decision="ROLLED_BACK",
            prior_id="prior-to-rollback",
            candidate_id="cand-rollback-fixture",
            reviewer="test_reviewer:rollback",
            rationale="Rollback after regression evidence",
            evidence_links=["evt-001", "rollback-evidence"],
            confidence_before=0.8,
            confidence_after=0.4,
            affected_loops=["motor_learning_organ_v1"],
            applicable_runways=["Software Repair"],
            repositories=["sina-governance-SSOT"],
            origin_event="evt-001",
            decision_timestamp="2026-07-11T12:00:00Z",
            rollback_target="prior-to-rollback",
        )
        validate_learning_receipt(receipt)
        entity = {"state": RATIFIED, "status": "active", "prior_id": "prior-to-rollback"}
        entity = transition(
            entity, ROLLED_BACK,
            actor="test_reviewer:rollback",
            reason="Rollback after regression evidence",
            evidence=["evt-001"],
            learning_receipt_id=receipt["receipt_id"],
        )
        self.assertEqual(entity["state"], ROLLED_BACK)
        prior2 = dict(prior)
        prior2["state"] = entity["state"]
        prior2["status"] = entity["status"]
        prior2["learning_receipt_id"] = receipt["receipt_id"]
        store.update(prior2)
        self.assertEqual(store.get("prior-to-rollback")["status"], "rolled_back")
        shutil.rmtree(td)

    def test_ecqr_blocks_similarity_promotion(self):
        with self.assertRaises(GovernanceBlock):
            validate_ecqr_decision({
                "decision": "RATIFIED",
                "candidate_id": "c",
                "reviewer": "test_reviewer:x",
                "rationale": "sim",
                "evidence_reviewed": ["e"],
                "shadow_result_ref": "s",
                "confidence_before": 0.9,
                "confidence_after": 0.9,
                "affected_loops": ["motor_learning_organ_v1"],
                "applicable_runways": ["Software Repair"],
                "effective_at": "2026-07-10T12:00:00Z",
                "policy_versions": {},
                "promoted_by_similarity": True,
            })


class TestNoLivePromo(unittest.TestCase):
    def test_summary_never_live(self):
        td = Path(tempfile.mkdtemp(prefix="mlo-live-"))
        summary = run_from_fixture_dir(FIX / "01_repeated_success_ratify", out_dir=td / "out", store_dir=td / "store", dry_run=True)
        self.assertFalse(summary["live_promotion"])
        self.assertFalse(summary["model_learning"])
        shutil.rmtree(td)


if __name__ == "__main__":
    unittest.main()
