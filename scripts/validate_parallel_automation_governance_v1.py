#!/usr/bin/env python3
"""Validate parallel automation governance registry vs repo workflows."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "github_automation_registry_v1.json"
WORKFLOWS = ROOT / ".github" / "workflows"
MULTI_REPO = ROOT / "ssot" / "MULTI_REPO_WORKER_REGISTRY_v1.md"
GOVERNANCE = ROOT / "ssot" / "PARALLEL_AUTOMATION_GOVERNANCE_v1.md"
REQUIRED_TASK_CELLS = (
    "trustfield_loops_build",
    "sourcea_brain_register",
    "brain_promote_ci",
    "sg_guardrail_append",
    "noos_doctrine_append",
)


def fail(msg: str) -> None:
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    errors: list[str] = []

    for path in (REGISTRY, MULTI_REPO, GOVERNANCE):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if reg.get("schema") != "github_automation_registry_v1":
        errors.append("schema must be github_automation_registry_v1")

    motors = reg.get("motors", [])
    agents = reg.get("agent_lanes", [])
    task_owners = reg.get("task_cell_owners", {})
    dup_rules = reg.get("duplication_forbidden", [])

    motor_ids = set()
    for m in motors:
        mid = m.get("motor_id")
        if not mid:
            errors.append("motor missing motor_id")
            continue
        if mid in motor_ids:
            errors.append(f"duplicate motor_id: {mid}")
        motor_ids.add(mid)
        wf = m.get("workflow_file")
        if wf and m.get("kind") == "github_actions":
            wf_path = ROOT / wf
            if not wf_path.is_file():
                errors.append(f"{mid}: workflow missing {wf}")

    # Every workflow file must be registered
    if WORKFLOWS.is_dir():
        for wf_file in WORKFLOWS.glob("*.yml"):
            rel = str(wf_file.relative_to(ROOT))
            registered = any(m.get("workflow_file") == rel for m in motors)
            if not registered:
                errors.append(f"unregistered workflow: {rel}")

    agent_ids = set()
    for a in agents:
        aid = a.get("agent_id")
        if not aid:
            errors.append("agent_lane missing agent_id")
            continue
        if aid in agent_ids:
            errors.append(f"duplicate agent_id: {aid}")
        agent_ids.add(aid)
        if "must_not_own" not in a:
            errors.append(f"{aid}: missing must_not_own")

    copilot = next((a for a in agents if a.get("agent_id") == "github_copilot_agent"), None)
    if not copilot:
        errors.append("github_copilot_agent lane missing")
    elif "autonomous_promote" not in copilot.get("must_not_own", []):
        errors.append("copilot must_not_own must include autonomous_promote")

    for cell in REQUIRED_TASK_CELLS:
        if cell not in task_owners:
            errors.append(f"task_cell_owners missing {cell}")

    if not dup_rules:
        errors.append("duplication_forbidden must be non-empty")

    promote_rule = next((r for r in dup_rules if r.get("task") == "brain_promote_same_window"), None)
    if not promote_rule or promote_rule.get("max_concurrent_writers") != 1:
        errors.append("brain_promote_same_window rule must enforce max_concurrent_writers=1")

    gov_text = GOVERNANCE.read_text(encoding="utf-8")
    for marker in ("One writer per task cell", "assist_only", "github_automation_registry_v1.json"):
        if marker not in gov_text:
            errors.append(f"PARALLEL_AUTOMATION_GOVERNANCE missing: {marker}")

    if errors:
        print("validate_parallel_automation_governance_v1: FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("validate_parallel_automation_governance_v1: ALL PASS")
    print(
        json.dumps(
            {
                "motor_count": len(motors),
                "agent_lane_count": len(agents),
                "task_cell_count": len(task_owners),
                "workflow_files": len(list(WORKFLOWS.glob("*.yml"))) if WORKFLOWS.is_dir() else 0,
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
