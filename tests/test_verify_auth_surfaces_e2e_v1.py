"""Tests for verify_auth_surfaces_e2e_v1.py v1.1."""
from __future__ import annotations

import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from verify_auth_surfaces_e2e_v1 import (  # noqa: E402
    build_summaries,
    check_surface,
    http_probe,
    is_auth_redirect,
    lint_redirect_allow_list,
    load_matrix,
    run_probe,
)


class AuthSurfaceProbeTests(unittest.TestCase):
    def test_matrix_loads(self) -> None:
        matrix = load_matrix()
        self.assertEqual(matrix["schema"], "auth_surface_matrix_v1")
        self.assertEqual(matrix["version"], "1.1.1")
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

    def test_tier0_follows_one_non_auth_redirect(self) -> None:
        spec = {
            "id": "x",
            "url": "https://example.com",
            "expect_http": [200],
            "must_not_redirect_to_auth": True,
        }
        with patch(
            "verify_auth_surfaces_e2e_v1.http_probe",
            side_effect=[
                {"http": 307, "location": "https://www.example.com/"},
                {"http": 200, "location": None},
                {"http": 200, "location": None},
            ],
        ):
            row = check_surface(spec, tier="tier_0_public")
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(row["http"], 200)

    def test_http_probe_does_not_follow_redirect_by_default(self) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                if self.path == "/public":
                    self.send_response(302)
                    self.send_header("Location", "/sign-in")
                    self.end_headers()
                else:
                    self.send_response(200)
                    self.end_headers()

            def log_message(self, *_args: object) -> None:
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = http_probe(f"http://127.0.0.1:{server.server_port}/public")
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()
        self.assertEqual(result["http"], 302)
        self.assertEqual(result["location"], "/sign-in")

    def test_http_probe_extracts_next_client_redirect(self) -> None:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                body = (
                    '<html><head><meta id="__next-page-redirect" http-equiv="refresh" '
                    'content="1;url=/auth/sign-in?next=/private"/></head></html>'
                ).encode()
                self.send_response(200)
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *_args: object) -> None:
                pass

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = http_probe(f"http://127.0.0.1:{server.server_port}/private")
        finally:
            server.shutdown()
            thread.join(timeout=2)
            server.server_close()
        self.assertEqual(result["http"], 200)
        self.assertEqual(result["client_redirect"], "/auth/sign-in?next=/private")

    def test_tier1_follows_one_canonical_redirect(self) -> None:
        spec = {"id": "register", "url": "https://example.com/register", "expect_http": [200, 302]}
        with patch(
            "verify_auth_surfaces_e2e_v1.http_probe",
            side_effect=[
                {"http": 307, "location": "https://www.example.com/register"},
                {"http": 200, "location": None},
            ],
        ):
            row = check_surface(spec, tier="tier_1_optional")
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(row["http"], 200)

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

    def test_tier2_live_passes_next_client_auth_redirect(self) -> None:
        spec = {
            "id": "gate",
            "url": "https://example.com/gated",
            "implementation": "live",
            "expect_when_gated": [401, 302, 307],
        }
        with patch(
            "verify_auth_surfaces_e2e_v1.http_probe",
            side_effect=[
                {"http": 307, "location": "/en/gated"},
                {"http": 200, "client_redirect": "/auth/sign-in?next=/gated"},
            ],
        ):
            row = check_surface(spec, tier="tier_2_gated")
        self.assertEqual(row["status"], "PASS")
        self.assertEqual(row["auth_redirect"], "/auth/sign-in?next=/gated")

    def test_tier2_locale_redirect_is_not_auth_proof(self) -> None:
        spec = {
            "id": "gate",
            "url": "https://example.com/gated",
            "implementation": "live",
            "expect_when_gated": [401, 302, 307],
        }
        with patch(
            "verify_auth_surfaces_e2e_v1.http_probe",
            side_effect=[
                {"http": 307, "location": "/en/gated"},
                {"http": 200, "client_redirect": None},
            ],
        ):
            row = check_surface(spec, tier="tier_2_gated")
        self.assertEqual(row["status"], "FAIL")

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

    def test_redirect_allow_list_rejects_non_callback_localhost(self) -> None:
        bad = lint_redirect_allow_list(
            {"supabase_redirect_allow_list": ["http://localhost:3000/anything"]}
        )
        self.assertEqual(bad["status"], "FAIL")

    def test_ratified_blockers_do_not_remain_in_next_actions(self) -> None:
        _, _, actions = build_summaries(
            [],
            {
                "repo_ownership": {"TrustField-Technologies": {"phase": 1}},
                "founder_decisions_pending": [
                    {"id": 2},
                    {"id": 3},
                    {"id": 5},
                ],
            },
        )
        self.assertTrue(any("TrustField-Technologies" in action for action in actions))
        self.assertFalse(any("ratify" in action.lower() for action in actions))

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
