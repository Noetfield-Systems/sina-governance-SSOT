#!/usr/bin/env python3
"""Weekly ROI heartbeat receipt — unknown values stay unknown (no fabrication)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"


def main() -> int:
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "schema": "roi-heartbeat-receipt-v1",
        "receipt_id": f"roi-heartbeat-{ts}",
        "recorded_at": ts,
        "canon_version": "founder_canon_v1.0.0",
        "metrics": {
            "cost_per_signal_cad": "unknown",
            "free_tier_ceiling_max_pct": "unknown",
            "trap_battery_pass_pct": "unknown",
            "fixture_agreement_pct": "unknown",
            "pattern_exports_per_week": "unknown",
            "receipt_chain_verifier": "unknown",
        },
        "blocker_count": "unknown",
        "source": "docs/1111_UPGRADE_PLANS_v2.md scorecard",
        "note": "Populate from TrustField cost_event and Signal Factory fixtures when available",
    }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS / f"{receipt['receipt_id']}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("write_roi_heartbeat_v1: OK")
    print(json.dumps({"receipt_id": receipt["receipt_id"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
