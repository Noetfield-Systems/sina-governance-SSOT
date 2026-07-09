# LINE ENGINE — Architecture Spec v0.2 (HARDENED / OPERATIONAL)

**Author:** Sina Kazemnezhad (Noetfield Systems Inc.)
**Status:** Founder DECIDE pending. Buildable blueprint for 24/7 autonomous parallel operation.
**Date:** 2026-06-30
**Supersedes:** v0.1 (skeleton). This version adds: 24/7 cloud operation, self-healing, research/AI stations, hardened ROI engine, Live-Brain control plane, blast-radius limits, and the **self-improvement safety doctrine**.

**Stack:** Python (engine + workers) · Cloudflare (Workers, Durable Objects, Queues, KV, R2, Cron, Workers AI) · Railway (orchestrator + heavy/long jobs) · Supabase (truth-layer state + receipts) · Perplexity / computer-use researcher (research station) · multi-provider AI stations (Claude/GPT/Gemini as specialist roles) · Git (canonical per line).

---

## 0. Thesis (hardened)

Run **10 revenue lines in parallel, fully on cloud, 24/7, self-improving and self-healing**, each a full-stack agentic unit, all standing on an **immutable governance substrate** that the lines **cannot weaken from the inside**. The founder manages the entire fleet through the **Live Brain** (one conversational + dashboard control plane), approving only irreversible actions. ROI receipts rank the lines and reallocate compute automatically.

**The risk reframe (founder's, accepted):** *Not* running this is the larger risk — a solo founder cannot hand-run 10 lines. The danger of running it is not autonomy itself; it is **autonomy without a floor it can't dissolve**. This spec's hardening exists to make 24/7 autonomy *survivable*, which is the only way it's also *useful*.

> **The one law that makes self-improvement safe:** *A self-improving system must never be able to improve away its own brakes.* The substrate (verifier, gate, identity invariant, claims policy, bounds, kill-switch) is **immutable from inside the loop**. Only the founder, out-of-band, changes the floor. The loop improves *work*; it can never edit the *rules that judge the work*.

---

## 1. Operating modes (the whole system has gears, per line)

| Mode | What runs without founder | What needs a tap | When a line is here |
|---|---|---|---|
| **OBSERVE** | research, planning, dry-runs, measurement | everything that ships | brand-new line |
| **CONFIRM** | plan→produce→verify | every ship | unproven line |
| **SEMI** | plan→produce→verify→gate; ships surface for veto | nothing blocks, founder can veto live stream | a few clean windows |
| **AUTO-24/7** | full loop incl. ship, within bounds | only irreversible/over-bound actions | many clean windows + behavior-pass history |
| **HEAL-ONLY** | self-healing fixes only (no new features) | escalations | a line that's degraded |

A line **earns** its way up one gear at a time, by track record, per line. **Nothing starts at AUTO.** The Hub can drop any line down a gear instantly (or to FROZEN) on anomaly.

---

## 2. Three layers + two new planes

```
        ┌──────────────────────────────────────────────────────────────┐
        │  LIVE BRAIN CONTROL PLANE  (conversational + dashboard)        │
        │  founder asks "how are the lines?" / "pause distribution" /    │
        │  "why did Forge line drop?" — Brain answers from receipts,     │
        │  routes commands, surfaces irreversible taps. READ truth,      │
        │  ROUTE commands. It cannot edit the substrate.                 │
        └───────────────┬──────────────────────────────────────────────┘
                        │
        ┌───────────────▼──────────────────────────────────────────────┐
        │  HUB ORCHESTRATOR (Railway)  spawn/pause/kill, budget, gates   │
        └───────────────┬──────────────────────────────────────────────┘
                        │
   ┌────────────────────▼───────────────────────────────────────────────┐
   │  LINE ENGINE × 10   (24/7 cloud, parallel, isolated)                 │
   │  PLAN → PRODUCE → VERIFY → SHIP → MEASURE → (SELF-HEAL ⟲)            │
   │     ↑ fed by RESEARCH + AI STATIONS                                  │
   └────────────────────┬───────────────────────────────────────────────┘
                        │ all stand on ↓ (IMMUTABLE FROM INSIDE)
   ┌────────────────────▼───────────────────────────────────────────────┐
   │  SUBSTRATE (the floor)  verifier · gate · identity · claims policy   │
   │  · bounds · mutation guard · KILL-SWITCH · receipts                  │
   └──────────────────────────────────────────────────────────────────────┘

   NEW PLANES feeding the engine:
   • RESEARCH STATION  (Perplexity / computer-use)  → market + competitor + truth signals
   • AI STATIONS       (Claude/GPT/Gemini as roles) → specialist producers + adversarial critics
```

---

## 3. SUBSTRATE — now with kill-switch + immutability (the hardening core)

Inherits all of v0.1 §3 (per-receipt PASS, content identity, token auth, mutation guard, receipts). **Added for 24/7:**

### 3.1 Immutability from inside the loop
- The substrate code, the verifier, the gate, the claims policy, the per-line bounds, and the kill-switch live behind a **founder-only identity** (separate account/key, the verifier-account pattern already built).
- **No line, no station, no self-heal step can modify them.** Any artifact whose diff touches a substrate path → **auto-FAIL, auto-FREEZE the proposing line, Hub alert.** This is the single most important 24/7 guarantee.
- The constitution/SSOT is git-locked; changes require a founder commit from the founder identity, out-of-band from the loop.

### 3.2 Global kill-switch + per-line freeze
- One **KILL** flag (KV, founder-only) → halts all shipping fleet-wide in <1 tick; lines keep observing/measuring but ship nothing.
- Per-line **FREEZE** → that line stops shipping, others continue.
- Kill/freeze are **fail-closed**: if the flag can't be read, the system behaves as if KILLED (no ship). Default-deny.

### 3.3 Blast-radius limits (every line, every window)
- `max_cost_usd`, `max_ships`, `max_external_sends`, `max_parallel_sandboxes` per line per window.
- Breaching any limit → line auto-FREEZE + Hub alert. A runaway line burns only its own bounded budget, then stops.
- **Circuit breaker** (already in your kernel): N consecutive failures on a line → open circuit → line drops to HEAL-ONLY.

### 3.4 Anomaly detection
- Cheap heuristics on the receipt stream: ship-rate spike, cost spike, behavior-pass-rate drop, claim-set drift, identity-mismatch, status-signal staleness.
- Any anomaly → auto drop the line one gear (e.g. AUTO→SEMI) and alert. **The system degrades toward safety, never toward more autonomy, on uncertainty.**

---

## 4. LINE ENGINE — full-stack, now with SELF-HEAL

Five stages (v0.1 §4) + a sixth continuous loop.

### 4.1 SELF-HEAL ⟲ (the self-improvement loop, bounded)
Runs continuously per line, but **strictly bounded**:

```
DETECT   → measurement/behavior-probe/health-check finds a degradation
           (ROI down, behavior FAIL, status red, error rate up)
DIAGNOSE → AI station proposes a CAUSE (adversarial: a 2nd station critiques it;
           convergence from same-base-model stations = warning, not validation)
PROPOSE  → produce a candidate FIX (content/plan/config — NEVER substrate)
VERIFY   → substrate verifier + line verify profile (claims, behavior)
SHIP     → per line ship_policy (gate applies)
RE-PROBE → behavior probe confirms the fix actually fixed it; if not → revert
```

**Self-heal is allowed to change:** line content, plans, outreach copy, prompts, routing, the knowledge bundle.
**Self-heal is FORBIDDEN to change:** the substrate, the claims policy, the bounds, the kill-switch, the verifier, the gate — anything that judges it. (Enforced by §3.1.)

> This is what makes "self-improvement 24/7" survivable: the system can fix and improve its *work* forever, but it physically cannot loosen the *rules*. It optimizes inside the box; it cannot widen the box.

### 4.2 Improvement requires REAL signal, not assumption
- A self-heal "fix" only counts as successful if RE-PROBE shows measurable improvement against the live signal (§6.2 status, §7 ROI). No "looks fine" — a fix that doesn't move the metric is **reverted automatically**.
- This kills the lazy-agent failure mode structurally: improvement is defined by *measured effect*, not by an agent declaring success.

---

## 5. RESEARCH STATION + AI STATIONS (the new producers)

### 5.1 Research Station (Perplexity / computer-use)
- A dedicated cloud research worker that runs **live market/competitor/truth research** on a schedule and on-demand.
- Feeds PLAN (what to make), feeds claims-truth (is "Forge available" actually true right now — computer-use can *open the URL and check*), feeds distribution (who to reach, what's resonating).
- **Output is a builder artifact under author≠subject** — research is SUBMITTED, not authoritative; a critic station challenges it before it drives spend.
- This is also a **truth source for the status signal** (§6.2): computer-use can verify a live surface works, not just ping it.

### 5.2 AI Stations (specialist roles, adversarial by design)
- Multiple model providers, each a **role**, not a vote: Producer, Critic, Diagnoser, Copywriter, Researcher.
- **Hard rule (banked tonight):** convergent recommendations from stations sharing a base model = **correlated agreement, not independent validation** → treated as a single voice. Divergence is preserved and surfaced to the founder, never collapsed into false consensus.
- Critic stations run **adversarial passes** on every producer artifact (invented metrics, unverified claims, grade-its-own-homework, phantom components) before VERIFY. This is the Critic-Circle you've run manually, now in the loop.

---

## 6. LINE-LEVEL VERIFY (hardened — the truth/behavior floor)

All of v0.1 §6 (commercial-claims source, live status signal + Cron health-check, warmth-always/confidence-tracks-signal policy, behavior probe + hard sanitizer). **Added:**

### 6.1 Claims-truth binding via computer-use
- For any claim that asserts a live capability ("Forge available", "demo bookable"), the status signal is refreshed by **computer-use actually exercising the surface**, not just an HTTP ping. A claim is "fresh+good" only if the *capability* was verified, not just that the endpoint returned 200.

### 6.2 Behavior probe is mandatory pre-promotion
- No line advances a gear (CONFIRM→SEMI→AUTO) until its behavior-pass-rate over the trailing window exceeds threshold. **Gear is earned by behavior, not just by clean deploys.**

### 6.3 Regulatory honesty profiles (commercial hardening)
- TrustField/financial lines carry a **regulatory-honesty verify profile**: no unsubstantiated regulatory-status claims, CASL-compliant outreach, deploy-truth law (live byte-fetch must match disk). These are line verify rules, fail-closed.

---

## 7. ROI ENGINE (hardened — compute follows money)

### 7.1 Normalized ROI receipt (every line, every window)
```
roi_receipt = {
  line_id, window_id, mode,
  plans_run, shipped, blocked, reverted,
  roi_metric, roi_value, roi_value_usd,     # leads/units/activations → $
  cost_usd (sandbox+API+research),
  net_usd = roi_value_usd - cost_usd,
  behavior_pass_rate, status_freshness,     # was it honest + working?
  self_heals_attempted, self_heals_successful
}
```

### 7.2 Compute reallocation (automatic, founder-overridable)
- Fleet compute budget flows toward highest `net_usd`. Producing lines get more parallel sandboxes; `net_usd <= 0` for K windows → auto-pause + Hub flag.
- **Founder override always wins** — the Hub can pin budget to a strategic line regardless of short-term ROI (a line you're investing in before it converts).
- **No line can increase its own budget** — only the Hub/founder allocates. (A self-improving line cannot give itself more compute; another box it can't widen.)

### 7.3 Commercial funnel as a measured line
- Distribution line's ROI isn't "content shipped" — it's **qualified leads / replies / booked demos**, measured end-to-end. The funnel stages (reach → engage → proof → demo → close) are receipt-tracked so the system optimizes toward *money*, not activity.

---

## 8. LIVE BRAIN CONTROL PLANE (manage the fleet by talking to it)

The founder runs the company through the Brain.

### 8.1 What it does
- **Read truth from receipts:** "How are the lines?" → ROI per line, modes, anomalies, pending taps. All grounded in receipts (§6 claims rules apply to the Brain itself — it never fakes fleet status).
- **Route commands:** "Pause distribution", "Drop Forge line to SEMI", "Why did TrustField net go negative?" → executes via Hub, or explains from receipts.
- **Surface taps:** irreversible actions queue here for one-tap founder approval.
- **Self-status honesty:** the Brain uses the live status signal — if it doesn't have fresh data on a line, it says so and fetches, never guesses (the §6.3 policy applied to fleet management).

### 8.2 What it CANNOT do
- It cannot edit the substrate, change bounds, lift the kill-switch, or grant a line a gear. It **routes** founder intent to the founder-only control path; the founder authorizes. Brain routes, founder clicks. (The Brain is a powerful read/route surface, not a privileged actor.)

---

## 9. 24/7 CLOUD OPERATION (concrete)

| Function | Cloud mechanism |
|---|---|
| Per-line continuous loop | **Railway** orchestrator process per line (or worker pool) + heartbeat/watchdog |
| Per-plan execution | **Cloudflare Workers** (short tasks) / Railway sandbox (heavy) — one per plan, isolated |
| Parallel queues | **Cloudflare Queues**, one per line, backpressure-aware |
| Live state / desired-vs-observed | **Supabase** (atomic reconciler writes observed; founder/Hub writes desired) |
| Receipts (the spine) | **Supabase** table + **R2** for artifacts — *MUST fix `SUPABASE_URL` from Railway first* |
| Scheduled health/research | **Cloudflare Cron** → research station + status-signal refresh |
| Edge surfaces | **Cloudflare Workers** (Brain, Forge, status, verifier) |
| Watchdog / self-recovery | kernel watchdog + circuit breaker (already built) — restarts dead line loops, opens circuits |
| Cost metering | per-line meter in receipts; Hub enforces blast-radius limits (§3.3) |

### 9.1 Always-on safety daemons
- **Watchdog:** detects a hung/dead line loop → restarts or freezes, alerts.
- **Reconciler:** keeps desired (founder) vs observed (system) state coherent; resolves split-brain atomically (the law you already established: `assignment.active` = founder desired only; reconciler writes observed).
- **Budget governor:** kills any line breaching cost/ship limits.
- **Kill-switch listener:** every shipping path checks KILL/FREEZE before acting, fail-closed.

---

## 10. BUILD SEQUENCE (rested — bounded, gated, ROI-first)

**Phase A — Engine + substrate immutability**
1. `line_engine/` five-stage package (extract from tonight's Brain loop).
2. Substrate immutability guard (§3.1): any diff touching substrate paths → auto-FAIL+FREEZE.
3. Global kill-switch + per-line freeze (§3.2), fail-closed. **Test the kill-switch first — before anything ships autonomously, prove you can stop the fleet in one tick.**

**Phase B — One line, OBSERVE→CONFIRM, with line-verify**
4. Brain line end-to-end; add claims source, status signal + Cron health-check (computer-use truth check), behavior probe + hard sanitizer (fix the PASS leak as code).
5. Run in CONFIRM. Prove behavior-pass gating.

**Phase C — Self-heal (bounded) + research/AI stations**
6. Add SELF-HEAL ⟲ to the Brain line; prove a degradation gets detected, fixed, re-probed, and that a non-improving fix auto-reverts.
7. Wire Research Station (Perplexity/computer-use) + one Critic station (adversarial pass).

**Phase D — Second line + Hub + ROI engine**
8. Instantiate Distribution from config only (no new engine code). Funnel-stage ROI receipts.
9. Hub orchestrator (spawn/pause/kill, budget governor, anomaly→degrade). Two lines parallel, isolated, ROI-ranked.

**Phase E — Live Brain control plane**
10. Brain reads fleet truth from receipts + routes commands + surfaces taps. (Brain manages the fleet, can't edit the floor.)

**Phase F — Scale to 10 + earn AUTO per line**
11. Add 8 line configs. Generate plan batches (cheap). Each line climbs OBSERVE→CONFIRM→SEMI→AUTO **individually, by track record**. Run 24/7. Compute follows ROI.

**Phase 0 blockers (must clear before Phase D parallel scale):**
- Fix `SUPABASE_URL` not resolving from Railway (`receipt_row_id: null`) — *no receipts = no measurement = no fleet*.
- Verifier repo-aware for every line's git ref.
- Public API routing defects (e.g. `/api/site/stats/v1` returning HTML) fixed on sales surfaces.

---

## 11. THE HARDENING, IN ONE TABLE (why 24/7 is survivable)

| Risk of 24/7 autonomy | The brake that makes it survivable |
|---|---|
| System optimizes away its own guardrails | **Substrate immutable from inside; loop can't edit the rules that judge it** (§3.1) |
| A line goes rogue / runs away | Blast-radius limits + circuit breaker + auto-freeze (§3.3) |
| Can't stop it in time | Global kill-switch + per-line freeze, fail-closed, <1 tick (§3.2) |
| It ships lies (fake "available") | Claims source + computer-use truth check + behavior probe (§6) |
| It ships garbage | Substrate verifier (validity+identity) + adversarial critic stations (§5.2) |
| "Improvement" that isn't | Self-heal fix must move a real metric or auto-revert (§4.2) |
| Lazy "everything's fine" | Improvement defined by measured effect, status by real check (§4.2, §6.1) |
| Drifts toward more autonomy on uncertainty | Anomaly → degrade one gear toward safety, never up (§3.4) |
| Founder loses oversight | Live Brain reads truth + surfaces taps; founder taps irreversible (§8) |
| A line steals fleet compute | Only Hub/founder allocates budget; no line raises its own (§7.2) |
| Correlated AI agreement looks like validation | Same-base-model convergence = warning; divergence preserved (§5.2) |

**Every one of these brakes is what lets you run the fleet 24/7 instead of watching it. The hardening is not the opposite of speed — it is the precondition for unattended speed.**

---

## 12. The commercial truth (so this is survival, not a science project)

- A line is real only when its ROI metric is **money-shaped**: leads, demos, activations, intros, dollars — receipt-tracked end-to-end.
- The **Distribution line is the survival line** — agentic marketing/distribution producing qualified pipeline 24/7. Build it second (right after Brain proves the engine), because it's the one that brings money in.
- Every line's claims must pass the **plausibility + serviceability** test (SSOT v6, D2): can you credibly say it, and can you serve who shows up? The status signal enforces serviceability; the claims source enforces plausibility.
- **Honesty is the product's edge.** A receipts-based company whose Brain admits what it doesn't know and *gets the answer* out-converts a bot that fakes confidence. Warmth always, confidence earned — that's commercial, not cautious.

---

## 13. One-line summary

**Ten money-shaped lines, full-stack, parallel, 24/7 on cloud, self-improving and self-healing — each able to optimize its work forever but physically unable to weaken the floor it stands on; managed by talking to the Live Brain; ranked and funded by ROI receipts; stoppable in one tick. The hardening is what makes the autonomy survivable, and the autonomy is what makes a solo founder survive.**

---

*v0.2 HARDENED — founder DECIDE pending. Build Phase A rested. Test the kill-switch before anything ships. The floor is done; this is the organism that runs on it.*
