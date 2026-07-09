# NOETFIELD COHERENT SYSTEM SPEC v1
## One living system: Brain · Spine · Nerves · Gates · Machines

Status: DECLARED (becomes VERIFIED per-section when its enforcement check runs green)
Owner: founder. Enforced by: machine, via checks named in each section.
Law base: governed-autorun v3 (L1–L13, D1–D8). This spec adds no new authority — it wires existing organs together.

---

## 0. ANATOMY — canonical terminology (machine-enforceable)

Every term below is a locked definition. Enforcement: `locked-definitions-v1.json` gains a `system_anatomy` block; any receipt/report using these words differently fails the definitions lint.

| Term | Definition | Lives where |
|---|---|---|
| **BRAIN** | The routing layer: reads all lane states from the SPINE, ranks work by mission priority + ROI, emits desired-state. Never executes. | brain tick (CF worker / Action) |
| **SPINE** | The single shared truth store spanning all lanes: truth_log, cycle receipts, heartbeats, checkpoints, definitions. | Supabase portfolio-spine |
| **NERVES** | Probes that sense: external-verify, health/ready endpoints, drift checks, schedule self-registration, dashboards. Read-only. | GitHub Actions + CF + dashboard |
| **GATES** | Deterministic YES/NO functions with {decision, reason, evidence}. Never prose. | gate CLIs, verifiers (L5-frozen) |
| **MACHINES** | Isolated run units doing work: FBE motor, inbox worker, loop fleet. One writer per state cell (D2). | Railway, GHA jobs, CF workers |
| **MISSION** | Top-level goal with a value_class, budget, and definition-of-done. Parent of workflows. | mission registry |
| **WORKFLOW** | A loop serving one mission in one lane. Has registry entry, states, receipts. | workflow registry |
| **CYCLE** | One tick of one workflow. Atomic, receipted, deterministic (L13). | cycle receipts |
| **RECEIPT** | Machine-parseable proof artifact per schema. The only admissible evidence. | spine + repo receipts/ |
| **VERIFIED** | State earned by a closed green 24h window on external receipts. Everything else is DECLARED. | window receipts |

---

## 1. TRIGGER CENSUS + TRIGGER REGISTRY

Current triggers across the estate (audit baseline):

| # | Trigger | System | Kind | Status |
|---|---|---|---|---|
| T1 | CF cron `*/10` → Railway tick | SourceA | schedule | live, auto-stop on exhausted queue |
| T2 | CF cron → `repository_dispatch` | NOOS | schedule→dispatch | live, PRIMARY NOOS motor |
| T3 | GitHub native `schedule` | NOOS factory | schedule | live but laggy (backup only) |
| T4 | GHA `push` on workflow/verify paths | SourceA external-verify | event | live |
| T5 | GHA `workflow_dispatch` | both | manual | allowed for humans/API only; invalid in VERIFIED windows |
| T6 | Loop fleet crons (inbox/chain/surface/self-heal/nerve/observe) | NOOS | schedule | live |
| T7 | determinism-gate.yml | SourceA | event | live |
| T8 | Supabase-side (none yet) | — | — | gap: no DB-triggered nerve |

**LAW T-REG (new, machine-enforceable):** `data/trigger-registry-v1.json` lists every trigger: `{trigger_id, system, kind, schedule, target, valid_in_verified_window, owner_workflow}`. The sandbox_health_sweep diffs *live* trigger config (CF cron list via API, GHA workflow files on main, Railway crons) against the registry every heartbeat. Unregistered live trigger, or registered-but-dead trigger → DRIFT receipt (L12). Triggers become governed objects, not tribal knowledge.

---

## 2. DETERMINISM HARDENING — result-driven enforcement

D1–D8 exist as law; this section makes each one a *check with a run URL*:

| Rule | Enforcement check (CI, determinism-gate.yml) | Result metric |
|---|---|---|
| D1 idempotency | run same op twice → assert 1 row | dupe_rate = 0 |
| D2 single writer/CAS | concurrent advance → 1 winner + 1 REJECTED receipt | silent_overwrites = 0 |
| D3 IDs from actuals | claimed range == actual rows post-write | phantom_ids = 0 |
| D4 advance = f(acks) | fault-inject sink NACK → assert no advance | lost_rows = 0 |
| D5 replay | fold(event log) byte-matches state files | replay_diff = 0 |
| D6 time/random quarantine | grep now()/random outside scheduling edge | violations = 0 |
| D7 LLM = proposal | schema-invalid LLM output → deterministic REJECT | prose_transitions = 0 |
| D8 verify = pure fn | two runners, same spec → same verdict | runner_divergence = 0 |

Result-driven = each metric lands in the daily heartbeat with trend. A metric leaving 0 auto-files a Kaizen item (highest severity).

---

## 3. MISSION HIERARCHY — parallel work with purpose

```
MISSION (founder-authored, budgeted, value_class)
  └── WORKFLOWS (lane-assigned, registry entries)
        └── CYCLES (deterministic ticks, receipts)
```

`data/mission-registry-v1.json`:

| mission_id | value_class | Workflows | Definition of done |
|---|---|---|---|
| M1 buyer-proof | revenue_path | external-verify, 15-recipe, buyer-surface fixes | 15/15 PASS daily via Action |
| M2 factory-24-7 | proof_asset | FBE motor, loop fleet, windows | both windows VERIFIED, stay green 7d |
| M3 truth-spine | risk_reduction | sinks, migrations, self-register, replay tests | D-metrics all 0 for 7d |
| M4 kaizen | hygiene→any | improvement runner | ≥1 machine_safe/day, 0 rollback debt |
| M5 client-recipes | revenue_path | recipe queue, batch motor | queue refilled only by rubric; demos replayable |

BRAIN rule: every cycle receipt carries `mission_id`. Spend with no mission = `value_class: none` → L11 throttle. Missions are how "parallel on different missions with hierarchy" becomes enforceable instead of vibes.

---

## 4. TOOL MAP — smart use of what's already paid for

| Tool | Use today | Smart upgrade |
|---|---|---|
| **GitHub Actions** | verify, CI, loops | matrix jobs = free parallelism (15 URLs fan-out); `concurrency:` groups = D2 at CI level; environments+required reviewers = founder_gated deploys enforced by GitHub itself; artifacts = receipt storage with retention |
| **GitHub Copilot coding agent** | unused | assign Kaizen `machine_safe` items as issues → Copilot agent opens PR → determinism-gate + external-verify must pass → auto-merge label. Self-improvement executed by a THIRD party, verified by nerves — L5-safe because Copilot can't touch verifier paths (CODEOWNERS protects scripts/verify_* + laws docs, founder-only) |
| **CODEOWNERS + branch protection** | unused | machine-enforce L5/L6: verifier paths and laws docs require founder review; main requires green determinism-gate + external-verify checks. GitHub becomes the gate executor, not the agent's honor system |
| **repository_dispatch** | NOOS motor | standard BRAIN→machine dispatch verb for both repos; client_payload carries {mission_id, workflow_id, op_key} — deterministic, idempotent dispatch |
| **CF Workers** | cron, proxy, intake | brain-tick worker (§5); queue backpressure sensor; edge IDLE decisions (already live) |
| **Railway** | FBE motor | deploy SHA in /health (L12); machine start/stop API (Tier 2, parked) |
| **Supabase** | sinks | THE SPINE: one portfolio-spine project, schemas per lane, RLS per worker; pg_cron as T8 nerve (stale-lane detector inside the DB itself) |

---

## 5. THE BRAIN — bridges, not a new authority

Missing today: lanes report to the spine but nothing *reads across* lanes and routes. The Brain is that reader. It is NOT a second reconciler (L1): it emits desired-state artifacts; each lane's reconciler remains sole executor in its sandbox.

**brain-tick** (CF worker or GHA cron, every 15m):
1. READ spine: latest cycle receipts, heartbeats, D-metrics, window states, founder_blocked, Kaizen backlog — all lanes.
2. RANK: mission priority → ROI → age. Detect cross-lane conditions no single lane sees (e.g. SourceA queue exhausted + M5 says refill rubric-only + NOOS idle slot free).
3. EMIT: `data/brain-desired-state-v1.json` rows: `{mission_id, workflow_id, directive: run|hold|throttle|escalate, reason, op_key}` + repository_dispatch to the target repo.
4. RECEIPT: brain-tick receipt to spine (it is itself a governed cycle: cost, value_class, evidence).
5. FOUNDER SURFACE: one daily brain digest — missions RAG-status, founder_blocked aging, founder_gated Kaizen queue by ROI, D-metric trends. One artifact replaces reading N agent reports.

**Bridges that make it one organism:**
- B1 SourceA lane → spine (exists: truth_log, cycle receipts)
- B2 NOOS lanes → spine (exists: noetfield_truth_log, self-register)
- B3 spine → dashboard (exists: read-only, STALE_DATA rule)
- B4 spine → BRAIN → repository_dispatch → machines (NEW — the missing efferent path)
- B5 GitHub (runs, PRs, Copilot) → spine via self-register steps (partial → standardize `if: always()` register on every workflow)
- B6 founder ↔ system: brain digest out; founder decisions in as gate receipts (NOOS-C-01 class)

**Brain safety:** brain directives are proposals to reconcilers (D7 applies to the Brain too). A lane may reject a directive with BLOCKED_WITH_REASON. Brain cannot edit verifiers, laws, budgets, or scope maps — those stay founder_gated. Brain has its own L11 budget and can be throttled like any workflow.

---

## 6. WORKER MANAGEMENT

| Worker | Territory | Boot doc |
|---|---|---|
| SourceA Loop Specialist | SourceA repo, M1/M2/M5 workflows | role prompt + laws v3 |
| NOOS Loop Specialist | noetfeld-os, M2/M3 loops, dashboard | role prompt + laws v3 |
| Copilot coding agent | Kaizen machine_safe PRs only, CODEOWNERS-fenced | issue templates |
| BRAIN | cross-lane routing, digest | this spec §5 |
| Founder | decisions, budgets, verifier diffs, missions | daily brain digest |

Dispatch protocol (all workers): governed-autorun v3 template — laws header, one sandbox, fixed report fields, op_key on every task.

---

## 7. ROLLOUT (each phase = one dispatch, machine-verifiable done)

| Phase | What | Owner | Done when |
|---|---|---|---|
| P1 | trigger-registry + sweep diff (§1) | both specialists | first DRIFT-clean heartbeat |
| P2 | anatomy block into locked-definitions + definitions lint | SourceA spec. | lint green in CI |
| P3 | mission-registry + mission_id on receipts | both | receipts carry mission_id |
| P4 | CODEOWNERS + branch protection + concurrency groups | founder (5 min UI) + specialists | protected paths verified |
| P5 | brain-tick v1 READ+DIGEST only (no dispatch) | SourceA spec. | first daily digest lands |
| P6 | brain-tick EMIT via repository_dispatch (observe→control, after P5 runs 3 days clean) | founder gate | first directive→cycle→receipt chain |
| P7 | Copilot Kaizen pilot: 1 issue → PR → gates → merge | NOOS spec. | first third-party machine_safe merge |
| P8 | D-metrics in heartbeat + trend | both | metrics table 7d at 0 |

Sequencing law: P5 before P6 (Brain observes before it routes — same observe-first rule as the dashboard). P4 before P7 (fences before third-party agents).

---

## 8. WHAT THIS SPEC DOES NOT DO
- No second reconciler (L1). Brain routes; reconcilers execute.
- No new runtime platforms until a mission's DoD demands one (Fly/LangGraph stay parked).
- No verifier authority for any machine, Brain included (L5).
- No founder attention as a scheduled dependency: founder consumes one daily digest and a founder_gated queue; nothing waits on founder for observations (observation law).
