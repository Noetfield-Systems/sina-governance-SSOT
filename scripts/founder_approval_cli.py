#!/usr/bin/env python3
"""Founder approval CLI v1

Scans receipts/agentic/grants-*.json for capabilities with founder_required and
offers an approval interface via CLI flags. On approval, emits approvals under
receipts/agentic/approvals-*.json and marks grant as approved in a local copy.

Usage:
  - List pending founder grants: python3 scripts/founder_approval_cli.py --list
  - Approve by grant filename: python3 scripts/founder_approval_cli.py --approve grants-<ts>.json --founder founder_name

This is non-networked; approvals are local receipts for operator records.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "agentic"
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)


def load_grant_receipts() -> Dict[str, Dict[str, Any]]:
    grants = {}
    for p in sorted(RECEIPT_DIR.glob("grants-*.json")):
        try:
            with open(p) as fh:
                grants[p.name] = json.load(fh)
        except Exception:
            continue
    return grants


def list_founder_required(grants: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    pending = {}
    for name, payload in grants.items():
        for cap, info in (payload.get("grants") or {}).items():
            if info.get("granted") is False and "founder_trigger_required" in (info.get("reasons") or []):
                pending.setdefault(name, {})[cap] = info
    return pending


def emit_approval_receipt(grant_filename: str, capability: str, founder: str) -> Path:
    payload = {
        "approval_id": f"approval-{int(datetime.utcnow().timestamp())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source_grant": grant_filename,
        "capability": capability,
        "founder": founder,
        "status": "approved",
    }
    path = RECEIPT_DIR / f"approvals-{int(datetime.utcnow().timestamp())}.json"
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)
    return path


def approve(grant_filename: str, capability: str, founder: str) -> Path:
    grants = load_grant_receipts()
    if grant_filename not in grants:
        raise FileNotFoundError(grant_filename)
    payload = grants[grant_filename]
    info = (payload.get("grants") or {}).get(capability)
    if not info:
        raise KeyError(capability)
    # record approval
    p = emit_approval_receipt(grant_filename, capability, founder)
    return p


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true", help="List pending founder-required grants")
    parser.add_argument("--approve", help="Grant filename to approve (e.g., grants-<ts>.json)")
    parser.add_argument("--capability", help="Capability name to approve (e.g., allow_publish_artifacts)")
    parser.add_argument("--founder", help="Founder name approving the grant")
    args = parser.parse_args(argv)

    grants = load_grant_receipts()
    if args.list:
        pending = list_founder_required(grants)
        print(json.dumps(pending, indent=2))
        return 0
    if args.approve:
        if not args.capability or not args.founder:
            parser.error("--approve requires --capability and --founder")
        p = approve(args.approve, args.capability, args.founder)
        print(f"Approval receipt written: {p}")
        return 0
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
