#!/usr/bin/env python3
"""SourceA Brain B-04 — independent verify + register trustfield-loops artifact.

Law: Worker report = claim, not receipt. SG/Brain runner re-executes phase1 battery
and registers only on independent PASS + locked-definition collision PASS.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TF_ROOT = Path.home() / "Desktop" / "trustfield-loops"
SOURCEA_ROOT = Path.home() / "Projects" / "SourceA"
REGISTRY_PATH = ROOT / "data" / "brain_external_artifact_registry_v1.json"
LOCKED_DEFS = SOURCEA_ROOT / "reports" / "locked-definitions-v1.json"
RECEIPTS_DIR = ROOT / "receipts"

ARTIFACT_PATHS = (
    "src/index.ts",
    "src/receipt.ts",
    "src/intake.ts",
    "src/crypto.ts",
    "src/types.ts",
    "migrations/0001_init.sql",
    "scripts/run_phase1_battery.sh",
)

FORBIDDEN_IN_TF = (
    "SourceA is an AI execution platform",
    "sourcea-brain-chat",
    "knowledge-bundle.json",
)

CUSTODY_CLAIMS_IN_CODE = (
    "we hold funds",
    "money transmission license for trustfield",
    "trustfield holds client funds",
)


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(repo: Path) -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()


def run_independent_verify() -> tuple[bool, str, list[str]]:
    if not TF_ROOT.is_dir():
        return False, f"trustfield-loops missing: {TF_ROOT}", []
    proc = subprocess.run(
        ["npm", "run", "test:phase1"],
        cwd=TF_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    out = proc.stdout + proc.stderr
    if proc.returncode != 0 or "PHASE1_BATTERY: PASS" not in out:
        return False, out[-2000:], []
    receipt_ids: list[str] = []
    for line in out.splitlines():
        if line.startswith("rcpt_"):
            receipt_ids.append(line.split()[0])
    return True, out, receipt_ids


def collision_check() -> tuple[bool, list[str]]:
    errors: list[str] = []
    if not LOCKED_DEFS.is_file():
        errors.append(f"locked-definitions missing: {LOCKED_DEFS}")
        return False, errors

    locked = json.loads(LOCKED_DEFS.read_text(encoding="utf-8"))
    approved_snippets: list[str] = []
    for term in locked.get("terms", []):
        text = term.get("approved_text", "")
        if text:
            approved_snippets.append(text[:80])

    blob = ""
    for rel in ARTIFACT_PATHS:
        p = TF_ROOT / rel
        if p.is_file():
            blob += p.read_text(encoding="utf-8", errors="replace") + "\n"

    for forbidden in FORBIDDEN_IN_TF:
        if forbidden.lower() in blob.lower():
            errors.append(f"collision: TF artifact embeds SourceA locked prose: {forbidden[:40]}")

    for claim in CUSTODY_CLAIMS_IN_CODE:
        if claim.lower() in blob.lower():
            errors.append(f"collision: TF code contains custody claim language: {claim}")

    if re.search(r"send_capability\s*:\s*true", blob, re.I):
        errors.append("collision: send_capability true found in artifact")

    # Venture artifact must not register as SourceA entity
    if '"entity":"sourcea"' in blob.replace(" ", "") or "entity: sourcea" in blob.lower():
        errors.append("collision: artifact tagged entity sourcea")

    return len(errors) == 0, errors


def artifact_provenance() -> dict:
    files = {}
    for rel in ARTIFACT_PATHS:
        p = TF_ROOT / rel
        if p.is_file():
            files[rel] = sha256_file(p)
    composite = hashlib.sha256(
        json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "repo_path": str(TF_ROOT),
        "git_head": git_head(TF_ROOT),
        "file_sha256": files,
        "composite_sha256": composite,
        "entity": "trustfield",
        "order": "TF-ARCH-W1",
        "phase": 1,
        "send_capability": False,
    }


def load_registry() -> dict:
    if REGISTRY_PATH.is_file():
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    return {"schema": "brain_external_artifact_registry_v1", "version": "1.0.0", "registrations": []}


def main() -> int:
    ts = utc_stamp()
    receipt_id = f"brain-register-tf-loops-{ts}"

    ok, verify_out, test_receipt_ids = run_independent_verify()
    if not ok:
        print("brain_register_trustfield_loops_v1: FAIL independent verify")
        print(verify_out)
        return 1

    coll_ok, coll_errors = collision_check()
    if not coll_ok:
        print("brain_register_trustfield_loops_v1: FAIL collision check")
        for e in coll_errors:
            print(f" - {e}")
        return 1

    prov = artifact_provenance()
    memory_line = (
        "brain/register: trustfield-loops Phase1 PASS independent; "
        f"head={prov['git_head'][:8]} entity=trustfield send=false"
    )[:280]

    entry = {
        "registration_id": receipt_id,
        "registered_at": ts,
        "artifact_id": "trustfield_loops_phase1",
        "owner_entity": "trustfield",
        "worker_actor": "TrustField Worker",
        "brain_task": "B-04",
        "provenance": prov,
        "independent_verify": {
            "runner": "sina-governance-ssot/scripts/brain_register_trustfield_loops_v1.py",
            "command": "npm run test:phase1",
            "pass_line": "PHASE1_BATTERY: PASS",
            "test_receipt_ids": test_receipt_ids,
        },
        "collision_check": {"status": "PASS", "locked_definitions": str(LOCKED_DEFS)},
        "memory_line": memory_line,
        "brain_mode": "read_only_pointer",
        "export_direction": "trustfield_to_sourcea_one_way",
    }

    registry = load_registry()
    regs = registry.setdefault("registrations", [])
    regs = [r for r in regs if r.get("artifact_id") != "trustfield_loops_phase1"]
    regs.append(entry)
    registry["registrations"] = regs
    registry["saved_at"] = ts
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "brain-artifact-registration-receipt-v1",
        "receipt_id": receipt_id,
        "receipt_type": "BRAIN_REGISTER_B04",
        "recorded_at": ts,
        "entity": "sourcea",
        "artifact_id": "trustfield_loops_phase1",
        "owner_entity": "trustfield",
        "independent_verify_pass": True,
        "collision_check_pass": True,
        "composite_sha256": prov["composite_sha256"],
        "git_head": prov["git_head"],
        "memory_line": memory_line,
        "registry_path": "data/brain_external_artifact_registry_v1.json",
        "test_receipt_ids": test_receipt_ids,
    }
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    receipt_path = RECEIPTS_DIR / f"{receipt_id}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print("brain_register_trustfield_loops_v1: ALL PASS")
    print(f"receipt_id={receipt_id}")
    print(f"composite_sha256={prov['composite_sha256']}")
    print(f"memory_line={memory_line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
