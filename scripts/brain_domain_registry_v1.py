#!/usr/bin/env python3
"""Load and resolve brain domain sandbox registry (SSOT)."""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "data/brain_domain_sandboxes_v1.json"

BRAIN_WORKER_CODE_PATHS = (
    "cloud/workers/sourcea-brain-chat-v1/src/index.js",
    "cloud/workers/sourcea-brain-chat-v1/src/guardrails.js",
    "cloud/workers/sourcea-brain-chat-v1/src/brain-core-gate-v1.js",
)
BUNDLE_PATH = "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"


def load_registry(path: Path | None = None) -> dict[str, Any]:
    registry_path = path or REGISTRY_PATH
    return json.loads(registry_path.read_text(encoding="utf-8"))


def expand_root(value: str) -> Path:
    return Path(os.path.expanduser(value)).resolve()


def resolve_sourcea_root(registry: dict[str, Any] | None = None) -> Path:
    reg = registry or load_registry()
    env_root = os.environ.get("SOURCEA_ROOT")
    if env_root:
        return expand_root(env_root)

    candidates = [
        reg.get("sourcea_root_default", "~/Projects/SourceA"),
        reg.get("sourcea_root_desktop", "~/Desktop/SourceA"),
    ]
    for candidate in candidates:
        resolved = expand_root(str(candidate))
        if resolved.exists():
            return resolved
    return expand_root(str(candidates[0]))


def resolve_sandbox_repo(registry: dict[str, Any], sandbox: dict[str, Any]) -> Path:
    """Repo for verifier/heal — always SOURCEA_ROOT env, never stale Desktop path."""
    _ = sandbox
    return resolve_sourcea_root(registry)


def workflow_health_targets(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    reg = registry or load_registry()
    defaults = {
        "freshness_target_minutes": 360,
        "success_rate_target": 99,
        "latency_target_minutes": 15,
        "heartbeat_max_age_minutes": 360,
        "min_health_score": 85,
        "kaizen_proof_prefix": "receipts/improvement-receipt-v2-",
    }
    targets = reg.get("workflow_health_targets", {}).get("brain_loop", {})
    if not isinstance(targets, dict):
        return defaults
    return {**defaults, **targets}


def get_sandbox(registry: dict[str, Any], sandbox_id: str) -> dict[str, Any]:
    for sandbox in registry.get("sandboxes", []):
        if sandbox.get("sandbox_id") == sandbox_id:
            return sandbox
    raise KeyError(f"sandbox_id not found: {sandbox_id}")


def git_ref(repo: Path, ref: str = "HEAD") -> str:
    return subprocess.check_output(["git", "rev-parse", ref], cwd=repo, text=True).strip()


def git_show_bytes(repo: Path, ref_path: str) -> bytes:
    return subprocess.check_output(["git", "show", ref_path], cwd=repo)


def sha256_bytes(data: bytes) -> str:
    import hashlib

    return hashlib.sha256(data).hexdigest()


def branch_exists(repo: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "show-ref", "--verify", f"refs/heads/{branch}"],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    if result.returncode == 0:
        return True
    result = subprocess.run(
        ["git", "show-ref", "--verify", f"refs/remotes/origin/{branch}"],
        cwd=repo,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def worker_code_sha256(repo: Path, ref: str) -> str:
    import hashlib

    path_hashes: dict[str, str] = {}
    for path in BRAIN_WORKER_CODE_PATHS:
        path_hashes[path] = sha256_bytes(git_show_bytes(repo, f"{ref}:{path}"))
    sorted_keys = sorted(path_hashes)
    payload = json.dumps({k: path_hashes[k] for k in sorted_keys}, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def proposed_brain_worker_sha256(repo: Path, ref: str) -> str:
    import hashlib

    path_hashes: dict[str, str] = {}
    for path in [*BRAIN_WORKER_CODE_PATHS, BUNDLE_PATH]:
        path_hashes[path] = sha256_bytes(git_show_bytes(repo, f"{ref}:{path}"))
    sorted_keys = sorted(path_hashes)
    payload = json.dumps({k: path_hashes[k] for k in sorted_keys}, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def bundle_sha256(repo: Path, ref: str, bundle_path: str = BUNDLE_PATH) -> str:
    return sha256_bytes(git_show_bytes(repo, f"{ref}:{bundle_path}"))


def build_artifact_descriptor(
    sandbox: dict[str, Any],
    repo: Path,
    *,
    ref: str | None = None,
    base_sha256: str = "0" * 64,
) -> dict[str, Any]:
    branch = sandbox.get("branch", "main")
    candidate_ref = ref or git_ref(repo, branch if branch_exists(repo, branch) else "HEAD")
    artifact_type = sandbox["artifact_type"]
    bundle_path = sandbox.get("candidate_path", BUNDLE_PATH)
    if artifact_type == "knowledge_bundle" and bundle_path.endswith("locked-definitions-v1.json"):
        bundle_path = BUNDLE_PATH

    descriptor: dict[str, Any] = {
        "artifact_type": artifact_type,
        "artifact_path": bundle_path if artifact_type == "knowledge_bundle" else BUNDLE_PATH,
        "author_id": "sandbox",
        "subject": "live Worker",
        "schema_valid": True,
        "validator_runtime": "cloudflare_worker_secondary_account",
        "candidate_repo": sandbox["candidate_repo"],
        "candidate_ref": candidate_ref,
    }

    if artifact_type == "knowledge_bundle":
        bundle_sha = bundle_sha256(repo, candidate_ref, BUNDLE_PATH)
        descriptor["proposed_sha256"] = bundle_sha
        descriptor["base_sha256"] = base_sha256
    else:
        bundle_sha = bundle_sha256(repo, candidate_ref)
        worker_sha = worker_code_sha256(repo, candidate_ref)
        proposed = proposed_brain_worker_sha256(repo, candidate_ref)
        descriptor["proposed_sha256"] = proposed
        descriptor["base_sha256"] = base_sha256
        descriptor["worker_code_sha256"] = worker_sha
        descriptor["knowledge_bundle_sha256"] = bundle_sha

    return descriptor


def build_verifier_post_body(sandbox: dict[str, Any], repo: Path, *, ref: str | None = None) -> dict[str, Any]:
    descriptor = build_artifact_descriptor(sandbox, repo, ref=ref)
    return {
        "candidate_repo": sandbox["candidate_repo"],
        "candidate_ref": descriptor["candidate_ref"],
        "candidate_path": descriptor["artifact_path"],
        "artifact_descriptor": descriptor,
    }
