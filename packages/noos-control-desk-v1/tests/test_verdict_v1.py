#!/usr/bin/env python3
"""Unit tests for control-desk/backend/verdict.py (Step 7B deterministic model:none patch)."""
import os
import sys
import unittest

BACKEND_ROOT = os.path.join(os.path.dirname(__file__), "..", "control-desk")
sys.path.insert(0, BACKEND_ROOT)

from backend.verdict import compute_verdict, is_deterministic_eligible  # noqa: E402


GHA_VERIFY = {
    "workflow_id": "ssot_agentic_ci",
    "owner": "github_actions",
    "class": "verify",
    "trigger": "event",
    "model_policy": "model:none",
}

CF_OBSERVE = {
    "workflow_id": "noos_loop_health_checks",
    "owner": "cloudflare_worker",
    "class": "observe",
    "trigger": "schedule",
    "model_policy": "model:none",
}

NOOS_RECONCILE = {
    "workflow_id": "ssot_brain_loop_autorun_v1",
    "owner": "noos_integrator",
    "class": "reconcile",
    "trigger": "schedule",
    "model_policy": "model:none",
}

COPILOT_MANUAL = {
    "workflow_id": "trustfield_copilot_cloud_agent",
    "owner": "copilot_manual",
    "class": "observe",
    "trigger": "manual",
    "model_policy": "gpt-5-mini-low",
}

COPILOT_MINI_OK = {
    "observed_trigger": "manual",
    "observed_mode": "manual",
    "observed_model": "gpt-5-mini",
    "observed_effort": "low",
}

MODEL_NONE_OK = {
    "observed_trigger": "event",
    "observed_mode": "deterministic",
    "observed_model": "model:none",
    "observed_effort": "low",
}


class VerdictDeterministicTests(unittest.TestCase):
    def test_gha_model_none_passes(self):
        verdict, reasons = compute_verdict(MODEL_NONE_OK, GHA_VERIFY)
        self.assertEqual(verdict, "PASS")
        self.assertTrue(any("model:none" in r for r in reasons))

    def test_cf_worker_model_none_passes(self):
        observed = {**MODEL_NONE_OK, "observed_trigger": "schedule", "observed_mode": "cloudflare-cron"}
        verdict, _ = compute_verdict(observed, CF_OBSERVE)
        self.assertEqual(verdict, "PASS")

    def test_noos_integrator_model_none_passes(self):
        observed = {**MODEL_NONE_OK, "observed_trigger": "schedule"}
        verdict, _ = compute_verdict(observed, NOOS_RECONCILE)
        self.assertEqual(verdict, "PASS")

    def test_copilot_unknown_model_blocked(self):
        observed = {
            "observed_trigger": "manual",
            "observed_mode": "unknown",
            "observed_model": "unknown",
            "observed_effort": "unknown",
        }
        verdict, reasons = compute_verdict(observed, COPILOT_MANUAL)
        self.assertEqual(verdict, "BLOCKED")
        self.assertTrue(any("Copilot" in r for r in reasons))

    def test_copilot_forbidden_model_fails(self):
        observed = {
            **COPILOT_MINI_OK,
            "observed_model": "gpt-5.4",
            "observed_effort": "high",
            "observed_trigger": "hourly",
        }
        verdict, reasons = compute_verdict(observed, COPILOT_MANUAL)
        self.assertEqual(verdict, "FAIL")
        self.assertTrue(any("forbidden" in r.lower() for r in reasons))

    def test_copilot_gpt5_mini_passes(self):
        verdict, _ = compute_verdict(COPILOT_MINI_OK, COPILOT_MANUAL)
        self.assertEqual(verdict, "PASS")

    def test_unknown_model_non_copilot_blocked(self):
        observed = {**COPILOT_MINI_OK, "observed_model": "SomeBrandNewModelXYZ"}
        verdict, reasons = compute_verdict(observed, GHA_VERIFY)
        self.assertEqual(verdict, "BLOCKED")
        self.assertTrue(any("unknown model" in r for r in reasons))

    def test_model_none_on_copilot_owner_blocked(self):
        observed = {**MODEL_NONE_OK, "observed_model": "model:none"}
        verdict, reasons = compute_verdict(observed, COPILOT_MANUAL)
        self.assertEqual(verdict, "BLOCKED")
        self.assertTrue(any("model:none" in r for r in reasons))

    def test_observed_reality_preserved_in_caller(self):
        """Verdict normalizes for comparison only; handler stores raw values separately."""
        raw_model = " model:none "
        observed = {**MODEL_NONE_OK, "observed_model": raw_model}
        verdict, _ = compute_verdict(observed, GHA_VERIFY)
        self.assertEqual(verdict, "PASS")
        self.assertEqual(observed["observed_model"], raw_model)

    def test_is_deterministic_eligible(self):
        self.assertTrue(is_deterministic_eligible(GHA_VERIFY))
        self.assertFalse(is_deterministic_eligible(COPILOT_MANUAL))

    def test_invalid_deterministic_trigger_fails(self):
        observed = {**MODEL_NONE_OK, "observed_trigger": "hourly"}
        verdict, reasons = compute_verdict(observed, GHA_VERIFY)
        self.assertEqual(verdict, "FAIL")
        self.assertTrue(any("trigger" in r.lower() for r in reasons))


if __name__ == "__main__":
    unittest.main()
