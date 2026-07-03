#!/usr/bin/env bash
# Repair TCC-safe SourceA worktree at ~/Projects/SourceA (never Desktop archive for launchd).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

WT="${HOME}/Projects/SourceA"
MAIN_REPO="${HOME}/Desktop/_ARCHIVE_OLD_WORKTREES/SourceA_old_20260702_191948"

if [[ ! -d "$MAIN_REPO/.git" ]]; then
  echo "repair_sourcea_worktree_v1: FAIL — main repo missing at $MAIN_REPO" >&2
  exit 1
fi

if brain_sourcea_git_ok "$WT"; then
  echo "repair_sourcea_worktree_v1: OK — worktree already valid at $WT"
  git -C "$WT" rev-parse --short HEAD
  exit 0
fi

echo "repair_sourcea_worktree_v1: repairing broken worktree at $WT"
mkdir -p "${HOME}/Projects"

git -C "$MAIN_REPO" worktree remove "$WT" --force 2>/dev/null || true
git -C "$MAIN_REPO" worktree prune 2>/dev/null || true

if [[ -e "$WT" ]]; then
  bak="${WT}.broken-$(date -u +%Y%m%dT%H%M%SZ)"
  echo "repair_sourcea_worktree_v1: moving broken tree to $bak"
  mv "$WT" "$bak"
fi

git -C "$MAIN_REPO" fetch origin main
git -C "$MAIN_REPO" worktree add -f "$WT" origin/main

if ! brain_sourcea_git_ok "$WT"; then
  echo "repair_sourcea_worktree_v1: FAIL — worktree still not valid" >&2
  exit 1
fi

export SOURCEA_ROOT="$WT"
echo "repair_sourcea_worktree_v1: OK head=$(git -C "$WT" rev-parse --short HEAD)"
