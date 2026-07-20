"""File-backed prior repository with governance-gated terminal persistence."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .errors import GovernanceBlock, SchemaError
from .hashutil import canonical_json, content_hash

VALID_STATUS = frozenset({
    "active", "shadow", "rejected", "expired", "superseded", "rolled_back", "proposed", "observed"
})
TERMINAL_STATUS = frozenset({"active", "rejected", "rolled_back"})
SEEDABLE_STATUS = frozenset({"shadow", "proposed", "observed", "expired", "superseded"})


def store_tree_hash(root: Path) -> str:
    """Deterministic hash of entire store tree (paths + contents)."""
    root = Path(root)
    parts = []
    if not root.exists():
        return content_hash({"empty": True, "root": str(root)})
    for p in sorted(root.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(root))
            parts.append({"path": rel, "bytes": p.read_bytes().hex()})
    return content_hash(parts)


class PriorStore:
    def __init__(self, root: Path, *, create=True):
        self.root = Path(root)
        self.index_path = self.root / "index.json"
        self.versions_dir = self.root / "versions"
        self._create = create
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
            self.versions_dir.mkdir(parents=True, exist_ok=True)
            if not self.index_path.exists():
                self._write_index({"schema": "nf_motor_learning_prior_index_v1", "priors": {}})

    def _write_index(self, idx: dict) -> None:
        self.index_path.write_text(canonical_json(idx) + "\n")

    def _read_index(self) -> dict:
        if not self.index_path.exists():
            return {"schema": "nf_motor_learning_prior_index_v1", "priors": {}}
        return json.loads(self.index_path.read_text())

    def _prior_path(self, prior_id: str) -> Path:
        safe = prior_id.replace("/", "_")
        return self.root / f"{safe}.json"

    def _version_path(self, prior_id: str, version: int) -> Path:
        safe = prior_id.replace("/", "_")
        return self.versions_dir / f"{safe}.v{version}.json"

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

    def seed_fixture(self, prior: dict[str, Any], *, allow_duplicate: bool = False) -> dict:
        """
        Restricted seeding API for fixtures/migrations only.
        Seeded objects are tagged fixture_seeded=True and live_consumable=False.
        Terminal statuses (active/rejected/rolled_back) are allowed ONLY as non-consumable seeds
        for rollback/lineage fixtures — never live-consumable.
        """
        body = dict(prior)
        body["fixture_seeded"] = True
        body["live_consumable"] = False
        body.setdefault("schema", "nf_motor_learning_prior_v1")
        if body.get("status") not in VALID_STATUS:
            raise SchemaError(f"invalid status: {body.get('status')}")
        return self._persist(body, allow_duplicate=allow_duplicate, expected_version=None, governed=False)

    def create(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool = False,
        expected_version: int | None = None,
        ecqr_decision: dict | None = None,
        learning_receipt: dict | None = None,
    ) -> dict:
        """
        Public create. Terminal statuses require validated ECQR + receipt + transition history.
        """
        return self._persist(
            prior,
            allow_duplicate=allow_duplicate,
            expected_version=expected_version,
            governed=True,
            ecqr_decision=ecqr_decision,
            learning_receipt=learning_receipt,
        )

    def update(
        self,
        prior: dict[str, Any],
        *,
        expected_version: int | None = None,
        ecqr_decision: dict | None = None,
        learning_receipt: dict | None = None,
    ) -> dict:
        return self.create(
            prior,
            allow_duplicate=True,
            expected_version=expected_version,
            ecqr_decision=ecqr_decision,
            learning_receipt=learning_receipt,
        )

    def _assert_governance(self, body: dict, *, ecqr_decision: dict | None, learning_receipt: dict | None) -> None:
        status = body.get("status")
        if status not in TERMINAL_STATUS:
            return
        if body.get("fixture_seeded") and not body.get("live_consumable", True):
            # Should not reach here via governed path for seeds
            raise GovernanceBlock("fixture-seeded priors cannot be written via governed create/update")
        if not ecqr_decision:
            raise GovernanceBlock(f"status={status} requires validated ecqr_decision")
        if not learning_receipt:
            raise GovernanceBlock(f"status={status} requires validated learning_receipt")
        from .receipt import validate_learning_receipt
        from .ecqr import validate_ecqr_decision

        # Receipt already validated externally preferred; re-validate
        validate_learning_receipt(learning_receipt)
        # ECQR binding check without recomputing shadow (artifacts must already be bound in decision)
        if not ecqr_decision.get("_artifacts_bound"):
            raise GovernanceBlock("ecqr_decision must be produced by validate_ecqr_decision with bound artifacts")

        hist = body.get("transition_history") or []
        if not hist:
            raise GovernanceBlock("terminal prior requires transition_history")
        last = hist[-1]
        expected_state = {"active": "RATIFIED", "rejected": "REJECTED", "rolled_back": "ROLLED_BACK"}[status]
        if last.get("to_state") != expected_state:
            raise GovernanceBlock(f"transition_history last state {last.get('to_state')} != {expected_state}")
        rid = learning_receipt.get("receipt_id") or learning_receipt.get("learning_receipt_id")
        if last.get("learning_receipt_id") != rid:
            raise GovernanceBlock("transition learning_receipt_id mismatches receipt")
        if body.get("prior_id") != learning_receipt.get("prior_id"):
            raise GovernanceBlock("prior_id mismatches receipt.prior_id")
        if learning_receipt.get("candidate_id") and body.get("candidate_id"):
            if learning_receipt["candidate_id"] != body["candidate_id"]:
                raise GovernanceBlock("candidate_id mismatches receipt")
        if ecqr_decision.get("candidate_id") and body.get("candidate_id"):
            if ecqr_decision["candidate_id"] != body["candidate_id"]:
                raise GovernanceBlock("candidate_id mismatches ecqr_decision")

    def _ensure_writable(self) -> None:
        if not self._create and not self.root.exists():
            raise GovernanceBlock("prior store is read-only / missing")
        self.root.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._write_index({"schema": "nf_motor_learning_prior_index_v1", "priors": {}})

    def _persist(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool,
        expected_version: int | None,
        governed: bool,
        ecqr_decision: dict | None = None,
        learning_receipt: dict | None = None,
    ) -> dict:
        self._ensure_writable()
        required = ("prior_id", "status", "action_attempted", "recommended_action", "scope")
        missing = [k for k in required if k not in prior]
        if missing:
            raise SchemaError(f"prior missing fields: {missing}")
        if prior["status"] not in VALID_STATUS:
            raise SchemaError(f"invalid status: {prior['status']}")

        body = dict(prior)
        pid = body["prior_id"]
        existing = self.get(pid)

        if governed and body["status"] in TERMINAL_STATUS:
            self._assert_governance(body, ecqr_decision=ecqr_decision, learning_receipt=learning_receipt)
            body["live_consumable"] = True
            body["fixture_seeded"] = False
        elif governed and body.get("fixture_seeded"):
            raise GovernanceBlock("cannot promote fixture_seeded via governed create without clearing tag through rollback/ratify path")

        if existing and not allow_duplicate:
            raise SchemaError(f"duplicate prior_id: {pid}")

        # CAS / versioning
        if existing:
            cur_ver = int(existing.get("version") or 1)
            if expected_version is not None and expected_version != cur_ver:
                raise GovernanceBlock(
                    f"CAS failure: expected_version={expected_version} current={cur_ver}"
                )
            # preserve immutable previous version
            self._version_path(pid, cur_ver).write_text(canonical_json(existing) + "\n")
            body["version"] = cur_ver + 1
        else:
            if expected_version not in (None, 0, 1):
                raise GovernanceBlock(f"CAS failure: new prior expected_version={expected_version}")
            body["version"] = int(body.get("version") or 1)

        body.setdefault("schema", "nf_motor_learning_prior_v1")
        body.setdefault("supersedes", None)
        body.setdefault("superseded_by", None)
        body.setdefault("expires_at", None)
        body.setdefault("fixture_seeded", False)
        body.setdefault("live_consumable", body["status"] in TERMINAL_STATUS and not body.get("fixture_seeded"))
        # strip content_hash then recompute
        body.pop("content_hash", None)
        body["content_hash"] = content_hash({k: body[k] for k in sorted(body)})

        path = self._prior_path(pid)
        path.write_text(canonical_json(body) + "\n")
        idx = self._read_index()
        idx["priors"][pid] = {
            "status": body["status"],
            "path": path.name,
            "content_hash": body["content_hash"],
            "version": body["version"],
            "live_consumable": body.get("live_consumable", False),
            "fixture_seeded": body.get("fixture_seeded", False),
        }
        self._write_index(idx)
        return body


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
        live_consumable_only: bool = False,
    ) -> list[dict]:
        want = None
        if status is not None:
            want = {status} if isinstance(status, str) else set(status)
        results = []
        for prior in self.list():
            st = prior.get("status")
            exp = prior.get("expires_at")
            effective = st
            if as_of and exp and st == "active" and exp <= as_of:
                effective = "expired"

            if live_consumable_only:
                if not prior.get("live_consumable") or prior.get("fixture_seeded"):
                    continue

            if want is not None:
                # Match against effective status for active/expired semantics
                if effective not in want and st not in want:
                    continue
                if "active" in want and effective != "active" and "expired" not in want:
                    # time-expired active must not appear as active
                    if st == "active" and effective == "expired":
                        continue
            else:
                if not include_expired and effective == "expired":
                    continue

            if not include_expired and want is not None and "expired" not in want:
                if effective == "expired":
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
            annotated = dict(prior)
            annotated["effective_status"] = effective
            results.append(annotated)
        return results
