#!/usr/bin/env python3
"""Tests for founder approval CLI."""
from __future__ import annotations

import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.autonomy_grant_policy import emit_grant_receipt
from scripts.founder_approval_cli import main as cli_main, load_grant_receipts

RECEIPT_DIR = ROOT / "receipts" / "agentic"


def test_founder_list_and_approve():
    # create a grant that requires founder
    grants = {"allow_publish_artifacts": {"granted": False, "reasons": ["founder_trigger_required"]}}
    p = emit_grant_receipt(grants)
    # list
    grants_map = load_grant_receipts()
    assert p.name in grants_map
    # approve via CLI
    rc = cli_main(["--approve", p.name, "--capability", "allow_publish_artifacts", "--founder", "founder-A"])
    assert rc == 0
    # cleanup
    try:
        p.unlink()
    except Exception:
        pass


if __name__ == "__main__":
    test_founder_list_and_approve()
    print("founder approval tests passed")
