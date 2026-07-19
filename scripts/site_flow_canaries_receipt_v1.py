#!/usr/bin/env python3
"""Validate and seal the bounded SITE_FLOW_CANARIES_V1 R2 receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

WORK_ORDER_ID = "wo.e2e_activation"
WORK_ORDER_VERSION = "v1"
IDEMPOTENCY_KEY = "wo.e2e_activation:v1"
SOURCE_REPOSITORY = "Noetfield-Systems/sina-governance-SSOT"
SCHEMA = "site_flow_canaries_v1"
VERDICT = "PASS_SYNTHETIC_CANARIES"
EXPECTED_FLOWS = {
    "sourceb.workspace",
    "noetfield.enterprise_intake",
    "trustfield.evidence_assessment",
}
ENVELOPE_FIELDS = (
    "work_order_id",
    "work_order_version",
    "idempotency_key",
    "source_repository",
    "source_sha",
    "run_url",
    "receipt_sha256",
)


class ReceiptValidationError(ValueError):
    """The receipt is missing a required invariant or crosses a fixed boundary."""


def _fail(message: str) -> None:
    raise ReceiptValidationError(message)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _fail(f"cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, dict):
        _fail("receipt root must be an object")
    return value


def canonical_receipt_bytes(receipt: dict[str, Any]) -> bytes:
    payload = dict(receipt)
    payload.pop("receipt_sha256", None)
    return json.dumps(
        payload,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def receipt_sha256(receipt: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_receipt_bytes(receipt)).hexdigest()


def validate_dispatch_constants(
    *, work_order_id: str, work_order_version: str, idempotency_key: str
) -> None:
    if work_order_id != WORK_ORDER_ID:
        _fail(f"work_order_id must be {WORK_ORDER_ID}")
    if work_order_version != WORK_ORDER_VERSION:
        _fail(f"work_order_version must be {WORK_ORDER_VERSION}")
    if idempotency_key != IDEMPOTENCY_KEY:
        _fail(f"idempotency_key must be {IDEMPOTENCY_KEY}")


def validate_base_receipt(receipt: dict[str, Any]) -> None:
    if receipt.get("schema") != SCHEMA:
        _fail(f"schema must be {SCHEMA}")
    if receipt.get("verdict") != VERDICT:
        _fail(f"verdict must be {VERDICT}")
    if receipt.get("mode") != "synthetic":
        _fail("mode must be synthetic")
    if receipt.get("errors") != []:
        _fail("errors must be an empty list")

    flows = receipt.get("flows")
    if not isinstance(flows, list) or len(flows) != len(EXPECTED_FLOWS):
        _fail(f"flows must contain exactly {len(EXPECTED_FLOWS)} rows")
    names = {
        row.get("site_flow")
        for row in flows
        if isinstance(row, dict) and isinstance(row.get("site_flow"), str)
    }
    if names != EXPECTED_FLOWS:
        _fail(f"flows must be exactly {sorted(EXPECTED_FLOWS)}")

    metrics = receipt.get("metrics")
    if not isinstance(metrics, dict):
        _fail("metrics must be an object")
    required_metrics = {
        "duplicate_executions": 0,
        "idle_llm_calls": 0,
        "customer_visible_failures": 0,
        "flows_proven_synthetic": len(EXPECTED_FLOWS),
    }
    for key, expected in required_metrics.items():
        if metrics.get(key) != expected:
            _fail(f"metrics.{key} must be {expected}")


def validate_enriched_receipt(receipt: dict[str, Any]) -> None:
    validate_base_receipt(receipt)
    validate_dispatch_constants(
        work_order_id=str(receipt.get("work_order_id", "")),
        work_order_version=str(receipt.get("work_order_version", "")),
        idempotency_key=str(receipt.get("idempotency_key", "")),
    )
    if receipt.get("source_repository") != SOURCE_REPOSITORY:
        _fail(f"source_repository must be {SOURCE_REPOSITORY}")
    source_sha = receipt.get("source_sha")
    if not isinstance(source_sha, str) or re.fullmatch(r"[0-9a-f]{40}", source_sha) is None:
        _fail("source_sha must be a lowercase 40-character Git SHA")
    run_url = receipt.get("run_url")
    run_pattern = (
        r"https://github\.com/Noetfield-Systems/sina-governance-SSOT/"
        r"actions/runs/[0-9]+"
    )
    if not isinstance(run_url, str) or re.fullmatch(run_pattern, run_url) is None:
        _fail("run_url must identify this repository's GitHub Actions run")
    claimed_hash = receipt.get("receipt_sha256")
    if not isinstance(claimed_hash, str) or re.fullmatch(r"[0-9a-f]{64}", claimed_hash) is None:
        _fail("receipt_sha256 must be a lowercase SHA-256 digest")
    actual_hash = receipt_sha256(receipt)
    if claimed_hash != actual_hash:
        _fail(f"receipt_sha256 mismatch: expected {actual_hash}, got {claimed_hash}")


def finalize_receipt(
    base: dict[str, Any], *, source_sha: str, run_url: str
) -> dict[str, Any]:
    validate_base_receipt(base)
    present = sorted(field for field in ENVELOPE_FIELDS if field in base)
    if present:
        _fail(f"generated receipt already contains executor envelope fields: {present}")
    enriched = dict(base)
    enriched.update(
        {
            "work_order_id": WORK_ORDER_ID,
            "work_order_version": WORK_ORDER_VERSION,
            "idempotency_key": IDEMPOTENCY_KEY,
            "source_repository": SOURCE_REPOSITORY,
            "source_sha": source_sha,
            "run_url": run_url,
        }
    )
    enriched["receipt_sha256"] = receipt_sha256(enriched)
    validate_enriched_receipt(enriched)
    return enriched


def _write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _dispatch_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--work-order-id", required=True)
    parser.add_argument("--work-order-version", required=True)
    parser.add_argument("--idempotency-key", required=True)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    preflight = subparsers.add_parser("preflight")
    preflight.add_argument("--receipt", type=Path, required=True)
    preflight.add_argument("--source-repository", required=True)
    _dispatch_args(preflight)

    finalize = subparsers.add_parser("finalize")
    finalize.add_argument("--input", type=Path, required=True)
    finalize.add_argument("--output", type=Path, required=True)
    finalize.add_argument("--source-repository", required=True)
    finalize.add_argument("--source-sha", required=True)
    finalize.add_argument("--run-url", required=True)
    _dispatch_args(finalize)

    verify = subparsers.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)
    verify.add_argument("--expected", type=Path, required=True)
    verify.add_argument("--source-repository", required=True)
    _dispatch_args(verify)
    return parser


def _validate_cli_bounds(args: argparse.Namespace) -> None:
    validate_dispatch_constants(
        work_order_id=args.work_order_id,
        work_order_version=args.work_order_version,
        idempotency_key=args.idempotency_key,
    )
    if args.source_repository != SOURCE_REPOSITORY:
        _fail(f"source_repository must be {SOURCE_REPOSITORY}")


def main() -> int:
    args = _build_parser().parse_args()
    try:
        _validate_cli_bounds(args)
        if args.command == "preflight":
            receipt = _read_json(args.receipt)
            validate_enriched_receipt(receipt)
            print(
                json.dumps(
                    {
                        "status": "ALREADY_COMPLETE",
                        "work_order_id": WORK_ORDER_ID,
                        "idempotency_key": IDEMPOTENCY_KEY,
                        "receipt_sha256": receipt["receipt_sha256"],
                    },
                    sort_keys=True,
                )
            )
            return 0

        if args.command == "finalize":
            receipt = finalize_receipt(
                _read_json(args.input), source_sha=args.source_sha, run_url=args.run_url
            )
            _write_json(args.output, receipt)
            print(json.dumps({"status": "SEALED", "receipt_sha256": receipt["receipt_sha256"]}))
            return 0

        receipt = _read_json(args.receipt)
        expected = _read_json(args.expected)
        validate_enriched_receipt(receipt)
        validate_enriched_receipt(expected)
        if receipt != expected:
            _fail("R2 read-back content differs from the uploaded receipt")
        print(json.dumps({"status": "READ_BACK_VERIFIED", "receipt_sha256": receipt["receipt_sha256"]}))
        return 0
    except ReceiptValidationError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
