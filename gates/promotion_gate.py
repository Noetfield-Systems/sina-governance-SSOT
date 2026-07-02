#!/usr/bin/env python3
from __future__ import annotations

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
from scripts.brain_autonomous_controls_v1 import (
    autonomous_deploy_enabled,
    autonomous_hold_active,
    mutation_trials_enabled,
    set_autonomous_hold,
)

REGISTRY_PATH = _REPO_ROOT / "data/brain_domain_sandboxes_v1.json"
INDEPENDENCE_RECEIPT_DEFAULT = _REPO_ROOT / "receipts/verifier-independence-proof-latest.json"


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


def load_sandbox_registry() -> dict[str, Any]:
    if not REGISTRY_PATH.is_file():
        raise RuntimeError(f"sandbox registry missing: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def get_sandbox_profile(registry: dict[str, Any], sandbox_id: str) -> dict[str, Any]:
    for sandbox in registry.get("sandboxes", []):
        if sandbox.get("sandbox_id") == sandbox_id:
            return sandbox
    raise RuntimeError(f"sandbox_id not found in registry: {sandbox_id}")


def apply_sandbox_profile(args: argparse.Namespace) -> None:
    if not args.sandbox_id:
        return
    registry = load_sandbox_registry()
    sandbox = get_sandbox_profile(registry, args.sandbox_id)
    profile = sandbox.get("gate_profile") or {}
    deploy_root = str(Path(sandbox["deploy_root"]).expanduser())

    env_root = os.environ.get("SOURCEA_ROOT")
    if not args.deploy_source_root:
        args.deploy_source_root = env_root if env_root else deploy_root
    if not args.health_url:
        args.health_url = sandbox.get("health_url")
    if profile.get("bundle_artifacts_only"):
        args.bundle_artifacts_only = True
    if profile.get("deploy_command") and not args.deploy_command:
        args.deploy_command = profile["deploy_command"]
    if profile.get("source_bundle_path") and not args.source_bundle_path:
        args.source_bundle_path = profile["source_bundle_path"]
    if profile.get("post_promote_command") and not args.post_promote_command:
        args.post_promote_command = profile["post_promote_command"]
    if profile.get("brain_live_smoke_default") and not args.brain_live_smoke_command:
        smoke_script = Path(deploy_root) / "scripts/validate-sourcea-brain-live-v1.sh"
        if smoke_script.is_file():
            args.brain_live_smoke_command = "bash scripts/validate-sourcea-brain-live-v1.sh"

    if os.environ.get("BRAIN_SANDBOX_SEMI_AUTO") == args.sandbox_id:
        args.semi_auto_window = True


def load_json_file(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def independence_refusal_reasons(args: argparse.Namespace) -> list[str]:
    if args.skip_independence_check:
        return []
    path = Path(args.independence_receipt_path or INDEPENDENCE_RECEIPT_DEFAULT)
    if not path.is_file():
        return [f"independence receipt missing: {path}"]
    proof = load_json_file(path)
    if proof.get("result") != "PASS" and proof.get("status") != "PASS":
        return ["independence receipt is not PASS"]
    if not proof.get("secondary_account_proven"):
        return ["independence receipt missing secondary_account_proven"]
    recorded_at = proof.get("recorded_at") or proof.get("checked_at")
    if not recorded_at:
        return ["independence receipt missing recorded_at"]
    try:
        stamp = dt.datetime.fromisoformat(str(recorded_at).replace("Z", "+00:00"))
        if stamp.tzinfo is None:
            stamp = stamp.replace(tzinfo=dt.timezone.utc)
    except ValueError:
        return ["independence receipt recorded_at is not ISO8601"]
    age_days = (dt.datetime.now(dt.timezone.utc) - stamp).days
    if age_days > args.independence_max_age_days:
        return [f"independence receipt stale ({age_days}d > {args.independence_max_age_days}d)"]
    return []


def autonomous_refusal_reasons(args: argparse.Namespace) -> list[str]:
    if not args.autonomous_deploy:
        return []
    if autonomous_hold_active():
        return ["autonomous hold flag is active (~/.sina/enforcement/brain-autonomous-hold-v1.flag)"]
    if not autonomous_deploy_enabled():
        return ["brain-autonomous-deploy-v1.flag not present (~/.sina/brain-autonomous-deploy-v1.flag)"]
    source_root = Path(args.deploy_source_root).expanduser() if args.deploy_source_root else None
    if mutation_trials_enabled(source_root):
        return ["SOURCEA_PHASE2_MUTATION_TRIALS is enabled"]
    return []


def rollback_receipt_reasons(args: argparse.Namespace) -> list[str]:
    if not args.rollback_receipt:
        return []
    path = Path(args.rollback_receipt)
    if not path.is_file():
        return [f"rollback receipt missing: {path}"]
    proof = load_json_file(path)
    if proof.get("drill_result") != "PASS" and proof.get("result") != "PASS":
        return ["rollback receipt drill_result is not PASS"]
    if not proof.get("live_health_restored"):
        return ["rollback receipt missing live_health_restored=true"]
    return []


def run_post_promote_command(args: argparse.Namespace) -> dict[str, Any]:
    if not args.post_promote_command:
        return {"skipped": True}
    cwd = Path(args.deploy_source_root).expanduser() if args.deploy_source_root else None
    result = subprocess.run(args.post_promote_command, shell=True, cwd=cwd, text=True, capture_output=True, check=False)
    return {
        "command": args.post_promote_command,
        "exit_code": result.returncode,
        "ok": result.returncode == 0,
        "stdout_tail": result.stdout.strip()[-500:],
        "stderr_tail": result.stderr.strip()[-500:],
    }


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
    if not str(receipt.get("candidate_ref") or "").startswith(args.expected_candidate_ref) and not str(
        args.expected_candidate_ref
    ).startswith(str(receipt.get("candidate_ref") or "")):
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
        head = run_text(["git", "rev-parse", "HEAD"], cwd=source_root)
        origin_main = run_text(["git", "rev-parse", "origin/main"], cwd=source_root)
        if branch != "main":
            if not (branch == "" and head == origin_main):
                reasons.append(f"deploy source branch is {branch!r}, not 'main'")
        if head != origin_main:
            reasons.append("deploy source HEAD does not match origin/main")
        try:
            subprocess.run(
                ["git", "merge-base", "--is-ancestor", args.expected_candidate_ref, "HEAD"],
                cwd=source_root,
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError:
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

    if args.sandbox_id == "brain_worker":
        guard = source_root / "scripts/deploy_dirty_tree_guard_v1.py"
        if guard.is_file():
            result = subprocess.run(
                [sys.executable, str(guard), "--scope", "brain_worker", "--json"],
                cwd=source_root,
                text=True,
                capture_output=True,
                check=False,
            )
            if result.returncode != 0:
                try:
                    payload = json.loads(result.stdout)
                except json.JSONDecodeError:
                    payload = {"stderr": result.stderr.strip(), "stdout": result.stdout.strip()}
                dirty_scoped = payload.get("dirty_scoped") or []
                dirty_total = payload.get("dirty_total")
                dirty_cap = payload.get("dirty_total_cap")
                if dirty_scoped:
                    reasons.append(
                        "brain_worker deploy scope is dirty: "
                        + ", ".join(str(path) for path in dirty_scoped[:8])
                    )
                elif dirty_total is not None and dirty_cap is not None:
                    reasons.append(f"deploy dirty-tree cap exceeded: dirty_total={dirty_total} cap={dirty_cap}")
                else:
                    reasons.append("brain_worker deploy dirty-tree guard failed")

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
            until = until.replace(tzinfo=dt.timezone.utc)
        return dt.datetime.now(dt.timezone.utc) <= until
    except ValueError:
        return False


def latest_live_version(version_command: str | None, cwd: Path | None = None) -> str | None:
    if not version_command:
        return None
    result = subprocess.run(
        version_command,
        shell=True,
        text=True,
        capture_output=True,
        check=False,
        cwd=cwd,
    )
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
    post_promote: dict[str, Any] | None,
    deploy_exit_code: int,
    *,
    semi_auto: bool = False,
    autonomous: bool = False,
    identity_ok: bool = True,
) -> None:
    if not args.deploy_receipt_path:
        return
    output_path = Path(args.deploy_receipt_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    smoke_ok = brain_live is None or brain_live.get("skipped") or brain_live.get("ok") is True
    post_promote_ok = post_promote is None or post_promote.get("skipped") or post_promote.get("ok") is True
    deploy_success = deploy_exit_code == 0 and identity_ok and smoke_ok and post_promote_ok
    if autonomous:
        receipt_type = "AUTONOMOUS_DEPLOY"
        founder_confirmation = "AUTONOMOUS_FLAG"
        confirmed_by = "autonomous"
    elif semi_auto:
        receipt_type = "SEMI_AUTO_WINDOW_DEPLOY"
        founder_confirmation = "SEMI_AUTO_WINDOW"
        confirmed_by = "semi_auto_window"
    else:
        receipt_type = "STEP10A_CONFIRM_EACH_TIME_DEPLOY"
        founder_confirmation = CONFIRM_TEXT
        confirmed_by = "founder"
    deploy_receipt = {
        "receipt_type": receipt_type,
        "recorded_at": dt.datetime.now(dt.timezone.utc).isoformat(),
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
        "post_promote": post_promote,
        "sandbox_id": args.sandbox_id,
        "content_identity_ok": identity_ok,
        "deploy_exit_code": deploy_exit_code,
        "deploy_executed": deploy_success,
        "deploy_marked_success": deploy_success,
        "founder_confirmation": founder_confirmation,
        "confirmed_by": confirmed_by,
        "autonomous_deploy": autonomous,
    }
    output_path.write_text(json.dumps(deploy_receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def execute_deploy_flow(
    args: argparse.Namespace,
    receipt: dict[str, Any],
    *,
    semi_auto: bool = False,
    autonomous: bool = False,
) -> int:
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

    source_cwd = Path(args.deploy_source_root).expanduser() if args.deploy_source_root else None
    pre_version = latest_live_version(args.live_version_command, cwd=source_cwd)
    if autonomous:
        print("PROMOTION_GATE: APPROVED_AUTONOMOUS_DEPLOY")
        print("founder_confirmation: not required (autonomous flag active)")
    elif semi_auto:
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
    post_version = latest_live_version(args.live_version_command, cwd=source_cwd)
    deploy_rc = result.returncode
    if (
        deploy_rc in (137, 139)
        and post_version
        and pre_version
        and post_version != pre_version
    ):
        print("PROMOTION_GATE: MAC_DEPLOY_SIGKILL_RECOVERED")
        print(f"deploy_exit_code_was: {deploy_rc}")
        result.returncode = 0
        deploy_rc = 0
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

    post_promote: dict[str, Any] = {"skipped": True}
    if identity_ok and result.returncode == 0:
        post_promote = run_post_promote_command(args)
        if post_promote.get("ok") is False:
            identity_ok = False
            print("PROMOTION_GATE: POST_PROMOTE_FAIL")
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
        post_promote,
        result.returncode,
        semi_auto=semi_auto,
        autonomous=autonomous,
        identity_ok=identity_ok,
    )

    deploy_failed = (
        not identity_ok
        or result.returncode != 0
        or brain_live.get("ok") is False
        or post_promote.get("ok") is False
    )
    if deploy_failed and autonomous:
        set_autonomous_hold(
            reason=(
                f"autonomous deploy failed exit={result.returncode} "
                f"identity_ok={identity_ok} smoke_ok={brain_live.get('ok')} "
                f"post_promote_ok={post_promote.get('ok')}"
            )
        )
        print("PROMOTION_GATE: AUTONOMOUS_HOLD_SET")

    if not identity_ok:
        return 4
    if result.returncode != 0:
        return result.returncode
    if brain_live.get("ok") is False:
        return 5
    if post_promote.get("ok") is False:
        return 6
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
    parser.add_argument(
        "--autonomous-deploy",
        action="store_true",
        help="Deploy without confirmation when ~/.sina/brain-autonomous-deploy-v1.flag exists.",
    )
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
    parser.add_argument("--sandbox-id", help="Load gate profile from brain_domain_sandboxes_v1.json.")
    parser.add_argument("--post-promote-command", help="Shell command after successful deploy.")
    parser.add_argument("--rollback-receipt", help="Path to a PASS rollback drill receipt (optional gate prerequisite).")
    parser.add_argument("--independence-receipt-path", help="Verifier independence proof receipt JSON.")
    parser.add_argument("--independence-max-age-days", type=int, default=30)
    parser.add_argument("--skip-independence-check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    apply_sandbox_profile(args)
    if (
        not args.brain_live_smoke_command
        and args.health_url
        and args.deploy_source_root
    ):
        smoke_script = Path(args.deploy_source_root).expanduser() / "scripts/validate-sourcea-brain-live-v1.sh"
        if smoke_script.is_file():
            args.brain_live_smoke_command = "bash scripts/validate-sourcea-brain-live-v1.sh"
    load_cloudflare_tokens()
    receipt = load_receipt(args.receipt_url)
    reasons = refusal_reasons(receipt, args)

    wants_deploy = (
        args.confirm_each_time
        or (args.semi_auto_window and semi_auto_window_active(args))
        or args.autonomous_deploy
    )
    if wants_deploy:
        reasons.extend(independence_refusal_reasons(args))
        reasons.extend(rollback_receipt_reasons(args))
        if args.autonomous_deploy:
            reasons.extend(autonomous_refusal_reasons(args))

    if reasons:
        print("PROMOTION_GATE: REFUSED")
        print(f"receipt_id: {receipt.get('receipt_id')}")
        print(f"status: {receipt.get('status')}")
        print("deploy_executed: false")
        print("reasons:")
        for reason in reasons:
            print(f"- {reason}")
        return 2

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
        return execute_deploy_flow(
            args,
            receipt,
            semi_auto=args.semi_auto_window and semi_auto_window_active(args),
            autonomous=args.autonomous_deploy,
        )

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
