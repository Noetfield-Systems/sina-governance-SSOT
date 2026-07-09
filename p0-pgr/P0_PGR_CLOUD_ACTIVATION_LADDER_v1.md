# P0-PGR Cloud Activation Ladder v1

**Purpose:** the ordered path from "loop runs when a session runs it" to "loop runs itself, Sina only observes + approves ROI-gated escalations." Each rung has an entry gate, an exit receipt, and a founder decision point. Skipping rungs is how false 24/7 claims are born (see workflow census RED history).

**Current rung: R1.** The loop's brain exists and has run (Phase 0–2, campaign, 2 executions) but only inside interactive sessions. That is the honest gap against the original founder ask.

## Rungs

### R1 — Session-driven (DONE, current)
Cycle/campaign/rank scripts run in Cowork/Cursor sessions. Deterministic, receipt-backed, founder-in-loop.
**Exit receipt:** commits `7bd58d5`/`acbb796` + shadow round-trip + campaign receipt. ✅

### R2 — Cloud manual trigger (BUILT, awaiting founder push + first run)
GitHub Actions workflow `p0pgr-shadow-cycle-v1.yml` with `workflow_dispatch` ONLY (no cron — scheduled automation stays founder-gated). Runs evidence reader + shadow cycle on a cloud runner, uploads receipts as artifacts + job summary.
**Entry gate:** branch pushed to origin; founder clicks Run workflow.
**Exit receipt:** 2 successful cloud runs whose receipts validate against loop-state schema. Proves the loop runs without any Mac and without any session.

### R3 — Cron shadow (founder unlock #1)
Enable the cron line in the same workflow (daily). Loop reads state and compiles packets into outbox EVERY DAY with zero human presence. Still zero dispatch.
**Entry gate:** founder receipt `receipts/p0pgr/founder/FOUNDER-UNLOCK-R3-CRON-SHADOW-*.json`.
**Exit receipt (governed-autorun bootstrap rule):** 2+ consecutive `schedule`-event runs green — manual green ≠ cron green — then a 7-day shadow window: Sina diff-reads packets on his own schedule; ≥7 packets accepted without rewrite (Phase 1 exit criteria finally close here, formally).

### R4 — Low-risk auto-dispatch (founder unlock #2)
Templates with registry status `AUTO_DISPATCH_APPROVED` (per-template founder approval, never global) auto-dispatch when ALL Phase-2 gates pass: CLOUD_ONLY · observe scope · ROI-positive · no send/deploy/legal · no P0 leak · cost cap. Eligible classes: verification, health checks, receipt audits, read-only research, no-send sourcing rows.
**Exit receipt:** 24h zero-manual window — scheduled receipts only, sink invariants green, heartbeat with cost table + drift check (L12), 0 authority violations.

### R5 — ROI-aware autonomy (founder unlock #3)
Bounded edit-scope packets auto-run (branch/PR, never merge). THROTTLED_ROI + monthly spend governor active ($1.5k cap pre-revenue). Harvest loop live: verified patterns flow to P0-CORE with earning-receipt citations. Sina's standing surface: merge · live deploy · legal/equity/offer copy · contact approval · L5 · phase unlocks.
**Exit condition (the original ask, measurably):** founder prompt-writes per week → 0; loop status flips DECLARED → VERIFIED.

## Standing rules on every rung

- Continuity law: weak output degrades (PARTIAL/PROVISIONAL/repair candidate), never lane STOP.
- Receipts: machine timestamps, evidence artifacts, exec-receipt schema, committed to git (cross-clone incident rule).
- TrustField Partner Access + Team Bench are the standing test feed: every rung proves itself on real current problems from those lanes (M03 already did this at R1), not synthetic tasks.
- Every rung's unlock is a founder receipt in `receipts/p0pgr/founder/` — chat approval is recorded first, then acted on.
