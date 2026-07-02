#!/usr/bin/env bash
# Mac-safe brain loop environment — TCC, Python SIGKILL, PATH, overlap lock.
# Source from every brain-loop shell entrypoint (launchd, autorun, promote, heal).
set -euo pipefail

if [[ -n "${BRAIN_MAC_ENV_LOADED:-}" ]]; then
  return 0 2>/dev/null || exit 0
fi
export BRAIN_MAC_ENV_LOADED=1

# SG repo root
if [[ -z "${BRAIN_SG_ROOT:-}" ]]; then
  _src="${BASH_SOURCE[0]}"
  BRAIN_SG_ROOT="$(cd "$(dirname "$_src")/.." && pwd)"
fi
export BRAIN_SG_ROOT

# SourceA — ~/Projects/SourceA worktree avoids Desktop TCC blocks under launchd
if [[ -z "${SOURCEA_ROOT:-}" ]]; then
  if [[ -r "${HOME}/Projects/SourceA/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
    export SOURCEA_ROOT="${HOME}/Projects/SourceA"
  elif [[ -r "${HOME}/Desktop/SourceA/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
    export SOURCEA_ROOT="${HOME}/Desktop/SourceA"
  else
    export SOURCEA_ROOT="${HOME}/Projects/SourceA"
  fi
fi

# Python — Framework Python (/Library/Frameworks/...) gets SIGKILL under launchd.
# System /usr/bin/python3 is stable for all brain-loop scripts.
if [[ -x /usr/bin/python3 ]]; then
  export BRAIN_PYTHON="/usr/bin/python3"
  export PATH="/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin:${PATH:-}"
elif command -v python3 >/dev/null 2>&1; then
  export BRAIN_PYTHON="$(command -v python3)"
else
  echo "BRAIN_MAC_ENV: FAIL — python3 not found" >&2
  exit 127
fi

# Wrangler + homebrew tools after system python
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH}"

brain_python() {
  exec "$BRAIN_PYTHON" "$@"
}

brain_rc_is_sigkill() {
  local rc="${1:-0}"
  [[ "$rc" -eq 137 || "$rc" -eq 139 ]]
}

brain_acquire_lock() {
  BRAIN_LOCK_DIR="${HOME}/.sina/locks/brain-loop-autorun-v1.lock"
  mkdir -p "${HOME}/.sina/locks"
  if [[ -d "$BRAIN_LOCK_DIR" ]]; then
    if ! pgrep -f 'brain_loop_(launchd_entry|autorun)_v1' >/dev/null 2>&1; then
      rmdir "$BRAIN_LOCK_DIR" 2>/dev/null || true
    fi
  fi
  if ! mkdir "$BRAIN_LOCK_DIR" 2>/dev/null; then
    echo "BRAIN_LOOP_BUSY: another cycle is running — skip (no hold, no fail)"
    exit 0
  fi
  trap 'rmdir "${BRAIN_LOCK_DIR}" 2>/dev/null || true' EXIT INT TERM
}

brain_sync_sourcea_worktree() {
  local root="${SOURCEA_ROOT:-}"
  [[ -n "$root" ]] || return 0
  [[ -d "$root/.git" || -f "$root/.git" ]] || return 0
  if ! git -C "$root" fetch origin main 2>/dev/null; then
    echo "WARN: git fetch skipped — using local worktree HEAD"
  fi
  git -C "$root" reset --hard origin/main 2>/dev/null || git -C "$root" reset --hard HEAD
}

brain_ensure_sourcea_worktree() {
  local wt="${HOME}/Projects/SourceA"
  local desktop="${HOME}/Desktop/SourceA"
  if [[ -r "${wt}/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
    export SOURCEA_ROOT="$wt"
    return 0
  fi
  if [[ ! -d "$desktop/.git" ]]; then
    echo "BRAIN_MAC_ENV: Desktop SourceA missing — cannot create worktree" >&2
    return 1
  fi
  echo "BRAIN_MAC_ENV: creating SourceA worktree at $wt"
  mkdir -p "${HOME}/Projects"
  git -C "$desktop" fetch origin main
  git -C "$desktop" worktree add "$wt" origin/main
  export SOURCEA_ROOT="$wt"
}
