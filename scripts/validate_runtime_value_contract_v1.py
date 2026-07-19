#!/usr/bin/env python3
"""Validate Runtime Value Contracts against registry motors and JSON Schema."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "github_automation_registry_v1.json"
CONTRACTS = ROOT / "data" / "runtime_value_contracts_v1.json"
SCHEMA = ROOT / "schemas" / "runtime_value_contract_v1.schema.json"

SCHEDULED_KINDS = {
    "github_actions",
    "cloudflare_cron",
    "cloudflare_worker",
    "mac_launchd",
    "railway_cron",
}


def main() -> int:
    errors: list[str] = []

    for path in (REGISTRY, CONTRACTS, SCHEMA):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    contracts_doc = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    validator = Draft202012Validator(schema)
    for err in sorted(validator.iter_errors(contracts_doc), key=lambda e: list(e.path)):
        errors.append(f"schema: {list(err.path)}: {err.message}")

    motors = registry.get("motors") or []
    motor_ids = {m.get("motor_id") for m in motors if m.get("motor_id")}
    contracts = contracts_doc.get("contracts") or []

    runtime_ids: set[str] = set()
    covered_motors: set[str] = set()
    for c in contracts:
        rid = c.get("runtime_id")
        mid = c.get("motor_id")
        if rid in runtime_ids:
            errors.append(f"duplicate runtime_id: {rid}")
        runtime_ids.add(rid)
        if mid not in motor_ids:
            errors.append(f"{rid}: motor_id not in registry: {mid}")
        else:
            covered_motors.add(mid)

        trigger = c.get("trigger") or {}
        ttype = trigger.get("type")
        if ttype == "justified_schedule":
            if not trigger.get("time_dependent_reason"):
                errors.append(f"{rid}: justified_schedule missing time_dependent_reason")
            if not trigger.get("cadence"):
                errors.append(f"{rid}: justified_schedule missing cadence")
        if ttype == "event" and not trigger.get("event"):
            errors.append(f"{rid}: event trigger missing event name")

        nw = c.get("no_work_behavior") or {}
        if not all(nw.get(k) is True for k in ("no_write", "no_llm", "no_notification")):
            errors.append(f"{rid}: no_work_behavior must be no_write/no_llm/no_notification=true")

        if c.get("beneficiary") == "none.quarantined" and c.get("status") not in {
            "quarantined",
            "disabled",
        }:
            errors.append(f"{rid}: beneficiary none.quarantined requires quarantined/disabled status")

        out = c.get("output") or {}
        if c.get("status") == "active" and out.get("visibility") == "none":
            errors.append(f"{rid}: active contract cannot have output.visibility=none")

    missing = sorted(motor_ids - covered_motors)
    for mid in missing:
        errors.append(f"registry motor missing runtime value contract: {mid}")

    # Finite/scheduled motors must not be active without justified schedule or on_demand/event/manual.
    by_motor = {m["motor_id"]: m for m in motors if m.get("motor_id")}
    for c in contracts:
        mid = c["motor_id"]
        motor = by_motor.get(mid) or {}
        if motor.get("kind") not in SCHEDULED_KINDS:
            continue
        if c.get("status") in {"quarantined", "disabled", "manual_only", "event_driven"}:
            continue
        trigger = c.get("trigger") or {}
        if trigger.get("type") == "justified_schedule" and not trigger.get("time_dependent_reason"):
            errors.append(f"{c['runtime_id']}: scheduled motor lacks time-dependent reason")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        print(f"FAIL: runtime value contract ({len(errors)} errors)", file=sys.stderr)
        return 1

    print(
        f"PASS: runtime value contract "
        f"({len(contracts)} contracts covering {len(covered_motors)} motors)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
