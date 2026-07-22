"""Durable event identity ledger — shared across runs for persistence-capable ops."""
from __future__ import annotations

import json
from pathlib import Path

from .errors import GovernanceBlock, SchemaError
from .hashutil import canonical_json


class EventRegistry:
    """
    Persist event_id → content_hash / provenance fingerprint.
    Same id + different hash = identity collision (not a duplicate).
    For persistence-capable operations, use a durable ledger path shared across runs
    (typically store_dir/event_identity_ledger.json), not an out_dir-local registry alone.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {}})

    def _write(self, data: dict) -> None:
        self.path.write_text(canonical_json(data) + "\n")

    def _read(self) -> dict:
        return json.loads(self.path.read_text())

    def register(self, event_id: str, content_hash: str, *, provenance: str | None = None) -> str:
        """
        Returns: 'accepted' | 'duplicate'
        Raises GovernanceBlock on identity collision (same id, different hash/provenance).
        """
        if not event_id or not content_hash:
            raise SchemaError("event_id and content_hash required")
        data = self._read()
        events = data.setdefault("events", {})
        prev = events.get(event_id)
        fingerprint = provenance or content_hash
        if prev is None:
            events[event_id] = {"content_hash": content_hash, "provenance_fingerprint": fingerprint}
            self._write(data)
            return "accepted"
        prev_hash = prev if isinstance(prev, str) else prev.get("content_hash")
        prev_prov = prev if isinstance(prev, str) else prev.get("provenance_fingerprint", prev_hash)
        if prev_hash == content_hash and prev_prov == fingerprint:
            return "duplicate"
        raise GovernanceBlock(
            f"event identity collision: event_id={event_id} "
            f"prior_hash={prev_hash} new_hash={content_hash} "
            f"prior_provenance={prev_prov} new_provenance={fingerprint}"
        )
