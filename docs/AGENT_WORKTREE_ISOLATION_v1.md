# Agent Worktree Isolation v1 — MANDATORY

**Status:** MANDATORY for all agents working in `sina-governance-SSOT` (and any repo
where more than one agent may run concurrently).

## The rule

**Every concurrent agent lane works in its OWN git worktree on its OWN branch.**
Never commit lane work to the shared main checkout. One branch shared by multiple
agents = interleaved commits, clobbered working trees, and "did you delete my
project?" panics. Isolation makes collisions structurally impossible.

## Why (what went wrong — 2026-07-09)

Three agents — L0-maintenance, sandbox-build, and product-lock — all worked on the
**same checkout** (`sina-governance-SSOT`) on the **same branch**
(`cursor/language-layer-v1`). Result: their commits interleaved on one branch, and a
merged-then-not-switched-back feature branch made a fully intact repo *look* deleted
in the IDE. The product-lock and sandbox agents had isolated into worktrees; the L0
agent had not. That was the bug.

## Do this (start of any lane)

```
# from the main checkout, once:
scripts/new_agent_worktree_v1.sh <lane-slug> [base-ref]
#   e.g.  scripts/new_agent_worktree_v1.sh payments-audit origin/main
#   -> worktree ~/Desktop/Noetfield-Systems/sg-payments-audit
#      branch   cursor/payments-audit-v1
cd ~/Desktop/Noetfield-Systems/sg-<lane-slug>
```

- **Base at a clean ref.** Default `origin/main`. If another agent has in-flight
  commits you must NOT inherit, base at a specific commit before theirs (that is how
  the L0 lane was recovered: forked at `3f61d41` and cherry-picked only its own 4
  commits, excluding the product-lock commits).
- **Register your lane** in `data/agent_worktree_lanes_v1.json` so others see it.
- **Do every edit/commit in your worktree.** Never `cd` to the shared checkout to
  commit.

## Do NOT

- Do not commit to the shared `sina-governance-SSOT` checkout / `cursor/language-layer-v1`.
- Do not touch another lane's worktree, branch pointer, or uncommitted files.
- Do not `git reset` a shared branch while any agent may have uncommitted work there —
  coordinate first (`git worktree list`, `git status`) and verify idle.
- Do not leave a repo checked out on a feature branch after its PR merges — switch it
  back to `main` (`git checkout main && git pull --ff-only`) so the IDE shows it cleanly.

## Verify before you claim isolation (no claims without proof)

```
git rev-parse --abbrev-ref HEAD                       # on my lane branch, not shared
git rev-list --count <base>..HEAD                     # only my commits
git merge-base --is-ancestor <other-agent-commit> HEAD && echo BAD || echo good
git worktree list                                     # my worktree present, others intact
```

## Current lanes

See `data/agent_worktree_lanes_v1.json` (source of truth). As of 2026-07-09:
`l0-repo-graph-maintenance` (sg-l0-maintenance), `product-category-lock`
(sg-product-lock), `sandbox-build` (sg-sandbox). The main checkout
`sina-governance-SSOT` is reserved for integration/review — not lane work.
