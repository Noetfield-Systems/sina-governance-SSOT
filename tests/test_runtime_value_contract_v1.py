from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "data/runtime_value_contracts_v1.json"
SCHEMA = ROOT / "schemas/runtime_value_contract_v1.schema.json"
REGISTRY = ROOT / "data/github_automation_registry_v1.json"
VALIDATOR = ROOT / "scripts/validate_runtime_value_contract_v1.py"


class RuntimeValueContractTests(unittest.TestCase):
    def test_schema_validates_contracts_document(self) -> None:
        schema = json.loads(SCHEMA.read_text())
        doc = json.loads(CONTRACTS.read_text())
        Draft202012Validator(schema).validate(doc)

    def test_every_registry_motor_has_contract(self) -> None:
        registry = json.loads(REGISTRY.read_text())
        contracts = json.loads(CONTRACTS.read_text())["contracts"]
        motor_ids = {m["motor_id"] for m in registry["motors"]}
        covered = {c["motor_id"] for c in contracts}
        self.assertTrue(motor_ids.issubset(covered), sorted(motor_ids - covered))

    def test_site_flows_present(self) -> None:
        contracts = json.loads(CONTRACTS.read_text())["contracts"]
        flows = {c.get("site_flow") for c in contracts}
        self.assertIn("sourceb.workspace", flows)
        self.assertIn("noetfield.enterprise_intake", flows)
        self.assertIn("trustfield.evidence_assessment", flows)

    def test_idle_no_work_forbids_llm(self) -> None:
        contracts = json.loads(CONTRACTS.read_text())["contracts"]
        for c in contracts:
            nw = c["no_work_behavior"]
            self.assertTrue(nw["no_llm"], c["runtime_id"])
            self.assertTrue(nw["no_write"], c["runtime_id"])
            self.assertTrue(nw["no_notification"], c["runtime_id"])

    def test_validator_script_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn("PASS:", result.stdout)


if __name__ == "__main__":
    unittest.main()
