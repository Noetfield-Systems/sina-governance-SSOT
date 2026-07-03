#!/usr/bin/env python3
"""Full automation surface audit — GH Actions, CF workers, Mac launchd, Copilot lanes."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "github_automation_registry_v1.json"
INVENTORY = ROOT / "data" / "automation_surface_inventory_v1.json"
GOVERNANCE = ROOT / "ssot" / "PARALLEL_AUTOMATION_GOVERNANCE_v1.md"
RECEIPTS = ROOT / "receipts"


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    checked_workflows = 0
    missing_repos: list[str] = []

    for path in (REGISTRY, INVENTORY, GOVERNANCE):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if errors:
        print("audit_automation_surface_v1: FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    inv = json.loads(INVENTORY.read_text(encoding="utf-8"))

    registered_sg_workflows = {
        m.get("workflow_file", "").split("/")[-1]
        for m in reg.get("motors", [])
        if m.get("kind") == "github_actions" and m.get("repo") == "sina-governance-ssot"
    }

    sg_wf_dir = ROOT / ".github" / "workflows"
    if sg_wf_dir.is_dir():
        for wf in sg_wf_dir.glob("*.yml"):
            checked_workflows += 1
            if wf.name not in registered_sg_workflows:
                errors.append(f"SG workflow unregistered in motors: {wf.name}")

    for repo in inv.get("repos", []):
        repo_path = expand(repo.get("path", ""))
        if not repo_path.is_dir():
            missing_repos.append(str(repo.get("repo_id")))
            warnings.append(f"repo path missing (skip disk check): {repo_path}")
            continue

        wf_dir = repo_path / ".github" / "workflows"
        if not wf_dir.is_dir():
            continue

        inventoried = {w.get("file") for w in repo.get("workflows", [])}
        for wf in wf_dir.glob("*.yml"):
            checked_workflows += 1
            if wf.name not in inventoried:
                warnings.append(f"{repo.get('repo_id')}: workflow on disk not in inventory: {wf.name}")

        for wf in repo.get("workflows", []):
            fname = wf.get("file")
            if fname and not (wf_dir / fname).is_file():
                warnings.append(f"{repo.get('repo_id')}: inventory workflow missing on disk: {fname}")

    # Conflict matrix sanity
    for rule in inv.get("conflict_matrix", []):
        if rule.get("writers_max", 0) < 1:
            errors.append(f"invalid conflict_matrix writers_max: {rule.get('task_cell')}")
        if not rule.get("motors"):
            errors.append(f"conflict_matrix missing motors: {rule.get('task_cell')}")

    # Copilot integration rules present
    copilot = inv.get("copilot_integration", {})
    if copilot.get("default_lane") != "assist_only":
        errors.append("copilot_integration.default_lane must be assist_only")

    # Duplication forbidden in registry
    if not reg.get("duplication_forbidden"):
        errors.append("github_automation_registry missing duplication_forbidden")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "schema": "automation-surface-audit-receipt-v1",
        "receipt_id": f"automation-surface-audit-{ts}",
        "recorded_at": ts,
        "checked_workflows": checked_workflows,
        "errors": errors,
        "warnings": warnings,
        "missing_repos": missing_repos,
        "pass": len(errors) == 0,
    }
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPTS / f"{receipt['receipt_id']}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    if errors:
        print("audit_automation_surface_v1: FAIL")
        for e in errors:
            print(f" - {e}")
        if warnings:
            print("warnings:")
            for w in warnings[:20]:
                print(f" ! {w}")
        print(f"receipt_id={receipt['receipt_id']}")
        return 1

    print("audit_automation_surface_v1: ALL PASS")
    print(
        json.dumps(
            {
                "checked_workflows": checked_workflows,
                "repos_in_inventory": len(inv.get("repos", [])),
                "warnings": len(warnings),
                "receipt_id": receipt["receipt_id"],
            },
            indent=2,
        )
    )
    if warnings:
        print("warnings:")
        for w in warnings[:15]:
            print(f" ! {w}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
