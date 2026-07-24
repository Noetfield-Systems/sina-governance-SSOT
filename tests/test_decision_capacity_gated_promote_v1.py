#!/usr/bin/env python3
"""Tests — GATED promote WEBPAGE_CHANGE."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
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

    def test_live_policy_file_shape(self):
        live = ROOT / "data/decision_policies/live/WEBPAGE_CHANGE.json"
        self.assertTrue(live.is_file(), "promote must create live policy file first")
        doc = json.loads(live.read_text(encoding="utf-8"))
        self.assertEqual(doc["schema"], "noetfield.decision_policy_live.v1")
        self.assertEqual(doc["decision_class"], "WEBPAGE_CHANGE")
        self.assertEqual(doc["status"], "active")
        self.assertEqual(doc["founder_order"], "promote WEBPAGE_CHANGE")
        self.assertEqual(doc["body"]["limits"]["max_fanout"], 0)
        cov = json.loads((ROOT / "data/decision_class_policy_coverage_v1.json").read_text())
        row = cov["classes"]["WEBPAGE_CHANGE"]
        self.assertEqual(row["status"], "live_policy_active")
        self.assertGreaterEqual(row["coverage"], 0.9)
        self.assertTrue(str(row["active_policy_version"]).endswith(".live.") or ".live" in str(row["active_policy_version"]))


if __name__ == "__main__":
    unittest.main()
