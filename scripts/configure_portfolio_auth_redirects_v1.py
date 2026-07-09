#!/usr/bin/env python3
"""Configure Supabase Auth redirect allow-lists for W11 cross-domain auth (founder/ops)."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

SG_ROOT = Path(__file__).resolve().parents[1]
MATRIX = SG_ROOT / "data" / "auth_surface_matrix_v1.json"

PROJECTS = {
    "portfolio_spine": {
        "ref": "ldfruywifqnfpwsfgmdl",
        "site_url": "https://sourcea.app",
        "uri_allow_list": (
            "https://sourcea.app/**,"
            "http://localhost:3000/**"
        ),
    },
    "noetfield": {
        "ref": "tkgpapowwplupyekpivy",
        "site_url": "https://www.noetfield.com",
        "uri_allow_list": (
            "https://www.noetfield.com/**,"
            "https://www.trustfield.ca/**,"
            "https://trustfield.ca/**,"
            "http://localhost:3000/**"
        ),
    },
}


def access_token() -> str:
    env = (
        os.environ.get("SUPABASE_ACCESS_TOKEN", "").strip()
        or os.environ.get("SUPABASE_PAT", "").strip()
    )
    if env:
        return env
    for path in (
        os.path.expanduser("~/.config/supabase/access-token"),
        os.path.expanduser("~/.supabase/access-token"),
    ):
        if os.path.isfile(path):
            return Path(path).read_text(encoding="utf-8").strip()
    return ""


def patch_project(ref: str, body: dict) -> dict:
    token = access_token()
    if not token:
        return {"ok": False, "skipped": True, "reason": "no SUPABASE_ACCESS_TOKEN"}
    req = urllib.request.Request(
        f"https://api.supabase.com/v1/projects/{ref}/config/auth",
        data=json.dumps(body).encode(),
        method="PATCH",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode()[:300]}


def main() -> int:
    matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
    allow = matrix.get("supabase_redirect_allow_list") or []
    results = []
    for name, cfg in PROJECTS.items():
        body = {
            "site_url": cfg["site_url"],
            "uri_allow_list": cfg["uri_allow_list"],
            "mailer_autoconfirm": False,
        }
        row = {"project": name, "ref": cfg["ref"], "patch": patch_project(cfg["ref"], body)}
        results.append(row)
        print(json.dumps(row, indent=2))

    receipt = {
        "schema": "sg-auth-supabase-redirect-config-v1",
        "allow_list_from_matrix": allow,
        "results": results,
    }
    out = SG_ROOT / "receipts" / "auth-supabase-redirect-config-latest.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(f"[configure-auth-redirects] receipt -> {out}")
    return 0 if all(r["patch"].get("ok") or r["patch"].get("skipped") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
