#!/usr/bin/env python3
"""Autonomy scorer for agentic receipts.

Reads receipts/agentic/*.json and computes simple autonomy metrics:
 - total receipts
 - validated_count (status == 'validated')
 - repaired_count (status startswith 'repaired')
 - failed_count (status == 'validation_failed')
 - average_risk
 - autonomy_score = (validated_count + repaired_count) / total

Writes a report to receipts/agentic/autonomy_report-<ts>.json
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
RECEIPT_DIR = ROOT / "receipts" / "agentic"
RECEIPT_DIR.mkdir(parents=True, exist_ok=True)


def load_receipts() -> List[dict]:
    receipts = []
    for p in sorted(RECEIPT_DIR.glob("receipt-*.json")):
        try:
            with open(p) as fh:
                receipts.append(json.load(fh))
        except Exception:
            continue
    return receipts


def score(receipts: List[dict]) -> dict:
    total = len(receipts)
    if total == 0:
        return {"total": 0, "autonomy_score": 0.0}
    validated = sum(1 for r in receipts if r.get("status") == "validated")
    repaired = sum(1 for r in receipts if isinstance(r.get("status"), str) and r.get("status").startswith("repaired"))
    failed = sum(1 for r in receipts if r.get("status") == "validation_failed")
    avg_risk = None
    risks = [float(r.get("risk_score", 0)) for r in receipts if r.get("risk_score") is not None]
    if risks:
        avg_risk = sum(risks) / len(risks)
    autonomy_score = (validated + repaired) / total
    return {"total": total, "validated": validated, "repaired": repaired, "failed": failed, "avg_risk": avg_risk, "autonomy_score": autonomy_score}


def emit_report(report: dict) -> Path:
    path = RECEIPT_DIR / f"autonomy_report-{int(datetime.utcnow().timestamp())}.json"
    with open(path, "w") as fh:
        json.dump(report, fh, indent=2)
    return path


def main():
    receipts = load_receipts()
    report = score(receipts)
    path = emit_report(report)
    print(f"Autonomy report written: {path}")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())