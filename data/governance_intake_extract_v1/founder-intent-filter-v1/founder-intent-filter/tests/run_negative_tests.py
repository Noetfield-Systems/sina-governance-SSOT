#!/usr/bin/env python3
"""
run_negative_tests.py

Proves scripts/check_founder_runtime_dependency.py actually rejects each known-bad
fixture and accepts the known-good one. This IS the "negative tests proving the
checker rejects..." deliverable from the deep-research-report follow-up instructions.

Run: python3 tests/run_negative_tests.py
Exit 0 if all expectations hold, exit 1 if the checker's behavior drifts from spec.
"""
import json
import os
import subprocess
import sys
import tempfile
import shutil

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHECKER = os.path.join(REPO_ROOT, "scripts", "check_founder_runtime_dependency.py")
POLICY = os.path.join(REPO_ROOT, "policy", "founder_intent.yaml")
FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures")

CASES = [
    {"file": "bad_founder_approval.md", "expect": "FAIL", "expect_rule": "R1_no_founder_specific_approval"},
    {"file": "bad_manual_merge.md", "expect": "FAIL", "expect_rule": "R5_evidence_based_merge_and_phase_unlock"},
    {"file": "bad_l5_normal_stage.md", "expect": "FAIL", "expect_rule": "R4_L5_is_anomaly_only"},
    {"file": "bad_blocker_no_repair.md", "expect": "FAIL", "expect_rule": "R3_denial_must_preserve_progress"},
    {"file": "bad_frozen_proof_target.md", "expect": "FAIL", "expect_rule": "R7_frozen_proof_targets_not_hard_blockers"},
    {"file": "good_clean_policy.md", "expect": "PASS", "expect_rule": None},
]


def run_checker_on_single_file(fixture_filename):
    """Isolate one fixture at a time in a temp repo so cases don't contaminate each other."""
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "policy"))
        shutil.copy(POLICY, os.path.join(tmp, "policy", "founder_intent.yaml"))
        shutil.copy(os.path.join(FIXTURES, fixture_filename), os.path.join(tmp, fixture_filename))
        out_json = os.path.join(tmp, "report.json")
        result = subprocess.run(
            [sys.executable, CHECKER, tmp, "--json", out_json],
            capture_output=True, text=True
        )
        with open(out_json) as f:
            report = json.load(f)
        return result.returncode, report


def main():
    failures = []
    for case in CASES:
        returncode, report = run_checker_on_single_file(case["file"])
        actual = report["status"]
        ok = (actual == case["expect"])
        if ok and case["expect_rule"]:
            rule_ids = {v["rule_id"] for v in report["violations_active"]}
            ok = case["expect_rule"] in rule_ids

        status_symbol = "✅" if ok else "❌"
        print(f"{status_symbol} {case['file']}: expected {case['expect']}"
              f"{' (' + case['expect_rule'] + ')' if case['expect_rule'] else ''}, got {actual}")

        if not ok:
            failures.append(case["file"])

    print()
    if failures:
        print(f"FAILED: {len(failures)}/{len(CASES)} cases did not match spec: {failures}")
        sys.exit(1)
    else:
        print(f"ALL PASS: {len(CASES)}/{len(CASES)} cases match spec.")
        sys.exit(0)


if __name__ == "__main__":
    main()
