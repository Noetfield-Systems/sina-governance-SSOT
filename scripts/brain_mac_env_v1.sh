#!/usr/bin/env bash
# Mac-safe brain loop environment — TCC, Python SIGKILL, PATH, overlap lock.
set -euo pipefail

_brain_mac_env_init() {
  if [[ -n "${BRAIN_MAC_ENV_LOADED:-}" ]]; then
    return 0
  fi
  export BRAIN_MAC_ENV_LOADED=1

  if [[ -z "${BRAIN_SG_ROOT:-}" ]]; then
    local _src="${BASH_SOURCE[1]:-${BASH_SOURCE[0]:-${0:-}}}"
    if [[ -n "$_src" && "$_src" != "main" ]]; then
      BRAIN_SG_ROOT="$(cd "$(dirname "$_src")/.." && pwd)"
    else
      BRAIN_SG_ROOT="${HOME}/Projects/sina-governance-ssot"
    fi
  fi
  export BRAIN_SG_ROOT

  if [[ -z "${SOURCEA_ROOT:-}" ]]; then
    if [[ -r "${HOME}/Projects/SourceA/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
      export SOURCEA_ROOT="${HOME}/Projects/SourceA"
    elif [[ -r "${HOME}/Desktop/SourceA/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
      export SOURCEA_ROOT="${HOME}/Desktop/SourceA"
    else
      export SOURCEA_ROOT="${HOME}/Projects/SourceA"
    fi
  fi

  if [[ -x /usr/bin/python3 ]]; then
    export BRAIN_PYTHON="/usr/bin/python3"
    export PATH="/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin:${PATH:-}"
  elif command -v python3 >/dev/null 2>&1; then
    export BRAIN_PYTHON="$(command -v python3)"
  else
    echo "BRAIN_MAC_ENV: FAIL — python3 not found" >&2
    return 127
  fi
  export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH}"
}

brain_rc_is_sigkill() {
  local rc="${1:-0}"
  [[ "$rc" -eq 137 || "$rc" -eq 139 ]]
}

brain_clear_stale_lock() {
  local lock_dir="${HOME}/.sina/locks/brain-loop-autorun-v1.lock"
  [[ -d "$lock_dir" ]] || return 0
  if pgrep -f 'brain_loop_(launchd_entry|autorun)_v1' >/dev/null 2>&1; then
    return 0
  fi
  rmdir "$lock_dir" 2>/dev/null || rm -rf "$lock_dir" 2>/dev/null || true
}

brain_acquire_lock() {
  local lock_dir="${HOME}/.sina/locks/brain-loop-autorun-v1.lock"
  mkdir -p "${HOME}/.sina/locks"
  brain_clear_stale_lock
  if ! mkdir "$lock_dir" 2>/dev/null; then
    echo "BRAIN_LOOP_BUSY: another cycle is running — skip (no hold, no fail)"
    exit 0
  fi
  echo "$$" >"${lock_dir}/pid"
  trap 'rm -f "${lock_dir}/pid" 2>/dev/null; rmdir "${lock_dir}" 2>/dev/null || true' EXIT INT TERM
}

brain_sync_sourcea_worktree() {
  local root="${SOURCEA_ROOT:-}"
  [[ -n "$root" ]] || return 0
  [[ -d "$root/.git" || -f "$root/.git" ]] || return 0
  local head origin
  head="$(git -C "$root" rev-parse HEAD 2>/dev/null || echo "")"
  origin="$(git -C "$root" rev-parse origin/main 2>/dev/null || echo "")"
  if [[ -n "$head" && "$head" == "$origin" ]]; then
    echo "sourcea_sync: already at origin/main ${head:0:12}"
    return 0
  fi
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

brain_try_clear_smoke_hold() {
  local hold="${HOME}/.sina/enforcement/brain-autonomous-hold-v1.flag"
  [[ -f "$hold" ]] || return 0
  if grep -q 'smoke_ok=False' "$hold" 2>/dev/null; then
    rm -f "$hold"
    echo "BRAIN_MAC_ENV: cleared smoke-deferred hold"
  fi
}

_brain_mac_env_init
