#!/usr/bin/env python3
"""P0-PGR evidence reader — deterministic digest of all runtime receipts. Read-only."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECEIPTS = ROOT / "receipts" / "p0pgr"


def digest(receipts_dir: Path = DEFAULT_RECEIPTS) -> dict:
    entries = []
    if receipts_dir.is_dir():
        for path in sorted(receipts_dir.rglob("*.json")):
            try:
                data = json.loads(path.read_text())
            except (json.JSONDecodeError, OSError) as exc:
                entries.append({"path": str(path.relative_to(ROOT)), "error": str(exc)})
                continue
            entries.append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "schema": data.get("schema"),
                    "id": data.get("receipt_id") or data.get("cycle_id") or data.get("packet_id") or data.get("campaign_id"),
                    "verdict": data.get("verdict") or data.get("quality_state") or data.get("status"),
                    "recorded_at": data.get("recorded_at") or data.get("created_at"),
                }
            )
    return {"schema": "p0pgr_evidence_digest_v1", "receipts_dir": str(receipts_dir), "count": len(entries), "entries": entries}


def main() -> int:
    receipts_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_RECEIPTS
    print(json.dumps(digest(receipts_dir), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
