"""Tests for verify_auth_surfaces_e2e_v1.py."""
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
    lint_redirect_allow_list,
    load_matrix,
)


class AuthSurfaceProbeTests(unittest.TestCase):
    def test_matrix_loads(self) -> None:
        matrix = load_matrix()
        self.assertEqual(matrix["schema"], "auth_surface_matrix_v1")
        self.assertIn("tier_0_public", matrix["tiers"])

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

    def test_redirect_allow_list_lint(self) -> None:
        ok = lint_redirect_allow_list({"supabase_redirect_allow_list": ["https://a.com/cb"]})
        self.assertEqual(ok["status"], "PASS")
        bad = lint_redirect_allow_list({"supabase_redirect_allow_list": ["ftp://bad"]})
        self.assertEqual(bad["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
