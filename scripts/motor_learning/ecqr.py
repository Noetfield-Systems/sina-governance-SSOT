"""ECQR decision gate — immutable after issuance; templates compile separately."""
from __future__ import annotations

import copy
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .confidence import RATIFY_THRESHOLD
from .hashutil import content_hash
from .artifacts import unwrap_shadow, unwrap_confidence, unwrap_candidate
from .validated import ValidatedECQR, _mint_ecqr
from . import ALGORITHM_VERSION, CONFIDENCE_VERSION

REQUIRED_DECISION = (
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
REQUIRED_RATIFIED_EXTRA = (
    "shadow_hash",
    "shadow_evidence_manifest_hash",
)

AUTO_PLACEHOLDERS = frozenset({"auto", "AUTO", ""})

ECQR_TEMPLATE_SCHEMA = "nf_motor_learning_ecqr_template_v1"
ECQR_DECISION_SCHEMA = "nf_motor_learning_ecqr_decision_v1"


def is_ecqr_template(obj: dict[str, Any]) -> bool:
    if not isinstance(obj, dict):
        return False
    if obj.get("schema") == ECQR_TEMPLATE_SCHEMA:
        return True
    if obj.get("kind") == "ECQR_TEMPLATE":
        return True
    # Heuristic: unresolved auto placeholders
    if obj.get("candidate_id") in AUTO_PLACEHOLDERS:
        return True
    if obj.get("shadow_result_ref") in AUTO_PLACEHOLDERS:
        return True
    if "shadow_hash" not in obj or obj.get("shadow_hash") in AUTO_PLACEHOLDERS:
        if obj.get("decision") == "RATIFIED":
            return True
    return False


def fixture_compile_ecqr(
    template: dict[str, Any],
    *,
    candidate: dict,
    shadow: dict,
    confidence: dict,
    mining_event_ids: list[str] | None = None,
    shadow_event_ids: list[str] | None = None,
) -> dict[str, Any]:
    """
    Separate pre-review compiler. Expands ECQR_TEMPLATE into a NEW ECQR_DECISION dict.
    Never mutates the template. Must NOT be called from governed run_pipeline.
    """
    if not isinstance(template, dict):
        raise SchemaError("ECQR template must be object")
    out = copy.deepcopy(template)
    out.pop("kind", None)
    if out.get("schema") == ECQR_TEMPLATE_SCHEMA:
        out["schema"] = ECQR_DECISION_SCHEMA
    else:
        out.setdefault("schema", ECQR_DECISION_SCHEMA)

    # Validate/normalize artifacts first
    cand = unwrap_candidate(candidate)
    sh = unwrap_shadow(shadow)
    conf = unwrap_confidence(confidence, shadow=sh)

    if out.get("candidate_id") in AUTO_PLACEHOLDERS or out.get("candidate_id") is None:
        out["candidate_id"] = cand["candidate_id"]
    if out.get("shadow_result_ref") in AUTO_PLACEHOLDERS or out.get("shadow_result_ref") is None:
        out["shadow_result_ref"] = f"shadow:{sh['shadow_id']}"
    out["shadow_hash"] = sh["content_hash"]
    out["shadow_id"] = sh["shadow_id"]
    out["shadow_evidence_manifest_hash"] = sh["evidence_manifest_hash"]
    out["confidence_before"] = conf["confidence_before"]
    out["confidence_after"] = conf["confidence_after"]
    out["confidence_hash"] = conf["content_hash"]

    mine = list(mining_event_ids or cand.get("source_event_ids") or [])
    sh_ids = list(shadow_event_ids or sh.get("shadow_event_ids") or [])
    existing = list(out.get("evidence_reviewed") or [])
    if not existing or existing == ["auto"]:
        out["evidence_reviewed"] = list(dict.fromkeys(
            mine + sh_ids + list(sh.get("evidence_refs") or []) + list(cand.get("evidence_refs") or [])
        ))
    else:
        out["evidence_reviewed"] = list(dict.fromkeys(existing + mine + sh_ids))

    out.setdefault("algorithm_versions", {
        "pipeline": ALGORITHM_VERSION,
        "confidence": CONFIDENCE_VERSION,
    })
    out["kind"] = "ECQR_DECISION"
    out["_compiled_from_fixture"] = True
    return out


def validate_ecqr_decision(
    decision: dict[str, Any] | ValidatedECQR,
    *,
    confidence: dict | None = None,
    shadow: dict | None = None,
    candidate: dict | None = None,
    require_bound_artifacts: bool = True,
) -> ValidatedECQR:
    """
    Validate an ECQR_DECISION WITHOUT mutating the caller object.
    Always revalidates even if a ValidatedECQR wrapper is supplied.
    Rejects ECQR_TEMPLATE / auto placeholders.
    """
    if isinstance(decision, ValidatedECQR):
        decision = decision.as_dict()
    if not isinstance(decision, dict):
        raise SchemaError("ECQR decision must be object")

    # Work on a copy — never mutate caller
    source_bytes_check = copy.deepcopy(decision)

    if is_ecqr_template(decision) or decision.get("kind") == "ECQR_TEMPLATE":
        raise GovernanceBlock(
            "ECQR_TEMPLATE is not a governed decision; compile separately before review issuance"
        )
    if decision.get("candidate_id") in AUTO_PLACEHOLDERS:
        raise GovernanceBlock("ECQR candidate_id unresolved; missing binding fails closed")
    if decision.get("shadow_result_ref") in AUTO_PLACEHOLDERS:
        raise GovernanceBlock("ECQR shadow_result_ref unresolved; missing binding fails closed")

    missing = [k for k in REQUIRED_DECISION if k not in decision]
    if missing:
        raise SchemaError(f"ECQR decision missing: {missing}")

    d = decision["decision"]
    if d == "RATIFIED":
        missing_r = [k for k in REQUIRED_RATIFIED_EXTRA if k not in decision or decision.get(k) in AUTO_PLACEHOLDERS]
        if missing_r:
            raise SchemaError(f"ECQR RATIFIED missing bindings: {missing_r}")
    if d not in ("RATIFIED", "REJECTED", "ROLLED_BACK"):
        raise SchemaError(f"invalid decision: {d}")
    reviewer = decision["reviewer"]
    if not str(reviewer).startswith(("test_reviewer:", "fixture:", "founder:", "gated_policy:", "machine_policy:")):
        raise GovernanceBlock(f"reviewer must be explicit; got {reviewer}")

    if decision.get("promoted_by_similarity") or decision.get("promoted_by_confidence_alone"):
        raise GovernanceBlock("similarity/confidence have no promotion authority")

    out = copy.deepcopy(decision)
    out.setdefault("schema", ECQR_DECISION_SCHEMA)
    out.setdefault("expires_at", None)
    out.setdefault("supersedes", None)
    out.setdefault("repositories", decision.get("repositories") or [])
    out.pop("_artifacts_bound", None)

    if d == "RATIFIED":
        if require_bound_artifacts and (shadow is None or confidence is None or candidate is None):
            raise GovernanceBlock("RATIFIED requires validated candidate+shadow+confidence artifacts")
        if shadow is None or confidence is None:
            raise GovernanceBlock("RATIFIED requires shadow and confidence artifacts")

        cand = unwrap_candidate(candidate) if candidate is not None else None
        sh = unwrap_shadow(shadow)
        conf = unwrap_confidence(confidence, shadow=sh)

        if cand and decision["candidate_id"] != cand.get("candidate_id"):
            raise GovernanceBlock(
                f"ECQR candidate_id mismatch: decision={decision['candidate_id']!r} "
                f"candidate={cand.get('candidate_id')!r}"
            )
        if sh.get("candidate_id") and decision["candidate_id"] != sh["candidate_id"]:
            raise GovernanceBlock("ECQR candidate_id mismatches shadow.candidate_id")

        shadow_id = sh.get("shadow_id")
        shadow_hash = sh.get("content_hash")
        ref = decision.get("shadow_result_ref")
        if ref not in (f"shadow:{shadow_id}", shadow_id, f"hash:{shadow_hash}"):
            raise GovernanceBlock(
                f"shadow_result_ref {ref!r} does not bind to shadow_id={shadow_id}"
            )
        if decision.get("shadow_hash") in (None, *AUTO_PLACEHOLDERS):
            raise GovernanceBlock("ECQR missing shadow_hash binding")
        if decision["shadow_hash"] != shadow_hash:
            raise GovernanceBlock(
                f"ECQR shadow_hash mismatch: decision={decision['shadow_hash']!r} computed={shadow_hash!r}"
            )
        manifest_hash = sh["evidence_manifest_hash"]
        if decision.get("shadow_evidence_manifest_hash") not in (None, *AUTO_PLACEHOLDERS):
            if decision["shadow_evidence_manifest_hash"] != manifest_hash:
                raise GovernanceBlock("ECQR shadow_evidence_manifest_hash mismatch")
        else:
            raise GovernanceBlock("ECQR missing shadow_evidence_manifest_hash binding")

        if float(decision["confidence_before"]) != float(conf["confidence_before"]):
            raise GovernanceBlock("ECQR confidence_before mismatches computed confidence")
        if float(decision["confidence_after"]) != float(conf["confidence_after"]):
            raise GovernanceBlock("ECQR confidence_after mismatches computed confidence")
        if decision.get("confidence_hash") and decision["confidence_hash"] != conf["content_hash"]:
            raise GovernanceBlock("ECQR confidence_hash mismatches confidence artifact")
        if not conf.get("meets_ratify_threshold"):
            raise GovernanceBlock("RATIFIED blocked: confidence below threshold")
        if conf["confidence_after"] < RATIFY_THRESHOLD:
            raise GovernanceBlock("RATIFIED blocked: confidence_after below ratify threshold")
        if not sh.get("ratifiable"):
            raise GovernanceBlock("RATIFIED blocked: shadow not ratifiable")

        reviewed = set(decision.get("evidence_reviewed") or [])
        allowed = set(conf.get("evidence_ids") or []) | set(sh.get("evidence_refs") or [])
        allowed |= set(sh.get("shadow_event_ids") or [])
        if cand:
            allowed |= set(cand.get("evidence_refs") or []) | set(cand.get("source_event_ids") or [])
        mine_need = set(cand.get("source_event_ids") or []) if cand else set()
        shadow_need = set(sh.get("shadow_event_ids") or [])
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
        if not alg:
            raise GovernanceBlock("ECQR algorithm_versions required")
        if alg.get("pipeline") and alg["pipeline"] != ALGORITHM_VERSION:
            raise GovernanceBlock("ECQR algorithm_versions.pipeline mismatch")
        if alg.get("confidence") and alg["confidence"] != CONFIDENCE_VERSION:
            raise GovernanceBlock("ECQR algorithm_versions.confidence mismatch")
        if not (decision.get("policy_versions") or {}):
            raise GovernanceBlock("ECQR policy_versions required")

        out["shadow_hash"] = shadow_hash
        out["shadow_id"] = shadow_id
        out["shadow_evidence_manifest_hash"] = manifest_hash
        out["confidence_hash"] = conf["content_hash"]
        if cand:
            out["candidate_hash"] = cand["content_hash"]

    elif d == "REJECTED":
        if not decision.get("rationale"):
            raise GovernanceBlock("REJECTED requires rationale")
        if not decision.get("evidence_reviewed"):
            raise GovernanceBlock("REJECTED requires evidence_reviewed")
        # Rejected may optionally bind artifacts if supplied
        if shadow is not None:
            unwrap_shadow(shadow)
        if confidence is not None:
            unwrap_confidence(confidence, shadow=shadow)

    elif d == "ROLLED_BACK":
        if not decision.get("rollback_target"):
            raise GovernanceBlock("ROLLED_BACK requires rollback_target")
        if not decision.get("rationale"):
            raise GovernanceBlock("ROLLED_BACK requires rationale")
        if not decision.get("evidence_reviewed"):
            raise GovernanceBlock("ROLLED_BACK requires evidence_reviewed")
        # Must already be ROLLED_BACK — caller must not rewrite
        if source_bytes_check.get("decision") != "ROLLED_BACK":
            raise GovernanceBlock("rollback ECQR must already have decision=ROLLED_BACK")

    decision_hash = content_hash({
        k: out[k] for k in sorted(out)
        if not str(k).startswith("_") and k != "decision_hash"
    })
    out["decision_hash"] = decision_hash
    return _mint_ecqr(out, decision_hash)
