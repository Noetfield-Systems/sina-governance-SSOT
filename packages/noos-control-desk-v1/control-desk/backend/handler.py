import json
import os
import sys
from datetime import date, datetime, timezone
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from . import config as cfg
from .receipts import build_receipt, write_receipt
from . import services as svc
from .verdict import compute_verdict

# Phase 1 canonical routes — see data/noos_control_desk_api_contract_v1.json
PHASE1_GET = {
    "/api/dashboard",
    "/api/registry/load",
    "/api/integrator/status",
    "/api/receipts/list",
    "/api/pr/prepare",
}

PHASE1_POST = {
    "/api/registry/save-draft",
    "/api/attestation/save",
    "/api/policy/check",
    "/api/integrator/sync",
    "/api/lock-candidate/submit",
}


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
        full_path = os.path.join(cfg.STATIC_DIR, safe_path)
        if not full_path.startswith(cfg.STATIC_DIR) or not os.path.isfile(full_path):
            self.send_response(404)
            self.end_headers()
            return
        ctype = (
            "text/html" if full_path.endswith(".html")
            else "application/javascript" if full_path.endswith(".js")
            else "text/css" if full_path.endswith(".css")
            else "application/octet-stream"
        )
        with open(full_path, "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        route = urlparse(self.path).path

        if route == "/api/dashboard":
            registry = svc.load_registry()
            draft = svc.load_draft()
            status = svc.draft_status(registry, draft)
            self._send_json({
                "registry_entries": status["total"],
                "pass_count": status["pass_count"],
                "fail_count": status["fail_count"],
                "blocked_count": status["blocked_count"],
                "todo_count": status["todo_count"],
                "ready_for_lock_candidate": status["ready_for_lock_candidate"],
                "git": svc.git_status_summary(),
            })
        elif route == "/api/registry/load":
            self._send_json(svc.load_registry())
        elif route == "/api/receipts/list":
            receipts_dir = os.path.join(cfg.REPO_ROOT, cfg.RECEIPTS_REL)
            files = sorted(os.listdir(receipts_dir)) if os.path.isdir(receipts_dir) else []
            self._send_json({"receipts": files})
        elif route == "/api/integrator/status":
            _, summary, _, _ = svc.run_sync_summary_only()
            self._send_json(summary or {"error": "integrator summary unavailable"}, status=200 if summary else 500)
        elif route == "/api/pr/prepare":
            today_str = date.today().isoformat()
            self._send_json({
                "status": "PLAN_ONLY",
                "suggested_branch": f"audit/update-registry-{today_str}",
                "suggested_commit": f"Update workflow_registry_v1.json attestation ({today_str})",
                "git": svc.git_status_summary(),
                "note": "Plan only — no push, no PR, no merge to main.",
            })
        elif route.startswith("/api/"):
            self._send_json({"error": "unknown route", "phase": 1, "contract": "data/noos_control_desk_api_contract_v1.json"}, status=404)
        else:
            self._serve_static(route)

    def do_POST(self):
        route = urlparse(self.path).path
        body = self._read_json_body()
        if body is None and route not in ("/api/policy/check", "/api/integrator/sync", "/api/lock-candidate/submit"):
            self._send_json({"error": "invalid JSON body"}, status=400)
            return

        if route == "/api/registry/save-draft":
            self._handle_registry_save_draft(body or {})
        elif route == "/api/attestation/save":
            self._handle_attestation_draft(body)
        elif route == "/api/lock-candidate/submit":
            self._handle_lock_candidate(body or {})
        elif route == "/api/policy/check":
            self._handle_policy_check()
        elif route == "/api/integrator/sync":
            self._handle_integrator_sync()
        else:
            self._send_json({"error": "unknown route", "phase": 1, "contract": "data/noos_control_desk_api_contract_v1.json"}, status=404)

    def _handle_registry_save_draft(self, body):
        if "workflows" not in body:
            self._send_json({"error": "body must include workflows array"}, status=400)
            return
        path = os.path.join(cfg.REPO_ROOT, cfg.REGISTRY_DRAFT_REL)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(body, f, indent=2)
        os.replace(tmp, path)
        receipt = build_receipt(
            "registry_save_draft",
            files_changed=[cfg.REGISTRY_DRAFT_REL],
            policy_pass=True,
            next_machine_action="Review workflow_registry_draft.json before any lock attempt.",
        )
        receipt_path = write_receipt("registry_draft_save.json", receipt)
        self._send_json({
            "status": "SAVED",
            "path": cfg.REGISTRY_DRAFT_REL,
            "entries": len(body.get("workflows", [])),
            "receipt": receipt_path,
        })

    def _handle_attestation_draft(self, body):
        workflow_id = body.get("workflow_id", "")
        if not cfg.WORKFLOW_ID_RE.match(workflow_id):
            self._send_json({"error": "invalid workflow_id"}, status=400)
            return

        registry = svc.load_registry()
        target = next((e for e in registry.get("workflows", []) if e["workflow_id"] == workflow_id), None)
        if target is None:
            self._send_json({"error": f"workflow_id '{workflow_id}' not found in registry"}, status=404)
            return

        last_audited = body.get("last_audited", "")
        if not cfg.DATE_RE.match(last_audited):
            self._send_json({"error": "last_audited must be YYYY-MM-DD"}, status=400)
            return
        try:
            date.fromisoformat(last_audited)
        except ValueError:
            self._send_json({"error": "last_audited is not a valid calendar date"}, status=400)
            return

        observed = {
            "observed_trigger": body.get("observed_trigger") if "observed_trigger" in body else "",
            "observed_mode": body.get("observed_mode") if "observed_mode" in body else "",
            "observed_model": body.get("observed_model") if "observed_model" in body else "",
            "observed_effort": body.get("observed_effort") if "observed_effort" in body else "",
            "evidence_note": body.get("evidence_note") if "evidence_note" in body else "",
        }

        desired = {
            "desired_trigger": body.get("desired_trigger", "manual"),
            "desired_model": body.get("desired_model", "gpt-5-mini"),
            "desired_effort": body.get("desired_effort", "low"),
        }
        invalid_desired = svc.validate_desired(desired)
        if invalid_desired:
            self._send_json({"error": "desired_* fields must be allowlisted", "invalid": invalid_desired}, status=400)
            return

        verdict, reasons = compute_verdict(observed, target)

        draft = svc.load_draft()
        draft.setdefault("attestations", {})[workflow_id] = {
            "automation_name": workflow_id,
            "repo": target.get("repo"),
            **observed,
            **desired,
            "policy_verdict": verdict,
            "verdict_reasons": reasons,
            "last_audited": last_audited,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        svc.save_draft(draft)

        receipt = build_receipt(
            "attestation_draft",
            files_changed=[cfg.DRAFT_REL],
            policy_pass=(verdict == "PASS"),
            errors=[{"workflow_id": workflow_id, "verdict": verdict, "reasons": reasons}] if verdict != "PASS" else [],
            next_machine_action="Continue attesting remaining workflows or run policy check.",
            extra={"workflow_id": workflow_id, "policy_verdict": verdict},
        )
        receipt_name = f"draft_save_{workflow_id}_{last_audited}.json"
        receipt_path = write_receipt(receipt_name, receipt)

        self._send_json({
            "status": "SAVED",
            "workflow_id": workflow_id,
            "policy_verdict": verdict,
            "verdict_reasons": reasons,
            "receipt": receipt_path,
        })

    def _handle_lock_candidate(self, body):
        registry = svc.load_registry()
        draft = svc.load_draft()
        blockers = svc.collect_lock_blockers(registry, draft)

        if blockers:
            receipt = build_receipt(
                "lock_candidate_blocked",
                files_changed=[],
                policy_pass=False,
                errors=blockers,
                next_machine_action="Fix draft attestations until all workflows PASS and are fresh.",
            )
            receipt_path = write_receipt(f"lock_candidate_blocked_{date.today().isoformat()}.json", receipt)
            self._send_json({
                "status": "BLOCKED",
                "message": "Lock candidate rejected — fix aggregated errors before retry.",
                "errors": blockers,
                "receipt": receipt_path,
            }, status=409)
            return

        attestations = draft["attestations"]
        for entry in registry["workflows"]:
            att = attestations.get(entry["workflow_id"])
            if att:
                entry["last_audited"] = att["last_audited"]
        svc.save_registry(registry)

        returncode, report, stderr, cmd = svc.run_checker()
        if report is None:
            errors = [{"kind": "policy_validation", "message": "Checker did not produce a report.", "stderr": stderr}]
            receipt = build_receipt(
                "lock_candidate_blocked",
                files_changed=[cfg.REGISTRY_REL],
                commands_run=[" ".join(cmd)],
                policy_pass=False,
                errors=errors,
                next_machine_action="Inspect checker output and registry state.",
            )
            write_receipt(f"lock_candidate_checker_error_{date.today().isoformat()}.json", receipt)
            self._send_json({"status": "BLOCKED", "message": "Policy checker failed.", "errors": errors}, status=409)
            return

        if report.get("status") != "PASS":
            policy_errors = svc.checker_errors_as_lock_blockers(report)
            receipt = build_receipt(
                "lock_candidate_blocked",
                files_changed=[cfg.REGISTRY_REL],
                commands_run=[" ".join(cmd)],
                policy_pass=False,
                errors=policy_errors,
                next_machine_action="Resolve active policy violations then re-attest.",
            )
            receipt_path = write_receipt(f"lock_candidate_policy_fail_{date.today().isoformat()}.json", receipt)
            self._send_json({
                "status": "BLOCKED",
                "message": "Registry applied but policy validation did not PASS.",
                "errors": policy_errors,
                "checker_report": report,
                "receipt": receipt_path,
            }, status=409)
            return

        today_str = date.today().isoformat()
        branch_name = f"audit/update-registry-{today_str}"
        status = svc.draft_status(registry, draft)
        commit_message = (
            f"Update workflow_registry_v1.json: {status['pass_count']} workflows attested PASS ({today_str})"
        )
        git_result = svc.git_create_bounded_branch_and_commit(branch_name, commit_message)

        receipt = build_receipt(
            "lock_candidate_ready",
            files_changed=[cfg.REGISTRY_REL, cfg.DRAFT_REL],
            commands_run=[" ".join(cmd)],
            policy_pass=True,
            next_machine_action="Review local branch; no push or main merge from this backend.",
            extra={
                "attested_pass_count": status["pass_count"],
                "checker_status": report["status"],
                "git_result": git_result,
                "cloud_write_unrestricted_allowed": cfg.CLOUD_WRITE_UNRESTRICTED_ALLOWED,
                "cloud_write_scope_gate": cfg.CLOUD_WRITE_SCOPE_GATE,
            },
        )
        receipt_path = write_receipt(f"lock_candidate_{today_str}.json", receipt)

        self._send_json({
            "status": "LOCK_CANDIDATE_READY",
            "checker_status": report["status"],
            "git_result": git_result,
            "receipt": receipt_path,
            "cloud_write_unrestricted_allowed": cfg.CLOUD_WRITE_UNRESTRICTED_ALLOWED,
            "cloud_write_scope": "gated",
            "cloud_write_scope_gate": cfg.CLOUD_WRITE_SCOPE_GATE,
            "gate_note": cfg.CLOUD_WRITE_SCOPE_GATE["rule"],
            "note": "Local branch+commit only when git repo present. No push, no main write, no unrestricted cloud propagation.",
        })

    def _handle_policy_check(self):
        returncode, report, stderr, cmd = svc.run_checker()
        if report is None:
            receipt = build_receipt(
                "policy_check",
                commands_run=[" ".join(cmd)],
                policy_pass=False,
                errors=[{"message": "Checker did not produce a report.", "stderr": stderr}],
                next_machine_action="Fix checker invocation or policy files.",
            )
            write_receipt(f"validation_error_{date.today().isoformat()}.json", receipt)
            self._send_json({"status": "ERROR", "message": "Checker did not produce a report.", "stderr": stderr}, status=500)
            return

        policy_pass = report.get("status") == "PASS"
        errors = svc.checker_errors_as_lock_blockers(report) if not policy_pass else []
        receipt = build_receipt(
            "policy_check",
            files_changed=[os.path.join(cfg.RECEIPTS_REL, "control_desk_last_validate.json")],
            commands_run=[" ".join(cmd)],
            policy_pass=policy_pass,
            errors=errors,
            next_machine_action="Fix violations" if not policy_pass else "Proceed toward lock candidate when draft complete.",
            extra={"checker_exit_code": returncode, "report_status": report.get("status")},
        )
        receipt_path = write_receipt(f"validation_{date.today().isoformat()}.json", receipt)
        self._send_json({
            "status": "OK",
            "checker_exit_code": returncode,
            "report": report,
            "receipt": receipt_path,
        })

    def _handle_integrator_sync(self):
        rc1, rc2, summary, stderr, cmd_sync, cmd_summary = svc.run_sync()
        if summary is None:
            receipt = build_receipt(
                "integrator_sync",
                commands_run=[" ".join(cmd_sync), " ".join(cmd_summary)],
                policy_pass=False,
                errors=[{"message": "Sync did not return a summary.", "stderr": stderr}],
                next_machine_action="Inspect noos_integrator_sync_v1.py output.",
            )
            write_receipt(f"sync_error_{date.today().isoformat()}.json", receipt)
            self._send_json({"status": "ERROR", "message": "Sync did not return a summary.", "stderr": stderr}, status=500)
            return

        receipt = build_receipt(
            "integrator_sync",
            files_changed=[os.path.join(".noos", "integrator_state.json")],
            commands_run=[" ".join(cmd_sync), " ".join(cmd_summary)],
            policy_pass=True,
            next_machine_action="Review integrator summary; scoped cloud writes only per NOOS Copilot gate.",
            extra={
                "summary": summary,
                "cloud_write_unrestricted_allowed": cfg.CLOUD_WRITE_UNRESTRICTED_ALLOWED,
                "cloud_write_scope_gate": cfg.CLOUD_WRITE_SCOPE_GATE,
            },
        )
        receipt_path = write_receipt(f"sync_{summary.get('sync_count', 'na')}.json", receipt)
        self._send_json({
            "status": "OK",
            "summary": summary,
            "receipt": receipt_path,
            "cloud_write_unrestricted_allowed": cfg.CLOUD_WRITE_UNRESTRICTED_ALLOWED,
            "cloud_write_scope": "gated",
            "cloud_write_scope_gate": cfg.CLOUD_WRITE_SCOPE_GATE,
            "gate_note": cfg.CLOUD_WRITE_SCOPE_GATE["rule"],
        })
