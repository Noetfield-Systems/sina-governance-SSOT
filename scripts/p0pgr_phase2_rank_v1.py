#!/usr/bin/env python3
"""P0-PGR Phase 2 ROI-Smart Cloud-Only Ranker v1 (executes move M10).

Operating mode: PHASE_2_CLOUD_ONLY_ROI_TRACK.

Deterministic weighted ranking of campaign moves for cloud-only execution:
    direct revenue/commercial impact  35
    trust/live-proof impact           25
    founder workload reduction        15
    cloud-executable now              15
    reversibility/low-risk            10

Routing rule: CLOUD_ONLY + ROI-positive -> ranked. Mac/local-state/secrets/
IDE-bound -> HOLD_CLOUD_UNSAFE (never HARD_BLOCK, never routed to Mac).
No Mac runner. No HYBRID_MAC fallback. No Cursor UI automation.

Deterministic (L13): factors are authored constants; same inputs -> same
order. Output is a ranked RECOMMENDATION queue; execution authorization
follows founder-approved Phase 2 rules, dispatch flags are not flipped here.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAMPAIGN = ROOT / "receipts" / "p0pgr" / "campaigns" / "P0PGR-CAMPAIGN-20260708-001.json"
QUEUE_OUT = ROOT / "receipts" / "p0pgr" / "phase2_queue_v1.json"

WEIGHTS = {"direct_revenue": 35, "trust_proof": 25, "workload_reduction": 15,
           "cloud_now": 15, "reversibility": 10}

# Authored factor table (0.0-1.0). Rationale strings keep this auditable.
FACTORS = {
    "M03": dict(direct_revenue=0.90, trust_proof=1.00, workload_reduction=0.30,
                cloud_now=1.00, reversibility=1.00,
                rationale="Protects live CAD 4k offer + /register funnel; pure external read"),
    "M04": dict(direct_revenue=0.85, trust_proof=0.80, workload_reduction=0.20,
                cloud_now=0.80, reversibility=0.90,
                rationale="Conversion audit; needs labeled test identity + gating care -> slightly less immediately executable"),
    "M05": dict(direct_revenue=0.80, trust_proof=0.60, workload_reduction=0.40,
                cloud_now=1.00, reversibility=1.00,
                rationale="Unblocks first compliant outbound pipeline; predicate audit only, zero send"),
    "M02": dict(direct_revenue=0.20, trust_proof=0.70, workload_reduction=0.60,
                cloud_now=1.00, reversibility=1.00,
                rationale="Registry trust underpins all dispatch; repo-evidence sweep"),
    "M06": dict(direct_revenue=0.50, trust_proof=0.40, workload_reduction=0.40,
                cloud_now=1.00, reversibility=1.00,
                rationale="~$20/mo dead-spend recovery + governor enforceability"),
    "M07": dict(direct_revenue=0.30, trust_proof=0.30, workload_reduction=1.00,
                cloud_now=1.00, reversibility=1.00,
                rationale="Packet factory; ranked only for its revenue/trust template share per founder rule"),
    "M01": dict(direct_revenue=0.20, trust_proof=0.60, workload_reduction=0.50,
                cloud_now=1.00, reversibility=1.00,
                rationale="Census triage; trust recovery, low direct revenue"),
    "M09": dict(direct_revenue=0.10, trust_proof=0.70, workload_reduction=0.30,
                cloud_now=1.00, reversibility=1.00,
                rationale="P0 leak sweep; governance trust, no direct revenue"),
}

HOLDS = {
    "M08": "HOLD_CLOUD_UNSAFE: value is Mac-execution planning; founder directive defers all Mac-bound design in Phase 2",
    "M10": "SELF: executed by this script run",
}

EXEC_GATES = ["CLOUD_ONLY", "read-only or reversible", "ROI-positive", "no deploy",
              "no external send", "no legal/financial commitment", "no P0 leakage",
              "no unauthorized authority change"]


def main() -> int:
    campaign = json.loads(CAMPAIGN.read_text())
    moves = {m["move_id"]: m for m in campaign["moves"]}

    ranked, held = [], []
    for mid, m in moves.items():
        if mid in HOLDS:
            held.append({"move_id": mid, "packet_id": m["packet_id"],
                         "status": HOLDS[mid].split(":")[0], "reason": HOLDS[mid]})
            continue
        f = FACTORS[mid]
        score = round(sum(WEIGHTS[k] * f[k] for k in WEIGHTS), 2)
        ranked.append({
            "move_id": mid,
            "packet_id": m["packet_id"],
            "packet_file": m["packet_file"],
            "phase2_score": score,
            "factors": {k: f[k] for k in WEIGHTS},
            "rationale": f["rationale"],
            "execution_mode": m["execution_mode"],
            "route_decision": "DISPATCH_CLOUD",
            "value_class_commercial": mid in {"M03", "M04", "M05"},
        })
    ranked.sort(key=lambda r: (-r["phase2_score"], r["move_id"]))

    first = ranked[0]
    queue = {
        "schema": "p0pgr-phase2-queue-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "operating_mode": "PHASE_2_CLOUD_ONLY_ROI_TRACK",
        "executed_by_move": "M10",
        "weights": WEIGHTS,
        "ranked_queue": ranked,
        "held_items": held,
        "first_execution_candidate": {
            "move_id": first["move_id"],
            "packet_id": first["packet_id"],
            "gates_required": EXEC_GATES,
        },
        "routing_rules": [
            "CLOUD_ONLY + ROI-positive -> ranked",
            "Mac/local-state/secrets/IDE-bound -> HOLD_CLOUD_UNSAFE (not HARD_BLOCK)",
            "no Mac routing, no Mac runner build, no HYBRID_MAC fallback",
            "no Cursor UI automation",
            "weak high-ROI packet -> PROVISIONAL/DEGRADED, continue",
        ],
        "note": "Ranked recommendation. Dispatch flags not flipped by this script.",
    }
    QUEUE_OUT.write_text(json.dumps(queue, indent=2) + "\n")
    print(json.dumps({
        "queue": str(QUEUE_OUT.relative_to(ROOT)),
        "order": [(r["move_id"], r["phase2_score"]) for r in ranked],
        "held": [h["move_id"] for h in held],
        "first_execution_candidate": first["move_id"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
