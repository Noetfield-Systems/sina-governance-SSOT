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
        "prior_id": entity.get("prior_id"),
        "candidate_id": entity.get("candidate_id"),
    }
    if to_state in TERMINAL_RECEIPT_STATES:
        if not record.get("prior_id"):
            raise GovernanceBlock(f"{to_state} transition requires entity.prior_id")
        if not record.get("candidate_id"):
            raise GovernanceBlock(f"{to_state} transition requires entity.candidate_id")
    out = dict(entity)
    out["state"] = to_state
    out["status"] = STATUS_MAP.get(to_state, to_state.lower())
    hist = list(out.get("transition_history") or [])
    hist.append(record)
    out["transition_history"] = hist
    if rid:
        out["learning_receipt_id"] = rid
    return out


def _parse_hist_ts(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GovernanceBlock("transition timestamp must be non-empty ISO8601 string")
    v = value.strip().replace(" ", "T")
    try:
        if v.endswith("Z"):
            dt = datetime.fromisoformat(v.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(v)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
    except ValueError as exc:
        raise GovernanceBlock(f"transition timestamp invalid ISO8601: {value!r}") from exc
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def assert_history_prefix_preserved(
    existing_history: list[dict] | None,
    new_history: list[dict] | None,
    *,
    existing_state: str | None = None,
) -> None:
    """New history must preserve existing history as an immutable exact prefix + one legal step."""
    old = list(existing_history or [])
    new = list(new_history or [])
    if not old:
        raise GovernanceBlock("existing prior update requires nonempty stored transition_history")
    if len(new) != len(old) + 1:
        raise GovernanceBlock(
            f"existing history update must append exactly one transition; "
            f"stored_len={len(old)} new_len={len(new)}"
        )
    from .hashutil import canonical_json
    if canonical_json(new[: len(old)]) != canonical_json(old):
        # Distinguish truncate vs modify
        if len(new) <= len(old) or canonical_json(new[: min(len(new), len(old))]) != canonical_json(old[: min(len(new), len(old))]):
            raise GovernanceBlock("existing transition_history modified or truncated (immutable prefix required)")
        raise GovernanceBlock("existing transition_history prefix mismatch (immutable prefix required)")
    # Legal next transition from existing state
    cur = normalize_state(existing_state or old[-1]["to_state"])
    nxt_from = normalize_state(new[-1]["from_state"])
    nxt_to = normalize_state(new[-1]["to_state"])
    if nxt_from != cur:
        raise GovernanceBlock(
            f"update transition from_state={nxt_from} does not continue existing state={cur}"
        )
    if (cur, nxt_to) in FORBIDDEN or nxt_to not in ALLOWED.get(cur, set()):
        raise GovernanceBlock(f"illegal next transition from existing state: {cur}→{nxt_to}")


def validate_transition_history(
    history: list[dict] | None,
    *,
    final_state: str | None = None,
    entity_status: str | None = None,
    require_observed_origin: bool = False,
    existing_history: list[dict] | None = None,
    existing_state: str | None = None,
    candidate_id: str | None = None,
    prior_id: str | None = None,
) -> None:
    """
    Replay every recorded transition through ALLOWED/FORBIDDEN.
    Rejects illegal jumps, discontinuous histories, incomplete origins,
    and updates that do not preserve the stored history as an immutable prefix.
    """
    if not history:
        raise GovernanceBlock("terminal commit requires nonempty transition_history")
    if not isinstance(history, list):
        raise GovernanceBlock("transition_history must be a list")

    if existing_history is not None:
        assert_history_prefix_preserved(
            existing_history, history, existing_state=existing_state,
        )
    elif require_observed_origin:
        first_from = normalize_state(history[0].get("from_state"))
        if first_from != OBSERVED:
            raise GovernanceBlock(
                f"new terminal prior transition_history must begin at OBSERVED; "
                f"got first from_state={first_from}"
            )

    first = history[0]
    if "from_state" not in first or "to_state" not in first:
        raise GovernanceBlock("transition record missing from_state/to_state")
    state = normalize_state(first["from_state"])
    prev_ts: str | None = None

    for i, rec in enumerate(history):
        if not isinstance(rec, dict):
            raise GovernanceBlock(f"transition_history[{i}] must be object")
        for req in ("from_state", "to_state", "actor", "timestamp", "reason", "evidence"):
            if req not in rec:
                raise GovernanceBlock(f"transition_history[{i}] missing {req}")
        if not isinstance(rec["actor"], str) or not rec["actor"].strip():
            raise GovernanceBlock(f"transition_history[{i}] actor must be non-empty string")
        if not isinstance(rec["reason"], str) or not rec["reason"].strip():
            raise GovernanceBlock(f"transition_history[{i}] reason must be non-empty string")
        if not isinstance(rec["evidence"], list):
            raise GovernanceBlock(f"transition_history[{i}] evidence must be a list")
        ts = _parse_hist_ts(rec["timestamp"])
        if prev_ts is not None and ts < prev_ts:
            raise GovernanceBlock(
                f"transition_history[{i}] timestamp not monotonic: {ts} < {prev_ts}"
            )
        prev_ts = ts

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
        # Terminal steps require receipt id + identity binds
        if to_s in TERMINAL_RECEIPT_STATES:
            rid = rec.get("learning_receipt_id")
            if not rid or not isinstance(rid, str):
                raise GovernanceBlock(
                    f"transition_history[{i}] {from_s}→{to_s} requires learning_receipt_id"
                )
            if not rec.get("prior_id"):
                raise GovernanceBlock(
                    f"transition_history[{i}] terminal record requires prior_id"
                )
            if not rec.get("candidate_id"):
                raise GovernanceBlock(
                    f"transition_history[{i}] terminal record requires candidate_id"
                )
        # Bind ids when represented
        if candidate_id is not None and rec.get("candidate_id") not in (None, candidate_id):
            raise GovernanceBlock(
                f"transition_history[{i}] candidate_id mismatch: "
                f"{rec.get('candidate_id')!r} != {candidate_id!r}"
            )
        if prior_id is not None and rec.get("prior_id") not in (None, prior_id):
            raise GovernanceBlock(
                f"transition_history[{i}] prior_id mismatch: "
                f"{rec.get('prior_id')!r} != {prior_id!r}"
            )
        state = to_s

    if final_state is not None:
        want = normalize_state(final_state)
        if state != want:
            raise GovernanceBlock(
                f"transition history ends at {state} but claimed final_state={want}"
            )
    if entity_status is not None:
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
