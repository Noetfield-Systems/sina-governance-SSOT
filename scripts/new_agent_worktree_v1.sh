#!/usr/bin/env bash
# new_agent_worktree_v1.sh — create an ISOLATED git worktree for an agent lane.
#
# Every concurrent agent lane MUST work in its own worktree on its own branch,
# never the shared main checkout. This enforces that. See
# docs/AGENT_WORKTREE_ISOLATION_v1.md and data/agent_worktree_lanes_v1.json.
#
# Usage:
#   scripts/new_agent_worktree_v1.sh <lane-slug> [base-ref]
#     <lane-slug>  e.g. product-category-lock  -> worktree sg-product-category-lock,
#                       branch cursor/product-category-lock-v1
#     [base-ref]   clean base to fork from (default: origin/main). Use a specific
#                  commit to EXCLUDE another agent's in-flight commits from your history.
#
# Prints the cd command to enter the isolated worktree. Makes NO commits.
set -uo pipefail

# Resolve the CANONICAL (main) checkout even when run from inside a worktree:
# --git-common-dir points at the shared .git; its parent is the main checkout.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMMON="$(git -C "$HERE" rev-parse --git-common-dir 2>/dev/null)"
case "$COMMON" in /*) ;; *) COMMON="$(cd "$HERE" && cd "$COMMON" && pwd)" ;; esac
REPO_ROOT="$(dirname "$COMMON")"                  # main checkout root
WS_ROOT="$(cd "$REPO_ROOT/.." && pwd)"            # ~/Desktop/Noetfield-Systems
REPO_NAME="$(basename "$REPO_ROOT")"

slug="${1:-}"
base="${2:-origin/main}"
if [ -z "$slug" ]; then
  echo "usage: $0 <lane-slug> [base-ref]"; exit 2
fi

branch="cursor/${slug}-v1"
wt="${WS_ROOT}/${REPO_NAME%-*}-${slug}"          # e.g. sg-<slug> style sibling dir
# Fall back to a clearly-named sibling if the prefix trick is ugly:
case "$REPO_NAME" in
  sina-governance-SSOT) wt="${WS_ROOT}/sg-${slug}" ;;
esac

if git -C "$REPO_ROOT" worktree list --porcelain | grep -q "branch refs/heads/${branch}$"; then
  echo "lane already isolated: branch ${branch} exists as a worktree:"; git -C "$REPO_ROOT" worktree list | grep "$branch"; exit 0
fi
if [ -e "$wt" ]; then echo "ABORT: $wt already exists"; exit 1; fi

echo "Creating isolated worktree for lane '${slug}'"
echo "  base:     ${base}  ($(git -C "$REPO_ROOT" rev-parse --short "$base" 2>/dev/null || echo '??'))"
echo "  worktree: ${wt}"
echo "  branch:   ${branch}"
git -C "$REPO_ROOT" fetch origin --quiet 2>/dev/null || true
git -C "$REPO_ROOT" worktree add "$wt" -b "$branch" "$base" || exit 1

echo
echo "Isolated. Do ALL your lane work here (never the shared checkout):"
echo "  cd \"$wt\""
echo
echo "Then add your lane to data/agent_worktree_lanes_v1.json so others can see it."
echo "When done: push your branch and open a PR; remove the worktree with:"
echo "  git -C \"$REPO_ROOT\" worktree remove \"$wt\""
