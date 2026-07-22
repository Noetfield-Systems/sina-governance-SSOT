#!/usr/bin/env python3
"""Motor Learning Organ tick — W0 observe/heartbeat only.

Does not promote live priors, train models, or mutate architecture.
Emits receipts/learning/motor-learning-organ-*.json and prints JSON summary.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "learning"
LOCK = ROOT / "data" / "nf_motor_learning_organ_v1_LOCKED.json"
PASS = ROOT / "data" / "nf_motor_learning_organ_pass_checks_v1.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["daily_mine", "weekly_roi", "heartbeat"], default="heartbeat")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    pass_checks = json.loads(PASS.read_text()) if PASS.exists() else {}

    receipt = {
        "schema": "motor_learning_organ_receipt_v1",
        "loop_id": "motor_learning_organ_v1",
        "mode": args.mode,
        "saved_at": now,
        "last_fired_at": now,
        "trigger_host": "cloud",
        "deadman": "sourcea-deadman-v1",
        "decision_id": lock.get("decision_id", "NF-MOTOR-LEARNING-ORGAN-V1"),
        "runtime_state": "STUB_W0_OBSERVE_ONLY",
        "actions": {
            "pattern_mine": "STUB_NOOP",
            "learning_record_emit": "STUB_NOOP",
            "policy_snapshot_promote": "FORBIDDEN_THIS_TICK",
            "architecture_mutate": "FORBIDDEN",
        },
        "pass_checks_ref": "data/nf_motor_learning_organ_pass_checks_v1.json",
        "checks_status": {
            c["check_id"]: c.get("status")
            for c in pass_checks.get("checks", [])
        },
        "verdict": "PASS_HEARTBEAT_STUB",
    }

    out_path = None
    if args.write_receipt:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = RECEIPT_DIR / f"motor-learning-organ-{args.mode}-{stamp}.json"
        out_path.write_text(json.dumps(receipt, indent=2) + "\n")
        receipt["receipt_path"] = str(out_path.relative_to(ROOT))

    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
