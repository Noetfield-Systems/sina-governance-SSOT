#!/usr/bin/env python3
"""Production validator for governance intelligence registry, audit, and pointers."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance_artifact_registry_v1.json"
REVIEW_QUEUE = ROOT / "data/governance_review_queue_v1.json"
AUTHORITY = ROOT / "ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md"
PIPELINE = ROOT / "ssot/GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md"
ENGINE = ROOT / "scripts/governance_intelligence_engine_v1.py"
AGENTS = ROOT / "AGENTS.md"
COPILOT = ROOT / ".github/copilot-instructions.md"
CANON_JSON = ROOT / "data/founder_canon_v1.json"
DISPATCH = ROOT / "docs/MAC_CURSOR_VENTURE_DISPATCH_v1.md"


def main() -> int:
    errors: list[str] = []

    required = (
        REGISTRY,
        REVIEW_QUEUE,
        AUTHORITY,
        PIPELINE,
        ENGINE,
        AGENTS,
        COPILOT,
        CANON_JSON,
        DISPATCH,
    )
    for path in required:
        if not path.is_file():
            errors.append(f"missing {path.relative_to(ROOT)}")

    if not REGISTRY.is_file():
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1

    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if reg.get("schema") != "governance_artifact_registry_v1":
        errors.append("registry schema must be governance_artifact_registry_v1")
    if not reg.get("production_grade"):
        errors.append("registry production_grade must be true")

    layers = set(reg.get("layer_model", {}))
    statuses = set(reg.get("status_model", {}))
    domains = set(reg.get("domains", []))
    artifact_ids: set[str] = set()
    paths_seen: set[str] = set()
    seen_ids: set[str] = set()

    for art in reg.get("artifacts", []):
        aid = art.get("artifact_id")
        if aid:
            artifact_ids.add(aid)

    for art in reg.get("artifacts", []):
        aid = art.get("artifact_id")
        if not aid:
            errors.append("artifact missing artifact_id")
            continue
        if aid in seen_ids:
            errors.append(f"duplicate artifact_id: {aid}")
        seen_ids.add(aid)

        rel = art.get("path", "")
        if rel in paths_seen:
            errors.append(f"duplicate artifact path: {rel}")
        paths_seen.add(rel)

        for field in (
            "path",
            "layer",
            "domain",
            "version",
            "status",
            "authority_rank",
            "owner_repo",
            "saved_at",
            "affects_layers",
        ):
            if field not in art:
                errors.append(f"{aid}: missing {field}")

        if art.get("layer") not in layers:
            errors.append(f"{aid}: invalid layer {art.get('layer')}")
        if art.get("domain") not in domains:
            errors.append(f"{aid}: invalid domain {art.get('domain')}")
        if art.get("status") not in statuses:
            errors.append(f"{aid}: invalid status {art.get('status')}")

        if rel and not str(rel).startswith("P"):
            full = ROOT / rel
            if not full.is_file():
                errors.append(f"{aid}: missing registered path {rel}")

        for dep in art.get("depends_on", []) + art.get("amends", []):
            if dep not in artifact_ids:
                errors.append(f"{aid}: unknown lineage target {dep}")

    required_ids = {
        "gov-structure-authority-v1",
        "governance-intelligence-pipeline-v1",
        "founder-canon-v1",
        "governance-artifact-registry-v1",
    }
    for rid in required_ids:
        if rid not in artifact_ids:
            errors.append(f"registry must include {rid}")

    pointer = "GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md"
    pipeline_pointer = "GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md"
    engine_pointer = "governance_intelligence_engine_v1.py"

    agents = AGENTS.read_text(encoding="utf-8") if AGENTS.is_file() else ""
    copilot = COPILOT.read_text(encoding="utf-8") if COPILOT.is_file() else ""
    dispatch = DISPATCH.read_text(encoding="utf-8") if DISPATCH.is_file() else ""
    canon = json.loads(CANON_JSON.read_text(encoding="utf-8")) if CANON_JSON.is_file() else {}

    for label, text in (
        ("AGENTS.md", agents),
        (".github/copilot-instructions.md", copilot),
        ("docs/MAC_CURSOR_VENTURE_DISPATCH_v1.md", dispatch),
    ):
        if pointer not in text:
            errors.append(f"{label} must reference {pointer}")
        if pipeline_pointer not in text and label != "docs/MAC_CURSOR_VENTURE_DISPATCH_v1.md":
            errors.append(f"{label} must reference {pipeline_pointer}")
        if engine_pointer not in text and label == "AGENTS.md":
            errors.append("AGENTS.md must reference governance_intelligence_engine_v1.py")

    if canon.get("governance_structure_authority") != "ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md":
        errors.append("founder_canon_v1.json governance_structure_authority mismatch")
    if canon.get("governance_intelligence_pipeline") != "ssot/GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md":
        errors.append("founder_canon_v1.json governance_intelligence_pipeline mismatch")
    if canon.get("governance_artifact_registry") != "data/governance_artifact_registry_v1.json":
        errors.append("founder_canon_v1.json governance_artifact_registry mismatch")

    queue = json.loads(REVIEW_QUEUE.read_text(encoding="utf-8")) if REVIEW_QUEUE.is_file() else {}
    if queue.get("schema") != "governance_review_queue_v1":
        errors.append("review queue schema must be governance_review_queue_v1")

    proc = subprocess.run(
        [sys.executable, str(ENGINE), "audit", "--json", "--no-write-queue"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if proc.returncode != 0:
        errors.append("governance_intelligence_engine_v1.py audit failed")
        if proc.stdout.strip():
            errors.append(f"audit stdout: {proc.stdout.strip()[-400:]}")
        if proc.stderr.strip():
            errors.append(f"audit stderr: {proc.stderr.strip()[-400:]}")

    if errors:
        print("validate_governance_intelligence_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    e2e = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_governance_intelligence_e2e_v1.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    print(e2e.stdout.strip())
    if e2e.returncode != 0:
        if e2e.stderr.strip():
            print(e2e.stderr.strip(), file=sys.stderr)
        return 1

    coherence = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_intake_coherence_v1.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    print(coherence.stdout.strip())
    if coherence.returncode != 0:
        if coherence.stderr.strip():
            print(coherence.stderr.strip(), file=sys.stderr)
        return 1

    structure = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_registry_structure_v1.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    print(structure.stdout.strip())
    if structure.returncode != 0:
        if structure.stderr.strip():
            print(structure.stderr.strip(), file=sys.stderr)
        return 1

    print("validate_governance_intelligence_v1: ALL PASS")
    print(
        json.dumps(
            {
                "artifacts": len(reg.get("artifacts", [])),
                "entry_points": len(reg.get("entry_points", [])),
                "review_queue_open": queue.get("open_count", 0),
                "review_queue_high": queue.get("high_severity_count", 0),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
