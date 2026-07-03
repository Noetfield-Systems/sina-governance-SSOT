#!/usr/bin/env python3
"""Validate Copilot/GitHub Agent PR template and registry assist_only gates."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / ".github" / "pull_request_template.md"
REGISTRY = ROOT / "data" / "github_automation_registry_v1.json"

REQUIRED_MARKERS = (
    "lane:",
    "motor_id_or_human_gate:",
    "Task cell:",
    "receipt_id:",
    "Non-duplication check",
    "assist_only",
)

COPILOT_FORBIDDEN = (
    "autonomous_promote",
    "register_brain_artifact",
    "cross_repo_writes",
)


def main() -> int:
    errors: list[str] = []

    if not TEMPLATE.is_file():
        errors.append("missing .github/pull_request_template.md")
    else:
        text = TEMPLATE.read_text(encoding="utf-8")
        for marker in REQUIRED_MARKERS:
            if marker not in text:
                errors.append(f"PR template missing marker: {marker}")

    if not REGISTRY.is_file():
        errors.append("missing github_automation_registry_v1.json")
    else:
        reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
        copilot = next(
            (a for a in reg.get("agent_lanes", []) if a.get("agent_id") == "github_copilot_agent"),
            None,
        )
        if not copilot:
            errors.append("github_copilot_agent missing from registry")
        else:
            if copilot.get("lane") != "assist_only":
                errors.append("github_copilot_agent lane must be assist_only")
            must_not = copilot.get("must_not_own", [])
            for forbidden in COPILOT_FORBIDDEN:
                if forbidden not in must_not:
                    errors.append(f"copilot must_not_own missing: {forbidden}")

    if errors:
        print("validate_copilot_pr_template_v1: FAIL")
        for e in errors:
            print(f" - {e}")
        return 1

    print("validate_copilot_pr_template_v1: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
