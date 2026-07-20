"""learning_receipt emission and validation — mandatory for terminal states."""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .hashutil import content_hash, integrity_hash
from . import ALGORITHM_VERSION, CONFIDENCE_VERSION, SIMILARITY_VERSION

REQUIRED = (
    "receipt_id",
    "learning_receipt_id",
    "decision",
    "decision_timestamp",
    "prior_id",
    "candidate_id",
    "evidence_links",
    "confidence_before",
    "confidence_after",
    "reviewer",
    "rationale",
    "why_accepted_or_rejected",
    "affected_loops",
    "applicable_runways",
    "repositories",
    "expiry",
    "supersedes",
    "schema_versions",
    "algorithm_versions",
    "integrity_hash",
    "origin_event",
    "ratified_at",
    "snapshot_id",
)

DECISION_MAP = {
    "RATIFIED": "accepted",
    "REJECTED": "rejected",
    "ROLLED_BACK": "rolled_back",
    "accepted": "accepted",
    "rejected": "rejected",
    "rolled_back": "rolled_back",
}


def _parse_ts(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError("timestamp must be non-empty ISO8601 string")
    v = value.strip().replace(" ", "T")
    if v.endswith("Z"):
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _finite_unit(x: Any, name: str) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError) as exc:
        raise SchemaError(f"{name} must be float") from exc
    if not math.isfinite(v) or v < 0.0 or v > 1.0:
        raise SchemaError(f"{name} must be finite in [0,1], got {v}")
    return v


def build_learning_receipt(
    *,
    decision: str,
    prior_id: str | None,
    candidate_id: str | None,
    reviewer: str,
    rationale: str,
    evidence_links: list[str],
    confidence_before: float,
    confidence_after: float,
    affected_loops: list[str],
    applicable_runways: list[str],
    repositories: list[str] | None = None,
    origin_event: str,
    decision_timestamp: str,
    expiry: str | None = None,
    supersedes: str | None = None,
    superseded_by: str | None = None,
    rollback_target: str | None = None,
    snapshot_id: str | None = None,
    shadow_evidence_path: str | None = None,
    shadow_id: str | None = None,
    shadow_hash: str | None = None,
    confidence_hash: str | None = None,
    similarity_score: float | None = None,
    ecqr_decision_id: str | None = None,
) -> dict[str, Any]:
    mapped = DECISION_MAP.get(decision)
    if not mapped:
        raise SchemaError(f"invalid decision for receipt: {decision}")
    if not rationale or not str(rationale).strip():
        raise SchemaError("rationale/why required")
    if not reviewer:
        raise SchemaError("reviewer required")
    if not evidence_links:
        raise SchemaError("evidence_links required")
    ts = _parse_ts(decision_timestamp)
    cb = _finite_unit(confidence_before, "confidence_before")
    ca = _finite_unit(confidence_after, "confidence_after")

    if mapped == "rolled_back" and not rollback_target:
        raise SchemaError("rollback requires rollback_target")
    if mapped == "accepted" and not (shadow_id or shadow_evidence_path):
        raise SchemaError("ratification requires shadow binding")

    rid = "lr-" + content_hash({
        "d": mapped,
        "p": prior_id,
        "c": candidate_id,
        "t": ts,
        "r": reviewer,
    })[:20]

    body = {
        "schema": "nf_motor_learning_receipt_v1",
        "receipt_id": rid,
        "learning_receipt_id": rid,
        "decision": mapped,
        "decision_outcome": mapped,
        "decision_timestamp": ts,
        "prior_id": prior_id,
        "candidate_id": candidate_id,
        "origin_event": origin_event,
        "evidence_links": list(evidence_links),
        "confidence_before": cb,
        "confidence_after": ca,
        "reviewer": reviewer,
        "rationale": rationale,
        "why_accepted_or_rejected": rationale,
        "affected_loops": list(affected_loops),
        "applicable_runways": list(applicable_runways),
        "repositories": list(repositories or []),
        "expiry": expiry,
        "supersedes": supersedes,
        "superseded_by": superseded_by,
        "rollback_target": rollback_target,
        "ratified_at": ts,
        "snapshot_id": snapshot_id or prior_id,
        "shadow_evidence_path": shadow_evidence_path,
        "shadow_id": shadow_id,
        "shadow_hash": shadow_hash,
        "confidence_hash": confidence_hash,
        "similarity_score": similarity_score,
        "ecqr_decision_id": ecqr_decision_id,
        "schema_versions": {
            "receipt": "nf_motor_learning_receipt_v1",
            "organ": "nf_motor_learning_organ_v1",
        },
        "algorithm_versions": {
            "pipeline": ALGORITHM_VERSION,
            "similarity": SIMILARITY_VERSION,
            "confidence": CONFIDENCE_VERSION,
        },
        "policy_versions": {
            "decision_id": "NF-MOTOR-LEARNING-ORGAN-V1",
        },
        "integrity_hash_note": "content integrity over receipt fields; not reviewer authentication",
    }
    body["integrity_hash"] = integrity_hash({k: body[k] for k in sorted(body) if k != "integrity_hash"})
    return body


def validate_learning_receipt(receipt: dict[str, Any]) -> dict:
    if not isinstance(receipt, dict):
        raise SchemaError("receipt must be object")
    missing = [k for k in REQUIRED if k not in receipt]
    if missing:
        raise GovernanceBlock(f"learning_receipt missing required fields: {missing}")

    if receipt.get("receipt_id") != receipt.get("learning_receipt_id"):
        raise GovernanceBlock("receipt_id must equal learning_receipt_id")

    if receipt["decision"] not in ("accepted", "rejected", "rolled_back"):
        raise GovernanceBlock(f"invalid receipt decision: {receipt['decision']}")
    if not receipt.get("reviewer"):
        raise GovernanceBlock("receipt reviewer required")
    if not receipt.get("evidence_links"):
        raise GovernanceBlock("receipt evidence_links required")
    if not isinstance(receipt["evidence_links"], list) or not all(isinstance(x, str) and x for x in receipt["evidence_links"]):
        raise GovernanceBlock("evidence_links must be nonempty list of strings")

    _parse_ts(receipt.get("decision_timestamp") or receipt.get("ratified_at") or "")
    _finite_unit(receipt["confidence_before"], "confidence_before")
    _finite_unit(receipt["confidence_after"], "confidence_after")

    for field in ("affected_loops", "applicable_runways", "repositories"):
        val = receipt.get(field)
        if not isinstance(val, list) or not all(isinstance(x, str) and x.strip() for x in val):
            # repositories may be empty list for global, but must be a list
            if field == "repositories" and isinstance(val, list) and all(isinstance(x, str) for x in val):
                continue
            if field != "repositories":
                raise GovernanceBlock(f"{field} must be nonempty list of nonempty strings")
            raise GovernanceBlock(f"{field} must be a list of strings")
    if not receipt["affected_loops"] or not receipt["applicable_runways"]:
        raise GovernanceBlock("affected_loops and applicable_runways must be nonempty")

    if not receipt.get("why_accepted_or_rejected") and not receipt.get("rationale"):
        raise GovernanceBlock("receipt rationale required")

    if receipt["decision"] == "rolled_back" and not receipt.get("rollback_target"):
        raise GovernanceBlock("rollback receipt requires rollback_target")
    if receipt["decision"] == "accepted":
        if not (receipt.get("shadow_id") or receipt.get("shadow_evidence_path") or receipt.get("shadow_hash")):
            raise GovernanceBlock("ratification receipt requires shadow binding")
        if receipt.get("confidence_hash") is None and receipt.get("confidence_after") is None:
            raise GovernanceBlock("ratification receipt requires confidence binding")
    if receipt["decision"] == "rejected":
        if not receipt.get("rationale") and not receipt.get("why_accepted_or_rejected"):
            raise GovernanceBlock("rejection requires rationale")
        if not receipt.get("evidence_links"):
            raise GovernanceBlock("rejection requires reviewed evidence")

    expected = integrity_hash({k: receipt[k] for k in sorted(receipt) if k != "integrity_hash"})
    if receipt.get("integrity_hash") and receipt["integrity_hash"] != expected:
        raise GovernanceBlock("receipt integrity_hash mismatch (content integrity, not auth)")
    return receipt


def write_receipt(receipt: dict, path: Path) -> Path:
    validate_learning_receipt(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return path
