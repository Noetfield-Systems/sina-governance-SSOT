
"""Signal/pattern extraction from normalized events."""
from __future__ import annotations

from typing import Any

from .hashutil import content_hash


def extract_signal(event: dict[str, Any]) -> dict[str, Any]:
    fingerprint = {
        "action_attempted": event["action_attempted"],
        "outcome": event["outcome"],
        "error_class": event.get("error_class"),
        "recovery_path": event.get("recovery_path"),
        "runway": event.get("runway"),
        "repository": event.get("repository"),
        "stage": event.get("stage"),
        "loop_id": event.get("loop_id"),
    }
    signal_id = "sig-" + content_hash(fingerprint)[:16]
    return {
        "schema": "nf_motor_learning_signal_v1",
        "signal_id": signal_id,
        "fingerprint": fingerprint,
        "fingerprint_hash": content_hash(fingerprint),
        "trigger_context": {
            "event_type": event["event_type"],
            "source": event["source"],
            "stage": event.get("stage"),
        },
        "attempted_action": event["action_attempted"],
        "observed_outcome": event["outcome"],
        "recovery_path": event.get("recovery_path"),
        "scope": {
            "loop_id": event.get("loop_id"),
            "runway": event.get("runway"),
            "repository": event.get("repository"),
        },
        "evidence_refs": list(event.get("evidence_refs") or []) + [event["event_id"]],
        "source_event_ids": [event["event_id"]],
        "occurrence_count": 1,
        "first_seen": event["occurred_at"],
        "last_seen": event["occurred_at"],
    }


def extract_many(events: list[dict]) -> list[dict]:
    return [extract_signal(e) for e in events]
