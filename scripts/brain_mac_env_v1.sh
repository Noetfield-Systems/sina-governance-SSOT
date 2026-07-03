#!/usr/bin/env bash
# Mac-safe brain loop environment — TCC, Python SIGKILL, PATH, overlap lock.
set -euo pipefail

brain_sourcea_git_ok() {
  local root="${1:-}"
  [[ -n "$root" ]] || return 1
  git -C "$root" rev-parse HEAD >/dev/null 2>&1
}

brain_resolve_sourcea_root() {
  local candidate archive="${HOME}/Desktop/_ARCHIVE_OLD_WORKTREES/SourceA_old_20260702_191948"
  for candidate in \
    "${HOME}/Projects/SourceA" \
    "${HOME}/Desktop/SourceA" \
    "$archive"; do
    if [[ -r "${candidate}/scripts/validate-sourcea-brain-live-v1.sh" ]] \
      && brain_sourcea_git_ok "$candidate"; then
      export SOURCEA_ROOT="$candidate"
      return 0
    fi
  done
  if [[ -r "${archive}/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
    echo "WARN: SourceA worktree git broken — run: bash scripts/repair_sourcea_worktree_v1.sh" >&2
    export SOURCEA_ROOT="${HOME}/Projects/SourceA"
    return 1
  fi
  export SOURCEA_ROOT="${HOME}/Projects/SourceA"
  return 1
}

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
    brain_resolve_sourcea_root || true
  fi

  if [[ -x /usr/bin/python3 ]]; then
    export BRAIN_PYTHON="/usr/bin/python3"
    export SOURCEA_E2E_PYTHON="/usr/bin/python3"
    mkdir -p "${HOME}/.sina/bin"
    ln -sf /usr/bin/python3 "${HOME}/.sina/bin/python3"
    export PATH="${HOME}/.sina/bin:/usr/bin:/bin:/opt/homebrew/bin:/usr/local/bin:${PATH:-}"
  elif command -v python3 >/dev/null 2>&1; then
    export BRAIN_PYTHON="$(command -v python3)"
    export SOURCEA_E2E_PYTHON="$BRAIN_PYTHON"
    export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-}"
  else
    echo "BRAIN_MAC_ENV: FAIL — python3 not found" >&2
    return 127
  fi
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
  if ! brain_sourcea_git_ok "$root"; then
    echo "WARN: sourcea_sync skipped — git not usable at $root"
    return 0
  fi
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
  if [[ -r "${wt}/scripts/validate-sourcea-brain-live-v1.sh" ]] && brain_sourcea_git_ok "$wt"; then
    export SOURCEA_ROOT="$wt"
    return 0
  fi
  bash "${BRAIN_SG_ROOT}/scripts/repair_sourcea_worktree_v1.sh"
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
