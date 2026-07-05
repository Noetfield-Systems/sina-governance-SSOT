#!/usr/bin/env python3
"""SG verifier — probe live Supabase profiles from Sina env (~/.sourcea-secrets/).

Does not print secret values. Exit 0 only when all live SSOT refs respond.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts"

LIVE_PROFILES = {
    "portfolio_spine": {
        "ref": "ldfruywifqnfpwsfgmdl",
        "env_file": Path.home() / ".sourcea-secrets/portfolio-spine.env",
        "url_keys": ["SUPABASE_URL"],
        "key_keys": ["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY"],
        "table": "truth_log",
    },
    "noetfield": {
        "ref": "tkgpapowwplupyekpivy",
        "env_file": Path.home() / ".sourcea-secrets/noetfield.env",
        "url_keys": ["NOETFIELD_SUPABASE_URL", "SUPABASE_URL"],
        "key_keys": ["NOETFIELD_SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_ROLE_KEY"],
        "table": "noetfield_factory_cycle_runs",
    },
}

# Personal-org orphan — NOT in live SSOT; pause email 2026-07-05. Do not wire to env.
ORPHAN_PAUSED_REFS = {
    "cybzznaieigeveiaoyoa": {
        "org": "sina.kazemnezhad.ca@gmail.com's Org",
        "action": "IGNORE unless founder identifies legacy use; not production",
    },
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def resolve_cred(spec: dict, vals: dict[str, str]) -> tuple[str, str] | None:
    url = ""
    for key in spec["url_keys"]:
        url = vals.get(key) or os.environ.get(key, "")
        if url:
            break
    secret = ""
    for key in spec["key_keys"]:
        secret = vals.get(key) or os.environ.get(key, "")
        if secret:
            break
    if url and secret:
        return url.rstrip("/"), secret
    return None


def probe_table(base: str, key: str, table: str) -> dict:
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    req = urllib.request.Request(
        f"{base}/rest/v1/{table}?select=id&limit=1",
        headers=headers,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(raw) if raw.strip() else []
            return {"ok": True, "http": resp.status, "rows": len(rows) if isinstance(rows, list) else 0}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")[:200]
        paused = exc.code in (522, 503) or "paused" in body.lower()
        return {"ok": False, "http": exc.code, "error": body, "likely_paused": paused}
    except urllib.error.URLError as exc:
        return {"ok": False, "http": 0, "error": str(exc.reason), "likely_paused": True}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Verify live Supabase profiles (Sina env)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()

    profiles_out: dict[str, dict] = {}
    failures: list[str] = []

    for name, spec in LIVE_PROFILES.items():
        env_path = spec["env_file"]
        vals = load_env_file(env_path)
        cred = resolve_cred(spec, vals)
        row: dict = {
            "expected_ref": spec["ref"],
            "env_file": str(env_path),
            "env_file_exists": env_path.is_file(),
        }
        if not cred:
            row["ok"] = False
            row["reason"] = "credentials_not_configured"
            failures.append(f"{name}: missing creds in {env_path}")
        else:
            base, key = cred
            actual_ref = base.split("//")[-1].split(".")[0]
            row["actual_ref"] = actual_ref
            row["ref_match"] = actual_ref == spec["ref"]
            if not row["ref_match"]:
                failures.append(f"{name}: ref mismatch expected {spec['ref']} got {actual_ref}")
            probe = probe_table(base, key, spec["table"])
            row.update(probe)
            if not probe.get("ok"):
                failures.append(f"{name}: probe failed ({probe.get('error', probe.get('http'))})")
                if probe.get("likely_paused"):
                    row["founder_action"] = f"Unpause at https://supabase.com/dashboard/project/{spec['ref']}"
        profiles_out[name] = row

    report = {
        "schema": "sg-supabase-live-profiles-verify-v1",
        "generated_at": utc_now(),
        "status": "PASS" if not failures else "FAIL",
        "credential_source": "~/.sourcea-secrets/ (Sina env — not Railway)",
        "live_profiles": profiles_out,
        "orphan_paused_refs": ORPHAN_PAUSED_REFS,
        "failures": failures,
        "founder_note": (
            "Email ref cybzznaieigeveiaoyoa is personal-org orphan — NOT in live SSOT. "
            "Production uses ldfruywifqnfpwsfgmdl + tkgpapowwplupyekpivy only."
        ),
    }

    if args.write_receipt:
        RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = RECEIPT_DIR / f"supabase-live-profiles-verify-{ts}.json"
        out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        report["receipt_path"] = str(out)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"status: {report['status']}")
        for name, row in profiles_out.items():
            mark = "OK" if row.get("ok") else "FAIL"
            print(f"  {name}: {mark} ref={row.get('actual_ref', '?')}")
        if failures:
            for f in failures:
                print(f"  FAIL: {f}")
        print(f"  orphan: cybzznaieigeveiaoyoa — ignore (not production)")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
