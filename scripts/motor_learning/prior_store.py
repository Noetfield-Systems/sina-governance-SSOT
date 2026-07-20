
"""File-backed prior repository (deterministic reference backend)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .errors import SchemaError
from .hashutil import canonical_json, content_hash

VALID_STATUS = frozenset({
    "active", "shadow", "rejected", "expired", "superseded", "rolled_back", "proposed", "observed"
})


class PriorStore:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "index.json"
        if not self.index_path.exists():
            self._write_index({"schema": "nf_motor_learning_prior_index_v1", "priors": {}})

    def _write_index(self, idx: dict) -> None:
        self.index_path.write_text(canonical_json(idx) + "\n")

    def _read_index(self) -> dict:
        return json.loads(self.index_path.read_text())

    def _prior_path(self, prior_id: str) -> Path:
        safe = prior_id.replace("/", "_")
        return self.root / f"{safe}.json"

    def get(self, prior_id: str) -> dict | None:
        p = self._prior_path(prior_id)
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def list(self) -> list[dict]:
        idx = self._read_index()
        out = []
        for pid in sorted(idx.get("priors", {})):
            prior = self.get(pid)
            if prior:
                out.append(prior)
        return out

    def create(self, prior: dict[str, Any], *, allow_duplicate: bool = False) -> dict:
        required = ("prior_id", "status", "action_attempted", "recommended_action", "scope")
        missing = [k for k in required if k not in prior]
        if missing:
            raise SchemaError(f"prior missing fields: {missing}")
        if prior["status"] not in VALID_STATUS:
            raise SchemaError(f"invalid status: {prior['status']}")
        pid = prior["prior_id"]
        existing = self.get(pid)
        if existing and not allow_duplicate:
            raise SchemaError(f"duplicate prior_id: {pid}")
        body = dict(prior)
        body.setdefault("schema", "nf_motor_learning_prior_v1")
        body.setdefault("version", 1)
        body.setdefault("supersedes", None)
        body.setdefault("superseded_by", None)
        body.setdefault("expires_at", None)
        body["content_hash"] = content_hash({k: body[k] for k in sorted(body) if k != "content_hash"})
        path = self._prior_path(pid)
        path.write_text(canonical_json(body) + "\n")
        idx = self._read_index()
        idx["priors"][pid] = {
            "status": body["status"],
            "path": path.name,
            "content_hash": body["content_hash"],
        }
        self._write_index(idx)
        return body

    def update(self, prior: dict[str, Any]) -> dict:
        return self.create(prior, allow_duplicate=True)

    def search(
        self,
        *,
        loop_id: str | None = None,
        runway: str | None = None,
        repository: str | None = None,
        action: str | None = None,
        status: str | Iterable[str] | None = None,
        include_expired: bool = False,
        as_of: str | None = None,
    ) -> list[dict]:
        statuses = None
        if status is not None:
            statuses = {status} if isinstance(status, str) else set(status)
        results = []
        for prior in self.list():
            st = prior.get("status")
            if statuses is not None and st not in statuses:
                continue
            if not include_expired and st == "expired":
                continue
            scope = prior.get("scope") or {}
            fp = prior.get("fingerprint") or {}
            if loop_id and scope.get("loop_id") not in (None, loop_id):
                continue
            if runway and scope.get("runway") not in (None, runway):
                continue
            if repository and scope.get("repository") not in (None, repository):
                continue
            if action:
                acts = {prior.get("action_attempted"), fp.get("action_attempted")}
                if action not in acts:
                    continue
            results.append(prior)
        return results
