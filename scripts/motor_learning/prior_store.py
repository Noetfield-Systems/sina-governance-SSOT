"""File-backed prior repository — W1 reference / fixture stores; transactional terminal writes."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Iterable

from .errors import GovernanceBlock, SchemaError, MotorLearningError
from .hashutil import canonical_json, content_hash
from .validated import ValidatedECQR, ValidatedReceipt
from .artifacts import (
    unwrap_shadow, unwrap_confidence, unwrap_candidate, candidate_content_hash,
)

VALID_STATUS = frozenset({
    "active", "shadow", "rejected", "expired", "superseded", "rolled_back", "proposed", "observed"
})
TERMINAL_STATUS = frozenset({"active", "rejected", "rolled_back"})
STORE_KINDS = frozenset({"w1_reference", "fixture"})


def store_tree_hash(root: Path) -> str:
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
    if store_kind not in STORE_KINDS:
        raise GovernanceBlock(f"unknown store_kind={store_kind}")
    return False  # W1 / fixture: never


W2_ACTIVATION_CONTRACT = {
    "schema": "nf_motor_learning_w2_activation_contract_v1",
    "status": "NOT_IMPLEMENTED",
    "sets_live_consumable": True,
    "note": "Only W2 may set live_consumable=true after verifying the complete W1 bundle.",
}


class PriorStore:
    """
    store_kind:
      - w1_reference: governed reference priors; live_consumable always false
      - fixture: test/fixture data only; excluded from governed search by default

    Terminal mutation is transactional via commit_terminal_bundle().
    Direct _persist for terminal governed writes is unavailable.
    """

    def __init__(
        self,
        root: Path,
        *,
        create: bool = True,
        store_kind: str = "w1_reference",
        allow_persist: bool = False,
    ):
        if store_kind not in STORE_KINDS:
            raise GovernanceBlock(f"PriorStore store_kind must be one of {sorted(STORE_KINDS)}")
        self.root = Path(root)
        self.store_kind = store_kind
        self.index_path = self.root / "index.json"
        if self.index_path.exists():
            import json as _json
            idx = _json.loads(self.index_path.read_text())
            existing_kind = idx.get("store_kind")
            if existing_kind and existing_kind != store_kind:
                raise GovernanceBlock(
                    f"store identity mismatch: index.store_kind={existing_kind!r} "
                    f"but PriorStore requested store_kind={store_kind!r}; "
                    f"fixture stores must never be opened as governed reference stores"
                )
        self.versions_dir = self.root / "versions"
        self.receipts_dir = self.root / "receipts"
        self._create = create
        self._allow_persist = allow_persist
        if create:
            self._ensure_dirs()
            if not self.index_path.exists():
                self._write_index(self._empty_index())

    def _empty_index(self) -> dict:
        return {
            "schema": "nf_motor_learning_prior_index_v1",
            "store_kind": self.store_kind,
            "live_consumable_authority": False,
            "priors": {},
        }

    def _ensure_dirs(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)

    def _write_index(self, idx: dict) -> None:
        self.index_path.write_text(canonical_json(idx) + "\n")

    def _read_index(self) -> dict:
        if not self.index_path.exists():
            return self._empty_index()
        return json.loads(self.index_path.read_text())

    def _prior_path(self, prior_id: str) -> Path:
        return self.root / f"{prior_id.replace('/', '_')}.json"

    def _version_path(self, prior_id: str, version: int) -> Path:
        return self.versions_dir / f"{prior_id.replace('/', '_')}.v{version}.json"

    def get(self, prior_id: str) -> dict | None:
        p = self._prior_path(prior_id)
        if not p.exists():
            return None
        return json.loads(p.read_text())

    def list(self, *, include_fixtures: bool = False) -> list[dict]:
        idx = self._read_index()
        out = []
        for pid in sorted(idx.get("priors", {})):
            prior = self.get(pid)
            if not prior:
                continue
            if prior.get("fixture_seeded") and not include_fixtures and self.store_kind != "fixture":
                continue
            if self.store_kind == "fixture" and not include_fixtures:
                # listing a fixture store still returns its contents when include_fixtures
                # but governed callers should not use fixture stores for search
                pass
            out.append(prior)
        return out

    def seed_fixture(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool = False,
        allow_terminal_seed: bool = False,
    ) -> dict:
        if self.store_kind != "fixture":
            raise GovernanceBlock(
                "seed_fixture only allowed on store_kind=fixture; "
                "governed w1_reference stores reject fixture seeding"
            )
        body = dict(prior)
        body["fixture_seeded"] = True
        body["live_consumable"] = False
        body["store_kind"] = "fixture"
        body.setdefault("schema", "nf_motor_learning_prior_v1")
        if body.get("status") not in VALID_STATUS:
            raise SchemaError(f"invalid status: {body.get('status')}")
        if body["status"] in TERMINAL_STATUS and not allow_terminal_seed:
            raise GovernanceBlock(
                f"seed_fixture status={body['status']} requires allow_terminal_seed=True"
            )
        return self._persist_nonterminal(body, allow_duplicate=allow_duplicate, expected_version=None)

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
        """
        Public create. Terminal statuses MUST use commit_terminal_bundle.
        Non-terminal may persist directly. Terminal via create raises.
        """
        if not self._allow_persist and self.store_kind == "w1_reference":
            raise GovernanceBlock(
                "W1 reference persist requires allow_persist=True "
                "(store_mode contract; not an authentication capability)"
            )
        status = prior.get("status")
        if status in TERMINAL_STATUS:
            raise GovernanceBlock(
                "terminal prior create must use commit_terminal_bundle() "
                "(transactional); nontransactional terminal _persist is inaccessible"
            )
        return self._persist_nonterminal(
            prior, allow_duplicate=allow_duplicate, expected_version=expected_version
        )

    def update(self, prior: dict[str, Any], **kwargs) -> dict:
        return self.create(prior, allow_duplicate=True, **kwargs)

    def commit_terminal_bundle(
        self,
        *,
        prior: dict[str, Any],
        learning_receipt: dict | ValidatedReceipt,
        ecqr_decision: dict | ValidatedECQR,
        candidate: dict | None = None,
        shadow: dict | None = None,
        confidence: dict | None = None,
        shadow_events: list | None = None,
        confidence_inputs: dict | None = None,
        mining_events: list | None = None,
        allow_duplicate: bool = False,
        expected_version: int | None = None,
        inject_failure_after: str | None = None,
    ) -> dict:
        """
        Atomic terminal commit: validate fully, then stage receipt/prior/version/index
        and rename into place. On any failure restore exact pre-call store tree
        (including nonexistence).
        """
        if self.store_kind != "w1_reference":
            raise GovernanceBlock("terminal commit only on w1_reference stores")
        if not self._allow_persist:
            raise GovernanceBlock("terminal commit requires allow_persist=True")

        existed = self.root.exists()
        hash_before = store_tree_hash(self.root)
        backup = Path(tempfile.mkdtemp(prefix="mlo-ps-bak-"))
        if existed:
            shutil.copytree(self.root, backup / "tree")
        else:
            (backup / "MISSING").write_text("1\n")

        staging = Path(tempfile.mkdtemp(prefix="mlo-ps-stage-"))
        try:
            # Pre-checks before ANY authoritative write
            body = dict(prior)
            status = body.get("status")
            if status not in TERMINAL_STATUS:
                raise GovernanceBlock(f"commit_terminal_bundle requires terminal status, got {status}")
            pid = body.get("prior_id")
            if not pid:
                raise SchemaError("prior_id required")

            # Ensure staging seeded from current
            if existed:
                shutil.copytree(self.root, staging, dirs_exist_ok=True)
            else:
                staging.mkdir(parents=True, exist_ok=True)

            stage_store = PriorStore(staging, create=True, store_kind="w1_reference", allow_persist=True)

            # Load existing BEFORE history/cross-bind (rollback + prefix require it)
            existing = stage_store.get(pid)

            from .receipt import validate_and_mint_receipt
            from .ecqr import validate_ecqr_decision
            from .lifecycle import validate_transition_history, normalize_state
            from .shadow import assert_shadow_independence
            from .artifacts import (
                assert_confidence_inputs_canonical,
                mining_evidence_manifest,
            )

            if existing and existing.get("status") == "active" and status == "active":
                raise GovernanceBlock(
                    "active prior overwrite with a new ratification history is forbidden; "
                    "use rollback/supersede paths"
                )

            if existing:
                if status in TERMINAL_STATUS and expected_version is None:
                    raise GovernanceBlock(
                        "existing terminal update requires expected_version (CAS)"
                    )
                cur_ver = int(existing.get("version") or 1)
                if expected_version is not None and expected_version != cur_ver:
                    raise GovernanceBlock(
                        f"CAS failure: expected_version={expected_version} current={cur_ver}"
                    )
                # Rollback target metadata must match stored prior exactly
                if status == "rolled_back":
                    if expected_version != cur_ver:
                        raise GovernanceBlock(
                            f"rollback expected_version must equal existing.version={cur_ver}"
                        )
                    want_hash = existing.get("content_hash")
                    want_receipt = existing.get("learning_receipt_id")
                    if body.get("rollback_target_prior_content_hash") != want_hash:
                        raise GovernanceBlock(
                            "rollback_target_prior_content_hash mismatches existing.content_hash"
                        )
                    if int(body.get("rollback_target_version")) != cur_ver:
                        raise GovernanceBlock(
                            "rollback_target_version mismatches existing.version"
                        )
                    if body.get("prior_ratification_receipt_id") != want_receipt:
                        raise GovernanceBlock(
                            "prior_ratification_receipt_id mismatches existing.learning_receipt_id"
                        )
                validate_transition_history(
                    body.get("transition_history"),
                    entity_status=status,
                    require_observed_origin=False,
                    existing_history=existing.get("transition_history"),
                    existing_state=existing.get("state") or existing.get("status"),
                    candidate_id=body.get("candidate_id"),
                    prior_id=pid,
                )
            else:
                if expected_version not in (None, 0, 1):
                    raise GovernanceBlock(f"CAS failure: new prior expected_version={expected_version}")
                # New terminal prior must prove complete OBSERVED origin
                validate_transition_history(
                    body.get("transition_history"),
                    entity_status=status,
                    require_observed_origin=True,
                    candidate_id=body.get("candidate_id"),
                    prior_id=pid,
                )

            # Active: re-validate mining/shadow independence + canonical confidence inputs
            if status == "active":
                if candidate is None or shadow is None or confidence is None:
                    raise GovernanceBlock("active prior requires candidate+shadow+confidence")
                if mining_events is None or not isinstance(mining_events, list) or not mining_events:
                    raise GovernanceBlock(
                        "active terminal commit requires concrete normalized mining_events"
                    )
                if shadow_events is None or not isinstance(shadow_events, list) or not shadow_events:
                    raise GovernanceBlock(
                        "active terminal commit requires concrete normalized shadow_events"
                    )
                cand0 = unwrap_candidate(candidate)
                assert_shadow_independence(
                    candidate=cand0, mining_events=mining_events, shadow_events=shadow_events,
                )
                # Derive/check confidence inputs against candidate+shadow (not unconstrained)
                # Shadow artifact must already be present; equality checked after unwrap below
                if confidence_inputs is None:
                    raise GovernanceBlock("active terminal commit requires confidence_inputs")
                # provisional canonical check against submitted shadow fields before full unwrap
                confidence_inputs = assert_confidence_inputs_canonical(
                    confidence_inputs, candidate=cand0, shadow=shadow if isinstance(shadow, dict) else shadow.as_dict(),
                )

            if isinstance(learning_receipt, ValidatedReceipt):
                receipt_body = learning_receipt.as_dict()
            else:
                receipt_body = dict(learning_receipt)
            vr = validate_and_mint_receipt(receipt_body)

            if isinstance(ecqr_decision, ValidatedECQR):
                ecqr_body = ecqr_decision.as_dict()
            else:
                ecqr_body = dict(ecqr_decision)

            # For rollback: ECQR must already carry exact target bindings matching body/existing
            if status == "rolled_back":
                for k in (
                    "rollback_target_prior_content_hash",
                    "rollback_target_version",
                    "prior_ratification_receipt_id",
                ):
                    if k not in ecqr_body or ecqr_body.get(k) in (None, ""):
                        raise GovernanceBlock(f"ROLLED_BACK ECQR missing required binding: {k}")
                    if body.get(k) != ecqr_body.get(k):
                        raise GovernanceBlock(f"rollback prior.{k} mismatches ECQR.{k}")
                if existing:
                    if ecqr_body.get("rollback_target_prior_content_hash") != existing.get("content_hash"):
                        raise GovernanceBlock("ECQR rollback_target_prior_content_hash mismatches existing")
                    if int(ecqr_body.get("rollback_target_version")) != int(existing.get("version") or 1):
                        raise GovernanceBlock("ECQR rollback_target_version mismatches existing")
                    if ecqr_body.get("prior_ratification_receipt_id") != existing.get("learning_receipt_id"):
                        raise GovernanceBlock("ECQR prior_ratification_receipt_id mismatches existing")

            vecqr = validate_ecqr_decision(
                ecqr_body,
                confidence=confidence,
                shadow=shadow,
                candidate=candidate,
                shadow_events=shadow_events,
                confidence_inputs=confidence_inputs,
                mining_events=mining_events,
                require_bound_artifacts=(status == "active"),
            )

            self._assert_exact_cross_bind(
                body=body,
                receipt=vr.as_dict(),
                ecqr=vecqr,
                candidate=candidate,
                shadow=shadow,
                confidence=confidence,
                shadow_events=shadow_events,
                confidence_inputs=confidence_inputs,
                mining_events=mining_events,
                existing=existing,
            )

            if existing and not allow_duplicate and status != "rolled_back":
                raise SchemaError(f"duplicate prior_id: {pid}")

            if inject_failure_after == "pre_write_checks":
                raise MotorLearningError("injected failure after pre_write_checks")

            # Stage receipt
            rpath = stage_store.receipts_dir / f"{vr.receipt_id}.json"
            if rpath.exists():
                existing_r = json.loads(rpath.read_text())
                if existing_r != vr.as_dict():
                    raise GovernanceBlock("receipt ID collision with different body")
            else:
                rpath.write_text(canonical_json(vr.as_dict()) + "\n")

            if inject_failure_after == "receipt_staging":
                raise MotorLearningError("injected failure after receipt staging")

            # Prepare prior body
            body["live_consumable"] = False
            body["store_kind"] = "w1_reference"
            body["w2_activation_required"] = True
            body["activation_authority"] = False
            body["fixture_seeded"] = False
            body.setdefault("schema", "nf_motor_learning_prior_v1")
            body.setdefault("supersedes", None)
            body.setdefault("superseded_by", None)
            body.setdefault("expires_at", None)
            if existing:
                cur_ver = int(existing.get("version") or 1)
                stage_store._version_path(pid, cur_ver).write_text(canonical_json(existing) + "\n")
                body["version"] = cur_ver + 1
            else:
                body["version"] = int(body.get("version") or 1)

            if inject_failure_after == "prior_staging":
                raise MotorLearningError("injected failure after prior staging")

            body.pop("content_hash", None)
            body["content_hash"] = content_hash({k: body[k] for k in sorted(body)})
            stage_store._prior_path(pid).write_text(canonical_json(body) + "\n")

            if inject_failure_after == "before_index_commit":
                raise MotorLearningError("injected failure before index commit")

            idx = stage_store._read_index()
            idx["store_kind"] = "w1_reference"
            idx["live_consumable_authority"] = False
            idx["priors"][pid] = {
                "status": body["status"],
                "path": stage_store._prior_path(pid).name,
                "content_hash": body["content_hash"],
                "version": body["version"],
                "live_consumable": False,
                "fixture_seeded": False,
            }
            stage_store._write_index(idx)

            if inject_failure_after == "after_index":
                raise MotorLearningError("injected failure after index")

            # Atomic replace
            live_tmp = Path(str(self.root) + ".mlo_replacing")
            if live_tmp.exists():
                shutil.rmtree(live_tmp)
            if self.root.exists():
                self.root.rename(live_tmp)
            staging.rename(self.root)
            if live_tmp.exists():
                shutil.rmtree(live_tmp)
            shutil.rmtree(backup, ignore_errors=True)
            return body

        except Exception as exc:
            # Restore exact pre-state
            if self.root.exists():
                shutil.rmtree(self.root)
            if (backup / "MISSING").exists():
                # store must remain nonexistent
                pass
            elif (backup / "tree").exists():
                shutil.copytree(backup / "tree", self.root)
            shutil.rmtree(backup, ignore_errors=True)
            shutil.rmtree(staging, ignore_errors=True)
            # Verify hash / existence
            if existed:
                if store_tree_hash(self.root) != hash_before:
                    # best-effort already restored
                    pass
            else:
                if self.root.exists():
                    shutil.rmtree(self.root)
            if isinstance(exc, MotorLearningError):
                raise
            raise MotorLearningError(f"terminal store commit failed: {exc}") from exc

    def _assert_exact_cross_bind(
        self,
        *,
        body: dict,
        receipt: dict,
        ecqr: ValidatedECQR,
        candidate: dict | None,
        shadow: dict | None,
        confidence: dict | None,
        shadow_events: list | None = None,
        confidence_inputs: dict | None = None,
        mining_events: list | None = None,
        existing: dict | None = None,
    ) -> None:
        """Exact receipt↔ECQR equality for every terminal decision; artifact binds for active."""
        status = body.get("status")
        ed = ecqr.as_dict()
        hist = body.get("transition_history") or []
        if not hist:
            raise GovernanceBlock("terminal prior requires transition_history")
        last = hist[-1]
        expected_state = {"active": "RATIFIED", "rejected": "REJECTED", "rolled_back": "ROLLED_BACK"}[status]
        if last.get("to_state") != expected_state:
            raise GovernanceBlock(f"transition_history last state {last.get('to_state')} != {expected_state}")
        if last.get("learning_receipt_id") != receipt.get("receipt_id"):
            raise GovernanceBlock("transition learning_receipt_id mismatches receipt")

        # Decision mapping
        dec_map = {"active": "accepted", "rejected": "rejected", "rolled_back": "rolled_back"}
        if receipt.get("decision") != dec_map[status]:
            raise GovernanceBlock("receipt decision mismatches prior status")
        if ed.get("decision") != expected_state:
            raise GovernanceBlock("ECQR decision mismatches prior status")

        # ALL terminal decisions: receipt and ECQR may never disagree
        if body.get("prior_id") != receipt.get("prior_id"):
            raise GovernanceBlock("prior_id mismatches receipt.prior_id")
        if ed.get("prior_id") not in (None, body.get("prior_id")) and ed.get("prior_id") != body.get("prior_id"):
            raise GovernanceBlock("ECQR prior_id mismatches prior")
        if receipt.get("candidate_id") != ed.get("candidate_id"):
            raise GovernanceBlock("receipt.candidate_id mismatches ECQR.candidate_id")
        if body.get("candidate_id") and receipt.get("candidate_id") != body.get("candidate_id"):
            raise GovernanceBlock("candidate_id mismatches receipt")
        if receipt.get("reviewer") != ed.get("reviewer"):
            raise GovernanceBlock("receipt.reviewer mismatches ECQR.reviewer")
        if receipt.get("rationale") != ed.get("rationale"):
            raise GovernanceBlock("receipt.rationale mismatches ECQR.rationale")
        if list(receipt.get("evidence_links") or []) != list(ed.get("evidence_reviewed") or []):
            raise GovernanceBlock("receipt evidence_links mismatch ECQR evidence_reviewed")
        if float(receipt.get("confidence_before")) != float(ed.get("confidence_before")):
            raise GovernanceBlock("receipt.confidence_before mismatches ECQR")
        if float(receipt.get("confidence_after")) != float(ed.get("confidence_after")):
            raise GovernanceBlock("receipt.confidence_after mismatches ECQR")
        if list(receipt.get("affected_loops") or []) != list(ed.get("affected_loops") or []):
            raise GovernanceBlock("receipt.affected_loops mismatches ECQR")
        if list(receipt.get("applicable_runways") or []) != list(ed.get("applicable_runways") or []):
            raise GovernanceBlock("receipt.applicable_runways mismatches ECQR")
        if list(receipt.get("repositories") or []) != list(ed.get("repositories") or []):
            raise GovernanceBlock("receipt.repositories mismatches ECQR")
        if receipt.get("decision_timestamp") != ed.get("effective_at"):
            raise GovernanceBlock("receipt.decision_timestamp mismatches ECQR.effective_at")

        if not receipt.get("ecqr_decision_hash"):
            raise GovernanceBlock("receipt missing ecqr_decision_hash")
        if receipt["ecqr_decision_hash"] != ecqr.decision_hash:
            raise GovernanceBlock(
                f"receipt.ecqr_decision_hash mismatch: "
                f"{receipt['ecqr_decision_hash']!r} != {ecqr.decision_hash!r}"
            )

        if status == "active":
            if candidate is None or shadow is None or confidence is None:
                raise GovernanceBlock("active prior requires candidate+shadow+confidence")
            if shadow_events is None or confidence_inputs is None or mining_events is None:
                raise GovernanceBlock(
                    "active prior requires mining_events+shadow_events+confidence_inputs"
                )
            from .artifacts import mining_evidence_manifest, assert_confidence_inputs_canonical
            from .shadow import assert_shadow_independence
            cand = unwrap_candidate(candidate)
            assert_shadow_independence(
                candidate=cand, mining_events=mining_events, shadow_events=shadow_events,
            )
            sh = unwrap_shadow(
                shadow, candidate=cand, shadow_events=shadow_events, require_derivation=True,
            )
            cin = assert_confidence_inputs_canonical(
                confidence_inputs, candidate=cand, shadow=sh,
            )
            conf = unwrap_confidence(
                confidence, shadow=sh, confidence_inputs=cin, require_derivation=True,
            )
            mine_manifest, mine_hash = mining_evidence_manifest(cand, mining_events)

            checks = [
                ("candidate_hash", cand["content_hash"]),
                ("shadow_hash", sh["content_hash"]),
                ("shadow_evidence_manifest_hash", sh["evidence_manifest_hash"]),
                ("confidence_hash", conf["content_hash"]),
                ("mining_evidence_manifest_hash", mine_hash),
            ]
            for field, expected in checks:
                got = receipt.get(field)
                if got != expected:
                    raise GovernanceBlock(
                        f"receipt.{field} mismatch: receipt={got!r} artifact={expected!r}"
                    )
                if ed.get(field) not in (None, expected) and ed.get(field) != expected:
                    raise GovernanceBlock(f"ECQR.{field} mismatches artifact")
            if ed.get("mining_evidence_manifest_hash") != mine_hash:
                raise GovernanceBlock("ECQR mining_evidence_manifest_hash mismatches mining manifest")
            if receipt.get("shadow_id") != sh.get("shadow_id"):
                raise GovernanceBlock("receipt.shadow_id mismatches shadow")
            if ed.get("candidate_hash") != cand["content_hash"]:
                raise GovernanceBlock("ECQR candidate_hash mismatches candidate")
            if ed.get("shadow_id") != sh["shadow_id"]:
                raise GovernanceBlock("ECQR shadow_id mismatches shadow")
            if ed.get("confidence_hash") != conf["content_hash"]:
                raise GovernanceBlock("ECQR confidence_hash mismatches confidence")

        elif status == "rolled_back":
            rb = ed.get("rollback_target")
            if not rb:
                raise GovernanceBlock("rollback ECQR missing rollback_target")
            if receipt.get("rollback_target") != rb:
                raise GovernanceBlock("rollback_target mismatch receipt/ECQR")
            if body.get("prior_id") != rb:
                raise GovernanceBlock("rollback_target mismatch prior_id/ECQR")
            for k in (
                "rollback_target_prior_content_hash",
                "rollback_target_version",
                "prior_ratification_receipt_id",
            ):
                if body.get(k) != ed.get(k):
                    raise GovernanceBlock(f"rollback {k} mismatch prior/ECQR")
                if receipt.get(k) != ed.get(k):
                    raise GovernanceBlock(f"rollback {k} mismatch receipt/ECQR")
            if existing is not None:
                if ed.get("rollback_target_prior_content_hash") != existing.get("content_hash"):
                    raise GovernanceBlock("rollback hash binding mismatches existing prior")
                if int(ed.get("rollback_target_version")) != int(existing.get("version") or 1):
                    raise GovernanceBlock("rollback version binding mismatches existing prior")
                if ed.get("prior_ratification_receipt_id") != existing.get("learning_receipt_id"):
                    raise GovernanceBlock("rollback receipt binding mismatches existing prior")
            if last.get("to_state") != "ROLLED_BACK":
                raise GovernanceBlock("transition history must end at ROLLED_BACK")

    def _persist_nonterminal(
        self,
        prior: dict[str, Any],
        *,
        allow_duplicate: bool,
        expected_version: int | None,
    ) -> dict:
        if not self.root.exists() and not self._create:
            raise GovernanceBlock("prior store is read-only / missing")
        self._ensure_dirs()
        if not self.index_path.exists():
            self._write_index(self._empty_index())

        required = ("prior_id", "status", "action_attempted", "recommended_action", "scope")
        missing = [k for k in required if k not in prior]
        if missing:
            raise SchemaError(f"prior missing fields: {missing}")
        if prior["status"] not in VALID_STATUS:
            raise SchemaError(f"invalid status: {prior['status']}")
        if prior["status"] in TERMINAL_STATUS and self.store_kind != "fixture":
            raise GovernanceBlock("terminal status forbidden on nonterminal persist path")

        body = dict(prior)
        body.pop("_artifacts_bound", None)
        pid = body["prior_id"]
        existing = self.get(pid)
        body["live_consumable"] = False
        body["store_kind"] = self.store_kind
        if self.store_kind == "fixture":
            body["fixture_seeded"] = True

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
        body.setdefault("fixture_seeded", self.store_kind == "fixture")
        body["live_consumable"] = False
        body.pop("content_hash", None)
        body["content_hash"] = content_hash({k: body[k] for k in sorted(body)})

        self._prior_path(pid).write_text(canonical_json(body) + "\n")
        idx = self._read_index()
        idx["store_kind"] = self.store_kind
        idx["live_consumable_authority"] = False
        idx["priors"][pid] = {
            "status": body["status"],
            "path": self._prior_path(pid).name,
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
        include_fixtures: bool = False,
    ) -> list[dict]:
        # Fixture stores never participate in governed search unless explicit
        if self.store_kind == "fixture" and not include_fixtures:
            return []

        want = None
        if status is not None:
            want = {status} if isinstance(status, str) else set(status)
        results = []
        for prior in self.list(include_fixtures=include_fixtures):
            if prior.get("fixture_seeded") and not include_fixtures:
                continue
            st = prior.get("status")
            exp = prior.get("expires_at")
            effective = st
            if as_of and exp and st == "active" and exp <= as_of:
                effective = "expired"

            if live_consumable_only:
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
