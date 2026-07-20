
"""Event ingestion and deterministic normalization."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .errors import SchemaError
from .hashutil import content_hash
from . import SCHEMA_VERSION

REQUIRED_RAW = ("event_id", "event_type", "source", "occurred_at", "action_attempted", "outcome")
SUPPORTED_TYPES = frozenset({
    "execution_failure",
    "execution_success",
    "recovery_success",
    "recovery_failure",
    "dispatch",
    "retry",
})
SUPPORTED_OUTCOMES = frozenset({"success", "failure", "abstain", "partial"})


def _parse_ts(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError("timestamp must be non-empty ISO8601 string")
    # Accept Z or offset; normalize to Z
    v = value.strip().replace(" ", "T")
    if v.endswith("Z"):
        dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
    else:
        dt = datetime.fromisoformat(v)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def normalize_event(raw: dict[str, Any], *, observed_at: str | None = None) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise SchemaError("event must be an object")
    missing = [k for k in REQUIRED_RAW if k not in raw or raw[k] in (None, "")]
    if missing:
        raise SchemaError(f"missing required fields: {missing}")
    if raw["event_type"] not in SUPPORTED_TYPES:
        raise SchemaError(f"unsupported event_type: {raw['event_type']}")
    if raw["outcome"] not in SUPPORTED_OUTCOMES:
        raise SchemaError(f"unsupported outcome: {raw['outcome']}")

    occurred_at = _parse_ts(raw["occurred_at"])
    observed = _parse_ts(observed_at or raw.get("observed_at") or occurred_at)

    # Stable identity for idempotency: prefer explicit event_id + content fingerprint of core fields
    core = {
        "event_id": str(raw["event_id"]),
        "event_type": raw["event_type"],
        "source": str(raw["source"]),
        "occurred_at": occurred_at,
        "action_attempted": str(raw["action_attempted"]),
        "outcome": raw["outcome"],
        "error_class": raw.get("error_class") or raw.get("error") or None,
        "recovery_path": raw.get("recovery_path"),
        "repository": raw.get("repository"),
        "runway": raw.get("runway"),
        "loop_id": raw.get("loop_id") or raw.get("actor_loop"),
    }
    ch = content_hash(core)

    normalized = {
        "schema": SCHEMA_VERSION,
        "schema_version": "1.0.0",
        "event_id": str(raw["event_id"]),
        "event_type": raw["event_type"],
        "source": str(raw["source"]),
        "occurred_at": occurred_at,
        "observed_at": observed,
        "actor": raw.get("actor"),
        "loop_id": core["loop_id"] or "motor_learning_organ_v1",
        "repository": raw.get("repository"),
        "runway": raw.get("runway"),
        "action_attempted": str(raw["action_attempted"]),
        "outcome": raw["outcome"],
        "error_class": core["error_class"],
        "recovery_path": raw.get("recovery_path"),
        "stage": raw.get("stage"),
        "provider": raw.get("provider"),
        "evidence_refs": list(raw.get("evidence_refs") or raw.get("evidence") or []),
        "raw_evidence_ref": raw.get("raw_evidence_ref") or f"raw://{raw['event_id']}",
        "content_hash": ch,
        "idempotency_key": f"{raw['event_id']}:{ch}",
    }
    return normalized


def normalize_many(
    raws: list[dict],
    *,
    seen_keys: set[str] | None = None,
    event_registry=None,
) -> tuple[list[dict], list[dict]]:
    """Return (accepted, duplicates). Same id+hash=duplicate; same id+diff hash=collision."""
    seen = seen_keys if seen_keys is not None else set()
    accepted: list[dict] = []
    duplicates: list[dict] = []
    for raw in raws:
        n = normalize_event(raw)
        if event_registry is not None:
            status = event_registry.register(n["event_id"], n["content_hash"])
            if status == "duplicate":
                duplicates.append(n)
                continue
        key = n["idempotency_key"]
        if key in seen:
            duplicates.append(n)
            continue
        # Also detect same event_id already accepted with same hash via seen by id
        id_key = f"id:{n['event_id']}:{n['content_hash']}"
        if id_key in seen:
            duplicates.append(n)
            continue
        seen.add(key)
        seen.add(id_key)
        accepted.append(n)
    return accepted, duplicates
