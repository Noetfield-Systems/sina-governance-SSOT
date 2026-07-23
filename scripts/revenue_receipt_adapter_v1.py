#!/usr/bin/env python3
"""Revenue receipt adapter v1 (W5-11).

Deterministic: Stripe checkout.session.completed event JSON in ->
FIRST_REVENUE_RECEIPT JSON file in receipts/revenue/ out. No network, no LLM.

Rules (fail-closed):
- Only event type checkout.session.completed is accepted.
- payment_status must be "paid".
- livemode=false (Stripe test mode) or --dry-run ALWAYS produces a
  FIRST_REVENUE_RECEIPT_DRYRUN_* file with mode=TEST_MODE_DRYRUN. A test-mode
  event can never mint a real-revenue claim.
- livemode=true produces FIRST_REVENUE_RECEIPT_* with status FOUNDER_VERIFY —
  the doctrine endpoint (W5-13) still requires founder countersign; this
  adapter records, it does not declare victory.
- No PII lands in the receipt: payer email is reduced to a sha256 prefix,
  session id to its first 12 chars.

Offer naming: metadata.offer if the checkout carried one, else the locked
first offer "Never Miss a Call" (sourceb.ca fit-call CA$95 and assessment
CA$295 checkouts are that offer's qualification funnel).
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

LOCKED_OFFER = "Never Miss a Call"
OUT_DIR = Path(__file__).resolve().parent.parent / "receipts" / "revenue"


def fail(msg: str) -> "SystemExit":
    print(json.dumps({"status": "REJECTED", "reason": msg}))
    return SystemExit(1)


def sha256_prefix(value: str, n: int = 16) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:n]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--event-file", help="path to Stripe event JSON (default: stdin)")
    ap.add_argument("--dry-run", action="store_true",
                    help="force DRYRUN output even for a livemode event")
    ap.add_argument("--out-dir", default=str(OUT_DIR))
    args = ap.parse_args()

    raw = Path(args.event_file).read_text() if args.event_file else sys.stdin.read()
    try:
        event = json.loads(raw)
    except json.JSONDecodeError as e:
        raise fail(f"invalid JSON: {e}")

    if event.get("type") != "checkout.session.completed":
        raise fail(f"unsupported event type {event.get('type')!r}")
    obj = (event.get("data") or {}).get("object") or {}
    if obj.get("payment_status") != "paid":
        raise fail(f"payment_status {obj.get('payment_status')!r} != paid")

    livemode = bool(event.get("livemode"))
    dryrun = args.dry_run or not livemode
    amount_total = obj.get("amount_total")
    currency = (obj.get("currency") or "").upper()
    metadata = obj.get("metadata") or {}
    offer = metadata.get("offer") or LOCKED_OFFER
    created = event.get("created")
    if isinstance(created, (int, float)):
        stamp_dt = datetime.fromtimestamp(created, tz=timezone.utc)
    else:
        raise fail("event.created missing — refusing to invent a timestamp")
    ts = stamp_dt.strftime("%Y%m%dT%H%M%SZ")

    payer_email = obj.get("customer_email") or (obj.get("customer_details") or {}).get("email") or ""
    receipt = {
        "schema": "first_revenue_receipt_v1",
        "job_id": "W5-11",
        "mode": "TEST_MODE_DRYRUN" if dryrun else "LIVE",
        "status": "DRYRUN_PASS" if dryrun else "FOUNDER_VERIFY",
        "offer": offer,
        "amount_total_cents": amount_total,
        "currency": currency,
        "event": {
            "id": str(event.get("id", ""))[:32],
            "type": event["type"],
            "livemode": livemode,
            "created_utc": stamp_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "session_id_prefix": str(obj.get("id", ""))[:12],
            "payer_email_sha256_prefix": sha256_prefix(payer_email) if payer_email else None,
            "sourceb_kind": metadata.get("sourceb_kind"),
            "lead_receipt_id": metadata.get("lead_receipt_id"),
        },
        "doctrine": ("test-mode dry-run: proves the adapter path only, claims no revenue"
                     if dryrun else
                     "real checkout recorded; doctrine endpoint W5-13 closes only on founder countersign"),
        "generated_by": "scripts/revenue_receipt_adapter_v1.py",
    }

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    name = ("FIRST_REVENUE_RECEIPT_DRYRUN_" if dryrun else "FIRST_REVENUE_RECEIPT_") + ts + ".json"
    out_path = out_dir / name
    out_path.write_text(json.dumps(receipt, indent=1) + "\n")
    print(json.dumps({"status": "OK", "receipt": str(out_path), "mode": receipt["mode"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
