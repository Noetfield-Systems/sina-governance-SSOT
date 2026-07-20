"""Persist event_id → content_hash; detect duplicates vs identity collisions."""
from __future__ import annotations

import json
from pathlib import Path

from .errors import GovernanceBlock, SchemaError
from .hashutil import canonical_json


class EventRegistry:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write({"schema": "nf_motor_learning_event_registry_v1", "events": {}})

    def _write(self, data: dict) -> None:
        self.path.write_text(canonical_json(data) + "\n")

    def _read(self) -> dict:
        return json.loads(self.path.read_text())

    def register(self, event_id: str, content_hash: str) -> str:
        """
        Returns: 'accepted' | 'duplicate'
        Raises GovernanceBlock on identity collision (same id, different hash).
        """
        if not event_id or not content_hash:
            raise SchemaError("event_id and content_hash required")
        data = self._read()
        events = data.setdefault("events", {})
        prev = events.get(event_id)
        if prev is None:
            events[event_id] = content_hash
            self._write(data)
            return "accepted"
        if prev == content_hash:
            return "duplicate"
        raise GovernanceBlock(
            f"event identity collision: event_id={event_id} prior_hash={prev} new_hash={content_hash}"
        )
