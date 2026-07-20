"""ECQR decision gate — fail closed; bind computed artifacts exactly."""
from __future__ import annotations

from typing import Any

from .errors import GovernanceBlock, SchemaError
from .confidence import RATIFY_THRESHOLD
from . import ALGORITHM_VERSION, CONFIDENCE_VERSION

REQUIRED = (
    "decision",
    "candidate_id",
    "reviewer",
    "rationale",
    "evidence_reviewed",
    "shadow_result_ref",
    "confidence_before",
    "confidence_after",
    "affected_loops",
    "applicable_runways",
    "effective_at",
    "policy_versions",
)


def validate_ecqr_decision(
    decision: dict[str, Any],
    *,
    confidence: dict | None = None,
    shadow: dict | None = None,
    candidate: dict | None = None,
    require_bound_artifacts: bool = True,
) -> dict:
    if not isinstance(decision, dict):
        raise SchemaError("ECQR decision must be object")
    missing = [k for k in REQUIRED if k not in decision]
    if missing:
        raise SchemaError(f"ECQR decision missing: {missing}")
    d = decision["decision"]
    if d not in ("RATIFIED", "REJECTED", "ROLLED_BACK"):
        raise SchemaError(f"invalid decision: {d}")
    reviewer = decision["reviewer"]
    if not str(reviewer).startswith(("test_reviewer:", "fixture:", "founder:", "gated_policy:", "machine_policy:")):
        raise GovernanceBlock(f"reviewer must be explicit fixture/founder/gated_policy/machine_policy; got {reviewer}")

    if decision.get("promoted_by_similarity"):
        raise GovernanceBlock("similarity has no promotion authority")
    if decision.get("promoted_by_confidence_alone"):
        raise GovernanceBlock("confidence has no promotion authority")

    out = dict(decision)
    out.setdefault("schema", "nf_motor_learning_ecqr_decision_v1")
    out.setdefault("expires_at", None)
    out.setdefault("supersedes", None)
    out.setdefault("repositories", decision.get("repositories") or [])

    if d == "RATIFIED":
        if require_bound_artifacts:
            if shadow is None:
                raise GovernanceBlock("RATIFIED requires non-None validated shadow artifact")
            if confidence is None:
                raise GovernanceBlock("RATIFIED requires non-None validated confidence artifact")
        if shadow is None or confidence is None:
            raise GovernanceBlock("RATIFIED requires shadow and confidence artifacts")

        # Bind candidate_id
        if candidate and decision["candidate_id"] != candidate.get("candidate_id"):
            raise GovernanceBlock("ECQR candidate_id mismatches candidate")
        if shadow.get("candidate_id") and decision["candidate_id"] != shadow["candidate_id"]:
            raise GovernanceBlock("ECQR candidate_id mismatches shadow.candidate_id")

        # Bind shadow id/hash — string ref alone insufficient without matching artifact
        shadow_id = shadow.get("shadow_id")
        shadow_hash = shadow.get("content_hash") or shadow.get("shadow_hash")
        ref = decision.get("shadow_result_ref")
        if not shadow_id:
            raise GovernanceBlock("shadow artifact missing shadow_id")
        if ref not in (f"shadow:{shadow_id}", shadow_id, f"hash:{shadow_hash}"):
            raise GovernanceBlock(
                f"shadow_result_ref {ref!r} does not bind to shadow_id={shadow_id} hash={shadow_hash}"
            )
        if decision.get("shadow_hash") and shadow_hash and decision["shadow_hash"] != shadow_hash:
            raise GovernanceBlock("ECQR shadow_hash mismatches computed shadow")

        # Bind confidence values exactly
        if float(decision["confidence_before"]) != float(confidence["confidence_before"]):
            raise GovernanceBlock("ECQR confidence_before mismatches computed confidence")
        if float(decision["confidence_after"]) != float(confidence["confidence_after"]):
            raise GovernanceBlock("ECQR confidence_after mismatches computed confidence")
        if not confidence.get("meets_ratify_threshold"):
            raise GovernanceBlock("RATIFIED blocked: confidence below threshold or contradictions")
        if confidence["confidence_after"] < RATIFY_THRESHOLD:
            raise GovernanceBlock("RATIFIED blocked: confidence_after below ratify threshold")
        if shadow.get("result") not in ("success", "mixed"):
            raise GovernanceBlock(f"RATIFIED blocked: shadow result={shadow.get('result')}")

        # Evidence IDs: decision evidence must be subset of candidate+shadow evidence
        reviewed = set(decision.get("evidence_reviewed") or [])
        allowed = set(confidence.get("evidence_ids") or []) | set(shadow.get("evidence_refs") or [])
        if candidate:
            allowed |= set(candidate.get("evidence_refs") or []) | set(candidate.get("source_event_ids") or [])
        if not reviewed:
            raise GovernanceBlock("RATIFIED requires nonempty evidence_reviewed")
        extra = reviewed - allowed
        if extra:
            raise GovernanceBlock(f"ECQR evidence_reviewed contains unbound IDs: {sorted(extra)}")

        # Algorithm / policy versions
        alg = (decision.get("algorithm_versions") or {})
        if alg.get("pipeline") and alg["pipeline"] != ALGORITHM_VERSION:
            raise GovernanceBlock("ECQR algorithm_versions.pipeline mismatch")
        if alg.get("confidence") and alg["confidence"] != CONFIDENCE_VERSION:
            raise GovernanceBlock("ECQR algorithm_versions.confidence mismatch")
        pol = decision.get("policy_versions") or {}
        if not pol:
            raise GovernanceBlock("ECQR policy_versions required")

        out["shadow_hash"] = shadow_hash
        out["shadow_id"] = shadow_id
        out["_artifacts_bound"] = True
        out["_bound_confidence_version"] = confidence.get("algorithm_version")
        out["_bound_shadow_id"] = shadow_id

    elif d == "REJECTED":
        if not decision.get("rationale"):
            raise GovernanceBlock("REJECTED requires rationale")
        if not decision.get("evidence_reviewed"):
            raise GovernanceBlock("REJECTED requires evidence_reviewed")
        out["_artifacts_bound"] = True

    elif d == "ROLLED_BACK":
        if not decision.get("rollback_target"):
            raise GovernanceBlock("ROLLED_BACK requires rollback_target")
        if not decision.get("rationale"):
            raise GovernanceBlock("ROLLED_BACK requires rationale")
        if not decision.get("evidence_reviewed"):
            raise GovernanceBlock("ROLLED_BACK requires evidence_reviewed")
        out["_artifacts_bound"] = True

    return out
