# P0-PGR/PDR Compiler — MVP Implementation Plan v1.1

**Patched 2026-07-08:** delivery-aware packets, RUNTIME_CONTINUITY_LAW_v1, 4-phase path (was 3). Contract: `P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`.

**Goal:** first operational prompt-authoring + delivery loop. No new doctrine. Each phase ends with an external receipt, not a claim.

## Build order (Phase-0 scripts — delivery-aware, not prompt-only)

1. `scripts/p0pgr_evidence_reader_v1.py` — reads `receipts/` (staleness-gated), registries, alive docs, open next-pointers, **plus repo/cloud state needed for routing** (is canonical state in remote? are secrets local-only?) → evidence bundle JSON with `bundle_hash`.
2. `scripts/p0pgr_cycle_v1.py` — runs the 12-stage pipeline; Main Brain verdicts are v1.1 (`DISPATCH_CLOUD | DISPATCH_MAC | HUMAN_REVIEW_PACKET | VERIFY_FIRST | HOLD | REJECT_LOW_ROI | FOUNDER_ONLY`); writes loop-state receipt to `receipts/p0pgr/`. LLM output is proposal; the script owns transitions (L13). Quality gates degrade per continuity law — the cycle never emits bare STOP.
3. `scripts/p0pgr_packet_lint_v1.py` — validates against packet schema v1.1 + semantic checks. **Must reject:**
   - missing `execution_mode`, `delivery_route`, `target_executor`, or `authority_scope`
   - missing `quality_handling` (result states + hard-block reason whitelist)
   - HARD_BLOCK configured with a reason outside the allowed enum
   - worker prompt containing P0 leakage (grep against P0-CORE fingerprints)
   - HYBRID_MAC packet without `canonical_path` + worktree rule + `mac_required_reason`
   - deploy / merge / authority-change without the FOUNDER_ONLY gate
   - premium tier with roi_score < 70
   - `cloud_safe: false` routed to a cloud destination
   Lint failure = packet rejected fail-closed — but the *cycle* continues: rejection files a repair candidate, it does not freeze the lane.

**Lane registration gate:** register lane `p0pgr` in `data/github_automation_registry_v1.json` only after all three scripts pass against schema v1.1 and one shadow packet round-trips. A half-delivery PGR is not registered as complete.

## Phase 1 — Packet Generator (shadow)

`P0 state → prompt_packet.json` in `receipts/p0pgr/outbox/`, `dispatch_mode: shadow`. No execution. Sina reviews as diff-read; forced rewrites = compiler defects → Kaizen candidates.
**Exit:** ≥10 packets, ≥7 with zero founder edits, 0 lint escapes, 0 P0 leakage, cost table on every cycle.

## Phase 2 — Cloud Router

`prompt_packet.json → cloud executor / GitHub Action / verifier`. Observe/test/report authority only. CLOUD_ONLY packets flow end-to-end; Receipt Verifier wired; rejected receipts re-enter as `repair`.
**Exit:** 24h zero-manual window on CLOUD_ONLY observe-scope packets, sink invariants green, heartbeat with cost + drift.

## Phase 3 — Mac Runner

`prompt_packet.json → Mac worktree → CLI agent → receipt`. Runner daemon per `P0_DISPATCH_ROUTER_RULES_v1.md` safety rules 1–10. No Cursor UI automation. Mac packets require founder review in this phase.
**Exit:** ≥5 HYBRID_MAC packets round-trip: poll → worktree → executor → receipt → push → cloud truth log, 0 path violations.

## Phase 4 — ROI Autonomy

Low-risk cloud AND Mac packets auto-dispatch; merge/L5/deploy/authority stay founder-gated. THROTTLED_ROI + spend governor active. Harvest loop live with earning-receipt citations. Weekly founder ROI digest.
**Exit:** DECLARED → VERIFIED after 24h green window; founder prompt-writes per week → 0.

## Hard stops carried through all phases

No repo moves. No authority flips. No verifier weakening without founder diff (L5). No worker reads P0. No dispatch without evidence classification. No UI automation as primary rail. Budget cap breach = BLOCKED_WITH_REASON on new spend, never overdraft, never a freeze on read-only continuity work.

## Example packet

`EXAMPLE_PACKET_P0PGR-20260708-001.json` — CLOUD_ONLY wiring audit via github_action, fallback mac_runner, hard-block disallowed (read-only packet).
