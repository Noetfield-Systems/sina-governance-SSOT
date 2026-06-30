#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Any


REQUIRED_STATUS = "PASS"


def load_receipt(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "sina-governance-promotion-gate",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"receipt fetch failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"receipt fetch failed: {exc.reason}") from exc


def refusal_reasons(receipt: dict[str, Any], args: argparse.Namespace) -> list[str]:
    reasons: list[str] = []

    if receipt.get("status") != REQUIRED_STATUS:
        reasons.append(f"receipt status is {receipt.get('status')!r}, not {REQUIRED_STATUS!r}")
    if receipt.get("result") != REQUIRED_STATUS:
        reasons.append(f"receipt result is {receipt.get('result')!r}, not {REQUIRED_STATUS!r}")
    if receipt.get("pass_claimed") is not True:
        reasons.append("receipt pass_claimed is not true")
    if receipt.get("edge_execution_proven") is not True:
        reasons.append("edge execution is not proven")
    if receipt.get("secondary_account_proven") is not True:
        reasons.append("secondary account is not proven")
    if receipt.get("cf_account_id") != args.expected_cf_account_id:
        reasons.append("receipt cf_account_id does not match expected secondary account")
    if receipt.get("candidate_ref") != args.expected_candidate_ref:
        reasons.append("receipt candidate_ref does not match expected candidate ref")
    if receipt.get("candidate_path") != args.expected_candidate_path:
        reasons.append("receipt candidate_path does not match expected candidate path")
    if receipt.get("candidate_sha256") != args.expected_candidate_sha256:
        reasons.append("receipt candidate_sha256 does not match expected candidate sha256")
    if receipt.get("candidate_validation_failures"):
        reasons.append("receipt has candidate_validation_failures")
    if receipt.get("failures"):
        reasons.append("receipt has failures")

    return reasons


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a knowledge bundle only when the verifier receipt is PASS.")
    parser.add_argument("--receipt-url", required=True, help="Verifier KV receipt endpoint, usually /receipt/latest.")
    parser.add_argument("--expected-candidate-ref", required=True)
    parser.add_argument("--expected-candidate-path", required=True)
    parser.add_argument("--expected-candidate-sha256", required=True)
    parser.add_argument("--expected-cf-account-id", required=True)
    parser.add_argument("--deploy-command", help="Command to run only after all PASS checks succeed.")
    parser.add_argument("--execute-deploy", action="store_true", help="Actually run --deploy-command after PASS checks.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    receipt = load_receipt(args.receipt_url)
    reasons = refusal_reasons(receipt, args)

    if reasons:
        print("PROMOTION_GATE: REFUSED")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print(f"status: {receipt.get('status')}")
        print("deploy_executed: false")
        print("reasons:")
        for reason in reasons:
            print(f"- {reason}")
        return 2

    if not args.execute_deploy:
        print("PROMOTION_GATE: APPROVED_DRY_RUN")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print("deploy_executed: false")
        return 0

    if not args.deploy_command:
        print("PROMOTION_GATE: REFUSED")
        print("reasons:")
        print("- --execute-deploy requires --deploy-command")
        return 2

    result = subprocess.run(args.deploy_command, shell=True, check=False)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
