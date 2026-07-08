"""Tests for verify_auth_surfaces_e2e_v1.py v1.1."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_auth_surfaces_e2e_v1 import (  # noqa: E402
    check_surface,
    is_auth_redirect,
    lint_redirect_allow_list,
    load_matrix,
    run_probe,
)


class AuthSurfaceProbeTests(unittest.TestCase):
    def test_matrix_loads(self) -> None:
        matrix = load_matrix()
        self.assertEqual(matrix["schema"], "auth_surface_matrix_v1")
        self.assertEqual(matrix["version"], "1.1.0")
        self.assertIn("tier_0_public", matrix["tiers"])

    def test_is_auth_redirect(self) -> None:
        self.assertTrue(is_auth_redirect("https://x.com/auth/sign-in"))
        self.assertFalse(is_auth_redirect("https://x.com/pricing"))

    def test_tier0_pass_on_200(self) -> None:
        spec = {"id": "x", "url": "https://example.com", "expect_http": [200]}
        with patch("verify_auth_surfaces_e2e_v1.http_probe", return_value={"http": 200}):
            row = check_surface(spec, tier="tier_0_public")
        self.assertEqual(row["status"], "PASS")

    def test_tier0_fail_on_404(self) -> None:
        spec = {"id": "x", "url": "https://example.com", "expect_http": [200]}
        with patch("verify_auth_surfaces_e2e_v1.http_probe", return_value={"http": 404}):
            row = check_surface(spec, tier="tier_0_public")
        self.assertEqual(row["status"], "FAIL")

    def test_tier0_fail_login_wall(self) -> None:
        spec = {
            "id": "x",
            "url": "https://example.com",
            "expect_http": [200],
            "must_not_redirect_to_auth": True,
        }
        with patch(
            "verify_auth_surfaces_e2e_v1.http_probe",
            return_value={"http": 302, "location": "https://example.com/sign-in"},
        ):
            row = check_surface(spec, tier="tier_0_public")
        self.assertEqual(row["status"], "FAIL")

    def test_tier2_planned_warns_on_public_200(self) -> None:
        spec = {
            "id": "gate",
            "url": "https://example.com/gated",
            "implementation": "planned",
            "warn_if_public_200": True,
            "expect_when_gated": [401, 302],
        }
        with patch("verify_auth_surfaces_e2e_v1.http_probe", return_value={"http": 200}):
            row = check_surface(spec, tier="tier_2_gated")
        self.assertEqual(row["status"], "WARN")

    def test_tier2_live_fails_on_public_200(self) -> None:
        spec = {
            "id": "gate",
            "url": "https://example.com/gated",
            "implementation": "live",
            "expect_when_gated": [401, 302],
        }
        with patch("verify_auth_surfaces_e2e_v1.http_probe", return_value={"http": 200}):
            row = check_surface(spec, tier="tier_2_gated")
        self.assertEqual(row["status"], "FAIL")

    def test_redirect_allow_list_lint_pass(self) -> None:
        ok = lint_redirect_allow_list(
            {
                "supabase_redirect_allow_list": [
                    "https://sourcea.app/auth/callback",
                    "http://localhost:3000/auth/callback",
                ]
            }
        )
        self.assertEqual(ok["status"], "PASS")

    def test_redirect_allow_list_lint_fail(self) -> None:
        bad = lint_redirect_allow_list({"supabase_redirect_allow_list": ["ftp://bad"]})
        self.assertEqual(bad["status"], "FAIL")

    def test_fail_on_warn_exit_code(self) -> None:
        with patch("verify_auth_surfaces_e2e_v1.load_matrix") as lm:
            lm.return_value = {
                "tiers": {
                    "tier_0_public": {
                        "surfaces": [{"id": "a", "url": "https://a.com", "expect_http": [200]}]
                    },
                    "tier_1_optional": {"surfaces": []},
                    "tier_2_gated": {"surfaces": []},
                    "tier_3_api": {"surfaces": []},
                },
                "supabase_redirect_allow_list": ["https://sourcea.app/auth/callback"],
                "repo_ownership": {},
                "founder_decisions_pending": [],
            }
            with patch("verify_auth_surfaces_e2e_v1.http_probe", return_value={"http": 200}):
                with patch("verify_auth_surfaces_e2e_v1.run_supabase_subprobe", return_value={"status": "WARN"}):
                    _, code = run_probe(write_receipt=False, emit_json=False, fail_on_warn=True)
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
