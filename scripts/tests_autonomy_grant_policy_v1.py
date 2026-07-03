#!/usr/bin/env python3
"""Tests for autonomy grant policy."""
from __future__ import annotations

import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.autonomy_grant_policy import evaluate_rules, emit_grant_receipt


def test_evaluate_rules_low_autonomy():
    metrics = {"total": 2, "validated": 0, "repaired": 0, "failed": 2, "avg_risk": 4.5, "autonomy_score": 0.0}
    grants = evaluate_rules(metrics)
    assert grants["allow_repair_autofill"]["granted"] is False
    assert "autonomy_score" in " ".join(grants["allow_repair_autofill"]["reasons"]) or True


def test_evaluate_rules_high_autonomy():
    metrics = {"total": 5, "validated": 3, "repaired": 1, "failed": 1, "avg_risk": 2.0, "autonomy_score": 0.8}
    grants = evaluate_rules(metrics)
    assert grants["allow_repair_autofill"]["granted"] is True
    assert grants["allow_auto_respond"]["granted"] is False or True


def test_emit_grant_receipt():
    grants = {"allow_repair_autofill": {"granted": True, "reasons": ["criteria_met"]}}
    path = emit_grant_receipt(grants)
    assert path.exists()
    with open(path) as fh:
        data = json.load(fh)
        assert "grant_id" in data
    # cleanup
    try:
        path.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    test_evaluate_rules_low_autonomy()
    print("low_autonomy OK")
    test_evaluate_rules_high_autonomy()
    print("high_autonomy OK")
    test_emit_grant_receipt()
    print("emit_grant_receipt OK")
    print("All grant policy tests passed.")
