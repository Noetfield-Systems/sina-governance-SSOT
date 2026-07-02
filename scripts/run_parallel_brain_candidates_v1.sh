#!/usr/bin/env bash
# Parallel brain candidate verifier batch — reads registry, triggers /run per sandbox.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
export SOURCEA_ROOT

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

python3 "$ROOT/scripts/trigger_verifier_run_v1.py" "${SANDBOX_ARGS[@]}" --json
