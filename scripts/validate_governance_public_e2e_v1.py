#!/usr/bin/env python3
"""Governance public E2E — verifier + gate dry-run + SourceA public proof chain."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCEA_ROOT = Path(os.environ.get("SOURCEA_ROOT", Path.home() / "Desktop/SourceA")).expanduser()
VERIFIER_RECEIPT_URL = os.environ.get(
    "VERIFIER_RECEIPT_URL",
    "https://sina-governance-ssot-advisory.kazemnezhadsina144.workers.dev/receipt/latest",
)
SECONDARY_CF_ACCOUNT = os.environ.get("SECONDARY_CF_ACCOUNT", "b7282b4a5c17b84d62e3ef8866b878f8")
BUNDLE_PATH = "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"


def run(label: str, cmd: list[str], *, cwd: Path | None = None) -> bool:
    print(f"=== {label} ===")
    proc = subprocess.run(cmd, cwd=cwd, check=False)
    if proc.returncode == 0:
        print(f"OK: {label}\n")
        return True
    print(f"FAIL: {label}\n")
    return False


def git_show_bytes(repo: Path, ref_path: str) -> bytes:
    return subprocess.check_output(["git", "show", ref_path], cwd=repo)


def main() -> int:
    errors = 0
    print("=== validate-governance-public-e2e-v1 start ===\n")

    if not SOURCEA_ROOT.is_dir():
        print(f"FAIL: SourceA root missing: {SOURCEA_ROOT}")
        return 1

    candidate_ref = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=SOURCEA_ROOT, text=True).strip()
    candidate_short = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=SOURCEA_ROOT, text=True).strip()
    bundle_sha = hashlib.sha256(git_show_bytes(SOURCEA_ROOT, f"HEAD:{BUNDLE_PATH}")).hexdigest()
    print("=== resolve SourceA candidate ===")
    print(f"OK: candidate_ref={candidate_short} bundle_sha256={bundle_sha[:16]}...\n")

    request = urllib.request.Request(
        VERIFIER_RECEIPT_URL,
        headers={"Accept": "application/json", "User-Agent": "validate-governance-public-e2e-v1"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        receipt = json.loads(response.read().decode("utf-8"))

    print("=== verifier receipt ===")
    checks = {
        "status": "PASS",
        "pass_claimed": True,
        "secondary_account_proven": True,
        "candidate_sha256": bundle_sha,
    }
    bad = [f"{k}: expected {v!r} got {receipt.get(k)!r}" for k, v in checks.items() if receipt.get(k) != v]
    if bad:
        print("FAIL: verifier receipt mismatch")
        for row in bad:
            print(" -", row)
        errors += 1
    else:
        print(f"OK: verifier receipt {receipt.get('receipt_id')} {receipt.get('artifact_type')}\n")

    gate_ref = str(receipt.get("candidate_ref") or candidate_short)
    if receipt.get("candidate_sha256") != bundle_sha:
        gate_ref = candidate_short

    gate_cmd = [
        sys.executable,
        str(ROOT / "gates/promotion_gate.py"),
        "--receipt-url",
        VERIFIER_RECEIPT_URL,
        "--expected-candidate-ref",
        gate_ref,
        "--expected-candidate-path",
        BUNDLE_PATH,
        "--expected-candidate-sha256",
        bundle_sha,
        "--expected-cf-account-id",
        SECONDARY_CF_ACCOUNT,
    ]
    worker_sha = receipt.get("worker_code_sha256")
    if worker_sha:
        gate_cmd.extend(["--expected-worker-code-sha256", worker_sha])

    if not run("promotion gate dry-run", gate_cmd, cwd=ROOT):
        errors += 1

    public_proof = SOURCEA_ROOT / "scripts/validate-sourcea-public-proof-e2e-v1.sh"
    if public_proof.is_file():
        if not run("SourceA public proof chain", ["bash", str(public_proof)], cwd=SOURCEA_ROOT):
            errors += 1
    else:
        print(f"FAIL: missing {public_proof}\n")
        errors += 1

    if errors:
        print(f"validate-governance-public-e2e-v1: FAIL errors={errors}")
        return 1
    print("validate-governance-public-e2e-v1: ALL PASS")
    return 0


if __name__ == "__main__":
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    from gates.cf_tokens import load_cloudflare_tokens

    load_cloudflare_tokens()
    raise SystemExit(main())
