#!/usr/bin/env python3
"""
run_negative_tests.py — proves check_repo_fences_v1.py rejects known-bad cases.

Run: python3 tests/repo_fences/run_negative_tests.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts" / "check_repo_fences_v1.py"
POLICY = ROOT / "policy" / "repo_fences_v1.yaml"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


def init_repo(tmp: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "fence@test.local"], cwd=tmp, check=True)
    subprocess.run(["git", "config", "user.name", "fence-test"], cwd=tmp, check=True)
    (tmp / "policy").mkdir(parents=True, exist_ok=True)
    policy_text = POLICY.read_text(encoding="utf-8")
    (tmp / "policy" / "repo_fences_v1.yaml").write_text(policy_text, encoding="utf-8")
    (tmp / "data").mkdir(exist_ok=True)
    pkg = {
        "package_status": "SCAFFOLD_READY_AUDIT_PENDING",
        "members": [],
    }
    (tmp / "data" / "noos_control_desk_package_map_v1.json").write_text(
        json.dumps(pkg, indent=2) + "\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "."], cwd=tmp, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp, check=True, capture_output=True)


def run_case(
    tmp: Path,
    *,
    target_branch: str,
    head_branch: str,
    pr_body: str,
    mutate,
    expect: str,
    rule_id: str | None,
) -> tuple[bool, str]:
    init_repo(tmp)
    base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp, text=True).strip()
    mutate(tmp)
    subprocess.run(["git", "add", "-A"], cwd=tmp, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "-m", "case change"],
        cwd=tmp,
        check=True,
        capture_output=True,
    )
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=tmp, text=True).strip()
    proc = subprocess.run(
        [
            sys.executable,
            str(CHECKER),
            "--base",
            base,
            "--head",
            head,
            "--target-branch",
            target_branch,
            "--head-branch",
            head_branch,
            "--pr-body",
            pr_body,
            "--repo-root",
            str(tmp),
            "--policy",
            str(tmp / "policy" / "repo_fences_v1.yaml"),
        ],
        capture_output=True,
        text=True,
    )
    out = proc.stdout + proc.stderr
    if expect == "PASS":
        ok = proc.returncode == 0
        return ok, out
    ok = proc.returncode != 0
    if rule_id and rule_id not in out:
        return False, out + f"\n(expected rule {rule_id})"
    return ok, out


def main() -> int:
    failures = 0

    # PASS: draft branch lane skips enforcement
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def no_op(_: Path) -> None:
            (tmp / "data" / "touch.json").write_text("{}\n", encoding="utf-8")

        ok, out = run_case(
            tmp,
            target_branch="main",
            head_branch="draft/step6-fence",
            pr_body="",
            mutate=no_op,
            expect="PASS",
            rule_id=None,
        )
        if not ok:
            print("FAIL draft branch should PASS:", out)
            failures += 1
        else:
            print("PASS draft branch skip")

    # FAIL: protected change without receipt
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def mutate_no_receipt(t: Path) -> None:
            (t / "ssot").mkdir(exist_ok=True)
            (t / "ssot" / "TEST.md").write_text("# test\n", encoding="utf-8")

        ok, out = run_case(
            tmp,
            target_branch="main",
            head_branch="feat/fence",
            pr_body="no proof here",
            mutate=mutate_no_receipt,
            expect="FAIL",
            rule_id="RF_RECEIPT_REQUIRED",
        )
        if not ok:
            print("FAIL missing receipt should FAIL:", out)
            failures += 1
        else:
            print("PASS missing receipt blocked")

    # FAIL: fake ACTIVE package_status while audit-pending
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def mutate_fake_active(t: Path) -> None:
            path = t / "data" / "noos_control_desk_package_map_v1.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["package_status"] = "ACTIVE"
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

        ok, out = run_case(
            tmp,
            target_branch="main",
            head_branch="feat/fence",
            pr_body="receipt_id: receipts/fake-test.json",
            mutate=mutate_fake_active,
            expect="FAIL",
            rule_id="RF1_package_status_active",
        )
        if not ok:
            print("FAIL fake ACTIVE should FAIL:", out)
            failures += 1
        else:
            print("PASS fake ACTIVE blocked")

    # FAIL: policy/law mutation without work_order_id
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def mutate_policy(t: Path) -> None:
            (t / "ssot").mkdir(exist_ok=True)
            (t / "ssot" / "LAW.md").write_text("# law change\n", encoding="utf-8")

        ok, out = run_case(
            tmp,
            target_branch="main",
            head_branch="feat/fence",
            pr_body="receipt_id: receipts/ok.json",
            mutate=mutate_policy,
            expect="FAIL",
            rule_id="RF_POLICY_LAW_MUTATION",
        )
        if not ok:
            print("FAIL policy mutation without work_order should FAIL:", out)
            failures += 1
        else:
            print("PASS policy mutation without work_order blocked")

    # PASS: receipt-only publication exempt
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)

        def mutate_receipt_only(t: Path) -> None:
            (t / "receipts").mkdir(exist_ok=True)
            (t / "receipts" / "status-publish.json").write_text("{}\n", encoding="utf-8")

        ok, out = run_case(
            tmp,
            target_branch="main",
            head_branch="feat/fence",
            pr_body="",
            mutate=mutate_receipt_only,
            expect="PASS",
            rule_id=None,
        )
        if not ok:
            print("FAIL receipt-only should PASS:", out)
            failures += 1
        else:
            print("PASS receipt-only lane")

    if failures:
        print(f"repo_fences negative tests: FAIL ({failures} cases)")
        return 1

    print("repo_fences negative tests: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
