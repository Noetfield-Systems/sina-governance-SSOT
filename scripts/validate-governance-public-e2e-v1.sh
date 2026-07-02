#!/usr/bin/env bash
# Governance public E2E — verifier receipt, promotion gate dry-run, SourceA public proof chain.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
export SOURCEA_ROOT
export VERIFIER_RECEIPT_URL="${VERIFIER_RECEIPT_URL:-https://sina-governance-ssot-advisory.kazemnezhadsina144.workers.dev/receipt/latest}"
export SECONDARY_CF_ACCOUNT="${SECONDARY_CF_ACCOUNT:-b7282b4a5c17b84d62e3ef8866b878f8}"

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

python3 "$ROOT/scripts/validate_governance_public_e2e_v1.py"
