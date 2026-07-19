from __future__ import annotations

import copy
import unittest
from pathlib import Path

from scripts.site_flow_canaries_receipt_v1 import (
    IDEMPOTENCY_KEY,
    ReceiptValidationError,
    SOURCE_REPOSITORY,
    finalize_receipt,
    receipt_sha256,
    validate_enriched_receipt,
)

ROOT = Path(__file__).resolve().parents[1]


def base_receipt() -> dict:
    return {
        "schema": "site_flow_canaries_v1",
        "generated_at": "2026-07-19T00:00:00Z",
        "mode": "synthetic",
        "flows": [
            {"site_flow": "sourceb.workspace"},
            {"site_flow": "noetfield.enterprise_intake"},
            {"site_flow": "trustfield.evidence_assessment"},
        ],
        "metrics": {
            "duplicate_executions": 0,
            "idle_llm_calls": 0,
            "customer_visible_failures": 0,
            "flows_proven_synthetic": 3,
        },
        "errors": [],
        "verdict": "PASS_SYNTHETIC_CANARIES",
    }


class ReceiptContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.enriched = finalize_receipt(
            base_receipt(),
            source_sha="a" * 40,
            run_url=(
                "https://github.com/Noetfield-Systems/"
                "sina-governance-SSOT/actions/runs/123"
            ),
        )

    def test_finalize_seals_the_fixed_envelope(self) -> None:
        validate_enriched_receipt(self.enriched)
        self.assertEqual(self.enriched["work_order_id"], "wo.e2e_activation")
        self.assertEqual(self.enriched["work_order_version"], "v1")
        self.assertEqual(self.enriched["idempotency_key"], IDEMPOTENCY_KEY)
        self.assertEqual(self.enriched["source_repository"], SOURCE_REPOSITORY)
        self.assertEqual(self.enriched["receipt_sha256"], receipt_sha256(self.enriched))

    def test_tampered_receipt_fails_closed(self) -> None:
        tampered = copy.deepcopy(self.enriched)
        tampered["metrics"]["idle_llm_calls"] = 1
        with self.assertRaises(ReceiptValidationError):
            validate_enriched_receipt(tampered)

    def test_mismatched_idempotency_key_fails_closed(self) -> None:
        mismatched = dict(self.enriched)
        mismatched["idempotency_key"] = "wo.e2e_activation:v2"
        mismatched["receipt_sha256"] = receipt_sha256(mismatched)
        with self.assertRaises(ReceiptValidationError):
            validate_enriched_receipt(mismatched)

    def test_mismatched_source_repository_fails_closed(self) -> None:
        mismatched = dict(self.enriched)
        mismatched["source_repository"] = "Noetfield-Systems/other"
        mismatched["receipt_sha256"] = receipt_sha256(mismatched)
        with self.assertRaises(ReceiptValidationError):
            validate_enriched_receipt(mismatched)


class WorkflowBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.workflow = (
            ROOT / ".github" / "workflows" / "site-flow-canaries-executor-v1.yml"
        ).read_text(encoding="utf-8")

    def test_workflow_is_dispatch_only_and_non_cancelling(self) -> None:
        self.assertEqual(self.workflow.count("workflow_dispatch:"), 1)
        self.assertNotIn("repository_dispatch:", self.workflow)
        self.assertNotIn("schedule:", self.workflow)
        self.assertNotIn("pull_request:", self.workflow)
        self.assertIn("cancel-in-progress: false", self.workflow)

    def test_workflow_has_read_only_repository_permissions(self) -> None:
        self.assertIn("permissions:\n  contents: read", self.workflow)
        self.assertNotIn("contents: write", self.workflow)

    def test_workflow_has_only_the_fixed_business_command(self) -> None:
        command = "python3 scripts/prove_site_flow_canaries_v1.py"
        self.assertEqual(self.workflow.count(command), 1)
        self.assertIn("WORK_ORDER_ID: wo.e2e_activation", self.workflow)
        self.assertIn("WORK_ORDER_VERSION: v1", self.workflow)
        self.assertIn("IDEMPOTENCY_KEY: wo.e2e_activation:v1", self.workflow)

    def test_workflow_pins_main_account_and_exact_staging_key(self) -> None:
        self.assertIn("CLOUDFLARE_ACCOUNT_ID: 0d0b967b77e2e5535455d39ff3dae72c", self.workflow)
        self.assertIn("R2_BUCKET: noetfield-runway-results-staging", self.workflow)
        self.assertIn("R2_KEY: mrw/external/SITE_FLOW_CANARIES_V1.json", self.workflow)
        self.assertIn("secrets.CF_MAIN_TOKEN", self.workflow)
        self.assertNotIn("CF_VERIFIER", self.workflow)


if __name__ == "__main__":
    unittest.main()
