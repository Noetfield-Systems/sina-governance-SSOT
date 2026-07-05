# LINE ENGINE — UNDERSTANDING · PLANNER · ROUTER · WORKERS (IDE lane roles)
**Understanding:** request → goal, non-goals, repo scope, allowed paths, risk, unknowns, success criteria, required validation, escalation? (medium/strong)
**Planner:** understanding packet → task graph (patch/test/research/review/receipt tasks, deps, model tier per task) (medium)
**Router:** each task → cheapest capable agent/model; circuit breaker (cheap/medium) — dispatcher not brain
**Workers:** Context (read repo, cheap) · Patch (small edits, cheap) · Test (run+summarize, cheap) · Repair (fix in sandbox, cheap/medium). Sandbox/worktree only, allowed paths + allowlist.
Economic: strong model plans; cheap agents execute. Full detail: `ide-agentic-lane.md`.
*v0.1 (2026-07-03 12:34 PDT) — IDE lane roles, upstream half.*
