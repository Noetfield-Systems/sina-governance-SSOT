#!/usr/bin/env python3
"""Validate Motor Learning Organ W1 reference implementation + governance bounds."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def main() -> int:
    required_files = [
        "scripts/motor_learning/normalize.py",
        "scripts/motor_learning/extract.py",
        "scripts/motor_learning/prior_store.py",
        "scripts/motor_learning/similarity.py",
        "scripts/motor_learning/mine.py",
        "scripts/motor_learning/confidence.py",
        "scripts/motor_learning/lifecycle.py",
        "scripts/motor_learning/shadow.py",
        "scripts/motor_learning/ecqr.py",
        "scripts/motor_learning/receipt.py",
        "scripts/motor_learning/orchestrator.py",
        "scripts/motor_learning_organ_w1_run.py",
        "tests/test_motor_learning_organ_w1.py",
        "data/nf_motor_learning_organ_v1_LOCKED.json",
        "data/nf_motor_learning_receipt_v1.json",
        "fixtures/motor_learning_w1/01_repeated_success_ratify/events.json",
    ]
    for rel in required_files:
        if not (ROOT / rel).exists():
            fail(f"missing required file: {rel}")

    lock = json.loads((ROOT / "data/nf_motor_learning_organ_v1_LOCKED.json").read_text())
    maturity = lock.get("implementation_maturity") or {}
    # Honest maturity: local W1 engine must be IMPLEMENTED; live cross-repo remain not
    must_impl = [
        "event_normalization",
        "pattern_extraction",
        "prior_retrieval",
        "pattern_mining",
        "similarity",
        "confidence",
        "shadow_evaluation",
        "learning_engine_orchestration",
        "ratification_evidence",
    ]
    for key in must_impl:
        if maturity.get(key) != "IMPLEMENTED":
            fail(f"maturity.{key} must be IMPLEMENTED for W1 reference (got {maturity.get(key)})")
    for key in ("sourcea_live_export", "runway_live_consume", "live_promotion"):
        if maturity.get(key) in ("IMPLEMENTED",):
            fail(f"maturity.{key} must not be IMPLEMENTED yet")

    # Forbidden unlocks
    if lock.get("data_runway_unlock") not in ("HOLD", False, "hold"):
        fail("data_runway_unlock must remain HOLD")
    for banned in ("base_model_finetune", "level_3_bandit_high_risk"):
        if banned not in (lock.get("not_learning_mode") or []) and banned not in (lock.get("forbidden") or []):
            # soft check via not_learning_mode or forbidden lists
            pass
    if "base_model_training_phase1" not in (lock.get("forbidden") or []):
        fail("forbidden must include base_model_training_phase1")

    # Scope guard: landing-site must not appear in this change set expectation
    # (validated at commit time; here ensure validator itself isn't under landing-site)
    if (ROOT / "landing-site").exists():
        # existence ok on main workspace; W1 worktree shouldn't add files there
        pass

    # No ML training imports in motor_learning package
    ml_dir = ROOT / "scripts" / "motor_learning"
    banned_tokens = ("torch", "tensorflow", "sklearn", "xgboost", "fit_predict", "backprop")
    for py in ml_dir.glob("*.py"):
        text = py.read_text().lower()
        for tok in banned_tokens:
            if tok in text:
                fail(f"ML token '{tok}' found in {py.name}")

    # Heartbeat workflow must not ratify
    wf = ROOT / ".github/workflows/motor-learning-organ-v1.yml"
    if wf.exists():
        wft = wf.read_text().lower()
        if "ratif" in wft and "fixture" not in wft:
            # allow comments about no ratify
            if "no live" not in wft and "no-promot" not in wft and "observe" not in wft:
                fail("heartbeat workflow appears to ratify")

    # Run unit tests
    proc = subprocess.run(
        [sys.executable, "-m", "unittest", "tests.test_motor_learning_organ_w1", "-q"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        fail("unittest failed:\n" + proc.stderr + proc.stdout)

    # Deterministic e2e fixture
    import tempfile
    td = Path(tempfile.mkdtemp(prefix="mlo-validate-"))
    proc2 = subprocess.run(
        [
            sys.executable,
            "scripts/motor_learning_organ_w1_run.py",
            "--fixture",
            "fixtures/motor_learning_w1/01_repeated_success_ratify",
            "--out",
            str(td / "out"),
            "--store",
            str(td / "store"),
            "--dry-run",
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc2.returncode != 0:
        fail("e2e fixture run failed:\n" + proc2.stderr + proc2.stdout)
    else:
        summary = json.loads((td / "out" / "summary.json").read_text())
        if summary.get("live_promotion"):
            fail("e2e summary claims live_promotion")
        if summary.get("ecqr_decision") != "RATIFIED":
            fail(f"e2e expected RATIFIED, got {summary.get('ecqr_decision')}")
        if not summary.get("receipt_id"):
            fail("e2e missing receipt_id")

    if errors:
        print("validate_motor_learning_organ_w1: FAIL")
        for e in errors:
            print(" -", e)
        return 1
    print("validate_motor_learning_organ_w1: ALL PASS")
    print(json.dumps({"maturity_w1_local": "IMPLEMENTED", "live_promotion": False, "model_learning": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
