#!/usr/bin/env bash
# launchd entry — Mac-safe env, overlap lock, worktree sync, autorun.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

brain_acquire_lock
brain_ensure_sourcea_worktree || true
brain_sync_sourcea_worktree

PROBE="${SOURCEA_ROOT}/scripts/validate-sourcea-brain-live-v1.sh"
if [[ ! -r "$PROBE" ]]; then
  echo "LAUNCHD_TCC_BLOCK: cannot read SourceA at $PROBE"
  echo "Run: bash $ROOT/scripts/install_brain_loop_launchd_v1.sh"
  exit 3
fi

echo "=== launchd entry ==="
echo "sourcea_root: $SOURCEA_ROOT"
echo "sourcea_head: $(git -C "$SOURCEA_ROOT" rev-parse HEAD 2>/dev/null || echo unknown)"
echo "brain_python: $BRAIN_PYTHON"

exec bash "$ROOT/scripts/brain_loop_autorun_v1.sh"
