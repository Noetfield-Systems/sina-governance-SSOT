#!/usr/bin/env python3
"""P0-PGR shadow cycle — compile + lint + route one packet. Zero execution, ever."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_packet_lint_v1 import NINE_GATES, lint_file, utc_now_compact, utc_now_iso  # noqa: E402

DEFAULT_RECEIPTS = ROOT / "receipts" / "p0pgr"


def founder_receipt_exists(receipts_dir: Path) -> bool:
    founder_dir = receipts_dir / "founder"
    return founder_dir.is_dir() and any(founder_dir.glob("*.json"))


def route_packet(packet: dict, receipts_dir: Path) -> tuple[str, dict]:
    """Routing decision order per P0_DISPATCH_ROUTER_RULES_v1.md."""
    gates = dict(packet.get("gates", {}))
    gates["founder_authorization_receipt"] = founder_receipt_exists(receipts_dir)
    results = {g: bool(gates.get(g)) for g in NINE_GATES}

    if not results["cloud_only"] and packet.get("route") != "SESSION_EMBEDDED":
        return "HOLD_CLOUD_UNSAFE", results
    failed = [g for g, ok in results.items() if not ok]
    if failed:
        return "QUEUED_FOUNDER_REVIEW", results
    return "ROUTED", results


def update_scorecard(receipts_dir: Path, verdict: str, cycle_id: str) -> None:
    scorecard_path = receipts_dir / "phase2_scorecard_v1.json"
    if not scorecard_path.exists():
        return
    scorecard = json.loads(scorecard_path.read_text())
    scorecard["counters"]["shadow_cycles"] = scorecard["counters"].get("shadow_cycles", 0) + 1
    scorecard["last_cycle"] = {"cycle_id": cycle_id, "verdict": verdict, "recorded_at": utc_now_iso()}
    scorecard["updated_at"] = utc_now_iso()
    scorecard_path.write_text(json.dumps(scorecard, indent=2) + "\n")


def run_cycle(packet_path: Path, receipts_dir: Path = DEFAULT_RECEIPTS) -> dict:
    receipts_dir.mkdir(parents=True, exist_ok=True)
    cycle_id = f"cycle-{utc_now_compact()}"

    lint = lint_file(packet_path, receipts_dir)
    packet: dict = {}
    if lint["verdict"] == "PASS":
        packet = json.loads(packet_path.read_text())
        verdict, gate_results = route_packet(packet, receipts_dir)
        route = packet.get("route", "")
    else:
        verdict, gate_results, route = "REPAIR_CANDIDATE", {}, ""

    receipt = {
        "schema": "p0_prompt_loop_state_v1",
        "cycle_id": cycle_id,
        "recorded_at": utc_now_iso(),
        "packet_id": packet.get("packet_id", "unparsed") if packet else "unparsed",
        "packet_path": str(packet_path.relative_to(ROOT)) if packet_path.is_relative_to(ROOT) else str(packet_path),
        "stages": {"compiled": True, "linted": True, "routed": verdict == "ROUTED"},
        "lint_rejects": lint["rejects"],
        "gate_results": gate_results,
        "verdict": verdict,
        "route": route,
        "counters": {"executions": 0, "sends": 0, "deploys": 0, "leaks": 0, "freezes": 0},
        "accounting_note": "deterministic script, zero LLM calls inside cycle; orchestration cost sits in the invoking session",
        "executor_route_note": "shadow cycle only — no executor invoked, no route deviation possible",
        "commit_flag": "flag for next founder-visible commit",
    }
    receipt_path = receipts_dir / f"loop-state-{cycle_id}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    update_scorecard(receipts_dir, verdict, cycle_id)
    receipt["_receipt_path"] = str(receipt_path)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description="P0-PGR shadow cycle runner")
    parser.add_argument("--packet", required=True)
    parser.add_argument("--receipts-dir", default=str(DEFAULT_RECEIPTS))
    args = parser.parse_args()
    receipt = run_cycle(Path(args.packet), Path(args.receipts_dir))
    print(json.dumps({k: v for k, v in receipt.items() if k != "gate_results"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
