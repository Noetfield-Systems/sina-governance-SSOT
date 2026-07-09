#!/usr/bin/env python3
"""
NOOS Control Desk - backend (app.py)

v2 patch (per Advisor critique): the attestation form must record OBSERVED
REALITY, including bad values (GPT-5.4, Auto, Claude, High effort, hourly
trigger, etc). It must never hide or refuse to accept a leak - it must
record it and mark the entry FAIL/BLOCKED. The server computes the verdict;
the client never gets to self-report PASS.

Two-state model:
  - Draft attestation  -> .noos/registry_draft.json (any mix of PASS/FAIL/
    BLOCKED/incomplete, savable at any time, never touches the real registry)
  - Lock Candidate      -> only submittable when all 23 workflows have a
    draft entry AND every verdict is PASS. On submit: applies to the real
    registry, re-runs the real checker, and - only if that also passes -
    writes a receipt and (if this is a real git repo) creates a bounded
    branch + local commit. It never pushes and never merges to main; PR
    creation is explicitly not built yet (see README) and this code does
    not claim otherwise.

Zero-dependency stdlib (http.server) - no pip install required to run this.
    python3 control-desk/app.py [--port 17877] [--repo-root ../]
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

REPO_ROOT = None
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

REGISTRY_REL = os.path.join(".noos", "workflow_registry_v1.json")
DRAFT_REL = os.path.join(".noos", "registry_draft.json")
CHECKER_REL = os.path.join("scripts", "check_cost_policy.py")
SYNC_SCRIPT_REL = os.path.join("scripts", "noos_integrator_sync_v1.py")
RECEIPTS_REL = "receipts"

# --- policy knowledge used to COMPUTE verdicts server-side (never trust client verdicts) ---
ALLOWED_MODEL_NAMES = {"gpt-5-mini", "gpt-5 mini", "gpt-5-mini-low"}
KNOWN_FORBIDDEN_MODELS = {
    "auto", "gpt-5.4", "gpt-5.4 mini", "gpt-5.3-codex", "auto: gpt-5.4", "auto: gpt-5.3-codex",
    "claude", "claude haiku", "claude sonnet", "claude opus", "anthropic",
    "gemini", "kimi", "mai-code", "coding agent model"
}
FORBIDDEN_EFFORT = {"high", "extra high", "unknown", "auto"}
FORBIDDEN_TRIGGERS_FOR_COPILOT = {
    "hourly", "daily", "weekly", "background", "keep awake",
    "unpinned schedule", "autopilot recurring"
}

VALID_MODEL_POLICY = {"model:none", "gpt-5-mini-low"}
WORKFLOW_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]{1,80}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------- verdict computation (server-side, authoritative) ----------

def compute_verdict(observed, owner):
    """
    observed: dict with observed_trigger, observed_mode, observed_model, observed_effort
    owner: registry entry's 'owner' field (e.g. 'copilot_manual')
    Returns (verdict, reasons_list). verdict in {PASS, FAIL, BLOCKED}.
    This function is the ONLY source of truth for policy_verdict - the client
    never sends a verdict, and if it does, this overwrites it.
    """
    reasons = []
    model_raw = (observed.get("observed_model") or "").strip()
    model_norm = model_raw.lower()

    if model_norm in ALLOWED_MODEL_NAMES:
        model_ok = True
    elif model_norm in KNOWN_FORBIDDEN_MODELS:
        model_ok = False
        reasons.append(f"observed_model '{model_raw}' is on the known-forbidden list.")
    elif model_norm == "":
        model_ok = None
        reasons.append("observed_model is empty - cannot attest without an actual observed value.")
    else:
        model_ok = None
        reasons.append(f"observed_model '{model_raw}' is not recognized as allowed or forbidden - unknown model.")

    effort_raw = (observed.get("observed_effort") or "").strip()
    effort_norm = effort_raw.lower()
    effort_ok = effort_norm == "low"
    if effort_norm in FORBIDDEN_EFFORT:
        reasons.append(f"observed_effort '{effort_raw}' is forbidden by default.")
    elif effort_norm == "medium":
        if observed.get("evidence_note"):
            reasons.append("observed_effort is medium - allowed only because an exception reason was logged in evidence_note.")
        else:
            reasons.append("observed_effort is medium with no evidence_note - medium requires a logged exception reason.")
            effort_ok = False
    elif effort_norm == "":
        reasons.append("observed_effort is empty - cannot attest without an actual observed value.")
        effort_ok = False

    trigger_raw = (observed.get("observed_trigger") or "").strip()
    trigger_norm = trigger_raw.lower()
    trigger_ok = True
    if owner == "copilot_manual" and trigger_norm in FORBIDDEN_TRIGGERS_FOR_COPILOT:
        trigger_ok = False
        reasons.append(f"observed_trigger '{trigger_raw}' is forbidden for a Copilot-owned automation.")
    elif trigger_norm == "":
        trigger_ok = False
        reasons.append("observed_trigger is empty - cannot attest without an actual observed value.")

    if model_ok is None:
        return "BLOCKED", reasons
    if model_ok and trigger_ok and (effort_ok or (effort_norm == "medium" and observed.get("evidence_note"))):
        return "PASS", reasons if reasons else ["Observed reality matches policy. Clean."]
    return "FAIL", reasons


# ---------- allowlisted command runners (the whole security model) ----------

def run_checker():
    out_path = os.path.join(REPO_ROOT, RECEIPTS_REL, "control_desk_last_validate.json")
    cmd = [sys.executable, os.path.join(REPO_ROOT, CHECKER_REL), REPO_ROOT, "--json", out_path]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    report = None
    if os.path.isfile(out_path):
        with open(out_path, "r", encoding="utf-8") as f:
            report = json.load(f)
    return proc.returncode, report, proc.stderr


def run_sync():
    cmd_sync = [sys.executable, os.path.join(REPO_ROOT, SYNC_SCRIPT_REL), "sync"]
    proc1 = subprocess.run(cmd_sync, capture_output=True, text=True, timeout=30)
    cmd_summary = [sys.executable, os.path.join(REPO_ROOT, SYNC_SCRIPT_REL), "summary", "--json"]
    proc2 = subprocess.run(cmd_summary, capture_output=True, text=True, timeout=30)
    summary = None
    try:
        summary = json.loads(proc2.stdout)
    except (json.JSONDecodeError, ValueError):
        pass
    return proc1.returncode, proc2.returncode, summary, (proc1.stderr + proc2.stderr)


def git_status_summary():
    if not os.path.isdir(os.path.join(REPO_ROOT, ".git")):
        return {"is_git_repo": False, "message": "Not a git repository - branch/commit flow unavailable until this is a real repo (e.g. sina-governance-SSOT)."}
    try:
        branch = subprocess.run(["git", "-C", REPO_ROOT, "branch", "--show-current"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
        status = subprocess.run(["git", "-C", REPO_ROOT, "status", "--porcelain"],
                                 capture_output=True, text=True, timeout=10).stdout
        dirty_files = [l for l in status.splitlines() if l.strip()]
        return {"is_git_repo": True, "current_branch": branch, "dirty_file_count": len(dirty_files),
                "dirty_files": dirty_files[:20]}
    except (subprocess.SubprocessError, OSError) as e:
        return {"is_git_repo": True, "error": str(e)}


def git_create_bounded_branch_and_commit(branch_name, commit_message):
    """Real local branch + commit only. Never pushes, never touches main, never opens a PR
    (that would require a remote + auth this sandbox doesn't have - not overclaimed here)."""
    if not os.path.isdir(os.path.join(REPO_ROOT, ".git")):
        return {"ok": False, "reason": "not_a_git_repo"}
    try:
        subprocess.run(["git", "-C", REPO_ROOT, "checkout", "-b", branch_name],
                        capture_output=True, text=True, timeout=10, check=True)
        subprocess.run(["git", "-C", REPO_ROOT, "add", REGISTRY_REL, DRAFT_REL],
                        capture_output=True, text=True, timeout=10, check=True)
        result = subprocess.run(["git", "-C", REPO_ROOT, "commit", "-m", commit_message],
                                 capture_output=True, text=True, timeout=10)
        return {"ok": True, "branch": branch_name, "commit_output": result.stdout + result.stderr}
    except subprocess.CalledProcessError as e:
        return {"ok": False, "reason": "git_command_failed", "detail": (e.stdout or "") + (e.stderr or "")}


# ---------- registry / draft read-write ----------

def load_registry():
    with open(os.path.join(REPO_ROOT, REGISTRY_REL), "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data):
    path = os.path.join(REPO_ROOT, REGISTRY_REL)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def load_draft():
    path = os.path.join(REPO_ROOT, DRAFT_REL)
    if not os.path.isfile(path):
        return {"attestations": {}}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_draft(data):
    path = os.path.join(REPO_ROOT, DRAFT_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp, path)


def write_receipt(name, payload):
    os.makedirs(os.path.join(REPO_ROOT, RECEIPTS_REL), exist_ok=True)
    path = os.path.join(REPO_ROOT, RECEIPTS_REL, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return os.path.relpath(path, REPO_ROOT)


def draft_status(registry, draft):
    entries = registry.get("workflows", [])
    attestations = draft.get("attestations", {})
    total = len(entries)
    pass_ids, fail_ids, blocked_ids, todo_ids = [], [], [], []
    for e in entries:
        wid = e["workflow_id"]
        att = attestations.get(wid)
        if att is None:
            todo_ids.append(wid)
        elif att.get("policy_verdict") == "PASS":
            pass_ids.append(wid)
        elif att.get("policy_verdict") == "BLOCKED":
            blocked_ids.append(wid)
        else:
            fail_ids.append(wid)
    ready = (len(pass_ids) == total)
    return {
        "total": total, "pass_count": len(pass_ids), "fail_count": len(fail_ids),
        "blocked_count": len(blocked_ids), "todo_count": len(todo_ids),
        "pass_ids": pass_ids, "fail_ids": fail_ids, "blocked_ids": blocked_ids, "todo_ids": todo_ids,
        "ready_for_lock_candidate": ready
    }


# ---------- HTTP handler ----------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("[control-desk] " + (fmt % args) + "\n")

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            return json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            return None

    def _serve_static(self, path):
        if path in ("", "/"):
            path = "/index.html"
        safe_path = os.path.normpath(path).lstrip(os.sep)
        full_path = os.path.join(STATIC_DIR, safe_path)
        if not full_path.startswith(STATIC_DIR) or not os.path.isfile(full_path):
            self.send_response(404)
            self.end_headers()
            return
        ctype = "text/html" if full_path.endswith(".html") else \
                "application/javascript" if full_path.endswith(".js") else \
                "text/css" if full_path.endswith(".css") else "application/octet-stream"
        with open(full_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == "/api/registry":
            self._send_json(load_registry())
        elif route == "/api/draft":
            self._send_json(load_draft())
        elif route == "/api/draft/status":
            self._send_json(draft_status(load_registry(), load_draft()))
        elif route == "/api/dashboard":
            registry = load_registry()
            draft = load_draft()
            status = draft_status(registry, draft)
            self._send_json({
                "registry_entries": status["total"],
                "pass_count": status["pass_count"],
                "fail_count": status["fail_count"],
                "blocked_count": status["blocked_count"],
                "todo_count": status["todo_count"],
                "ready_for_lock_candidate": status["ready_for_lock_candidate"],
                "git": git_status_summary()
            })
        elif route == "/api/receipts":
            receipts_dir = os.path.join(REPO_ROOT, RECEIPTS_REL)
            files = sorted(os.listdir(receipts_dir)) if os.path.isdir(receipts_dir) else []
            self._send_json({"receipts": files})
        elif route.startswith("/api/"):
            self._send_json({"error": "unknown route"}, status=404)
        else:
            self._serve_static(route)

    def do_POST(self):
        route = urlparse(self.path).path
        body = self._read_json_body()
        if body is None:
            self._send_json({"error": "invalid JSON body"}, status=400)
            return

        if route == "/api/draft/save":
            self._handle_draft_save(body)
        elif route == "/api/lock-candidate/submit":
            self._handle_lock_candidate_submit(body)
        elif route == "/api/validate":
            self._handle_validate()
        elif route == "/api/sync":
            self._handle_sync()
        else:
            self._send_json({"error": "unknown route"}, status=404)

    def _handle_draft_save(self, body):
        workflow_id = body.get("workflow_id", "")
        if not WORKFLOW_ID_RE.match(workflow_id):
            self._send_json({"error": "invalid workflow_id"}, status=400)
            return

        registry = load_registry()
        target = next((e for e in registry.get("workflows", []) if e["workflow_id"] == workflow_id), None)
        if target is None:
            self._send_json({"error": f"workflow_id '{workflow_id}' not found in registry"}, status=404)
            return

        last_audited = body.get("last_audited", "")
        if not DATE_RE.match(last_audited):
            self._send_json({"error": "last_audited must be YYYY-MM-DD"}, status=400)
            return
        try:
            date.fromisoformat(last_audited)
        except ValueError:
            self._send_json({"error": "last_audited is not a valid calendar date"}, status=400)
            return

        observed = {
            "observed_trigger": body.get("observed_trigger", ""),
            "observed_mode": body.get("observed_mode", ""),
            "observed_model": body.get("observed_model", ""),
            "observed_effort": body.get("observed_effort", ""),
            "evidence_note": body.get("evidence_note", "")
        }
        desired = {
            "desired_trigger": body.get("desired_trigger", "manual"),
            "desired_model": body.get("desired_model", "gpt-5-mini"),
            "desired_effort": body.get("desired_effort", "low")
        }

        # Server computes the verdict. Client-sent verdicts, if any, are ignored.
        verdict, reasons = compute_verdict(observed, target.get("owner"))

        draft = load_draft()
        draft.setdefault("attestations", {})[workflow_id] = {
            "automation_name": workflow_id,
            "repo": target.get("repo"),
            **observed,
            **desired,
            "policy_verdict": verdict,
            "verdict_reasons": reasons,
            "last_audited": last_audited,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        save_draft(draft)

        receipt_name = f"draft_save_{workflow_id}_{last_audited}.json"
        receipt_path = write_receipt(receipt_name, {
            "action": "draft_save", "workflow_id": workflow_id,
            "verdict": verdict, "reasons": reasons
        })

        self._send_json({
            "status": "SAVED", "workflow_id": workflow_id,
            "policy_verdict": verdict, "verdict_reasons": reasons,
            "receipt": receipt_path
        })

    def _handle_lock_candidate_submit(self, body):
        registry = load_registry()
        draft = load_draft()
        status = draft_status(registry, draft)

        if not status["ready_for_lock_candidate"]:
            self._send_json({
                "status": "BLOCKED",
                "message": "Lock Candidate requires all workflows attested PASS. Not ready.",
                "todo_ids": status["todo_ids"],
                "fail_ids": status["fail_ids"],
                "blocked_ids": status["blocked_ids"]
            }, status=409)
            return

        # Apply draft's last_audited into the real registry (only PASS entries exist at this point).
        attestations = draft["attestations"]
        for entry in registry["workflows"]:
            att = attestations.get(entry["workflow_id"])
            if att:
                entry["last_audited"] = att["last_audited"]
        save_registry(registry)

        returncode, report, stderr = run_checker()
        if report is None or report.get("status") != "PASS":
            # Do not leave a half-applied state silently claimed as locked.
            self._send_json({
                "status": "CHECKER_FAILED_AFTER_APPLY",
                "message": "Applied attested dates but the real checker did not return PASS. Registry was NOT rolled back automatically - inspect receipts/control_desk_last_validate.json.",
                "checker_report": report,
                "stderr": stderr
            }, status=500)
            return

        today_str = date.today().isoformat()
        branch_name = f"audit/update-registry-{today_str}"
        commit_message = f"Update workflow_registry_v1.json: {status['pass_count']} workflows attested PASS ({today_str})"
        git_result = git_create_bounded_branch_and_commit(branch_name, commit_message)

        receipt_path = write_receipt(f"lock_candidate_{today_str}.json", {
            "action": "lock_candidate_submit",
            "attested_pass_count": status["pass_count"],
            "checker_status": report["status"],
            "git_result": git_result
        })

        self._send_json({
            "status": "LOCK_CANDIDATE_READY",
            "checker_status": report["status"],
            "git_result": git_result,
            "receipt": receipt_path,
            "note": "Committed locally only if this is a real git repo. No push, no PR, no merge to main happened or is claimed here."
        })

    def _handle_validate(self):
        returncode, report, stderr = run_checker()
        if report is None:
            self._send_json({"status": "ERROR", "message": "Checker did not produce a report.", "stderr": stderr}, status=500)
            return
        self._send_json({"status": "OK", "checker_exit_code": returncode, "report": report})

    def _handle_sync(self):
        rc1, rc2, summary, stderr = run_sync()
        if summary is None:
            self._send_json({"status": "ERROR", "message": "Sync did not return a summary.", "stderr": stderr}, status=500)
            return
        receipt_path = write_receipt(f"sync_{summary.get('sync_count','na')}.json", {
            "action": "noos_integrator_sync", "summary": summary
        })
        self._send_json({"status": "OK", "summary": summary, "receipt": receipt_path})


def main():
    global REPO_ROOT
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=17877)
    parser.add_argument("--repo-root", default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    args = parser.parse_args()

    REPO_ROOT = os.path.abspath(args.repo_root)
    if not os.path.isfile(os.path.join(REPO_ROOT, REGISTRY_REL)):
        print(f"FATAL: no registry found at {os.path.join(REPO_ROOT, REGISTRY_REL)}", file=sys.stderr)
        sys.exit(2)

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"NOOS Control Desk running at http://localhost:{args.port}  (repo root: {REPO_ROOT})")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
