#!/usr/bin/env python3
"""Step 7 — Real 23-workflow audit via Control Desk /api/attestation/save."""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE = os.environ.get("CONTROL_DESK_URL", "http://127.0.0.1:17877")
TODAY = date.today().isoformat()
RECEIPTS_DIR = os.path.join(PKG_ROOT, "receipts")

# Observed reality from GH workflow list/view, local files, integrator state, CF wrangler.
AUDIT_ROWS = [
    {
        "workflow_id": "ssot_agentic_ci",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GH Actions 'Agentic CI' (workflow id 306625675); path .github/workflows/agentic-ci.yml; "
            "active but YAML not on main — recent runs on branch copilot/cost-locks-v1 (push event). "
            "Deterministic pytest/CI job; no Copilot Automations UI binding observed."
        ),
    },
    {
        "workflow_id": "ssot_security_risk_assessment",
        "observed_trigger": "schedule",
        "observed_mode": "code-scanning",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GitHub dynamic workflow dynamic/github-code-scanning/code-security-risk-assessment "
            "in Noetfield-Systems/sina-governance-ssot; CodeQL/security risk assessment — no LLM."
        ),
    },
    {
        "workflow_id": "ssot_brain_loop_autorun_v1",
        "observed_trigger": "schedule",
        "observed_mode": "integrator+gha",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "Owner noos_integrator: .noos/integrator_state.json sync_count=14 cross_ide_ready=true; "
            "GHA brain-loop-autorun-v1.yml cron */30 + workflow_dispatch; "
            "mac launchd scripts/brain_loop_launchd_entry_v1.sh. No Copilot surface."
        ),
    },
    {
        "workflow_id": "ssot_cost_policy_receipt_validation",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "Surfaced via Agentic CI promotion gate on copilot/cost-locks-v1 (run 28683011633 "
            "'Validate cost_policy receipt schema'); local checker scripts/check_cost_policy.py present. "
            "repo-fences-v1.yml exists locally unmerged on main."
        ),
    },
    {
        "workflow_id": "noos_cost_policy_scan",
        "observed_trigger": "schedule",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GH 'Cost policy scan' (306862038) path .github/workflows/cost-policy-scan.yml; "
            "active; YAML not on main — recent run on branch pr-10. Scheduled cost-policy scanner."
        ),
    },
    {
        "workflow_id": "noos_factory_autorun",
        "observed_trigger": "schedule",
        "observed_mode": "integrator+gha",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA noos-factory-autorun.yml cron 0,10,20,30,40,50 * * * * + repository_dispatch "
            "noos_factory_autorun_tick; CF worker noos-factory-autorun-tick-v1 bridges cron. "
            "No workflow_dispatch (by design). Owner noos_integrator."
        ),
    },
    {
        "workflow_id": "noos_loop_health_checks",
        "observed_trigger": "schedule",
        "observed_mode": "cloudflare-cron",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "CF worker noos-loop-fleet-tick-v1 wrangler.toml crons */5 * * * *; /health endpoint "
            "in cloud/workers/noos-loop-fleet-tick-v1/src/index.js dispatches loop ticks. "
            "GHA loop workflows are separate dispatch targets."
        ),
    },
    {
        "workflow_id": "noos_cross_repo_health",
        "observed_trigger": "schedule",
        "observed_mode": "integrator+gha",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA noos-cross-repo-orchestrator.yml cron 0 */3 * * * + workflow_dispatch; "
            "matrix repos noetfeld-os, Noetfield, TrustField. Owner noos_integrator."
        ),
    },
    {
        "workflow_id": "sourcea_validate_boot",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA validate-sourcea-boot-v1.yml on push/PR paths packages/sourcea-boot/**; "
            "Noetfield-Systems/SourceA workflow id 299504816."
        ),
    },
    {
        "workflow_id": "sourcea_repo_policy_gate",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA repo-policy-gate.yml pull_request on AGENTS.md, repo-policy.json, "
            "scripts/check_sourcea_repo_policy.py paths."
        ),
    },
    {
        "workflow_id": "sourcea_external_verify",
        "observed_trigger": "schedule",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA external-verify.yml: workflow_dispatch, workflow_run after deploy-sourcea-buyer-surfaces-v1, "
            "schedule 30 */6 * * *. Registry trigger=schedule; also chains on deploy completion."
        ),
    },
    {
        "workflow_id": "sourcea_determinism_gate",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA determinism-gate.yml: workflow_dispatch, schedule 30 */6 * * *, push main on "
            "verify_autorun_determinism scripts. PR/push event class verify."
        ),
    },
    {
        "workflow_id": "sourcea_deploy_buyer_surfaces_v1",
        "observed_trigger": "manual",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA deploy-sourcea-buyer-surfaces-v1.yml: workflow_dispatch + push main on landing paths; "
            "production environment gate. Manual promote path per registry."
        ),
    },
    {
        "workflow_id": "noetfield_governance_console_e2e",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA governance-console-e2e.yml PR/push on governance-console/** + workflow_dispatch."
        ),
    },
    {
        "workflow_id": "noetfield_www_ci",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA noetfield-www-ci.yml push/PR on html/assets/sitemap paths."
        ),
    },
    {
        "workflow_id": "noetfield_platform_ci",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA platform-deploy.yml (Platform CI deploy-ready) push/PR on services/packages/infra paths."
        ),
    },
    {
        "workflow_id": "noetfield_supabase_heartbeat",
        "observed_trigger": "schedule",
        "observed_mode": "gha-scheduled",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "DRIFT: registry owner=cloudflare_worker but observed surface is GHA supabase-heartbeat.yml "
            "cron 0 14 * * 1 (Mondays) + workflow_dispatch REST ping. No CF worker cron found for this row."
        ),
    },
    {
        "workflow_id": "noetfield_trust_ledger_ci",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA trust-ledger-ci.yml push/PR on services/governance/** and trust ledger migrations."
        ),
    },
    {
        "workflow_id": "trustfield_autorun_24_7_health",
        "observed_trigger": "schedule",
        "observed_mode": "gha-scheduled",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "DRIFT: registry owner=cloudflare_worker but primary surface is GHA autorun-health.yml "
            "cron */30 + workflow_dispatch. Separate GHA cloud-loop-health.yml exists as backup."
        ),
    },
    {
        "workflow_id": "trustfield_ci",
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA ci.yml push/PR on main|master branches."
        ),
    },
    {
        "workflow_id": "trustfield_deploy_vercel",
        "observed_trigger": "manual",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA vercel-deploy.yml workflow_dispatch only (CLI token deploy). "
            "Hook-based vercel-deploy-hook.yml is separate production path."
        ),
    },
    {
        "workflow_id": "trustfield_e2e_production_smoke",
        "observed_trigger": "schedule",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "GHA e2e-prod-smoke.yml workflow_dispatch + schedule cron 0 15 * * *."
        ),
    },
    {
        "workflow_id": "trustfield_copilot_cloud_agent",
        "observed_trigger": "manual",
        "observed_mode": "unknown",
        "observed_model": "unknown",
        "observed_effort": "unknown",
        "evidence_note": (
            "Registry DISABLE (max_daily_runs=0). GH lists dynamic/copilot-swe-agent/copilot "
            "'Copilot cloud agent' active — YAML not machine-readable. Copilot Automations UI not "
            "scraped this session; cannot attest model/effort/trigger honestly."
        ),
    },
]


def api_post(path, body):
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        BASE + path,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        try:
            return e.code, json.loads(raw)
        except json.JSONDecodeError:
            return e.code, {"raw": raw}


def api_get(path):
    req = urllib.request.Request(BASE + path, method="GET")
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


def main():
    results = []
    for row in AUDIT_ROWS:
        body = {
            **row,
            "desired_trigger": "manual",
            "desired_model": "gpt-5-mini",
            "desired_effort": "low",
            "last_audited": TODAY,
        }
        code, data = api_post("/api/attestation/save", body)
        ok = code == 200 and data.get("status") == "SAVED"
        results.append({
            "workflow_id": row["workflow_id"],
            "http_status": code,
            "saved": ok,
            "policy_verdict": data.get("policy_verdict"),
            "verdict_reasons": data.get("verdict_reasons", []),
            "receipt": data.get("receipt"),
            "error": data.get("error"),
        })
        print(
            f"{'OK' if ok else 'ERR'} {row['workflow_id']}: "
            f"verdict={data.get('policy_verdict')} code={code}"
        )

    _, dash = api_get("/api/dashboard")
    _, draft_path_check = api_get("/api/registry/load")

    summary = {
        "pass": [r["workflow_id"] for r in results if r.get("policy_verdict") == "PASS"],
        "fail": [r["workflow_id"] for r in results if r.get("policy_verdict") == "FAIL"],
        "blocked": [r["workflow_id"] for r in results if r.get("policy_verdict") == "BLOCKED"],
        "todo": [],
        "errors": [r for r in results if not r.get("saved")],
    }

    unresolved = []
    for r in results:
        wid = r["workflow_id"]
        if r.get("policy_verdict") != "PASS":
            unresolved.append({
                "workflow_id": wid,
                "verdict": r.get("policy_verdict"),
                "reasons": r.get("verdict_reasons"),
            })
    unresolved.extend([
        {
            "workflow_id": None,
            "kind": "surface_drift",
            "detail": "noetfield_supabase_heartbeat registry owner cloudflare_worker vs GHA supabase-heartbeat.yml",
        },
        {
            "workflow_id": None,
            "kind": "surface_drift",
            "detail": "trustfield_autorun_24_7_health registry owner cloudflare_worker vs GHA autorun-health.yml",
        },
        {
            "workflow_id": None,
            "kind": "branch_gap",
            "detail": "ssot_agentic_ci + noos_cost_policy_scan workflow YAML not on main branch",
        },
        {
            "workflow_id": None,
            "kind": "backend_gap",
            "detail": "verdict.py does not recognize observed_model=model:none for deterministic surfaces (BLOCKED)",
        },
        {
            "workflow_id": "trustfield_copilot_cloud_agent",
            "kind": "copilot_ui_unread",
            "detail": "Copilot Automations UI / dynamic copilot workflow settings not machine-readable",
        },
    ])

    receipt = {
        "action": "step7_workflow_audit_23",
        "repo": "sina-governance-SSOT",
        "package": "noos-control-desk-v1",
        "step": 7,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "policy_pass": len(summary["pass"]) == 23,
        "files_changed": [".noos/registry_draft.json"],
        "commands_run": [
            f"python3 scripts/run_step7_workflow_audit_v1.py (via {BASE}/api/attestation/save x23)",
        ],
        "errors": unresolved,
        "summary": {
            "total": 23,
            "pass_count": len(summary["pass"]),
            "fail_count": len(summary["fail"]),
            "blocked_count": len(summary["blocked"]),
            "todo_count": 23 - len(summary["pass"]) - len(summary["fail"]) - len(summary["blocked"]),
            "pass_ids": summary["pass"],
            "fail_ids": summary["fail"],
            "blocked_ids": summary["blocked"],
            "ready_for_lock_candidate": dash.get("ready_for_lock_candidate", False),
        },
        "dashboard": dash,
        "attestation_results": results,
        "next_machine_action": (
            "Step 8 policy check — do not submit lock candidate until all 23 PASS "
            "(backend may need model:none recognition for deterministic workflows)."
        ),
        "package_status": "SCAFFOLD_READY_AUDIT_PENDING",
        "active_promotion": False,
    }

    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    receipt_name = f"step7_workflow_audit_{TODAY}.json"
    receipt_path = os.path.join(RECEIPTS_DIR, receipt_name)
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    print(f"\nSUMMARY PASS={len(summary['pass'])} FAIL={len(summary['fail'])} "
          f"BLOCKED={len(summary['blocked'])}")
    print(f"Receipt: {receipt_path}")
    return 0 if len(results) == 23 else 1


if __name__ == "__main__":
    sys.exit(main())
