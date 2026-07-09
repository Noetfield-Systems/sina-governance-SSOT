#!/usr/bin/env python3
"""AUDIT_RECEIPT_LEDGER_v1 — scan receipts/ for anomalies that look like a
duplicate-motor / dual-ownership claim rather than a normal proof trail.

This does not replace human judgment about which receipt is "correct" — it
surfaces the same class of collision the pr-conflict-resolver skill was built
to catch during a merge (two motors claiming the same task cell), except this
scan runs on a single checked-out tree, not during a merge. A finding here
means: go look at these specific files before trusting either of them.

Checks:
  1. Malformed JSON        -- a receipt that can't be parsed is not proof of anything.
  2. Missing timestamp     -- no recognizable "at"/"timestamp"/"saved_at" field.
  3. Near-simultaneous receipts with different task identity
                           -- two+ receipts within CLUSTER_WINDOW_SECONDS of each
                              other whose filenames don't obviously match, which
                              is either coincidence or two motors firing at once.
  4. Duplicate basename stem across different top-level receipt dirs
                           -- same logical receipt name appearing more than once,
                              which is how the eval2 collision scenario looked.

Usage:
    python3 scripts/audit_receipt_ledger_v1.py [--json] [--write-receipt]

Exit code is always 0 -- this is an audit, not a gate. Pair it with human
review or with registry-motor-validator for anything that should block.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIRS = [ROOT / "receipts"]
CLUSTER_WINDOW_SECONDS = 5
TIMESTAMP_KEYS = ("at", "timestamp", "saved_at", "locked_at", "created_at", "wired_at")
TS_IN_NAME_RE = re.compile(r"(\d{8}T\d{6}Z)")
DATE_IN_NAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_ts(value: str) -> datetime | None:
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y%m%dT%H%M%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def find_timestamp(data: dict, filename: str) -> tuple[datetime | None, bool]:
    """Returns (timestamp, precise). precise=False means date-only resolution
    (no time component), so second-level clustering checks aren't meaningful
    for it -- it's still a real date, just coarse."""
    for key in TIMESTAMP_KEYS:
        v = data.get(key) if isinstance(data, dict) else None
        if isinstance(v, str):
            ts = parse_ts(v)
            if ts:
                return ts, True
    m = TS_IN_NAME_RE.search(filename)
    if m:
        ts = parse_ts(m.group(1))
        if ts:
            return ts, True
    m = DATE_IN_NAME_RE.search(filename)
    if m:
        ts = parse_ts(m.group(1))
        if ts:
            return ts, False
    return None, False


def stem_without_timestamp(filename: str) -> str:
    return TS_IN_NAME_RE.sub("<TS>", filename)


def collect_receipts() -> list[Path]:
    files: list[Path] = []
    for d in RECEIPT_DIRS:
        if d.is_dir():
            files.extend(sorted(p for p in d.glob("*.json") if p.is_file()))
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    args = parser.parse_args()

    files = collect_receipts()
    malformed: list[dict] = []
    missing_ts: list[dict] = []
    parsed: list[tuple[Path, dict, datetime]] = []
    stem_map: dict[str, list[str]] = {}

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            malformed.append({"file": str(f.relative_to(ROOT)), "error": str(e)})
            continue
        ts, precise = find_timestamp(data if isinstance(data, dict) else {}, f.name)
        if ts is None:
            missing_ts.append({"file": str(f.relative_to(ROOT))})
            continue
        stem_map.setdefault(stem_without_timestamp(f.name), []).append(str(f.relative_to(ROOT)))
        if not precise:
            continue  # date-only resolution isn't meaningful for second-level clustering
        parsed.append((f, data, ts))

    parsed.sort(key=lambda t: t[2])
    clusters: list[dict] = []
    i = 0
    while i < len(parsed):
        group = [parsed[i]]
        j = i + 1
        while j < len(parsed) and (parsed[j][2] - group[-1][2]).total_seconds() <= CLUSTER_WINDOW_SECONDS:
            group.append(parsed[j])
            j += 1
        if len(group) > 1:
            names = {stem_without_timestamp(g[0].name) for g in group}
            if len(names) > 1:
                clusters.append({
                    "window_start": group[0][2].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "window_end": group[-1][2].strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "files": [str(g[0].relative_to(ROOT)) for g in group],
                    "note": "Different receipt types clustered within "
                            f"{CLUSTER_WINDOW_SECONDS}s of each other -- verify these "
                            "aren't two motors racing on the same task cell.",
                })
        i = j

    # Receipt "families" (same stem, recurring motor) are normal and expected --
    # a cron/loop motor produces many receipts of the same shape over time.
    # Only surface a family here for visibility; it is NOT a finding on its own.
    receipt_families = {k: v for k, v in stem_map.items() if len(v) > 1}

    result = {
        "schema": "receipt_ledger_audit_v1",
        "at": utc_now(),
        "receipts_scanned": len(files),
        "malformed_count": len(malformed),
        "missing_timestamp_count": len(missing_ts),
        "cluster_count": len(clusters),
        "receipt_family_count": len(receipt_families),
        "malformed": malformed,
        "missing_timestamp": missing_ts,
        "clusters": clusters,
        "receipt_families_informational": receipt_families,
        "ok": not malformed and not clusters,
    }

    if args.write_receipt:
        out = ROOT / "receipts" / f"receipt-ledger-audit-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_id"] = out.stem

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"audit_receipt_ledger_v1: scanned {result['receipts_scanned']} receipts")
        print(f"  malformed: {result['malformed_count']}, missing_timestamp: {result['missing_timestamp_count']}, "
              f"clusters: {result['cluster_count']} (receipt_families, informational: {result['receipt_family_count']})")
        if result["ok"]:
            print("audit_receipt_ledger_v1: CLEAN")
        else:
            print("audit_receipt_ledger_v1: FINDINGS -- review before trusting affected receipts")

    return 0


if __name__ == "__main__":
    sys.exit(main())
