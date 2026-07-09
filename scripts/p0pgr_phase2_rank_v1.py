#!/usr/bin/env python3
"""P0-PGR Phase 2 ROI ranker — deterministic queue. Weights: 35 revenue / 25 trust / 15 workload / 15 cloud-now / 10 reversibility."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_packet_lint_v1 import utc_now_iso  # noqa: E402

DEFAULT_RECEIPTS = ROOT / "receipts" / "p0pgr"

WEIGHTS = {"revenue": 35, "trust": 25, "workload_relief": 15, "cloud_now": 15, "reversibility": 10}


def score_packet(packet: dict) -> float:
    roi = packet.get("roi", {})
    total = 0.0
    for field, weight in WEIGHTS.items():
        value = roi.get(field, 0)
        if isinstance(value, (int, float)):
            total += weight * (max(0.0, min(5.0, float(value))) / 5.0)
    return round(total, 1)


def rank(receipts_dir: Path = DEFAULT_RECEIPTS) -> dict:
    outbox = receipts_dir / "outbox"
    rows = []
    if outbox.is_dir():
        for path in sorted(outbox.glob("*.json")):
            try:
                packet = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError):
                continue
            if packet.get("status") in ("DONE", "KILLED"):
                continue
            rows.append(
                {
                    "packet_id": packet.get("packet_id", path.stem),
                    "score": score_packet(packet),
                    "route": packet.get("route"),
                    "status": packet.get("status"),
                    "mission": packet.get("mission", ""),
                    "path": str(path.relative_to(ROOT)),
                }
            )
    rows.sort(key=lambda r: (-r["score"], r["packet_id"]))
    for i, row in enumerate(rows, 1):
        row["rank"] = i
    queue = {
        "schema": "p0pgr_phase2_queue_v1",
        "generated_at": utc_now_iso(),
        "weights": WEIGHTS,
        "queue": rows,
        "next_move": rows[0]["packet_id"] if rows else None,
    }
    receipts_dir.mkdir(parents=True, exist_ok=True)
    (receipts_dir / "phase2_queue_v1.json").write_text(json.dumps(queue, indent=2) + "\n")
    return queue


def main() -> int:
    print(json.dumps(rank(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
