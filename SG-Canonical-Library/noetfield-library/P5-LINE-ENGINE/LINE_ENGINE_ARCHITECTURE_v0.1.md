# LINE ENGINE — Architecture Spec v0.1

**Author:** Sina Kazemnezhad (Noetfield Systems Inc.)
**Status:** Founder DECIDE pending — this is a buildable blueprint, not yet ratified.
**Date:** 2026-06-30
**Stack:** Python (line logic, workers) · Cloudflare (Workers, KV, Queues, R2, Cron) · Railway (long-running orchestration) · Supabase (truth-layer state) · Git (canonical source per line)

---

## 0. One-paragraph thesis

A solo founder in June 2026 does not hire a sales team, a content team, or a research team. The founder builds **one full-stack agentic line-engine** and instantiates it **N times** — one instance per revenue line (distribution, factory, Brain, Forge, TrustField, NOOS, …). Each instance runs its own plans in parallel, on a **shared governance substrate** that guarantees no line ships garbage, fakes a claim, or corrupts another line. The founder sits at a **Hub**, approves only irreversible actions, watches ROI per line, and kills dead lines. **Brain routes. Worker ships. You click.**

The governance loop built on 2026-06-30 (verifier + gate + content-identity + token-auth + mutation-guard) is **NOT the product** — it is the **safety floor** every line stands on. This spec defines the lines that run on top.

---

## 1. The core insight that shapes everything

The bottleneck was never planning capacity (1000 plans across 10 lines is one prompt). The bottleneck was that **no parallel execution structure exists**, so planning has nowhere to run, and the founder kept perfecting a single row (the deploy loop) instead of building the board.

**Design consequence:** build the **Line Engine** (the reusable full-stack unit) ONCE. Ten lines is then *configuration*, not ten builds. Feeding 1000 plans is trivial because the engine *consumes* plans.

---

## 2. The three structural layers

```
┌─────────────────────────────────────────────────────────────┐
│  HUB  (founder control plane)                                │
│  - spawns / pauses / kills line instances                    │
│  - approves only IRREVERSIBLE actions                        │
│  - sees ROI per line, reallocates                            │
└───────────────┬─────────────────────────────────────────────┘
                │ tap-only
┌───────────────▼─────────────────────────────────────────────┐
│  LINE ENGINE × N   (one full-stack instance per line)        │
│  ┌────────┐ ┌─────────┐ ┌────────┐ ┌──────┐ ┌──────────┐    │
│  │ PLAN   │→│ PRODUCE │→│ VERIFY │→│ SHIP │→│ MEASURE  │→Hub │
│  └────────┘ └─────────┘ └────────┘ └──────┘ └──────────┘    │
│  isolated workspace · own git lane · own ROI metric · queue  │
└───────────────┬─────────────────────────────────────────────┘
                │ every line stands on ↓
┌───────────────▼─────────────────────────────────────────────┐
│  SUBSTRATE  (built 2026-06-30 — the safety floor)            │
│  independent verifier · promotion gate · content-identity    │
│  invariant · token auth (no human switching) · mutation      │
│  guard (fail-closed) · receipts on every action              │
└──────────────────────────────────────────────────────────────┘
```

**The substrate is shared. The Line Engine is replicated. The Hub is singular.**

---

## 3. The SUBSTRATE (already built — recorded here as the floor)

Every line inherits these guarantees. No line may bypass them.

| Guarantee | Mechanism (built 2026-06-30) | Invariant |
|---|---|---|
| **Independent verification** | Verifier Worker on **separate Cloudflare account** (`b7282b4a…`), reads candidate repo via GitHub App, emits PASS only when independence proven | `author_id ≠ subject_id`; PASS computed per-receipt from identity/path fields, never declared by a flag |
| **Promotion gate** | `promotion_gate.py` — confirm-each-time; refuses unattended `--execute-deploy`; refuses non-verified deploy command | No PASS → no ship. No fresh receipt → no ship. |
| **Content identity** | `deploy-verified` mode ships the **committed/verified artifact as-is**, no refresh/regeneration at ship time | `committed_sha == verified_sha == shipped_sha` or auto-rollback |
| **Token auth** | Per-account scoped tokens in `~/.sina/secrets/` (gitignored); each command sets `CLOUDFLARE_API_TOKEN` inline | No human login-switching; both accounts usable in one session; token values never printed/committed |
| **Mutation guard** | `SOURCEA_PHASE2_MUTATION_TRIALS` real flag (default FALSE) + enforcing reader, checked before any mutation step | Fail-closed; founder-only flip |
| **Auditability** | Receipt written for every candidate, verdict, deploy, rollback | Every action has a signed, queryable record |

> **Rule:** the substrate verifies *validity + identity*. It does **NOT** verify *truth of claims* or *quality of content* or *correctness of behavior*. Those are line-level concerns (§6, §7) — this is the single most important lesson banked tonight.

---

## 4. The LINE ENGINE — the reusable full-stack unit

One Python package, instantiated per line via config. Five stages, each a bounded step with a receipt.

### 4.1 Stage contract

```
PLAN     → emits N candidate plans for this line's offer (cheap, batch)
PRODUCE  → an isolated sandbox worker executes ONE plan → produces an artifact
VERIFY   → substrate verifier + line-level checks (claims, behavior) → PASS/FAIL
SHIP     → on PASS (+ gate policy), push artifact to the line's real surface
MEASURE  → record ROI signal; report to Hub; feed next-plan selection
```

Each stage:
- runs in an **isolated workspace** (own dir, own git lane, own sandbox);
- is **bounded** (time, cost, scope limits per line);
- writes a **receipt** (consumed by Hub + measurement);
- **fails closed** (any stage failure halts that plan, never the line, never other lines).

### 4.2 Line config (the only thing that differs across 10 lines)

```yaml
# lines/distribution-v1.yaml
line_id: distribution
offer_ref: offers/distribution.md        # what this line sells (founder-authored)
roi_metric: leads_qualified               # what "produced" means in money terms
surface:                                   # where SHIP pushes to
  type: outbound                           # outbound | site | repo | brain | api
  targets: [linkedin, email, x]
ship_policy: confirm_each_time             # confirm_each_time | semi_auto | gated_auto
artifact_type: outreach_sequence           # what PRODUCE makes
verify_profile: commercial_claims_v1       # which line-level checks apply (§6)
bounds:
  max_parallel_plans: 5
  max_cost_usd_per_window: 20
  window_hours: 2
  mutation_allowed: false
```

10 YAML files = 10 lines. Same engine.

### 4.3 Line types (all share the engine; differ only by surface + verify profile)

| Line | artifact_type | surface | roi_metric | verify_profile |
|---|---|---|---|---|
| Distribution | outreach/content | outbound | leads / replies | commercial_claims + CASL |
| Factory | product unit | repo/site | units shipped | content + behavior |
| Brain (live chat) | knowledge bundle | brain worker | answer-quality / conversion | claims + behavior + identity |
| Forge | build env feature | repo/site | activations | content + behavior + status-signal |
| TrustField | compliance asset | site/api | qualified intros | claims + regulatory honesty |
| NOOS | governance feature | repo | adoption | content + identity |
| … | … | … | … | … |

> All ten run the **same five-stage engine**. A line is a *config + an offer + a surface + a verify profile*. Nothing else.

---

## 5. The HUB — founder control plane

The Hub is the only thing the founder touches. It does not do work; it *routes and gates*.

### 5.1 Responsibilities
- **Spawn/pause/kill** line instances and individual plans.
- **Surface irreversible actions** for tap approval (ship-to-live, spend above bound, external send).
- **Show ROI per line** (live dashboard) and let founder reallocate plan budget toward producing lines.
- **Kill dead lines** — a line producing no ROI after K windows gets paused automatically and flagged.

### 5.2 The tap-only principle
The founder approves **only irreversible actions**. Everything reversible (plan generation, sandbox production, verification, measurement) runs without a tap. The gate (§3) enforces which actions require a tap per line's `ship_policy`.

```
ship_policy: confirm_each_time  → every ship needs a tap (new/risky lines)
ship_policy: semi_auto          → auto-verify+gate; ship surfaces for veto, doesn't block
ship_policy: gated_auto         → auto-ship IF identity holds + claims pass + within bounds
```

A line **earns** its way from `confirm_each_time` → `semi_auto` → `gated_auto` by accumulating clean windows (the same trust-by-track-record discipline proven tonight). No line starts at `gated_auto`.

---

## 6. LINE-LEVEL VERIFY — the gap the substrate can't close (banked tonight)

The substrate proves *valid + identical*. It cannot prove *true*, *good*, or *behaving*. These checks live in the **verify profile** per line and are the difference between "shipped" and "actually working / not lying."

### 6.1 Commercial-claims governance (Type 1 — D1/D2, founder-authored)
- Each line draws claims **only** from a founder-authored **approved-claims source** (`offers/<line>.md`).
- The verifier checks the artifact asserts **only** claims in the approved set.
- Claims outside the set → FAIL. (Solves: "Brain said Forge is available and the founder didn't know if it was true.")

### 6.2 Live status signal (closes the lazy-agent gap)
- A small machine-readable status file per claim-dependent thing: `status/<thing>.json = {status, last_checked}`.
- A **scheduled health-check** (Cloudflare Cron) pings the real endpoint (e.g. Forge Terminal URL) and writes status+timestamp.
- Confident claims require a **fresh + good** signal. Stale → the line must use the graceful gear (§6.3).
- **This structurally fixes laziness:** an agent cannot "assume fine" — the signal is red until a real check makes it green. The line's ability to claim confidently *depends on* the thing actually working.

### 6.3 Conversational / commercial policy — warmth always, confidence earned
Decouple two dials so "enticing" and "honest" stop competing:
- **Warmth: always high.** Every output is helpful, momentum-forward, human — regardless of status.
- **Confidence: tracks the live signal.**
  - signal fresh+good → confident, specific claim;
  - signal stale/unknown → **not** cold ("I can't confirm") and **not** fake ("yes") → *enticing + escalating*: sell the value, offer a live link / a person / an alternative;
  - signal bad → honest redirect to a working alternative ("being upgraded — here's what works now").
- Uncertainty is a **selling opportunity** (honesty = the proof of a receipts-based product), not a defensive crouch.

### 6.4 Behavior test (closes "deployed ≠ behaving")
- After SHIP, the line **probes its own live surface** with a fixed prompt/scenario set and checks compliance (no internal jargon leak, answers-first, ≤1 CTA, no fake claim, claims grounded in signal).
- A deploy is **not "done"** until the behavior probe passes. (Solves: bundle live + rule present + runtime still leaked `PASS`.)
- Hard enforcement (e.g. output sanitizer in the Worker) for things that must **never** leak — code, not a bundle suggestion the model can ignore.

> **Division of labor, locked:** Founder authors *what may be claimed* (Type 1, strategy). The loop enforces the line *stays inside the approved set + backs confident claims with a fresh signal + behaves correctly* (Type 2, governance). The verifier can't decide the right claim — but it can enforce the line never exceeds the founder's approved claims.

---

## 7. MEASURE — ROI is the only thing that ranks lines

Every line reports a normalized ROI signal to the Hub each window. The Hub reallocates plan budget toward producing lines and pauses dead ones.

```
roi_receipt = {
  line_id, window_id,
  plans_run, plans_shipped, plans_blocked,
  roi_metric, roi_value,           # leads, units, activations, intros, $
  cost_usd,                        # sandbox + API spend
  net = roi_value_in_$ - cost_usd,
  status_signal_freshness,         # were claims backed?
  behavior_pass_rate               # did shipped artifacts behave?
}
```

**Reallocation rule:** budget flows to highest `net` per window. A line with `net <= 0` for K consecutive windows → auto-pause + Hub flag. **The founder doesn't guess which line works — the receipts rank them.**

---

## 8. TECH STACK — concrete

| Concern | Choice | Why |
|---|---|---|
| Line logic / stage engine | **Python** package `line_engine/` | matches existing kernel work (circuit breaker, reducer, lease, watchdog); reusable, testable |
| Long-running orchestration | **Railway** worker(s) | already the prod stack; runs the engine loop per line |
| Edge surfaces (Brain, Forge, status, verifier) | **Cloudflare Workers** | already live; low-latency public surfaces |
| Parallel plan queue | **Cloudflare Queues** (or Railway worker pool) | one queue per line; isolated; backpressure-aware |
| Truth-layer state | **Supabase** | desired/observed state, receipts index *(NOTE: fix `SUPABASE_URL` not resolving from Railway → `receipt_row_id: null` — known blocker, must resolve before parallel scale)* |
| Artifact storage | **Cloudflare R2** | produced artifacts, bundles, reports |
| Canonical source per line | **Git lane** (branch/repo per line) | `main = truth`; verifier reads from git ref |
| Scheduled health-checks | **Cloudflare Cron Triggers** | keep status signals fresh (§6.2) |
| Secrets / auth | **scoped API tokens** in `~/.sina/secrets/` | per-account, gitignored, no login-switching (§3) |
| Hub UI | thin web app (Codex-built, isolated repo) | founder dashboard; governance agents are weak at UI — keep UI lane separate |

### 8.1 Repo layout (proposed)
```
line-engine/
  line_engine/            # the reusable engine (Python)
    plan.py produce.py verify.py ship.py measure.py
    sandbox.py bounds.py receipts.py
  lines/                  # 10 YAML configs
    distribution-v1.yaml factory-v1.yaml brain-v1.yaml forge-v1.yaml ...
  offers/                 # founder-authored approved-claims sources (Type 1)
    distribution.md forge.md trustfield.md ...
  status/                 # live status signals (§6.2)
  hub/                    # control-plane API (Railway) — UI lives in separate Codex repo
  substrate/              # references to verifier/gate (the floor; mostly already built)
```

---

## 9. ISOLATION — why one line can't break another

- **One sandbox per running plan** (own workspace dir, own env, own token scope, own cost meter).
- **One git lane per line** (a line's artifacts never touch another line's `main`).
- **Bounded per line** (`max_parallel_plans`, `max_cost`, `window_hours` from config) — a runaway line burns only its own budget, then halts.
- **Fail-closed everywhere** — a plan failure halts that plan; a line failure pauses that line; neither propagates.
- **Substrate gate is shared but per-artifact** — the gate evaluates each artifact independently; one line's bad artifact is blocked without affecting another line's good one.

---

## 10. BUILD SEQUENCE (rested, not at 6am)

> Each step is bounded, produces a receipt, and is founder-gated where irreversible. Do **not** flip any line to `gated_auto` until it has accumulated clean windows (trust-by-track-record).

**Phase A — Engine skeleton (1 line, confirm-each-time)**
1. Build `line_engine/` five-stage package; one line (Brain — already has substrate + surface).
2. Run Brain line end-to-end in `confirm_each_time` on the existing substrate. (You already did the equivalent tonight — this formalizes it as the engine.)

**Phase B — Line-level verify (close the banked gaps)**
3. Add commercial-claims source for Brain (`offers/forge.md` etc.) + claims check in `verify.py`.
4. Add live status signal + Cloudflare Cron health-check for Forge/proof/platform.
5. Add behavior-probe step + hard output sanitizer (the `PASS`-leak fix as code).

**Phase C — Second line (prove replication)**
6. Instantiate Distribution line from config only (no new engine code). Run `confirm_each_time`.
7. Confirm two lines run in parallel, isolated, on shared substrate, ROI reported per line.

**Phase D — Hub + measurement**
8. Build Hub control-plane API (spawn/pause/kill, ROI dashboard). UI in separate Codex repo.
9. Wire `roi_receipt` + reallocation rule + auto-pause for dead lines.

**Phase E — Scale to 10**
10. Add remaining 8 line configs. Generate plan batches (cheap). Run all in `confirm_each_time` → earn `semi_auto` → earn `gated_auto` per line, individually, by track record.

**Phase F — Resolve standing blockers before parallel scale**
- Fix `SUPABASE_URL` not resolving from Railway (`receipt_row_id: null`) — receipts must persist for measurement to work.
- Confirm verifier reads every line's git ref (repo-aware, already done for SourceA).
- Confirm no stale duplicate verifier on main account.

---

## 11. WHERE TONIGHT'S CATCHES PLUG IN (nothing wasted)

| Catch banked 2026-06-30 | Where it lives in the Line Engine |
|---|---|
| PASS computed per-receipt, not by flag | Substrate verifier (§3) — inherited by all lines |
| deploy-verifies-X-ships-Y bug → content identity | Substrate SHIP guarantee (§3) — every line |
| token auth, no login-switching | Substrate auth (§3) — every line |
| mutation guard real + fail-closed | Substrate (§3); per-line `mutation_allowed` bound (§4.2) |
| verifier checks validity not truth/behavior | Line-level VERIFY (§6) — claims + status + behavior |
| commercial claims = founder DECIDE (D1/D2) | `offers/<line>.md` approved-claims source (§6.1) |
| lazy agents assume "fine" | Live status signal + Cron health-check (§6.2) |
| enticing-but-honest balance | Warmth-always / confidence-tracks-signal policy (§6.3) |
| deployed ≠ behaving (PASS leak) | Behavior-probe step + hard sanitizer (§6.4) |
| convergent agent agreement ≠ validation | Hub keeps founder as reconciling decision-maker; divergence preserved, not consensus-collapsed |

---

## 12. The one-line summary

**Build the full-stack Line Engine once. Instantiate it per revenue line. Stand all lines on the governance substrate as the safety floor. Let ROI receipts rank the lines. Founder taps only the irreversible. Brain routes, worker ships, you click — across ten lines in parallel, none able to lie or break another.**

---

*v0.1 — founder DECIDE pending. Build Phase A when rested. The substrate is done; this is what runs on it.*
