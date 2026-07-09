#!/usr/bin/env python3
"""
run_negative_tests.py

Proves scripts/check_cost_policy.py actually rejects each known-bad fixture
(both free-text config patterns and registry-rule violations) and accepts
the known-good ones.

Run: python3 tests/run_negative_tests.py
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHECKER = os.path.join(REPO_ROOT, "scripts", "check_cost_policy.py")
POLICY = os.path.join(REPO_ROOT, "policy", "cost_policy.yaml")
FIXTURES = os.path.join(REPO_ROOT, "tests", "fixtures")

TEXT_CASES = [
    {"file": "bad_forbidden_model.md", "expect": "FAIL", "expect_rule": "COST_forbidden_model"},
    {"file": "bad_forbidden_effort.md", "expect": "FAIL", "expect_rule": "COST_forbidden_effort"},
    {"file": "bad_forbidden_trigger.md", "expect": "FAIL", "expect_rule": "COST_forbidden_trigger"},
    {"file": "good_clean_config.md", "expect": "PASS", "expect_rule": None},
]

REGISTRY_CASES = [
    {"file": "bad_registry_rcp1.json", "expect": "FAIL", "expect_rule": "RCP1_safe_fix_needs_receipt"},
    {"file": "bad_registry_rcp2.json", "expect": "FAIL", "expect_rule": "RCP2_unique_workflow_id"},
    {"file": "bad_registry_rcp3.json", "expect": "FAIL", "expect_rule": "RCP3_direct_write_only_for_deploy"},
    {"file": "bad_registry_rcp4.json", "expect": "FAIL", "expect_rule": "RCP4_model_policy_value_locked"},
    {"file": "good_registry.json", "expect": "PASS", "expect_rule": None},
]


def run_on_text_fixture(fixture_filename):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "policy"))
        shutil.copy(POLICY, os.path.join(tmp, "policy", "cost_policy.yaml"))
        shutil.copy(os.path.join(FIXTURES, fixture_filename), os.path.join(tmp, fixture_filename))
        out_json = os.path.join(tmp, "report.json")
        subprocess.run([sys.executable, CHECKER, tmp, "--json", out_json], capture_output=True, text=True)
        with open(out_json) as f:
            return json.load(f)


def run_on_registry_fixture(fixture_filename):
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "policy"))
        os.makedirs(os.path.join(tmp, ".noos"))
        shutil.copy(POLICY, os.path.join(tmp, "policy", "cost_policy.yaml"))
        shutil.copy(os.path.join(FIXTURES, fixture_filename), os.path.join(tmp, ".noos", "workflow_registry_v1.json"))
        out_json = os.path.join(tmp, "report.json")
        subprocess.run([sys.executable, CHECKER, tmp, "--json", out_json], capture_output=True, text=True)
        with open(out_json) as f:
            return json.load(f)


def evaluate(case, report):
    actual = report["status"]
    ok = (actual == case["expect"])
    if ok and case["expect_rule"]:
        rule_ids = {v["rule_id"] for v in report["violations_active"]}
        ok = case["expect_rule"] in rule_ids
    return ok, actual


def main():
    failures = []

    print("--- text-pattern cases ---")
    for case in TEXT_CASES:
        report = run_on_text_fixture(case["file"])
        ok, actual = evaluate(case, report)
        symbol = "✅" if ok else "❌"
        print(f"{symbol} {case['file']}: expected {case['expect']}"
              f"{' (' + case['expect_rule'] + ')' if case['expect_rule'] else ''}, got {actual}")
        if not ok:
            failures.append(case["file"])

    print("\n--- registry-rule cases ---")
    for case in REGISTRY_CASES:
        report = run_on_registry_fixture(case["file"])
        ok, actual = evaluate(case, report)
        symbol = "✅" if ok else "❌"
        print(f"{symbol} {case['file']}: expected {case['expect']}"
              f"{' (' + case['expect_rule'] + ')' if case['expect_rule'] else ''}, got {actual}")
        if not ok:
            failures.append(case["file"])

    total = len(TEXT_CASES) + len(REGISTRY_CASES)
    print()
    if failures:
        print(f"FAILED: {len(failures)}/{total} cases did not match spec: {failures}")
        sys.exit(1)
    else:
        print(f"ALL PASS: {total}/{total} cases match spec.")
        sys.exit(0)


if __name__ == "__main__":
    main()
