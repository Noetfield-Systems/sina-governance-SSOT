#!/usr/bin/env python3
"""Unit tests — Decision Capacity closed path."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.decision_capacity_v1 import (  # noqa: E402
    build_capacity_proposal,
    close_capacity_loop,
    detect_capacity_gap,
    map_events_to_founder_choices,
    to_learning_organ_record,
    to_policy_candidate,
)


class DecisionCapacityTests(unittest.TestCase):
    def test_map_choices(self):
        choices = map_events_to_founder_choices(
            ["GOAL_RESTATEMENT", "GOAL_RESTATEMENT", "MANUAL_CORRECTION", "OWNER_DECISION"]
        )
        self.assertEqual(choices, ["restate_goal_intent", "select_target_files"])

    def test_gap_on_repeated_tax(self):
        gap = detect_capacity_gap(
            decision_class="WEBPAGE_REPAIR",
            event_types=["GOAL_RESTATEMENT", "SCOPE_RESTATEMENT", "FALSE_DONE_REJECTION"],
            existing_policy_coverage=0.35,
            task_id="t1",
            human_tax_units=12,
        )
        self.assertIsNotNone(gap)
        assert gap is not None
        self.assertEqual(gap["incident_type"], "MISSING_DECISION_CAPACITY")
        self.assertEqual(gap["work_status"], "FROZEN")
        self.assertIn("restate_goal_intent", gap["repeated_founder_choices"])
        self.assertEqual(gap["proposed_action"], "CREATE_OR_EXTEND_POLICY")

    def test_no_gap_when_covered(self):
        gap = detect_capacity_gap(
            decision_class="EMAIL_DRAFT",
            event_types=["GOAL_RESTATEMENT"],
            existing_policy_coverage=0.99,
        )
        self.assertIsNone(gap)

    def test_proposal_and_candidate(self):
        gap = detect_capacity_gap(
            decision_class="EMAIL_DRAFT",
            event_types=["TOOL_CANCELLATION", "MANUAL_RESTART"],
            existing_policy_coverage=0.2,
        )
        self.assertIsNotNone(gap)
        assert gap is not None
        prop = build_capacity_proposal(gap)
        self.assertEqual(prop["schema"], "noetfield.decision_capacity_proposal.v1")
        self.assertIn("max_fanout", prop["proposed_policy"]["limits"])
        cand = to_policy_candidate(prop)
        self.assertEqual(cand["replay_status"], "queued")
        lr = to_learning_organ_record(cand)
        self.assertEqual(lr["status"], "draft")
        self.assertEqual(lr["layer"], "policy")
        self.assertEqual(lr["source_event"], "MISSING_DECISION_CAPACITY")

    def test_close_loop(self):
        loop = close_capacity_loop(
            decision_class="WEBPAGE_CHANGE",
            event_types=["GOAL_RESTATEMENT", "MANUAL_CORRECTION", "MANUAL_VERIFICATION"],
            existing_policy_coverage=0.1,
        )
        self.assertIsNotNone(loop)
        assert loop is not None
        self.assertEqual(loop["policy_candidate"]["learning_record_id"], loop["learning_record"]["record_id"])


if __name__ == "__main__":
    unittest.main()
