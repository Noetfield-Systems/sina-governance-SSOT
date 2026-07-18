#!/usr/bin/env python3
"""
Prove the identity + installation scope of the candidate App noetfield-sg-authority.

Uses the private key held in SG custody (~/.sina/secrets) to mint a short-lived App
JWT, then verifies via the GitHub API:
  - App slug == noetfield-sg-authority, owner == Noetfield-Systems
  - Permissions exactly match the authorized manifest, webhook events empty
  - Installation exists on the org, repository_selection == "selected"
  - Installed on EXACTLY the 2 authorized repos (no more, no less)

Records PUBLIC METADATA ONLY. The private key never enters the repo, chat, or logs.
On full PASS, flips data/sg_candidate_app_state_v1.json to identity PROVEN.
Never removes HOLD, enables enforcement, or commissions runtime.
"""
import base64
import glob
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

ORG = "Noetfield-Systems"
EXPECTED_SLUG = "noetfield-sg-authority"
REPO_ROOT = Path(__file__).resolve().parents[1]
KEY_PATH = Path(os.path.expanduser("~/.sina/secrets/noetfield-sg-authority.private-key.pem"))
RECEIPT_DIR = REPO_ROOT / "receipts" / "sg-candidate-app"
STATE_PATH = REPO_ROOT / "data" / "sg_candidate_app_state_v1.json"

EXPECTED_REPOS = sorted([
    "Noetfield-Systems/sina-governance-SSOT",
    "Noetfield-Systems/noetfield-sandbox-private",
])
EXPECTED_PERMISSIONS = {
    "metadata": "read",
    "contents": "read",
    "pull_requests": "read",
    "actions": "read",
    "checks": "write",
    "statuses": "write",
}


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def latest_app_id() -> int:
    files = sorted(glob.glob(str(RECEIPT_DIR / "creation_*.json")))
    if not files:
        die("No creation receipt found. Run bootstrap first.")
    with open(files[-1]) as f:
        rec = json.load(f)
    app_id = (rec.get("app") or {}).get("id")
    if not app_id:
        die("Creation receipt missing app id.")
    return int(app_id)


def make_jwt(app_id: int) -> str:
    if not KEY_PATH.exists():
        die(f"Custody key not found at {KEY_PATH}. Run bootstrap creation first.")
    header = {"alg": "RS256", "typ": "JWT"}
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": app_id}
    signing_input = f"{b64url(json.dumps(header).encode())}.{b64url(json.dumps(payload).encode())}"
    proc = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", str(KEY_PATH)],
        input=signing_input.encode(),
        capture_output=True,
    )
    if proc.returncode != 0:
        die(f"openssl signing failed: {proc.stderr.decode()}")
    return f"{signing_input}.{b64url(proc.stdout)}"


def api(url: str, token: str, method: str = "GET") -> dict:
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "noetfield-sg-candidate-prove")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def die(msg: str):
    print(f"[prove] BLOCKED: {msg}", file=sys.stderr)
    sys.exit(2)


def main():
    app_id = latest_app_id()
    jwt = make_jwt(app_id)
    checks = []

    def check(name, ok, detail=""):
        checks.append({"check": name, "pass": bool(ok), "detail": detail})
        print(f"[prove] {'PASS' if ok else 'FAIL'} {name} {detail}")

    app = api("https://api.github.com/app", jwt)
    check("app_slug", app.get("slug") == EXPECTED_SLUG, f"got={app.get('slug')}")
    check("owner_login", (app.get("owner") or {}).get("login") == ORG, f"got={(app.get('owner') or {}).get('login')}")
    perms = app.get("permissions") or {}
    check("permissions_exact", perms == EXPECTED_PERMISSIONS, f"got={json.dumps(perms, sort_keys=True)}")
    check("events_empty", not app.get("events"), f"got={app.get('events')}")

    installation = api(f"https://api.github.com/orgs/{ORG}/installation", jwt)
    inst_id = installation.get("id")
    check("installation_exists", bool(inst_id), f"id={inst_id}")
    check(
        "installation_selected",
        installation.get("repository_selection") == "selected",
        f"got={installation.get('repository_selection')}",
    )

    tok = api(
        f"https://api.github.com/app/installations/{inst_id}/access_tokens", jwt, method="POST"
    )
    inst_token = tok.get("token")
    repos_resp = api("https://api.github.com/installation/repositories", inst_token)
    installed = sorted(r.get("full_name") for r in repos_resp.get("repositories", []))
    check("repos_exact", installed == EXPECTED_REPOS, f"got={installed}")

    all_pass = all(c["pass"] for c in checks)
    fingerprint = hashlib.sha256(KEY_PATH.read_bytes()).hexdigest()
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    proof = {
        "receipt_type": "sg_candidate_app_identity_proof_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_metadata_only": True,
        "verdict": "PROVEN" if all_pass else "NOT_PROVEN",
        "app": {
            "id": app.get("id"),
            "slug": app.get("slug"),
            "node_id": app.get("node_id"),
            "html_url": app.get("html_url"),
            "owner_login": (app.get("owner") or {}).get("login"),
            "permissions": perms,
            "events": app.get("events"),
        },
        "installation": {
            "id": inst_id,
            "repository_selection": installation.get("repository_selection"),
            "repositories": installed,
        },
        "expected_repositories": EXPECTED_REPOS,
        "private_key_fingerprint_sha256": fingerprint,
        "checks": checks,
        "runtime_state": {
            "SG_CANDIDATE_APP": "CREATED",
            "SG_CANDIDATE_IDENTITY": "PROVEN" if all_pass else "NOT_PROVEN",
            "SG_RUNTIME": "NOT_COMMISSIONED",
            "SG_ENFORCEMENT": "NOT_ENABLED",
            "AUTONOMOUS_PRODUCTION_MUTATIONS": "HOLD",
        },
    }
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    out = RECEIPT_DIR / f"identity_proof_{ts}.json"
    with open(out, "w") as f:
        json.dump(proof, f, indent=2)
        f.write("\n")
    print(f"[prove] receipt={out}")

    if all_pass:
        state = json.loads(STATE_PATH.read_text()) if STATE_PATH.exists() else {}
        state["SG_CANDIDATE_APP"] = "CREATED"
        state["SG_CANDIDATE_IDENTITY"] = "PROVEN"
        state["SG_RUNTIME"] = "NOT_COMMISSIONED"
        state["SG_ENFORCEMENT"] = "NOT_ENABLED"
        state["AUTONOMOUS_PRODUCTION_MUTATIONS"] = "HOLD"
        state["app_id"] = app.get("id")
        state["app_slug"] = app.get("slug")
        state["installation_id"] = inst_id
        state["proven_at_utc"] = datetime.now(timezone.utc).isoformat()
        state["latest_proof_receipt"] = out.name
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n")
        print("[prove] IDENTITY_PROVEN")
    else:
        print("[prove] IDENTITY_NOT_PROVEN")
        sys.exit(1)


if __name__ == "__main__":
    main()
