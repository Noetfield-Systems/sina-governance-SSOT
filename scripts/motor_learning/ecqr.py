
"""ECQR decision gate — ratification remains governed. No fake human review."""
from __future__ import annotations

from typing import Any

from .errors import GovernanceBlock, SchemaError
from .confidence import RATIFY_THRESHOLD

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


def validate_ecqr_decision(decision: dict[str, Any], *, confidence: dict | None = None, shadow: dict | None = None) -> dict:
    if not isinstance(decision, dict):
        raise SchemaError("ECQR decision must be object")
    missing = [k for k in REQUIRED if k not in decision]
    if missing:
        raise SchemaError(f"ECQR decision missing: {missing}")
    d = decision["decision"]
    if d not in ("RATIFIED", "REJECTED", "ROLLED_BACK"):
        raise SchemaError(f"invalid decision: {d}")
    reviewer = decision["reviewer"]
    # Explicit test/fixture reviewers allowed; never invent founder approval
    if not str(reviewer).startswith(("test_reviewer:", "fixture:", "founder:", "gated_policy:")):
        raise GovernanceBlock(f"reviewer must be explicit fixture/founder/gated_policy; got {reviewer}")

    if d == "RATIFIED":
        if not decision.get("shadow_result_ref"):
            raise GovernanceBlock("RATIFIED requires shadow_result_ref")
        if shadow and shadow.get("result") not in ("success", "mixed"):
            raise GovernanceBlock(f"RATIFIED blocked: shadow result={shadow.get('result')}")
        if confidence and not confidence.get("meets_ratify_threshold"):
            raise GovernanceBlock("RATIFIED blocked: confidence below threshold or contradictions")
        if confidence and confidence["confidence_after"] < RATIFY_THRESHOLD:
            raise GovernanceBlock("RATIFIED blocked: confidence_after below ratify threshold")

    # Similarity alone cannot promote — ensure decision does not claim similarity_authority
    if decision.get("promoted_by_similarity"):
        raise GovernanceBlock("similarity has no promotion authority")
    if decision.get("promoted_by_confidence_alone"):
        raise GovernanceBlock("confidence has no promotion authority")

    out = dict(decision)
    out.setdefault("schema", "nf_motor_learning_ecqr_decision_v1")
    out.setdefault("expires_at", None)
    out.setdefault("supersedes", None)
    out.setdefault("repositories", decision.get("repositories") or [])
    return out
