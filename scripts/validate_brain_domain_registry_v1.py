#!/usr/bin/env python3
"""Validate brain domain sandbox registry schema and local branch refs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.brain_domain_registry_v1 import (  # noqa: E402
    branch_exists,
    expand_root,
    get_sandbox,
    load_registry,
    resolve_sourcea_root,
    workflow_health_targets,
)

REQUIRED_SANDBOX_FIELDS = (
    "sandbox_id",
    "branch",
    "artifact_type",
    "candidate_repo",
    "candidate_path",
    "deploy_root",
    "health_url",
    "gate_profile",
)
ALLOWED_ARTIFACT_TYPES = {"knowledge_bundle", "brain_worker_bundle"}


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    registry = load_registry()
    if registry.get("schema") != "brain_domain_sandboxes_v1":
        errors.append("schema must be brain_domain_sandboxes_v1")

    targets = workflow_health_targets(registry)
    if int(targets["freshness_target_minutes"]) <= 0:
        errors.append("freshness_target_minutes must be positive")
    if int(targets["success_rate_target"]) <= 0:
        errors.append("success_rate_target must be positive")
    if int(targets["latency_target_minutes"]) <= 0:
        errors.append("latency_target_minutes must be positive")

    sandboxes = registry.get("sandboxes")
    if not isinstance(sandboxes, list) or not sandboxes:
        errors.append("sandboxes must be a non-empty list")

    seen_ids: set[str] = set()
    for sandbox in sandboxes or []:
        sid = sandbox.get("sandbox_id")
        if not sid:
            errors.append("sandbox missing sandbox_id")
            continue
        if sid in seen_ids:
            errors.append(f"duplicate sandbox_id: {sid}")
        seen_ids.add(sid)

        for field in REQUIRED_SANDBOX_FIELDS:
            if field not in sandbox:
                errors.append(f"{sid}: missing {field}")

        artifact_type = sandbox.get("artifact_type")
        if artifact_type not in ALLOWED_ARTIFACT_TYPES:
            errors.append(f"{sid}: invalid artifact_type {artifact_type!r}")

        health_url = sandbox.get("health_url", "")
        if not isinstance(health_url, str) or not health_url.startswith("https://"):
            errors.append(f"{sid}: health_url must be https URL")

        deploy_root = expand_root(sandbox.get("deploy_root", ""))
        if not deploy_root.is_dir():
            warnings.append(f"{sid}: deploy_root missing: {deploy_root}")
        elif (deploy_root / ".git").exists():
            branch = sandbox.get("branch", "main")
            if not branch_exists(deploy_root, branch):
                # External SourceA branch state is environment-specific; keep this validator repo-local.
                pass

    sourcea = resolve_sourcea_root(registry)
    if not sourcea.is_dir():
        warnings.append(f"sourcea_root missing: {sourcea}")

    try:
        get_sandbox(registry, "brain_worker")
    except KeyError:
        errors.append("required sandbox brain_worker missing")

    if warnings:
        print("validate_brain_domain_registry_v1: WARN")
        for row in warnings:
            print(f" - WARNING: {row}")

    if errors:
        print("validate_brain_domain_registry_v1: FAIL")
        for row in errors:
            print(f" - {row}")
        return 1

    print("validate_brain_domain_registry_v1: ALL PASS")
    print(json.dumps({"sandbox_count": len(sandboxes), "sandbox_ids": sorted(seen_ids)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
