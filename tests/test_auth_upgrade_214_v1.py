"""Validate auth_upgrade_214_v1 registry."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "auth_upgrade_214_v1.json"


class AuthUpgrade214Tests(unittest.TestCase):
    def test_count_and_ids(self) -> None:
        doc = json.loads(REGISTRY.read_text(encoding="utf-8"))
        plans = doc["plans"]
        self.assertEqual(len(plans), 214)
        ids = [p["id"] for p in plans]
        self.assertEqual(ids[0], "AUTH-UPG-001")
        self.assertEqual(ids[-1], "AUTH-UPG-214")
        self.assertEqual(len(set(ids)), 214)


if __name__ == "__main__":
    unittest.main()
