#!/usr/bin/env python3
"""
check_cost_policy.py

Validates SMART_PRODUCTION_COST_LAW_v2.md compliance across:
  (a) .noos/workflow_registry_v1.json - schema + registry_rules (RCP1-RCP5)
  (b) free-text automation/workflow config files - forbidden model/effort/trigger patterns

Exit 0 -> PASS. Exit 1 -> active violations found. Exit 2 -> could not run (never silently PASS).

Usage:
    python3 scripts/check_cost_policy.py [repo_root] [--policy path] [--registry path] [--json out.json]
"""
import argparse
import fnmatch
import glob
import json
import os
import re
import sys
from datetime import date, datetime

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML required (`pip install pyyaml --break-system-packages`).", file=sys.stderr)
    sys.exit(2)


def load_policy(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_registry(path):
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------- registry validation ----------

def validate_registry(registry, policy):
    violations = []
    if registry is None:
        return violations  # no registry yet is not itself a violation of the *checker*; caller may warn separately

    schema = policy.get("registry_schema", {})
    required = schema.get("required_fields", [])
    enums = schema.get("enums", {})
    entries = registry.get("workflows", [])

    seen_ids = {}

    for entry in entries:
        wid = entry.get("workflow_id", "<missing-id>")

        # required fields present
        for field in required:
            if field not in entry:
                violations.append({
                    "rule_id": "SCHEMA_missing_field",
                    "severity": "red",
                    "file": ".noos/workflow_registry_v1.json",
                    "line": None,
                    "matched_text": f"workflow_id={wid} missing required field '{field}'",
                    "description": "Registry entry missing a required schema field."
                })

        # enum validation
        for field, allowed_values in enums.items():
            if field in entry and entry[field] not in allowed_values:
                violations.append({
                    "rule_id": "SCHEMA_bad_enum",
                    "severity": "red",
                    "file": ".noos/workflow_registry_v1.json",
                    "line": None,
                    "matched_text": f"workflow_id={wid} field '{field}'='{entry[field]}' not in {allowed_values}",
                    "description": "Registry field value outside allowed enum."
                })

        # RCP2: global uniqueness
        seen_ids.setdefault(wid, 0)
        seen_ids[wid] += 1

        for rule in policy.get("registry_rules", []):
            rid = rule["id"]

            if rid == "RCP1_safe_fix_needs_receipt":
                if entry.get("safe_fix_allowed") is True and entry.get("receipt_required") is not True:
                    violations.append({
                        "rule_id": rid, "severity": rule.get("severity", "red"),
                        "file": ".noos/workflow_registry_v1.json", "line": None,
                        "matched_text": f"workflow_id={wid}: safe_fix_allowed=true but receipt_required!=true",
                        "description": rule["description"]
                    })

            elif rid == "RCP3_direct_write_only_for_deploy":
                if entry.get("writes") == "direct" and entry.get("class") != "deploy":
                    violations.append({
                        "rule_id": rid, "severity": rule.get("severity", "red"),
                        "file": ".noos/workflow_registry_v1.json", "line": None,
                        "matched_text": f"workflow_id={wid}: writes=direct but class={entry.get('class')}",
                        "description": rule["description"]
                    })

            elif rid == "RCP4_model_policy_value_locked":
                allowed = rule.get("allowed", [])
                if "model_policy" in entry and entry["model_policy"] not in allowed:
                    violations.append({
                        "rule_id": rid, "severity": rule.get("severity", "red"),
                        "file": ".noos/workflow_registry_v1.json", "line": None,
                        "matched_text": f"workflow_id={wid}: model_policy='{entry['model_policy']}' not in {allowed}",
                        "description": rule["description"]
                    })

            elif rid == "RCP5_audit_staleness":
                max_days = rule.get("max_days", 30)
                last_audited = entry.get("last_audited")
                if last_audited in (None, "", "TODO"):
                    violations.append({
                        "rule_id": rid, "severity": rule.get("severity", "yellow"),
                        "file": ".noos/workflow_registry_v1.json", "line": None,
                        "matched_text": f"workflow_id={wid}: last_audited is unset/TODO",
                        "description": rule["description"]
                    })
                else:
                    try:
                        d = date.fromisoformat(last_audited)
                        age = (date.today() - d).days
                        if age > max_days:
                            violations.append({
                                "rule_id": rid, "severity": rule.get("severity", "yellow"),
                                "file": ".noos/workflow_registry_v1.json", "line": None,
                                "matched_text": f"workflow_id={wid}: last_audited {age} days ago (max {max_days})",
                                "description": rule["description"]
                            })
                    except ValueError:
                        violations.append({
                            "rule_id": rid, "severity": "red",
                            "file": ".noos/workflow_registry_v1.json", "line": None,
                            "matched_text": f"workflow_id={wid}: last_audited '{last_audited}' is not a valid ISO date",
                            "description": "Invalid date format for last_audited."
                        })

    # RCP2 duplicate check, done once after collecting all ids
    for wid, count in seen_ids.items():
        if count > 1:
            violations.append({
                "rule_id": "RCP2_unique_workflow_id",
                "severity": "red",
                "file": ".noos/workflow_registry_v1.json",
                "line": None,
                "matched_text": f"workflow_id='{wid}' appears {count} times - must be globally unique",
                "description": "Duplicate workflow_id creates an ownership collision risk (see canon 10.1)."
            })

    return violations


# ---------- free-text pattern scanning ----------

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
            if fnmatch.fnmatch(norm, ex_norm) or fnmatch.fnmatch(os.path.basename(norm), ex_norm):
                return True
        return False

    return sorted(p for p in matched if not is_excluded(p))


def scan_text_patterns(repo_root, files, policy):
    violations = []
    pattern_groups = [
        ("forbidden_model_patterns", "COST_forbidden_model"),
        ("forbidden_effort_patterns", "COST_forbidden_effort"),
        ("forbidden_trigger_patterns", "COST_forbidden_trigger"),
    ]
    for rel_path in files:
        full_path = os.path.join(repo_root, rel_path)
        try:
            with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.read().splitlines()
        except OSError:
            continue
        for key, rule_id in pattern_groups:
            for pat in policy.get(key, []):
                for lineno, line in enumerate(lines, start=1):
                    if re.search(pat, line):
                        violations.append({
                            "rule_id": rule_id,
                            "severity": "red" if key != "forbidden_trigger_patterns" else "yellow",
                            "file": rel_path,
                            "line": lineno,
                            "matched_text": line.strip(),
                            "description": f"Matched forbidden pattern group '{key}': {pat}"
                        })
    return violations


def apply_exceptions(violations, exceptions, today):
    active, exempted = [], []
    for v in violations:
        matched = None
        for ex in exceptions or []:
            if ex.get("rule_id") != v["rule_id"]:
                continue
            scope = ex.get("scope", "")
            if scope and scope not in (v["file"], v.get("matched_text", "")):
                continue
            expires = ex.get("expires")
            if expires:
                try:
                    if date.fromisoformat(expires) < today:
                        continue
                except ValueError:
                    continue
            matched = ex
            break
        if matched:
            v["exempted_by"] = matched
            exempted.append(v)
        else:
            active.append(v)
    return active, exempted


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("repo_root", nargs="?", default=".")
    parser.add_argument("--policy", default=None)
    parser.add_argument("--registry", default=None)
    parser.add_argument("--json", default=None)
    args = parser.parse_args()

    repo_root = os.path.abspath(args.repo_root)
    policy_path = args.policy or os.path.join(repo_root, "policy", "cost_policy.yaml")
    registry_path = args.registry or os.path.join(repo_root, ".noos", "workflow_registry_v1.json")

    if not os.path.isfile(policy_path):
        print(f"FATAL: policy file not found at {policy_path}", file=sys.stderr)
        sys.exit(2)

    policy = load_policy(policy_path)
    registry = load_registry(registry_path)

    include_globs = ["**/*.md", "**/*.yaml", "**/*.yml", "**/*.json"]
    exclude_globs = ["node_modules/**", ".git/**", "tests/fixtures/**", "receipts/**",
                      "SMART_PRODUCTION_COST_LAW_v2.md", "policy/cost_policy.yaml",
                      "COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md"]
    files = collect_files(repo_root, include_globs, exclude_globs)

    all_violations = []
    all_violations.extend(validate_registry(registry, policy))
    all_violations.extend(scan_text_patterns(repo_root, files, policy))

    active, exempted = apply_exceptions(all_violations, policy.get("exceptions", []), date.today())

    report = {
        "checker": "check_cost_policy.py",
        "policy_version": policy.get("policy_version"),
        "registry_present": registry is not None,
        "registry_entries": len(registry.get("workflows", [])) if registry else 0,
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
        print(f"❌ COST POLICY: {len(active)} active violation(s). "
              f"{report['registry_entries']} registry entries, {len(files)} files scanned.\n")
        for v in active:
            loc = f"{v['file']}:{v['line']}" if v.get('line') else v['file']
            print(f"  [{v['severity'].upper()}] {v['rule_id']} @ {loc}")
            print(f"      {v['matched_text']}")
        if exempted:
            print(f"\n  ({len(exempted)} additional violation(s) covered by logged exceptions.)")
        sys.exit(1)
    else:
        print(f"✅ COST POLICY: PASS. {report['registry_entries']} registry entries, "
              f"{len(files)} files scanned, 0 active violations ({len(exempted)} exempted).")
        sys.exit(0)


if __name__ == "__main__":
    main()
