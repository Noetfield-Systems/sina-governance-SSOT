---
name: p0pgr-operator
description: Operate the P0 Dispatch Brain Runtime (P0-PGR/PDR) in the sina-governance-SSOT repo — run shadow cycles, strategic campaigns, ROI ranking, Phase 2 cloud-only executions, and scorecard updates under the v1.1 contract. Use this skill whenever the user or an advisor message mentions P0-PGR, PGR/PDR, prompt packets, dispatch brain, shadow cycles, campaign mode, phase 1/2/3 operations, ranked queue, "what's the next move", "run the next packet", "execute the top candidate", "update the scorecard", or pastes advisor instructions about phases, dispatch, or runtime operating modes. Also use it when asked to check what phase the system is in or whether an action is allowed in the current phase.
---

# P0-PGR Operator

Drive the P0 Dispatch Brain Runtime correctly without re-deriving its rules. The runtime's purpose: the system writes and routes prompts so Sina doesn't. Your job as operator is to keep it moving — motion first, authority controlled.

## Repo map (source of truth — read these, never assume)

| What | Where |
|---|---|
| Master contract (v1.1) | `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md` |
| Router rules + Mac safety + rails | `p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md` |
| Packet schema (v1.1 delivery-aware) | `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json` |
| Loop-state schema | `p0-pgr/P0_PROMPT_LOOP_STATE_SCHEMA_v1.json` |
| MVP phases + lint reject list | `p0-pgr/P0_PROMPT_COMPILER_MVP_PLAN_v1.md` |
| Cycle runner | `scripts/p0pgr_cycle_v1.py` |
| Evidence reader | `scripts/p0pgr_evidence_reader_v1.py` |
| Packet linter | `scripts/p0pgr_packet_lint_v1.py` |
| Campaign planner | `scripts/p0pgr_campaign_planner_v1.py` |
| Phase 2 ROI ranker | `scripts/p0pgr_phase2_rank_v1.py` |
| Real packets (outbox) | `receipts/p0pgr/outbox/` |
| Campaign receipts | `receipts/p0pgr/campaigns/` |
| Scorecards | `receipts/p0pgr/phase1_scorecard_v1.json`, `receipts/p0pgr/phase2_scorecard_v1.json` |
| Ranked queue | `receipts/p0pgr/phase2_queue_v1.json` |
| Tests | `tests/test_p0pgr_phase0.py` (must stay green) |

## First action, always

Read the newest scorecard and queue before doing anything. The current phase, operating mode, next queued move, and founder directives live there — not in your memory of past sessions. If the scorecard and your assumptions disagree, the scorecard wins.

## Operating mode rules (current era: PHASE_2_CLOUD_ONLY_ROI_TRACK)

- Cloud-only. Never route to Mac, never build the Mac runner, never use HYBRID_MAC as fallback. Cloud-unsafe work is labeled `HOLD_CLOUD_UNSAFE` — a label, not a block.
- A packet may actually execute only if ALL gates pass: CLOUD_ONLY · read-only or reversible · ROI-positive · no deploy · no external send · no legal/financial commitment · no P0 leakage · no authority change · **an in-repo founder authorization receipt exists** (`receipts/p0pgr/founder/`). Anything failing a gate queues for founder review; it does not execute "a little bit".
- Founder directives arriving in chat are real authority but not durable evidence. Before acting on one, record it as a founder receipt (verbatim directive, date, scope, what it unlocks) — the M03 audit flagged exactly this gap: execution happened on chat-only authorization and later verifiers could not find the unlock anywhere in the repo.
- Deploy, merge, L5 verifier changes, phase unlocks, authority changes: FOUNDER_ONLY, always.
- No scheduled automation unless the founder has explicitly approved it.

## Continuity law (governs every gate you touch)

Prefer continuous imperfect output over blocked perfection. When quality is weak: tag confidence → reduce scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue. Never default to STOP. HARD_BLOCK only for the eight irreversible reasons in the contract, and it must cite one. A failed lint files a repair candidate and the lane keeps moving. If you ever find yourself freezing the lane for quality purity, you are violating founder doctrine.

## Standard operations

**Run a shadow cycle** (compile + lint + route one packet, zero execution):
```bash
python3 scripts/p0pgr_cycle_v1.py --packet <packet-path>
```
Receipt lands in `receipts/p0pgr/`. Malformed packet → repair candidate in `receipts/p0pgr/repair_candidates/`, verdict REPAIR_CANDIDATE, lane continues.

**Run a strategic campaign** (board-wide candidate generation with CHESS pass):
```bash
python3 scripts/p0pgr_campaign_planner_v1.py
```
Generates candidates across the six board axes (runtime health, authority wiring, commercial readiness, live truth, cost/ROI, delivery readiness), CHESS-passes each (Forecast → Patch → Proceed → Verify — an improver, not a blocker), lints, and writes a campaign receipt.

**Re-rank the Phase 2 queue** (deterministic, weights 35 revenue / 25 trust / 15 workload / 15 cloud-now / 10 reversibility):
```bash
python3 scripts/p0pgr_phase2_rank_v1.py
```

**Execute a cloud move**: check all nine gates above, execute with external evidence (fetches, script runs), then write an execution receipt validating against `p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json`. Be honest about quality_state: PARTIAL with labeled limitations beats an inflated PASS. Never claim an audited issue is fixed.

**Receipt provenance rules** (each learned from a real audit finding on the M03 receipt):
- Timestamps are machine-generated at the moment of the event (`datetime.now(timezone.utc)` in the writing code) — never typed from memory. A verifier will compare `recorded_at` to file mtime and reject hand-authored clocks.
- Every external claim stores an artifact: per-URL status + body sha256 + saved body under `receipts/p0pgr/artifacts/<receipt-id>/`. Prose reproduction of what a page said is not evidence.
- If the actual executor differs from the packet's declared route, say so in `executor_route_note` — silent route deviation reads as authority drift.
- Cost accounting: session-embedded LLM work is not a bare $0; use `accounting_note` to say where the cost actually sits.
- Flag new receipts for git commit in the next founder-visible commit — untracked receipts carry no tamper evidence.

**Update scorecards** after every operation: counters (executions, sends=0, deploys=0, leaks, freezes, cost), queue position, new candidate packets born from findings.

## Verification discipline

- Never trust a script's own success claim, including scripts you just ran: re-validate emitted receipts against the loop-state schema independently, re-lint packets independently.
- Metered cost on every receipt (L11). Deterministic scripts with zero LLM calls report a true $0.
- Findings that need founder eyes get an ID (F1, F2, …) and a next_pointer; they never silently disappear (L7).
- Keep `python3 -m pytest tests/test_p0pgr_phase0.py -q` green after any script change.

## Report format (fixed — kills narrative padding)

OBSERVED · <operation-specific sections> · QUALITY STATE · RECEIPT · SCORECARD · NEXT · STOP

## Companion skills

Authoring a new packet from a problem statement → use `p0pgr-packet-compiler`. Auditing a returned receipt or agent report → use `p0pgr-receipt-verifier`.
