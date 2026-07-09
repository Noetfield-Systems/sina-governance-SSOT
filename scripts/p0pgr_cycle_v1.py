#!/usr/bin/env python3
"""P0-PGR Shadow Cycle v1 (Phase-0).

One shadow cycle: read evidence → load packet → lint → ROUTE DECISION ONLY
(no execution) → emit loop-state receipt to receipts/p0pgr/.

Hard limits (Phase-0): no deploy, no repo moves, no authority-plane writes,
no Mac runner execution, no Cursor UI automation, no lane registration.

Non-binary output (RUNTIME_CONTINUITY_LAW_v1): PASS / PARTIAL / DEGRADED /
SANDBOXED / PROVISIONAL / NEEDS_RETRY / NEEDS_REVIEW / FOUNDER_ONLY /
HARD_BLOCK / REPAIR_CANDIDATE. A bad packet becomes a REPAIR_CANDIDATE
file — the lane never stops.

Deterministic (L13): script owns all transitions; no LLM calls in Phase-0,
so metered cost is a true 0.0.
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_evidence_reader_v1 import collect as collect_evidence  # noqa: E402
from p0pgr_packet_lint_v1 import lint_packet  # noqa: E402

RECEIPT_DIR = ROOT / "receipts" / "p0pgr"
REPAIR_DIR = RECEIPT_DIR / "repair_candidates"
LOOP_SCHEMA = ROOT / "p0-pgr" / "P0_PROMPT_LOOP_STATE_SCHEMA_v1.json"

ROUTE_VERDICT = {
    "CLOUD_ONLY": "DISPATCH_CLOUD",
    "HYBRID_MAC": "DISPATCH_MAC",
    "HUMAN_REVIEW": "HUMAN_REVIEW_PACKET",
    "FOUNDER_ONLY": "FOUNDER_ONLY",
}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def cycle_id() -> str:
    return "P0PGR-CYCLE-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def validate_receipt(receipt: dict) -> list[str]:
    try:
        from jsonschema import Draft202012Validator
        schema = json.loads(LOOP_SCHEMA.read_text())
        return [e.message for e in Draft202012Validator(schema).iter_errors(receipt)]
    except ImportError:
        return ["DEGRADED: jsonschema unavailable, receipt not schema-checked"]


def run_cycle(packet_path: Path) -> dict:
    started = utcnow()
    cid = cycle_id()

    # 1. Evidence (bundle_hash for replay)
    evidence = collect_evidence()

    # 2. Load packet
    packet = json.loads(packet_path.read_text())
    packet_id = packet.get("id", "UNKNOWN")

    # 3. Lint
    lint = lint_packet(packet)

    # 4. Route decision only — no execution in shadow mode
    if lint["verdict"] == "PASS":
        verdict = ROUTE_VERDICT.get(packet.get("execution_mode"), "HOLD")
        decision_reason = (
            f"lint PASS; shadow route -> {packet.get('delivery_route')}"
            f" / {packet.get('target_executor')} (no execution in Phase-0)"
        )
        quality_state = "PASS"
        cycle_verdict = "PASS"
    else:
        verdict = "HOLD"
        decision_reason = "lint REPAIR_CANDIDATE: " + "; ".join(lint["reasons"])[:400]
        quality_state = "NEEDS_RETRY"
        cycle_verdict = "REPAIR_CANDIDATE"
        REPAIR_DIR.mkdir(parents=True, exist_ok=True)
        (REPAIR_DIR / f"{cid}-{packet_id}.json").write_text(json.dumps({
            "schema": "p0pgr-repair-candidate-v1",
            "cycle_id": cid,
            "packet_id": packet_id,
            "packet_path": str(packet_path),
            "reasons": lint["reasons"],
            "filed_at": utcnow(),
            "next_improvement": "fix packet fields listed in reasons, re-lint",
        }, indent=2) + "\n")

    # 5. Loop-state receipt
    receipt = {
        "cycle_id": cid,
        "started_at": started,
        "finished_at": utcnow(),
        "state": "COMPLETE",
        "evidence": {
            "sources_read": sorted(evidence["p0pgr_files"].keys())
            + ["data/github_automation_registry_v1.json",
               "data/agent_read_surfaces_v1.json", "receipts/"],
            "row_ids": [packet_id],
            "stale_sources": (
                [] if evidence["census"].get("file") else ["workflow-census"]
            ),
            "bundle_hash": evidence["bundle_hash"],
        },
        "classification": {
            "problem_class": "repair" if cycle_verdict == "REPAIR_CANDIDATE"
            else packet.get("problem_class", "verification"),
            "reason": decision_reason[:500],
            "evidence_refs": packet.get("evidence_refs", [f"packet:{packet_id}"]),
        },
        "roi": {
            "score": packet.get("roi_score", 0),
            "value_class": packet.get("value_class", "none"),
            "model_tier": packet.get("model_tier", "cheap"),
            "reduces_founder_workload": True,
        },
        "decision": {"verdict": verdict, "reason": decision_reason[:500]},
        "packet_id": packet_id if packet_id != "UNKNOWN" else None,
        "dispatch": {
            "target": packet.get("owner_agent", "verifier"),
            "mode": "shadow",
            "execution_mode": packet.get("execution_mode"),
            "delivery_route": packet.get("delivery_route"),
            "target_executor": packet.get("target_executor"),
            "fallback_used": False,
            "dispatched_at": utcnow(),
            "founder_approved": False,
        },
        "receipt_result": {
            "quality_state": quality_state,
            "verdict": "PENDING",
            "low_quality_labels": {
                "confidence": "high" if cycle_verdict == "PASS" else "low",
                "scope": "shadow compile+route only, zero execution",
                "reversibility": "fully reversible (files only)",
                "next_improvement": "founder review of shadow packet"
                if cycle_verdict == "PASS" else "repair packet per candidate file",
            },
        },
        "cost": {
            "provider": "none", "model": "none",
            "tokens_in": 0, "tokens_out": 0,
            "total_usd": 0.0,
        },
        "founder_blocked_snapshot": {"count": 0, "oldest_age_days": 0},
    }
    # drop None packet_id to satisfy schema pattern
    if receipt["packet_id"] is None:
        del receipt["packet_id"]

    # remove keys not in schema for dispatch when packet malformed
    receipt["dispatch"] = {k: v for k, v in receipt["dispatch"].items() if v is not None}

    schema_errors = validate_receipt(receipt)
    if schema_errors:
        # Continuity: degrade, tag, still write.
        receipt["receipt_result"]["quality_state"] = "DEGRADED"
        cycle_verdict = "DEGRADED"

    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    out = RECEIPT_DIR / f"{cid}.json"
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    return {
        "cycle_id": cid,
        "verdict": cycle_verdict,
        "decision": verdict,
        "quality_state": receipt["receipt_result"]["quality_state"],
        "bundle_hash": evidence["bundle_hash"],
        "lint": lint["verdict"],
        "lint_reasons": lint["reasons"],
        "receipt_path": str(out.relative_to(ROOT)),
        "receipt_schema_errors": schema_errors,
        "cost_usd": 0.0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--packet", type=Path,
                    default=ROOT / "p0-pgr" / "EXAMPLE_PACKET_P0PGR-20260708-001.json")
    args = ap.parse_args()
    result = run_cycle(args.packet)
    print(json.dumps(result, indent=2))
    return 0  # continuity: every verdict is a valid outcome


if __name__ == "__main__":
    sys.exit(main())
