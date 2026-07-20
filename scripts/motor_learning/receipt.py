
"""learning_receipt emission and validation — mandatory for ratify/reject/rollback."""
from __future__ import annotations

import json
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
    similarity_score: float | None = None,
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
    if not decision_timestamp:
        raise SchemaError("decision_timestamp required")

    rid = "lr-" + content_hash({
        "d": mapped,
        "p": prior_id,
        "c": candidate_id,
        "t": decision_timestamp,
        "r": reviewer,
    })[:20]

    body = {
        "schema": "nf_motor_learning_receipt_v1",
        "receipt_id": rid,
        "learning_receipt_id": rid,
        "decision": mapped,
        "decision_outcome": mapped,
        "decision_timestamp": decision_timestamp,
        "prior_id": prior_id,
        "candidate_id": candidate_id,
        "origin_event": origin_event,
        "evidence_links": list(evidence_links),
        "confidence_before": confidence_before,
        "confidence_after": confidence_after,
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
        "ratified_at": decision_timestamp,
        "snapshot_id": snapshot_id or prior_id,
        "shadow_evidence_path": shadow_evidence_path,
        "similarity_score": similarity_score,
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
    }
    body["integrity_hash"] = integrity_hash({k: body[k] for k in sorted(body) if k != "integrity_hash"})
    return body


def validate_learning_receipt(receipt: dict[str, Any]) -> dict:
    if not isinstance(receipt, dict):
        raise SchemaError("receipt must be object")
    missing = [k for k in REQUIRED if k not in receipt]
    if missing:
        raise GovernanceBlock(f"learning_receipt missing required fields: {missing}")
    if receipt["decision"] not in ("accepted", "rejected", "rolled_back"):
        raise GovernanceBlock(f"invalid receipt decision: {receipt['decision']}")
    if not receipt.get("reviewer"):
        raise GovernanceBlock("receipt reviewer required")
    if not receipt.get("evidence_links"):
        raise GovernanceBlock("receipt evidence_links required")
    if not receipt.get("decision_timestamp") and not receipt.get("ratified_at"):
        raise GovernanceBlock("receipt decision_timestamp required")
    if not receipt.get("why_accepted_or_rejected") and not receipt.get("rationale"):
        raise GovernanceBlock("receipt rationale required")
    # verify integrity if present
    expected = integrity_hash({k: receipt[k] for k in sorted(receipt) if k != "integrity_hash"})
    if receipt.get("integrity_hash") and receipt["integrity_hash"] != expected:
        raise GovernanceBlock("receipt integrity_hash mismatch")
    return receipt


def write_receipt(receipt: dict, path: Path) -> Path:
    validate_learning_receipt(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    return path
