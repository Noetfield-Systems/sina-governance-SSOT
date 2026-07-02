#!/usr/bin/env python3
"""Re-prove SG verifier runs from secondary CF account without MAIN token."""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.brain_domain_registry_v1 import build_verifier_post_body, expand_root, get_sandbox, load_registry  # noqa: E402
from scripts.trigger_verifier_run_v1 import post_verifier_run  # noqa: E402

SECONDARY_CF_ACCOUNT = "b7282b4a5c17b84d62e3ef8866b878f8"
DEFAULT_OUT = ROOT / "receipts/verifier-independence-proof-latest.json"


def load_verifier_token_only() -> None:
    if os.environ.get("CF_VERIFIER_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN"):
        return
    tokens_file = Path.home() / ".sina/secrets/cloudflare-tokens.env"
    if not tokens_file.is_file():
        return
    for raw_line in tokens_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key in ("CF_VERIFIER_TOKEN", "CLOUDFLARE_API_TOKEN") and not os.environ.get(key):
            os.environ[key] = value


def verifier_token() -> str | None:
    return os.environ.get("CF_VERIFIER_TOKEN") or os.environ.get("CLOUDFLARE_API_TOKEN")


def fetch_whoami(token: str) -> dict[str, Any]:
    request = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/accounts",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
        accounts = payload.get("result") or []
        ids = [row.get("id") for row in accounts if row.get("id")]
        return {"ok": True, "account_ids": ids}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Prove verifier independence (secondary CF account).")
    parser.add_argument("--write-receipt", default=str(DEFAULT_OUT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    os.environ.pop("CF_MAIN_TOKEN", None)
    load_verifier_token_only()
    token = verifier_token()
    whoami = fetch_whoami(token) if token else {"ok": False, "error": "no verifier token in env"}

    registry = load_registry()
    sandbox = get_sandbox(registry, "brain_worker")
    repo = expand_root(sandbox["deploy_root"])
    body = build_verifier_post_body(sandbox, repo)
    receipt = post_verifier_run(registry["verifier_base_url"], body)

    proof = {
        "receipt_type": "VERIFIER_INDEPENDENCE_PROOF",
        "recorded_at": dt.datetime.now(dt.UTC).isoformat(),
        "status": receipt.get("status"),
        "result": receipt.get("result"),
        "secondary_account_proven": receipt.get("secondary_account_proven"),
        "cf_account_id": receipt.get("cf_account_id"),
        "expected_cf_account_id": SECONDARY_CF_ACCOUNT,
        "verifier_receipt_id": receipt.get("receipt_id"),
        "whoami": whoami,
        "main_token_absent": "CF_MAIN_TOKEN" not in os.environ,
        "verifier_token_present": bool(token),
        "candidate_ref": body["candidate_ref"],
    }
    whoami_ok = SECONDARY_CF_ACCOUNT in (whoami.get("account_ids") or [])
    proof["pass"] = (
        proof["result"] == "PASS"
        and proof["secondary_account_proven"] is True
        and proof["cf_account_id"] == SECONDARY_CF_ACCOUNT
        and (whoami_ok or not token)
    )
    if proof["pass"] and not whoami_ok:
        proof["note"] = "Verifier edge PASS on secondary account; CF whoami skipped or unavailable."

    out = Path(args.write_receipt)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(proof, indent=2, sort_keys=True))
    else:
        print(f"independence_proof pass={proof['pass']} receipt={out}")

    return 0 if proof["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
