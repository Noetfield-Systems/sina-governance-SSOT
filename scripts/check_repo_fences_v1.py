#!/usr/bin/env python3
"""
check_repo_fences_v1.py

Phase 1 machine-enforceable repo fences for sina-governance-ssot.
Loads policy/repo_fences_v1.yaml and validates protected-path changes on merge to main.

Exit 0 -> PASS (or enforcement skipped for draft/non-main lanes)
Exit 1 -> violation(s) found
Exit 2 -> could not run (missing policy, git error, etc.)

Usage:
    python3 scripts/check_repo_fences_v1.py [--base SHA] [--head SHA] \\
        [--target-branch main] [--head-branch feat/x] [--pr-body TEXT] [--json out.json]
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print(
        "FATAL: PyYAML required (`pip install pyyaml --break-system-packages`).",
        file=sys.stderr,
    )
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "policy" / "repo_fences_v1.yaml"


def load_policy(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def run_git(args: list[str], cwd: Path) -> str:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "git failed")
    return proc.stdout


def norm_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def matches_any(path: str, patterns: list[str]) -> bool:
    for pat in patterns:
        p = pat.replace("\\", "/")
        if path == p.rstrip("/") or path.startswith(p.rstrip("/") + "/"):
            return True
        if fnmatch.fnmatch(path, p):
            return True
    return False


def is_exempt(path: str, exempt_paths: list[str]) -> bool:
    return matches_any(path, exempt_paths)


def is_protected(path: str, protected_zones: list[str]) -> bool:
    return matches_any(path, protected_zones)


def is_policy_law_path(path: str, globs: list[str]) -> bool:
    from pathlib import PurePath

    pure = PurePath(path)
    for g in globs:
        g = g.replace("\\", "/")
        if pure.match(g):
            return True
        if fnmatch.fnmatch(path, g):
            return True
    # Phase 1 explicit fallbacks when ** globs miss single-segment paths.
    if path.startswith("ssot/") and path.endswith(".md"):
        return True
    if path.startswith("policy/") and path.endswith((".yaml", ".yml")):
        return True
    name = pure.name
    if path.startswith("packages/noos-control-desk-v1/policy/"):
        return True
    if path.startswith("packages/noos-control-desk-v1/") and (
        "LAW" in name or name.startswith(("COPILOT_", "NOOS_", "SMART_"))
    ):
        return True
    return False


def branch_is_draft(branch: str, patterns: list[str]) -> bool:
    branch = branch.replace("refs/heads/", "")
    for pat in patterns:
        if fnmatch.fnmatch(branch, pat):
            return True
    return False


def changed_files(base: str, head: str, cwd: Path) -> list[str]:
    if base in ("", "0" * 40, head):
        return []
    out = run_git(["diff", "--name-only", f"{base}...{head}"], cwd)
    return [norm_path(line) for line in out.splitlines() if line.strip()]


def file_diff(base: str, head: str, path: str, cwd: Path) -> str:
    try:
        return run_git(["diff", f"{base}...{head}", "--", path], cwd)
    except RuntimeError:
        return ""


def text_has_reference(text: str, patterns: list[str]) -> bool:
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            return True
    return False


def commit_messages(base: str, head: str, cwd: Path) -> str:
    try:
        return run_git(["log", "--format=%B", f"{base}..{head}"], cwd)
    except RuntimeError:
        return ""


def load_package_status(policy: dict, cwd: Path, base: str | None = None) -> str | None:
    rel = policy.get("package_map")
    if not rel:
        return None
    if base:
        try:
            raw = run_git(["show", f"{base}:{rel}"], cwd)
            payload = json.loads(raw)
            return payload.get("package_status")
        except RuntimeError:
            pass
    path = cwd / rel
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("package_status")


def package_audit_pending(status: str | None, pending_values: list[str]) -> bool:
    if not status:
        return False
    return status in pending_values


def check_fake_active(diff_text: str, rule: dict) -> bool:
    """Return True if diff shows a forbidden ACTIVE promotion for this rule."""
    rid = rule["id"]
    if rid == "RF3_status_flip_from_audit_pending":
        removed = re.findall(r"^-\s*" + rule["from_pattern"], diff_text, flags=re.MULTILINE)
        added = re.findall(r"^\+\s*" + rule["to_pattern"], diff_text, flags=re.MULTILINE)
        return bool(removed and added)
    pattern = rule["pattern"]
    for line in diff_text.splitlines():
        if not line.startswith("+"):
            continue
        if re.search(pattern, line):
            return True
    return False


def enforceable_changes(
    all_changes: list[str],
    policy: dict,
) -> tuple[list[str], list[str], list[str]]:
    protected: list[str] = []
    policy_law: list[str] = []
    exempt_only: list[str] = []
    zones = policy.get("protected_zones", [])
    exempt = policy.get("exempt_paths", [])
    law_globs = policy.get("policy_law_globs", [])

    for path in all_changes:
        if is_exempt(path, exempt):
            exempt_only.append(path)
            continue
        if is_protected(path, zones):
            protected.append(path)
            if is_policy_law_path(path, law_globs):
                policy_law.append(path)
    return protected, policy_law, exempt_only


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 1 SG repo fence checker")
    parser.add_argument("--base", default="HEAD~1", help="Base git SHA for diff")
    parser.add_argument("--head", default="HEAD", help="Head git SHA for diff")
    parser.add_argument("--target-branch", default="", help="PR target branch (e.g. main)")
    parser.add_argument("--head-branch", default="", help="PR head branch name")
    parser.add_argument("--pr-body", default="", help="Pull request body text")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY), help="Policy YAML path")
    parser.add_argument("--json", dest="json_out", default="", help="Write JSON report")
    parser.add_argument("--repo-root", default=str(ROOT), help="Repo root")
    args = parser.parse_args()

    cwd = Path(args.repo_root).resolve()
    policy_path = Path(args.policy)
    if not policy_path.is_file():
        print(f"FATAL: missing policy {policy_path}", file=sys.stderr)
        return 2

    policy = load_policy(policy_path)
    violations: list[dict] = []
    notes: list[str] = []

    target = (args.target_branch or "").replace("refs/heads/", "")
    head_branch = (args.head_branch or "").replace("refs/heads/", "")
    enforce_targets = policy.get("enforce_target_branches", ["main"])

    try:
        changes = changed_files(args.base, args.head, cwd)
    except RuntimeError as exc:
        print(f"FATAL: git diff failed: {exc}", file=sys.stderr)
        return 2

    protected_changes, policy_law_changes, exempt_changes = enforceable_changes(changes, policy)

    skip_reason = None
    if target and target not in enforce_targets:
        skip_reason = f"target_branch={target} not in enforce list"
    elif head_branch and branch_is_draft(head_branch, policy.get("draft_branch_patterns", [])):
        skip_reason = f"draft_lane head_branch={head_branch}"

    if skip_reason:
        notes.append(f"enforcement_skipped: {skip_reason}")
        report = {
            "checker": "check_repo_fences_v1",
            "status": "PASS",
            "skipped": True,
            "skip_reason": skip_reason,
            "changed_files": changes,
            "violations": [],
        }
        print(f"check_repo_fences_v1: PASS (skipped — {skip_reason})")
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 0

    if not protected_changes:
        notes.append("no_protected_changes")
        report = {
            "checker": "check_repo_fences_v1",
            "status": "PASS",
            "changed_files": changes,
            "protected_changes": [],
            "violations": [],
            "notes": notes,
        }
        print("check_repo_fences_v1: PASS (no protected-path changes)")
        if args.json_out:
            Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return 0

    # Receipt-only lane: all changes exempt (receipt/status publication).
    if not protected_changes and changes:
        notes.append("receipt_or_exempt_only")

    receipt_sources = [
        args.pr_body or "",
        commit_messages(args.base, args.head, cwd),
    ]
    for path in changes:
        if path.startswith("receipts/"):
            receipt_sources.append(path)

    receipt_blob = "\n".join(receipt_sources)
    receipt_patterns = policy.get("receipt_reference_patterns", [])
    work_order_patterns = policy.get("work_order_reference_patterns", [])

    has_receipt_ref = text_has_reference(receipt_blob, receipt_patterns)
    has_work_order_ref = text_has_reference(receipt_blob, work_order_patterns)
    new_receipt_in_diff = any(p.startswith("receipts/") and p.endswith((".json", ".md")) for p in changes)

    if not (has_receipt_ref or new_receipt_in_diff):
        violations.append(
            {
                "rule_id": "RF_RECEIPT_REQUIRED",
                "severity": "red",
                "description": "Protected-path changes require a receipt reference in PR body, commits, or a new receipts/ file.",
                "files": protected_changes,
            }
        )

    if policy_law_changes and not (has_work_order_ref and (has_receipt_ref or new_receipt_in_diff)):
        missing = []
        if not has_work_order_ref:
            missing.append("work_order_id")
        if not (has_receipt_ref or new_receipt_in_diff):
            missing.append("receipt")
        violations.append(
            {
                "rule_id": "RF_POLICY_LAW_MUTATION",
                "severity": "red",
                "description": "Policy/law mutation requires work_order_id and receipt on merge to main.",
                "missing": missing,
                "files": policy_law_changes,
            }
        )

    pkg_status = load_package_status(policy, cwd, base=args.base)
    pending_values = policy.get("audit_pending_statuses", [])
    if package_audit_pending(pkg_status, pending_values):
        for path in protected_changes:
            if not path.endswith((".json", ".md", ".yaml", ".yml")):
                continue
            diff_text = file_diff(args.base, args.head, path, cwd)
            if not diff_text:
                continue
            for rule in policy.get("fake_active_rules", []):
                if check_fake_active(diff_text, rule):
                    violations.append(
                        {
                            "rule_id": rule["id"],
                            "severity": "red",
                            "description": rule["description"],
                            "file": path,
                            "package_status": pkg_status,
                        }
                    )

    status = "FAIL" if violations else "PASS"
    report = {
        "checker": "check_repo_fences_v1",
        "status": status,
        "target_branch": target or None,
        "head_branch": head_branch or None,
        "package_status": pkg_status,
        "changed_files": changes,
        "protected_changes": protected_changes,
        "policy_law_changes": policy_law_changes,
        "has_receipt_ref": has_receipt_ref or new_receipt_in_diff,
        "has_work_order_ref": has_work_order_ref,
        "violations": violations,
        "notes": notes,
    }

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if violations:
        print("check_repo_fences_v1: FAIL")
        for v in violations:
            print(f" - [{v['rule_id']}] {v['description']}")
            if v.get("files"):
                for f in v["files"][:8]:
                    print(f"     file: {f}")
            if v.get("file"):
                print(f"     file: {v['file']}")
        return 1

    print("check_repo_fences_v1: ALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
