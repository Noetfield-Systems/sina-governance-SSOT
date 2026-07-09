#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from commercial_pulse_dispatch_check_v1 import (  # noqa: E402
    _approval_metadata_present,
    _inside_approval_window,
    check_dispatchable,
)


def _valid_draft() -> dict:
    now = datetime.now(timezone.utc)
    return {
        "draft_id": "draft-1",
        "icp_stranger_id": "icp-1",
        "offer_id": "offer-1",
        "entity": "Noetfield Systems Inc.",
        "casl": {
            "mailing_address": "123 Main St, Toronto ON",
            "unsubscribe_url": "https://www.noetfield.com/unsubscribe",
        },
        "link_check_receipt_id": "linkcheck-1",
        "approval": {
            "required": True,
            "status": "pending",
            "window_start": (now - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "window_end": (now + timedelta(days=2)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    }


class CommercialPulseDispatchCheckTests(unittest.TestCase):
    def test_missing_approval_metadata_fails(self) -> None:
        draft = _valid_draft()
        draft.pop("approval")
        ok, failed = check_dispatchable(draft)
        self.assertFalse(ok)
        self.assertIn("approval_metadata_present", failed)

    def test_required_false_fails_approval_metadata(self) -> None:
        draft = _valid_draft()
        draft["approval"]["required"] = False
        self.assertFalse(_approval_metadata_present(draft))
        ok, failed = check_dispatchable(draft)
        self.assertIn("approval_metadata_present", failed)

    def test_expired_window_end_fails_even_without_flag(self) -> None:
        draft = _valid_draft()
        past = datetime.now(timezone.utc) - timedelta(hours=2)
        draft["approval"]["window_end"] = past.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.assertFalse(_inside_approval_window(draft))
        ok, failed = check_dispatchable(draft)
        self.assertIn("inside_approval_window", failed)

    def test_valid_draft_passes(self) -> None:
        ok, failed = check_dispatchable(_valid_draft())
        self.assertTrue(ok)
        self.assertEqual(failed, [])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
