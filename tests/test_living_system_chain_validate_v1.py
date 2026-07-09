#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from living_system_chain_validate_v1 import (  # noqa: E402
    _is_scheduled_pulse,
    check_mutation_or_idle,
    load_subsystem,
)


class LivingSystemChainValidateTests(unittest.TestCase):
    def test_load_subsystem_global_uses_registry_entry(self) -> None:
        row = load_subsystem("global")
        self.assertIsNotNone(row)
        assert row is not None
        self.assertEqual(row.get("id"), "global")
        globs = row.get("pulse_receipt_globs") or []
        self.assertIn("receipts/brain-loop-autorun-*.json", globs)
        self.assertEqual(row.get("window_hours"), 168)

    def test_cloud_trigger_without_pulse_proof_is_not_scheduled(self) -> None:
        path = Path("receipts/living-system-w1-terminology-2026-07-08.json")
        payload = json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(_is_scheduled_pulse(payload, path))

    def test_terminology_receipt_does_not_satisfy_mutation_check(self) -> None:
        rel = "receipts/living-system-w1-terminology-2026-07-08.json"
        check = check_mutation_or_idle(load_subsystem("global"))
        self.assertNotIn(rel, check.evidence)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
