#!/usr/bin/env python3
"""CHESS v2.0 package — CLI and install smoke tests."""
from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "SG-Canonical-Library/noetfield-library"
CLI = ROOT / "scripts/chess_pass_cli_v1.py"


def _run_cli(payload: dict) -> dict:
    proc = subprocess.run(
        ["python3", str(CLI)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
        cwd=str(ROOT),
    )
    return json.loads(proc.stdout)


class ChessPassCliTests(unittest.TestCase):
    def test_risky_wording_proceed_with_patch(self) -> None:
        out = _run_cli({"raw_move": "clean up and simplify the header"})
        self.assertEqual(out["action"], "PROCEED_WITH_PATCH")
        self.assertTrue(out["likely_misread"])

    def test_benign_proceed(self) -> None:
        out = _run_cli({"raw_move": "fix typo in footer copyright year"})
        self.assertEqual(out["action"], "PROCEED")

    def test_irreversible_hint(self) -> None:
        out = _run_cli({"raw_move": "delete the admin review panel"})
        self.assertEqual(out["action"], "ASK_IF_IRREVERSIBLE")

    def test_sample_example_matches_schema_required(self) -> None:
        schema = json.loads((LIB / "SCHEMAS/chess_pass.schema.json").read_text())
        sample = json.loads((LIB / "EXAMPLES/sample_chess_pass.json").read_text())
        for key in schema["required"]:
            self.assertIn(key, sample)

    def test_manifest_files_on_disk(self) -> None:
        manifest = json.loads((ROOT / "data/chess_pattern_reasoning_machine_v2_manifest.json").read_text())
        for rel in manifest["files"]:
            if rel.startswith("TOOLS/"):
                self.assertTrue(CLI.is_file(), rel)
            elif rel in ("README.md",) or rel.startswith("INSTALL/"):
                self.assertTrue((LIB / "CHESS-v2" / rel).is_file(), rel)
            else:
                self.assertTrue((LIB / rel).is_file(), rel)


if __name__ == "__main__":
    unittest.main()
