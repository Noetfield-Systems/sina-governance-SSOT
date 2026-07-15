#!/usr/bin/env python3
"""Basic tests for agentic loops components. Run with: python3 scripts/tests_agentic_v1.py"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
import tempfile
import time

# Ensure repo root is importable for 'scripts' package imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.agentic_loops_v1 import SimpleWorker, Validator, Adversary, SelfRepair, emit_receipt, RECEIPT_DIR
from scripts.autonomy_scorer import score, emit_report


def test_validator_pass():
    payload = {
        "signal_id": "t1",
        "timestamp": "2026-07-03T00:00:00Z",
        "source": "email:test@example.com",
        "classification": "vendor",
        "decision": "reply",
        "risk_score": 1,
        "action": "reply",
        "status": "generated",
    }
    ok, errs = Validator.validate(payload)
    assert ok, errs


def test_adversary_corrupt():
    payload = {
        "signal_id": "t2",
        "timestamp": "2026-07-03T00:00:00Z",
        "source": "email:test@example.com",
        "classification": "vendor",
        "decision": "reply",
        "risk_score": 1,
        "action": "reply",
        "status": "generated",
    }
    corrupted = Adversary.corrupt(payload)
    ok, errs = Validator.validate(corrupted)
    assert not ok
    assert any("missing required field" in e or "risk_score out of 0..5 range" in e or "risk_score not numeric" in e for e in errs)


def test_selfrepair_strategies():
    worker = SimpleWorker()
    task_name = "test-task"
    # original payload that will cause worker to drop 'source' when classification == 'client' and not repair
    original = {"signal_id": "t3", "source": "web:1", "classification": "client", "decision": "reply", "risk_score": 2}
    # produce corrupted output via adversary
    out = worker.process(task_name, original)
    corrupted = Adversary.corrupt(out)
    # attempt repair
    repaired = SelfRepair.attempt_repair(worker, task_name, original)
    assert repaired is not None
    assert repaired.get("status", "").startswith("repaired")


def test_autonomy_scorer_writes_report(tmp_path):
    # create couple of receipts in a temp dir, but scorer reads from receipts/agentic; so write there
    r1 = {"signal_id": "s-test-1", "status": "validated", "risk_score": 1}
    r2 = {"signal_id": "s-test-2", "status": "repaired_by_rerun", "risk_score": 3}
    p1 = RECEIPT_DIR / f"receipt-s-test-1-{int(time.time())}.json"
    p2 = RECEIPT_DIR / f"receipt-s-test-2-{int(time.time())}.json"
    with open(p1, "w") as f:
        json.dump(r1, f)
    with open(p2, "w") as f:
        json.dump(r2, f)
    rep = score([r1, r2])
    assert rep["total"] == 2
    assert rep["validated"] == 1
    assert rep["repaired"] == 1
    path = emit_report(rep)
    assert path.exists()
    # cleanup
    try:
        p1.unlink()
        p2.unlink()
        path.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    test_validator_pass()
    print("test_validator_pass OK")
    test_adversary_corrupt()
    print("test_adversary_corrupt OK")
    test_selfrepair_strategies()
    print("test_selfrepair_strategies OK")
    test_autonomy_scorer_writes_report(None)
    print("test_autonomy_scorer_writes_report OK")
    print("All agentic tests passed.")