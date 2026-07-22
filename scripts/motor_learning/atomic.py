"""Atomic terminal commit: stage → validate → rename; restore on failure."""
from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any, Callable

from .errors import MotorLearningError, GovernanceBlock
from .hashutil import canonical_json, content_hash
from .prior_store import store_tree_hash


def snapshot_store(store_dir: Path, backup_dir: Path) -> str:
    store_dir = Path(store_dir)
    backup_dir = Path(backup_dir)
    if backup_dir.exists():
        shutil.rmtree(backup_dir)
    if store_dir.exists():
        shutil.copytree(store_dir, backup_dir)
    else:
        backup_dir.mkdir(parents=True, exist_ok=True)
    return store_tree_hash(store_dir)


def restore_store(store_dir: Path, backup_dir: Path) -> None:
    store_dir = Path(store_dir)
    backup_dir = Path(backup_dir)
    if store_dir.exists():
        shutil.rmtree(store_dir)
    if backup_dir.exists() and any(backup_dir.iterdir()):
        shutil.copytree(backup_dir, store_dir)
    else:
        store_dir.mkdir(parents=True, exist_ok=True)


def write_failed_attempt(out_dir: Path, *, stage: str, error: str, staged: dict | None = None) -> Path:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "nf_motor_learning_failed_attempt_v1",
        "stage": stage,
        "error": error,
        "staged": staged,
    }
    path = out_dir / f"failed_attempt-{content_hash({'s': stage, 'e': error})[:12]}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


def atomic_terminal_commit(
    *,
    store_dir: Path,
    out_dir: Path,
    receipt: dict,
    prior: dict,
    transition_record: dict | None,
    commit_fn: Callable[[Path], None],
    inject_failure_after: str | None = None,
) -> dict[str, Any]:
    """
    Stage receipt, prior revision, transition record, and index update.
    Validate the staged bundle, then commit via commit_fn into a staging store
    and atomically replace the live store using backup/restore semantics.

    inject_failure_after: test hook — 'receipt_staging' | 'prior_staging' | 'before_index_commit'
    """
    store_dir = Path(store_dir)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    backup = Path(tempfile.mkdtemp(prefix="mlo-store-bak-"))
    staging = Path(tempfile.mkdtemp(prefix="mlo-store-stage-"))
    hash_before = snapshot_store(store_dir, backup)

    # Seed staging from current store
    if store_dir.exists():
        shutil.copytree(store_dir, staging, dirs_exist_ok=True)
    else:
        staging.mkdir(parents=True, exist_ok=True)

    try:
        # Stage receipt under out_dir staging area (not authoritative until commit)
        stage_dir = out_dir / "_staging"
        if stage_dir.exists():
            shutil.rmtree(stage_dir)
        stage_dir.mkdir(parents=True, exist_ok=True)
        receipt_stage = stage_dir / f"learning_receipt-{receipt['receipt_id']}.json"
        receipt_stage.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

        if inject_failure_after == "receipt_staging":
            raise MotorLearningError("injected failure after receipt staging")

        prior_stage = stage_dir / "prior.json"
        prior_stage.write_text(json.dumps(prior, indent=2, sort_keys=True) + "\n")
        if transition_record:
            (stage_dir / "transition.json").write_text(
                json.dumps(transition_record, indent=2, sort_keys=True) + "\n"
            )

        if inject_failure_after == "prior_staging":
            raise MotorLearningError("injected failure after prior staging")

        # Validate staged bundle completeness
        staged_bundle = {
            "receipt_id": receipt["receipt_id"],
            "prior_id": prior["prior_id"],
            "status": prior["status"],
            "live_consumable": prior.get("live_consumable"),
            "learning_receipt_id": prior.get("learning_receipt_id"),
        }
        if staged_bundle["live_consumable"] is not False:
            raise GovernanceBlock("staged prior must have live_consumable=false for W1")
        if staged_bundle["learning_receipt_id"] != receipt["receipt_id"]:
            raise GovernanceBlock("staged prior/receipt id mismatch")

        if inject_failure_after == "before_index_commit":
            raise MotorLearningError("injected failure before index commit")

        # Commit into staging store via provided function
        commit_fn(staging)

        # Atomic replace: move staging over store via rename dance
        live_tmp = Path(str(store_dir) + ".mlo_replacing")
        if live_tmp.exists():
            shutil.rmtree(live_tmp)
        if store_dir.exists():
            store_dir.rename(live_tmp)
        staging.rename(store_dir)
        if live_tmp.exists():
            shutil.rmtree(live_tmp)

        # Promote staged receipt to authoritative out_dir location
        auth_receipt = out_dir / f"learning_receipt-{receipt['receipt_id']}.json"
        shutil.copy2(receipt_stage, auth_receipt)
        shutil.copy2(prior_stage, out_dir / "prior.json")
        shutil.rmtree(stage_dir, ignore_errors=True)

        hash_after = store_tree_hash(store_dir)
        shutil.rmtree(backup, ignore_errors=True)
        return {
            "ok": True,
            "store_hash_before": hash_before,
            "store_hash_after": hash_after,
            "receipt_path": str(auth_receipt),
        }
    except Exception as exc:
        restore_store(store_dir, backup)
        # Remove any authoritative-looking receipt written during failed attempt
        for p in out_dir.glob("learning_receipt-*.json"):
            p.unlink(missing_ok=True)
        write_failed_attempt(
            out_dir,
            stage=inject_failure_after or "commit",
            error=str(exc),
            staged={"receipt_id": receipt.get("receipt_id"), "prior_id": prior.get("prior_id")},
        )
        shutil.rmtree(backup, ignore_errors=True)
        shutil.rmtree(staging, ignore_errors=True)
        if isinstance(exc, MotorLearningError):
            raise
        raise MotorLearningError(f"terminal commit failed: {exc}") from exc
