import json
import os
import subprocess
import sys
from datetime import date

from . import config as cfg
from .receipts import build_receipt, write_receipt
from .verdict import compute_verdict


def load_registry():
    with open(os.path.join(cfg.REPO_ROOT, cfg.REGISTRY_REL), "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data):
    path = os.path.join(cfg.REPO_ROOT, cfg.REGISTRY_REL)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def load_draft():
    path = os.path.join(cfg.REPO_ROOT, cfg.DRAFT_REL)
    if not os.path.isfile(path):
        return {"attestations": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_draft(data):
    path = os.path.join(cfg.REPO_ROOT, cfg.DRAFT_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def draft_status(registry, draft):
    entries = registry.get("workflows", [])
    attestations = draft.get("attestations", {})
    total = len(entries)
    pass_ids, fail_ids, blocked_ids, todo_ids = [], [], [], []
    for entry in entries:
        wid = entry["workflow_id"]
        att = attestations.get(wid)
        if att is None:
            todo_ids.append(wid)
        elif att.get("policy_verdict") == "PASS":
            pass_ids.append(wid)
        elif att.get("policy_verdict") == "BLOCKED":
            blocked_ids.append(wid)
        else:
            fail_ids.append(wid)
    ready = len(pass_ids) == total and total > 0
    return {
        "total": total,
        "pass_count": len(pass_ids),
        "fail_count": len(fail_ids),
        "blocked_count": len(blocked_ids),
        "todo_count": len(todo_ids),
        "pass_ids": pass_ids,
        "fail_ids": fail_ids,
        "blocked_ids": blocked_ids,
        "todo_ids": todo_ids,
        "ready_for_lock_candidate": ready,
    }


def _attestation_stale(last_audited):
    if not last_audited or last_audited == "TODO":
        return True, "last_audited is unset or TODO"
    try:
        age = (date.today() - date.fromisoformat(last_audited)).days
    except ValueError:
        return True, f"last_audited '{last_audited}' is not a valid ISO date"
    if age > cfg.AUDIT_STALE_MAX_DAYS:
        return True, f"last_audited is {age} days old (max {cfg.AUDIT_STALE_MAX_DAYS})"
    return False, None


def collect_lock_blockers(registry, draft):
    """Aggregate every reason a lock-candidate attempt must return 409."""
    errors = []
    attestations = draft.get("attestations", {})

    for entry in registry.get("workflows", []):
        wid = entry["workflow_id"]
        att = attestations.get(wid)
        registry_la = entry.get("last_audited")

        if att is None:
            errors.append({
                "workflow_id": wid,
                "kind": "incomplete",
                "message": "No draft attestation saved for this workflow.",
            })
            continue

        verdict = att.get("policy_verdict")
        if verdict == "FAIL":
            errors.append({
                "workflow_id": wid,
                "kind": "failed",
                "message": "Draft attestation policy_verdict is FAIL.",
                "verdict_reasons": att.get("verdict_reasons", []),
            })
        elif verdict == "BLOCKED":
            errors.append({
                "workflow_id": wid,
                "kind": "blocked",
                "message": "Draft attestation policy_verdict is BLOCKED.",
                "verdict_reasons": att.get("verdict_reasons", []),
            })
        elif verdict != "PASS":
            errors.append({
                "workflow_id": wid,
                "kind": "incomplete",
                "message": f"Draft attestation has non-PASS verdict: {verdict!r}.",
            })

        stale, stale_msg = _attestation_stale(att.get("last_audited"))
        if stale:
            errors.append({
                "workflow_id": wid,
                "kind": "stale",
                "message": stale_msg,
            })

        if registry_la in (None, "", "TODO") and verdict != "PASS":
            errors.append({
                "workflow_id": wid,
                "kind": "unaudited",
                "message": "Registry last_audited is TODO and draft is not PASS.",
            })

    return errors


def validate_desired(desired):
    invalid = []
    for field, allowed in cfg.ALLOWED_DESIRED.items():
        value = desired.get(field)
        if value is not None and value not in allowed:
            invalid.append({"field": field, "value": value, "allowed": sorted(allowed)})
    return invalid


def run_checker():
    out_path = os.path.join(cfg.REPO_ROOT, cfg.RECEIPTS_REL, "control_desk_last_validate.json")
    cmd = [sys.executable, os.path.join(cfg.REPO_ROOT, cfg.CHECKER_REL), cfg.REPO_ROOT, "--json", out_path]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    report = None
    if os.path.isfile(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            report = json.load(f)
    return proc.returncode, report, proc.stderr, cmd


def run_sync():
    cmd_sync = [sys.executable, os.path.join(cfg.REPO_ROOT, cfg.SYNC_SCRIPT_REL), "sync"]
    proc1 = subprocess.run(cmd_sync, capture_output=True, text=True, timeout=30)
    cmd_summary = [sys.executable, os.path.join(cfg.REPO_ROOT, cfg.SYNC_SCRIPT_REL), "summary", "--json"]
    proc2 = subprocess.run(cmd_summary, capture_output=True, text=True, timeout=30)
    summary = None
    try:
        summary = json.loads(proc2.stdout)
    except (json.JSONDecodeError, ValueError):
        pass
    return proc1.returncode, proc2.returncode, summary, (proc1.stderr + proc2.stderr), cmd_sync, cmd_summary


def run_sync_summary_only():
    cmd_summary = [sys.executable, os.path.join(cfg.REPO_ROOT, cfg.SYNC_SCRIPT_REL), "summary", "--json"]
    proc = subprocess.run(cmd_summary, capture_output=True, text=True, timeout=30)
    summary = None
    try:
        summary = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        pass
    return proc.returncode, summary, proc.stderr, cmd_summary


def git_status_summary():
    if not os.path.isdir(os.path.join(cfg.REPO_ROOT, ".git")):
        return {
            "is_git_repo": False,
            "message": "Not a git repository - branch/commit flow unavailable until this is a real repo.",
        }
    try:
        branch = subprocess.run(
            ["git", "-C", cfg.REPO_ROOT, "branch", "--show-current"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", cfg.REPO_ROOT, "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        ).stdout
        dirty_files = [line for line in status.splitlines() if line.strip()]
        return {
            "is_git_repo": True,
            "current_branch": branch,
            "dirty_file_count": len(dirty_files),
            "dirty_files": dirty_files[:20],
        }
    except (subprocess.SubprocessError, OSError) as exc:
        return {"is_git_repo": True, "error": str(exc)}


def git_create_bounded_branch_and_commit(branch_name, commit_message):
    if not os.path.isdir(os.path.join(cfg.REPO_ROOT, ".git")):
        return {"ok": False, "reason": "not_a_git_repo"}
    try:
        subprocess.run(
            ["git", "-C", cfg.REPO_ROOT, "checkout", "-b", branch_name],
            capture_output=True, text=True, timeout=10, check=True,
        )
        subprocess.run(
            ["git", "-C", cfg.REPO_ROOT, "add", cfg.REGISTRY_REL, cfg.DRAFT_REL],
            capture_output=True, text=True, timeout=10, check=True,
        )
        result = subprocess.run(
            ["git", "-C", cfg.REPO_ROOT, "commit", "-m", commit_message],
            capture_output=True, text=True, timeout=10,
        )
        return {"ok": True, "branch": branch_name, "commit_output": result.stdout + result.stderr}
    except subprocess.CalledProcessError as exc:
        return {"ok": False, "reason": "git_command_failed", "detail": (exc.stdout or "") + (exc.stderr or "")}


def checker_errors_as_lock_blockers(report):
    blockers = []
    for violation in report.get("violations_active", []):
        blockers.append({
            "workflow_id": None,
            "kind": "policy_validation",
            "message": violation.get("matched_text") or violation.get("description"),
            "rule_id": violation.get("rule_id"),
            "severity": violation.get("severity"),
        })
    if report.get("status") != "PASS" and not blockers:
        blockers.append({
            "workflow_id": None,
            "kind": "policy_validation",
            "message": f"Checker returned status {report.get('status')!r}.",
        })
    return blockers
