#!/usr/bin/env python3
"""audit_receipt_ledger_unified_v1.py — W4-01 wiring wrapper.

Runs the UNCHANGED audit_receipt_ledger_v1 logic over the UNIFIED receipt
corpus instead of only top-level receipts/: every directory containing .json
under receipts/ (recursive, incl. p0pgr/) and language_gate/receipts/
(recursive). Zero new audit logic — it only widens RECEIPT_DIRS, which the
base module reads at collect time. Same flags: [--json] [--write-receipt].
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import audit_receipt_ledger_v1 as base  # noqa: E402

ROOT = base.ROOT
dirs = set()
for top in (ROOT / "receipts", ROOT / "language_gate" / "receipts"):
    if top.is_dir():
        for p in top.rglob("*.json"):
            dirs.add(p.parent)
base.RECEIPT_DIRS = sorted(dirs)

if __name__ == "__main__":
    sys.exit(base.main())
