"""ECQR decision gate — immutable after issuance; bind computed artifacts exactly."""
from __future__ import annotations

import copy
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .confidence import RATIFY_THRESHOLD
from .hashutil import content_hash
from .validated import mint_validated_ecqr, ValidatedECQR, is_validated_ecqr
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

AUTO_PLACEHOLDERS = frozenset({"auto", "AUTO", ""})


def fixture_compile_ecqr(
    fixture: dict[str, Any],
    *,
    candidate: dict,
    shadow: dict,
    confidence: dict,
    mining_event_ids: list[str] | None = None,
    shadow_event_ids: list[str] | None = None,
) -> dict[str, Any]:
    """
    Expand fixture "auto" placeholders into a NEW decision dict.
    Never mutates the original fixture object.
    """
    out = copy.deepcopy(fixture)
    if out.get("candidate_id") in AUTO_PLACEHOLDERS or out.get("candidate_id") is None:
        out["candidate_id"] = candidate["candidate_id"]
    if out.get("shadow_result_ref") in AUTO_PLACEHOLDERS or out.get("shadow_result_ref") is None:
        out["shadow_result_ref"] = f"shadow:{shadow['shadow_id']}"
    if out.get("shadow_hash") in AUTO_PLACEHOLDERS or out.get("shadow_hash") is None:
        out["shadow_hash"] = shadow.get("content_hash")
    # confidence auto: only when both are exactly 0.0 placeholder convention OR missing
    if "confidence_before" not in out or out.get("_auto_confidence"):
        out["confidence_before"] = confidence["confidence_before"]
        out["confidence_after"] = confidence["confidence_after"]
    elif float(out.get("confidence_before", 0)) == 0.0 and float(out.get("confidence_after", 0)) == 0.0:
        # Fixture convention: 0.0/0.0 means auto-fill (compile step only)
        out["confidence_before"] = confidence["confidence_before"]
        out["confidence_after"] = confidence["confidence_after"]
    mine = list(mining_event_ids or candidate.get("source_event_ids") or [])
    sh = list(shadow_event_ids or shadow.get("shadow_event_ids") or [])
    existing = list(out.get("evidence_reviewed") or [])
    if not existing or existing == ["auto"]:
        out["evidence_reviewed"] = list(dict.fromkeys(
            mine + sh + list(shadow.get("evidence_refs") or []) + list(candidate.get("evidence_refs") or [])
        ))
    else:
        # Preserve reviewer list but ensure both manifests are covered (compile-time only)
        out["evidence_reviewed"] = list(dict.fromkeys(existing + mine + sh))
    out.setdefault("algorithm_versions", {
        "pipeline": ALGORITHM_VERSION,
        "confidence": CONFIDENCE_VERSION,
    })
    if shadow.get("evidence_manifest_hash"):
        out.setdefault("shadow_evidence_manifest_hash", shadow["evidence_manifest_hash"])
    out["_compiled_from_fixture"] = True
    return out


def validate_ecqr_decision(
    decision: dict[str, Any],
    *,
    confidence: dict | None = None,
    shadow: dict | None = None,
    candidate: dict | None = None,
    require_bound_artifacts: bool = True,
) -> ValidatedECQR:
    """
    Validate an ECQR decision WITHOUT mutating it.
    Returns an opaque ValidatedECQR. Callers cannot forge via plain dict markers.
    """
    if is_validated_ecqr(decision):
        return decision
    if not isinstance(decision, dict):
        raise SchemaError("ECQR decision must be object")

    # Refuse unresolved auto placeholders — must be compiled first
    if decision.get("candidate_id") in AUTO_PLACEHOLDERS:
        raise GovernanceBlock("ECQR candidate_id is unresolved auto placeholder; compile fixture first")
    if decision.get("shadow_result_ref") in AUTO_PLACEHOLDERS:
        raise GovernanceBlock("ECQR shadow_result_ref is unresolved auto placeholder; compile fixture first")

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

    # Build validated payload as a copy — never mutate caller decision
    out = copy.deepcopy(decision)
    out.setdefault("schema", "nf_motor_learning_ecqr_decision_v1")
    out.setdefault("expires_at", None)
    out.setdefault("supersedes", None)
    out.setdefault("repositories", decision.get("repositories") or [])
    # Strip any caller-supplied internal markers — they are never trust
    out.pop("_artifacts_bound", None)
    out.pop("_bound_confidence_version", None)
    out.pop("_bound_shadow_id", None)

    if d == "RATIFIED":
        if require_bound_artifacts:
            if shadow is None:
                raise GovernanceBlock("RATIFIED requires non-None validated shadow artifact")
            if confidence is None:
                raise GovernanceBlock("RATIFIED requires non-None validated confidence artifact")
        if shadow is None or confidence is None:
            raise GovernanceBlock("RATIFIED requires shadow and confidence artifacts")

        # Explicit mismatch → GovernanceBlock (no overwrite)
        if candidate and decision["candidate_id"] != candidate.get("candidate_id"):
            raise GovernanceBlock(
                f"ECQR candidate_id mismatch: decision={decision['candidate_id']!r} "
                f"candidate={candidate.get('candidate_id')!r}"
            )
        if shadow.get("candidate_id") and decision["candidate_id"] != shadow["candidate_id"]:
            raise GovernanceBlock("ECQR candidate_id mismatches shadow.candidate_id")

        shadow_id = shadow.get("shadow_id")
        shadow_hash = shadow.get("content_hash") or shadow.get("shadow_hash")
        ref = decision.get("shadow_result_ref")
        if not shadow_id:
            raise GovernanceBlock("shadow artifact missing shadow_id")
        if ref not in (f"shadow:{shadow_id}", shadow_id, f"hash:{shadow_hash}"):
            raise GovernanceBlock(
                f"shadow_result_ref {ref!r} does not bind to shadow_id={shadow_id} hash={shadow_hash}"
            )
        # Missing binding
        if "shadow_hash" not in decision or decision.get("shadow_hash") in (None, *AUTO_PLACEHOLDERS):
            raise GovernanceBlock("ECQR missing shadow_hash binding")
        if decision["shadow_hash"] != shadow_hash:
            raise GovernanceBlock(
                f"ECQR shadow_hash mismatch: decision={decision['shadow_hash']!r} computed={shadow_hash!r}"
            )

        # Manifest binding
        manifest_hash = shadow.get("evidence_manifest_hash")
        if not manifest_hash:
            raise GovernanceBlock("shadow missing evidence_manifest_hash")
        if decision.get("shadow_evidence_manifest_hash") and decision["shadow_evidence_manifest_hash"] != manifest_hash:
            raise GovernanceBlock("ECQR shadow_evidence_manifest_hash mismatch")
        out["shadow_evidence_manifest_hash"] = manifest_hash

        if float(decision["confidence_before"]) != float(confidence["confidence_before"]):
            raise GovernanceBlock("ECQR confidence_before mismatches computed confidence")
        if float(decision["confidence_after"]) != float(confidence["confidence_after"]):
            raise GovernanceBlock("ECQR confidence_after mismatches computed confidence")
        if not confidence.get("meets_ratify_threshold"):
            raise GovernanceBlock("RATIFIED blocked: confidence below threshold or contradictions")
        if confidence["confidence_after"] < RATIFY_THRESHOLD:
            raise GovernanceBlock("RATIFIED blocked: confidence_after below ratify threshold")
        if not shadow.get("ratifiable"):
            raise GovernanceBlock(f"RATIFIED blocked: shadow not ratifiable result={shadow.get('result')}")
        if shadow.get("result") not in ("success", "mixed"):
            raise GovernanceBlock(f"RATIFIED blocked: shadow result={shadow.get('result')}")

        reviewed = set(decision.get("evidence_reviewed") or [])
        allowed = set(confidence.get("evidence_ids") or []) | set(shadow.get("evidence_refs") or [])
        allowed |= set(shadow.get("shadow_event_ids") or [])
        if candidate:
            allowed |= set(candidate.get("evidence_refs") or []) | set(candidate.get("source_event_ids") or [])
        # Must cover both mining and shadow manifests
        mine_need = set(candidate.get("source_event_ids") or []) if candidate else set()
        shadow_need = set(shadow.get("shadow_event_ids") or [])
        if mine_need and not (mine_need & reviewed):
            raise GovernanceBlock("ECQR evidence_reviewed missing mining manifest coverage")
        if shadow_need and not (shadow_need & reviewed):
            raise GovernanceBlock("ECQR evidence_reviewed missing shadow manifest coverage")
        if not reviewed:
            raise GovernanceBlock("RATIFIED requires nonempty evidence_reviewed")
        extra = reviewed - allowed
        if extra:
            raise GovernanceBlock(f"ECQR evidence_reviewed contains unbound IDs: {sorted(extra)}")

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
        out["confidence_hash"] = confidence.get("content_hash")

    elif d == "REJECTED":
        if not decision.get("rationale"):
            raise GovernanceBlock("REJECTED requires rationale")
        if not decision.get("evidence_reviewed"):
            raise GovernanceBlock("REJECTED requires evidence_reviewed")

    elif d == "ROLLED_BACK":
        if not decision.get("rollback_target"):
            raise GovernanceBlock("ROLLED_BACK requires rollback_target")
        if not decision.get("rationale"):
            raise GovernanceBlock("ROLLED_BACK requires rationale")
        if not decision.get("evidence_reviewed"):
            raise GovernanceBlock("ROLLED_BACK requires evidence_reviewed")

    decision_hash = content_hash({
        k: out[k] for k in sorted(out)
        if not str(k).startswith("_") and k != "decision_hash"
    })
    out["decision_hash"] = decision_hash
    return mint_validated_ecqr(out, decision_hash)
