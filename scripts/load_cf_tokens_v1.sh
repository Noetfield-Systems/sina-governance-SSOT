#!/usr/bin/env bash
# Source Cloudflare tokens from ~/.sina/secrets when unset.
set -euo pipefail

CF_TOKENS_FILE="${HOME}/.sina/secrets/cloudflare-tokens.env"

load_cf_tokens() {
  if [[ -n "${CF_MAIN_TOKEN:-}" && -n "${CF_VERIFIER_TOKEN:-}" ]]; then
    return 0
  fi
  if [[ ! -f "$CF_TOKENS_FILE" ]]; then
    echo "WARN: missing $CF_TOKENS_FILE; CF tokens not loaded" >&2
    if [[ "${CI:-}" == "true" || "${GITHUB_ACTIONS:-}" == "true" ]]; then
      return 0
    fi
    return 1
  fi
  set -a
  # shellcheck disable=SC1090
  source "$CF_TOKENS_FILE"
  set +a
}

load_cf_tokens "$@"
