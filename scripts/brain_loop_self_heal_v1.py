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
    now = dt.datetime.now(dt.timezone.utc)
    heartbeat_dt = parse_timestamp(latest.get("checked_at") or latest.get("recorded_at"))
    heartbeat_at = heartbeat_dt.isoformat() if heartbeat_dt else None
    heartbeat_age_minutes = None
    if heartbeat_dt is not None:
        heartbeat_age_minutes = int((now - heartbeat_dt).total_seconds() // 60)

    heartbeat_max_age_minutes = int(targets.get("heartbeat_max_age_minutes", 360))
    min_health_score = int(targets.get("min_health_score", 85))
    latest_result = str(latest.get("result") or latest.get("status") or "")
    latest_failures = latest.get("failures") or []
    drift_detected = assessment["action"] == "reverify"

    health_score = 100
    if heartbeat_age_minutes is None:
        health_score -= 30
    elif heartbeat_age_minutes > heartbeat_max_age_minutes:
        health_score -= 40
    elif heartbeat_age_minutes > max(heartbeat_max_age_minutes - 60, heartbeat_max_age_minutes * 3 // 4):
        health_score -= 10
    if latest_result not in {"PASS", "MATCH"}:
        health_score -= 25
    if latest_failures:
        health_score -= 15
    if drift_detected:
        health_score -= 20
    if assessment["reason"] != "receipt_fresh":
        health_score -= 5
    health_score = max(0, min(100, health_score))

    slo_miss = (
        heartbeat_age_minutes is None
        or heartbeat_age_minutes > heartbeat_max_age_minutes
        or health_score < min_health_score
        or latest_result not in {"PASS", "MATCH"}
        or bool(latest_failures)
    )
    if drift_detected and not slo_miss:
        health_state = "degraded"
    elif slo_miss:
        health_state = "at_risk"
    else:
        health_state = "healthy"

    proof_reason = []
    if heartbeat_age_minutes is None:
        proof_reason.append("heartbeat_missing")
    elif heartbeat_age_minutes > heartbeat_max_age_minutes:
        proof_reason.append("heartbeat_stale")
    if health_score < min_health_score:
        proof_reason.append("health_score_below_threshold")
    if latest_result not in {"PASS", "MATCH"}:
        proof_reason.append("verifier_result_unhealthy")
    if latest_failures:
        proof_reason.append("verifier_failures_present")
    if drift_detected:
        proof_reason.append("drift_detected")
    if assessment["reason"] != "receipt_fresh":
        proof_reason.append(assessment["reason"])
    if not proof_reason:
        proof_reason.append("health_ok")

    return {
        "heartbeat_at": heartbeat_at,
        "heartbeat_age_minutes": heartbeat_age_minutes,
        "health_score": health_score,
        "health_state": health_state,
        "health_threshold": min_health_score,
        "heartbeat_max_age_minutes": heartbeat_max_age_minutes,
        "slo_targets": targets,
        "slo_miss": slo_miss,
        "drift_detected": drift_detected,
        "proof_reason": ",".join(proof_reason),
    }


def build_kaizen_proof_receipt(
    registry: dict[str, Any],
    latest: dict[str, Any],
    assessment: dict[str, Any],
    rerun_result: dict[str, Any] | None,
    health: dict[str, Any],
    *,
    sandbox_id: str,
) -> dict[str, Any]:
    return {
        "receipt_type": "BRAIN_KAIZEN_PROOF",
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "sourcea_root": str(resolve_sourcea_root(registry)),
        "workflow": "brain_loop_self_heal_v1",
        "sandbox_id": sandbox_id,
        "latest_verifier_receipt_id": latest.get("receipt_id"),
        "latest_verifier_result": latest.get("result") or latest.get("status"),
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
    }


def parse_args() -> argparse.Namespace:
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
        proof_prefix = str(workflow_health_targets(registry).get("kaizen_proof_prefix", "receipts/brain-kaizen-proof-"))
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
            print(f"kaizen_proof: {proof_path}")

    if assessment["action"] == "reverify" and not args.trigger:
        return 2
    if rerun_result and rerun_result.get("result") != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
