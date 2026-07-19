#!/usr/bin/env python3
"""Compute or verify exact source pins for the SG v2 shadow evaluator."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "workers/sg-authority-v2-shadow"
HASH_FILE = ROOT / "data/sg_authority_v2_shadow_hashes_v1.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle(paths: list[Path]) -> dict:
    files = [
        {"path": path.relative_to(ROOT).as_posix(), "sha256": sha256(path)}
        for path in sorted(paths)
    ]
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return {"sha256": hashlib.sha256(canonical).hexdigest(), "files": files}


def expected() -> dict:
    policy = ROOT / "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_SG_AUTHORITY_IDENTITY_V2_LOCKED.md"
    schemas = [
        ROOT / "schemas/sg_decision_receipt_v1.schema.json",
        ROOT / "schemas/sg_signed_permit_v1.schema.json",
        ROOT / "schemas/sg_webhook_delivery_v1.schema.json",
    ]
    evaluator = [WORKER / "src/evaluator.ts", WORKER / "src/types.ts"]
    worker_sources = list((WORKER / "src").glob("*.ts"))
    return {
        "schema": "noetfield.sg-authority-v2-shadow-hashes.v1",
        "policy": {"path": policy.relative_to(ROOT).as_posix(), "sha256": sha256(policy)},
        "schema_bundle": bundle(schemas),
        "evaluator_bundle": bundle(evaluator),
        "worker_source_bundle": bundle(worker_sources),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    pins = expected()
    if args.check:
        actual = json.loads(HASH_FILE.read_text())
        comparable = {key: value for key, value in actual.items() if key != "generated_at"}
        if comparable != pins:
            print("SG_V2_SHADOW_HASHES=FAIL")
            return 1
        print("SG_V2_SHADOW_HASHES=PASS")
        return 0

    record = {
        **pins,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }
    HASH_FILE.write_text(json.dumps(record, indent=2) + "\n")
    wrangler_path = WORKER / "wrangler.jsonc"
    wrangler = json.loads(wrangler_path.read_text())
    wrangler["vars"].update({
        "POLICY_HASH": pins["policy"]["sha256"],
        "SCHEMA_HASH": pins["schema_bundle"]["sha256"],
        "EVALUATOR_HASH": pins["evaluator_bundle"]["sha256"],
    })
    wrangler_path.write_text(json.dumps(wrangler, indent=2) + "\n")
    config_path = ROOT / "data/sg_authority_v2_shadow_config_v1.json"
    config = json.loads(config_path.read_text())
    config["worker"].update({
        "policy_hash": pins["policy"]["sha256"],
        "schema_hash": pins["schema_bundle"]["sha256"],
        "evaluator_hash": pins["evaluator_bundle"]["sha256"],
        "source_hash": pins["worker_source_bundle"]["sha256"],
    })
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    print("SG_V2_SHADOW_HASHES=UPDATED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
