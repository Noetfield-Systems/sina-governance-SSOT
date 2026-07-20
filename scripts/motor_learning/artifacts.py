"""Authoritative artifact validators — derive from inputs; reject synthetic self-hashes."""
from __future__ import annotations

import math
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .hashutil import content_hash, canonical_json
from .shadow import evaluate_shadow, MIN_EVALUATED, MIN_COVERAGE, MIN_SUCCESS_RATE, MAX_FAILURES
from .confidence import compute_confidence, WEIGHTS, RATIFY_THRESHOLD
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


def _canonical_equal(a: Any, b: Any) -> bool:
    return canonical_json(a) == canonical_json(b)


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
    expected = content_hash(manifest)
    claimed = report.get("evidence_manifest_hash")
    if claimed is not None and claimed != expected:
        raise GovernanceBlock(
            f"shadow evidence_manifest_hash mismatch: claimed={claimed!r} recomputed={expected!r}"
        )
    return expected


def validate_shadow_report(
    shadow: dict[str, Any] | ValidatedShadow,
    *,
    candidate: dict[str, Any] | None = None,
    shadow_events: list[dict] | None = None,
    require_derivation: bool = True,
) -> ValidatedShadow:
    """
    Prefer derivation proof: require concrete normalized shadow_events + candidate,
    rerun evaluate_shadow, and require complete canonical equality with submitted artifact.
    """
    if isinstance(shadow, ValidatedShadow):
        shadow = shadow.as_dict()
    if not isinstance(shadow, dict):
        raise SchemaError("shadow must be object")

    if require_derivation:
        if candidate is None:
            raise GovernanceBlock("shadow validation requires candidate for derivation proof")
        if shadow_events is None:
            raise GovernanceBlock(
                "shadow validation requires concrete normalized shadow_events; "
                "self-hash alone is never proof"
            )
        if not isinstance(shadow_events, list) or not shadow_events:
            raise GovernanceBlock("shadow_events must be a nonempty list of normalized events")

        derived = evaluate_shadow(candidate, shadow_events)
        # Every derived key must match; no extra material keys allowed to disagree
        for key in sorted(derived.keys()):
            if key not in shadow:
                raise GovernanceBlock(f"submitted shadow missing derived field: {key}")
            if not _canonical_equal(shadow[key], derived[key]):
                raise GovernanceBlock(
                    f"shadow derivation mismatch on {key}: "
                    f"submitted≠evaluate_shadow(candidate, shadow_events)"
                )
        extra = set(shadow.keys()) - set(derived.keys())
        if extra:
            raise GovernanceBlock(f"submitted shadow has undeclared extra fields: {sorted(extra)}")
        if not _canonical_equal(shadow, derived):
            raise GovernanceBlock(
                "shadow artifact is not canonically equal to evaluate_shadow(candidate, shadow_events)"
            )
        return _mint_shadow(dict(derived))

    # Non-derivation path forbidden for ratification paths
    raise GovernanceBlock("shadow validation requires derivation proof")


def validate_confidence_artifact(
    confidence: dict[str, Any] | ValidatedConfidence,
    *,
    shadow: dict | ValidatedShadow | None = None,
    confidence_inputs: dict[str, Any] | None = None,
    require_derivation: bool = True,
) -> ValidatedConfidence:
    """
    Prefer derivation proof: require canonical confidence_inputs, rerun compute_confidence,
    and require exact component names/weights/contributions and complete artifact equality.
    """
    if isinstance(confidence, ValidatedConfidence):
        confidence = confidence.as_dict()
    if not isinstance(confidence, dict):
        raise SchemaError("confidence must be object")

    if require_derivation:
        if confidence_inputs is None:
            raise GovernanceBlock(
                "confidence validation requires canonical confidence_inputs; "
                "caller-supplied component sums alone are never proof"
            )
        required_in = (
            "occurrence_count", "outcomes_seen", "evidence_refs",
            "confidence_before", "scope", "mining_evidence_ids", "shadow_evidence_ids",
        )
        missing = [k for k in required_in if k not in confidence_inputs]
        if missing:
            raise GovernanceBlock(f"confidence_inputs missing: {missing}")

        sh_dict = shadow.as_dict() if isinstance(shadow, ValidatedShadow) else shadow
        derived = compute_confidence(
            occurrence_count=int(confidence_inputs["occurrence_count"]),
            outcomes_seen=list(confidence_inputs["outcomes_seen"]),
            evidence_refs=list(confidence_inputs["evidence_refs"]),
            shadow_report=sh_dict,
            expired_evidence=bool(confidence_inputs.get("expired_evidence", False)),
            confidence_before=float(confidence_inputs["confidence_before"]),
            scope=dict(confidence_inputs.get("scope") or {}),
            mining_evidence_ids=list(confidence_inputs["mining_evidence_ids"]),
            shadow_evidence_ids=list(confidence_inputs["shadow_evidence_ids"]),
        )

        # Exact component names
        want_names = set(WEIGHTS.keys())
        got_names = set((confidence.get("component_contributions") or {}).keys())
        der_names = set((derived.get("component_contributions") or {}).keys())
        if got_names != want_names:
            raise GovernanceBlock(
                f"confidence components must be exactly {sorted(want_names)}; got {sorted(got_names)}"
            )
        if der_names != want_names:
            raise GovernanceBlock("derived confidence components incomplete")

        for name in want_names:
            sc = (confidence.get("component_contributions") or {})[name]
            dc = derived["component_contributions"][name]
            if not _canonical_equal(sc, dc):
                raise GovernanceBlock(
                    f"confidence component {name} mismatch vs compute_confidence() "
                    f"(invented/omitted/reweighted components forbidden)"
                )
            if abs(float(sc.get("weight")) - float(WEIGHTS[name])) > 1e-12:
                raise GovernanceBlock(f"confidence component {name} weight reweighted")

        for key in (
            "schema", "algorithm_version", "confidence_before", "confidence_after",
            "component_contributions", "threshold_references", "meets_ratify_threshold",
            "evidence_ids", "mining_evidence_ids", "shadow_evidence_ids",
            "shadow_contaminated_by_mining_overlap", "overlap_event_ids",
            "promotion_authority", "advisory_only", "content_hash", "explanation",
        ):
            if key not in derived:
                continue
            if key not in confidence:
                raise GovernanceBlock(f"submitted confidence missing derived field: {key}")
            if not _canonical_equal(confidence[key], derived[key]):
                raise GovernanceBlock(
                    f"confidence derivation mismatch on {key}: "
                    f"submitted≠compute_confidence(...)"
                )

        if confidence.get("algorithm_version") != CONFIDENCE_VERSION:
            raise GovernanceBlock("confidence algorithm_version mismatch")
        if not _canonical_equal(
            {k: confidence[k] for k in sorted(confidence)},
            {k: derived[k] for k in sorted(derived)},
        ):
            raise GovernanceBlock(
                "confidence artifact is not canonically equal to compute_confidence()"
            )
        return _mint_confidence(dict(derived))

    raise GovernanceBlock("confidence validation requires derivation proof")


def unwrap_shadow(
    obj: Any,
    *,
    candidate: dict | None = None,
    shadow_events: list[dict] | None = None,
    require_derivation: bool = True,
) -> dict:
    if isinstance(obj, ValidatedShadow):
        return validate_shadow_report(
            obj.as_dict(), candidate=candidate, shadow_events=shadow_events,
            require_derivation=require_derivation,
        ).as_dict()
    if isinstance(obj, dict):
        return validate_shadow_report(
            obj, candidate=candidate, shadow_events=shadow_events,
            require_derivation=require_derivation,
        ).as_dict()
    raise GovernanceBlock("shadow artifact required")


def unwrap_confidence(
    obj: Any,
    *,
    shadow=None,
    confidence_inputs: dict | None = None,
    require_derivation: bool = True,
) -> dict:
    if isinstance(obj, ValidatedConfidence):
        return validate_confidence_artifact(
            obj.as_dict(), shadow=shadow, confidence_inputs=confidence_inputs,
            require_derivation=require_derivation,
        ).as_dict()
    if isinstance(obj, dict):
        return validate_confidence_artifact(
            obj, shadow=shadow, confidence_inputs=confidence_inputs,
            require_derivation=require_derivation,
        ).as_dict()
    raise GovernanceBlock("confidence artifact required")


def unwrap_candidate(obj: Any) -> dict:
    if isinstance(obj, ValidatedCandidate):
        return validate_candidate_artifact(obj.as_dict()).as_dict()
    if isinstance(obj, dict):
        return validate_candidate_artifact(obj).as_dict()
    raise GovernanceBlock("candidate artifact required")
