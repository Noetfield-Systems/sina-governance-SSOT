#!/usr/bin/env python3
"""Step 7F-C — Final re-attestation for affected workflows after 7F-A/7F-B."""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DRAFT_PATH = os.path.join(PKG_ROOT, ".noos", "registry_draft.json")
BASE = os.environ.get("CONTROL_DESK_URL", "http://127.0.0.1:17878")
TODAY = date.today().isoformat()
RECEIPTS_DIR = os.path.join(PKG_ROOT, "receipts")

AFFECTED = [
    "trustfield_copilot_cloud_agent",
    "ssot_agentic_ci",
    "noos_cost_policy_scan",
]

# Honest observed updates — preserve prior fields where surface unchanged.
REATTEST_OBSERVED = {
    "ssot_agentic_ci": {
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "Step 7F-A: merge_intended_branch_pending — agentic-ci.yml NOT on main (verified 2026-07-04; "
            "main has brain-loop-autorun-v1.yml only). PR #5 OPEN copilot/cost-locks-v1→main. "
            "Agentic CI FAIL run 28695304453: ModuleNotFoundError yaml in cost_policy_enforcer.py. "
            "7F-B incomplete (CI not green, not merged). Branch YAML also has hourly schedule cron — "
            "registry trigger=event; reconcile post-merge."
        ),
    },
    "noos_cost_policy_scan": {
        "observed_trigger": "event",
        "observed_mode": "deterministic",
        "observed_model": "model:none",
        "observed_effort": "low",
        "evidence_note": (
            "Step 7F-A: merge_intended_branch_pending — cost-policy-scan.yml NOT on main (verified 2026-07-04). "
            "PR #22 OPEN pr-10→main. scan FAIL run 28683001606: cost_policy_scan.py exit 1. "
            "7F-B incomplete (CI not green, not merged). Branch YAML push/PR triggers only; "
            "registry trigger=schedule — reconcile post-merge."
        ),
    },
    "trustfield_copilot_cloud_agent": {
        "observed_trigger": "manual",
        "observed_mode": "unknown",
        "observed_model": "unknown",
        "observed_effort": "unknown",
        "evidence_note": (
            "Step 7F-C refresh. Registry DISABLE (max_daily_runs=0). GH dynamic/copilot-swe-agent/copilot "
            "'Copilot cloud agent' active (id 306444735); last observed success run 28640779314 on "
            "cursor/chatbot-audit-system 2026-07-03. Surface/registry mismatch: GH active vs registry DISABLE. "
            "Copilot Automations UI model/effort/mode not machine-readable — cannot attest beyond unknown."
        ),
    },
}


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
    with open(DRAFT_PATH, "r", encoding="utf-8") as f:
        draft = json.load(f)
    attestations = draft.get("attestations", {})

    results = []
    for workflow_id in AFFECTED:
        if workflow_id not in attestations:
            print(f"ERR missing prior attestation: {workflow_id}", file=sys.stderr)
            return 1
        prior = attestations[workflow_id]
        observed = REATTEST_OBSERVED[workflow_id]
        body = {
            "workflow_id": workflow_id,
            **observed,
            "desired_trigger": prior.get("desired_trigger", "manual"),
            "desired_model": prior.get("desired_model", "gpt-5-mini"),
            "desired_effort": prior.get("desired_effort", "low"),
            "last_audited": TODAY,
        }
        code, data = api_post("/api/attestation/save", body)
        ok = code == 200 and data.get("status") == "SAVED"
        results.append({
            "workflow_id": workflow_id,
            "saved": ok,
            "policy_verdict": data.get("policy_verdict"),
            "verdict_reasons": data.get("verdict_reasons", []),
            "receipt": data.get("receipt"),
            "error": data.get("error"),
        })
        print(f"{'OK' if ok else 'ERR'} {workflow_id}: verdict={data.get('policy_verdict')}")

    _, dash = api_get("/api/dashboard")

    with open(DRAFT_PATH, "r", encoding="utf-8") as f:
        final_draft = json.load(f)

    all_verdicts = {
        wid: final_draft["attestations"][wid]["policy_verdict"]
        for wid in final_draft.get("attestations", {})
    }
    summary = {
        "pass": [w for w, v in all_verdicts.items() if v == "PASS"],
        "fail": [w for w, v in all_verdicts.items() if v == "FAIL"],
        "blocked": [w for w, v in all_verdicts.items() if v == "BLOCKED"],
        "todo": [w for w in all_verdicts if w not in all_verdicts],
    }

    receipt = {
        "action": "step7fc_final_reattestation",
        "repo": "sina-governance-SSOT",
        "package": "noos-control-desk-v1",
        "step": "7F-C",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "policy_pass": dash.get("ready_for_lock_candidate", False),
        "files_changed": [".noos/registry_draft.json"],
        "commands_run": [
            f"python3 scripts/run_step7fc_final_reattestation_v1.py (via {BASE}/api/attestation/save x3)"
        ],
        "affected_workflows": AFFECTED,
        "reattest_results": results,
        "seven_f_b_status": "incomplete",
        "seven_f_b_evidence": {
            "ssot_pr5": "OPEN, CI FAIL",
            "noos_pr22": "OPEN, CI FAIL",
            "main_merge": False,
        },
        "summary": {
            "total": dash.get("registry_entries", 23),
            "pass_count": dash.get("pass_count"),
            "fail_count": dash.get("fail_count"),
            "blocked_count": dash.get("blocked_count"),
            "todo_count": dash.get("todo_count"),
            "pass_ids": summary["pass"],
            "fail_ids": summary["fail"],
            "blocked_ids": summary["blocked"],
            "ready_for_lock_candidate": dash.get("ready_for_lock_candidate", False),
        },
        "errors": [
            r for r in results if r.get("policy_verdict") != "PASS"
        ],
        "remaining_blockers": [
            {
                "workflow_id": "trustfield_copilot_cloud_agent",
                "kind": "copilot_ui_unread",
                "detail": "Copilot UI not machine-readable; registry DISABLE vs GH active",
            },
            {
                "workflow_id": "ssot_agentic_ci",
                "kind": "branch_pending",
                "detail": "7F-B incomplete — not on main; PR #5 CI red",
            },
            {
                "workflow_id": "noos_cost_policy_scan",
                "kind": "branch_pending",
                "detail": "7F-B incomplete — not on main; PR #22 CI red",
            },
        ],
        "next_machine_action": "Complete 7F-B CI fixes + bounded merge; re-attest Copilot after UI evidence.",
        "package_status": "SCAFFOLD_READY_AUDIT_PENDING",
        "lock_candidate_submitted": False,
    }

    receipt_path = os.path.join(RECEIPTS_DIR, f"step7fc_final_reattestation_{TODAY}.json")
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    print(
        f"\nFINAL PASS={dash.get('pass_count')} BLOCKED={dash.get('blocked_count')} "
        f"ready={dash.get('ready_for_lock_candidate')}"
    )
    print(f"Receipt: {receipt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
