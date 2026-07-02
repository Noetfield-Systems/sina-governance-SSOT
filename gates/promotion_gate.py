#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
import os


REQUIRED_STATUS = "PASS"
CONFIRM_TEXT = "CONFIRM DEPLOY"
REFRESHING_BRAIN_DEPLOY_COMMAND = "bash scripts/brain_cli_v1.sh deploy"
CF_TOKENS_FILE = Path.home() / ".sina/secrets/cloudflare-tokens.env"
CF_TOKEN_KEYS = ("CF_MAIN_TOKEN", "CF_VERIFIER_TOKEN", "CLOUDFLARE_API_TOKEN")


def load_cloudflare_tokens() -> None:
    """Load CF tokens from ~/.sina/secrets when not already in the environment."""
    if all(os.environ.get(key) for key in ("CF_MAIN_TOKEN", "CF_VERIFIER_TOKEN")):
        return
    if not CF_TOKENS_FILE.is_file():
        return
    for raw_line in CF_TOKENS_FILE.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in CF_TOKEN_KEYS and not os.environ.get(key):
            os.environ[key] = value


def run_text(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return result.stdout.strip()


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


def source_refusal_reasons(args: argparse.Namespace) -> list[str]:
    if not args.deploy_source_root or not args.source_bundle_path:
        return ["--confirm-each-time requires --deploy-source-root and --source-bundle-path"]

    source_root = Path(args.deploy_source_root).expanduser().resolve()
    source_bundle = source_root / args.source_bundle_path
    reasons: list[str] = []

    if not source_root.exists():
        return [f"deploy source root does not exist: {source_root}"]
    if not source_bundle.exists():
        reasons.append(f"source bundle does not exist: {args.source_bundle_path}")

    try:
        branch = run_text(["git", "branch", "--show-current"], cwd=source_root)
        if branch != "main":
            reasons.append(f"deploy source branch is {branch!r}, not 'main'")

        head = run_text(["git", "rev-parse", "HEAD"], cwd=source_root)
        origin_main = run_text(["git", "rev-parse", "origin/main"], cwd=source_root)
        if head != origin_main:
            reasons.append("deploy source HEAD does not match origin/main")
        if not head.startswith(args.expected_candidate_ref):
            reasons.append("deploy source HEAD does not match expected candidate ref")

        status = run_text(["git", "status", "--porcelain"], cwd=source_root)
        if status:
            reasons.append("deploy source working tree is not clean")

        committed_bytes = subprocess.check_output(
            ["git", "show", f"HEAD:{args.source_bundle_path}"],
            cwd=source_root,
        )
        committed_sha = hashlib.sha256(committed_bytes).hexdigest()
        if committed_sha != args.expected_candidate_sha256:
            reasons.append("committed source bundle sha256 does not match expected candidate sha256")

        if source_bundle.exists():
            worktree_sha = hashlib.sha256(source_bundle.read_bytes()).hexdigest()
            if worktree_sha != committed_sha:
                reasons.append("worktree source bundle sha256 does not match committed source bundle")
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        reasons.append(str(exc))

    return reasons


def latest_live_version(version_command: str | None) -> str | None:
    if not version_command:
        return None
    result = subprocess.run(version_command, shell=True, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    data = json.loads(result.stdout)
    if not isinstance(data, list) or not data:
        return None
    versions = data[-1].get("versions", [])
    for version in versions:
        if version.get("percentage") == 100:
            return version.get("version_id")
    return versions[-1].get("version_id") if versions else None


def fetch_health(health_url: str | None) -> dict[str, Any] | None:
    if not health_url:
        return None
    request = urllib.request.Request(
        health_url,
        headers={
            "Accept": "application/json",
            "User-Agent": "sina-governance-promotion-gate",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def write_deploy_receipt(
    args: argparse.Namespace,
    receipt: dict[str, Any],
    pre_version: str | None,
    post_version: str | None,
    health: dict[str, Any] | None,
    deploy_exit_code: int,
) -> None:
    if not args.deploy_receipt_path:
        return
    output_path = Path(args.deploy_receipt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    deploy_receipt = {
        "receipt_type": "STEP10A_CONFIRM_EACH_TIME_DEPLOY",
        "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
        "candidate_ref": receipt.get("candidate_ref"),
        "candidate_path": receipt.get("candidate_path"),
        "candidate_sha256": receipt.get("candidate_sha256"),
        "verifier_receipt_id": receipt.get("receipt_id"),
        "pre_live_version_id": pre_version,
        "post_live_version_id": post_version,
        "new_live_version_id": post_version,
        "health_result": health,
        "deploy_exit_code": deploy_exit_code,
        "deploy_executed": deploy_exit_code == 0,
        "founder_confirmation": CONFIRM_TEXT,
        "confirmed_by": "founder",
    }
    output_path.write_text(json.dumps(deploy_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a knowledge bundle only when the verifier receipt is PASS.")
    parser.add_argument("--receipt-url", required=True, help="Verifier KV receipt endpoint, usually /receipt/latest.")
    parser.add_argument("--expected-candidate-ref", required=True)
    parser.add_argument("--expected-candidate-path", required=True)
    parser.add_argument("--expected-candidate-sha256", required=True)
    parser.add_argument("--expected-cf-account-id", required=True)
    parser.add_argument("--deploy-command", help="Command to run only after all PASS checks succeed.")
    parser.add_argument("--execute-deploy", action="store_true", help="Disabled for Step 10a; use --confirm-each-time.")
    parser.add_argument("--confirm-each-time", action="store_true", help="Require a receipt-specific founder confirmation before deploying.")
    parser.add_argument("--deploy-source-root", help="SourceA repo root; must be clean main matching origin/main.")
    parser.add_argument("--source-bundle-path", help="Candidate bundle path inside the deploy source repo.")
    parser.add_argument("--live-version-command", help="Command that returns Worker deployments JSON.")
    parser.add_argument("--health-url", help="Live Worker health endpoint to fetch after deploy.")
    parser.add_argument("--deploy-receipt-path", help="Path to write the confirmed deploy receipt JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_cloudflare_tokens()
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

    if args.confirm_each_time:
        source_reasons = source_refusal_reasons(args)
        if source_reasons:
            print("PROMOTION_GATE: BLOCKED")
            print(f"receipt_id: {receipt.get('receipt_id')}")
            print("deploy_executed: false")
            print("reasons:")
            for reason in source_reasons:
                print(f"- {reason}")
            return 2
        if not args.deploy_command:
            print("PROMOTION_GATE: REFUSED")
            print(f"receipt_id: {receipt.get('receipt_id')}")
            print("deploy_executed: false")
            print("reasons:")
            print("- --confirm-each-time requires --deploy-command after founder confirmation")
            return 2
        if args.deploy_command.strip() == REFRESHING_BRAIN_DEPLOY_COMMAND:
            print("PROMOTION_GATE: REFUSED")
            print(f"receipt_id: {receipt.get('receipt_id')}")
            print("deploy_executed: false")
            print("reasons:")
            print("- refreshing Brain deploy command is not allowed; use deploy-verified/deploy-no-refresh")
            return 2

        pre_version = latest_live_version(args.live_version_command)
        print("PROMOTION_GATE: APPROVED_CONFIRMATION_REQUIRED")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print(f"candidate_ref: {receipt.get('candidate_ref')}")
        print(f"candidate_path: {receipt.get('candidate_path')}")
        print(f"candidate_sha256: {receipt.get('candidate_sha256')}")
        print(f"deploy_command: {args.deploy_command}")
        print(f"pre_live_version_id: {pre_version}")
        print(f'type "{CONFIRM_TEXT}" to deploy:')
        try:
            confirmation = input()
        except EOFError:
            confirmation = ""
        if confirmation != CONFIRM_TEXT:
            print("PROMOTION_GATE: CONFIRMATION_NOT_GIVEN")
            print("deploy_executed: false")
            return 3

        print("PROMOTION_GATE: APPROVED_CONFIRMED_DEPLOY")
        print("founder_confirmation: true")
        result = subprocess.run(args.deploy_command, shell=True, cwd=Path(args.deploy_source_root), check=False)
        post_version = latest_live_version(args.live_version_command)
        health = fetch_health(args.health_url)
        print(f"deploy_exit_code: {result.returncode}")
        print(f"post_live_version_id: {post_version}")
        write_deploy_receipt(args, receipt, pre_version, post_version, health, result.returncode)
        return result.returncode

    if args.execute_deploy:
        print("PROMOTION_GATE: REFUSED")
        print("deploy_executed: false")
        print("reasons:")
        print("- unattended --execute-deploy is disabled; use --confirm-each-time")
        return 2

    if not args.execute_deploy:
        print("PROMOTION_GATE: APPROVED_DRY_RUN")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print("deploy_executed: false")
        return 0


if __name__ == "__main__":
    sys.exit(main())
