#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.brain_domain_registry_v1 import load_registry, workflow_health_targets
from scripts.brain_loop_self_heal_v1 import calculate_health_snapshot, build_kaizen_proof_receipt


def main() -> int:
    registry = load_registry()
    targets = workflow_health_targets(registry)
    assert int(targets["heartbeat_max_age_minutes"]) > 0
    assert int(targets["min_health_score"]) > 0
    assert str(targets["kaizen_proof_prefix"]).startswith("receipts/")

    latest = {
        "receipt_id": "latest-test-receipt",
        "checked_at": "2026-07-02T00:00:00Z",
        "result": "PASS",
        "status": "PASS",
        "failures": [],
    }
    assessment = {
        "sandbox_id": "brain_worker",
        "head_ref": "deadbeef",
        "bundle_sha256": "cafebabecafebabecafebabecafebabecafebabecafebabecafebabecafebabe",
        "receipt_ref": "deadbeef",
        "receipt_sha256": "cafebabecafebabecafebabecafebabecafebabecafebabecafebabecafebabe",
        "action": "reverify",
        "reason": "receipt_ref_stale_or_missing",
    }
    health = calculate_health_snapshot(targets, latest, assessment)
    proof = build_kaizen_proof_receipt(registry, latest, assessment, None, health, sandbox_id="brain_worker")

    required_fields = {
        "receipt_type",
        "recorded_at",
        "sourcea_root",
        "workflow",
        "sandbox_id",
        "latest_verifier_receipt_id",
        "health_score",
        "health_state",
        "health_threshold",
        "slo_targets",
        "slo_miss",
        "drift_detected",
        "proof_reason",
    }
    missing = sorted(required_fields - set(proof))
    assert not missing, f"missing proof fields: {missing}"
    assert proof["receipt_type"] == "BRAIN_KAIZEN_PROOF"
    assert proof["slo_miss"] or proof["drift_detected"]
    assert health["health_score"] <= 100
    assert health["health_state"] in {"healthy", "degraded", "at_risk"}
    print("brain loop health receipt validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
