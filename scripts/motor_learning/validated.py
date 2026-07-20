"""Validated wrappers — minted only by validators after canonical checks.

Wrapper possession is not authorization. lifecycle/PriorStore always revalidate as_dict().
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidatedECQR:
    decision: str
    payload: dict[str, Any]
    decision_hash: str
    _minted_by_validator: bool = field(default=True, repr=False, compare=False)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class ValidatedReceipt:
    receipt_id: str
    payload: dict[str, Any]
    integrity_hash: str
    _minted_by_validator: bool = field(default=True, repr=False, compare=False)

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class ValidatedShadow:
    payload: dict[str, Any]
    content_hash: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class ValidatedConfidence:
    payload: dict[str, Any]
    content_hash: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


@dataclass(frozen=True)
class ValidatedCandidate:
    payload: dict[str, Any]
    content_hash: str

    def as_dict(self) -> dict[str, Any]:
        return dict(self.payload)


def _mint_ecqr(payload: dict[str, Any], decision_hash: str) -> ValidatedECQR:
    """Internal — only from validate_ecqr_decision after validation."""
    return ValidatedECQR(
        decision=payload["decision"],
        payload=dict(payload),
        decision_hash=decision_hash,
        _minted_by_validator=True,
    )


def _mint_receipt(payload: dict[str, Any]) -> ValidatedReceipt:
    """Internal — only from validate_and_mint_receipt after validation."""
    return ValidatedReceipt(
        receipt_id=payload["receipt_id"],
        payload=dict(payload),
        integrity_hash=payload["integrity_hash"],
        _minted_by_validator=True,
    )


def _mint_shadow(payload: dict[str, Any]) -> ValidatedShadow:
    return ValidatedShadow(payload=dict(payload), content_hash=payload["content_hash"])


def _mint_confidence(payload: dict[str, Any]) -> ValidatedConfidence:
    return ValidatedConfidence(payload=dict(payload), content_hash=payload["content_hash"])


def _mint_candidate(payload: dict[str, Any]) -> ValidatedCandidate:
    return ValidatedCandidate(payload=dict(payload), content_hash=payload["content_hash"])
