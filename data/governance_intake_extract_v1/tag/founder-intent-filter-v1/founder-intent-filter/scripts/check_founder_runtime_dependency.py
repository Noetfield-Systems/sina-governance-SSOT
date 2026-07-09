#!/usr/bin/env python3
"""
check_founder_runtime_dependency.py

Scans governance/order/workflow files in the repo for violations of
FOUNDER_INTENT_FILTER.md, as encoded in policy/founder_intent.yaml.

Exit code 0  -> no unexempted violations found (CI passes)
Exit code 1  -> at least one unexempted violation found (CI gate fails)
Exit code 2  -> could not run (bad policy file, no PyYAML, etc.) - never silently PASS

Usage:
    python3 scripts/check_founder_runtime_dependency.py [repo_root] [--policy path] [--json out.json]

This script is intentionally dependency-light (stdlib + PyYAML only) and repo-local:
no OPA, no Kubernetes, no network calls. It is v1 of a lightweight enforcement layer,
per FOUNDER_INTENT_FILTER.md's explicit "downscope" instruction.
"""

import argparse
import fnmatch
import glob
import json
import os
import re
import sys
from datetime import date

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML is required (`pip install pyyaml --break-system-packages`). "
          "Refusing to silently pass without running checks.", file=sys.stderr)
    sys.exit(2)


def load_policy(policy_path):
    with open(policy_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_files(repo_root, include_globs, exclude_globs):
    matched = set()
    for pattern in include_globs:
        for path in glob.glob(os.path.join(repo_root, pattern), recursive=True):
            if os.path.isfile(path):
                matched.add(os.path.relpath(path, repo_root))

    def is_excluded(rel_path):
        norm = rel_path.replace(os.sep, "/")
        for ex in exclude_globs:
            ex_norm = ex.replace(os.sep, "/")
            candidates = {ex_norm, ex_norm.lstrip("*/")}
            for cand in candidates:
                if fnmatch.fnmatch(norm, cand) or fnmatch.fnmatch(os.path.basename(norm), cand):
                    return True
        return False

    return sorted(p for p in matched if not is_excluded(p))


def line_is_tagged_exempt(text_block, allow_tags):
    if not allow_tags:
        return False
    return any(tag.lower() in text_block.lower() for tag in allow_tags)


def check_regex_rule(rule, file_path, content):
    """Return list of violation dicts for a single regex-based rule."""
    violations = []
    patterns = rule.get("violation_patterns", [])
    allow_tags = rule.get("allow_if_tagged", [])
    require_nearby_any = rule.get("require_nearby_any")

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        for pat in patterns:
            if re.search(pat, line):
                # context window: a few lines around the match, for tag-exemption and nearby-keyword checks
                window = "\n".join(lines[max(0, lineno - 3):lineno + 2])

                if line_is_tagged_exempt(window, allow_tags):
                    continue

                if require_nearby_any:
                    if any(kw.lower() in window.lower() for kw in require_nearby_any):
                        continue  # repair/reroute/escape keyword nearby -> not a violation

                violations.append({
                    "rule_id": rule["id"],
                    "severity": rule.get("severity", "unknown"),
                    "file": file_path,
                    "line": lineno,
                    "matched_text": line.strip(),
                    "description": rule.get("description", "")
                })
    return violations


def check_frequency_rule(rule, repo_root):
    """R6-style rule: count recurring founder-judgment entries across receipts/*.json."""
    violations = []
    threshold = rule.get("threshold", 3)
    evidence_glob = rule.get("evidence_source", "receipts/*.json")
    receipt_paths = glob.glob(os.path.join(repo_root, evidence_glob))

    judgment_counts = {}
    for rp in receipt_paths:
        try:
            with open(rp, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for entry in data.get("founder_judgments_requested", []):
            key = entry.get("topic", "unspecified")
            judgment_counts[key] = judgment_counts.get(key, 0) + 1

    for topic, count in judgment_counts.items():
        if count > threshold:
            violations.append({
                "rule_id": rule["id"],
                "severity": rule.get("severity", "unknown"),
                "file": rule.get("evidence_source", "receipts/*.json"),
                "line": None,
                "matched_text": f"topic '{topic}' asked of founder {count} times (threshold {threshold})",
                "description": rule.get("description", "")
            })
    return violations


def apply_exceptions(violations, exceptions, today):
    """Drop violations covered by a logged, non-expired exception."""
    active = []
    dropped = []
    for v in violations:
        matched_exception = None
        for ex in exceptions or []:
            if ex.get("rule_id") != v["rule_id"]:
                continue
            scope = ex.get("scope", "")
            if scope and not fnmatch.fnmatch(v["file"], scope) and scope != v["file"]:
                continue
            expires = ex.get("expires")
            if expires:
                try:
                    if date.fromisoformat(expires) < today:
                        continue  # expired exception does NOT cover this violation
                except ValueError:
                    continue
            matched_exception = ex
            break
        if matched_exception:
            v["exempted_by"] = matched_exception
            dropped.append(v)
        else:
            active.append(v)
    return active, dropped


def main():
    parser = argparse.ArgumentParser(description="Check repo for Founder Intent Filter violations.")
    parser.add_argument("repo_root", nargs="?", default=".", help="Repo root to scan (default: cwd)")
    parser.add_argument("--policy", default=None, help="Path to founder_intent.yaml")
    parser.add_argument("--json", default=None, help="Write full JSON report to this path")
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    policy_path = args.policy or os.path.join(repo_root, "policy", "founder_intent.yaml")

    if not os.path.isfile(policy_path):
        print(f"FATAL: policy file not found at {policy_path}", file=sys.stderr)
        sys.exit(2)

    policy = load_policy(policy_path)
    scan_cfg = policy.get("scan", {})
    files = collect_files(repo_root, scan_cfg.get("include_globs", ["**/*.md"]),
                           scan_cfg.get("exclude_globs", []))

    all_violations = []
    for rule in policy.get("rules", []):
        if rule.get("mode") == "frequency-check":
            all_violations.extend(check_frequency_rule(rule, repo_root))
            continue
        for rel_path in files:
            full_path = os.path.join(repo_root, rel_path)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue
            all_violations.extend(check_regex_rule(rule, rel_path, content))

    active, exempted = apply_exceptions(all_violations, policy.get("exceptions", []), date.today())

    report = {
        "checker": "check_founder_runtime_dependency.py",
        "policy_version": policy.get("version"),
        "files_scanned": len(files),
        "violations_found": len(all_violations),
        "violations_active": active,
        "violations_exempted": exempted,
        "status": "FAIL" if active else "PASS"
    }

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

    if active:
        print(f"❌ FOUNDER INTENT FILTER: {len(active)} active violation(s) across {len(files)} files scanned.\n")
        for v in active:
            loc = f"{v['file']}:{v['line']}" if v['line'] else v['file']
            print(f"  [{v['severity'].upper()}] {v['rule_id']} @ {loc}")
            print(f"      {v['matched_text']}")
        if exempted:
            print(f"\n  ({len(exempted)} additional violation(s) covered by logged exceptions.)")
        sys.exit(1)
    else:
        print(f"✅ FOUNDER INTENT FILTER: PASS. {len(files)} files scanned, 0 active violations "
              f"({len(exempted)} exempted).")
        sys.exit(0)


if __name__ == "__main__":
    main()
