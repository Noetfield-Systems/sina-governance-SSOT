#!/usr/bin/env python3
"""
SG candidate GitHub App bootstrap (manifest flow).

Scope (founder-authorized): candidate App creation + private-key custody only.
NOT authorized here: SG commissioning, production ruleset enforcement, Motor
production permits, HOLD removal, legacy App revocation.

Flow:
  1. Serves a localhost page that POSTs an exact-permission App manifest to the
     Noetfield-Systems org "new App" page.
  2. Founder confirms "Create GitHub App" in the browser (the only interactive step).
  3. GitHub redirects to the localhost callback with a one-time code.
  4. This script converts the code -> App credentials, writes the PRIVATE KEY and
     webhook/client secrets ONLY to the SG custody dir (~/.sina/secrets, 0600),
     and writes a repo receipt containing PUBLIC METADATA ONLY (no secrets).

The private key never enters the repo, chat, or logs. Only its SHA256 fingerprint
is recorded.
"""
import hashlib
import json
import os
import secrets
import sys
import urllib.request
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ORG = "noetfield-systems".replace("noetfield-systems", "Noetfield-Systems")
HOST = "127.0.0.1"
PORT = 8737
REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "data" / "sg_candidate_app_manifest_v1.json"
CUSTODY_DIR = Path(os.path.expanduser("~/.sina/secrets"))
KEY_PATH = CUSTODY_DIR / "noetfield-sg-authority.private-key.pem"
WEBHOOK_SECRET_PATH = CUSTODY_DIR / "noetfield-sg-authority.webhook-secret.txt"
CLIENT_SECRET_PATH = CUSTODY_DIR / "noetfield-sg-authority.client-secret.txt"
RECEIPT_DIR = REPO_ROOT / "receipts" / "sg-candidate-app"

STATE = secrets.token_urlsafe(24)
NEW_APP_URL = f"https://github.com/organizations/{ORG}/settings/apps/new?state={STATE}"

EXPECTED_REPOS = [
    "Noetfield-Systems/sina-governance-SSOT",
    "Noetfield-Systems/noetfield-sandbox-private",
]


def load_manifest() -> str:
    with open(MANIFEST_PATH) as f:
        return f.read()


def convert_code(code: str) -> dict:
    url = f"https://api.github.com/app-manifests/{code}/conversions"
    req = urllib.request.Request(url, method="POST")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", "noetfield-sg-candidate-bootstrap")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def write_custody(data: dict) -> str:
    CUSTODY_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CUSTODY_DIR, 0o700)
    pem = data.get("pem", "")
    fd = os.open(str(KEY_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(pem)
    if data.get("webhook_secret"):
        fd = os.open(str(WEBHOOK_SECRET_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(data["webhook_secret"])
    if data.get("client_secret"):
        fd = os.open(str(CLIENT_SECRET_PATH), os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(data["client_secret"])
    return hashlib.sha256(pem.encode()).hexdigest()


def write_receipt(data: dict, fingerprint: str) -> Path:
    RECEIPT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt = {
        "receipt_type": "sg_candidate_app_creation_v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "public_metadata_only": True,
        "app": {
            "id": data.get("id"),
            "slug": data.get("slug"),
            "node_id": data.get("node_id"),
            "name": data.get("name"),
            "html_url": data.get("html_url"),
            "owner_login": (data.get("owner") or {}).get("login"),
            "owner_type": (data.get("owner") or {}).get("type"),
            "created_at": data.get("created_at"),
            "permissions": data.get("permissions"),
            "events": data.get("events"),
        },
        "private_key_custody": {
            "path": str(KEY_PATH),
            "sha256_fingerprint": fingerprint,
            "in_repo": False,
        },
        "authorized_installation_targets": EXPECTED_REPOS,
        "not_authorized": [
            "SG commissioning",
            "production ruleset enforcement",
            "Motor production permits",
            "HOLD removal",
            "legacy App revocation",
        ],
        "runtime_state": {
            "SG_CANDIDATE_APP": "CREATED",
            "SG_CANDIDATE_IDENTITY": "NOT_PROVEN",
            "SG_RUNTIME": "NOT_COMMISSIONED",
            "SG_ENFORCEMENT": "NOT_ENABLED",
            "AUTONOMOUS_PRODUCTION_MUTATIONS": "HOLD",
        },
    }
    out = RECEIPT_DIR / f"creation_{ts}.json"
    with open(out, "w") as f:
        json.dump(receipt, f, indent=2)
        f.write("\n")
    return out


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._serve_form()
        elif parsed.path == "/callback":
            self._handle_callback(parse_qs(parsed.query))
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_form(self):
        import html as _html
        manifest = load_manifest()
        # Use a visible textarea so the JSON is not mangled by attribute quoting.
        # GitHub App Manifest API requires: name, url, redirect_url.
        escaped = _html.escape(manifest, quote=True)
        html = f"""<!doctype html><html><head><meta charset=utf-8>
<title>Create noetfield-sg-authority (candidate)</title></head>
<body style="font-family:system-ui;max-width:640px;margin:60px auto">
<h2>Create candidate App: noetfield-sg-authority</h2>
<p>Owner org: <b>{ORG}</b>. Permissions are pre-filled (read-mostly + checks/statuses write). Webhook disabled.</p>
<p>Click the button, then confirm <b>Create GitHub App</b> on GitHub.</p>
<form action="{NEW_APP_URL}" method="post">
  <textarea name="manifest" style="display:none">{escaped}</textarea>
  <button type="submit" style="font-size:18px;padding:12px 20px">Create GitHub App</button>
</form>
<details style="margin-top:16px"><summary>Manifest preview</summary>
<pre style="font-size:12px;background:#f6f8fa;padding:12px;overflow:auto">{escaped}</pre>
</details>
<p style="color:#666;margin-top:24px">After creation, return here; the callback records public metadata and stores the key in SG custody.</p>
</body></html>"""
        body = html.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_callback(self, qs):
        code = (qs.get("code") or [None])[0]
        state = (qs.get("state") or [None])[0]
        if state != STATE:
            self._respond_html(400, "<h2>State mismatch. Aborted.</h2>")
            return
        if not code:
            self._respond_html(400, "<h2>Missing code. Aborted.</h2>")
            return
        try:
            data = convert_code(code)
            fingerprint = write_custody(data)
            receipt_path = write_receipt(data, fingerprint)
        except Exception as e:  # noqa
            self._respond_html(500, f"<h2>Conversion failed.</h2><pre>{e}</pre>")
            print(f"[bootstrap] ERROR: {e}", file=sys.stderr)
            return
        app_id = data.get("id")
        slug = data.get("slug")
        install_url = f"https://github.com/organizations/{ORG}/settings/apps/{slug}/installations"
        self._respond_html(
            200,
            f"""<h2>Candidate App created.</h2>
<ul>
<li>App id: <b>{app_id}</b></li>
<li>Slug: <b>{slug}</b></li>
<li>Private key stored in SG custody (fingerprint {fingerprint[:16]}...). Not in repo.</li>
<li>Public receipt: {receipt_path.name}</li>
</ul>
<p><b>Next (interactive):</b> <a href="{install_url}">Install on exactly these 2 repos</a>:</p>
<ol><li>Noetfield-Systems/sina-governance-SSOT</li>
<li>Noetfield-Systems/noetfield-sandbox-private</li></ol>
<p>Choose "Only select repositories" and pick exactly those two. Then return to Cursor.</p>""",
        )
        print(f"[bootstrap] CREATED app_id={app_id} slug={slug} fingerprint={fingerprint}")
        print(f"[bootstrap] receipt={receipt_path}")
        print(f"[bootstrap] install_url={install_url}")
        print("[bootstrap] DONE_CREATION")

    def _respond_html(self, status, inner):
        body = f"<!doctype html><html><body style='font-family:system-ui;max-width:640px;margin:60px auto'>{inner}</body></html>".encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    print(f"[bootstrap] serving http://{HOST}:{PORT}/  (state={STATE[:8]}...)")
    print(f"[bootstrap] new-app POST target: {NEW_APP_URL}")
    server = HTTPServer((HOST, PORT), Handler)
    try:
        webbrowser.open(f"http://{HOST}:{PORT}/")
    except Exception:
        pass
    server.serve_forever()


if __name__ == "__main__":
    main()
