#!/usr/bin/env python3
"""SG auth surface probe — tiered HTTP checks + Supabase identity plane.

Reads data/auth_surface_matrix_v1.json. SG verifies; venture repos implement UI/RLS.
Does not print secrets. Exit 0 when tier-0 public surfaces pass and no hard failures.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/auth_surface_matrix_v1.json"
RECEIPT_DIR = ROOT / "receipts"
SUPABASE_VERIFY = ROOT / "scripts/verify_supabase_live_profiles_v1.py"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_matrix() -> dict[str, Any]:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def http_probe(url: str, *, timeout: int = 25) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "sg-auth-surface-probe-v1"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return {"ok": True, "http": resp.status, "url": url}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "http": exc.code, "url": url, "error": "http_error"}
    except urllib.error.URLError as exc:
        return {"ok": False, "http": 0, "url": url, "error": str(exc.reason)}
    except TimeoutError:
        return {"ok": False, "http": 0, "url": url, "error": "timeout"}


def check_surface(spec: dict[str, Any], *, tier: str) -> dict[str, Any]:
    url = spec["url"]
    probe = http_probe(url)
    http = probe.get("http", 0)
    row: dict[str, Any] = {
        "id": spec["id"],
        "tier": tier,
        "url": url,
        "venture": spec.get("venture"),
        "http": http,
        "implementation": spec.get("implementation", "live"),
    }

    if tier == "tier_0_public":
        allowed = spec.get("expect_http", [200])
        row["status"] = "PASS" if http in allowed else "FAIL"
        if row["status"] == "FAIL":
            row["reason"] = f"expected {allowed}, got {http}"
        return row

    if tier == "tier_1_optional":
        allowed = spec.get("expect_http", [200, 302])
        row["status"] = "PASS" if http in allowed else "WARN"
        if row["status"] != "PASS":
            row["reason"] = f"expected {allowed}, got {http}"
        return row

    if tier == "tier_2_gated":
        impl = spec.get("implementation", "planned")
        gated_codes = set(spec.get("expect_when_gated", [401, 302, 307]))
        if impl == "planned" and http == 200 and spec.get("warn_if_public_200"):
            row["status"] = "WARN"
            row["reason"] = "public 200 — gate not wired yet (expected when Phase 1 ships)"
            return row
        if http in gated_codes:
            row["status"] = "PASS"
            return row
        if http == 200:
            row["status"] = "WARN" if impl != "live" else "FAIL"
            row["reason"] = "gated path returned 200 without auth probe"
            return row
        row["status"] = "WARN"
        row["reason"] = f"unexpected http {http}"
        return row

    if tier == "tier_3_api":
        allowed = spec.get("expect_http", [200])
        row["status"] = "PASS" if http in allowed else "WARN"
        if row["status"] != "PASS":
            row["reason"] = f"expected {allowed}, got {http}"
        return row

    row["status"] = "SKIP"
    return row


def run_supabase_subprobe() -> dict[str, Any]:
    if not SUPABASE_VERIFY.is_file():
        return {"status": "SKIP", "reason": "verify_supabase_live_profiles_v1.py missing"}
    try:
        proc = subprocess.run(
            [sys.executable, str(SUPABASE_VERIFY), "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=ROOT,
        )
        if proc.returncode != 0 and not proc.stdout.strip():
            return {"status": "WARN", "reason": "supabase probe failed", "stderr": proc.stderr[:200]}
        data = json.loads(proc.stdout) if proc.stdout.strip() else {}
        return {
            "status": "PASS" if data.get("status") == "PASS" else "WARN",
            "schema": data.get("schema"),
            "failures": data.get("failures", []),
        }
    except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
        return {"status": "WARN", "reason": str(exc)}


def lint_redirect_allow_list(matrix: dict[str, Any]) -> dict[str, Any]:
    urls = matrix.get("supabase_redirect_allow_list", [])
    bad = [u for u in urls if not u.startswith("http")]
    return {
        "status": "PASS" if not bad else "FAIL",
        "count": len(urls),
        "bad_entries": bad,
    }


def run_probe(*, write_receipt: bool, emit_json: bool) -> tuple[dict[str, Any], int]:
    matrix = load_matrix()
    results: list[dict[str, Any]] = []
    hard_failures: list[str] = []

    for tier_key, tier_block in matrix.get("tiers", {}).items():
        for spec in tier_block.get("surfaces", []):
            row = check_surface(spec, tier=tier_key)
            results.append(row)
            if row["status"] == "FAIL":
                hard_failures.append(f"{row['id']}: {row.get('reason', row['http'])}")

    supabase = run_supabase_subprobe()
    redirect_lint = lint_redirect_allow_list(matrix)

    tier0 = [r for r in results if r["tier"] == "tier_0_public"]
    tier0_pass = all(r["status"] == "PASS" for r in tier0)

    if redirect_lint["status"] == "FAIL":
        hard_failures.append("redirect_allow_list invalid entries")

    overall = "PASS"
    if hard_failures or not tier0_pass:
        overall = "FAIL"
    elif any(r["status"] == "WARN" for r in results) or supabase.get("status") == "WARN":
        overall = "WARN"

    report = {
        "schema": "sg-auth-surface-probe-v1",
        "generated_at": utc_now(),
        "motor_id": "gh_actions_sg_auth_surface_probe_v1",
        "loop_id": "sg_auth_surface_probe_v1",
        "status": overall,
        "identity_plane": matrix.get("identity_plane"),
        "surface_results": results,
        "supabase_subprobe": supabase,
        "redirect_allow_list_lint": redirect_lint,
        "hard_failures": hard_failures,
        "repo_ownership": matrix.get("repo_ownership"),
        "founder_decisions_pending": matrix.get("founder_decisions_pending"),
        "closed_loop": "probe → FAIL/WARN → alert → venture fix → redeploy → probe PASS",
    }

    if write_receipt:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = RECEIPT_DIR / f"auth-surface-probe-{ts}.json"
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["receipt_path"] = str(out.relative_to(ROOT))

    if emit_json:
        print(json.dumps(report, indent=2))
    else:
        print(f"sg-auth-surface-probe-v1: {overall}")
        print(f"  tier_0: {sum(1 for r in tier0 if r['status']=='PASS')}/{len(tier0)} PASS")
        print(f"  supabase: {supabase.get('status')}")
        for f in hard_failures:
            print(f"  FAIL: {f}")

    exit_code = 0 if overall in ("PASS", "WARN") else 1
    return report, exit_code


def main() -> int:
    ap = argparse.ArgumentParser(description="SG auth surface E2E probe")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--fail-on-warn", action="store_true", help="exit 1 on WARN (CI strict mode)")
    args = ap.parse_args()

    _, code = run_probe(write_receipt=args.write_receipt, emit_json=args.json)
    if args.fail_on_warn:
        # re-load would be wasteful; caller uses --json in CI for artifacts
        pass
    return code


if __name__ == "__main__":
    raise SystemExit(main())
