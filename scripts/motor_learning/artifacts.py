"""Authoritative artifact validators — recompute hashes; reject synthetic dicts."""
from __future__ import annotations

import math
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .hashutil import content_hash
from .shadow import MIN_EVALUATED, MIN_COVERAGE, MIN_SUCCESS_RATE, MAX_FAILURES
from .validated import (
    ValidatedShadow,
    ValidatedConfidence,
    ValidatedCandidate,
    _mint_shadow,
    _mint_confidence,
    _mint_candidate,
)
from . import CONFIDENCE_VERSION


def _finite_unit(x: Any, name: str) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError) as exc:
        raise SchemaError(f"{name} must be float") from exc
    if not math.isfinite(v) or v < 0.0 or v > 1.0:
        raise SchemaError(f"{name} must be finite in [0,1]")
    return v


def candidate_content_hash(candidate: dict[str, Any]) -> str:
    body = {
        "candidate_id": candidate.get("candidate_id"),
        "fingerprint": candidate.get("fingerprint"),
        "recommended_action": candidate.get("recommended_action"),
        "source_event_ids": candidate.get("source_event_ids"),
        "evidence_refs": candidate.get("evidence_refs"),
        "occurrence_count": candidate.get("occurrence_count"),
        "scope": candidate.get("scope"),
    }
    return content_hash(body)


def validate_candidate_artifact(candidate: dict[str, Any] | ValidatedCandidate) -> ValidatedCandidate:
    if isinstance(candidate, ValidatedCandidate):
        candidate = candidate.as_dict()
    if not isinstance(candidate, dict):
        raise SchemaError("candidate must be object")
    for req in ("candidate_id", "fingerprint", "recommended_action", "source_event_ids", "evidence_refs"):
        if req not in candidate:
            raise GovernanceBlock(f"candidate missing {req}")
    if not candidate["candidate_id"] or not candidate["source_event_ids"]:
        raise GovernanceBlock("candidate_id and source_event_ids required")
    expected = candidate_content_hash(candidate)
    claimed = candidate.get("content_hash")
    out = dict(candidate)
    out["content_hash"] = expected
    if claimed is not None and claimed != expected:
        raise GovernanceBlock(
            f"candidate content_hash mismatch: claimed={claimed!r} recomputed={expected!r}"
        )
    return _mint_candidate(out)


def validate_shadow_evidence_manifest(manifest: dict[str, Any], *, report: dict[str, Any]) -> str:
    if not isinstance(manifest, dict):
        raise GovernanceBlock("shadow evidence_manifest must be object")
    required = (
        "shadow_event_ids", "evidence_refs", "normalized_event_hashes",
        "successes", "failures", "abstentions", "evaluated", "coverage", "success_rate",
    )
    missing = [k for k in required if k not in manifest]
    if missing:
        raise GovernanceBlock(f"shadow evidence_manifest missing: {missing}")
    if list(manifest.get("shadow_event_ids") or []) != list(report.get("shadow_event_ids") or []):
        raise GovernanceBlock("manifest shadow_event_ids mismatch report")
    if sorted(manifest.get("evidence_refs") or []) != sorted(report.get("evidence_refs") or []):
        raise GovernanceBlock("manifest evidence_refs mismatch report")
    for k in ("successes", "failures", "abstentions", "evaluated"):
        if int(manifest[k]) != int(report[k]):
            raise GovernanceBlock(f"manifest {k} mismatch")
    expected = content_hash(manifest)
    claimed = report.get("evidence_manifest_hash")
    if claimed is not None and claimed != expected:
        raise GovernanceBlock(
            f"shadow evidence_manifest_hash mismatch: claimed={claimed!r} recomputed={expected!r}"
        )
    return expected


def validate_shadow_report(shadow: dict[str, Any] | ValidatedShadow) -> ValidatedShadow:
    if isinstance(shadow, ValidatedShadow):
        shadow = shadow.as_dict()
    if not isinstance(shadow, dict):
        raise SchemaError("shadow must be object")
    required = (
        "schema", "shadow_id", "candidate_id", "successes", "failures", "abstentions",
        "total", "evaluated", "coverage", "success_rate", "result", "ratifiable",
        "details", "shadow_event_ids", "evidence_refs", "evidence_manifest",
        "evidence_manifest_hash", "content_hash",
    )
    missing = [k for k in required if k not in shadow]
    if missing:
        raise GovernanceBlock(f"shadow report missing: {missing}")
    if shadow.get("schema") != "nf_motor_learning_shadow_report_v1":
        raise GovernanceBlock("invalid shadow schema")
    if shadow.get("production_change") is True:
        raise GovernanceBlock("shadow must not claim production_change")

    successes = int(shadow["successes"])
    failures = int(shadow["failures"])
    abstentions = int(shadow["abstentions"])
    total = int(shadow["total"])
    evaluated = int(shadow["evaluated"])
    if successes + failures + abstentions != total:
        raise GovernanceBlock("shadow counters do not sum to total")
    if successes + failures != evaluated:
        raise GovernanceBlock("shadow evaluated != successes+failures")
    coverage = float(shadow["coverage"])
    success_rate = float(shadow["success_rate"])
    expected_coverage = (evaluated / total) if total else 0.0
    expected_rate = (successes / evaluated) if evaluated else 0.0
    if abs(coverage - expected_coverage) > 1e-6:
        raise GovernanceBlock("shadow coverage inconsistent with counters")
    if abs(success_rate - expected_rate) > 1e-6:
        raise GovernanceBlock("shadow success_rate inconsistent with counters")

    result = shadow["result"]
    if evaluated == 0 and result != "insufficient_evidence":
        raise GovernanceBlock("shadow result must be insufficient_evidence when evaluated=0")
    if failures > successes and result != "failure":
        raise GovernanceBlock("shadow result inconsistent with failure majority")
    if successes > 0 and failures == 0 and evaluated > 0 and result != "success":
        raise GovernanceBlock("shadow result inconsistent with pure successes")

    ratifiable = bool(shadow["ratifiable"])
    expected_ratifiable = (
        evaluated >= MIN_EVALUATED
        and coverage >= MIN_COVERAGE
        and success_rate >= MIN_SUCCESS_RATE
        and failures <= MAX_FAILURES
        and result in ("success", "mixed")
    )
    if ratifiable != expected_ratifiable:
        raise GovernanceBlock(
            f"shadow ratifiable={ratifiable} inconsistent with thresholds "
            f"(expected={expected_ratifiable})"
        )

    manifest = shadow.get("evidence_manifest") or {}
    manifest_hash = validate_shadow_evidence_manifest(manifest, report=shadow)
    if shadow.get("evidence_manifest_hash") != manifest_hash:
        raise GovernanceBlock("shadow evidence_manifest_hash failed recompute")

    body = {k: shadow[k] for k in sorted(shadow) if k != "content_hash"}
    body["evidence_manifest_hash"] = manifest_hash
    expected_hash = content_hash(body)
    if shadow.get("content_hash") != expected_hash:
        raise GovernanceBlock(
            f"shadow content_hash mismatch: claimed={shadow.get('content_hash')!r} "
            f"recomputed={expected_hash!r}"
        )
    out = dict(shadow)
    out["evidence_manifest_hash"] = manifest_hash
    out["content_hash"] = expected_hash
    return _mint_shadow(out)


def validate_confidence_artifact(
    confidence: dict[str, Any] | ValidatedConfidence,
    *,
    shadow: dict | ValidatedShadow | None = None,
) -> ValidatedConfidence:
    if isinstance(confidence, ValidatedConfidence):
        confidence = confidence.as_dict()
    if not isinstance(confidence, dict):
        raise SchemaError("confidence must be object")
    required = (
        "schema", "algorithm_version", "confidence_before", "confidence_after",
        "component_contributions", "threshold_references", "meets_ratify_threshold",
        "evidence_ids", "mining_evidence_ids", "shadow_evidence_ids", "content_hash",
    )
    missing = [k for k in required if k not in confidence]
    if missing:
        raise GovernanceBlock(f"confidence missing: {missing}")
    if confidence.get("schema") != "nf_motor_learning_confidence_v1":
        raise GovernanceBlock("invalid confidence schema")
    if confidence.get("algorithm_version") != CONFIDENCE_VERSION:
        raise GovernanceBlock("confidence algorithm_version mismatch")
    if confidence.get("promotion_authority") is True:
        raise GovernanceBlock("confidence must not claim promotion_authority")

    before = _finite_unit(confidence["confidence_before"], "confidence_before")
    after = _finite_unit(confidence["confidence_after"], "confidence_after")
    comps = confidence.get("component_contributions") or {}
    if not isinstance(comps, dict) or not comps:
        raise GovernanceBlock("confidence component_contributions required")
    recon = 0.0
    for name, c in comps.items():
        if not isinstance(c, dict) or "contribution" not in c or "weight" not in c:
            raise GovernanceBlock(f"confidence component {name} malformed")
        recon += float(c["contribution"])
    recon = max(0.0, min(1.0, recon))
    if abs(recon - after) > 0.05:
        raise GovernanceBlock(
            f"confidence_after {after} inconsistent with component sum {recon}"
        )

    thresh = float((confidence.get("threshold_references") or {}).get("ratify_min") or 0.70)
    overlap = bool(confidence.get("shadow_contaminated_by_mining_overlap"))
    mine = set(confidence.get("mining_evidence_ids") or [])
    sh = set(confidence.get("shadow_evidence_ids") or [])
    if mine & sh and not overlap:
        raise GovernanceBlock("confidence overlap flag inconsistent with evidence id sets")

    shadow_ok = True
    sh_dict = shadow.as_dict() if isinstance(shadow, ValidatedShadow) else shadow
    if sh_dict is not None:
        if sh_dict.get("ratifiable") is False or int(sh_dict.get("evaluated") or 0) < 3:
            shadow_ok = False

    if confidence.get("meets_ratify_threshold") and not (
        after >= thresh and not overlap and shadow_ok
    ):
        raise GovernanceBlock(
            "meets_ratify_threshold=true inconsistent with after/overlap/shadow_ok"
        )

    body = {k: confidence[k] for k in sorted(confidence) if k != "content_hash"}
    expected_hash = content_hash(body)
    if confidence.get("content_hash") != expected_hash:
        raise GovernanceBlock(
            f"confidence content_hash mismatch: claimed={confidence.get('content_hash')!r} "
            f"recomputed={expected_hash!r}"
        )
    out = dict(confidence)
    out["confidence_before"] = before
    out["confidence_after"] = after
    out["content_hash"] = expected_hash
    return _mint_confidence(out)


def unwrap_shadow(obj: Any) -> dict:
    if isinstance(obj, ValidatedShadow):
        return validate_shadow_report(obj.as_dict()).as_dict()
    if isinstance(obj, dict):
        return validate_shadow_report(obj).as_dict()
    raise GovernanceBlock("shadow artifact required")


def unwrap_confidence(obj: Any, *, shadow=None) -> dict:
    if isinstance(obj, ValidatedConfidence):
        return validate_confidence_artifact(obj.as_dict(), shadow=shadow).as_dict()
    if isinstance(obj, dict):
        return validate_confidence_artifact(obj, shadow=shadow).as_dict()
    raise GovernanceBlock("confidence artifact required")


def unwrap_candidate(obj: Any) -> dict:
    if isinstance(obj, ValidatedCandidate):
        return validate_candidate_artifact(obj.as_dict()).as_dict()
    if isinstance(obj, dict):
        return validate_candidate_artifact(obj).as_dict()
    raise GovernanceBlock("candidate artifact required")
