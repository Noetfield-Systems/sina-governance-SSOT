#!/usr/bin/env python3
"""Autonomy revocation checker v1

Reads grant receipts under receipts/agentic/grants-*.json and compares current
metrics (from autonomy_scorer) against revoke_if conditions. Emits revocation
receipts under receipts/agentic/revocations-*.json for capabilities whose
revoke conditions are met.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from scripts.autonomy_scorer import load_receipts, score

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "agentic"
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)


def load_grant_receipts() -> Dict[str, Dict[str, Any]]:
    grants = {}
    for p in sorted(RECEIPT_DIR.glob("grants-*.json")):
        try:
            with open(p) as fh:
                data = json.load(fh)
                grants[p.name] = data
        except Exception:
            continue
    return grants


def evaluate_revocations(metrics: Dict[str, Any], grant_payload: Dict[str, Any]) -> Dict[str, Any]:
    revocations = {}
    grants = grant_payload.get("grants", {})
    for cap, info in grants.items():
        revoke_if = info.get("revoke_if")
        if not revoke_if:
            continue
        # currently only support autonomy_below
        autonomy_below = revoke_if.get("autonomy_below")
        if autonomy_below is None:
            continue
        current_autonomy = float(metrics.get("autonomy_score", 0.0) or 0.0)
        if current_autonomy < autonomy_below:
            revocations[cap] = {"reason": f"autonomy_score {current_autonomy:.2f} < revoke threshold {autonomy_below}", "metrics": metrics}
    return revocations


def emit_revocation_receipt(revocations: Dict[str, Any], grant_filename: str) -> Path:
    payload = {
        "revocation_id": f"revoke-{int(datetime.utcnow().timestamp())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source_grant": grant_filename,
        "revocations": revocations,
    }
    path = RECEIPT_DIR / f"revocations-{int(datetime.utcnow().timestamp())}.json"
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)
    return path


def main() -> int:
    receipts = load_receipts()
    metrics = score(receipts)
    grant_receipts = load_grant_receipts()
    any_revoked = False
    for fname, data in grant_receipts.items():
        revs = evaluate_revocations(metrics, data)
        if revs:
            p = emit_revocation_receipt(revs, fname)
            print(f"Revocation emitted: {p}")
            any_revoked = True
    if not any_revoked:
        print("No revocations needed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
