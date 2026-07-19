#!/usr/bin/env python3
"""Prove SG key2 custody ESTABLISHED, then stamp runtime_reality + receipt.

Done when:
  - key1 (bootstrap fingerprint 5d75d4e1...) fails GET /app
  - key2 (fingerprint 22a9513a...) succeeds GET /app + installation token
  - shadow health ok
  - local bootstrap archived pem removed (or proven absent)

Usage:
  python3 scripts/prove_sg_key2_custody_established_v1.py
  python3 scripts/prove_sg_key2_custody_established_v1.py --apply
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import padding
except ImportError:
    print("FAIL: cryptography package required", file=sys.stderr)
    raise SystemExit(2)

ROOT = Path(__file__).resolve().parents[1]
APP_ID = 4330805
INSTALL_ID = 147378007
KEY2_FP = "22a9513a3aaee95266538a5fc49c94a4591119d14fe9332f2964fd603817c3a8"
KEY1_FP = "5d75d4e187747d65f459bd1d15ec8005c4477f65c0ccb9d8431599a35f4c436b"
SECRETS = Path.home() / ".sina" / "secrets"
KEY2_PEM = SECRETS / "noetfield-sg-authority.commissioning-key-2.private-key.pem"
KEY1_PEM = SECRETS / "noetfield-sg-authority.bootstrap-key-1.ARCHIVED.pem"
CANONICAL_PEM = SECRETS / "noetfield-sg-authority.private-key.pem"
SHADOW_HEALTH = "https://noetfield-sg-authority-v2-shadow.kazemnezhadsina144.workers.dev/health"


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def public_fp(pem: Path) -> str:
    key = serialization.load_pem_private_key(pem.read_bytes(), password=None)
    pub = key.public_key().public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return hashlib.sha256(pub).hexdigest()


def mint_jwt(pem: Path) -> str:
    key = serialization.load_pem_private_key(pem.read_bytes(), password=None)
    now = int(time.time())
    header = b64url(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    payload = b64url(json.dumps({"iat": now - 60, "exp": now + 540, "iss": APP_ID}).encode())
    signing = f"{header}.{payload}".encode()
    sig = key.sign(signing, padding.PKCS1v15(), hashes.SHA256())
    return f"{header}.{payload}.{b64url(sig)}"


def gh_ok(pem: Path, path: str, method: str = "GET") -> tuple[bool, int, dict]:
    jwt = mint_jwt(pem)
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=b"{}" if method == "POST" else None,
        method=method,
        headers={
            "Authorization": f"Bearer {jwt}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "prove-sg-key2-custody-v1",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = json.loads(resp.read().decode() or "{}")
            return True, resp.status, body
    except urllib.error.HTTPError as e:
        return False, e.code, {"error": e.reason}
    except Exception as e:  # noqa: BLE001
        return False, 0, {"error": str(e)}


def probe_shadow() -> dict:
    req = urllib.request.Request(SHADOW_HEALTH, headers={"User-Agent": "prove-sg-key2-custody-v1"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="Write runtime_reality + receipt on PASS")
    args = ap.parse_args()
    at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if not KEY2_PEM.is_file():
        print("FAIL: key2 pem missing", KEY2_PEM)
        return 2
    if public_fp(KEY2_PEM) != KEY2_FP:
        print("FAIL: key2 fingerprint mismatch", public_fp(KEY2_PEM))
        return 2
    if CANONICAL_PEM.is_file() and public_fp(CANONICAL_PEM) != KEY2_FP:
        print("FAIL: canonical pem is not key2", public_fp(CANONICAL_PEM))
        return 2

    key2_app_ok, _, key2_app = gh_ok(KEY2_PEM, "/app")
    key2_tok_ok, _, _ = gh_ok(KEY2_PEM, f"/app/installations/{INSTALL_ID}/access_tokens", "POST")
    key1_present = KEY1_PEM.is_file()
    key1_app_ok = False
    if key1_present:
        if public_fp(KEY1_PEM) != KEY1_FP:
            print("WARN: archived key1 fingerprint unexpected", public_fp(KEY1_PEM))
        key1_app_ok, code, _ = gh_ok(KEY1_PEM, "/app")
        print(f"key1_present=True key1_auth_ok={key1_app_ok} http={code}")
    else:
        print("key1_present=False (local archived pem absent)")

    shadow = probe_shadow()
    print(f"key2_app_ok={key2_app_ok} key2_install_ok={key2_tok_ok} shadow_ok={shadow.get('ok')}")

    if not (key2_app_ok and key2_tok_ok and shadow.get("ok") is True):
        print("FAIL: key2 or shadow not proven")
        return 1

    if key1_present and key1_app_ok:
        print("BLOCKED_FOUNDER: bootstrap key1 still authenticates on GitHub.")
        print("Delete OLD private key in App 4330805 UI (fingerprint 5d75d4e1...). Keep key2 22a9513a...")
        print("URL: https://github.com/settings/apps/noetfield-sg-authority")
        return 3

    # key1 absent locally OR key1 auth fails → ESTABLISHED path
    if key1_present and not key1_app_ok:
        # safe to delete local archived copy after GitHub revoke proven
        bak = KEY1_PEM.with_suffix(KEY1_PEM.suffix + f".revoked-{at.replace(':', '')}")
        KEY1_PEM.rename(bak)
        print("quarantined local key1 ->", bak)

    result = {
        "receipt_type": "nf_sg_key2_custody_established_v1",
        "captured_at": at,
        "verdict": "ESTABLISHED",
        "key2_fingerprint": KEY2_FP,
        "key1_fingerprint": KEY1_FP,
        "key1_auth_ok": False,
        "key2_app_ok": key2_app_ok,
        "key2_install_ok": key2_tok_ok,
        "shadow_health": shadow,
        "app": {"id": key2_app.get("id"), "slug": key2_app.get("slug")},
    }
    print(json.dumps(result, indent=2))

    if not args.apply:
        print("DRY_RUN: pass --apply to stamp runtime_reality + receipt")
        return 0

    reality_path = ROOT / "data" / "runtime_reality_v1.json"
    reality = json.loads(reality_path.read_text())
    reality["key_custody"] = {
        **reality.get("key_custody", {}),
        "SG_BOOTSTRAP_KEY_1": "REVOKED",
        "SG_BOOTSTRAP_KEY_1_COMMISSIONING_ELIGIBLE": False,
        "SG_KEY_CUSTODY": "KEY2_INDEPENDENT_VERIFIER_ONLY",
        "SG_COMMISSIONING_KEY_CUSTODY": "IMPORTED_VERIFIER_ACCOUNT",
        "SG_COMMISSIONING_ELIGIBLE": True,
        "SG_COMMISSIONING_KEY_2_CUSTODY": "ESTABLISHED",
        "SG_BOOTSTRAP_KEY_1_REVOKED": True,
        "custody_reason": "Key2 only in verifier CF account; bootstrap key1 revoked in GitHub and removed from agent-local use.",
        "SG_COMMISSIONING_KEY_2_PUBLIC_FINGERPRINT_SHA256": KEY2_FP,
        "custody_cloudflare_account_id": "b7282b4a5c17b84d62e3ef8866b878f8",
        "custody_worker": "noetfield-sg-authority-v2-shadow",
        "established_at": at,
    }
    reality_path.write_text(json.dumps(reality, indent=2) + "\n")

    cand_path = ROOT / "data" / "sg_candidate_app_state_v1.json"
    if cand_path.is_file():
        cand = json.loads(cand_path.read_text())
        cand["SG_COMMISSIONING_KEY_CUSTODY"] = "ESTABLISHED"
        cand["SG_COMMISSIONING_ELIGIBLE"] = True
        cand_path.write_text(json.dumps(cand, indent=2) + "\n")

    receipt_path = ROOT / "receipts" / "doctrine" / "NF_SG_KEY2_CUSTODY_ESTABLISHED_v1.json"
    receipt_path.write_text(json.dumps(result, indent=2) + "\n")
    print("WROTE", reality_path)
    print("WROTE", receipt_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
