"""Opaque validated capability objects — cannot be forged via plain dicts."""
from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Any

_ECQR_SECRET = secrets.token_hex(16)
_RECEIPT_SECRET = secrets.token_hex(16)
_STORE_CAP_SECRET = secrets.token_hex(16)


@dataclass(frozen=True)
class ValidatedECQR:
    decision: str
    payload: dict[str, Any]
    decision_hash: str
    _secret: str = field(repr=False, compare=False)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class ValidatedReceipt:
    receipt_id: str
    payload: dict[str, Any]
    integrity_hash: str
    _secret: str = field(repr=False, compare=False)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class W1ReferenceStoreCapability:
    """Library-level capability required for W1 reference persistence (never live-consumable)."""

    store_kind: str
    _secret: str = field(repr=False, compare=False)


def mint_validated_ecqr(payload: dict[str, Any], decision_hash: str) -> ValidatedECQR:
    return ValidatedECQR(
        decision=payload["decision"],
        payload=dict(payload),
        decision_hash=decision_hash,
        _secret=_ECQR_SECRET,
    )


def mint_validated_receipt(payload: dict[str, Any]) -> ValidatedReceipt:
    return ValidatedReceipt(
        receipt_id=payload["receipt_id"],
        payload=dict(payload),
        integrity_hash=payload["integrity_hash"],
        _secret=_RECEIPT_SECRET,
    )


def mint_w1_reference_store_capability() -> W1ReferenceStoreCapability:
    return W1ReferenceStoreCapability(store_kind="w1_reference", _secret=_STORE_CAP_SECRET)


def is_validated_ecqr(obj: Any) -> bool:
    return isinstance(obj, ValidatedECQR) and getattr(obj, "_secret", None) == _ECQR_SECRET


def is_validated_receipt(obj: Any) -> bool:
    return isinstance(obj, ValidatedReceipt) and getattr(obj, "_secret", None) == _RECEIPT_SECRET


def is_w1_reference_store_capability(obj: Any) -> bool:
    return (
        isinstance(obj, W1ReferenceStoreCapability)
        and getattr(obj, "_secret", None) == _STORE_CAP_SECRET
        and obj.store_kind == "w1_reference"
    )
