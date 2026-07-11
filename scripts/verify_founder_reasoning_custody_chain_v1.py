#!/usr/bin/env python3
"""Verify founder-reasoning custody chain and Option C absorption artifacts."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "SG-Canonical-Library/noetfield-library"
NOOS = Path.home() / "Desktop/Noetfield-Systems/noetfeld-OS"

REQUIRED = [
    ROOT / "ssot/strategy-ssot-v6-split.md",
    LIB / "P2-SSOT/LIBRARY_CUSTODY_MATRIX_LOCKED_v1.md",
    LIB / "P2-SSOT/AUTHORITY_GRAPH_FOUNDER_REASONING_LOCKED_v1.md",
    LIB / "P2-SSOT/SSOT_INDEX.md",
    LIB / "P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md",
    LIB / "P8-MACHINE-LOOPS/founder-reasoning-continuation-doctrine-LOCKED_v1.md",
    LIB / "P8-MACHINE-LOOPS/MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md",
    LIB / "P10-PRODUCT-LAYERS/COST_EXECUTION_DOCTRINE_LOCKED_v1.md",
    ROOT / "receipts/custody/CUSTODY_WIRING_FOUNDER_REASONING_v1.json",
    ROOT / "receipts/custody/CUSTODY_ABSORPTION_ADVISOR_PACKAGE_OPTION_C_v1.json",
]

NOOS_REQUIRED = [
    NOOS / "noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json",
    NOOS / "noetfield-org/FOUNDER_REASONING_MOTOR_OPERATIONAL_BINDING_v1.md",
    NOOS / "noetfield-org/schemas/SCHEMA_INDEX_v1.md",
    NOOS / "noetfield-org/schemas/founder_reasoning_packet.v1.schema.json",
    NOOS / "noetfield-org/schemas/founder_reasoning_result.v1.schema.json",
    NOOS / "noetfield-org/schemas/motor_job_contract.v1.schema.json",
    NOOS / "noetfield-org/schemas/private_worker_binding.v1.schema.json",
]


def main() -> int:
    missing = [str(p) for p in REQUIRED + NOOS_REQUIRED if not p.is_file()]

    ms = (ROOT / "ssot/strategy-ssot-v6-split.md").read_text(encoding="utf-8")
    if "0.7 — Motor escalation continuity" not in ms:
        print("FAIL: Master SSOT missing §0.7 anchor")
        return 2

    term = (LIB / "P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md").read_text(encoding="utf-8")
    if "§12 — Advisor-package harmonization" not in term:
        print("FAIL: P7 terminology §12 harmonization missing")
        return 2

    if missing:
        print("FAIL: missing files:")
        for m in missing:
            print(f"  - {m}")
        return 2

    pins = json.loads((NOOS / "noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json").read_text(encoding="utf-8"))
    if not pins.get("sg_repo") or not pins.get("noos_repo"):
        print("FAIL: CUSTODY_AUTHORITY_PINS_v1.json incomplete")
        return 2

    schema_roles = {a.get("role") for a in pins.get("artifacts", [])}
    if "motor_schemas" not in schema_roles or "commissioning_standard" not in schema_roles:
        print("FAIL: pins missing Option C artifacts (motor_schemas / commissioning_standard)")
        return 2

    print("PASS: founder-reasoning custody chain + Option C absorption verified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
