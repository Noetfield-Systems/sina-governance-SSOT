#!/usr/bin/env python3
"""Tests — GATED promote live Decision Capacity policies."""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class GatedPromoteTests(unittest.TestCase):
    def test_refuse_wrong_order(self):
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/decision_capacity_gated_promote_v1.py"),
                "--decision-class",
                "WEBPAGE_CHANGE",
                "--founder-order",
                "please promote",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("REFUSE", proc.stderr + proc.stdout)

    def _assert_live(self, decision_class: str, founder_order: str) -> None:
        live = ROOT / f"data/decision_policies/live/{decision_class}.json"
        self.assertTrue(live.is_file(), f"promote must create live policy for {decision_class}")
        doc = json.loads(live.read_text(encoding="utf-8"))
        self.assertEqual(doc["schema"], "noetfield.decision_policy_live.v1")
        self.assertEqual(doc["decision_class"], decision_class)
        self.assertEqual(doc["status"], "active")
        self.assertEqual(doc["founder_order"], founder_order)
        self.assertEqual(doc["body"]["limits"]["max_fanout"], 0)
        cov = json.loads((ROOT / "data/decision_class_policy_coverage_v1.json").read_text())
        row = cov["classes"][decision_class]
        self.assertEqual(row["status"], "live_policy_active")
        self.assertGreaterEqual(row["coverage"], 0.9)
        self.assertIn(".live.", str(row["active_policy_version"]))

    def test_live_webpage_change(self):
        self._assert_live("WEBPAGE_CHANGE", "promote WEBPAGE_CHANGE")

    def test_live_webpage_repair(self):
        self._assert_live("WEBPAGE_REPAIR", "promote WEBPAGE_REPAIR")

    def test_live_email_draft(self):
        self._assert_live("EMAIL_DRAFT", "promote EMAIL_DRAFT")


if __name__ == "__main__":
    unittest.main()
