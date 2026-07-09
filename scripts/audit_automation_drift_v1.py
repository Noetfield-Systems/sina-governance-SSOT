#!/usr/bin/env python3
"""Drift detection — launchd, SourceA HEAD, inventory hash, CF/GH probes."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "data" / "automation_surface_inventory_v1.json"
REGISTRY = ROOT / "data" / "github_automation_registry_v1.json"
RECEIPTS = ROOT / "receipts"
LAUNCHD_LABEL = "com.sina.brain-loop-autorun-v1"


def sha_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_short(repo: Path) -> str | None:
    try:
        return (
            subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True)
            .strip()
        )
    except subprocess.CalledProcessError:
        return None


def launchd_loaded() -> bool:
    try:
        out = subprocess.check_output(["launchctl", "list"], text=True, stderr=subprocess.DEVNULL)
        return LAUNCHD_LABEL in out
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def curl_ok(url: str, timeout: float = 8.0) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(4096).decode("utf-8", errors="replace")
            return True, body[:200]
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, str(exc)


def gh_main_workflow_status() -> str:
    try:
        out = subprocess.check_output(
            [
                "gh",
                "run",
                "list",
                "--workflow=brain-loop-autorun-v1.yml",
                "--repo",
                "Noetfield-Systems/sina-governance-SSOT",
                "--branch",
                "main",
                "--limit",
                "1",
                "--json",
                "conclusion,status",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        rows = json.loads(out)
        if not rows:
            return "unknown"
        row = rows[0]
        return f"{row.get('status')}:{row.get('conclusion')}"
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired):
        return "unknown"


def main() -> int:
    drift_items: list[dict[str, str]] = []
    sourcea = Path(os.path.expanduser("~/Projects/SourceA"))
    head = git_short(sourcea)

    if not head:
        drift_items.append({"check": "sourcea_git", "status": "DRIFT", "detail": "git HEAD unreadable at ~/Projects/SourceA"})
    if not launchd_loaded():
        drift_items.append({"check": "launchd", "status": "DRIFT", "detail": f"{LAUNCHD_LABEL} not loaded"})

    inv_hash = sha_file(INVENTORY) if INVENTORY.is_file() else "missing"
    reg_hash = sha_file(REGISTRY) if REGISTRY.is_file() else "missing"

    cf_runtime_ok, _ = curl_ok("https://sourcea.app/api/cloud-forge-run/health/v1")
    cf_brain_ok, _ = curl_ok("https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/health")
    if not cf_runtime_ok:
        drift_items.append({"check": "cf_auto_runtime", "status": "DRIFT", "detail": "health probe failed"})
    if not cf_brain_ok:
        drift_items.append({"check": "cf_brain_chat", "status": "DRIFT", "detail": "health probe failed"})

    gh_status = gh_main_workflow_status()
    if gh_status.endswith(":failure"):
        drift_items.append(
            {
                "check": "gh_brain_loop_main",
                "status": "DRIFT",
                "detail": f"latest main run {gh_status} (merge CI fixes to clear)",
            }
        )

    if drift_items:
        drift_status = "DRIFT"
    else:
        drift_status = "PASS"

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "schema": "automation-drift-audit-receipt-v1",
        "receipt_id": f"automation-drift-audit-{ts}",
        "recorded_at": ts,
        "drift_status": drift_status,
        "sourcea_head": head or "unknown",
        "launchd_loaded": launchd_loaded(),
        "inventory_sha256": inv_hash,
        "registry_sha256": reg_hash,
        "gh_brain_loop_main": gh_status,
        "cf_auto_runtime_ok": cf_runtime_ok,
        "cf_brain_chat_ok": cf_brain_ok,
        "drift_items": drift_items,
    }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    path = RECEIPTS / f"{receipt['receipt_id']}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"audit_automation_drift_v1: {drift_status}")
    print(json.dumps({"receipt_id": receipt["receipt_id"], "drift_count": len(drift_items)}, indent=2))
    for item in drift_items:
        print(f" - {item['check']}: {item['detail']}")
    return 0 if drift_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
