"""Load Cloudflare API tokens from ~/.sina/secrets without printing values."""
from __future__ import annotations

import os
from pathlib import Path

CF_TOKENS_FILE = Path.home() / ".sina/secrets/cloudflare-tokens.env"
CF_TOKEN_KEYS = ("CF_MAIN_TOKEN", "CF_VERIFIER_TOKEN", "CLOUDFLARE_API_TOKEN")


def load_cloudflare_tokens() -> None:
    """Load CF tokens when not already in the environment."""
    if all(os.environ.get(key) for key in ("CF_MAIN_TOKEN", "CF_VERIFIER_TOKEN")):
        return
    if not CF_TOKENS_FILE.is_file():
        return
    for raw_line in CF_TOKENS_FILE.read_text().splitlines():
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
        if key in CF_TOKEN_KEYS and not os.environ.get(key):
            os.environ[key] = value
