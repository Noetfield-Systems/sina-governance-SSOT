#!/usr/bin/env bash
# launchd entry — preflight Desktop/TCC before brain autorun.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
PROBE="$SOURCEA_ROOT/scripts/validate-sourcea-brain-live-v1.sh"

if [[ ! -r "$PROBE" ]]; then
  echo "LAUNCHD_TCC_BLOCK: cannot read SourceA scripts at $PROBE"
  echo "Fix: System Settings → Privacy & Security → Full Disk Access → add /bin/bash (or Terminal)"
  exit 3
fi

exec bash "$ROOT/scripts/brain_loop_autorun_v1.sh"
