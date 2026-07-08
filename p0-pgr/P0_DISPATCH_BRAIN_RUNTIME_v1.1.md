# P0 Dispatch Brain Runtime — Operating Contract v1.1

**Supersedes:** `P0_PROMPT_GOVERNANCE_RUNTIME_v1.md` (prompt-governance only — no delivery rail)
**Subsystems:** P0-PGR (Prompt Governance Runtime) + P0-PDR (Prompt Delivery Runtime)
**Status:** DECLARED. Lane `p0pgr` may be registered only against THIS version, not v1.0.
**Laws in force:** governed-autorun L1–L13 + RUNTIME_CONTINUITY_LAW_v1 (below).

## Purpose

v1.0 answered "what prompt should be generated?" v1.1 answers the full question: the prompt was generated — now to which agent, which repo, which environment, with what permission, over which rail, with what receipt?

```
P0 thinks → prompt packet → routed → executed → receipted → harvested
```

A prompt brain without a delivery rail is just a better writer. With a delivery rail it is a runtime.

## RUNTIME_CONTINUITY_LAW_v1

The system must prefer continuous imperfect output over blocked perfection. No verifier, quality gate, blocker, receipt rule, critic, or governance layer may become a default runtime bottleneck. Governance exists to preserve motion, guide correction, and improve quality over time — not to freeze the living system.

Low-quality output is better than no output when the action is reversible, scoped, labeled, and non-destructive. Every quality control must, before stopping, attempt in order of preference: tag confidence, reduce authority scope, route to sandbox, produce partial output, emit degraded-mode result, mark provisional, retry if ROI-positive, split into smaller steps, or queue for lightweight review — always with a receipt that preserves momentum.

**HARD_BLOCK is allowed only for:** destructive repo/file operations, production deploy without authority, money movement, legal/financial commitments, credential or security exposure, irreversible external sends, authority-plane changes, and founder-only merge/L5/phase-unlock decisions. HARD_BLOCK must be rare, and every HARD_BLOCK receipt must cite one of these reasons — a HARD_BLOCK without an allowed reason is itself malformed.

Goal: progressive correction, not perfect prevention. Never sacrifice runtime life for theoretical quality purity.

> Harvest note: this law is P0-Core doctrine. Writing it into `P0-FOUNDATION-SPINE/P0-CORE/` is an authority-plane change → founder-gated. Until approved there, this file is its canonical home.

## Result states (non-binary)

PASS/STOP thinking is forbidden. Every stage and every receipt resolves to one of:

`PASS · PARTIAL · DEGRADED · SANDBOXED · PROVISIONAL · NEEDS_RETRY · NEEDS_REVIEW · FOUNDER_ONLY · HARD_BLOCK`

Low-quality outputs carry mandatory labels: confidence, scope, reversibility, next_improvement. Rejected receipts re-enter the loop as `repair` — they never silently die and never freeze the lane.

## Pipeline (unchanged 12 stages, patched decisions)

Evidence Reader → Problem Classifier → Researcher → Thinker → Critic → Advisor → ROI Judge → **Main Brain Decision** → Prompt Compiler → **Dispatch Router** → Receipt Verifier → Harvest.

Main Brain verdicts (v1.1): `DISPATCH_CLOUD | DISPATCH_MAC | HUMAN_REVIEW_PACKET | VERIFY_FIRST | HOLD | REJECT_LOW_ROI | FOUNDER_ONLY`

## Delivery rail (P0-PDR)

**Execution modes** — every packet declares one:

| Mode | Meaning |
|---|---|
| `CLOUD_ONLY` | Default. Runs without the Mac: cloud worker, GitHub Actions, Railway, Cloudflare, cloud checkout |
| `HYBRID_MAC` | Mac acts as controlled local execution node (Mac Code Runner), only when cloud can't |
| `HUMAN_REVIEW` | Packet lands in review queue; Cursor IDE opens repo/branch/task file for Sina |
| `FOUNDER_ONLY` | Merge, L5, deploy authorization, phase unlock, authority changes |

**Rails (in order of preference):** headless CLI executors — Cursor CLI, Claude Code (`claude -p`), Codex (`codex exec`) — GitHub Actions, Railway workers, Cloudflare workers, custom scripts, isolated git worktrees.

**Forbidden as primary rail:** injecting prompts into Cursor IDE chat, moving windows, any UI automation. Permitted only as emergency/manual fallback. **IDE is a viewing/editing surface, not the automation rail.**

Routing doctrine, Mac Runner safety rules, and the full destination table: `P0_DISPATCH_ROUTER_RULES_v1.md`.

## Layer separation, cycle receipts, spend governor

Unchanged from v1.0: workers never read P0; P0 leakage = lint rejection; every cycle writes a receipt (incl. IDLE_NO_WORK) with metered cost (L11); daily heartbeat with spend-by-value_class, drift (L12), founder_blocked snapshot (L7). Monthly spend governor: model budget cap enforced in ROI Judge — cap breach = BLOCKED_WITH_REASON on new premium dispatches, never overdraft; the runtime that cannot limit its own model spend is itself a problem.

## Hard constraints (v1.1 delta)

All v1.0 constraints hold, plus: no UI automation as primary rail; no prompt injection into Cursor chat as a required mechanism; every packet must carry execution_mode, delivery_route, target_executor, and fallback_route; Mac packets require canonical_path + worktree rule + mac_required_reason; deploy/merge/authority-change packets require the FOUNDER_ONLY gate; quality gates default to degrade-not-block per RUNTIME_CONTINUITY_LAW_v1.
