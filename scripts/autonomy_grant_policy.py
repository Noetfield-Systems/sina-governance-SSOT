#!/usr/bin/env python3
"""Autonomy-based grant policy v1

Reads receipts/agentic and computes autonomy metrics (via autonomy_scorer) then
applies capability grant rules. Emits a grant receipt for each decision under
receipts/agentic/grants-*.json.

Rules (example):
 - allow_repair_autofill: autonomy_score >= 0.5 and avg_risk <= 3 and validated+repaired >= 3
 - allow_auto_respond: autonomy_score >= 0.7 and avg_risk <= 2
 - allow_publish_artifacts: founder trigger (requires founder approval) -> never auto-grant
 - allow_package_publish: founder trigger -> requires founder
 - allow_retry_rerun: autonomy_score >= 0.4

Grant receipts include rationale, metrics, and revoke conditions.
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


CAPABILITY_RULES = {
    "allow_repair_autofill": {
        "autonomy_min": 0.5,
        "max_avg_risk": 3.0,
        "min_validated_or_repaired": 3,
        "founder_required": False,
    },
    "allow_auto_respond": {
        "autonomy_min": 0.7,
        "max_avg_risk": 2.0,
        "min_validated_or_repaired": 5,
        "founder_required": False,
    },
    "allow_retry_rerun": {
        "autonomy_min": 0.4,
        "max_avg_risk": 5.0,
        "min_validated_or_repaired": 1,
        "founder_required": False,
    },
    "allow_publish_artifacts": {
        "founder_required": True,
    },
    "allow_package_publish": {
        "founder_required": True,
    },
}


def evaluate_rules(metrics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    grants: Dict[str, Dict[str, Any]] = {}
    validated = metrics.get("validated", 0)
    repaired = metrics.get("repaired", 0)
    total_ok = validated + repaired
    autonomy = float(metrics.get("autonomy_score", 0.0) or 0.0)
    avg_risk = metrics.get("avg_risk") if metrics.get("avg_risk") is not None else float("inf")

    for cap, rule in CAPABILITY_RULES.items():
        entry: Dict[str, Any] = {"granted": False, "reasons": [], "metrics": metrics}
        if rule.get("founder_required"):
            entry["granted"] = False
            entry["reasons"].append("founder_trigger_required")
            grants[cap] = entry
            continue
        if autonomy < rule.get("autonomy_min", 0.0):
            entry["reasons"].append(f"autonomy_score {autonomy:.2f} < required {rule.get('autonomy_min')}")
        if avg_risk is not None and avg_risk > rule.get("max_avg_risk", float("inf")):
            entry["reasons"].append(f"avg_risk {avg_risk:.2f} > allowed {rule.get('max_avg_risk')}")
        if total_ok < rule.get("min_validated_or_repaired", 0):
            entry["reasons"].append(f"validated+repaired {total_ok} < required {rule.get('min_validated_or_repaired')}")
        if not entry["reasons"]:
            entry["granted"] = True
            entry["reasons"].append("criteria_met")
            # Add revoke condition
            entry["revoke_if"] = {"autonomy_below": rule.get("autonomy_min") * 0.9}
        grants[cap] = entry
    return grants


def emit_grant_receipt(grants: Dict[str, Any]) -> Path:
    payload = {
        "grant_id": f"grant-{int(datetime.utcnow().timestamp())}",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "grants": grants,
    }
    path = RECEIPT_DIR / f"grants-{int(datetime.utcnow().timestamp())}.json"
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)
    return path


def main():
    receipts = load_receipts()
    metrics = score(receipts)
    grants = evaluate_rules(metrics)
    path = emit_grant_receipt(grants)
    print(f"Grant receipt emitted: {path}")
    print(json.dumps({"metrics": metrics, "grants": grants}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
