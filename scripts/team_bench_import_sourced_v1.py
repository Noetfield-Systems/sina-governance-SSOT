#!/usr/bin/env python3
"""Import SOURCED Team Bench rows into the Partner Access Platform tracker.

Reads data/team_bench_sourced_rows_v1.json and POSTs each row to
/api/partner-access/team-bench/admin (status SOURCED only — the CASL gate
lives in the API; nothing here can mark anyone CONTACTED).

Usage:
    ADMIN_TOKEN=... python3 scripts/team_bench_import_sourced_v1.py [--dry-run]
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = ROOT / "data" / "team_bench_sourced_rows_v1.json"
API = os.environ.get("TEAM_BENCH_API", "https://api.trustfield.ca")


def main() -> int:
    dry = "--dry-run" in sys.argv
    token = os.environ.get("ADMIN_TOKEN", "").strip()
    if not token and not dry:
        print("ADMIN_TOKEN env required (or use --dry-run)")
        return 2

    data = json.loads(ROWS.read_text())
    rows = data["rows"] if isinstance(data, dict) else data
    results = []
    for row in rows:
        payload = {
            "role_lane": row["role_lane"],
            "full_name": row["full_name"],
            "email": row.get("email"),
            "handle_or_link": row.get("handle_or_link"),
            "source_channel": row.get("source_channel"),
            "source_url": row.get("source_url"),
            "warm_intro_source": row.get("warm_intro_source"),
            "casl_basis": row.get("casl_basis"),
            "intended_message_type": row.get("intended_message_type"),
            "notes": row.get("fit_notes", "") + (" | risk: " + row["risk_notes"] if row.get("risk_notes") else ""),
        }
        if dry:
            results.append({"full_name": row["full_name"], "dry_run": True})
            continue
        req = urllib.request.Request(
            f"{API}/api/partner-access/team-bench/admin",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json", "X-Admin-Token": token},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                created = json.loads(resp.read().decode())
            ref = created["prospect_ref"]
            # scores go in via PATCH so the API recomputes total + flags
            scores = row.get("scores", {})
            if scores:
                patch = urllib.request.Request(
                    f"{API}/api/partner-access/team-bench/admin/{ref}",
                    data=json.dumps(scores).encode(),
                    headers={"Content-Type": "application/json", "X-Admin-Token": token},
                    method="PATCH",
                )
                with urllib.request.urlopen(patch, timeout=20) as resp:
                    created = json.loads(resp.read().decode())
            results.append({"full_name": row["full_name"], "prospect_ref": ref,
                            "total_bench_score": created.get("total_bench_score"), "status": created.get("status")})
        except Exception as exc:  # keep lane moving; report per-row
            results.append({"full_name": row["full_name"], "error": str(exc)[:160]})

    out = {
        "schema": "team_bench_import_result_v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "api": API,
        "dry_run": dry,
        "imported": sum(1 for r in results if "prospect_ref" in r),
        "errors": sum(1 for r in results if "error" in r),
        "results": results,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
