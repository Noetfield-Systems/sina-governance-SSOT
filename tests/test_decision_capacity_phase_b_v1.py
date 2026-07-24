#!/usr/bin/env python3
"""Phase B — Decision Capacity shadow replay tests."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from decision_capacity_shadow_replay_v1 import (  # noqa: E402
    bump_coverage,
    run,
    structural_replay_checks,
)


class PhaseBShadowReplayTests(unittest.TestCase):
    def test_structural_ok(self):
        body = {
            "when": {"task_type": "webpage_change"},
            "select": {"workflow": "deterministic_web_change_v1"},
            "limits": {"max_files": 5, "max_attempts": 2, "max_fanout": 0},
            "verify": [
                "build_passes",
                "target_issue_absent",
                "unrelated_pages_unchanged",
                "receipt_written",
            ],
            "escalate_when": ["positioning_change_detected"],
        }
        self.assertEqual(structural_replay_checks(body, "WEBPAGE_CHANGE"), [])

    def test_structural_fanout_fail(self):
        body = {
            "when": {"task_type": "email_draft"},
            "select": {"workflow": "deterministic_email_draft_v1"},
            "limits": {"max_files": 1, "max_attempts": 2, "max_fanout": 3},
            "verify": ["draft_exists", "no_send_without_owner", "receipt_written"],
            "escalate_when": ["legal_claim_detected"],
        }
        fails = structural_replay_checks(body, "EMAIL_DRAFT")
        self.assertTrue(any("fanout" in f for f in fails))

    def test_run_fixture(self):
        fixture = ROOT / "receipts" / "learning" / "decision-capacity-phase-b-fixture-v1.json"
        self.assertTrue(fixture.is_file())
        with tempfile.TemporaryDirectory() as td:
            # run against real fixture; coverage file is repo-local — restore after
            cov_path = ROOT / "data" / "decision_class_policy_coverage_v1.json"
            before = cov_path.read_text(encoding="utf-8")
            try:
                summary = run(inputs=[fixture], write_receipt=False)
                self.assertGreaterEqual(summary["processed"], 1)
                self.assertEqual(summary["passed"], summary["processed"])
                self.assertTrue(summary["verdict"].startswith("PASS_PHASE_B"))
            finally:
                cov_path.write_text(before, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
