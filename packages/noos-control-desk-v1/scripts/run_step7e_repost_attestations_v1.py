#!/usr/bin/env python3
"""Step 7E — Re-post Step 7 attestations after 7B verdict + 7D registry patches."""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timezone

PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DRAFT_PATH = os.path.join(PKG_ROOT, ".noos", "registry_draft.json")
BASE = os.environ.get("CONTROL_DESK_URL", "http://127.0.0.1:17877")
TODAY = date.today().isoformat()
RECEIPTS_DIR = os.path.join(PKG_ROOT, "receipts")

# Step 7D registry alignment — observed fields only; evidence preserved/annotated.
OBSERVED_CORRECTIONS = {
    "sourcea_external_verify": {
        "observed_trigger": "event",
        "evidence_note": (
            "GHA external-verify.yml: workflow_dispatch, workflow_run after "
            "deploy-sourcea-buyer-surfaces-v1 (main success), path-filtered push. "
            "Step 7D: no schedule stanza in live YAML — primary surface is event/workflow_run chain."
        ),
    },
    "noetfield_supabase_heartbeat": {
        "evidence_note": (
            "GHA supabase-heartbeat.yml cron 0 14 * * 1 (Mondays) + workflow_dispatch REST ping. "
            "Step 7D: registry owner corrected to github_actions (was cloudflare_worker seed error)."
        ),
    },
    "trustfield_autorun_24_7_health": {
        "evidence_note": (
            "GHA autorun-health.yml cron */30 + workflow_dispatch. "
            "Step 7D: registry owner corrected to github_actions (was cloudflare_worker seed error). "
            "cloud-loop-health.yml is separate backup."
        ),
    },
}

BRANCH_ONLY_BLOCKERS = [
    {
        "workflow_id": "ssot_agentic_ci",
        "kind": "branch_only_pending",
        "detail": "agentic-ci.yml not on main — merge before lock candidate",
    },
    {
        "workflow_id": "noos_cost_policy_scan",
        "kind": "branch_only_pending",
        "detail": "cost-policy-scan.yml not on main — merge before lock candidate",
    },
]

COPILOT_BLOCKERS = [
    {
        "workflow_id": "trustfield_copilot_cloud_agent",
        "kind": "surface_registry_mismatch",
        "detail": "Registry DISABLE (max_daily_runs=0) vs GH Copilot cloud agent active; Copilot UI unread",
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


def load_attestations():
    with open(DRAFT_PATH, "r", encoding="utf-8") as f:
        draft = json.load(f)
    return draft.get("attestations", {})


def build_post_body(workflow_id, att):
    body = {
        "workflow_id": workflow_id,
        "observed_trigger": att.get("observed_trigger", ""),
        "observed_mode": att.get("observed_mode", ""),
        "observed_model": att.get("observed_model", ""),
        "observed_effort": att.get("observed_effort", ""),
        "evidence_note": att.get("evidence_note", ""),
        "desired_trigger": att.get("desired_trigger", "manual"),
        "desired_model": att.get("desired_model", "gpt-5-mini"),
        "desired_effort": att.get("desired_effort", "low"),
        "last_audited": TODAY,
    }
    fixes = OBSERVED_CORRECTIONS.get(workflow_id, {})
    body.update(fixes)
    return body


def main():
    attestations = load_attestations()
    if len(attestations) != 23:
        print(f"FATAL: expected 23 attestations, found {len(attestations)}", file=sys.stderr)
        return 1

    results = []
    for workflow_id in sorted(attestations.keys()):
        body = build_post_body(workflow_id, attestations[workflow_id])
        code, data = api_post("/api/attestation/save", body)
        ok = code == 200 and data.get("status") == "SAVED"
        results.append({
            "workflow_id": workflow_id,
            "http_status": code,
            "saved": ok,
            "policy_verdict": data.get("policy_verdict"),
            "verdict_reasons": data.get("verdict_reasons", []),
            "receipt": data.get("receipt"),
            "error": data.get("error"),
        })
        print(
            f"{'OK' if ok else 'ERR'} {workflow_id}: verdict={data.get('policy_verdict')} code={code}"
        )

    _, dash = api_get("/api/dashboard")

    summary = {
        "pass": [r["workflow_id"] for r in results if r.get("policy_verdict") == "PASS"],
        "fail": [r["workflow_id"] for r in results if r.get("policy_verdict") == "FAIL"],
        "blocked": [r["workflow_id"] for r in results if r.get("policy_verdict") == "BLOCKED"],
        "todo": [],
    }

    unresolved = []
    for r in results:
        if r.get("policy_verdict") != "PASS":
            unresolved.append({
                "workflow_id": r["workflow_id"],
                "verdict": r.get("policy_verdict"),
                "reasons": r.get("verdict_reasons"),
            })
    for b in BRANCH_ONLY_BLOCKERS:
        if b["workflow_id"] in summary["pass"]:
            unresolved.append(b)
    unresolved.extend(COPILOT_BLOCKERS)
    unresolved.append({
        "workflow_id": None,
        "kind": "rcp5_staleness",
        "detail": "workflow_registry_v1.json last_audited still TODO until lock candidate (not submitted)",
    })

    receipt = {
        "action": "step7e_repost_attestations",
        "repo": "sina-governance-SSOT",
        "package": "noos-control-desk-v1",
        "step": "7E",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "policy_pass": len(summary["pass"]) == 23,
        "files_changed": [".noos/registry_draft.json"],
        "commands_run": [
            f"python3 scripts/run_step7e_repost_attestations_v1.py (via {BASE}/api/attestation/save x23)",
        ],
        "patches_applied": ["7B verdict (model:none deterministic PASS)", "7D registry drift (3 rows)"],
        "observed_corrections": OBSERVED_CORRECTIONS,
        "errors": unresolved,
        "summary": {
            "total": 23,
            "pass_count": len(summary["pass"]),
            "fail_count": len(summary["fail"]),
            "blocked_count": len(summary["blocked"]),
            "todo_count": 0,
            "pass_ids": summary["pass"],
            "fail_ids": summary["fail"],
            "blocked_ids": summary["blocked"],
            "ready_for_lock_candidate": dash.get("ready_for_lock_candidate", False),
        },
        "dashboard": dash,
        "attestation_results": results,
        "next_machine_action": (
            "Resolve branch-only + Copilot blockers; Step 8 policy check when 23/23 PASS."
        ),
        "package_status": "SCAFFOLD_READY_AUDIT_PENDING",
        "active_promotion": False,
        "lock_candidate_submitted": False,
    }

    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    receipt_path = os.path.join(RECEIPTS_DIR, f"step7e_repost_attestations_{TODAY}.json")
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    print(
        f"\nSUMMARY PASS={len(summary['pass'])} FAIL={len(summary['fail'])} "
        f"BLOCKED={len(summary['blocked'])}"
    )
    print(f"Receipt: {receipt_path}")
    return 0 if len(results) == 23 else 1


if __name__ == "__main__":
    sys.exit(main())
