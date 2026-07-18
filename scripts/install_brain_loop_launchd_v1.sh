#!/usr/bin/env bash
# One-shot Mac install — SourceA worktree + launchd agent (TCC-safe, overlap-safe).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOLD_FLAG="${HOME}/.sina/enforcement/brain-autonomous-hold-v1.flag"

if [[ -f "$HOLD_FLAG" ]]; then
  echo "BLOCKED_GOVERNANCE_HOLD: installer cannot remove or bypass $HOLD_FLAG" >&2
  exit 78
fi

if python3 - "$ROOT/data/runtime_reality_v1.json" <<'PY_REALITY'
import json, sys
r=json.load(open(sys.argv[1]))
raise SystemExit(0 if r["authority"]["autonomous_production_mutations"] == "HOLD" else 1)
PY_REALITY
then
  echo "BLOCKED_SG_NOT_COMMISSIONED: runtime reality is HOLD" >&2
  exit 78
fi

# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

USER_NAME="$(whoami)"
PLIST_SRC="$ROOT/scripts/com.sina.brain-loop-autorun-v1.plist"
PLIST_DST="${HOME}/Library/LaunchAgents/com.sina.brain-loop-autorun-v1.plist"

mkdir -p "${HOME}/.sina/logs" "${HOME}/.sina/locks" "${HOME}/Library/LaunchAgents"
brain_clear_stale_lock
if [[ -f "${HOME}/.sina/brain-autonomous-deploy-v1.flag" ]]; then
  touch "${HOME}/.sina/asf-ship-window-v1.flag"
fi

brain_ensure_sourcea_worktree
brain_sync_sourcea_worktree

sed \
  -e "s|@HOME@|${HOME}|g" \
  -e "s|@USER@|${USER_NAME}|g" \
  -e "s|@SG_ROOT@|${ROOT}|g" \
  "$PLIST_SRC" > "$PLIST_DST"

launchctl bootout "gui/$(id -u)/com.sina.brain-loop-autorun-v1" 2>/dev/null || \
  launchctl unload "$PLIST_DST" 2>/dev/null || true

launchctl bootstrap "gui/$(id -u)" "$PLIST_DST" 2>/dev/null || \
  launchctl load "$PLIST_DST"

echo "=== brain_loop_launchd install OK ==="
echo "plist: $PLIST_DST"
echo "sourcea_root: $SOURCEA_ROOT"
echo "python: $BRAIN_PYTHON"
launchctl list | grep brain-loop-autorun || true
echo ""
bash "$ROOT/scripts/brain_loop_health_check_v1.sh" || true
echo ""
echo "Logs: ${HOME}/.sina/logs/brain-loop-autorun-v1.{out,err}.log"
echo "Manual cycle: bash $ROOT/scripts/brain_loop_launchd_entry_v1.sh"
