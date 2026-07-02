#!/usr/bin/env bash
# Fast preflight — verify Mac brain loop is ready (<5s).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

ERR=0
_check() {
  local label="$1"
  shift
  if "$@"; then
    echo "OK: $label"
  else
    echo "FAIL: $label"
    ERR=$((ERR + 1))
  fi
}

_check "python" "$BRAIN_PYTHON" -c "import sys; assert sys.version_info >= (3,9)"
_check "sourcea readable" test -r "${SOURCEA_ROOT}/scripts/validate-sourcea-brain-live-v1.sh"
_check "sg registry" test -f "$ROOT/data/brain_domain_sandboxes_v1.json"
_check "autonomous flag" test -f "${HOME}/.sina/brain-autonomous-deploy-v1.flag"
_check "cf tokens script" test -f "$ROOT/scripts/load_cf_tokens_v1.sh"
_check "wrangler" command -v wrangler >/dev/null
brain_clear_stale_lock
echo "OK: stale lock cleared"

HEAD="$(git -C "$SOURCEA_ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown)"
ORIGIN="$(git -C "$SOURCEA_ROOT" rev-parse --short origin/main 2>/dev/null || echo unknown)"
echo "sourcea_head=${HEAD} origin_main=${ORIGIN}"

if [[ "$ERR" -gt 0 ]]; then
  echo "brain_loop_health_check_v1: FAIL errors=${ERR}"
  exit 1
fi
echo "brain_loop_health_check_v1: ALL PASS"
exit 0
