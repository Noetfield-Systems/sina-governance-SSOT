"""Candidate/prior state machine — illegal transitions fail closed."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .errors import IllegalTransition, GovernanceBlock
from .validated import ValidatedReceipt

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

DECISION_FOR_STATE = {
    RATIFIED: "accepted",
    REJECTED: "rejected",
    ROLLED_BACK: "rolled_back",
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


def _require_validated_receipt(
    *,
    to_state: str,
    learning_receipt: Any,
    learning_receipt_id: str | None,
    entity: dict[str, Any],
    receipt_resolver=None,
) -> ValidatedReceipt:
    """
    Terminal transitions require a complete canonically revalidated receipt.
    Wrapper possession never bypasses validation — always revalidate as_dict().
    """
    if learning_receipt is None and learning_receipt_id and receipt_resolver is not None:
        loaded = receipt_resolver(learning_receipt_id)
        if loaded is None:
            raise GovernanceBlock(f"{to_state}: receipt_resolver returned nothing for id={learning_receipt_id}")
        learning_receipt = loaded

    if learning_receipt is None:
        raise GovernanceBlock(
            f"{to_state} requires a complete validated learning_receipt object; "
            f"raw learning_receipt_id alone is never proof"
        )

    # ALWAYS extract dict and revalidate — even for ValidatedReceipt wrappers
    if isinstance(learning_receipt, ValidatedReceipt):
        body = learning_receipt.as_dict()
    elif isinstance(learning_receipt, dict):
        body = learning_receipt
    else:
        raise GovernanceBlock(f"{to_state}: learning_receipt must be ValidatedReceipt or dict")

    from .receipt import validate_and_mint_receipt
    vr = validate_and_mint_receipt(body)

    expected = DECISION_FOR_STATE[to_state]
    if vr.as_dict().get("decision") != expected:
        raise GovernanceBlock(
            f"receipt decision {vr.as_dict().get('decision')!r} mismatches transition {to_state}"
        )

    body = vr.as_dict()
    if entity.get("candidate_id") and body.get("candidate_id"):
        if entity["candidate_id"] != body["candidate_id"]:
            raise GovernanceBlock("receipt.candidate_id mismatches entity.candidate_id")
    if entity.get("prior_id") and body.get("prior_id"):
        if entity["prior_id"] != body["prior_id"]:
            raise GovernanceBlock("receipt.prior_id mismatches entity.prior_id")

    if not body.get("reviewer"):
        raise GovernanceBlock("receipt missing reviewer")
    if not body.get("evidence_links"):
        raise GovernanceBlock("receipt missing evidence_links")

    if to_state == RATIFIED:
        for req in (
            "shadow_id", "shadow_hash", "shadow_evidence_manifest_hash",
            "confidence_hash", "ecqr_decision_hash", "candidate_hash",
        ):
            if not body.get(req):
                raise GovernanceBlock(f"ratification receipt missing binding field: {req}")

    return vr


def transition(
    entity: dict[str, Any],
    to_state: str,
    *,
    actor: str,
    reason: str,
    evidence: list[str] | None = None,
    learning_receipt_id: str | None = None,
    learning_receipt: Any = None,
    receipt_resolver=None,
    require_receipt: bool | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    from_state = normalize_state(entity.get("state") or entity.get("status"))
    to_state = to_state.upper()

    if (from_state, to_state) in FORBIDDEN:
        raise IllegalTransition(f"forbidden transition {from_state}→{to_state}")
    allowed = ALLOWED.get(from_state, set())
    if to_state not in allowed:
        raise IllegalTransition(f"illegal transition {from_state}→{to_state}; allowed={sorted(allowed)}")

    rid = None
    if to_state in TERMINAL_RECEIPT_STATES:
        if require_receipt is False:
            raise GovernanceBlock(
                f"{to_state} requires validated learning_receipt; require_receipt=False is forbidden"
            )
        if learning_receipt is None and receipt_resolver is None and learning_receipt_id:
            raise GovernanceBlock(
                f"{to_state}: learning_receipt_id alone is never proof; "
                f"supply validated learning_receipt object or receipt_resolver"
            )
        vr = _require_validated_receipt(
            to_state=to_state,
            learning_receipt=learning_receipt,
            learning_receipt_id=learning_receipt_id,
            entity=entity,
            receipt_resolver=receipt_resolver,
        )
        rid = vr.receipt_id
        if learning_receipt_id and learning_receipt_id != rid:
            raise GovernanceBlock("learning_receipt_id mismatches validated receipt.receipt_id")
    else:
        if require_receipt and not (learning_receipt or learning_receipt_id):
            raise GovernanceBlock(f"{to_state} require_receipt=True but no learning_receipt")

    ts = timestamp or _now()
    record = {
        "from_state": from_state,
        "to_state": to_state,
        "actor": actor,
        "timestamp": ts,
        "reason": reason,
        "evidence": list(evidence or []),
        "learning_receipt_id": rid,
    }
    out = dict(entity)
    out["state"] = to_state
    out["status"] = STATUS_MAP.get(to_state, to_state.lower())
    hist = list(out.get("transition_history") or [])
    hist.append(record)
    out["transition_history"] = hist
    if rid:
        out["learning_receipt_id"] = rid
    return out


def validate_transition_history(
    history: list[dict] | None,
    *,
    final_state: str | None = None,
    entity_status: str | None = None,
) -> None:
    """
    Replay every recorded transition through ALLOWED/FORBIDDEN.
    Rejects illegal jumps (OBSERVED→RATIFIED, PROPOSED→RATIFIED), discontinuous
    histories, and histories whose final state merely appears correct.
    """
    if not history:
        raise GovernanceBlock("terminal commit requires nonempty transition_history")
    if not isinstance(history, list):
        raise GovernanceBlock("transition_history must be a list")

    # Seed state from first record's from_state
    first = history[0]
    if "from_state" not in first or "to_state" not in first:
        raise GovernanceBlock("transition record missing from_state/to_state")
    state = normalize_state(first["from_state"])

    for i, rec in enumerate(history):
        if not isinstance(rec, dict):
            raise GovernanceBlock(f"transition_history[{i}] must be object")
        if "from_state" not in rec or "to_state" not in rec:
            raise GovernanceBlock(f"transition_history[{i}] missing from_state/to_state")
        from_s = normalize_state(rec["from_state"])
        to_s = normalize_state(rec["to_state"])
        if from_s != state:
            raise GovernanceBlock(
                f"discontinuous transition history at index {i}: "
                f"expected from_state={state} got {from_s}"
            )
        if (from_s, to_s) in FORBIDDEN:
            raise GovernanceBlock(
                f"forbidden transition in history at index {i}: {from_s}→{to_s}"
            )
        allowed = ALLOWED.get(from_s, set())
        if to_s not in allowed:
            raise GovernanceBlock(
                f"illegal transition in history at index {i}: {from_s}→{to_s}; "
                f"allowed={sorted(allowed)}"
            )
        state = to_s

    if final_state is not None:
        want = normalize_state(final_state)
        if state != want:
            raise GovernanceBlock(
                f"transition history ends at {state} but claimed final_state={want}"
            )
    if entity_status is not None:
        # Map store status to lifecycle state
        status_to_state = {
            "active": RATIFIED,
            "rejected": REJECTED,
            "rolled_back": ROLLED_BACK,
            "shadow": SHADOW,
            "proposed": PROPOSED,
            "observed": OBSERVED,
            "superseded": SUPERSEDED,
            "expired": EXPIRED,
        }
        want = status_to_state.get(entity_status, normalize_state(entity_status))
        if state != want:
            raise GovernanceBlock(
                f"transition history ends at {state} but prior status={entity_status} "
                f"implies {want}"
            )
