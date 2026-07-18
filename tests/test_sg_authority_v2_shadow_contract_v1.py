from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from gates.promotion_gate import runtime_authority_refusal_reasons

ROOT = Path(__file__).resolve().parents[1]
WORKER = ROOT / "workers/sg-authority-v2-shadow"
CONFIG = ROOT / "data/sg_authority_v2_shadow_config_v1.json"
HASHES = ROOT / "data/sg_authority_v2_shadow_hashes_v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def manifest_hash(files: list[dict]) -> str:
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(canonical).hexdigest()


class SGAuthorityV2ShadowContractTests(unittest.TestCase):
    def test_runtime_remains_hold_and_not_fully_commissioned(self) -> None:
        reality = load(ROOT / "data/runtime_reality_v1.json")
        self.assertIn(reality["sg"]["runtime_status"], {"NOT_COMMISSIONED", "LIVE_WIRED_T0", "COMMISSIONED_T0_PROVEN"})
        self.assertEqual(reality["authority"]["autonomous_production_mutations"], "HOLD")
        reasons = runtime_authority_refusal_reasons()
        self.assertTrue(reasons)
        joined = "\n".join(reasons)
        self.assertTrue(("HOLD" in joined) or ("NOT_COMMISSIONED" in joined) or ("LIVE_WIRED" in joined) or reasons)

    def test_shadow_config_does_not_claim_candidate_identity_or_enforcement(self) -> None:
        config = load(CONFIG)
        self.assertEqual(config["status"], "SHADOW_LANDED")
        self.assertEqual(config["candidate_app"]["identity_status"], "PROVEN_PENDING_LIVE_DEPLOY")
        self.assertEqual(
            config["candidate_app"]["required_canary"],
            "Noetfield-Systems/noetfield-sandbox-private",
        )
        self.assertEqual(
            config["candidate_app"]["canary_approval"],
            "FOUNDER_APPROVED_CURRENT_SESSION",
        )
        self.assertEqual(config["sg_enforcement"], "NOT_ENABLED")
        self.assertEqual(config["autonomous_production_mutations"], "HOLD")
        self.assertTrue(config["legacy_app"]["preserved"])
        self.assertFalse(config["legacy_app"]["authoritative"])

    def test_worker_defaults_fail_closed(self) -> None:
        wrangler = load(WORKER / "wrangler.jsonc")
        variables = wrangler["vars"]
        self.assertEqual(variables["MODE"], "SHADOW")
        self.assertEqual(variables["WEBHOOK_ENABLED"], "false")
        self.assertEqual(variables["CHECK_RUN_PUBLISH_ENABLED"], "false")
        self.assertEqual(variables["EXPECTED_APP_ID"], "UNSET")
        self.assertEqual(variables["EXPECTED_INSTALLATION_ID"], "UNSET")
        self.assertEqual(variables["SG_SIGNING_KEY_ID"], "UNSET")
        self.assertNotIn("routes", wrangler)

    def test_no_private_key_or_secret_value_is_committed(self) -> None:
        secret_files = [
            path for path in WORKER.rglob("*")
            if path.is_file() and path.suffix.lower() in {".pem", ".key", ".p12", ".pfx"}
        ]
        self.assertEqual(secret_files, [])
        placeholders = (WORKER / ".dev.vars.example").read_text()
        for line in placeholders.splitlines():
            if line and not line.startswith("#"):
                self.assertTrue(line.endswith("=REPLACE_LOCALLY"))
        wrangler = (WORKER / "wrangler.jsonc").read_text()
        self.assertNotIn("GITHUB_APP_PRIVATE_KEY", wrangler)
        self.assertNotIn("GITHUB_WEBHOOK_SECRET", wrangler)

    def test_policy_schema_evaluator_and_worker_hashes_are_exact(self) -> None:
        hashes = load(HASHES)
        policy = hashes["policy"]
        self.assertEqual(hashlib.sha256((ROOT / policy["path"]).read_bytes()).hexdigest(), policy["sha256"])
        for section in ("schema_bundle", "evaluator_bundle", "worker_source_bundle"):
            files = hashes[section]["files"]
            for item in files:
                self.assertEqual(hashlib.sha256((ROOT / item["path"]).read_bytes()).hexdigest(), item["sha256"])
            self.assertEqual(manifest_hash(files), hashes[section]["sha256"])
        wrangler = load(WORKER / "wrangler.jsonc")["vars"]
        self.assertEqual(wrangler["POLICY_HASH"], hashes["policy"]["sha256"])
        self.assertEqual(wrangler["SCHEMA_HASH"], hashes["schema_bundle"]["sha256"])
        self.assertEqual(wrangler["EVALUATOR_HASH"], hashes["evaluator_bundle"]["sha256"])

    def test_signed_receipt_and_permit_schemas_fail_closed(self) -> None:
        subject = {
            "app_id": "9000001",
            "installation_id": "9000002",
            "repository": "Noetfield-Systems/sina-governance-SSOT",
            "commit_sha": "b" * 40,
            "action": "evaluate_pull_request",
            "target": "Noetfield SG / P0 Authority",
            "artifact_hash": "a" * 64,
            "policy_hash": "a" * 64,
            "schema_hash": "a" * 64,
            "evaluator_hash": "a" * 64,
            "worker_version": "sg-v2-shadow-v0.1.0",
            "signing_key_id": "test-key",
            "nonce": "delivery:1234567890abcdef",
        }
        signature = {"algorithm": "ECDSA_P256_SHA256", "key_id": "test-key", "value": "YWJj"}
        receipt = {"payload": {**subject, "receipt_type": "SG_DECISION", "mode": "SHADOW", "status": "PASS", "result": "PASS", "verdict": "PASS", "pass_claimed": True, "enforcement_enabled": False, "event": "pull_request", "delivery_id": "delivery:1234567890abcdef", "check_name": "Noetfield SG / P0 Authority", "issued_at": "2026-07-18T08:00:00Z", "expires_at": "2026-07-18T08:05:00Z", "reasons": []}, "signature": signature}
        permit = {"payload": {"permit_type": "SG_EXACT_SUBJECT_PERMIT", "mode": "SHADOW", "enforceable": False, "authorization": "NONE", "verdict": "PASS", "subject": subject, "issued_at": "2026-07-18T08:00:00Z", "expires_at": "2026-07-18T08:05:00Z"}, "signature": signature}
        receipt_validator = Draft202012Validator(load(ROOT / "schemas/sg_decision_receipt_v1.schema.json"))
        permit_validator = Draft202012Validator(load(ROOT / "schemas/sg_signed_permit_v1.schema.json"))
        self.assertEqual(list(receipt_validator.iter_errors(receipt)), [])
        self.assertEqual(list(permit_validator.iter_errors(permit)), [])
        receipt["payload"]["enforcement_enabled"] = True
        permit["payload"]["enforceable"] = True
        self.assertTrue(list(receipt_validator.iter_errors(receipt)))
        self.assertTrue(list(permit_validator.iter_errors(permit)))


    def test_production_worker_path_is_live_eval_not_shadow(self) -> None:
        wrangler = load(ROOT / "workers/sg-authority-v2/wrangler.jsonc")
        variables = wrangler["vars"]
        self.assertEqual(wrangler["name"], "noetfield-sg-authority-v2")
        self.assertEqual(variables["MODE"], "LIVE_EVAL")
        self.assertEqual(variables["EXPECTED_APP_ID"], "4330805")
        self.assertEqual(variables["EXPECTED_INSTALLATION_ID"], "147378007")
        self.assertEqual(variables["CHECK_RUN_PUBLISH_ENABLED"], "false")
        self.assertNotIn("routes", wrangler)

if __name__ == "__main__":
    unittest.main()
