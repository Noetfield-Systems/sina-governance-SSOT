#!/usr/bin/env bash
# Parallel brain candidate verifier batch — reads registry, triggers /run per sandbox.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

PARALLEL="${BRAIN_PARALLEL_JOBS:-2}"
SANDBOX_ARGS=()
if [[ "${1:-}" == "--all" ]]; then
  SANDBOX_ARGS=(--all)
elif [[ -n "${BRAIN_SANDBOX_IDS:-}" ]]; then
  IFS=',' read -r -a IDS <<< "$BRAIN_SANDBOX_IDS"
  for id in "${IDS[@]}"; do
    SANDBOX_ARGS+=(--sandbox-id "$id")
  done
else
  SANDBOX_ARGS=(--sandbox-id brain_worker --sandbox-id knowledge_bundle)
fi

"$BRAIN_PYTHON" "$ROOT/scripts/trigger_verifier_run_v1.py" "${SANDBOX_ARGS[@]}" --json
