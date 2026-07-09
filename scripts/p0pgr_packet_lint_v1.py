#!/usr/bin/env python3
"""P0-PGR packet linter — reject list R1-R9; failures file repair candidates, lane continues."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPTS = ROOT / "receipts" / "p0pgr"

ALLOWED_ROUTES = {"CLOUD_WORKER", "CLOUD_RESEARCH", "SESSION_EMBEDDED", "REVIEW_QUEUE"}
FORBIDDEN_ROUTES = {"MAC_RUNNER", "HYBRID_MAC"}
NINE_GATES = [
    "cloud_only",
    "read_only_or_reversible",
    "roi_positive",
    "no_deploy",
    "no_external_send",
    "no_legal_financial_commitment",
    "no_p0_leakage",
    "no_authority_change",
    "founder_authorization_receipt",
]
ROI_FIELDS = ["revenue", "trust", "workload_relief", "cloud_now", "reversibility"]
VAGUE_VERBS = ["explore", "consider", "look into", "think about"]
FOUNDER_ROUTING_MARKERS = [
    "founder will validate",
    "founder will review",
    "ask sina",
    "sina to review",
    "founder to verify",
]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def lint_packet(packet: dict) -> list[str]:
    rejects: list[str] = []

    if not str(packet.get("mission", "")).strip() or not str(packet.get("problem_statement", "")).strip():
        rejects.append("R1: missing/empty mission or problem_statement")

    deliverable = packet.get("deliverable")
    if not isinstance(deliverable, dict) or not all(
        str(deliverable.get(k, "")).strip() for k in ("type", "destination", "acceptance")
    ):
        rejects.append("R2: deliverable missing type/destination/acceptance")

    route = packet.get("route")
    if route in FORBIDDEN_ROUTES:
        rejects.append(f"R3: forbidden Mac route {route}")
    elif route not in ALLOWED_ROUTES:
        rejects.append(f"R3: route not in allowed enum: {route!r}")

    gates = packet.get("gates")
    if not isinstance(gates, dict):
        rejects.append("R4: gates block missing")
    else:
        missing = [g for g in NINE_GATES if g not in gates]
        if missing:
            rejects.append(f"R4: gates absent: {', '.join(missing)}")

    roi = packet.get("roi")
    if not isinstance(roi, dict):
        rejects.append("R5: roi block missing")
    else:
        bad = [f for f in ROI_FIELDS if not isinstance(roi.get(f), (int, float))]
        if bad:
            rejects.append(f"R5: roi non-numeric: {', '.join(bad)}")

    mission = str(packet.get("mission", "")).lower()
    acceptance = ""
    if isinstance(deliverable, dict):
        acceptance = str(deliverable.get("acceptance", "")).strip()
    if any(v in mission for v in VAGUE_VERBS) and len(acceptance) < 16:
        rejects.append("R6: vague-verb mission without measurable acceptance")

    blob = json.dumps(packet).lower()
    hits = [m for m in FOUNDER_ROUTING_MARKERS if m in blob]
    if hits:
        rejects.append(f"R7: routes validation to founder: {', '.join(hits)}")

    evidence = packet.get("evidence_required")
    if not isinstance(evidence, list) or not evidence:
        rejects.append("R8: evidence_required empty")

    if packet.get("schema") != "p0_prompt_packet_v1.1":
        rejects.append("R9: wrong/missing schema version")
    pid = str(packet.get("packet_id", ""))
    if not pid.startswith("PKT-") or len(pid) < 8:
        rejects.append("R9: packet_id format invalid")

    return rejects


def file_repair_candidate(packet: dict, rejects: list[str], receipts_dir: Path, source: str) -> Path:
    repair_dir = receipts_dir / "repair_candidates"
    repair_dir.mkdir(parents=True, exist_ok=True)
    ts = utc_now_compact()
    pid = str(packet.get("packet_id", "unparsed")) if isinstance(packet, dict) else "unparsed"
    path = repair_dir / f"repair-{pid}-{ts}.json"
    path.write_text(
        json.dumps(
            {
                "schema": "p0pgr_repair_candidate_v1",
                "recorded_at": utc_now_iso(),
                "source": source,
                "rejects": rejects,
                "packet": packet,
                "continuity_law": "lane continues; repair and re-lint",
            },
            indent=2,
        )
        + "\n"
    )
    return path


def lint_file(packet_path: Path, receipts_dir: Path = DEFAULT_RECEIPTS) -> dict:
    try:
        packet = json.loads(packet_path.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        rejects = [f"R9: unparseable packet ({exc})"]
        repair = file_repair_candidate({}, rejects, receipts_dir, str(packet_path))
        return {"verdict": "REPAIR_CANDIDATE", "rejects": rejects, "repair_candidate": str(repair)}

    rejects = lint_packet(packet)
    if rejects:
        repair = file_repair_candidate(packet, rejects, receipts_dir, str(packet_path))
        return {"verdict": "REPAIR_CANDIDATE", "rejects": rejects, "repair_candidate": str(repair)}
    return {"verdict": "PASS", "rejects": [], "packet_id": packet.get("packet_id")}


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(json.dumps({"error": "usage: p0pgr_packet_lint_v1.py <packet.json>"}))
        return 2
    result = lint_file(Path(argv[1]))
    print(json.dumps(result, indent=2))
    return 0  # continuity law: lint failure never blocks the lane


if __name__ == "__main__":
    sys.exit(main(sys.argv))
