#!/usr/bin/env python3
"""DAILY_COST_SENTINEL_v1 — doctrine #133 (the audit's #1 ranked gap, unlock 5).

The system spends money through agents every day but has never summed what it
spent. This sentinel is the explicit currency the whole cost-governance cluster
(doctrine #109/#132/#134/#142/#143) depends on. Deterministic, stdlib-only,
no LLM, no network.

What it does, once per day (or on demand):
  1. Scans the unified receipt corpus (receipts/ + language_gate/receipts/,
     recursive — same corpus as audit_receipt_ledger_unified_v1).
  2. Collects every receipt dated the target day and extracts real cost
     signals: cost blocks (total_usd / tokens_in / tokens_out / model /
     provider) and est_cost_usd fields.
  3. Emits the doctrine #133 field set: total spend, spend by store, by model,
     by provider, retry cost, failed-job cost, top-5 most expensive receipts.
  4. Reports METERING COVERAGE honestly: how many of the day's receipts carry
     no cost data at all. Zeros are reported as zeros — this sentinel makes
     the blindness visible; it never invents numbers (doctrine #107 note).
  5. Accumulates month-to-date spend and checks it against the founder cap
     (P0_DISPATCH_ROUTER_RULES_v1.md: <= $1,500/month before revenue >=
     $10k/month) — the #109 enforcement building block. Over cap -> exit 2
     so any caller can gate on it.
  6. Writes receipts/cost/DAILY_COST_SENTINEL_<date>.json and regenerates
     docs/DAILY_COST_SENTINEL_LATEST.md (machine-generated view, doctrine #128).

Usage:
    python3 scripts/daily_cost_sentinel_v1.py [--date YYYY-MM-DD] [--dry-run]
    python3 scripts/daily_cost_sentinel_v1.py --self-test

Exit codes: 0 = ok. 2 = month-to-date spend over founder cap. 3 = malformed args.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_TOPS = [ROOT / "receipts", ROOT / "language_gate" / "receipts"]
OUT_DIR = ROOT / "receipts" / "cost"
DOC_VIEW = ROOT / "docs" / "DAILY_COST_SENTINEL_LATEST.md"

# Founder cap law: p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md line 58.
MONTHLY_CAP_PRE_REVENUE_USD = 1500.0

TIMESTAMP_KEYS = ("at", "timestamp", "saved_at", "locked_at", "created_at",
                  "wired_at", "resolved_at", "checked_at", "commissioned_at")
TS_IN_NAME_RE = re.compile(r"(\d{8}T\d{6}Z)")
DATE_IN_NAME_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
FAIL_TOKENS = ("FAIL", "HARD_BLOCK", "BLOCKED", "DEAD_LETTER")
RETRY_TOKENS = ("NEEDS_RETRY", "RETRY")


def parse_ts(value: str):
    for fmt in ("%Y-%m-%dT%H:%M:%SZ", "%Y%m%dT%H%M%SZ", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def receipt_date(data, path: Path):
    """Date resolution mirrors audit_receipt_ledger_v1: explicit keys first,
    then filename stamp, then date-only filename."""
    if isinstance(data, dict):
        for key in TIMESTAMP_KEYS:
            v = data.get(key)
            if isinstance(v, str):
                ts = parse_ts(v)
                if ts:
                    return ts.date()
    m = TS_IN_NAME_RE.search(path.name)
    if m:
        ts = parse_ts(m.group(1))
        if ts:
            return ts.date()
    m = DATE_IN_NAME_RE.search(path.name)
    if m:
        ts = parse_ts(m.group(1))
        if ts:
            return ts.date()
    return None


def extract_cost(data):
    """Walk a receipt and pull real cost signals.

    Accounting rule (stated on every sentinel receipt): usd = sum of all
    numeric total_usd fields; if a receipt has NO total_usd anywhere, fall
    back to sum of numeric est_cost_usd. Never both — avoids double count.
    Tokens/models/providers are taken from cost blocks only.
    """
    total_usd, est_usd, tokens_in, tokens_out = 0.0, 0.0, 0, 0
    models, providers = {}, {}
    has_cost_field = False

    def walk(o):
        nonlocal total_usd, est_usd, tokens_in, tokens_out, has_cost_field
        if isinstance(o, dict):
            tu = o.get("total_usd")
            if isinstance(tu, (int, float)):
                has_cost_field = True
                total_usd += float(tu)
                model = o.get("model") if isinstance(o.get("model"), str) else "unknown"
                provider = o.get("provider") if isinstance(o.get("provider"), str) else "unknown"
                models[model] = models.get(model, 0.0) + float(tu)
                providers[provider] = providers.get(provider, 0.0) + float(tu)
                for key, bucket in (("tokens_in", "in"), ("tokens_out", "out")):
                    tv = o.get(key)
                    if isinstance(tv, (int, float)):
                        if bucket == "in":
                            tokens_in += int(tv)
                        else:
                            tokens_out += int(tv)
            ec = o.get("est_cost_usd")
            if isinstance(ec, (int, float)):
                has_cost_field = True
                est_usd += float(ec)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(data)
    usd = total_usd if total_usd > 0 or (has_cost_field and est_usd == 0) else est_usd
    return {"usd": round(usd, 6), "tokens_in": tokens_in, "tokens_out": tokens_out,
            "models": models, "providers": providers, "metered": has_cost_field}


def classify(data):
    blob = json.dumps(data)[:20000].upper() if isinstance(data, (dict, list)) else ""
    failed = any(t in blob for t in FAIL_TOKENS)
    retry = any(t in blob for t in RETRY_TOKENS)
    return failed, retry


def collect(corpus_tops, day):
    """Returns (day_rows, month_usd). One row per receipt dated `day`."""
    rows, month_usd = [], 0.0
    month_key = (day.year, day.month)
    for top in corpus_tops:
        if not top.is_dir():
            continue
        for p in sorted(top.rglob("*.json")):
            try:
                data = json.loads(p.read_text())
            except (OSError, ValueError):
                continue
            d = receipt_date(data, p)
            if d is None:
                continue
            cost = extract_cost(data)
            if (d.year, d.month) == month_key and cost["metered"]:
                month_usd += cost["usd"]
            if d != day:
                continue
            failed, retry = classify(data)
            try:
                store = str(p.relative_to(ROOT)).split("/")[0:2]
                store = "/".join(store[:-1]) if len(store) > 1 else store[0]
            except ValueError:
                store = str(p.parent.name)
            rows.append({"path": str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
                         "store": store, "usd": cost["usd"], "tokens_in": cost["tokens_in"],
                         "tokens_out": cost["tokens_out"], "models": cost["models"],
                         "providers": cost["providers"], "metered": cost["metered"],
                         "failed": failed, "retry": retry})
    return rows, round(month_usd, 6)


def summarize(rows, day, month_usd):
    def agg(key):
        out = {}
        for r in rows:
            for name, usd in r[key].items():
                out[name] = round(out.get(name, 0.0) + usd, 6)
        return dict(sorted(out.items(), key=lambda kv: -kv[1]))

    by_store = {}
    for r in rows:
        if r["metered"]:
            by_store[r["store"]] = round(by_store.get(r["store"], 0.0) + r["usd"], 6)

    metered = [r for r in rows if r["metered"]]
    total = round(sum(r["usd"] for r in metered), 6)
    top5 = sorted(metered, key=lambda r: -r["usd"])[:5]
    over_cap = month_usd > MONTHLY_CAP_PRE_REVENUE_USD
    return {
        "schema": "daily_cost_sentinel_v1",
        "doctrine": "#133 (daily cost sentinel) + #109 building block (monthly accumulator vs founder cap)",
        "law": ["docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md",
                "p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md (monthly cap)"],
        "date": day.isoformat(),
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "accounting_rule": "usd per receipt = sum(total_usd); fallback sum(est_cost_usd) only when no total_usd. Zeros reported as zeros — no invented numbers.",
        "totals": {
            "spend_usd": total,
            "tokens_in": sum(r["tokens_in"] for r in metered),
            "tokens_out": sum(r["tokens_out"] for r in metered),
            "receipts_today": len(rows),
            "receipts_metered": len(metered),
            "receipts_unmetered": len(rows) - len(metered),
            "metering_coverage_pct": round(100.0 * len(metered) / len(rows), 1) if rows else 0.0,
        },
        "by_store": by_store,
        "by_model": agg("models"),
        "by_provider": agg("providers"),
        "retry_cost_usd": round(sum(r["usd"] for r in metered if r["retry"]), 6),
        "failed_job_cost_usd": round(sum(r["usd"] for r in metered if r["failed"]), 6),
        "top_5_expensive": [{"path": r["path"], "usd": r["usd"]} for r in top5],
        "month_to_date": {
            "spend_usd": month_usd,
            "cap_usd": MONTHLY_CAP_PRE_REVENUE_USD,
            "cap_basis": "pre-revenue cap; revisit at revenue >= $10k/month per router rules",
            "remaining_usd": round(MONTHLY_CAP_PRE_REVENUE_USD - month_usd, 6),
            "over_cap": over_cap,
        },
        "blindness_note": ("METERING GAP: most receipts carry zero/no cost data (doctrine #107 is PARTIAL — "
                           "upstream token metering is the keystone fix). This sentinel reports what exists; "
                           "coverage % above is the honest measure of how blind the system still is."),
    }


def render_view(report):
    lines = [
        "<!-- GENERATED from receipts/cost/DAILY_COST_SENTINEL_%s.json — do not hand-edit (doctrine #128) -->" % report["date"],
        "# Daily Cost Sentinel — %s" % report["date"],
        "",
        "**Spend today:** $%s across %d metered receipts (%d receipts total, %.1f%% metering coverage)" % (
            report["totals"]["spend_usd"], report["totals"]["receipts_metered"],
            report["totals"]["receipts_today"], report["totals"]["metering_coverage_pct"]),
        "**Month to date:** $%s of $%s cap — $%s remaining%s" % (
            report["month_to_date"]["spend_usd"], report["month_to_date"]["cap_usd"],
            report["month_to_date"]["remaining_usd"],
            " — **OVER CAP**" if report["month_to_date"]["over_cap"] else ""),
        "**Retry cost:** $%s · **Failed-job cost:** $%s" % (report["retry_cost_usd"], report["failed_job_cost_usd"]),
        "",
    ]
    for title, key in (("By store", "by_store"), ("By model", "by_model"), ("By provider", "by_provider")):
        if report[key]:
            lines.append("## %s" % title)
            for name, usd in report[key].items():
                lines.append("- %s: $%s" % (name, usd))
            lines.append("")
    if report["top_5_expensive"]:
        lines.append("## Top 5 expensive receipts")
        for r in report["top_5_expensive"]:
            lines.append("- $%s — `%s`" % (r["usd"], r["path"]))
        lines.append("")
    lines.append("> %s" % report["blindness_note"])
    return "\n".join(lines) + "\n"


def self_test():
    day = datetime(2026, 7, 23, tzinfo=timezone.utc).date()
    with tempfile.TemporaryDirectory() as td:
        top = Path(td) / "receipts"
        (top / "p0pgr").mkdir(parents=True)
        (top / "app").mkdir()
        # Metered receipt with a real cost block.
        (top / "p0pgr" / "A-20260723T010000Z.json").write_text(json.dumps(
            {"at": "2026-07-23T01:00:00Z",
             "cost": {"model": "m1", "provider": "p1", "tokens_in": 100, "tokens_out": 50, "total_usd": 1.25}}))
        # Metered est-only receipt, also a failed retry.
        (top / "app" / "B-20260723T020000Z.json").write_text(json.dumps(
            {"saved_at": "2026-07-23T02:00:00Z", "status": "NEEDS_RETRY_after_FAIL", "est_cost_usd": 0.5}))
        # Unmetered receipt (the blindness case).
        (top / "app" / "C-20260723T030000Z.json").write_text(json.dumps(
            {"saved_at": "2026-07-23T03:00:00Z", "note": "no cost fields"}))
        # Same month, different day -> month accumulator only.
        (top / "app" / "D-20260701T010000Z.json").write_text(json.dumps(
            {"saved_at": "2026-07-01T01:00:00Z", "cost": {"total_usd": 2.0}}))
        # Different month -> ignored everywhere.
        (top / "app" / "E-20260601T010000Z.json").write_text(json.dumps(
            {"saved_at": "2026-06-01T01:00:00Z", "cost": {"total_usd": 99.0}}))

        rows, month_usd = collect([top], day)
        report = summarize(rows, day, month_usd)

        checks = [
            ("3 receipts found for the day", report["totals"]["receipts_today"] == 3),
            ("2 metered / 1 unmetered", report["totals"]["receipts_metered"] == 2
             and report["totals"]["receipts_unmetered"] == 1),
            ("day spend = 1.75", abs(report["totals"]["spend_usd"] - 1.75) < 1e-9),
            ("month-to-date = 3.75 (excludes June)", abs(report["month_to_date"]["spend_usd"] - 3.75) < 1e-9),
            ("by_model captures m1=1.25", abs(report["by_model"].get("m1", 0) - 1.25) < 1e-9),
            ("retry+failed cost = 0.5", abs(report["retry_cost_usd"] - 0.5) < 1e-9
             and abs(report["failed_job_cost_usd"] - 0.5) < 1e-9),
            ("under cap", report["month_to_date"]["over_cap"] is False),
            ("view renders", report["date"] in render_view(report)),
        ]
        failures = 0
        for name, ok in checks:
            failures += 0 if ok else 1
            print("%s %s" % ("PASS" if ok else "FAIL", name))
        print("self-test: %d/%d passed" % (len(checks) - failures, len(checks)))
        return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(description="Daily cost sentinel (doctrine #133)")
    ap.add_argument("--date", help="UTC day to report, YYYY-MM-DD (default: today)")
    ap.add_argument("--dry-run", action="store_true", help="print report, write nothing")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())

    if args.date:
        ts = parse_ts(args.date)
        if not ts:
            print("MALFORMED --date, expected YYYY-MM-DD")
            sys.exit(3)
        day = ts.date()
    else:
        day = datetime.now(timezone.utc).date()

    rows, month_usd = collect(CORPUS_TOPS, day)
    report = summarize(rows, day, month_usd)
    print(json.dumps(report, indent=2))

    if not args.dry_run:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = OUT_DIR / ("DAILY_COST_SENTINEL_%s.json" % day.isoformat())
        out.write_text(json.dumps(report, indent=2) + "\n")
        DOC_VIEW.parent.mkdir(parents=True, exist_ok=True)
        DOC_VIEW.write_text(render_view(report))
        print("wrote: %s" % out.relative_to(ROOT))
        print("wrote: %s" % DOC_VIEW.relative_to(ROOT))

    sys.exit(2 if report["month_to_date"]["over_cap"] else 0)


if __name__ == "__main__":
    main()
