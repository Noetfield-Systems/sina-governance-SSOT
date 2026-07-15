#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.brain_domain_registry_v1 import load_registry, workflow_health_targets
from scripts.brain_loop_health_model_v1 import build_improvement_receipt_v2, score_loop_health


def main() -> int:
    registry = load_registry()
    targets = workflow_health_targets(registry)
    assert int(targets["freshness_target_minutes"]) > 0
    assert int(targets["success_rate_target"]) > 0
    assert int(targets["latency_target_minutes"]) > 0
    assert int(targets["heartbeat_max_age_minutes"]) > 0
    assert int(targets["min_health_score"]) > 0
    assert str(targets["kaizen_proof_prefix"]).startswith("receipts/")

    health = score_loop_health(
        targets,
        freshness_age_minutes=420,
        success_rate_pct=90,
        latency_minutes=25,
        latest_result="FAIL",
        failure_count=1,
        drift_detected=True,
        reason="receipt_ref_stale_or_missing",
        heartbeat_at="2026-07-02T00:00:00Z",
    )
    assert health["freshness_miss"] is True
    assert health["success_rate_miss"] is True
    assert health["latency_miss"] is True
    assert health["slo_miss"] is True
    assert health["health_score"] <= 100
    assert health["health_state"] in {"healthy", "degraded", "at_risk"}

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
    receipt = build_improvement_receipt_v2(
        registry,
        health,
        workflow_name="brain_loop_self_heal_v1",
        diff_summary="freshness, success rate, and latency exceeded targets",
        expected_effect="reduce drift and keep the loop inside SLOs",
        roi={"expected_hours_saved_per_week": 1, "confidence": "medium"},
        rollback_command="git revert HEAD",
        evidence=[{"kind": "test", "value": "validate_brain_loop_health_v1"}],
        trigger="unit_test",
        latest=latest,
        assessment=assessment,
    )

    required_fields = {
        "receipt_type",
        "receipt_version",
        "recorded_at",
        "workflow",
        "repo",
        "branch",
        "trigger",
        "health_score",
        "health_state",
        "slo_miss",
        "missed_targets",
        "freshness_age_minutes",
        "freshness_target_minutes",
        "success_rate_pct",
        "success_rate_target",
        "latency_minutes",
        "latency_target_minutes",
        "diff_summary",
        "expected_effect",
        "ROI",
        "rollback_command",
        "evidence",
        "slo_targets",
    }
    missing = sorted(required_fields - set(receipt))
    assert not missing, f"missing improvement receipt fields: {missing}"
    assert receipt["receipt_type"] == "IMPROVEMENT_RECEIPT_V2"
    assert receipt["slo_miss"] is True
    assert receipt["latest_verifier_receipt_id"] == latest["receipt_id"]
    print("brain loop health receipt validation: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
