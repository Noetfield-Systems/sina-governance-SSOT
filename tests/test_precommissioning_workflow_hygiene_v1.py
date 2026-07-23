from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.validate_p0pgr_packet_path_v1 import ROOT, validate_packet_path

WORKFLOW = ROOT / ".github/workflows/p0pgr-shadow-cycle-v1.yml"
REGISTRY = ROOT / "data/github_automation_registry_v1.json"
PINS = ROOT / "data/github_action_pins_v1.json"
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")
EXPECTED_ACTION_PINS = {
    "actions/checkout": "34e114876b0b11c390a56381ad16ebd13914f8d5",
    "actions/setup-python": "a26af69be951a213d495a4c3e4e4022e16d87065",
    "actions/upload-artifact": "ea165f8d65b6e75b540449e92b4886f43607fa02",
}


class PrecommissioningWorkflowHygieneTests(unittest.TestCase):
    def test_every_workflow_has_exactly_one_registry_entry(self) -> None:
        registry = json.loads(REGISTRY.read_text())
        registered = [motor.get("workflow_file") for motor in registry["motors"]]
        workflows = sorted(
            [*ROOT.glob(".github/workflows/*.yml"), *ROOT.glob(".github/workflows/*.yaml")]
        )
        self.assertTrue(workflows)
        for workflow in workflows:
            relative = workflow.relative_to(ROOT).as_posix()
            self.assertEqual(registered.count(relative), 1, relative)

    def test_valid_packet_is_canonical_repository_relative_json(self) -> None:
        packet = "p0-pgr/EXAMPLE_PACKET_P0PGR-20260708-001.json"
        self.assertEqual(validate_packet_path(packet), packet)

    def test_malicious_and_invalid_packet_inputs_are_rejected(self) -> None:
        invalid = (
            "",
            "/etc/passwd.json",
            "../secret.json",
            "p0-pgr/../data/runtime_reality_v1.json",
            "p0-pgr/./EXAMPLE_PACKET_P0PGR-20260708-001.json",
            "p0-pgr//EXAMPLE_PACKET_P0PGR-20260708-001.json",
            "p0-pgr/nested/packet.json",
            "p0-pgr/not-json.txt",
            "p0-pgr/not-json.JSON",
            "p0-pgr/file.json; touch /tmp/pwned",
            "p0-pgr/$(touch /tmp/pwned).json",
            "p0-pgr/file.json\nMALICIOUS=1",
            r"p0-pgr\file.json",
        )
        for packet in invalid:
            with self.subTest(packet=packet):
                with self.assertRaises((OSError, ValueError)):
                    validate_packet_path(packet)

    def test_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            packet_root = root / "p0-pgr"
            packet_root.mkdir()
            outside = root / "outside.json"
            outside.write_text("{}\n")
            (packet_root / "escape.json").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "symlink"):
                validate_packet_path("p0-pgr/escape.json", root=root)

    def test_dispatch_input_is_not_interpolated_into_shell(self) -> None:
        workflow = WORKFLOW.read_text()
        self.assertIn("RAW_PACKET_INPUT: ${{ inputs.packet }}", workflow)
        self.assertNotIn('"${{ github.event.inputs.packet', workflow)
        self.assertNotIn('"${{ inputs.packet }}"', workflow)
        self.assertIn('--packet "$P0PGR_PACKET_PATH"', workflow)

    def test_actions_are_pinned_to_verified_full_shas(self) -> None:
        workflow = WORKFLOW.read_text()
        uses = re.findall(r"uses:\s+([^@\s]+)@([^\s#]+)", workflow)
        self.assertEqual(dict(uses), EXPECTED_ACTION_PINS)
        for _, sha in uses:
            self.assertRegex(sha, FULL_SHA)
        pins = json.loads(PINS.read_text())["pins"]
        self.assertEqual(
            {pin["action"]: pin["commit_sha"] for pin in pins},
            EXPECTED_ACTION_PINS,
        )
        self.assertTrue(all(pin["commit_signature_verified"] for pin in pins))
        self.assertIn("persist-credentials: false", workflow)

    def test_workflow_remains_manual_shadow_only(self) -> None:
        workflow = WORKFLOW.read_text()
        active_lines = [
            line.strip()
            for line in workflow.splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        active = "\n".join(active_lines)
        self.assertIn("workflow_dispatch:", active)
        self.assertNotIn("schedule:", active)
        self.assertNotIn("pull_request:", active)
        self.assertNotIn("push:", active)
        for forbidden in ("git push", "gh pr merge", "wrangler deploy", "curl -X POST"):
            self.assertNotIn(forbidden, active)


if __name__ == "__main__":
    unittest.main()
