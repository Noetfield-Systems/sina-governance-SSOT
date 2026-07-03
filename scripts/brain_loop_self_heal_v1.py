#!/usr/bin/env python3
'''Brain loop self-heal tick — detect stale verifier receipts and re-trigger /run.'''
from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gates.cf_tokens import load_cloudflare_tokens  # noqa: E402
from scripts.brain_domain_registry_v1 import (  # noqa: E402
    bundle_sha256,
    get_sandbox,
    git_ref,
    load_registry,
    resolve_sandbox_repo,
    resolve_sourcea_root,
    workflow_health_targets,
)
from scripts.brain_loop_health_model_v1 import (  # noqa: E402
    build_improvement_receipt_v2,
    score_loop_health,
)
from scripts.trigger_verifier_run_v1 import run_one  # noqa: E402


def fetch_latest_receipt(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "brain-loop-self-heal-v1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def is_ancestor(repo: Path, ancestor: str, head: str) -> bool:
    result = subprocess.run(
        ["git", "merge-base", "--is-ancestor", ancestor, head],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def parse_timestamp(value: Any) -> dt.datetime | None:
    if not value:
        return None
    if isinstance(value, dt.datetime):
        return value.astimezone(dt.timezone.utc)
    try:
        return dt.datetime.fromisoformat(str(value).replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except ValueError:
        return None


def calculate_health_snapshot(targets: dict[str, Any], latest: dict[str, Any], assessment: dict[str, Any]) -> dict[str, Any]:
    heartbeat_dt = parse_timestamp(latest.get("checked_at") or latest.get("recorded_at"))
    heartbeat_at = heartbeat_dt.isoformat() if heartbeat_dt else None
    freshness_age_minutes = None
    if heartbeat_dt is not None:
        freshness_age_minutes = max(0.0, (dt.datetime.now(dt.timezone.utc) - heartbeat_dt).total_seconds() / 60.0)

    latest_result = str(latest.get("result") or latest.get("status") or "")
    success_rate_pct = 100.0 if latest_result in {"PASS", "MATCH"} else 0.0
    latency_minutes = latest.get("latency_minutes")
    if latency_minutes is None:
        latency_minutes = latest.get("execution_latency_minutes")
    if latency_minutes is None:
        latency_minutes = latest.get("duration_minutes")
    if latency_minutes is not None:
        latency_minutes = float(latency_minutes)

    health = score_loop_health(
        targets,
        freshness_age_minutes=freshness_age_minutes,
        success_rate_pct=success_rate_pct,
        latency_minutes=latency_minutes,
        latest_result=latest_result,
        failure_count=len(latest.get("failures") or []),
        drift_detected=assessment["action"] == "reverify",
        reason=assessment["reason"],
        heartbeat_at=heartbeat_at,
    )
    health["latest_result"] = latest_result
    health["heartbeat_at"] = heartbeat_at
    health["checked_at"] = latest.get("checked_at") or latest.get("recorded_at")
    return health


def build_kaizen_proof_receipt(
    registry: dict[str, Any],
    latest: dict[str, Any],
    assessment: dict[str, Any],
    rerun_result: dict[str, Any] | None,
    health: dict[str, Any],
    *,
    sandbox_id: str,
) -> dict[str, Any]:
    diff_summary = ", ".join(
        part
        for part in [
            f"freshness={health.get('freshness_age_minutes')}m/{health.get('freshness_target_minutes')}m",
            f"success_rate={health.get('success_rate_pct')}%/{health.get('success_rate_target')}%",
            f"latency={health.get('latency_minutes')}m/{health.get('latency_target_minutes')}m",
        ]
        if part
    )
    expected_effect = (
        "Keep the brain loop within freshness, success-rate, and latency SLOs and surface explicit misses early."
    )
    roi = {
        "expected_hours_saved_per_week": 1,
        "confidence": "medium",
        "risk_reduction": "medium",
    }
    rollback_command = f"git revert {subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()}"
    evidence = [
        {
            "kind": "latest_verifier_receipt",
            "receipt_id": latest.get("receipt_id"),
            "result": latest.get("result") or latest.get("status"),
            "checked_at": latest.get("checked_at"),
        },
        {
            "kind": "health_snapshot",
            "health_score": health.get("health_score"),
            "health_state": health.get("health_state"),
            "slo_miss": health.get("slo_miss"),
            "missed_targets": health.get("missed_targets", []),
        },
        {
            "kind": "assessment",
            "action": assessment.get("action"),
            "reason": assessment.get("reason"),
        },
    ]
    if rerun_result:
        evidence.append(
            {
                "kind": "rerun_result",
                "receipt_id": rerun_result.get("receipt_id"),
                "result": rerun_result.get("result"),
                "status": rerun_result.get("status"),
            }
        )
    return build_improvement_receipt_v2(
        registry,
        health,
        workflow_name="brain_loop_self_heal_v1",
        diff_summary=diff_summary,
        expected_effect=expected_effect,
        roi=roi,
        rollback_command=rollback_command,
        evidence=evidence,
        trigger="drift_or_slo_miss",
        latest=latest,
        assessment=assessment,
    )


def parse_args(
) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brain loop self-heal tick.")
    parser.add_argument("--sandbox-id", default="brain_worker")
    parser.add_argument("--trigger", action="store_true", help="Trigger /run when stale.")
    parser.add_argument("--write-receipt", help="Receipt output path.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def assess_sandbox(registry: dict[str, Any], sandbox_id: str, receipt: dict[str, Any]) -> dict[str, Any]:
    sandbox = get_sandbox(registry, sandbox_id)
    repo = resolve_sandbox_repo(registry, sandbox)
    head = git_ref(repo, sandbox.get("branch", "main"))
    bundle_sha = bundle_sha256(repo, head)
    receipt_ref = str(receipt.get("candidate_ref") or "")
    receipt_sha = str(receipt.get("candidate_sha256") or "")

    action = "skip"
    reason = "receipt_fresh"

    if receipt_sha and receipt_sha == bundle_sha:
        reason = "bundle_sha_match"
    elif receipt_ref and (head.startswith(receipt_ref) or receipt_ref.startswith(head)):
        reason = "ref_prefix_match"
    elif receipt_ref and is_ancestor(repo, receipt_ref, head):
        if receipt_sha == bundle_sha:
            reason = "ancestor_bundle_match"
        else:
            action = "reverify"
            reason = "ancestor_ref_but_bundle_sha_changed"
    else:
        action = "reverify"
        reason = "receipt_ref_stale_or_missing"

    return {
        "sandbox_id": sandbox_id,
        "head_ref": head,
        "bundle_sha256": bundle_sha,
        "receipt_ref": receipt_ref,
        "receipt_sha256": receipt_sha,
        "action": action,
        "reason": reason,
    }


def main() -> int:
    load_cloudflare_tokens()
    args = parse_args()
    registry = load_registry()
    receipt_url = f"{registry['verifier_base_url'].rstrip('/')}/receipt/latest"
    latest = fetch_latest_receipt(receipt_url)
    assessment = assess_sandbox(registry, args.sandbox_id, latest)
    health = calculate_health_snapshot(workflow_health_targets(registry), latest, assessment)

    rerun_result = None
    if assessment["action"] == "reverify" and args.trigger:
        rerun_result = run_one(registry, args.sandbox_id)

    proof_receipt = None
    proof_path = None
    if health["slo_miss"] or health["drift_detected"]:
        proof_receipt = build_kaizen_proof_receipt(
            registry,
            latest,
            assessment,
            rerun_result,
            health,
            sandbox_id=args.sandbox_id,
        )
        proof_prefix = str(workflow_health_targets(registry).get("kaizen_proof_prefix", "receipts/improvement-receipt-v2-"))
        proof_path = ROOT / f"{proof_prefix}{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        proof_path.parent.mkdir(parents=True, exist_ok=True)
        proof_path.write_text(json.dumps(proof_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        proof_receipt["proof_receipt_path"] = str(proof_path)

    tick = {
        "receipt_type": "BRAIN_SELF_HEAL_TICK",
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sourcea_root": str(resolve_sourcea_root(registry)),
        "latest_verifier_receipt_id": latest.get("receipt_id"),
        "assessment": assessment,
        "heartbeat_at": health["heartbeat_at"],
        "heartbeat_age_minutes": health["heartbeat_age_minutes"],
        "health_score": health["health_score"],
        "health_state": health["health_state"],
        "health_threshold": health["health_threshold"],
        "slo_targets": health["slo_targets"],
        "slo_miss": health["slo_miss"],
        "drift_detected": health["drift_detected"],
        "proof_reason": health["proof_reason"],
        "triggered_rerun": bool(rerun_result),
        "rerun_result": (
            {
                "receipt_id": rerun_result.get("receipt_id"),
                "result": rerun_result.get("result"),
                "status": rerun_result.get("status"),
            }
            if rerun_result
            else None
        ),
        "improvement_receipt_path": str(proof_path) if proof_path else None,
        "kaizen_proof_path": str(proof_path) if proof_path else None,
    }

    out = Path(args.write_receipt) if args.write_receipt else ROOT / "receipts" / f"brain-self-heal-tick-{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tick, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tick["tick_receipt_path"] = str(out)

    if args.json:
        print(json.dumps(tick, indent=2, sort_keys=True))
    else:
        print(f"self-heal: action={assessment['action']} reason={assessment['reason']}")
        print(f"tick_receipt: {out}")
        if proof_path:
            print(f"improvement_receipt: {proof_path}")

    if assessment["action"] == "reverify" and not args.trigger:
        return 2
    if rerun_result and rerun_result.get("result") != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
