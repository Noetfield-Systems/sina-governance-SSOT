"""Candidate/prior state machine — illegal transitions fail closed."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .errors import IllegalTransition, GovernanceBlock

OBSERVED = "OBSERVED"
PROPOSED = "PROPOSED"
SHADOW = "SHADOW"
RATIFIED = "RATIFIED"
REJECTED = "REJECTED"
SUPERSEDED = "SUPERSEDED"
EXPIRED = "EXPIRED"
ROLLED_BACK = "ROLLED_BACK"

TERMINAL_RECEIPT_STATES = frozenset({RATIFIED, REJECTED, ROLLED_BACK})

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

FORBIDDEN = {
    (OBSERVED, RATIFIED),
    (OBSERVED, SHADOW),
    (PROPOSED, RATIFIED),
    (PROPOSED, ROLLED_BACK),
}

STATUS_MAP = {
    RATIFIED: "active",
    REJECTED: "rejected",
    SHADOW: "shadow",
    PROPOSED: "proposed",
    OBSERVED: "observed",
    ROLLED_BACK: "rolled_back",
    SUPERSEDED: "superseded",
    EXPIRED: "expired",
}


def normalize_state(raw: str | None) -> str:
    if not raw:
        raise IllegalTransition("missing state")
    s = str(raw)
    mapping = {
        "active": RATIFIED,
        "shadow": SHADOW,
        "proposed": PROPOSED,
        "observed": OBSERVED,
        "rejected": REJECTED,
        "rolled_back": ROLLED_BACK,
        "superseded": SUPERSEDED,
        "expired": EXPIRED,
    }
    return mapping.get(s, s.upper())


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
    learning_receipt: dict | None = None,
    require_receipt: bool | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """
    Transition entity state.

    For RATIFIED / REJECTED / ROLLED_BACK:
    - receipt is ALWAYS required (require_receipt cannot disable this).
    - learning_receipt object (validated) or learning_receipt_id+validated receipt must be present.
    """
    from_state = normalize_state(entity.get("state") or entity.get("status"))
    to_state = to_state.upper()

    if (from_state, to_state) in FORBIDDEN:
        raise IllegalTransition(f"forbidden transition {from_state}→{to_state}")
    allowed = ALLOWED.get(from_state, set())
    if to_state not in allowed:
        raise IllegalTransition(f"illegal transition {from_state}→{to_state}; allowed={sorted(allowed)}")

    # Terminal receipt is NON-BYPASSABLE. require_receipt=False is ignored for terminals.
    if to_state in TERMINAL_RECEIPT_STATES:
        if require_receipt is False:
            # Explicit adversarial attempt — still fail closed
            raise GovernanceBlock(
                f"{to_state} requires validated learning_receipt; require_receipt=False is forbidden"
            )
        rid = learning_receipt_id
        if learning_receipt is not None:
            from .receipt import validate_learning_receipt
            validate_learning_receipt(learning_receipt)
            rid = learning_receipt.get("receipt_id") or learning_receipt.get("learning_receipt_id")
            # decision must match target
            expected = {"RATIFIED": "accepted", "REJECTED": "rejected", "ROLLED_BACK": "rolled_back"}[to_state]
            if learning_receipt.get("decision") != expected:
                raise GovernanceBlock(
                    f"receipt decision {learning_receipt.get('decision')} mismatches transition {to_state}"
                )
        if not rid:
            raise GovernanceBlock(f"{to_state} requires validated learning_receipt / learning_receipt_id")
        learning_receipt_id = rid
    else:
        # Non-terminal: require_receipt may force a receipt but is not used today
        if require_receipt and not learning_receipt_id:
            raise GovernanceBlock(f"{to_state} require_receipt=True but no learning_receipt_id")

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
    out["status"] = STATUS_MAP.get(to_state, to_state.lower())
    hist = list(out.get("transition_history") or [])
    hist.append(record)
    out["transition_history"] = hist
    if learning_receipt_id:
        out["learning_receipt_id"] = learning_receipt_id
    return out
