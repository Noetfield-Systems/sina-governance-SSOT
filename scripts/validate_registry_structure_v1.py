#!/usr/bin/env python3
"""Strict structure tree + registry + thread registry validator."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance_artifact_registry_v1.json"
STRUCTURE_TREE = ROOT / "data/governance_structure_tree_v1.json"
THREAD_REGISTRY = ROOT / "data/governance_thread_registry_v1.json"
OPS = ROOT / "scripts/governance_registry_ops_v1.py"


def main() -> int:
    errors: list[str] = []

    for path in (REGISTRY, STRUCTURE_TREE, THREAD_REGISTRY, OPS):
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if not REGISTRY.is_file():
        print("validate_registry_structure_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    tree = json.loads(STRUCTURE_TREE.read_text(encoding="utf-8"))
    threads = json.loads(THREAD_REGISTRY.read_text(encoding="utf-8"))

    if tree.get("schema") != "governance_structure_tree_v1":
        errors.append("structure tree schema mismatch")
    if threads.get("schema") != "governance_thread_registry_v1":
        errors.append("thread registry schema mismatch")

    sys.path.insert(0, str(ROOT / "scripts"))
    from governance_registry_ops_v1 import validate_structure_strict

    errors.extend(validate_structure_strict(registry, tree))

    required_machines = {
        "governance_registry_ops",
        "validate_registry_structure",
        "governance_intelligence_engine",
    }
    machine_ids = {m.get("machine_id") for m in tree.get("machines", [])}
    for mid in required_machines:
        if mid not in machine_ids:
            errors.append(f"structure tree missing machine: {mid}")

    layer_keys = set(tree.get("layers", {}))
    reg_layers = set(registry.get("layer_model", {}))
    if layer_keys != reg_layers:
        errors.append("structure tree layers must match registry layer_model keys")

    if errors:
        print("validate_registry_structure_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("validate_registry_structure_v1: ALL PASS")
    print(
        json.dumps(
            {
                "artifacts": len(registry.get("artifacts", [])),
                "layers": len(layer_keys),
                "machines": len(tree.get("machines", [])),
                "threads": len(threads.get("threads", [])),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
