"""Tests for hourly AI circle job plan artifact."""
from __future__ import annotations

import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "hourly_ai_circle_job_plan_v1",
    ROOT / "scripts" / "hourly_ai_circle_job_plan_v1.py",
)
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MOD)


class JobPlanTests(unittest.TestCase):
    def test_build_plan_allowlisted(self) -> None:
        plan = MOD.build_plan("motor_job", "receipt-test", "bounded proof")
        self.assertEqual(plan["schema"], MOD.SCHEMA)
        self.assertEqual(plan["hold"], "HOLD")
        self.assertEqual(plan["job_id"], "motor_job")
        self.assertIn("IndependentVerify", plan["closed_loop"])

    def test_rejects_unknown_job(self) -> None:
        with self.assertRaises(ValueError):
            MOD.build_plan("merge_main", "receipt-test")

    def test_rejects_hold_lift(self) -> None:
        with self.assertRaises(ValueError):
            MOD.build_plan("motor_job", "receipt-test", hold="LIFTED")


if __name__ == "__main__":
    unittest.main()
