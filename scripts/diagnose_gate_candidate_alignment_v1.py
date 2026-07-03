#!/usr/bin/env python3
"""Compare local SourceA candidate bytes vs latest verifier receipt — no gate weakening."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"
BUNDLE_PATH = "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"


def bundle_sha256(repo: Path) -> tuple[str, str]:
    data = subprocess.check_output(["git", "show", f"HEAD:{BUNDLE_PATH}"], cwd=repo)
    return hashlib.sha256(data).hexdigest(), subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=repo, text=True
    ).strip()


def latest_parallel_batch() -> dict | None:
    batches = sorted(RECEIPTS.glob("parallel-candidate-batch-*.json"), reverse=True)
    if not batches:
        return None
    return json.loads(batches[0].read_text(encoding="utf-8"))


def main() -> int:
    sourcea = Path(os.environ.get("SOURCEA_ROOT", Path.home() / "Projects" / "SourceA")).expanduser()
    errors: list[str] = []

    try:
        local_bundle_sha, local_head = bundle_sha256(sourcea)
    except subprocess.CalledProcessError as exc:
        print("diagnose_gate_candidate_alignment_v1: FAIL")
        print(f" - cannot read bundle at {sourcea}: {exc}")
        return 1

    batch = latest_parallel_batch()
    receipt_sha = None
    receipt_status = "missing"
    receipt_id = None
    blockers: list[str] = []

    if batch:
        for cand in batch.get("candidates", []):
            if cand.get("sandbox_id") != "brain_worker":
                continue
            rec = cand.get("receipt") or {}
            receipt_sha = rec.get("knowledge_bundle_sha256") or rec.get("candidate_sha256")
            receipt_status = cand.get("status") or rec.get("status") or "unknown"
            receipt_id = cand.get("receipt_id") or rec.get("receipt_id")
            blockers = list(rec.get("failures") or cand.get("failures") or [])
            break

    aligned = receipt_sha == local_bundle_sha and receipt_status == "PASS"
    alignment_status = "ALIGNED" if aligned else "MISALIGNED"
    if receipt_status != "PASS":
        alignment_status = "BLOCKED_WITH_REASON"

    if receipt_sha and receipt_sha != local_bundle_sha:
        errors.append(f"bundle_sha local={local_bundle_sha[:16]}… receipt={receipt_sha[:16]}…")
    if receipt_status != "PASS":
        errors.append(f"verifier status={receipt_status} (need PASS before promote)")

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = {
        "schema": "gate-candidate-alignment-v1",
        "receipt_id": f"gate-candidate-alignment-{ts}",
        "recorded_at": ts,
        "alignment_status": alignment_status,
        "local_head": local_head,
        "local_bundle_sha256": local_bundle_sha,
        "receipt_bundle_sha256": receipt_sha,
        "receipt_status": receipt_status,
        "verifier_receipt_id": receipt_id,
        "blockers": blockers,
        "remediation": "bash scripts/run_parallel_brain_candidates_v1.sh --sandbox-id brain_worker --json",
        "note": "Do not weaken promotion_gate — fix verifier PASS or repo ref blockers first",
    }
    path = RECEIPTS / f"{out['receipt_id']}.json"
    path.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")

    print(f"diagnose_gate_candidate_alignment_v1: {alignment_status}")
    print(json.dumps(out, indent=2))
    if errors:
        for e in errors:
            print(f" - {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
