from __future__ import annotations

import copy
import unittest
from pathlib import Path

from scripts.site_flow_canaries_receipt_v1 import (
    IDEMPOTENCY_KEY,
    ReceiptValidationError,
    SOURCE_REPOSITORY,
    finalize_receipt,
    rebind_receipt,
    receipt_hmac_sha256,
    receipt_sha256,
    sign_receipt,
    validate_enriched_receipt,
)

ROOT = Path(__file__).resolve().parents[1]
HMAC_SECRET = "test-site-flow-canaries-hmac-secret-32-bytes"


def base_receipt() -> dict:
    return {
        "schema": "site_flow_canaries_v1",
        "generated_at": "2026-07-19T00:00:00Z",
        "mode": "synthetic",
        "flows": [
            {
                "site_flow": "sourceb.workspace",
                "runtime_id": "site.sourceb.workspace_completion",
                "event": "sourceb.workspace.setup_verified",
                "output_schema": "noetfield.sourceb-workspace-receipt.v0.1",
                "beneficiary": "customer.sourceb",
                "synthetic_proof": "contract_and_route_gate",
            },
            {
                "site_flow": "noetfield.enterprise_intake",
                "runtime_id": "site.noetfield.enterprise_intake",
                "event": "noetfield.enterprise_intake.received",
                "output_schema": "noetfield.enterprise-intake-qualified.v0.1",
                "beneficiary": "customer.noetfield",
                "synthetic_proof": "contract_and_route_gate",
            },
            {
                "site_flow": "trustfield.evidence_assessment",
                "runtime_id": "site.trustfield.evidence_assessment",
                "event": "trustfield.assessment.requested",
                "output_schema": "trustfield.evidence-assessment-package.v0.1",
                "beneficiary": "customer.trustfield",
                "synthetic_proof": "contract_and_route_gate",
            },
        ],
        "gates_activated": [
            "runtime_value_contract_validator",
            "governance-registry-validate-v1",
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
            generated_at="2026-07-19T00:01:00Z",
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

    def test_hmac_binds_the_exact_sealed_receipt(self) -> None:
        signed = sign_receipt(self.enriched, HMAC_SECRET)
        validate_enriched_receipt(
            signed, hmac_secret=HMAC_SECRET, require_hmac=True
        )
        self.assertEqual(
            signed["receipt_hmac_sha256"],
            receipt_hmac_sha256(signed, HMAC_SECRET),
        )

        forged = dict(signed)
        forged["receipt_hmac_sha256"] = "0" * 64
        with self.assertRaises(ReceiptValidationError):
            validate_enriched_receipt(
                forged, hmac_secret=HMAC_SECRET, require_hmac=True
            )

    def test_incomplete_flow_proof_fails_closed(self) -> None:
        incomplete = copy.deepcopy(self.enriched)
        incomplete["flows"][0].pop("event")
        incomplete["receipt_sha256"] = receipt_sha256(incomplete)
        with self.assertRaises(ReceiptValidationError):
            validate_enriched_receipt(incomplete)

    def test_unsigned_legacy_receipt_rebinds_once_to_upgrade_run(self) -> None:
        rebound = rebind_receipt(
            self.enriched,
            source_sha="b" * 40,
            run_url=(
                "https://github.com/Noetfield-Systems/"
                "sina-governance-SSOT/actions/runs/456"
            ),
        )
        self.assertEqual(rebound["source_sha"], "b" * 40)
        self.assertNotEqual(rebound["generated_at"], self.enriched["generated_at"])
        self.assertTrue(rebound["run_url"].endswith("/456"))
        self.assertNotEqual(rebound["receipt_sha256"], self.enriched["receipt_sha256"])
        self.assertNotIn("receipt_hmac_sha256", rebound)
        signed = sign_receipt(rebound, HMAC_SECRET)
        validate_enriched_receipt(
            signed, hmac_secret=HMAC_SECRET, require_hmac=True
        )

    def test_rebind_rejects_arbitrary_invalid_legacy_object(self) -> None:
        invalid = copy.deepcopy(self.enriched)
        invalid["flows"][0]["runtime_id"] = "forged.runtime"
        invalid["receipt_sha256"] = receipt_sha256(invalid)
        with self.assertRaises(ReceiptValidationError):
            rebind_receipt(
                invalid,
                source_sha="b" * 40,
                run_url=(
                    "https://github.com/Noetfield-Systems/"
                    "sina-governance-SSOT/actions/runs/456"
                ),
            )

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

    def test_workflow_authenticates_and_read_back_verifies_exact_receipt(self) -> None:
        self.assertIn("secrets.SITE_FLOW_CANARIES_HMAC_SECRET", self.workflow)
        self.assertIn("site_flow_canaries_receipt_v1.py sign", self.workflow)
        self.assertIn("--expected \"$ENRICHED_RECEIPT\"", self.workflow)
        self.assertIn("needs_hmac_upgrade=true", self.workflow)
        self.assertIn("site_flow_canaries_receipt_v1.py rebind", self.workflow)
        self.assertIn("steps.preflight.outputs.needs_hmac_upgrade == 'true'", self.workflow)
        self.assertNotIn(
            "if: steps.preflight.outputs.already_complete != 'true'\n        env:\n          CLOUDFLARE_API_TOKEN",
            self.workflow,
        )


if __name__ == "__main__":
    unittest.main()
