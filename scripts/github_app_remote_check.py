#!/usr/bin/env python3
import argparse
import base64
import hashlib
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from gates.cf_tokens import load_cloudflare_tokens

load_cloudflare_tokens()

APP_ID = "4179901"
INSTALLATION_ID = "143449507"
OWNER = "kazemnezhadsina144-dot"
REPO = "sina-governance-SSOT"
BRANCH = "main"
SSOT_PATH = "ssot/strategy-ssot-v6-split.md"
PEM_PATH = Path("~/.sina/secrets/sina-governance-ssot.github-app.private-key.pem").expanduser()
EXPECTED_SHA256 = "1ba4a793dba183388afd244ea21e850cad879c78824f78603e961070ae9b3af4"
API_BASE = "https://api.github.com"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign_with_openssl(payload: bytes, pem_path: Path) -> bytes:
    result = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(pem_path)],
        input=payload,
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        error = result.stderr.decode(errors="replace").strip() or "openssl signing failed"
        raise RuntimeError(error)
    return result.stdout


def create_jwt(pem_path: Path) -> str:
    if not pem_path.exists():
        raise RuntimeError(f"private key not found: {pem_path}")

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": APP_ID,
    }
    signing_input = f"{b64url(json.dumps(header, separators=(',', ':')).encode())}.{b64url(json.dumps(claims, separators=(',', ':')).encode())}".encode(
        "ascii"
    )
    signature = sign_with_openssl(signing_input, pem_path)
    return f"{signing_input.decode('ascii')}.{b64url(signature)}"


def github_request(method: str, path: str, *, token: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        f"{API_BASE}{path}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "sina-governance-remote-check",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API {method} {path} failed: HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"GitHub API {method} {path} failed: {exc.reason}") from exc


def installation_token(jwt: str) -> str:
    response = github_request("POST", f"/app/installations/{INSTALLATION_ID}/access_tokens", token=jwt, body={})
    token = response.get("token")
    if not isinstance(token, str) or not token:
        raise RuntimeError("GitHub installation token response did not include token")
    return token


def read_remote_head(token: str) -> str:
    response = github_request("GET", f"/repos/{OWNER}/{REPO}/git/ref/heads/{BRANCH}", token=token)
    obj = response.get("object")
    if not isinstance(obj, dict):
        raise RuntimeError("GitHub ref response did not include object")
    sha = obj.get("sha")
    if not isinstance(sha, str) or not sha:
        raise RuntimeError("GitHub ref response did not include object.sha")
    return sha


def read_remote_file(token: str) -> bytes:
    response = github_request("GET", f"/repos/{OWNER}/{REPO}/contents/{SSOT_PATH}?ref={BRANCH}", token=token)
    encoding = response.get("encoding")
    content = response.get("content")
    if encoding != "base64" or not isinstance(content, str):
        raise RuntimeError("GitHub contents response did not include base64 content")
    return base64.b64decode(content)


def build_report() -> tuple[dict[str, Any], int]:
    failures: list[str] = []
    report: dict[str, Any] = {
        "status": "FAIL",
        "repo": f"{OWNER}/{REPO}",
        "branch": BRANCH,
        "ssot_path": SSOT_PATH,
        "remote_head": None,
        "expected_sha256": EXPECTED_SHA256,
        "remote_ssot_sha256": None,
        "credential": "github_app_installation_token",
        "app_id": APP_ID,
        "installation_id": INSTALLATION_ID,
        "failures": failures,
    }

    try:
        jwt = create_jwt(PEM_PATH)
        token = installation_token(jwt)
        report["remote_head"] = read_remote_head(token)
        content = read_remote_file(token)
        actual_sha256 = hashlib.sha256(content).hexdigest()
        report["remote_ssot_sha256"] = actual_sha256
        if actual_sha256 != EXPECTED_SHA256:
            failures.append(f"SSOT SHA256 expected {EXPECTED_SHA256}, got {actual_sha256}")
    except Exception as exc:  # noqa: BLE001 - CLI reports advisory check failures uniformly.
        failures.append(str(exc))

    if not failures:
        report["status"] = "MATCH"
        return report, 0
    return report, 1


def print_text(report: dict[str, Any]) -> None:
    print(f"REMOTE_CHECK_ADVISORY: {report['status']}")
    print(f"repo: {report['repo']}")
    print(f"branch: {report['branch']}")
    print(f"remote_head: {report['remote_head']}")
    print(f"ssot_path: {report['ssot_path']}")
    print(f"expected_sha256: {report['expected_sha256']}")
    print(f"remote_ssot_sha256: {report['remote_ssot_sha256']}")
    failures = report["failures"]
    if failures:
        print("details:")
        for failure in failures:
            print(f"- {failure}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run GitHub App based remote advisory SSOT check.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report, exit_code = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text(report)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
