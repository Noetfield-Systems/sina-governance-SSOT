#!/usr/bin/env python3
"""SG auth surface probe v1.1 — tiered HTTP checks + Supabase identity plane.

Reads data/auth_surface_matrix_v1.json. SG verifies; venture repos implement UI/RLS.
Does not print secrets. Exit 0 when tier-0 public surfaces pass and no hard failures.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "data/auth_surface_matrix_v1.json"
RECEIPT_DIR = ROOT / "receipts"
SUPABASE_VERIFY = ROOT / "scripts/verify_supabase_live_profiles_v1.py"

AUTH_REDIRECT_PATTERNS = re.compile(r"/(sign-in|sign-up|login|auth)(/|$)", re.I)


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Expose redirects to policy checks instead of following them implicitly."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> None:
        return None


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_matrix() -> dict[str, Any]:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def http_probe(
    url: str,
    *,
    timeout: int = 25,
    follow_redirect: bool = False,
    headers: dict[str, str] | None = None,
) -> dict[str, Any]:
    request_headers = {"User-Agent": "sg-auth-surface-probe-v1.1"}
    request_headers.update(headers or {})
    req = urllib.request.Request(url, method="GET", headers=request_headers)
    opener = (
        urllib.request.build_opener()
        if follow_redirect
        else urllib.request.build_opener(_NoRedirectHandler())
    )
    try:
        with opener.open(req, timeout=timeout) as resp:
            headers = {k.lower(): v for k, v in resp.headers.items()}
            return {
                "ok": True,
                "http": resp.status,
                "url": url,
                "location": headers.get("location"),
                "cache_control": headers.get("cache-control"),
            }
    except urllib.error.HTTPError as exc:
        loc = exc.headers.get("Location") if exc.headers else None
        return {
            "ok": False,
            "http": exc.code,
            "url": url,
            "error": "http_error",
            "location": loc,
        }
    except urllib.error.URLError as exc:
        return {"ok": False, "http": 0, "url": url, "error": str(exc.reason)}
    except TimeoutError:
        return {"ok": False, "http": 0, "url": url, "error": "timeout"}


def is_auth_redirect(location: str | None) -> bool:
    if not location:
        return False
    path = urlparse(location).path
    return bool(AUTH_REDIRECT_PATTERNS.search(path))


def check_tier0_anti_login_wall(spec: dict[str, Any], probe: dict[str, Any]) -> str | None:
    if not spec.get("must_not_redirect_to_auth"):
        return None
    http = probe.get("http", 0)
    if http in (301, 302, 307, 308):
        loc = probe.get("location")
        if is_auth_redirect(loc):
            return f"login-wall redirect to {loc}"
        if loc and follow_once(spec["url"], loc):
            return "redirect chain leads to auth path"
    return None


def follow_once(base_url: str, location: str) -> bool:
    target = urljoin(base_url, location)
    second = http_probe(target, follow_redirect=False)
    return is_auth_redirect(second.get("location")) or is_auth_redirect(target)


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
        wall = check_tier0_anti_login_wall(spec, probe)
        if wall:
            row["status"] = "FAIL"
            row["reason"] = wall
            return row
        # Canonical host/path redirects are allowed only after one explicit hop.
        # The hop remains visible to the anti-login-wall check above.
        if http in (301, 302, 307, 308) and probe.get("location"):
            target = urljoin(url, probe["location"])
            probe = http_probe(target, follow_redirect=False)
            http = probe.get("http", 0)
            row["http"] = http
            row["redirected_once_to"] = target
            if is_auth_redirect(target) or is_auth_redirect(probe.get("location")):
                row["status"] = "FAIL"
                row["reason"] = f"redirect chain leads to auth path: {target}"
                return row
        allowed = spec.get("expect_http", [200])
        row["status"] = "PASS" if http in allowed else "FAIL"
        if row["status"] == "FAIL":
            row["reason"] = f"expected {allowed}, got {http}"
        return row

    if tier == "tier_1_optional":
        # Follow one canonical non-auth redirect; an auth redirect remains an
        # acceptable optional-sign-up outcome and is evaluated as-is.
        if (
            http in (301, 302, 307, 308)
            and probe.get("location")
            and not is_auth_redirect(probe.get("location"))
        ):
            target = urljoin(url, probe["location"])
            second = http_probe(target, follow_redirect=False)
            http = second.get("http", 0)
            row["http"] = http
            row["redirected_once_to"] = target
        allowed = spec.get("expect_http", [200, 302])
        row["status"] = "PASS" if http in allowed else "WARN"
        if row["status"] != "PASS":
            row["reason"] = f"expected {allowed}, got {http}"
        return row

    if tier == "tier_2_gated":
        impl = spec.get("implementation", "planned")
        gated_codes = set(spec.get("expect_when_gated", [401, 302, 307]))
        planned_codes = set(spec.get("expect_when_planned", []))

        if impl == "planned" and http in planned_codes:
            row["status"] = "WARN"
            row["reason"] = f"planned route http {http} — ship Phase 1"
            return row
        if impl == "planned" and http == 200 and spec.get("warn_if_public_200"):
            row["status"] = "WARN"
            row["reason"] = "public 200 — gate not wired yet (expected when Phase 1 ships)"
            return row
        if impl == "live" and http == 200:
            row["status"] = "FAIL"
            row["reason"] = "gated path live but returns 200 without auth"
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


def _load_portfolio_spine_url() -> str | None:
    import os

    for key in ("SUPABASE_URL",):
        val = os.environ.get(key, "").strip()
        if val:
            return val.rstrip("/")
    env_path = Path.home() / ".sourcea-secrets/portfolio-spine.env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("SUPABASE_URL="):
                return line.split("=", 1)[1].strip().strip('"').strip("'").rstrip("/")
    return None


def _load_supabase_probe_key() -> str | None:
    import os

    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
    )
    if key:
        return key.strip()
    env_path = Path.home() / ".sourcea-secrets/portfolio-spine.env"
    if env_path.is_file():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if line.startswith(("SUPABASE_SERVICE_ROLE_KEY=", "SUPABASE_SERVICE_KEY=", "SUPABASE_ANON_KEY=")):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def probe_auth_health(base: str) -> dict[str, Any]:
    url = f"{base}/auth/v1/health"
    key = _load_supabase_probe_key()
    headers = {"apikey": key, "Authorization": f"Bearer {key}"} if key else None
    probe = http_probe(url, timeout=15, headers=headers)
    status = "PASS" if probe.get("http") == 200 else "WARN"
    return {"status": status, "url": url, "http": probe.get("http"), "error": probe.get("error")}


def probe_profiles_table(base: str) -> dict[str, Any]:
    key = _load_supabase_probe_key()
    if not key:
        return {"status": "WARN", "reason": "credentials_not_configured_for_profiles_probe"}

    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    req = urllib.request.Request(
        f"{base}/rest/v1/profiles?select=id&limit=1",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"status": "PASS", "http": resp.status, "table": "profiles"}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:200]
        if exc.code == 404 or "does not exist" in body.lower() or "relation" in body.lower():
            return {"status": "WARN", "http": exc.code, "reason": "profiles table not migrated yet"}
        if exc.code >= 500:
            return {"status": "FAIL", "http": exc.code, "reason": "profiles probe server error"}
        return {"status": "WARN", "http": exc.code, "reason": "profiles probe non-200"}
    except urllib.error.URLError as exc:
        return {"status": "WARN", "reason": str(exc.reason)}


def run_supabase_subprobe() -> dict[str, Any]:
    out: dict[str, Any] = {}
    if SUPABASE_VERIFY.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(SUPABASE_VERIFY), "--json"],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=ROOT,
            )
            data = json.loads(proc.stdout) if proc.stdout.strip() else {}
            out["live_profiles"] = {
                "status": "PASS" if data.get("status") == "PASS" else "WARN",
                "schema": data.get("schema"),
                "failures": data.get("failures", []),
            }
        except (subprocess.TimeoutExpired, json.JSONDecodeError, OSError) as exc:
            out["live_profiles"] = {"status": "WARN", "reason": str(exc)}
    else:
        out["live_profiles"] = {"status": "SKIP"}

    base = _load_portfolio_spine_url()
    if base:
        out["auth_health"] = probe_auth_health(base)
        out["profiles_table"] = probe_profiles_table(base)
    else:
        out["auth_health"] = {"status": "WARN", "reason": "portfolio_spine URL not configured"}
        out["profiles_table"] = {"status": "SKIP", "reason": "no base URL"}

    statuses = [v.get("status") for v in out.values() if isinstance(v, dict)]
    if "FAIL" in statuses:
        out["status"] = "FAIL"
    elif "WARN" in statuses:
        out["status"] = "WARN"
    else:
        out["status"] = "PASS"
    return out


def lint_redirect_allow_list(matrix: dict[str, Any]) -> dict[str, Any]:
    urls = matrix.get("supabase_redirect_allow_list", [])
    bad: list[str] = []
    mismatched: list[str] = []
    venture_domains = {
        "sourcea.app": "sourcea",
        "www.noetfield.com": "noetfield",
        "www.trustfield.ca": "trustfield",
        "localhost:3000": "dev",
    }
    for u in urls:
        if not u.startswith("http"):
            bad.append(u)
            continue
        parsed = urlparse(u)
        host = parsed.netloc
        if host not in venture_domains and not host.startswith("localhost"):
            mismatched.append(u)
            continue
        if parsed.path.rstrip("/") != "/auth/callback":
            mismatched.append(u)
    status = "PASS"
    if bad or mismatched:
        status = "FAIL"
    return {
        "status": status,
        "count": len(urls),
        "bad_entries": bad,
        "mismatched_entries": mismatched,
    }


def build_summaries(results: list[dict[str, Any]], matrix: dict[str, Any]) -> tuple[dict[str, int], dict[str, int], list[str]]:
    tier_summary: dict[str, int] = {}
    venture_summary: dict[str, int] = {}
    for row in results:
        tier_summary[row["tier"]] = tier_summary.get(row["tier"], 0) + (1 if row["status"] == "PASS" else 0)
        v = row.get("venture") or "unknown"
        venture_summary[v] = venture_summary.get(v, 0) + (1 if row["status"] in ("PASS", "WARN") else 0)

    next_actions: list[str] = []
    for _repo, spec in matrix.get("repo_ownership", {}).items():
        phase = spec.get("phase")
        if phase == 1:
            next_actions.append("TrustField-Technologies: execute docs/dispatch/auth-phase-1-trustfield.md")
            break
    pending = matrix.get("founder_decisions_pending", [])
    blocking = sorted(d.get("id") for d in pending if d.get("id") in (1, 4))
    if blocking:
        next_actions.append(
            "Founder: ratify blocking auth decision(s) "
            + ", ".join(f"#{decision_id}" for decision_id in blocking)
        )
    return tier_summary, venture_summary, next_actions


def run_probe(*, write_receipt: bool, emit_json: bool, fail_on_warn: bool) -> tuple[dict[str, Any], int]:
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

    if supabase.get("status") == "FAIL":
        hard_failures.append("supabase identity plane probe FAIL")
    if redirect_lint["status"] == "FAIL":
        hard_failures.append("redirect_allow_list invalid entries")

    tier0 = [r for r in results if r["tier"] == "tier_0_public"]
    tier0_pass = all(r["status"] == "PASS" for r in tier0)

    overall = "PASS"
    if hard_failures or not tier0_pass:
        overall = "FAIL"
    elif any(r["status"] == "WARN" for r in results) or supabase.get("status") == "WARN":
        overall = "WARN"

    tier_summary, venture_summary, next_actions = build_summaries(results, matrix)

    report = {
        "schema": "sg-auth-surface-probe-v1.1",
        "generated_at": utc_now(),
        "motor_id": "gh_actions_sg_auth_surface_probe_v1",
        "loop_id": "sg_auth_surface_probe_v1",
        "status": overall,
        "identity_plane": matrix.get("identity_plane"),
        "surface_results": results,
        "tier_summary": tier_summary,
        "venture_summary": venture_summary,
        "next_venture_action": next_actions,
        "supabase_subprobe": supabase,
        "redirect_allow_list_lint": redirect_lint,
        "hard_failures": hard_failures,
        "repo_ownership": matrix.get("repo_ownership"),
        "founder_decisions_pending": matrix.get("founder_decisions_pending"),
        "founder_decisions_ratified": matrix.get("founder_decisions_ratified", []),
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
        print(f"sg-auth-surface-probe-v1.1: {overall}")
        print(f"  tier_0: {sum(1 for r in tier0 if r['status']=='PASS')}/{len(tier0)} PASS")
        print(f"  supabase: {supabase.get('status')}")
        for f in hard_failures:
            print(f"  FAIL: {f}")

    exit_code = 0
    if overall == "FAIL":
        exit_code = 1
    elif overall == "WARN" and fail_on_warn:
        exit_code = 1
    return report, exit_code


def main() -> int:
    ap = argparse.ArgumentParser(description="SG auth surface E2E probe v1.1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--fail-on-warn", action="store_true", help="exit 1 on WARN")
    args = ap.parse_args()

    _, code = run_probe(
        write_receipt=args.write_receipt,
        emit_json=args.json,
        fail_on_warn=args.fail_on_warn,
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
