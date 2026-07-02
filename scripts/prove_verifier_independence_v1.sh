#!/usr/bin/env bash
# Re-prove verifier independence from secondary CF account (no MAIN token).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
unset CF_MAIN_TOKEN || true
python3 "$ROOT/scripts/prove_verifier_independence_v1.py" --json
