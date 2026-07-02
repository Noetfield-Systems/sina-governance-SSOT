#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from gates.cf_tokens import load_cloudflare_tokens


REQUIRED_STATUS = "PASS"
CONFIRM_TEXT = "CONFIRM DEPLOY"
REFRESHING_BRAIN_DEPLOY_COMMAND = "bash scripts/brain_cli_v1.sh deploy"

BUNDLE_ARTIFACT_ALLOWLIST = (
    "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json",
    "data/brain-public-rules-v1.json",
    "data/chatbot-knowledge/",
)

DEPLOY_DIRTY_SCOPE_PREFIXES = (
    "cloud/workers/sourcea-brain-chat-v1/",
    "scripts/brain_cli_v1.sh",
)


def run_text(command: list[str], cwd: Path | None = None) -> str:
    result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return result.stdout.strip()


def path_allowed(path: str, allowlist: tuple[str, ...]) -> bool:
    normalized = path.strip()
    for entry in allowlist:
        if entry.endswith("/"):
            if normalized.startswith(entry):
                return True
        elif normalized == entry:
            return True
    return False


def dirty_paths_in_scope(source_root: Path, scope_prefixes: tuple[str, ...]) -> list[str]:
    status = run_text(["git", "status", "--porcelain"], cwd=source_root)
    scoped: list[str] = []
    for line in status.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path_allowed(path, scope_prefixes):
            scoped.append(path)
    return scoped


def commit_changed_paths(source_root: Path, commit_ref: str) -> list[str]:
    output = run_text(["git", "show", "--name-only", "--pretty=format:", commit_ref], cwd=source_root)
    return [line.strip() for line in output.splitlines() if line.strip()]


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
    artifact_type = receipt.get("artifact_type")

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

    if artifact_type == "brain_worker_bundle":
        for field in ("worker_code_sha256", "knowledge_bundle_sha256"):
            expected = getattr(args, f"expected_{field}", None)
            if expected and receipt.get(field) != expected:
                reasons.append(f"receipt {field} does not match expected value")

    return reasons


def bundle_scope_refusal_reasons(args: argparse.Namespace) -> list[str]:
    if not args.bundle_artifacts_only:
        return []
    if not args.deploy_source_root:
        return ["--bundle-artifacts-only requires --deploy-source-root"]

    source_root = Path(args.deploy_source_root).expanduser().resolve()
    reasons: list[str] = []
    try:
        changed = commit_changed_paths(source_root, args.expected_candidate_ref)
        disallowed = [path for path in changed if not path_allowed(path, BUNDLE_ARTIFACT_ALLOWLIST)]
        if disallowed:
            reasons.append(
                "candidate commit touches paths outside bundle-artifacts-only allowlist: "
                + ", ".join(disallowed[:8])
                + ("..." if len(disallowed) > 8 else "")
            )
    except RuntimeError as exc:
        reasons.append(str(exc))
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

        scoped_dirty = dirty_paths_in_scope(source_root, DEPLOY_DIRTY_SCOPE_PREFIXES)
        if scoped_dirty:
            reasons.append(
                "deploy-scoped working tree is dirty: " + ", ".join(scoped_dirty[:8])
            )

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

    reasons.extend(bundle_scope_refusal_reasons(args))
    return reasons


def semi_auto_window_active(args: argparse.Namespace) -> bool:
    if not args.semi_auto_window:
        return False
    if not args.semi_auto_window_until:
        return True
    try:
        until = dt.datetime.fromisoformat(args.semi_auto_window_until.replace("Z", "+00:00"))
        if until.tzinfo is None:
            until = until.replace(tzinfo=dt.UTC)
        return dt.datetime.now(dt.UTC) <= until
    except ValueError:
        return False


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


def run_brain_live_smoke(command: str | None, cwd: Path | None) -> dict[str, Any]:
    if not command:
        return {"skipped": True}
    result = subprocess.run(command, shell=True, cwd=cwd, text=True, capture_output=True, check=False)
    return {
        "command": command,
        "exit_code": result.returncode,
        "ok": result.returncode == 0,
        "stdout_tail": result.stdout.strip()[-500:],
        "stderr_tail": result.stderr.strip()[-500:],
    }


def write_deploy_receipt(
    args: argparse.Namespace,
    receipt: dict[str, Any],
    pre_version: str | None,
    post_version: str | None,
    health: dict[str, Any] | None,
    brain_live: dict[str, Any] | None,
    deploy_exit_code: int,
    *,
    semi_auto: bool = False,
    identity_ok: bool = True,
) -> None:
    if not args.deploy_receipt_path:
        return
    output_path = Path(args.deploy_receipt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    smoke_ok = brain_live is None or brain_live.get("skipped") or brain_live.get("ok") is True
    deploy_success = deploy_exit_code == 0 and identity_ok and smoke_ok
    deploy_receipt = {
        "receipt_type": "SEMI_AUTO_WINDOW_DEPLOY" if semi_auto else "STEP10A_CONFIRM_EACH_TIME_DEPLOY",
        "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
        "candidate_ref": receipt.get("candidate_ref"),
        "candidate_path": receipt.get("candidate_path"),
        "candidate_sha256": receipt.get("candidate_sha256"),
        "artifact_type": receipt.get("artifact_type"),
        "verifier_receipt_id": receipt.get("receipt_id"),
        "pre_live_version_id": pre_version,
        "post_live_version_id": post_version,
        "new_live_version_id": post_version,
        "health_result": health,
        "brain_live_smoke": brain_live,
        "content_identity_ok": identity_ok,
        "deploy_exit_code": deploy_exit_code,
        "deploy_executed": deploy_success,
        "deploy_marked_success": deploy_success,
        "founder_confirmation": "SEMI_AUTO_WINDOW" if semi_auto else CONFIRM_TEXT,
        "confirmed_by": "semi_auto_window" if semi_auto else "founder",
    }
    output_path.write_text(json.dumps(deploy_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute_deploy_flow(args: argparse.Namespace, receipt: dict[str, Any], *, semi_auto: bool) -> int:
    if not args.deploy_command:
        print("PROMOTION_GATE: REFUSED")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print("deploy_executed: false")
        print("reasons:")
        print("- deploy requires --deploy-command")
        return 2
    if args.deploy_command.strip() == REFRESHING_BRAIN_DEPLOY_COMMAND:
        print("PROMOTION_GATE: REFUSED")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print("deploy_executed: false")
        print("reasons:")
        print("- refreshing Brain deploy command is not allowed; use deploy-verified/deploy-no-refresh")
        return 2

    pre_version = latest_live_version(args.live_version_command)
    if semi_auto:
        print("PROMOTION_GATE: APPROVED_SEMI_AUTO_DEPLOY")
        print(f"semi_auto_window_until: {args.semi_auto_window_until or 'unbounded'}")
    else:
        print("PROMOTION_GATE: APPROVED_CONFIRMATION_REQUIRED")
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

    print(f"receipt_id: {receipt.get('receipt_id')}")
    print(f"candidate_ref: {receipt.get('candidate_ref')}")
    print(f"candidate_path: {receipt.get('candidate_path')}")
    print(f"candidate_sha256: {receipt.get('candidate_sha256')}")
    print(f"deploy_command: {args.deploy_command}")
    print(f"pre_live_version_id: {pre_version}")

    result = subprocess.run(
        args.deploy_command,
        shell=True,
        cwd=Path(args.deploy_source_root) if args.deploy_source_root else None,
        check=False,
    )
    post_version = latest_live_version(args.live_version_command)
    health = fetch_health(args.health_url)
    brain_live = run_brain_live_smoke(args.brain_live_smoke_command, Path(args.deploy_source_root) if args.deploy_source_root else None)

    identity_ok = True
    is_live_deploy = "deploy-verified" in args.deploy_command or "wrangler deploy" in args.deploy_command
    if (
        is_live_deploy
        and post_version
        and pre_version
        and post_version == pre_version
        and result.returncode == 0
    ):
        identity_ok = False
        print("PROMOTION_GATE: IDENTITY_MISMATCH")
        print("deploy_executed: false")
        print(f"rollback_hint: wrangler versions deploy {pre_version} --name sourcea-brain-chat-v1")
    elif health is not None and health.get("ok") is not True:
        identity_ok = False
        print("PROMOTION_GATE: HEALTH_FAIL")
        print("deploy_executed: false")
        if pre_version:
            print(f"rollback_hint: wrangler versions deploy {pre_version} --name sourcea-brain-chat-v1")
    elif brain_live.get("ok") is False:
        identity_ok = False
        print("PROMOTION_GATE: BRAIN_LIVE_SMOKE_FAIL")
        print("deploy_executed: false")
        if pre_version:
            print(f"rollback_hint: wrangler versions deploy {pre_version} --name sourcea-brain-chat-v1")

    print(f"deploy_exit_code: {result.returncode}")
    print(f"post_live_version_id: {post_version}")
    write_deploy_receipt(
        args,
        receipt,
        pre_version,
        post_version,
        health,
        brain_live,
        result.returncode,
        semi_auto=semi_auto,
        identity_ok=identity_ok,
    )

    if not identity_ok:
        return 4
    if result.returncode != 0:
        return result.returncode
    if brain_live.get("ok") is False:
        return 5
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Promote a knowledge bundle only when the verifier receipt is PASS.")
    parser.add_argument("--receipt-url", required=True, help="Verifier KV receipt endpoint, usually /receipt/latest.")
    parser.add_argument("--expected-candidate-ref", required=True)
    parser.add_argument("--expected-candidate-path", required=True)
    parser.add_argument("--expected-candidate-sha256", required=True)
    parser.add_argument("--expected-cf-account-id", required=True)
    parser.add_argument("--expected-worker-code-sha256", help="Required when artifact_type is brain_worker_bundle.")
    parser.add_argument("--expected-knowledge-bundle-sha256", help="Alias check for brain_worker_bundle receipts.")
    parser.add_argument("--deploy-command", help="Command to run only after all PASS checks succeed.")
    parser.add_argument("--execute-deploy", action="store_true", help="Disabled for Step 10a; use --confirm-each-time.")
    parser.add_argument("--confirm-each-time", action="store_true", help="Require founder confirmation before deploying.")
    parser.add_argument("--semi-auto-window", action="store_true", help="Auto-deploy on PASS inside an authorized window.")
    parser.add_argument("--semi-auto-window-until", help="ISO8601 timestamp; window closes after this instant.")
    parser.add_argument("--bundle-artifacts-only", action="store_true", help="Refuse candidates that change non-bundle paths.")
    parser.add_argument("--deploy-source-root", help="SourceA repo root; must be clean main matching origin/main.")
    parser.add_argument("--source-bundle-path", help="Candidate bundle path inside the deploy source repo.")
    parser.add_argument("--live-version-command", help="Command that returns Worker deployments JSON.")
    parser.add_argument("--health-url", help="Live Worker health endpoint to fetch after deploy.")
    parser.add_argument(
        "--brain-live-smoke-command",
        help="Shell command for production brain live smoke after deploy.",
    )
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

    wants_deploy = args.confirm_each_time or (args.semi_auto_window and semi_auto_window_active(args))

    if args.semi_auto_window and not semi_auto_window_active(args):
        print("PROMOTION_GATE: REFUSED")
        print("deploy_executed: false")
        print("reasons:")
        print("- semi-auto window is not active or has expired")
        return 2

    if wants_deploy:
        source_reasons = source_refusal_reasons(args)
        if source_reasons:
            print("PROMOTION_GATE: BLOCKED")
            print(f"receipt_id: {receipt.get('receipt_id')}")
            print("deploy_executed: false")
            print("reasons:")
            for reason in source_reasons:
                print(f"- {reason}")
            return 2
        return execute_deploy_flow(args, receipt, semi_auto=args.semi_auto_window and semi_auto_window_active(args))

    if args.execute_deploy:
        print("PROMOTION_GATE: REFUSED")
        print("deploy_executed: false")
        print("reasons:")
        print("- unattended --execute-deploy is disabled; use --confirm-each-time or --semi-auto-window")
        return 2

    print("PROMOTION_GATE: APPROVED_DRY_RUN")
    print(f"receipt_id: {receipt.get('receipt_id')}")
    print("deploy_executed: false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
