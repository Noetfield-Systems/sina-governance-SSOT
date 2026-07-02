#!/usr/bin/env python3
"""Trigger SG verifier /run for one or more brain domain sandboxes."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gates.cf_tokens import load_cloudflare_tokens  # noqa: E402
from scripts.brain_domain_registry_v1 import (  # noqa: E402
    build_verifier_post_body,
    expand_root,
    get_sandbox,
    load_registry,
    resolve_sourcea_root,
)


def post_verifier_run(base_url: str, body: dict[str, Any]) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/run"
    data = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "trigger-verifier-run-v1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
            payload["_http_status"] = response.status
            return payload
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(detail)
        except json.JSONDecodeError:
            payload = {"error": detail}
        payload["_http_status"] = exc.code
        return payload
    except urllib.error.URLError as exc:
        return {"status": "FAIL", "result": "FAIL", "failures": [str(exc.reason)], "_http_status": 0}


def run_one(registry: dict[str, Any], sandbox_id: str, *, ref: str | None = None) -> dict[str, Any]:
    sandbox = get_sandbox(registry, sandbox_id)
    repo = expand_root(sandbox["deploy_root"])
    body = build_verifier_post_body(sandbox, repo, ref=ref)
    receipt = post_verifier_run(registry["verifier_base_url"], body)
    return {
        "sandbox_id": sandbox_id,
        "candidate_ref": body["candidate_ref"],
        "artifact_type": sandbox["artifact_type"],
        "receipt_id": receipt.get("receipt_id"),
        "status": receipt.get("status"),
        "result": receipt.get("result"),
        "candidate_sha256": receipt.get("candidate_sha256"),
        "http_status": receipt.get("_http_status"),
        "failures": receipt.get("failures") or [],
        "receipt": receipt,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Trigger verifier /run for brain domain sandboxes.")
    parser.add_argument("--sandbox-id", action="append", dest="sandbox_ids", help="Repeatable sandbox id.")
    parser.add_argument("--all", action="store_true", help="Run all registry sandboxes.")
    parser.add_argument("--ref", help="Override candidate git ref.")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-batch-receipt", help="Write batch receipt JSON path.")
    return parser.parse_args()


def main() -> int:
    load_cloudflare_tokens()
    args = parse_args()
    registry = load_registry()
    if not args.sandbox_ids and not args.all:
        args.sandbox_ids = ["brain_worker"]

    sandbox_ids = args.sandbox_ids or [s["sandbox_id"] for s in registry["sandboxes"]]
    results = [run_one(registry, sid, ref=args.ref) for sid in sandbox_ids]

    batch = {
        "receipt_type": "PARALLEL_BRAIN_CANDIDATE_BATCH",
        "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
        "sourcea_root": str(resolve_sourcea_root(registry)),
        "verifier_base_url": registry["verifier_base_url"],
        "candidates": results,
        "pass_count": sum(1 for row in results if row.get("result") == "PASS"),
        "fail_count": sum(1 for row in results if row.get("result") != "PASS"),
    }

    if args.write_batch_receipt:
        out = Path(args.write_batch_receipt)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    default_receipt = ROOT / "receipts" / f"parallel-candidate-batch-{dt.datetime.now(dt.UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    if not args.write_batch_receipt:
        default_receipt.parent.mkdir(parents=True, exist_ok=True)
        default_receipt.write_text(json.dumps(batch, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        batch["batch_receipt_path"] = str(default_receipt)

    if args.json:
        print(json.dumps(batch, indent=2, sort_keys=True))
    else:
        print(f"parallel batch: pass={batch['pass_count']} fail={batch['fail_count']}")
        for row in results:
            print(
                f" - {row['sandbox_id']}: {row.get('result')} "
                f"receipt_id={row.get('receipt_id')} ref={row.get('candidate_ref', '')[:12]}"
            )
        print(f"batch_receipt: {default_receipt if not args.write_batch_receipt else args.write_batch_receipt}")

    return 0 if batch["fail_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
