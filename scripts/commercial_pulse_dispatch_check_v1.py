#!/usr/bin/env python3
"""Commercial Pulse dispatchability check (LS-053). Emits MALFORMED_DRAFT receipt on fail."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"
QUEUE_PATH = ROOT / "data/commercial_pulse_queue_v1.json"

PREDICATES = (
    "named_icp_stranger",
    "priced_offer_attached",
    "entity_hygiene_pass",
    "casl_mailing_address",
    "casl_unsubscribe",
    "link_check_receipt_attached",
    "approval_metadata_present",
    "inside_approval_window",
)

FORBIDDEN_ENTITY_TOKENS = ("trustfield technologies inc", "sourcea forge", "competitor")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_iso(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except ValueError:
        return None


def _approval_metadata_present(draft: dict[str, Any]) -> bool:
    approval = draft.get("approval")
    if not isinstance(approval, dict):
        return False
    if approval.get("required") is not True:
        return False
    status = str(approval.get("status") or "").strip()
    return bool(status)


def _inside_approval_window(draft: dict[str, Any], *, now: datetime | None = None) -> bool:
    if draft.get("approval_window_expired") is True:
        return False
    now = now or datetime.now(timezone.utc)
    approval = draft.get("approval") if isinstance(draft.get("approval"), dict) else {}
    start_raw = approval.get("window_start") or draft.get("approval_window_start")
    end_raw = approval.get("window_end") or draft.get("approval_window_end")
    start = _parse_iso(start_raw)
    end = _parse_iso(end_raw)
    if start and now < start:
        return False
    if end and now > end:
        return False
    return True


def check_dispatchable(draft: dict[str, Any]) -> tuple[bool, list[str]]:
    failed: list[str] = []
    if not draft.get("icp_stranger_id"):
        failed.append("named_icp_stranger")
    if not draft.get("offer_id") and not draft.get("price_display"):
        failed.append("priced_offer_attached")

    entity = str(draft.get("entity", "")).strip()
    if not entity or any(tok in entity.lower() for tok in FORBIDDEN_ENTITY_TOKENS):
        failed.append("entity_hygiene_pass")

    casl = draft.get("casl") or {}
    if not casl.get("mailing_address"):
        failed.append("casl_mailing_address")
    if not casl.get("unsubscribe_url"):
        failed.append("casl_unsubscribe")
    if not draft.get("link_check_receipt_id"):
        failed.append("link_check_receipt_attached")

    if not _approval_metadata_present(draft):
        failed.append("approval_metadata_present")
    if not _inside_approval_window(draft):
        failed.append("inside_approval_window")

    return len(failed) == 0, failed


def write_malformed_receipt(draft_id: str | None, failed: list[str]) -> Path:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RECEIPTS / f"commercial-pulse-malformed-draft-{stamp}.json"
    payload = {
        "schema": "MALFORMED_DRAFT",
        "receipt_type": "MALFORMED_DRAFT",
        "saved_at": _now(),
        "draft_id": draft_id,
        "failed_predicates": failed,
        "checker": "scripts/commercial_pulse_dispatch_check_v1.py",
        "status": "FAIL",
    }
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description="Commercial Pulse dispatchability check")
    parser.add_argument("--draft", help="path to draft JSON file")
    parser.add_argument("--json", action="store_true", help="print result JSON")
    args = parser.parse_args()

    if args.draft:
        draft = json.loads(Path(args.draft).read_text(encoding="utf-8"))
    else:
        try:
            draft = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("FAIL: provide --draft or stdin JSON", file=sys.stderr)
            return 2

    ok, failed = check_dispatchable(draft)
    result = {
        "schema": "commercial_pulse_dispatch_check_v1",
        "saved_at": _now(),
        "pass": ok,
        "failed_predicates": failed,
        "draft_id": draft.get("draft_id"),
    }

    if not ok:
        receipt_path = write_malformed_receipt(draft.get("draft_id"), failed)
        result["malformed_receipt"] = str(receipt_path.relative_to(ROOT))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"commercial_pulse_dispatch_check_v1: {'PASS' if ok else 'FAIL'}")
        if failed:
            print("failed:", ", ".join(failed))

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
