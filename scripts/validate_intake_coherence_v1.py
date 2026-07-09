#!/usr/bin/env python3
"""Coherence validator — intake machine must make sense; fails on contradictions."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts/governance_intelligence_engine_v1.py"
PATH_RUBRIC = ROOT / "data/governance_intake_path_rubric_v1.json"


def expand(p: str) -> Path:
    return Path(p).expanduser().resolve()


def main() -> int:
    errors: list[str] = []
    rubric = json.loads(PATH_RUBRIC.read_text(encoding="utf-8"))
    fixture = rubric.get("fixture_roots", {}).get("raw_ai_example", "~/Desktop/Raw AI")
    root = expand(fixture)
    if not root.exists():
        print(f"validate_intake_coherence_v1: SKIP (no fixture at {fixture})")
        return 0

    proc = subprocess.run(
        [sys.executable, str(ENGINE), "second-pass-audit", "--root", str(root), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    if proc.returncode != 0:
        print("validate_intake_coherence_v1: FAIL")
        print(proc.stderr or proc.stdout)
        return 1

    payload = json.loads(proc.stdout)
    second = payload.get("second_pass", payload)

    from governance_intake_path_intelligence_v1 import run_coherence_checks

    errors.extend(run_coherence_checks(second, rubric))

    for thread in second.get("threads", []):
        tid = thread.get("thread_id")
        ev = thread.get("evidence_summary", {})
        final = (thread.get("final_carrier") or {}).get("path", "")
        earlier = ev.get("earlier_copies", 0)
        if tid == "sourcea_brain_registry_learning_gate" and earlier < 5:
            errors.append(f"{tid}: expected >=5 earlier copies demoted, got {earlier}")
        if final and "learning gate" in tid.replace("_", " "):
            if "v0_1_4" not in final.lower() and "v0.1.4" not in final.lower():
                errors.append(f"{tid}: winner must be v0.1.4 carrier")

    sink = second.get("folder_intelligence", {})
    if sink.get("confidence", 0) < rubric.get("coherence_rules", {}).get("min_sink_confidence", 0.5):
        errors.append(f"probable sink confidence too low: {sink.get('confidence')}")

    if errors:
        print("validate_intake_coherence_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        "validate_intake_coherence_v1: ALL PASS "
        f"(threads={second.get('thread_count')}, "
        f"sink_confidence={sink.get('confidence')}, "
        f"corrections={second.get('second_pass_summary', {}).get('corrections_count', 0)})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
