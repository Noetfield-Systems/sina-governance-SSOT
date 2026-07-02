#!/usr/bin/env python3
"""Brain loop self-heal tick — detect stale verifier receipts and re-trigger /run."""
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
    expand_root,
    get_sandbox,
    git_ref,
    load_registry,
    resolve_sourcea_root,
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


def assess_sandbox(registry: dict[str, Any], sandbox_id: str, receipt: dict[str, Any]) -> dict[str, Any]:
    sandbox = get_sandbox(registry, sandbox_id)
    repo = expand_root(sandbox["deploy_root"])
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Brain loop self-heal tick.")
    parser.add_argument("--sandbox-id", default="brain_worker")
    parser.add_argument("--trigger", action="store_true", help="Trigger /run when stale.")
    parser.add_argument("--write-receipt", help="Receipt output path.")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    load_cloudflare_tokens()
    args = parse_args()
    registry = load_registry()
    receipt_url = f"{registry['verifier_base_url'].rstrip('/')}/receipt/latest"
    latest = fetch_latest_receipt(receipt_url)
    assessment = assess_sandbox(registry, args.sandbox_id, latest)

    rerun_result = None
    if assessment["action"] == "reverify" and args.trigger:
        rerun_result = run_one(registry, args.sandbox_id)

    tick = {
        "receipt_type": "BRAIN_SELF_HEAL_TICK",
        "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
        "sourcea_root": str(resolve_sourcea_root(registry)),
        "latest_verifier_receipt_id": latest.get("receipt_id"),
        "assessment": assessment,
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

    out = Path(args.write_receipt) if args.write_receipt else ROOT / "receipts" / f"brain-self-heal-tick-{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(tick, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tick["tick_receipt_path"] = str(out)

    if args.json:
        print(json.dumps(tick, indent=2, sort_keys=True))
    else:
        print(f"self-heal: action={assessment['action']} reason={assessment['reason']}")
        print(f"tick_receipt: {out}")

    if assessment["action"] == "reverify" and not args.trigger:
        return 2
    if rerun_result and rerun_result.get("result") != "PASS":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
