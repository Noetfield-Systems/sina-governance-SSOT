from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from gates import promotion_gate

ROOT = Path(__file__).resolve().parents[1]


class SGAuthorityContainmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.reality = json.loads((ROOT / "data/runtime_reality_v1.json").read_text())

    def test_runtime_reality_is_fail_closed(self) -> None:
        self.assertEqual(self.reality["authority"]["containment"], "ENFORCED")
        self.assertEqual(self.reality["authority"]["autonomous_production_mutations"], "HOLD")
        self.assertIn(
            self.reality["authority"]["system_status"],
            {"BLOCKED_NOT_COMMISSIONED", "SCOPED_LIVE_T0_AUTHORIZED", "LIVE_WIRED_T0", "COMMISSIONED_T0_PROVEN"},
        )
        self.assertIn(
            self.reality["sg"]["runtime_status"],
            {"NOT_COMMISSIONED", "LIVE_WIRED_T0", "COMMISSIONED_T0_PROVEN"},
        )
        self.assertIn(
            self.reality["sg"]["replacement_status"],
            {"NOT_YET_COMMISSIONED", "SHADOW_LANDED", "LIVE_WIRED_T0"},
        )
        self.assertIn(
            self.reality["unified_motor"]["runtime_status"],
            {"NOT_COMMISSIONED", "LIVE_WIRED_T0", "COMMISSIONED_T0_PROVEN"},
        )
        if self.reality["unified_motor"]["runtime_status"] in {"LIVE_WIRED_T0", "COMMISSIONED_T0_PROVEN"}:
            self.assertTrue(self.reality["unified_motor"]["active"])
        else:
            self.assertFalse(self.reality["unified_motor"]["active"])
        directive = self.reality["commissioning_directive"]
        self.assertIn(directive["unified_motor_runtime"], {"NOT_COMMISSIONED", "COMMISSIONED_T0"})
        self.assertFalse(directive["fully_commissioned_claim"])
        reasons = promotion_gate.runtime_authority_refusal_reasons()
        self.assertTrue(reasons)
        self.assertTrue(any("HOLD" in reason for reason in reasons))

    def test_two_disjoint_security_principals(self) -> None:
        principals = self.reality["security_principals"]
        self.assertEqual(principals["motor_execution_app_count"], 1)
        self.assertEqual(principals["sg_authority_app_count"], 1)
        self.assertEqual(principals["total_required"], 2)
        self.assertTrue(principals["credentials_disjoint"])
        self.assertFalse(principals["motor_may_issue_sg_decisions"])
        self.assertFalse(principals["sg_may_execute_mutations"])
        self.assertFalse(self.reality["noetfield_motor_app"]["is_sg_authority"])

    def _args(self) -> SimpleNamespace:
        return SimpleNamespace(
            expected_cf_account_id="secondary",
            expected_candidate_ref="abc",
            expected_candidate_path="artifact.json",
            expected_candidate_sha256="a" * 64,
            expected_worker_code_sha256=None,
            expected_knowledge_bundle_sha256=None,
        )

    def _pass_receipt(self) -> dict:
        return {
            "receipt_type": "SG_DECISION",
            "status": "PASS",
            "result": "PASS",
            "verdict": "PASS",
            "pass_claimed": True,
            "edge_execution_proven": True,
            "secondary_account_proven": True,
            "cf_account_id": "secondary",
            "candidate_ref": "abc",
            "candidate_path": "artifact.json",
            "candidate_sha256": "a" * 64,
            "candidate_validation_failures": [],
            "failures": [],
            "artifact_type": "knowledge_bundle",
        }

    def test_legacy_advisory_identity_is_unconditionally_denied(self) -> None:
        receipt = self._pass_receipt()
        receipt.update({
            "receipt_type": "REMOTE_CHECK_ADVISORY",
            "app_id": "4179901",
            "installation_id": "143449507",
            "repo": "kazemnezhadsina144-dot/sina-governance-SSOT",
        })
        reasons = promotion_gate.refusal_reasons(receipt, self._args())
        joined = "\n".join(reasons)
        self.assertIn("REMOTE_CHECK_ADVISORY", joined)
        self.assertIn("4179901", joined)
        self.assertIn("143449507", joined)
        self.assertIn("personal repository", joined)

    def test_non_pass_verdicts_deny(self) -> None:
        for verdict in ("FAIL", "BLOCKED", "ESCALATE_REQUIRED"):
            receipt = self._pass_receipt()
            receipt.update({"status": verdict, "result": verdict, "verdict": verdict, "pass_claimed": False})
            self.assertTrue(promotion_gate.refusal_reasons(receipt, self._args()), verdict)

    def test_motor_executor_cannot_spoof_sg_decision(self) -> None:
        receipt = self._pass_receipt()
        receipt["app_id"] = "4275961"
        reasons = promotion_gate.refusal_reasons(receipt, self._args())
        self.assertTrue(any("Motor executor" in reason for reason in reasons))

    def test_missing_exact_pass_verdict_denies(self) -> None:
        receipt = self._pass_receipt()
        receipt.pop("verdict")
        reasons = promotion_gate.refusal_reasons(receipt, self._args())
        self.assertTrue(any("verdict" in reason for reason in reasons))

    def test_secret_presence_cannot_enable_autonomy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            env = os.environ.copy()
            env.update({
                "HOME": tmp,
                "CF_MAIN_TOKEN": "present-but-not-authority",
                "CF_VERIFIER_TOKEN": "present-but-not-authority",
                "BRAIN_CI_AUTONOMOUS": "1",
                "BRAIN_RECEIPT_DIR": str(Path(tmp) / "receipts"),
            })
            result = subprocess.run(
                ["bash", str(ROOT / "scripts/brain_loop_autorun_v1.sh")],
                cwd=ROOT, env=env, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 78, result.stdout + result.stderr)
            self.assertIn("BLOCKED_SG_NOT_COMMISSIONED", result.stdout)
            receipt_path = next((Path(tmp) / "receipts").glob("brain-loop-autorun-*.json"))
            receipt = json.loads(receipt_path.read_text())
            self.assertFalse(receipt["production_mutation_authorized"])
            self.assertTrue(receipt["token_presence_ignored"])

    def test_promote_script_never_reaches_deploy(self) -> None:
        env = os.environ.copy()
        env.update({"CF_MAIN_TOKEN": "present", "CF_VERIFIER_TOKEN": "present"})
        result = subprocess.run(
            ["bash", str(ROOT / "scripts/promote_brain_worker_v1.sh"), "--autonomous-deploy"],
            cwd=ROOT, env=env, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 78)
        self.assertIn("BLOCKED_SG_NOT_COMMISSIONED", result.stdout)
        self.assertIn("deploy_executed: false", result.stdout)

    def test_installer_cannot_erase_or_bypass_hold(self) -> None:
        script = (ROOT / "scripts/install_brain_loop_launchd_v1.sh").read_text()
        self.assertNotIn('rm -f "${HOME}/.sina/enforcement/brain-autonomous-hold-v1.flag"', script)
        with tempfile.TemporaryDirectory() as tmp:
            hold = Path(tmp) / ".sina/enforcement/brain-autonomous-hold-v1.flag"
            hold.parent.mkdir(parents=True)
            hold.write_text("HOLD\n")
            env = os.environ.copy()
            env["HOME"] = tmp
            result = subprocess.run(
                ["bash", str(ROOT / "scripts/install_brain_loop_launchd_v1.sh")],
                cwd=ROOT, env=env, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 78)
            self.assertTrue(hold.exists())
            self.assertIn("BLOCKED_GOVERNANCE_HOLD", result.stderr)

    def test_workflow_is_manual_observe_only_without_secret_authority(self) -> None:
        workflow = (ROOT / ".github/workflows/brain-loop-autorun-v1.yml").read_text()
        self.assertNotIn("schedule:", workflow)
        self.assertNotIn("BRAIN_CI_AUTONOMOUS", workflow)
        self.assertNotIn("CF_MAIN_TOKEN", workflow)
        self.assertNotIn("CF_VERIFIER_TOKEN", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn('SG_OBSERVE_ONLY: "1"', workflow)


if __name__ == "__main__":
    unittest.main()
