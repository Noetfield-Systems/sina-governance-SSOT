# LINE ENGINE — IDE AGENTIC LANE (candidate first line)

**Status:** Concrete Line Engine instance. Source: this chat (deep-research IDE spec + WORK_ORDER_IDE_LANE).
**First written:** 2026-07-03 12:34 PDT

## What it is
A governed agentic IDE: multiple agents + sub-agents that understand a coding/product task, decompose it, route subtasks to cheaper specialist agents, run inside sandbox/worktree lanes, validate, repair, and aggregate — with minimum founder triggers. **Not general SourceA governance — the IDE architecture specifically.**

## The pipeline
```
IDE request → Understanding → Planner → Router → Sandbox Workers → Critic/Verifier → Aggregator → Receipt
```

## Roles (each scoped — layered-agents)
| Agent | Job | Model tier |
|---|---|---|
| Understanding | request → goal, non-goals, repo scope, allowed paths, risk, unknowns, success criteria, required validation, escalation? | medium/strong |
| Planner | understanding → task graph (patch/test/research/review/receipt tasks, deps, model tier per task) | medium |
| Router | assign each task to cheapest capable agent/model | cheap/medium |
| Context | read repo, find files | cheap |
| Patch/Test/Repair Workers | small edits / run tests / fix in sandbox | cheap/medium |
| Critic | attack the output, detect drift | medium/strong |
| Verifier | schema/test/policy validation | deterministic/cheap |
| Aggregator | merge worker outputs, mark unresolved conflicts, emit receipt | medium |
| Escalation | hard ambiguity only | premium |

## Mechanical L5 gates (from WORK_ORDER — MECHANICAL not prose)
Runs in `noetfield-studio-ide` only, worktree lanes off main, per-task allowed_paths, command_allowlist, max_commits, no network. Gates G1–G6 are **hook/CI-enforced** (governance-path lock, approval-language lock, sweep-lock, unordered-commit lock, transform-fidelity, policy-immutability-during-cycle). Phase-1 tool = **Aider** (git-native, smallest command surface). Acceptance = **5 consecutive clean cycles**, each gate proven by **negative-proof** (a failing commit it rejects).

## Economic principle
strong model plans · cheap agents execute · verifier proves · aggregator composes. Founder is not the validation layer.

## Relation
Full-stack Line Engine instance (plan→produce→verify→ship→measure) + layered-agents + mechanical-not-prose + negative-proof, all in one concrete lane. **Candidate first line to build.**

---
*v0.1 (2026-07-03 12:34 PDT) — first write. IDE lane: understanding→planner→router→workers→critic→aggregator→receipt; mechanical G1-G6; Aider phase-1; 5 clean cycles. From this chat.*
