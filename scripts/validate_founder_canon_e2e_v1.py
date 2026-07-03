#!/usr/bin/env python3
"""E2E validator — FOUNDER_CANON v1 wired across SG SSOT, loops, dispatch, receipts."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANON_MD = ROOT / "ssot/FOUNDER_CANON_v1.md"
CANON_JSON = ROOT / "data/founder_canon_v1.json"
LOOPS_JSON = ROOT / "data/machine_autonomy_loops_v1.json"
AGENTS = ROOT / "AGENTS.md"
PR_TEMPLATE = ROOT / ".github/pull_request_template.md"
DISPATCH = ROOT / "docs/MAC_CURSOR_VENTURE_DISPATCH_v1.md"
ACTIVATION = ROOT / "receipts/founder-canon-activation-v1.json"
INTEGRATOR_RULES = ROOT / "ssot/NOOS_INTEGRATOR_RULES_v1.md"
CYCLE_SCRIPT = ROOT / "scripts/run_machine_autonomy_cycle_v1.py"
CANON_VERSION = "founder_canon_v1.0.0"
LAWS_SNIPPET = "FOUNDER_CANON v1"


def main() -> int:
    errors: list[str] = []

    for path in (CANON_MD, CANON_JSON, LOOPS_JSON, ACTIVATION, CYCLE_SCRIPT, INTEGRATOR_RULES):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if CANON_MD.is_file():
        text = CANON_MD.read_text(encoding="utf-8")
        if "**Status:** ACTIVE" not in text:
            errors.append("FOUNDER_CANON_v1.md must be ACTIVE")
        if "MACHINE_AUTONOMY_LOOPS_v1" not in text:
            errors.append("FOUNDER_CANON must link machine autonomy implementation")

    if CANON_JSON.is_file():
        canon = json.loads(CANON_JSON.read_text(encoding="utf-8"))
        if canon.get("status") != "ACTIVE":
            errors.append("founder_canon_v1.json status must be ACTIVE")
        if canon.get("version") != "1.0.0":
            errors.append("founder_canon_v1.json version must be 1.0.0")
        if len(canon.get("founder_touchpoints", [])) != 4:
            errors.append("founder_canon must define exactly 4 touchpoints")
        if len(canon.get("intent_filter", [])) != 5:
            errors.append("founder_canon intent_filter must have 5 questions")

    if ACTIVATION.is_file():
        act = json.loads(ACTIVATION.read_text(encoding="utf-8"))
        if act.get("canon_version") != CANON_VERSION:
            errors.append("activation receipt canon_version mismatch")

    if AGENTS.is_file():
        agents = AGENTS.read_text(encoding="utf-8")
        if "FOUNDER_CANON" not in agents and "founder_canon" not in agents:
            errors.append("AGENTS.md must reference FOUNDER_CANON")

    if PR_TEMPLATE.is_file():
        pr = PR_TEMPLATE.read_text(encoding="utf-8")
        if LAWS_SNIPPET not in pr:
            errors.append("PR template missing FOUNDER_CANON v1 LAWS line")

    if DISPATCH.is_file():
        disp = DISPATCH.read_text(encoding="utf-8")
        if LAWS_SNIPPET not in disp:
            errors.append("MAC_CURSOR_VENTURE_DISPATCH missing LAWS line")

    if CYCLE_SCRIPT.is_file():
        cycle = CYCLE_SCRIPT.read_text(encoding="utf-8")
        if "canon_version" not in cycle:
            errors.append("run_machine_autonomy_cycle_v1 must emit canon_version")

    if LOOPS_JSON.is_file():
        loops = json.loads(LOOPS_JSON.read_text(encoding="utf-8"))
        if len(loops.get("founder_triggers_minimal", [])) < 4:
            errors.append("machine_autonomy_loops must define founder_triggers_minimal")

    if errors:
        print("validate_founder_canon_e2e_v1: FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("validate_founder_canon_e2e_v1: ALL PASS")
    print(json.dumps({"canon_version": CANON_VERSION, "checks": 10}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
