# P0 Prompt Governance Runtime (P0-PGR) — Operating Contract v1

**SUPERSEDED by `P0_DISPATCH_BRAIN_RUNTIME_v1.1.md` (2026-07-08).** v1.0 lacked the delivery rail, RUNTIME_CONTINUITY_LAW_v1, and non-binary result states. Do not register lane `p0pgr` against this version.

**Status:** DECLARED (not VERIFIED until 24h shadow window closes green — governed-autorun bootstrap rule)
**Authority:** extends existing reconciler (L1). No new run/lock/state authority.
**Laws in force:** governed-autorun L1–L13 (`SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/GOVERNED_AUTORUN_LAWS_v3.md`)

## Purpose

Replace Sina as prompt writer / router / critic / dispatcher. The runtime reads system evidence, decides what needs doing, and compiles governed prompt packets for workers. Sina's remaining roles: observe, approve phase unlocks, merge, L5 verifier changes, founder_blocked items.

The foundation is useful only if it compiles decisions into prompts without Sina becoming the runtime.

## Layer separation (least-knowledge, LOCKED)

| Layer | Reads P0? | Role |
|---|---|---|
| P0 Core | is P0 | Founder judgment, ROI doctrine, decision patterns |
| Base Live Brain | YES | Final decision on every packet |
| P0-PGR pipeline stages | YES (scoped) | Classify, research, think, criticize, advise, judge ROI, compile |
| Specialists (Architect, SG, SourceA Brain, NOOS) | high-decision only | Propose / critique / research |
| Workers | **NEVER** | Execute compiled packets only |
| Receipts | n/a | Final truth |

**P0 leakage = authority violation.** A worker prompt containing P0 doctrine text, founder-judgment patterns, or pipeline reasoning is malformed and must be rejected by the packet linter before dispatch.

## Pipeline (one cycle)

```
SYSTEM STATE → 1 Evidence Reader → 2 Problem Classifier → 3 Researcher
→ 4 Thinker → 5 Critic → 6 Advisor → 7 ROI Judge → 8 Main Brain Decision
→ 9 Prompt Compiler → 10 Dispatch Router → 11 Receipt Verifier → 12 Harvest
```

1. **Evidence Reader** — inputs, read-only: `receipts/` (freshest first, staleness gate `scripts/verify_agent_read_staleness_v1.sh` applied — stale = STALE_DATA, never guessed, L10), `data/github_automation_registry_v1.json`, `data/agent_read_surfaces_v1.json`, open next-pointers, blockers, revenue priorities. Output: evidence bundle with row IDs and timestamps. No evidence = IDLE_NO_WORK receipt (L2), never manufactured work.
2. **Problem Classifier** — exactly one of: `blocker | repair | verification | revenue | hygiene | research | deploy | architecture | founder_escalation`. Emission: `{class, reason, evidence}` (L3). `founder_escalation` routes to founder queue as `founder_blocked` (L7) and consumes no machine slot.
3. **Researcher** — collects only evidence the decision needs. No speculative research, no broad reports.
4. **Thinker** — 2–4 candidate execution strategies, each with cost estimate and authority scope.
5. **Critic** — attacks each candidate for: risk, cost, authority violation, repo contamination, false-PASS potential, P0 leakage, founder-as-runtime regression, ROI weakness. A candidate with an unanswered critique is dead.
6. **Advisor** — selects best surviving candidate; records why alternatives lost.
7. **ROI Judge** — scores 0–100: worth doing now? which model tier (`cheap | capable | premium` — premium only if ROI and difficulty justify, L11)? does it reduce Sina's future workload? Assigns `value_class` (`revenue_path | proof_asset | risk_reduction | hygiene | none`). Trailing-window spend >X% `none` → THROTTLED_ROI.
8. **Main Brain Decision** — one of: `DISPATCH | HOLD | REQUEST_FOUNDER_ONLY_IF_REQUIRED | RESEARCH_MORE | VERIFY_FIRST | REJECT_AS_LOW_ROI`. Every decision carries reason + evidence (L3).
9. **Prompt Compiler** — emits a prompt packet conforming to `P0_PROMPT_PACKET_SCHEMA_v1.json`. Packet linter checks: no P0 text, authority scope set, cost limit explicit, forbidden actions present, receipt schema required, stop rule present. Lint failure = packet rejected, never "fixed by hand downstream."
10. **Dispatch Router** — routes by `owner_agent` to SG / SourceA Brain / NOOS / Architect / Worker / Verifier / Revenue agent. One repo per packet. Concurrency keys respected — never two packets against the same mutable state.
11. **Receipt Verifier** — rejects: self-authored PASS, speculative proof ("should work"), missing evidence fields, stale receipts, verify−publish <60s (L4), authority violations, verifier edits in diff (L5 hard stop). Rejection = FAILED_WITH_RECEIPT back to step 2 as `repair`.
12. **Harvest** — only after externally verified execution: extract reusable decision pattern into P0-CORE (`FOUNDER_JUDGMENT_PATTERNS_v1.md` lineage). Never speculative philosophy. Harvest entry cites the receipt that earned it.

## Cycle receipt

Every cycle (including IDLE_NO_WORK) writes a receipt to `receipts/p0pgr/` with: cycle id, evidence row IDs read, classification, decision, packet id (if any), dispatch target, verification result, cost table (provider/model/tokens/$, metered at call site, L11), value_class. Heartbeat daily: loop states, spend by value_class, drift check (L12), founder_blocked count/oldest/age (L7).

## Hard constraints (verbatim, enforced by linter + verifier)

- Workers never read P0; no P0 reasoning in worker prompts.
- No permission loops that make Sina the runtime.
- Targets are not blockers.
- Agent self-report is not proof.
- No repo moves. No authority flips between SG / NOOS / SourceA / library.
- No new doctrine before the operational loop runs.
- No blind dispatch without evidence classification.
- No premium models without ROI justification.
- Determinism (L13): same evidence bundle → same classification → same decision. LLM output is proposal, never transition; the state machine advances only on verified receipts.

## Lane & keys

Lane: `p0pgr`. Concurrency key: `p0pgr-dispatch` (one packet in flight per target agent). Priority within tick: P0 machine work first. Founder items never occupy a slot.
