#!/usr/bin/env python3
"""Proof validator — evidence intake sink (Raw AI fixture is example only, not Tag name law)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts/governance_intelligence_engine_v1.py"
FIXTURE_ROOT = Path.home() / "Desktop/Raw AI"

REQUIRED_SINK_ARTIFACTS = (
    "sourcea-brain-registry-learning-gate-v0-1-4",
    "sourcea-brain-registry-learning-gate-impl-prompt-v0-1-4",
    "ssot-conflict-log-runtime-rules-v0-1-2",
    "ssot-proposal-artifact-versioning-v0-1-1",
    "copilot-automation-cost-profile-v1",
    "founder-intent-filter-v1",
    "smart-production-cost-law-v2",
    "noos-control-desk-v2",
)

REQUIRED_ZIP_SOURCES = (
    "smart-production-cost-law-v2",
    "noos-control-desk-v2",
)

FORBIDDEN_IN_MANIFEST = ("deep-research-founder-intent-v1",)


def main() -> int:
    errors: list[str] = []
    if not FIXTURE_ROOT.is_dir():
        print(f"validate_intake_sink_v1: SKIP (no fixture at {FIXTURE_ROOT})")
        return 0

    proc = subprocess.run(
        [sys.executable, str(ENGINE), "promote-intake-drafts", "--root", str(FIXTURE_ROOT), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if proc.returncode != 0:
        errors.append(f"promote-intake-drafts failed: {proc.stderr[:300] or proc.stdout[:300]}")
    else:
        payload = json.loads(proc.stdout)
        manifest = payload.get("manifest", {})
        arts = manifest.get("artifacts", [])
        found_ids = {a.get("artifact_id") for a in arts}
        sink = manifest.get("sink_detection", {})

        if not sink.get("sink_relative_dirs"):
            errors.append("evidence sink detection returned no sink dirs")
        if sink.get("confidence", 0) < 0.5:
            errors.append(f"sink confidence too low: {sink.get('confidence')}")
        if manifest.get("counts", {}).get("from_zip", 0) < 2:
            errors.append(
                f"expected >=2 zip-sourced artifacts in sink manifest, got {manifest.get('counts', {}).get('from_zip')}"
            )

        for aid in REQUIRED_SINK_ARTIFACTS:
            if aid not in found_ids:
                errors.append(f"sink manifest missing required artifact: {aid}")

        for aid in FORBIDDEN_IN_MANIFEST:
            if aid in found_ids:
                errors.append(f"sink manifest must not include: {aid}")

        by_id = {a["artifact_id"]: a for a in arts}
        for aid in REQUIRED_ZIP_SOURCES:
            row = by_id.get(aid)
            if row and row.get("source_kind") != "zip_bundle":
                errors.append(f"{aid} must be sourced from zip bundle, got {row.get('source_kind')}")

    if errors:
        print("validate_intake_sink_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        "validate_intake_sink_v1: ALL PASS "
        f"(artifacts={len(REQUIRED_SINK_ARTIFACTS)}, zip_sources={len(REQUIRED_ZIP_SOURCES)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
