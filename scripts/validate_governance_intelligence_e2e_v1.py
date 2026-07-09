#!/usr/bin/env python3
"""E2E validator: progress scoring, selection cases, and thread intelligence."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "scripts/governance_intelligence_engine_v1.py"
RUBRIC = ROOT / "data/governance_completeness_rubric_v1.json"
THREAD_RUBRIC = ROOT / "data/governance_thread_rubric_v1.json"


def expand(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def run_audit_selection(paths: list[Path]) -> dict:
    joined = ",".join(str(p) for p in paths)
    cmd = [
        sys.executable,
        str(ENGINE),
        "audit-selection",
        "--json",
        "--cluster-by",
        "domain",
        "--paths",
        joined,
    ]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=90, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "audit-selection failed")
    return json.loads(proc.stdout)


def primary_for_case(result: dict, paths: list[Path]) -> str | None:
    path_set = {str(p) for p in paths}
    for cluster in result.get("clusters", []):
        decision = cluster.get("decision", {})
        primary = decision.get("primary_final", {}).get("path")
        if primary and primary in path_set:
            return primary
        for ranked in decision.get("deterministic_rank_order", []):
            if ranked.get("path") in path_set:
                return ranked["path"]
    return None


def run_thread_audit(root: Path) -> dict:
    cmd = [sys.executable, str(ENGINE), "thread-audit", "--json", "--root", str(root)]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=90, check=False)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "thread-audit failed")
    return json.loads(proc.stdout)


def validate_thread_cases(errors: list[str]) -> tuple[int, int]:
    if not THREAD_RUBRIC.is_file():
        return 0, 0
    rubric = json.loads(THREAD_RUBRIC.read_text(encoding="utf-8"))
    cases = rubric.get("e2e_thread_cases", [])
    passed = 0
    skipped = 0

    for case in cases:
        case_id = case.get("id", "unknown")
        root = expand(case.get("root", ""))
        if not root.exists():
            skipped += 1
            print(f"  SKIP {case_id}: root missing")
            continue
        try:
            result = run_thread_audit(root)
        except RuntimeError as exc:
            errors.append(f"{case_id}: {exc}")
            continue

        thread_id = case.get("thread_id")
        thread = next((t for t in result.get("threads", []) if t.get("thread_id") == thread_id), None)
        if not thread:
            errors.append(f"{case_id}: thread '{thread_id}' not found")
            continue

        expect_state = case.get("expect_completion_state")
        if expect_state and thread.get("completion_state") != expect_state:
            errors.append(
                f"{case_id}: expected state {expect_state}, got {thread.get('completion_state')}"
            )
            continue

        final = thread.get("final_carrier") or {}
        expect_role = case.get("expect_final_role")
        if expect_role and final.get("role") != expect_role:
            errors.append(f"{case_id}: expected role {expect_role}, got {final.get('role')}")
            continue

        expect_contains = case.get("expect_final_contains")
        if expect_contains and expect_contains not in str(final.get("path", "")):
            errors.append(f"{case_id}: final carrier missing '{expect_contains}'")
            continue

        expect_pending = case.get("expect_pending_contains")
        if expect_pending:
            pending_blob = json.dumps(thread.get("pending_items", []))
            if expect_pending not in pending_blob:
                errors.append(f"{case_id}: pending items missing '{expect_pending}'")
                continue

        min_quality = case.get("expect_change_quality_min")
        if min_quality is not None:
            net = thread.get("change_quality_summary", {}).get("net_quality_score", 0)
            if net < min_quality:
                errors.append(f"{case_id}: net change quality {net} < {min_quality}")
                continue

        passed += 1
        print(f"  PASS {case_id}: {thread_id} [{thread.get('completion_state')}]")

    return passed, skipped


def main() -> int:
    errors: list[str] = []
    rubric = json.loads(RUBRIC.read_text(encoding="utf-8"))
    fixtures = rubric.get("e2e_fixtures", {})
    cases = fixtures.get("cases", [])

    if not cases:
        print("validate_governance_intelligence_e2e_v1: SKIP (no fixtures)")
        return 0

    passed = 0
    skipped = 0

    for case in cases:
        case_id = case.get("id", "unknown")
        raw_paths = case.get("paths", [])
        resolved = [expand(p) for p in raw_paths]
        missing = [str(p) for p in resolved if not p.is_file()]
        if missing:
            skipped += 1
            print(f"  SKIP {case_id}: missing {len(missing)} fixture path(s)")
            continue

        try:
            result = run_audit_selection(resolved)
        except RuntimeError as exc:
            errors.append(f"{case_id}: {exc}")
            continue

        primary = primary_for_case(result, resolved)
        if not primary:
            errors.append(f"{case_id}: no primary selected among fixture paths")
            continue

        expect_contains = case.get("expect_primary_contains", "")
        expect_excludes = case.get("expect_primary_excludes", "")

        if expect_contains and expect_contains not in primary:
            errors.append(f"{case_id}: expected primary to contain '{expect_contains}', got {primary}")
            continue
        if expect_excludes and expect_excludes in primary:
            errors.append(f"{case_id}: expected primary to exclude '{expect_excludes}', got {primary}")
            continue

        passed += 1
        print(f"  PASS {case_id}: {Path(primary).name}")

    thread_passed, thread_skipped = validate_thread_cases(errors)

    story_root = expand("~/Desktop/Raw AI")
    if story_root.exists():
        proc = subprocess.run(
            [sys.executable, str(ENGINE), "session-story", "--root", str(story_root), "--plain-only"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(f"session-story failed: {proc.stderr.strip() or proc.stdout.strip()}")
        else:
            story = proc.stdout
            for needle in ("The whole story", "Repo structure", "most complete", "Brain Vocabulary"):
                if needle.lower() not in story.lower():
                    errors.append(f"session-story missing section hint: {needle}")
            if not errors:
                print("  PASS session_story_plain_language")

        proc2 = subprocess.run(
            [sys.executable, str(ENGINE), "second-pass-audit", "--root", str(story_root), "--json"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if proc2.returncode != 0:
            errors.append(f"second-pass-audit failed: {proc2.stderr.strip() or proc2.stdout.strip()}")
        else:
            payload = json.loads(proc2.stdout)
            sp = payload.get("second_pass", payload)
            sink_conf = sp.get("folder_intelligence", {}).get("confidence", 0)
            if sink_conf < 0.5:
                errors.append(f"second-pass sink confidence {sink_conf} < 0.5")
            from governance_intake_path_intelligence_v1 import run_coherence_checks
            from pathlib import Path as P

            errors.extend(run_coherence_checks(sp, json.loads((ROOT / "data/governance_intake_path_rubric_v1.json").read_text())))
            brain = next((t for t in sp.get("threads", []) if t.get("thread_id") == "sourcea_brain_registry_learning_gate"), {})
            fc = (brain.get("final_carrier") or {}).get("path", "")
            if fc and "v0_1_4" not in fc:
                errors.append("brain gate final must be v0_1_4 in second pass")
            if not errors:
                print(f"  PASS second_pass_evidence (confidence={sink_conf})")

        proc3 = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_intake_coherence_v1.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        print(proc3.stdout.strip())
        if proc3.returncode != 0:
            if proc3.stderr.strip():
                errors.append(proc3.stderr.strip())
            errors.append("validate_intake_coherence_v1 failed")

    if errors:
        print("validate_governance_intelligence_e2e_v1: FAIL")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"validate_governance_intelligence_e2e_v1: ALL PASS "
        f"(selection {passed}/{len(cases)}, threads {thread_passed}/{thread_passed + thread_skipped})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
