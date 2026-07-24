#!/usr/bin/env python3
"""Motor Learning Organ tick — heartbeat + Decision Capacity Phase B shadow replay.

Does not promote live priors, train models, or mutate architecture.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "learning"
LOCK = ROOT / "data" / "nf_motor_learning_organ_v1_LOCKED.json"
PASS = ROOT / "data" / "nf_motor_learning_organ_pass_checks_v1.json"
CAPACITY_REPLAY = ROOT / "scripts" / "decision_capacity_shadow_replay_v1.py"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["daily_mine", "weekly_roi", "heartbeat"], default="heartbeat")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lock = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    pass_checks = json.loads(PASS.read_text()) if PASS.exists() else {}

    capacity_replay: dict = {"ran": False}
    learning_emit = "NOOP_HEARTBEAT"
    exit_code = 0
    if args.mode == "daily_mine" and CAPACITY_REPLAY.is_file():
        proc = subprocess.run(
            [sys.executable, str(CAPACITY_REPLAY), "--write-receipt"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        exit_code = proc.returncode
        try:
            capacity_replay = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            capacity_replay = {
                "ran": True,
                "parse_error": True,
                "stdout_tail": (proc.stdout or "")[-400:],
                "stderr_tail": (proc.stderr or "")[-400:],
            }
        capacity_replay["ran"] = True
        capacity_replay["exit_code"] = proc.returncode
        learning_emit = "DECISION_CAPACITY_SHADOW_REPLAY"

    receipt = {
        "schema": "motor_learning_organ_receipt_v1",
        "loop_id": "motor_learning_organ_v1",
        "mode": args.mode,
        "saved_at": now,
        "last_fired_at": now,
        "trigger_host": "cloud",
        "deadman": "sourcea-deadman-v1",
        "decision_id": lock.get("decision_id", "NF-MOTOR-LEARNING-ORGAN-V1"),
        "runtime_state": "PHASE_B_CAPACITY_SHADOW_ENABLED" if args.mode == "daily_mine" else "HEARTBEAT",
        "actions": {
            "pattern_mine": "DECISION_CAPACITY_ENQUEUE_SCAN" if args.mode == "daily_mine" else "NOOP",
            "learning_record_emit": learning_emit,
            "policy_snapshot_promote": "FORBIDDEN_THIS_TICK",
            "architecture_mutate": "FORBIDDEN",
            "decision_capacity_shadow_replay": capacity_replay,
        },
        "pass_checks_ref": "data/nf_motor_learning_organ_pass_checks_v1.json",
        "checks_status": {
            c["check_id"]: c.get("status")
            for c in pass_checks.get("checks", [])
        },
        "verdict": "PASS_HEARTBEAT" if args.mode == "heartbeat" else "PASS_DAILY_MINE",
    }
    if capacity_replay.get("verdict") and str(capacity_replay.get("verdict")).startswith("PASS"):
        receipt["verdict"] = "PASS_DAILY_MINE_WITH_CAPACITY_SHADOW"

    if args.write_receipt:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out_path = RECEIPT_DIR / f"motor-learning-organ-{args.mode}-{stamp}.json"
        out_path.write_text(json.dumps(receipt, indent=2) + "\n")
        receipt["receipt_path"] = str(out_path.relative_to(ROOT))

    print(json.dumps(receipt, indent=2))
    if args.mode == "daily_mine" and CAPACITY_REPLAY.is_file():
        return 0 if exit_code == 0 else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
