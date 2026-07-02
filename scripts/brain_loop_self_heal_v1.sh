#!/usr/bin/env bash
# Brain loop self-heal tick — compare HEAD vs verifier receipt; optional re-verify.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

TRIGGER=()
if [[ "${BRAIN_SELF_HEAL_TRIGGER:-0}" == "1" ]]; then
  TRIGGER=(--trigger)
fi

"$BRAIN_PYTHON" "$ROOT/scripts/brain_loop_self_heal_v1.py" \
  --sandbox-id "${BRAIN_SANDBOX_ID:-brain_worker}" \
  "${TRIGGER[@]}" \
  --json
