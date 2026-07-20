"""ECQR decision gate — immutable after issuance; templates compile separately."""
from __future__ import annotations

import copy
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .confidence import RATIFY_THRESHOLD
from .hashutil import content_hash
from .artifacts import unwrap_shadow, unwrap_confidence, unwrap_candidate, candidate_content_hash
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
REQUIRED_RATIFIED_BINDINGS = (
    "candidate_hash",
    "shadow_id",
    "shadow_hash",
    "shadow_evidence_manifest_hash",
    "mining_evidence_manifest_hash",
    "confidence_hash",
    "algorithm_versions",
)

AUTO_PLACEHOLDERS = frozenset({"auto", "AUTO", ""})

ECQR_TEMPLATE_SCHEMA = "nf_motor_learning_ecqr_template_v1"
ECQR_DECISION_SCHEMA = "nf_motor_learning_ecqr_decision_v1"


def is_ecqr_template(obj: dict[str, Any]) -> bool:
    if not isinstance(obj, dict):
        return False
    # Already-issued decisions: missing bindings fail closed in validate_ecqr_decision
    if obj.get("schema") == ECQR_DECISION_SCHEMA or obj.get("kind") == "ECQR_DECISION":
        return False
    if obj.get("schema") == ECQR_TEMPLATE_SCHEMA:
        return True
    if obj.get("kind") == "ECQR_TEMPLATE":
        return True
    if obj.get("candidate_id") in AUTO_PLACEHOLDERS:
        return True
    if obj.get("shadow_result_ref") in AUTO_PLACEHOLDERS:
        return True
    if obj.get("decision") == "RATIFIED":
        for k in REQUIRED_RATIFIED_BINDINGS:
            if k not in obj or obj.get(k) in AUTO_PLACEHOLDERS:
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
    shadow_events: list[dict] | None = None,
    confidence_inputs: dict | None = None,
    mining_events: list[dict] | None = None,
) -> dict[str, Any]:
    """Separate pre-review compiler. Emits a fully bound ECQR_DECISION."""
    if not isinstance(template, dict):
        raise SchemaError("ECQR template must be object")
    out = copy.deepcopy(template)
    out.pop("kind", None)
    out["schema"] = ECQR_DECISION_SCHEMA

    cand = unwrap_candidate(candidate)
    if shadow_events is None or confidence_inputs is None:
        raise GovernanceBlock(
            "fixture_compile_ecqr requires shadow_events and confidence_inputs for derivation"
        )
    sh = unwrap_shadow(shadow, candidate=cand, shadow_events=shadow_events, require_derivation=True)
    conf = unwrap_confidence(
        confidence, shadow=sh, confidence_inputs=confidence_inputs, require_derivation=True,
    )

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
    out["candidate_hash"] = cand["content_hash"]

    mine = list(mining_event_ids or cand.get("source_event_ids") or [])
    sh_ids = list(shadow_event_ids or sh.get("shadow_event_ids") or [])
    existing = list(out.get("evidence_reviewed") or [])
    if not existing or existing == ["auto"]:
        out["evidence_reviewed"] = list(dict.fromkeys(
            mine + sh_ids + list(sh.get("evidence_refs") or []) + list(cand.get("evidence_refs") or [])
        ))
    else:
        out["evidence_reviewed"] = list(dict.fromkeys(existing + mine + sh_ids))

    from .artifacts import mining_evidence_manifest
    from .shadow import assert_shadow_independence
    if mining_events is None:
        raise GovernanceBlock("fixture_compile_ecqr requires mining_events")
    assert_shadow_independence(candidate=cand, mining_events=mining_events, shadow_events=shadow_events)
    _, mine_hash = mining_evidence_manifest(cand, mining_events)
    out["mining_evidence_manifest_hash"] = mine_hash

    out["algorithm_versions"] = {
        "pipeline": ALGORITHM_VERSION,
        "confidence": CONFIDENCE_VERSION,
    }
    out["kind"] = "ECQR_DECISION"
    out["_compiled_from_fixture"] = True
    return out


def validate_ecqr_decision(
    decision: dict[str, Any] | ValidatedECQR,
    *,
    confidence: dict | None = None,
    shadow: dict | None = None,
    candidate: dict | None = None,
    shadow_events: list[dict] | None = None,
    confidence_inputs: dict | None = None,
    mining_events: list[dict] | None = None,
    require_bound_artifacts: bool = True,
) -> ValidatedECQR:
    """
    Validate an already fully bound ECQR_DECISION.
    May append decision_hash only — never populate material reviewer/artifact bindings.
    """
    if isinstance(decision, ValidatedECQR):
        decision = decision.as_dict()
    if not isinstance(decision, dict):
        raise SchemaError("ECQR decision must be object")

    source = copy.deepcopy(decision)

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
        raise GovernanceBlock(f"ECQR decision missing: {missing}")

    d = decision["decision"]
    if d not in ("RATIFIED", "REJECTED", "ROLLED_BACK"):
        raise SchemaError(f"invalid decision: {d}")

    if d == "RATIFIED":
        for k in REQUIRED_RATIFIED_BINDINGS:
            if k not in decision:
                raise GovernanceBlock(f"RATIFIED ECQR missing required binding: {k}")
            val = decision.get(k)
            if val in (None, ""):
                raise GovernanceBlock(f"RATIFIED ECQR missing required binding: {k}")
            if isinstance(val, str) and val in AUTO_PLACEHOLDERS:
                raise GovernanceBlock(f"RATIFIED ECQR missing required binding: {k}")
        alg = decision.get("algorithm_versions") or {}
        if not isinstance(alg, dict) or not alg.get("pipeline") or not alg.get("confidence"):
            raise GovernanceBlock("RATIFIED ECQR requires complete algorithm_versions (pipeline+confidence)")

    reviewer = decision["reviewer"]
    if not str(reviewer).startswith(("test_reviewer:", "fixture:", "founder:", "gated_policy:", "machine_policy:")):
        raise GovernanceBlock(f"reviewer must be explicit; got {reviewer}")

    if decision.get("promoted_by_similarity") or decision.get("promoted_by_confidence_alone"):
        raise GovernanceBlock("similarity/confidence have no promotion authority")

    # Copy for decision_hash only — do not populate material bindings
    out = copy.deepcopy(decision)
    out.pop("_artifacts_bound", None)

    if d == "RATIFIED":
        if require_bound_artifacts and (shadow is None or confidence is None or candidate is None):
            raise GovernanceBlock("RATIFIED requires validated candidate+shadow+confidence artifacts")
        if shadow is None or confidence is None or candidate is None:
            raise GovernanceBlock("RATIFIED requires shadow, confidence, and candidate artifacts")
        if shadow_events is None:
            raise GovernanceBlock("RATIFIED requires concrete shadow_events for derivation proof")
        if confidence_inputs is None:
            raise GovernanceBlock("RATIFIED requires canonical confidence_inputs for derivation proof")

        from .artifacts import mining_evidence_manifest, assert_confidence_inputs_canonical
        from .shadow import assert_shadow_independence

        if mining_events is None:
            raise GovernanceBlock("RATIFIED requires concrete mining_events for evidence binding")

        cand = unwrap_candidate(candidate)
        assert_shadow_independence(
            candidate=cand, mining_events=mining_events, shadow_events=shadow_events,
        )
        sh = unwrap_shadow(shadow, candidate=cand, shadow_events=shadow_events, require_derivation=True)
        cin = assert_confidence_inputs_canonical(
            confidence_inputs, candidate=cand, shadow=sh,
        )
        conf = unwrap_confidence(
            confidence, shadow=sh, confidence_inputs=cin, require_derivation=True,
        )

        if decision["candidate_id"] != cand.get("candidate_id"):
            raise GovernanceBlock("ECQR candidate_id mismatches candidate")
        if decision["candidate_hash"] != cand["content_hash"]:
            raise GovernanceBlock("ECQR candidate_hash mismatches candidate")
        if decision["shadow_id"] != sh["shadow_id"]:
            raise GovernanceBlock("ECQR shadow_id mismatches shadow")
        if decision["shadow_hash"] != sh["content_hash"]:
            raise GovernanceBlock("ECQR shadow_hash mismatches shadow")
        if decision["shadow_evidence_manifest_hash"] != sh["evidence_manifest_hash"]:
            raise GovernanceBlock("ECQR shadow_evidence_manifest_hash mismatches shadow")
        if decision["confidence_hash"] != conf["content_hash"]:
            raise GovernanceBlock("ECQR confidence_hash mismatches confidence")
        if float(decision["confidence_before"]) != float(conf["confidence_before"]):
            raise GovernanceBlock("ECQR confidence_before mismatches confidence")
        if float(decision["confidence_after"]) != float(conf["confidence_after"]):
            raise GovernanceBlock("ECQR confidence_after mismatches confidence")

        ref = decision.get("shadow_result_ref")
        if ref not in (f"shadow:{sh['shadow_id']}", sh["shadow_id"], f"hash:{sh['content_hash']}"):
            raise GovernanceBlock(f"shadow_result_ref {ref!r} does not bind to shadow")

        if not conf.get("meets_ratify_threshold"):
            raise GovernanceBlock("RATIFIED blocked: confidence below threshold")
        if conf["confidence_after"] < RATIFY_THRESHOLD:
            raise GovernanceBlock("RATIFIED blocked: confidence_after below ratify threshold")
        if not sh.get("ratifiable"):
            raise GovernanceBlock("RATIFIED blocked: shadow not ratifiable")

        mine_manifest, mine_hash = mining_evidence_manifest(cand, mining_events)
        if decision.get("mining_evidence_manifest_hash") != mine_hash:
            raise GovernanceBlock(
                "RATIFIED ECQR missing or mismatched mining_evidence_manifest_hash"
            )

        reviewed = list(decision.get("evidence_reviewed") or [])
        reviewed_set = set(reviewed)
        mine_need = set(cand.get("source_event_ids") or [])
        shadow_need = set(sh.get("shadow_event_ids") or [])
        # Complete manifest coverage OR explicit manifest hashes reviewed
        hash_ok = (
            mine_hash in reviewed_set and sh["evidence_manifest_hash"] in reviewed_set
        )
        if not hash_ok:
            if not mine_need.issubset(reviewed_set):
                raise GovernanceBlock(
                    "ECQR evidence_reviewed missing complete mining source_event_id coverage"
                )
            if not shadow_need.issubset(reviewed_set):
                raise GovernanceBlock(
                    "ECQR evidence_reviewed missing complete shadow_event_id coverage"
                )
        if not reviewed:
            raise GovernanceBlock("RATIFIED requires nonempty evidence_reviewed")
        allowed = set(conf.get("evidence_ids") or []) | set(sh.get("evidence_refs") or [])
        allowed |= set(sh.get("shadow_event_ids") or [])
        allowed |= set(cand.get("evidence_refs") or []) | set(cand.get("source_event_ids") or [])
        allowed |= {mine_hash, sh["evidence_manifest_hash"]}
        extra = reviewed_set - allowed
        if extra:
            raise GovernanceBlock(f"ECQR evidence_reviewed contains unbound IDs: {sorted(extra)}")

        alg = decision.get("algorithm_versions") or {}
        if alg.get("pipeline") != ALGORITHM_VERSION:
            raise GovernanceBlock("ECQR algorithm_versions.pipeline mismatch")
        if alg.get("confidence") != CONFIDENCE_VERSION:
            raise GovernanceBlock("ECQR algorithm_versions.confidence mismatch")
        if not (decision.get("policy_versions") or {}):
            raise GovernanceBlock("ECQR policy_versions required")

        # DO NOT populate material fields on out — only verify

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
        if source.get("decision") != "ROLLED_BACK":
            raise GovernanceBlock("rollback ECQR must already have decision=ROLLED_BACK")
        for k in (
            "rollback_target_prior_content_hash",
            "rollback_target_version",
            "prior_ratification_receipt_id",
        ):
            if k not in decision or decision.get(k) in (None, ""):
                raise GovernanceBlock(f"ROLLED_BACK ECQR missing required binding: {k}")

    # Append decision_hash only
    decision_hash = content_hash({
        k: out[k] for k in sorted(out)
        if not str(k).startswith("_") and k != "decision_hash"
    })
    out["decision_hash"] = decision_hash

    # Prove material fields of caller input were not repaired
    for k, v in source.items():
        if k == "decision_hash":
            continue
        if k not in out or out[k] != v:
            # out may add decision_hash and drop _artifacts_bound only
            if k.startswith("_"):
                continue
            if out.get(k) != v:
                raise GovernanceBlock(f"ECQR validation must not alter material field: {k}")

    return _mint_ecqr(out, decision_hash)
