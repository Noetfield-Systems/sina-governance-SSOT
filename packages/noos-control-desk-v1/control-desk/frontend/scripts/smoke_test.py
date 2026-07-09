#!/usr/bin/env python3
"""Step 3 frontend smoke test — hits backend routes, writes receipt."""
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone

BASE = os.environ.get("CONTROL_DESK_URL", "http://127.0.0.1:17877")
PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RECEIPTS_DIR = os.path.join(PKG_ROOT, "receipts")


def req(method, path, body=None, parse_json=True):
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            if not parse_json:
                return resp.status, raw
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8")
        if not parse_json:
            return e.code, raw
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            payload = {"raw": raw}
        return e.code, payload


def check(name, ok, detail=""):
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def main():
    results = []
    print(f"NOOS Control Desk frontend smoke @ {BASE}\n")

    code, html = req("GET", "/", parse_json=False)
    ok = code == 200 and ("NOOS Control Desk" in html or "NOOS CONTROL DESK" in html)
    results.append(check("1. App opens at localhost:17877", ok, f"HTTP {code}"))

    code, dash = req("GET", "/api/dashboard")
    ok = code == 200 and dash.get("registry_entries") == 23
    results.append(check("2. Dashboard loads registry count", ok, f"entries={dash.get('registry_entries')}"))

    code, reg = req("GET", "/api/registry/load")
    ok = code == 200 and len(reg.get("workflows", [])) == 23
    results.append(check("2b. Registry load 23 workflows", ok))

    code, att = req(
        "POST",
        "/api/attestation/save",
        {
            "workflow_id": "ssot_agentic_ci",
            "observed_model": "gpt-5.4",
            "observed_effort": "high",
            "observed_trigger": "hourly",
            "observed_mode": "autopilot",
            "evidence_note": "smoke test leak",
            "desired_model": "gpt-5-mini",
            "desired_effort": "low",
            "desired_trigger": "manual",
            "last_audited": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        },
    )
    ok = code == 200 and att.get("policy_verdict") == "FAIL"
    results.append(check("3. Save observed state", ok, f"verdict={att.get('policy_verdict')}"))

    ok = att.get("policy_verdict") == "FAIL" and len(att.get("verdict_reasons", [])) > 0
    results.append(check("4. Backend verdict displayed honestly", ok))

    code, draft_save = req(
        "POST",
        "/api/registry/save-draft",
        {"workflows": reg.get("workflows", [])[:1]},
    )
    ok = code == 200 and draft_save.get("status") == "SAVED"
    results.append(check("5. Save Draft with incomplete audits", ok))

    code, policy = req("POST", "/api/policy/check", {})
    active = (policy.get("report") or {}).get("violations_active") or []
    ok = code == 200 and len(active) > 0
    results.append(check("6. Policy Validator aggregated errors", ok, f"active={len(active)}"))

    code, sync = req("POST", "/api/integrator/sync", {})
    ok = (
        code == 200
        and sync.get("cloud_write_unrestricted_allowed") is False
        and sync.get("cloud_write_scope") == "gated"
        and bool(sync.get("gate_note") or (sync.get("cloud_write_scope_gate") or {}).get("rule"))
    )
    results.append(check("7. Integrator sync scope-gated cloud writes", ok))

    code, receipts = req("GET", "/api/receipts/list")
    ok = code == 200 and isinstance(receipts.get("receipts"), list) and len(receipts["receipts"]) > 0
    results.append(check("8. Receipts listed", ok, f"count={len(receipts.get('receipts', []))}"))

    code, pr = req("GET", "/api/pr/prepare")
    ok = code == 200 and pr.get("status") == "PLAN_ONLY" and dash.get("ready_for_lock_candidate") is False
    results.append(check("9. PR Prep plan-only, not fake ready", ok, f"plan={pr.get('status')}"))

    code, lock = req("POST", "/api/lock-candidate/submit", {})
    ok = code == 409 and lock.get("status") == "BLOCKED"
    results.append(check("9b. Lock candidate rejected when not ready", ok))

    passed = sum(results)
    total = len(results)
    all_pass = passed == total

    receipt = {
        "action": "frontend_step3_smoke",
        "repo": "sina-governance-SSOT",
        "package": "noos-control-desk-v1",
        "step": "frontend_builder_step_3",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "policy_pass": all_pass,
        "checks_passed": passed,
        "checks_total": total,
        "base_url": BASE,
        "acceptance": {
            "app_localhost_17877": results[0],
            "dashboard_registry": results[1],
            "attestation_save": results[2],
            "verdict_honest": results[3],
            "save_draft": results[4],
            "policy_aggregated": results[5],
            "integrator_local": results[6],
            "receipts_list": results[7],
            "pr_prep_plan_only": results[8],
            "lock_blocked": results[9],
        },
        "next_machine_action": "Step 5 — NOOS Sync Mode Patch.",
    }

    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    receipt_path = os.path.join(RECEIPTS_DIR, "frontend_step3_smoke_v1.json")
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)

    print(f"\n{'ALL PASS' if all_pass else 'FAILURES'}: {passed}/{total}")
    print(f"Receipt: {receipt_path}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
