#!/usr/bin/env python3
"""
NOOS Control Desk - backend (app.py)

Zero-dependency local cockpit for managing .noos/workflow_registry_v1.json,
running the cost-policy checker, and running NOOS integrator sync -
per the "Localhost web first" decision (Electron/Tauri deferred to Phase 2+).

Deliberately stdlib-only (http.server): no pip install required to run this.
    python3 control-desk/app.py [--port 17877] [--repo-root ../]

Then open http://localhost:17877

Command allowlist (§ below) is the whole security model here: this server
only ever runs a small fixed set of subprocess commands, built from constants,
never from raw request input. It binds to localhost only.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

REPO_ROOT = None  # set in main()
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

REGISTRY_REL = os.path.join(".noos", "workflow_registry_v1.json")
CHECKER_REL = os.path.join("scripts", "check_cost_policy.py")
SYNC_SCRIPT_REL = os.path.join("scripts", "noos_integrator_sync_v1.py")
RECEIPTS_REL = "receipts"

VALID_MODEL_POLICY = {"model:none", "gpt-5-mini-low"}
VALID_TRIGGER = {"schedule", "manual", "event"}
VALID_CLASS = {"observe", "triage", "safe_fix", "verify", "deploy", "reconcile"}
VALID_OWNER = {"github_actions", "cloudflare_worker", "copilot_manual", "noos_integrator"}
VALID_WRITES = {"artifacts_only", "branch_pr", "direct"}
VALID_RISK = {"low", "medium", "high"}

WORKFLOW_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]{1,80}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


# ---------- allowlisted command runners (the whole security model) ----------

def run_checker():
    """Fixed command, no user input in argv. Returns (returncode, stdout, stderr)."""
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
    """Read-only git status - never writes. Honest report if not a git repo."""
    if not os.path.isdir(os.path.join(REPO_ROOT, ".git")):
        return {"is_git_repo": False, "message": "Not a git repository - PR flow unavailable until this is a real repo (e.g. sina-governance-SSOT)."}
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


# ---------- registry read/write helpers ----------

def load_registry():
    path = os.path.join(REPO_ROOT, REGISTRY_REL)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(data):
    path = os.path.join(REPO_ROOT, REGISTRY_REL)
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    os.replace(tmp_path, path)


def validate_attestation_fields(fields):
    """Strict allowlist validation for a single attestation update. Returns list of errors."""
    errors = []
    if "model_policy" in fields and fields["model_policy"] not in VALID_MODEL_POLICY:
        errors.append(f"model_policy must be one of {sorted(VALID_MODEL_POLICY)}")
    if "trigger" in fields and fields["trigger"] not in VALID_TRIGGER:
        errors.append(f"trigger must be one of {sorted(VALID_TRIGGER)}")
    if "class" in fields and fields["class"] not in VALID_CLASS:
        errors.append(f"class must be one of {sorted(VALID_CLASS)}")
    if "owner" in fields and fields["owner"] not in VALID_OWNER:
        errors.append(f"owner must be one of {sorted(VALID_OWNER)}")
    if "writes" in fields and fields["writes"] not in VALID_WRITES:
        errors.append(f"writes must be one of {sorted(VALID_WRITES)}")
    if "risk" in fields and fields["risk"] not in VALID_RISK:
        errors.append(f"risk must be one of {sorted(VALID_RISK)}")
    if "last_audited" in fields and not DATE_RE.match(fields["last_audited"]):
        errors.append("last_audited must be YYYY-MM-DD")
    if "last_audited" in fields and DATE_RE.match(fields["last_audited"]):
        try:
            date.fromisoformat(fields["last_audited"])
        except ValueError:
            errors.append("last_audited is not a valid calendar date")
    return errors


def write_receipt(name, payload):
    os.makedirs(os.path.join(REPO_ROOT, RECEIPTS_REL), exist_ok=True)
    path = os.path.join(REPO_ROOT, RECEIPTS_REL, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return os.path.relpath(path, REPO_ROOT)


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
        if path == "/" or path == "":
            path = "/index.html"
        safe_path = os.path.normpath(path).lstrip(os.sep)
        full_path = os.path.join(STATIC_DIR, safe_path)
        if not full_path.startswith(STATIC_DIR) or not os.path.isfile(full_path):
            self.send_response(404)
            self.end_headers()
            return
        content_type = "text/html" if full_path.endswith(".html") else \
                        "application/javascript" if full_path.endswith(".js") else \
                        "text/css" if full_path.endswith(".css") else "application/octet-stream"
        with open(full_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/registry":
            self._send_json(load_registry())
        elif route == "/api/dashboard":
            registry = load_registry()
            entries = registry.get("workflows", [])
            todo_count = sum(1 for e in entries if e.get("last_audited") in (None, "", "TODO"))
            self._send_json({
                "registry_entries": len(entries),
                "todo_audits": todo_count,
                "audited": len(entries) - todo_count,
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
        parsed = urlparse(self.path)
        route = parsed.path
        body = self._read_json_body()

        if body is None:
            self._send_json({"error": "invalid JSON body"}, status=400)
            return

        if route == "/api/registry/attest":
            self._handle_attest(body)
        elif route == "/api/validate":
            self._handle_validate()
        elif route == "/api/sync":
            self._handle_sync()
        else:
            self._send_json({"error": "unknown route"}, status=404)

    def _handle_attest(self, body):
        workflow_id = body.get("workflow_id", "")
        if not WORKFLOW_ID_RE.match(workflow_id):
            self._send_json({"error": "invalid workflow_id"}, status=400)
            return

        fields = {k: v for k, v in body.items() if k != "workflow_id"}
        errors = validate_attestation_fields(fields)
        if errors:
            self._send_json({"status": "REJECTED", "errors": errors}, status=400)
            return

        registry = load_registry()
        target = None
        for entry in registry.get("workflows", []):
            if entry.get("workflow_id") == workflow_id:
                target = entry
                break
        if target is None:
            self._send_json({"error": f"workflow_id '{workflow_id}' not found"}, status=404)
            return

        before = dict(target)
        target.update(fields)
        save_registry(registry)

        receipt_name = f"attest_{workflow_id}_{fields.get('last_audited', 'unknown')}.json"
        receipt_path = write_receipt(receipt_name, {
            "action": "attest", "workflow_id": workflow_id,
            "before": before, "after": target
        })
        self._send_json({"status": "SAVED", "workflow_id": workflow_id, "receipt": receipt_path})

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
