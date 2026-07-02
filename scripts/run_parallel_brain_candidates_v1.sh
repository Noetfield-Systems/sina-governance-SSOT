#!/usr/bin/env bash
# Parallel brain candidate verifier batch — reads registry, triggers /run per sandbox.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

if [[ $# -gt 0 ]]; then
  "$BRAIN_PYTHON" "$ROOT/scripts/trigger_verifier_run_v1.py" "$@" --json
  exit $?
fi

"$BRAIN_PYTHON" "$ROOT/scripts/trigger_verifier_run_v1.py" \
  --sandbox-id brain_worker \
  --sandbox-id knowledge_bundle \
  --json
