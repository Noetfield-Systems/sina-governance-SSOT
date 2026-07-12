#!/usr/bin/env python3
"""Tests for autonomy revocation checker."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.autonomy_grant_policy import emit_grant_receipt
from scripts.autonomy_revocation_checker import main as revoker_main, load_grant_receipts
from scripts.autonomy_scorer import load_receipts, score

RECEIPT_DIR = ROOT / "receipts" / "agentic"


def test_revocation_emitted_when_autonomy_low():
    # prepare a grant receipt that has a revoke_if.autonomy_below very high
    grants = {
        "allow_retry_rerun": {"granted": True, "reasons": ["criteria_met"], "revoke_if": {"autonomy_below": 0.99}}
    }
    p = emit_grant_receipt(grants)
    # create minimal receipts showing low autonomy
    r1 = {"signal_id": "rtest-1", "status": "validation_failed", "risk_score": 5}
    with open(RECEIPT_DIR / f"receipt-rtest-1-{int(time.time())}.json", "w") as fh:
        json.dump(r1, fh)
    # run revoker
    revoker_main()
    # check for revocation files
    found = False
    for f in RECEIPT_DIR.glob("revocations-*.json"):
        with open(f, 'r') as fh:
            data = json.load(fh)
            if data.get("source_grant") == p.name:
                found = True
                break
    assert found, "Expected revocation not emitted"
    # cleanup created files (best-effort)
    try:
        p.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    test_revocation_emitted_when_autonomy_low()
    print("revocation test OK")
