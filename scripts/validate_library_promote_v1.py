#!/usr/bin/env python3
"""Light validator — library promote manifest builds and target map integrity."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts/governance_intelligence_engine_v1.py"
TARGET_MAP = ROOT / "data/governance_library_target_map_v1.json"


def main() -> int:
    errors: list[str] = []
    if not TARGET_MAP.is_file():
        errors.append("missing data/governance_library_target_map_v1.json")
    else:
        payload = json.loads(TARGET_MAP.read_text(encoding="utf-8"))
        if not payload.get("artifact_targets"):
            errors.append("artifact_targets empty")
        if not payload.get("placeholder_targets"):
            errors.append("placeholder_targets empty")

    downloads = Path.home() / "Downloads"
    if downloads.is_dir():
        proc = subprocess.run(
            [sys.executable, str(ENGINE), "promote-library-drafts", "--root", str(downloads), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(f"promote-library-drafts dry-run failed: {proc.stderr[:200]}")
        proc2 = subprocess.run(
            [sys.executable, str(ENGINE), "promote-intake-artifacts", "--root", str(downloads), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if proc2.returncode != 0:
            errors.append(f"promote-intake-artifacts dry-run failed: {proc2.stderr[:200]}")
        else:
            intake = json.loads(proc2.stdout)
            manifest = intake.get("manifest", {})
            arts = manifest.get("artifacts", []) if isinstance(manifest, dict) else manifest
            ids = [r.get("artifact_id") for r in arts if isinstance(r, dict)]
            if (downloads / "NOETFIELD_COHERENT_SYSTEM_SPEC_v1.md").is_file():
                if "noetfield-coherent-system-spec-v1" not in ids:
                    errors.append("missing noetfield-coherent-system-spec-v1 in intake manifest")
            if "deep-research-founder-intent-v1" in ids:
                errors.append("deep-research must not appear in intake manifest")
    else:
        print("validate_library_promote_v1: SKIP Downloads fixture missing")

    if errors:
        print("validate_library_promote_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("validate_library_promote_v1: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
