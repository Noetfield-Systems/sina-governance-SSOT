#!/usr/bin/env python3
"""Shared brain-loop health scoring and improvement receipt helpers."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def _clamp(value: float, *, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def _score_lower_is_better(target: float, observed: float | None) -> float:
    if observed is None:
        return 0.0
    if target <= 0:
        return 100.0 if observed <= 0 else 0.0
    if observed <= target:
        return 100.0
    return _clamp(round((target / observed) * 100.0, 2))


def _score_higher_is_better(target: float, observed: float | None) -> float:
    if observed is None:
        return 0.0
    if target <= 0:
        return 100.0
    if observed >= target:
        return 100.0
    return _clamp(round((observed / target) * 100.0, 2))


def normalize_targets(targets: dict[str, Any]) -> dict[str, float]:
    return {
        "freshness_target_minutes": float(targets.get("freshness_target_minutes", targets.get("heartbeat_max_age_minutes", 360))),
        "success_rate_target": float(targets.get("success_rate_target", 99)),
        "latency_target_minutes": float(targets.get("latency_target_minutes", 15)),
        "heartbeat_max_age_minutes": float(targets.get("heartbeat_max_age_minutes", targets.get("freshness_target_minutes", 360))),
        "min_health_score": float(targets.get("min_health_score", 85)),
    }


def score_loop_health(
    targets: dict[str, Any],
    *,
    freshness_age_minutes: float | None,
    success_rate_pct: float | None,
    latency_minutes: float | None,
    latest_result: str = "",
    failure_count: int = 0,
    drift_detected: bool = False,
    reason: str = "receipt_fresh",
    heartbeat_at: str | None = None,
) -> dict[str, Any]:
    normalized = normalize_targets(targets)
    freshness_score = _score_lower_is_better(normalized["freshness_target_minutes"], freshness_age_minutes)
    success_score = _score_higher_is_better(normalized["success_rate_target"], success_rate_pct)
    latency_score = _score_lower_is_better(normalized["latency_target_minutes"], latency_minutes)

    freshness_miss = freshness_age_minutes is None or freshness_age_minutes > normalized["freshness_target_minutes"]
    success_rate_miss = success_rate_pct is None or success_rate_pct < normalized["success_rate_target"]
    latency_miss = latency_minutes is None or latency_minutes > normalized["latency_target_minutes"]
    result_miss = latest_result not in {"PASS", "MATCH", "OK", "SKIP"}
    evidence_miss = failure_count > 0

    weighted = round((freshness_score * 0.4) + (success_score * 0.35) + (latency_score * 0.25), 2)
    health_score = int(round(_clamp(weighted)))
    slo_miss = freshness_miss or success_rate_miss or latency_miss or result_miss or evidence_miss or drift_detected or reason != "receipt_fresh"

    if not slo_miss and health_score >= normalized["min_health_score"]:
        health_state = "healthy"
    elif drift_detected or freshness_miss or success_rate_miss or latency_miss or evidence_miss or result_miss:
        health_state = "degraded"
    else:
        health_state = "at_risk"

    missed_targets = [
        name
        for name, miss in (
            ("freshness", freshness_miss),
            ("success_rate", success_rate_miss),
            ("latency", latency_miss),
        )
        if miss
    ]
    if drift_detected:
        missed_targets.append("drift")
    if result_miss:
        missed_targets.append("result")
    if evidence_miss:
        missed_targets.append("evidence")
    if reason != "receipt_fresh":
        missed_targets.append(reason)

    return {
        "heartbeat_at": heartbeat_at,
        "freshness_target_minutes": normalized["freshness_target_minutes"],
        "success_rate_target": normalized["success_rate_target"],
        "latency_target_minutes": normalized["latency_target_minutes"],
        "heartbeat_max_age_minutes": normalized["heartbeat_max_age_minutes"],
        "min_health_score": normalized["min_health_score"],
        "freshness_age_minutes": freshness_age_minutes,
        "success_rate_pct": success_rate_pct,
        "latency_minutes": latency_minutes,
        "freshness_score": freshness_score,
        "success_rate_score": success_score,
        "latency_score": latency_score,
        "freshness_miss": freshness_miss,
        "success_rate_miss": success_rate_miss,
        "latency_miss": latency_miss,
        "latest_result": latest_result,
        "failure_count": failure_count,
        "health_score": health_score,
        "health_state": health_state,
        "slo_miss": slo_miss,
        "drift_detected": drift_detected,
        "missed_targets": missed_targets,
        "slo_targets": normalized,
        "score_breakdown": {
            "freshness": freshness_score,
            "success_rate": success_score,
            "latency": latency_score,
        },
    }


def build_improvement_receipt_v2(
    registry: dict[str, Any],
    health: dict[str, Any],
    *,
    workflow_name: str,
    diff_summary: str,
    expected_effect: str,
    roi: dict[str, Any],
    rollback_command: str,
    evidence: list[dict[str, Any]],
    trigger: str,
    latest: dict[str, Any] | None = None,
    assessment: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_full_name = registry.get("repo_full_name") or registry.get("repo") or "Noetfield-Systems/sina-governance-SSOT"
    branch = registry.get("autonomous_promote_branch", "main")
    receipt = {
        "receipt_type": "IMPROVEMENT_RECEIPT_V2",
        "receipt_version": 2,
        "recorded_at": _now_iso(),
        "workflow": workflow_name,
        "repo": repo_full_name,
        "branch": branch,
        "trigger": trigger,
        "health_score": health.get("health_score"),
        "health_state": health.get("health_state"),
        "slo_miss": bool(health.get("slo_miss")),
        "missed_targets": health.get("missed_targets", []),
        "freshness_age_minutes": health.get("freshness_age_minutes"),
        "freshness_target_minutes": health.get("freshness_target_minutes"),
        "success_rate_pct": health.get("success_rate_pct"),
        "success_rate_target": health.get("success_rate_target"),
        "latency_minutes": health.get("latency_minutes"),
        "latency_target_minutes": health.get("latency_target_minutes"),
        "diff_summary": diff_summary,
        "expected_effect": expected_effect,
        "ROI": roi,
        "rollback_command": rollback_command,
        "evidence": evidence,
        "slo_targets": health.get("slo_targets", {}),
    }
    if latest is not None:
        receipt["latest_verifier_receipt_id"] = latest.get("receipt_id")
        receipt["latest_verifier_result"] = latest.get("result") or latest.get("status")
    if assessment is not None:
        receipt["assessment"] = assessment
    return receipt


def build_kaizen_proof_receipt(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return build_improvement_receipt_v2(*args, **kwargs)
