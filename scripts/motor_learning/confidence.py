"""Versioned explainable confidence model. Advisory only — no promotion authority."""
from __future__ import annotations

from typing import Any

from . import CONFIDENCE_VERSION
from .hashutil import content_hash

WEIGHTS = {
    "evidence_count": 0.20,
    "recurrence": 0.15,
    "outcome_consistency": 0.20,
    "contradiction_rate": 0.15,
    "evidence_quality": 0.10,
    "recency": 0.10,
    "scope_coverage": 0.05,
    "shadow_performance": 0.05,
}

RATIFY_THRESHOLD = 0.70


def _clamp(x: float) -> float:
    return max(0.0, min(1.0, x))


def compute_confidence(
    *,
    occurrence_count: int,
    outcomes_seen: list[str],
    evidence_refs: list[str],
    shadow_report: dict | None = None,
    expired_evidence: bool = False,
    confidence_before: float = 0.0,
    scope: dict | None = None,
    mining_evidence_ids: list[str] | None = None,
    shadow_evidence_ids: list[str] | None = None,
) -> dict[str, Any]:
    components = {}

    ec = _clamp(occurrence_count / 5.0)
    components["evidence_count"] = {
        "value": round(ec, 4), "weight": WEIGHTS["evidence_count"],
        "contribution": round(ec * WEIGHTS["evidence_count"], 4),
        "source": "mining",
    }

    rec = _clamp((occurrence_count - 1) / 4.0) if occurrence_count else 0.0
    components["recurrence"] = {
        "value": round(rec, 4), "weight": WEIGHTS["recurrence"],
        "contribution": round(rec * WEIGHTS["recurrence"], 4),
        "source": "mining",
    }

    uniq = set(outcomes_seen or [])
    cons = 1.0 if len(uniq) == 1 and uniq else 0.0
    components["outcome_consistency"] = {
        "value": cons, "weight": WEIGHTS["outcome_consistency"],
        "contribution": round(cons * WEIGHTS["outcome_consistency"], 4),
        "source": "mining",
    }

    contrad = 0.0 if len(uniq) <= 1 else 1.0
    contrad_score = 1.0 - contrad
    components["contradiction_rate"] = {
        "value": round(contrad_score, 4), "weight": WEIGHTS["contradiction_rate"],
        "contribution": round(contrad_score * WEIGHTS["contradiction_rate"], 4),
        "source": "mining",
    }

    eq = 0.0 if expired_evidence else (0.8 if evidence_refs else 0.2)
    components["evidence_quality"] = {
        "value": eq, "weight": WEIGHTS["evidence_quality"],
        "contribution": round(eq * WEIGHTS["evidence_quality"], 4),
        "source": "mining",
    }

    components["recency"] = {
        "value": 0.8 if not expired_evidence else 0.1,
        "weight": WEIGHTS["recency"],
        "contribution": round((0.8 if not expired_evidence else 0.1) * WEIGHTS["recency"], 4),
        "source": "mining",
    }

    scope = scope or {}
    filled = sum(1 for k in ("loop_id", "runway", "repository") if scope.get(k))
    sc = filled / 3.0
    components["scope_coverage"] = {
        "value": round(sc, 4), "weight": WEIGHTS["scope_coverage"],
        "contribution": round(sc * WEIGHTS["scope_coverage"], 4),
        "source": "mining",
    }

    shadow_val = 0.0
    if shadow_report:
        rate = shadow_report.get("success_rate")
        if rate is None and shadow_report.get("total"):
            rate = shadow_report["successes"] / max(1, shadow_report["total"])
        shadow_val = float(rate or 0.0)
        if shadow_report.get("result") == "failure":
            shadow_val = min(shadow_val, 0.2)
    components["shadow_performance"] = {
        "value": round(shadow_val, 4), "weight": WEIGHTS["shadow_performance"],
        "contribution": round(shadow_val * WEIGHTS["shadow_performance"], 4),
        "source": "shadow",
    }

    after = _clamp(sum(c["contribution"] for c in components.values()))
    if contrad or (shadow_report and shadow_report.get("result") == "failure"):
        after = min(after, max(0.0, confidence_before - 0.1)) if confidence_before else after
    after = round(after, 4)
    before = round(_clamp(float(confidence_before)), 4)

    mine_ids = list(mining_evidence_ids if mining_evidence_ids is not None else (evidence_refs or []))
    sh_ids = list(shadow_evidence_ids or [])
    overlap = sorted(set(mine_ids) & set(sh_ids))

    shadow_ok = True
    if shadow_report is not None:
        if shadow_report.get("ratifiable") is False:
            shadow_ok = False
        if shadow_report.get("evaluated", 0) < 3:
            shadow_ok = False

    out = {
        "schema": "nf_motor_learning_confidence_v1",
        "algorithm_version": CONFIDENCE_VERSION,
        "confidence_before": before,
        "confidence_after": after,
        "component_contributions": components,
        "threshold_references": {"ratify_min": RATIFY_THRESHOLD},
        "meets_ratify_threshold": (
            after >= RATIFY_THRESHOLD
            and contrad_score == 1.0
            and not expired_evidence
            and not overlap
            and shadow_ok
        ),
        "explanation": (
            f"confidence {before}->{after} via {CONFIDENCE_VERSION}; "
            f"evidence_n={occurrence_count}; outcomes={sorted(uniq)}; "
            f"shadow={shadow_val:.2f}; expired={expired_evidence}; overlap={len(overlap)}; "
            f"shadow_ok={shadow_ok}"
        ),
        "evidence_ids": list(evidence_refs or []),
        "mining_evidence_ids": mine_ids,
        "shadow_evidence_ids": sh_ids,
        "shadow_contaminated_by_mining_overlap": bool(overlap),
        "overlap_event_ids": overlap,
        "promotion_authority": False,
        "advisory_only": True,
    }
    out["content_hash"] = content_hash({k: out[k] for k in sorted(out) if k != "content_hash"})
    return out
