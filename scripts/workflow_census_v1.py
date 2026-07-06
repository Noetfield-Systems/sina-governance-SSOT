#!/usr/bin/env python3
"""WORKFLOW_CENSUS_v1 — crawl motors, classify by receipt served, write Supabase + receipt.

Judging layer: which receipt does this loop serve? (UNLOCK / architect dispatch 2026-07-06)
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data" / "automation_surface_inventory_v1.json"
RULES = ROOT / "data" / "workflow_census_value_class_rules_v1.json"
EXTENSIONS = ROOT / "data" / "workflow_census_extensions_v1.json"
RECEIPTS = ROOT / "receipts"
NOETFIELD_ENV = Path.home() / ".sourcea-secrets" / "noetfield.env"
GATEWAY_ENV = Path.home() / ".sourcea-secrets" / "sina-gateway.env"

REPO_PATH_CANDIDATES = {
    "sina-governance-ssot": [
        ROOT,
        Path.home() / "Projects/sina-governance-ssot",
        Path.home() / "Desktop/Noetfield-Systems/sina-governance-SSOT",
    ],
    "SourceA": [
        Path.home() / "Projects/SourceA",
        Path.home() / "Projects/noetfield-systems_sourcea",
        Path.home() / "Desktop/Noetfield-Systems/SourceA",
    ],
    "noetfeld-os": [
        Path.home() / "Projects/noetfeld-os",
        Path.home() / "Desktop/Noetfield-Systems/noetfeld-os",
    ],
    "trustfield-loops": [
        Path.home() / "Desktop/trustfield-loops",
        Path.home() / "Projects/trustfield-loops",
    ],
}

GH_REPO_MAP = {
    "sina-governance-ssot": "Noetfield-Systems/sina-governance-SSOT",
    "SourceA": "Noetfield-Systems/SourceA",
    "noetfeld-os": "Noetfield-Systems/noetfeld-os",
    "trustfield-loops": "Noetfield-Systems/trustfield-loops",
    "sina-gateway": "kazemnezhadsina144-dot/sina-gateway",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_env_file(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    vals: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        vals[k.strip()] = v.strip().strip("'").strip('"')
    return vals


def resolve_supabase_cred() -> tuple[str, str] | None:
    vals = load_env_file(NOETFIELD_ENV)
    url = vals.get("NOETFIELD_SUPABASE_URL") or vals.get("SUPABASE_URL") or os.environ.get("NOETFIELD_SUPABASE_URL", "")
    key = (
        vals.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY")
        or vals.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "")
    )
    if url and key:
        return url.rstrip("/"), key
    return None


def estimate_invocations_from_cadence(cadence: str) -> float | None:
    if not cadence or cadence in ("on_push", "manual_dispatch", "on_tag_push", "workflow_run_after_deploy", "on_push_paths", "disabled_intentional", "always_on", "request", "webhook_request", "daily_snapshot"):
        return None
    if cadence.endswith("s") and cadence[:-1].isdigit():
        secs = int(cadence[:-1])
        return round(86400 / secs, 1) if secs else None
    # */N minute patterns
    m = re.match(r"\*/(\d+)", cadence.replace(" ", ""))
    if m:
        mins = int(m.group(1))
        return round(1440 / mins, 1)
    # comma-separated minute lists e.g. 0,10,20,30,40,50 * * * *
    parts = cadence.split()
    if parts and "," in parts[0]:
        return float(len(parts[0].split(",")))
    # hourly
    if parts and parts[0].startswith("0") and len(parts) > 1 and parts[1] == "*":
        if parts[0] == "0":
            return 24.0
        if "/" in parts[1]:
            hm = re.match(r"\*/(\d+)", parts[1])
            if hm:
                return round(24 / int(hm.group(1)), 1)
    return None


def classify(task_cell: str, loop_id: str, rules: dict) -> tuple[str, str]:
    by_cell = rules.get("by_task_cell", {})
    if task_cell in by_cell:
        row = by_cell[task_cell]
        return row["value_class"], row["receipt_target"]
    hay = f"{loop_id} {task_cell}".lower()
    for pat in rules.get("by_id_pattern", []):
        if re.search(pat["match"], hay, re.I):
            return pat["value_class"], pat.get("receipt_target", rules["default"]["receipt_target"])
    default = rules["default"]
    return default["value_class"], default["receipt_target"]


def cost_for_host(host: str, cost_tier: str | None, rules: dict) -> float:
    costs = rules.get("cost_usd_month", {})
    if cost_tier and cost_tier in costs:
        return float(costs[cost_tier])
    if host == "github":
        return float(costs.get("github_actions", 0))
    if host == "cloudflare":
        return float(costs.get("cloudflare_workers_paid", 5))
    if host == "railway":
        return float(costs.get("railway_hobby", 5))
    return 0.0


def gh_runs_24h(repo_slug: str, workflow_file: str) -> tuple[int | None, str | None]:
    if not repo_slug or not workflow_file:
        return None, None
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        out = subprocess.check_output(
            [
                "gh", "run", "list",
                "--repo", repo_slug,
                "--workflow", workflow_file,
                "--limit", "100",
                "--json", "databaseId,conclusion,createdAt,updatedAt",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
        rows = json.loads(out)
        recent = [r for r in rows if (r.get("createdAt") or "") >= since]
        last_at = rows[0].get("updatedAt") if rows else None
        return len(recent), last_at
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return None, None


def supabase_get(base: str, key: str, path: str) -> list | dict | None:
    req = urllib.request.Request(
        f"{base}/rest/v1/{path}",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError):
        return None


def supabase_upsert_rows(base: str, key: str, table: str, rows: list[dict]) -> bool:
    if not rows:
        return True
    body = json.dumps(rows).encode("utf-8")
    req = urllib.request.Request(
        f"{base}/rest/v1/{table}",
        data=body,
        method="POST",
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates,return=minimal",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return 200 <= resp.status < 300
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")[:300]
        print(f"supabase upsert {table} failed: {exc.code} {err}", file=sys.stderr)
        return False


def fetch_factory_last_receipts(base: str, key: str) -> dict[str, dict]:
    rows = supabase_get(
        base,
        key,
        "noetfield_factory_cycle_runs?select=factory_id,recorded_at,id&order=recorded_at.desc&limit=200",
    )
    out: dict[str, dict] = {}
    if not isinstance(rows, list):
        return out
    for row in rows:
        fid = row.get("factory_id")
        if fid and fid not in out:
            out[fid] = {"last_receipt_at": row.get("recorded_at"), "last_receipt_id": str(row.get("id", ""))}
    return out


def fetch_gateway_leads_stats(base: str, key: str) -> dict:
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).strftime("%Y-%m-%dT%H:%M:%SZ")
    total = supabase_get(base, key, "gateway_leads?select=id&is_test=eq.false&limit=1")
    recent = supabase_get(
        base,
        key,
        f"gateway_leads?select=id,created_at&is_test=eq.false&created_at=gte.{since}&order=created_at.desc",
    )
    recent_count = len(recent) if isinstance(recent, list) else 0
    latest_at = recent[0].get("created_at") if isinstance(recent, list) and recent else None
    return {
        "non_test_leads_total": "unknown" if total is None else "present",
        "non_test_leads_24h": recent_count,
        "last_lead_at": latest_at,
    }


def collect_inventory_loops(inv: dict) -> list[dict]:
    loops: list[dict] = []
    for repo in inv.get("repos", []):
        repo_id = repo.get("repo_id", "")
        for wf in repo.get("workflows", []):
            loops.append(
                {
                    "loop_id": wf.get("motor_id") or f"gh_{repo_id}_{wf.get('file', '').replace('.yml', '')}",
                    "name": wf.get("file", "").replace(".yml", ""),
                    "host": "github",
                    "repo_id": repo_id,
                    "workflow_file": wf.get("file"),
                    "schedule": wf.get("cadence", "unknown"),
                    "task_cell": wf.get("task_cell", ""),
                    "cost_tier": "github_actions",
                }
            )
        for cm in repo.get("cloud_motors", []):
            loops.append(
                {
                    "loop_id": cm.get("motor_id", ""),
                    "name": cm.get("motor_id", ""),
                    "host": "cloudflare",
                    "repo_id": repo_id,
                    "schedule": cm.get("cadence", "unknown"),
                    "task_cell": cm.get("task_cell", ""),
                    "health_url": cm.get("health_url") or cm.get("health_path"),
                    "cost_tier": "cloudflare_workers_paid",
                }
            )
        for mm in repo.get("mac_motors", []):
            loops.append(
                {
                    "loop_id": mm.get("id", ""),
                    "name": mm.get("id", ""),
                    "host": "mac",
                    "repo_id": repo_id,
                    "schedule": mm.get("cadence", "unknown"),
                    "task_cell": mm.get("task_cell", ""),
                    "cost_tier": "mac_launchd",
                }
            )
    return loops


def collect_extension_loops(ext: dict) -> list[dict]:
    loops: list[dict] = []
    for cm in ext.get("cloudflare_workers", []):
        loops.append({**cm, "repo_id": cm.get("repo", "sina-gateway")})
    for rs in ext.get("railway_services", []):
        loops.append({**rs, "repo_id": rs.get("repo", "sina-gateway")})
    for wf in ext.get("github_workflows", []):
        loops.append(
            {
                **wf,
                "repo_id": wf.get("repo", "sina-gateway").split("/")[-1],
                "workflow_file": wf.get("workflow_file"),
            }
        )
    for tp in ext.get("traffic_probes", []):
        loops.append({**tp, "repo_id": "traffic"})
    return loops


def enrich_loop(loop: dict, rules: dict, factory_receipts: dict[str, dict], gh_cache: dict) -> dict:
    task_cell = loop.get("task_cell", "")
    loop_id = loop.get("loop_id", "")
    value_class, receipt_target = classify(task_cell, loop_id, rules)
    if loop.get("receipt_target"):
        receipt_target = loop["receipt_target"]

    host = loop.get("host", "github")
    inv_day = estimate_invocations_from_cadence(loop.get("schedule", ""))
    last_receipt_at = None
    last_receipt_id = None

    wf = loop.get("workflow_file")
    repo_id = loop.get("repo_id", "")
    gh_slug = GH_REPO_MAP.get(repo_id) or loop.get("repo")
    cache_key = f"{gh_slug}:{wf}"
    if host == "github" and wf:
        if cache_key not in gh_cache:
            gh_cache[cache_key] = gh_runs_24h(gh_slug, wf)
        runs_24h, last_at = gh_cache[cache_key]
        if runs_24h is not None:
            inv_day = float(runs_24h)
        if last_at:
            last_receipt_at = last_at

    # Map NOOS factory loops
    for fid, rec in factory_receipts.items():
        if fid in loop_id or fid.replace("loop-", "") in loop_id:
            last_receipt_at = rec.get("last_receipt_at") or last_receipt_at
            last_receipt_id = rec.get("last_receipt_id") or last_receipt_id

    if loop_id == "railway_sina_gateway_v1" and factory_receipts.get("gateway"):
        pass  # filled below via gateway stats

    cost = cost_for_host(host, loop.get("cost_tier"), rules)

    return {
        "loop_id": loop_id,
        "name": loop.get("name", loop_id),
        "host": host,
        "schedule": loop.get("schedule"),
        "invocations_per_day": inv_day,
        "cost_usd_month": cost,
        "last_receipt_at": last_receipt_at,
        "last_receipt_id": last_receipt_id,
        "receipt_target": receipt_target,
        "value_class": value_class,
        "metadata": {
            "repo_id": repo_id,
            "task_cell": task_cell,
            "workflow_file": wf,
            "health_url": loop.get("health_url"),
        },
    }


def apply_standing_audit(loops: list[dict], rules: dict, ext: dict) -> tuple[list[dict], str]:
    flags: list[dict] = []
    stale_days = int(rules.get("none_stale_days", 14))
    now = datetime.now(timezone.utc)
    skip_none_demote = {"gh_actions_workflow_census_weekly_v1", "traffic_www_intake_conversion_v1"}

    revenue = [l for l in loops if l["value_class"] == "REVENUE"]
    guard = [l for l in loops if l["value_class"] == "GUARD"]
    meta = [l for l in loops if l["value_class"] == "META"]

    rev_cost = sum(l.get("cost_usd_month") or 0 for l in revenue)
    guard_cost = sum(l.get("cost_usd_month") or 0 for l in guard)
    meta_cost = sum(l.get("cost_usd_month") or 0 for l in meta)

    for loop in loops:
        if not loop.get("receipt_target"):
            flags.append({"rule": 3, "loop_id": loop["loop_id"], "message": "missing receipt_target"})
        ts = loop.get("last_receipt_at")
        vc = loop.get("value_class")
        if ts:
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if (now - dt).days >= stale_days and vc != "REVENUE":
                    loop["value_class"] = "NONE"
                    flags.append({"rule": 1, "loop_id": loop["loop_id"], "message": f"no receipt in {stale_days}d — propose retirement"})
            except ValueError:
                pass
        elif vc not in ("REVENUE",) and loop["loop_id"] not in skip_none_demote:
            loop["value_class"] = "NONE"
            flags.append({"rule": 1, "loop_id": loop["loop_id"], "message": "never produced receipt — NONE"})

    required_cells = set(ext.get("revenue_motors_required", []))
    present_cells = {l.get("metadata", {}).get("task_cell") for l in loops if l["value_class"] == "REVENUE"}
    missing_revenue = required_cells - present_cells
    if missing_revenue:
        flags.append({"rule": 4, "message": f"REVENUE motors missing: {sorted(missing_revenue)}"})

    stale_revenue = [
        l["loop_id"]
        for l in loops
        if l["value_class"] == "REVENUE"
        and not l.get("last_receipt_at")
        and l.get("loop_id") != "traffic_www_intake_conversion_v1"
    ]
    if stale_revenue:
        flags.append({"rule": 4, "message": f"REVENUE loops with zero receipts: {stale_revenue}"})

    if meta_cost > (guard_cost + rev_cost):
        flags.append(
            {
                "rule": 2,
                "message": f"META cost ${meta_cost:.2f}/mo > GUARD+REVENUE ${guard_cost + rev_cost:.2f}/mo",
                "meta_cost": meta_cost,
                "guard_revenue_cost": guard_cost + rev_cost,
            }
        )

    status = "GREEN"
    if any(f.get("rule") in (2, 4) for f in flags):
        status = "RED"
    elif flags:
        status = "YELLOW"

    return flags, status


def main() -> int:
    ap = argparse.ArgumentParser(description="WORKFLOW_CENSUS_v1")
    ap.add_argument("--write-supabase", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--traffic-visits-24h", type=float, default=0, help="Optional CF/www visits snapshot")
    args = ap.parse_args()

    for path in (INVENTORY, RULES, EXTENSIONS):
        if not path.is_file():
            print(f"workflow_census_v1: missing {path}", file=sys.stderr)
            return 1

    inv = load_json(INVENTORY)
    rules = load_json(RULES)
    ext = load_json(EXTENSIONS)

    run_id = f"workflow-census-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    raw_loops = collect_inventory_loops(inv) + collect_extension_loops(ext)

    cred = resolve_supabase_cred()
    factory_receipts: dict[str, dict] = {}
    gateway_stats: dict = {}
    if cred:
        base, key = cred
        factory_receipts = fetch_factory_last_receipts(base, key)
        gateway_stats = fetch_gateway_leads_stats(base, key)

    gh_cache: dict = {}
    loops = [enrich_loop(loop, rules, factory_receipts, gh_cache) for loop in raw_loops]

    # Dedupe by loop_id
    seen: set[str] = set()
    deduped: list[dict] = []
    for loop in loops:
        if loop["loop_id"] in seen:
            continue
        seen.add(loop["loop_id"])
        deduped.append(loop)
    loops = deduped

    # Enrich traffic row
    for loop in loops:
        if loop["loop_id"] == "traffic_www_intake_conversion_v1":
            visits = args.traffic_visits_24h
            leads = gateway_stats.get("non_test_leads_24h", 0)
            loop["metadata"]["visits_24h"] = visits
            loop["metadata"]["non_test_leads_24h"] = leads
            loop["metadata"]["conversion_rate"] = round(leads / visits, 6) if visits else None
            loop["last_receipt_at"] = gateway_stats.get("last_lead_at")
            if visits and leads == 0:
                loop["value_class"] = "REVENUE"
                loop["metadata"]["diagnosis"] = "traffic without intake conversion — fix funnel or bot filter"

    # Enrich gateway capture
    for loop in loops:
        if loop["loop_id"] == "railway_sina_gateway_v1":
            loop["last_receipt_at"] = gateway_stats.get("last_lead_at")
            loop["metadata"]["non_test_leads_24h"] = gateway_stats.get("non_test_leads_24h")

    audit_flags, audit_status = apply_standing_audit(loops, rules, ext)

    counts = {k: sum(1 for l in loops if l["value_class"] == k) for k in ("REVENUE", "GUARD", "META", "NONE")}
    costs = {
        k: sum(l.get("cost_usd_month") or 0 for l in loops if l["value_class"] == k)
        for k in ("REVENUE", "GUARD", "META", "NONE")
    }

    for loop in loops:
        loop["census_run_id"] = run_id

    report = {
        "schema": "workflow-census-receipt-v1",
        "run_id": run_id,
        "recorded_at": utc_now(),
        "loop_count": len(loops),
        "counts": counts,
        "costs_usd_month": costs,
        "audit_status": audit_status,
        "audit_flags": audit_flags,
        "standing_audit_rules": rules.get("standing_audit_rules", []),
        "gateway_stats": gateway_stats,
        "loops": loops,
    }

    receipt_path = None
    if args.write_receipt:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        receipt_path = RECEIPTS / f"{run_id}.json"
        receipt_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["receipt_path"] = str(receipt_path)

    if args.write_supabase:
        if not cred:
            print("workflow_census_v1: Supabase creds missing — skip write", file=sys.stderr)
        else:
            base, key = cred
            rows = [
                {
                    "loop_id": l["loop_id"],
                    "name": l["name"],
                    "host": l["host"],
                    "schedule": l.get("schedule"),
                    "invocations_per_day": l.get("invocations_per_day"),
                    "cost_usd_month": l.get("cost_usd_month"),
                    "last_receipt_at": l.get("last_receipt_at"),
                    "last_receipt_id": l.get("last_receipt_id"),
                    "receipt_target": l["receipt_target"],
                    "value_class": l["value_class"],
                    "census_run_id": run_id,
                    "metadata": l.get("metadata", {}),
                }
                for l in loops
            ]
            ok_loops = supabase_upsert_rows(base, key, "workflow_census_v1", rows)
            run_row = {
                "run_id": run_id,
                "loop_count": len(loops),
                "revenue_count": counts["REVENUE"],
                "guard_count": counts["GUARD"],
                "meta_count": counts["META"],
                "none_count": counts["NONE"],
                "revenue_cost_usd_month": costs["REVENUE"],
                "guard_cost_usd_month": costs["GUARD"],
                "meta_cost_usd_month": costs["META"],
                "audit_flags": audit_flags,
                "audit_status": audit_status,
                "receipt_path": str(receipt_path) if receipt_path else None,
                "metadata": {"gateway_stats": gateway_stats},
            }
            ok_run = supabase_upsert_rows(base, key, "workflow_census_runs_v1", [run_row])
            report["supabase_write"] = ok_loops and ok_run
            if not (ok_loops and ok_run):
                print("workflow_census_v1: Supabase write failed (apply migration first?)", file=sys.stderr)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"workflow_census_v1: {run_id}")
        print(f"  loops={len(loops)} REVENUE={counts['REVENUE']} GUARD={counts['GUARD']} META={counts['META']} NONE={counts['NONE']}")
        print(f"  costs/mo: REVENUE=${costs['REVENUE']:.2f} GUARD=${costs['GUARD']:.2f} META=${costs['META']:.2f}")
        print(f"  audit_status={audit_status}")
        for flag in audit_flags[:8]:
            print(f"  FLAG rule {flag.get('rule')}: {flag.get('message') or flag.get('loop_id')}")
        if receipt_path:
            print(f"  receipt={receipt_path}")

    return 0 if audit_status != "RED" else 2


if __name__ == "__main__":
    sys.exit(main())
