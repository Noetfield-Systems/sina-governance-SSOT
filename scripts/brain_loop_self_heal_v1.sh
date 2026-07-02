#!/usr/bin/env bash
# Brain loop self-heal tick — compare HEAD vs verifier receipt; optional re-verify.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
export SOURCEA_ROOT

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

TRIGGER=()
if [[ "${BRAIN_SELF_HEAL_TRIGGER:-0}" == "1" ]]; then
  TRIGGER=(--trigger)
fi

python3 "$ROOT/scripts/brain_loop_self_heal_v1.py" \
  --sandbox-id "${BRAIN_SANDBOX_ID:-brain_worker}" \
  "${TRIGGER[@]}" \
  --json
