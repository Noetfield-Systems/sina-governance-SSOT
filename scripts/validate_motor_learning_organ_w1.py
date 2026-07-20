#!/usr/bin/env python3
"""Validate Motor Learning Organ W1 — hard-fail governance + scope guards."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def main() -> int:
    required = [
        "scripts/motor_learning/lifecycle.py",
        "scripts/motor_learning/prior_store.py",
        "scripts/motor_learning/ecqr.py",
        "scripts/motor_learning/receipt.py",
        "scripts/motor_learning/orchestrator.py",
        "scripts/motor_learning/event_registry.py",
        "scripts/motor_learning_organ_w1_run.py",
        "tests/test_motor_learning_organ_w1.py",
        "data/nf_motor_learning_organ_v1_LOCKED.json",
    ]
    for rel in required:
        if not (ROOT / rel).exists():
            fail(f"missing: {rel}")

    lock = json.loads((ROOT / "data/nf_motor_learning_organ_v1_LOCKED.json").read_text())
    maturity = lock.get("implementation_maturity") or {}

    # Hard forbidden checks
    if lock.get("data_runway_unlock") not in ("HOLD", "hold", False):
        fail("data_runway_unlock must be HOLD")
    forbidden = set(lock.get("forbidden") or [])
    for req in ("base_model_training_phase1", "level_3_bandit_high_risk", "unsupervised_architecture_redesign"):
        if req not in forbidden:
            fail(f"forbidden missing {req}")
    not_mode = set(lock.get("not_learning_mode") or [])
    for req in ("base_model_finetune", "level_3_bandit_high_risk"):
        if req not in not_mode and req not in forbidden:
            fail(f"not_learning_mode/forbidden missing {req}")

    if maturity.get("live_promotion") != "FORBIDDEN":
        fail("live_promotion must be FORBIDDEN")
    if maturity.get("model_learning") != "FORBIDDEN":
        fail("model_learning must be FORBIDDEN")

    # Lifecycle must not allow require_receipt=False for terminals
    life = (ROOT / "scripts/motor_learning/lifecycle.py").read_text()
    if "require_receipt=False is forbidden" not in life:
        fail("lifecycle must reject require_receipt=False for terminal states")

    # No ML tokens
    for py in (ROOT / "scripts/motor_learning").glob("*.py"):
        text = py.read_text().lower()
        for tok in ("torch", "tensorflow", "sklearn", "xgboost", "backprop"):
            if tok in text:
                fail(f"ML token {tok} in {py.name}")

    # Unit tests
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_motor_learning_organ_w1", "-q"],
        cwd=str(ROOT), capture_output=True, text=True,
    )
    if proc.returncode != 0:
        fail("unittest failed:\n" + proc.stderr + proc.stdout)

    # E2E + dry-run store hash
    import tempfile
    sys.path.insert(0, str(ROOT / "scripts"))
    from motor_learning.prior_store import store_tree_hash as sth
    from motor_learning.orchestrator import run_from_fixture_dir

    td = Path(tempfile.mkdtemp(prefix="mlo-val-"))
    store = td / "store"
    store.mkdir()
    before = sth(store)
    summary = run_from_fixture_dir(
        ROOT / "fixtures/motor_learning_w1/01_repeated_success_ratify",
        out_dir=td / "out", store_dir=store, dry_run=True,
    )
    after = sth(store)
    if before != after:
        fail(f"dry-run mutated store: {before} != {after}")
    if summary.get("ecqr_decision") != "RATIFIED":
        fail(f"e2e expected RATIFIED got {summary.get('ecqr_decision')} blocked={summary.get('blocked_reason')}")
    if not summary.get("receipt_id"):
        fail("e2e missing receipt")
    if summary.get("live_promotion"):
        fail("live_promotion true")

    # Rollback e2e
    td2 = Path(tempfile.mkdtemp(prefix="mlo-rb-"))
    rb = run_from_fixture_dir(
        ROOT / "fixtures/motor_learning_w1/07_rollback",
        out_dir=td2 / "out", store_dir=td2 / "store", dry_run=True,
    )
    if rb.get("final_state") != "ROLLED_BACK":
        fail(f"rollback e2e failed: {rb}")

    # Scope guard vs exact base SHA
    base = os.environ.get("MLO_BASE_SHA") or ""
    if not base:
        r = subprocess.run(["git", "rev-parse", "origin/main"], cwd=str(ROOT), capture_output=True, text=True)
        if r.returncode != 0:
            fail(f"cannot resolve base SHA for scope guard: {r.stderr}")
        else:
            base = r.stdout.strip()
    if base:
        # Prefer merge-base so shallow/unrelated tips cannot break the guard
        mb = subprocess.run(
            ["git", "merge-base", "HEAD", base],
            cwd=str(ROOT), capture_output=True, text=True,
        )
        diff_base = mb.stdout.strip() if mb.returncode == 0 and mb.stdout.strip() else base
        if mb.returncode != 0:
            # Fetch origin/main and retry once
            subprocess.run(["git", "fetch", "origin", "main", "--depth=0"], cwd=str(ROOT), capture_output=True)
            mb2 = subprocess.run(
                ["git", "merge-base", "HEAD", "origin/main"],
                cwd=str(ROOT), capture_output=True, text=True,
            )
            if mb2.returncode != 0:
                fail(f"scope diff failed against {base}: no merge base ({mb.stderr or mb2.stderr})")
                diff_base = None
            else:
                diff_base = mb2.stdout.strip()
        if diff_base:
            diff = subprocess.run(
                ["git", "diff", "--name-only", f"{diff_base}...HEAD"],
                cwd=str(ROOT), capture_output=True, text=True,
            )
            if diff.returncode != 0:
                fail(f"scope diff failed against {diff_base}: {diff.stderr}")
            else:
                for line in diff.stdout.splitlines():
                    if line.startswith("landing-site/"):
                        fail(f"landing-site/ changed: {line}")

    # Maturity honesty — PARTIAL until new adversarial probes prove closure
    for key in (
        "terminal_receipt_enforcement",
        "persistence_governance_gate",
        "ecqr_artifact_binding",
        "atomic_terminal_persistence",
    ):
        val = maturity.get(key)
        if val not in ("IMPLEMENTED", "PARTIAL"):
            fail(f"maturity.{key} must be IMPLEMENTED or PARTIAL, got {val}")
    if maturity.get("executable_reference_pipeline") not in ("IMPLEMENTED", None):
        # optional key
        if maturity.get("executable_reference_pipeline") != "IMPLEMENTED":
            fail("executable_reference_pipeline must be IMPLEMENTED")
    if maturity.get("w1_live_consumable") not in ("FORBIDDEN", None):
        if maturity.get("w1_live_consumable") != "FORBIDDEN":
            fail("w1_live_consumable must be FORBIDDEN")
    if maturity.get("live_promotion") != "FORBIDDEN":
        fail("live_promotion must be FORBIDDEN")
    if maturity.get("model_learning") != "FORBIDDEN":
        fail("model_learning must be FORBIDDEN")
    if maturity.get("data_runway") not in ("HOLD", "FORBIDDEN"):
        fail("data_runway must be HOLD")
    aa = lock.get("auto_apply_allowlist") or {}
    if aa.get("enabled") is not False:
        fail("auto_apply_allowlist.enabled must be false")
    if maturity.get("auto_apply") not in ("FUTURE_W2", "NOT_IMPLEMENTED"):
        fail("maturity.auto_apply must be FUTURE_W2 or NOT_IMPLEMENTED")

    if errors:
        print("validate_motor_learning_organ_w1: FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("validate_motor_learning_organ_w1: ALL PASS")
    print(json.dumps({
        "dry_run_store_hash_before": before,
        "dry_run_store_hash_after": after,
        "rollback_final_state": rb.get("final_state"),
        "live_promotion": False,
        "live_consumable": False,
        "model_learning": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
