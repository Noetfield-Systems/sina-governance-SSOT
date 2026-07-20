
"""Candidate/prior state machine — illegal transitions fail closed."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .errors import IllegalTransition, GovernanceBlock

# Canonical states
OBSERVED = "OBSERVED"
PROPOSED = "PROPOSED"
SHADOW = "SHADOW"
RATIFIED = "RATIFIED"
REJECTED = "REJECTED"
SUPERSEDED = "SUPERSEDED"
EXPIRED = "EXPIRED"
ROLLED_BACK = "ROLLED_BACK"

ALLOWED = {
    OBSERVED: {PROPOSED, REJECTED},
    PROPOSED: {SHADOW, REJECTED},
    SHADOW: {RATIFIED, REJECTED, PROPOSED},
    RATIFIED: {SUPERSEDED, EXPIRED, ROLLED_BACK},
    REJECTED: set(),
    SUPERSEDED: set(),
    EXPIRED: set(),
    ROLLED_BACK: set(),
}

# Forbidden shortcuts
FORBIDDEN = {
    (OBSERVED, RATIFIED),
    (OBSERVED, SHADOW),
    (PROPOSED, RATIFIED),
    (PROPOSED, ROLLED_BACK),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def transition(
    entity: dict[str, Any],
    to_state: str,
    *,
    actor: str,
    reason: str,
    evidence: list[str] | None = None,
    learning_receipt_id: str | None = None,
    require_receipt: bool | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    from_state = entity.get("state") or entity.get("status", "").upper()
    # map prior store lowercase
    if from_state in ("active",):
        from_state = RATIFIED
    if from_state in ("shadow",):
        from_state = SHADOW
    if from_state in ("proposed",):
        from_state = PROPOSED
    if from_state in ("observed",):
        from_state = OBSERVED
    if from_state in ("rejected",):
        from_state = REJECTED
    if from_state in ("rolled_back",):
        from_state = ROLLED_BACK

    if (from_state, to_state) in FORBIDDEN:
        raise IllegalTransition(f"forbidden transition {from_state}→{to_state}")
    allowed = ALLOWED.get(from_state, set())
    if to_state not in allowed:
        raise IllegalTransition(f"illegal transition {from_state}→{to_state}; allowed={sorted(allowed)}")

    needs_receipt = to_state in {RATIFIED, REJECTED, ROLLED_BACK}
    if require_receipt is None:
        require_receipt = needs_receipt
    if require_receipt and needs_receipt and not learning_receipt_id:
        raise GovernanceBlock(f"{to_state} requires learning_receipt_id")

    ts = timestamp or _now()
    record = {
        "from_state": from_state,
        "to_state": to_state,
        "actor": actor,
        "timestamp": ts,
        "reason": reason,
        "evidence": list(evidence or []),
        "learning_receipt_id": learning_receipt_id,
    }
    out = dict(entity)
    out["state"] = to_state
    # prior store status mapping
    status_map = {
        RATIFIED: "active",
        REJECTED: "rejected",
        SHADOW: "shadow",
        PROPOSED: "proposed",
        OBSERVED: "observed",
        ROLLED_BACK: "rolled_back",
        SUPERSEDED: "superseded",
        EXPIRED: "expired",
    }
    out["status"] = status_map.get(to_state, to_state.lower())
    hist = list(out.get("transition_history") or [])
    hist.append(record)
    out["transition_history"] = hist
    return out
