"""File-backed W1 reference prior repository — never mints live_consumable authority."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

from .errors import GovernanceBlock, SchemaError, MotorLearningError
from .hashutil import canonical_json, content_hash
from .validated import (
    ValidatedECQR,
    ValidatedReceipt,
    is_validated_ecqr,
    is_validated_receipt,
    is_w1_reference_store_capability,
    mint_w1_reference_store_capability,
)

VALID_STATUS = frozenset({
    "active", "shadow", "rejected", "expired", "superseded", "rolled_back", "proposed", "observed"
})
TERMINAL_STATUS = frozenset({"active", "rejected", "rolled_back"})
NON_CONSUMABLE_STATUS = frozenset({"rejected", "rolled_back", "expired", "superseded", "active", "shadow", "proposed", "observed"})
SEEDABLE_STATUS = frozenset({"shadow", "proposed", "observed", "expired", "superseded"})

# W1 never mints live consumption authority for any status
W1_LIVE_CONSUMABLE = False


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


def live_consumable_for_status(status: str, *, store_kind: str = "w1_reference") -> bool:
    """
    W1 reference stores: always False.
    W2 activation contract (not implemented here) is the only path to True.
    """
    if store_kind != "w1_reference":
        raise GovernanceBlock(f"unknown store_kind={store_kind}; W1 only supports w1_reference")
    # Explicit matrix — never TERMINAL_STATUS-based True
    if status in ("rejected", "rolled_back", "expired", "superseded", "active", "shadow", "proposed", "observed"):
        return False
    return False


class PriorStore:
    """
    W1 reference prior store.

    store_kind is always w1_reference. live_consumable is always False.
    Terminal persistence requires opaque ValidatedECQR + ValidatedReceipt.
    Caller-supplied _artifacts_bound markers are ignored/stripped and never trusted.
    """

    def __init__(
        self,
        root: Path,
        *,
        create: bool = True,
        store_kind: str = "w1_reference",
        store_capability=None,
        allow_persist: bool = False,
    ):
        if store_kind != "w1_reference":
            raise GovernanceBlock("W1 PriorStore only accepts store_kind=w1_reference")
        self.root = Path(root)
        self.store_kind = "w1_reference"
        self.index_path = self.root / "index.json"
        self.versions_dir = self.root / "versions"
        self.receipts_dir = self.root / "receipts"
        self._create = create
        self._allow_persist = allow_persist
        self._capability = store_capability
        if create:
            self.root.mkdir(parents=True, exist_ok=True)
            self.versions_dir.mkdir(parents=True, exist_ok=True)
            self.receipts_dir.mkdir(parents=True, exist_ok=True)
            if not self.index_path.exists():
                self._write_index({
                    "schema": "nf_motor_learning_prior_index_v1",
                    "store_kind": "w1_reference",
                    "live_consumable_authority": False,
                    "priors": {},
                })

    def require_persist_capability(self) -> None:
        if not self._allow_persist:
            raise GovernanceBlock(
                "W1 store persist requires allow_persist=True with validated w1_reference capability"
            )
        if not is_w1_reference_store_capability(self._capability):
            raise GovernanceBlock(
                "W1 store persist requires mint_w1_reference_store_capability(); "
                "CLI path blacklists are not the primary security mechanism"
            )

    def _write_index(self, idx: dict) -> None:
        self.index_path.write_text(canonical_json(idx) + "\n")

    def _read_index(self) -> dict:
        if not self.index_path.exists():
            return {"schema": "nf_motor_learning_prior_index_v1", "store_kind": "w1_reference", "priors": {}}
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

    def seed_fixture(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool = False,
        allow_terminal_seed: bool = False,
    ) -> dict:
        body = dict(prior)
        body["fixture_seeded"] = True
        body["live_consumable"] = False
        body["store_kind"] = "w1_reference"
        body.setdefault("schema", "nf_motor_learning_prior_v1")
        if body.get("status") not in VALID_STATUS:
            raise SchemaError(f"invalid status: {body.get('status')}")
        if body["status"] in TERMINAL_STATUS and not allow_terminal_seed:
            raise GovernanceBlock(
                f"seed_fixture status={body['status']} requires allow_terminal_seed=True "
                "(rollback/lineage fixtures only); never live-consumable"
            )
        return self._persist(body, allow_duplicate=allow_duplicate, expected_version=None, governed=False)

    def create(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool = False,
        expected_version: int | None = None,
        ecqr_decision: Any = None,
        learning_receipt: Any = None,
        candidate: dict | None = None,
        shadow: dict | None = None,
        confidence: dict | None = None,
    ) -> dict:
        self.require_persist_capability()
        return self._persist(
            prior,
            allow_duplicate=allow_duplicate,
            expected_version=expected_version,
            governed=True,
            ecqr_decision=ecqr_decision,
            learning_receipt=learning_receipt,
            candidate=candidate,
            shadow=shadow,
            confidence=confidence,
        )

    def update(
        self,
        prior: dict[str, Any],
        *,
        expected_version: int | None = None,
        ecqr_decision: Any = None,
        learning_receipt: Any = None,
        candidate: dict | None = None,
        shadow: dict | None = None,
        confidence: dict | None = None,
    ) -> dict:
        return self.create(
            prior,
            allow_duplicate=True,
            expected_version=expected_version,
            ecqr_decision=ecqr_decision,
            learning_receipt=learning_receipt,
            candidate=candidate,
            shadow=shadow,
            confidence=confidence,
        )

    def _revalidate_ecqr_binding(
        self,
        *,
        body: dict,
        ecqr: ValidatedECQR,
        receipt: ValidatedReceipt,
        candidate: dict | None,
        shadow: dict | None,
        confidence: dict | None,
    ) -> None:
        """Re-validate ECQR against concrete artifacts — never trust _artifacts_bound."""
        from .ecqr import validate_ecqr_decision
        from .receipt import validate_learning_receipt

        raw = {k: v for k, v in ecqr.as_dict().items() if not str(k).startswith("_artifacts")}

        validate_learning_receipt(receipt.as_dict())

        # Re-run full ECQR validation against concrete artifacts for terminal RATIFIED
        decision = raw.get("decision")
        if decision == "RATIFIED":
            if not (candidate and shadow and confidence):
                raise GovernanceBlock(
                    "terminal active prior requires candidate+shadow+confidence for ECQR re-validation"
                )
            # Re-validate from payload fields (immutable check)
            revalidated = validate_ecqr_decision(
                {k: v for k, v in raw.items() if not str(k).startswith("_")},
                confidence=confidence,
                shadow=shadow,
                candidate=candidate,
            )
            if revalidated.decision_hash != ecqr.decision_hash:
                raise GovernanceBlock("ECQR decision_hash changed under re-validation")
        elif decision in ("REJECTED", "ROLLED_BACK"):
            # Still require opaque type (already checked) and receipt cross-bind
            pass
        else:
            raise GovernanceBlock(f"unexpected ECQR decision for terminal persist: {decision}")

        # Cross-bind receipt
        r = receipt.as_dict()
        hist = body.get("transition_history") or []
        if not hist:
            raise GovernanceBlock("terminal prior requires transition_history")
        last = hist[-1]
        status = body.get("status")
        expected_state = {"active": "RATIFIED", "rejected": "REJECTED", "rolled_back": "ROLLED_BACK"}[status]
        if last.get("to_state") != expected_state:
            raise GovernanceBlock(f"transition_history last state {last.get('to_state')} != {expected_state}")
        if last.get("learning_receipt_id") != receipt.receipt_id:
            raise GovernanceBlock("transition learning_receipt_id mismatches receipt")
        if body.get("prior_id") != r.get("prior_id"):
            raise GovernanceBlock("prior_id mismatches receipt.prior_id")
        if r.get("candidate_id") and body.get("candidate_id") and r["candidate_id"] != body["candidate_id"]:
            raise GovernanceBlock("candidate_id mismatches receipt")
        if raw.get("candidate_id") and body.get("candidate_id") and raw["candidate_id"] != body["candidate_id"]:
            raise GovernanceBlock("candidate_id mismatches ecqr_decision")

        # Hash bindings for active
        if status == "active":
            for req in ("shadow_hash", "confidence_hash", "ecqr_decision_hash", "candidate_hash", "shadow_evidence_manifest_hash"):
                if not r.get(req):
                    raise GovernanceBlock(f"receipt missing {req} for active prior")

        # test/fixture reviewers cannot create activation authority (already live_consumable=False)
        reviewer = str(r.get("reviewer") or "")
        if reviewer.startswith(("test_reviewer:", "fixture:", "machine_policy:")):
            # Allowed for W1 reference records only — never activatable
            body["activation_authority"] = False
            body["activatable"] = False

    def _assert_governance(
        self,
        body: dict,
        *,
        ecqr_decision: Any,
        learning_receipt: Any,
        candidate: dict | None,
        shadow: dict | None,
        confidence: dict | None,
    ) -> None:
        status = body.get("status")
        if status not in TERMINAL_STATUS:
            return
        if body.get("fixture_seeded"):
            raise GovernanceBlock("fixture-seeded priors cannot be written via governed create/update")

        # Reject plain dict with forged marker
        if isinstance(ecqr_decision, dict):
            if ecqr_decision.get("_artifacts_bound"):
                raise GovernanceBlock(
                    "forged _artifacts_bound marker is not proof; require ValidatedECQR from validate_ecqr_decision"
                )
            raise GovernanceBlock(
                "ecqr_decision must be ValidatedECQR opaque type; plain dict is rejected"
            )
        if not is_validated_ecqr(ecqr_decision):
            raise GovernanceBlock("status terminal requires ValidatedECQR")
        if isinstance(learning_receipt, dict):
            from .receipt import validate_and_mint_receipt
            learning_receipt = validate_and_mint_receipt(learning_receipt)
        if not is_validated_receipt(learning_receipt):
            raise GovernanceBlock("status terminal requires ValidatedReceipt")

        self._revalidate_ecqr_binding(
            body=body,
            ecqr=ecqr_decision,
            receipt=learning_receipt,
            candidate=candidate,
            shadow=shadow,
            confidence=confidence,
        )

    def _ensure_writable(self) -> None:
        if not self._create and not self.root.exists():
            raise GovernanceBlock("prior store is read-only / missing")
        self.root.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        if not self.index_path.exists():
            self._write_index({
                "schema": "nf_motor_learning_prior_index_v1",
                "store_kind": "w1_reference",
                "live_consumable_authority": False,
                "priors": {},
            })

    def _persist(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool,
        expected_version: int | None,
        governed: bool,
        ecqr_decision: Any = None,
        learning_receipt: Any = None,
        candidate: dict | None = None,
        shadow: dict | None = None,
        confidence: dict | None = None,
    ) -> dict:
        self._ensure_writable()
        required = ("prior_id", "status", "action_attempted", "recommended_action", "scope")
        missing = [k for k in required if k not in prior]
        if missing:
            raise SchemaError(f"prior missing fields: {missing}")
        if prior["status"] not in VALID_STATUS:
            raise SchemaError(f"invalid status: {prior['status']}")

        body = dict(prior)
        # Strip caller trust markers
        body.pop("_artifacts_bound", None)
        pid = body["prior_id"]
        existing = self.get(pid)

        # W1: force live_consumable=False for ALL statuses — no TERMINAL_STATUS defaults
        body["live_consumable"] = live_consumable_for_status(body["status"], store_kind=self.store_kind)
        body["store_kind"] = "w1_reference"
        body["w2_activation_required"] = True
        body["activation_authority"] = False

        if governed and body["status"] in TERMINAL_STATUS:
            self._assert_governance(
                body,
                ecqr_decision=ecqr_decision,
                learning_receipt=learning_receipt,
                candidate=candidate,
                shadow=shadow,
                confidence=confidence,
            )
            body["fixture_seeded"] = False
            # Append-only receipt ledger
            if is_validated_receipt(learning_receipt):
                rpath = self.receipts_dir / f"{learning_receipt.receipt_id}.json"
                if rpath.exists():
                    existing_r = json.loads(rpath.read_text())
                    if existing_r != learning_receipt.as_dict():
                        raise GovernanceBlock("receipt ID collision with different body")
                else:
                    rpath.write_text(canonical_json(learning_receipt.as_dict()) + "\n")

        if existing and not allow_duplicate:
            raise SchemaError(f"duplicate prior_id: {pid}")

        if existing:
            cur_ver = int(existing.get("version") or 1)
            if expected_version is not None and expected_version != cur_ver:
                raise GovernanceBlock(
                    f"CAS failure: expected_version={expected_version} current={cur_ver}"
                )
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
        # Force again after setdefault
        body["live_consumable"] = False

        body.pop("content_hash", None)
        body["content_hash"] = content_hash({k: body[k] for k in sorted(body)})

        path = self._prior_path(pid)
        path.write_text(canonical_json(body) + "\n")
        idx = self._read_index()
        idx["store_kind"] = "w1_reference"
        idx["live_consumable_authority"] = False
        idx["priors"][pid] = {
            "status": body["status"],
            "path": path.name,
            "content_hash": body["content_hash"],
            "version": body["version"],
            "live_consumable": False,
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
                # W1: never returns anything — live_consumable always false
                if not prior.get("live_consumable") or prior.get("fixture_seeded"):
                    continue

            if want is not None:
                if effective not in want and st not in want:
                    continue
                if "active" in want and effective != "active" and "expired" not in want:
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


# W2 activation contract stub (not implemented — authority boundary documentation)
W2_ACTIVATION_CONTRACT = {
    "schema": "nf_motor_learning_w2_activation_contract_v1",
    "status": "NOT_IMPLEMENTED",
    "requires": [
        "complete_w1_reference_bundle",
        "w2_activation_receipt",
        "verified_ecqr_decision_hash",
        "verified_shadow_evidence_manifest_hash",
        "verified_learning_receipt",
        "founder_or_gated_policy_reviewer",
    ],
    "sets_live_consumable": True,
    "note": "Only W2 may set live_consumable=true after verifying the complete W1 bundle.",
}
