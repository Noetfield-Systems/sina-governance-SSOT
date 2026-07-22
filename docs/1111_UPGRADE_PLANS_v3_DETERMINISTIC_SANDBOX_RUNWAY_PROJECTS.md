# 1111 Upgrade Plans v3 — Deterministic Sandbox + Runway-as-Project (Days)

**Status:** DRAFT → LOCK candidate · execute top-down per plan; cross-plan deps noted.  
**Saved:** 2026-07-22  
**Parent:** [1111_UPGRADE_PLANS_v2.md](1111_UPGRADE_PLANS_v2.md) · extends (does not replace) TF/SF tracks  
**Repo SSOT (machine):** `NOETFIELD-RUNWAY/data/nf_1111_deterministic_runway_projects_v3.json`  
**Specs pack:** `NOETFIELD-RUNWAY/governance/1111-deterministic-runway-projects.v3/`  
**Control plane:** Project Runtime + Goal Pursuit (`goal.v1`) · Motor `noetfield.runway-core.v0.1` pin `e24a27c`

---

## Thesis

v1/v2 1111 plans proved **four parallel tracks** for TrustField / Signal Factory.  
v3 reuses that **1-1-1-1** shape for the next product law:

> Every runway outcome is a **multi-day Project** with a **full Requirements + Spec pack**, executed only inside a **deterministic sandbox**, verified by **independent gates**, and closed with a **receipt** — never by model self-acceptance.

Customers buy the **finished, verified result**. Models propose; Kernel + sandbox + verifier decide.

---

## Four parallel tracks (1-1-1-1)

| # | Plan | Owner | Primary surface |
|---|------|-------|-----------------|
| **1** | Deterministic Sandbox Kernel | Motor / Runtime Worker | `services/runway-cloud-runtime` · sandbox_id isolation |
| **2** | Goal Pursuit over Days | Project Runtime Control Plane | `goal-pursuit-workflow` · project-lifecycle |
| **3** | Runway Portfolio as Day-Projects | Runway lanes | software-repair · research · commissioning · (video HOLD for cash) |
| **4** | Proof, Commercial Gate, Deterministic API | Founder + Motor + Det API | E2E wake path · nf-deterministic-api · receipts |

```
Plan 1 (Sandbox) ──► Plan 2 (Goal Pursuit days) ──► Plan 3 (Runway projects)
Plan 4 (Proof/Commercial) ◄── consumes Plans 1–3 QUALIFIED receipts
```

---

## Value classes (unchanged from v2)

| Class | Meaning | Throttle |
|-------|---------|----------|
| `revenue_path` | Direct line to paid pilot / SKU | Never |
| `proof_asset` | Sellable receipt / QUALIFIED evidence | Never |
| `risk_reduction` | Prevents fake deploy, leak, downgrade | Never |
| `hygiene` | Docs, mirrors | Throttle if >30% 7d spend |
| `none` | No measurable ROI | Auto-deprioritize |

---

## Wave model

```
WAVE 0  Spec pack + machine JSON on disk (this deliverable)
WAVE 1  Sandbox isolation + Goal Pursuit day loop (staging)
WAVE 2  First paid-shaped runway project (Software Repair pilot project)
WAVE 3  Research day-projects + Det API commercial proof
WAVE 4  Multi-project parallel (≤3) with write leases + founder promote gate
```

| Milestone | Target | Proof |
|-----------|--------|-------|
| Spec pack + machine SSOT filed | Wave 0, day 0 | files + schema validate |
| Sandbox isolation for 3 concurrent jobs | Wave 1, ≤3 days | distinct `sandbox_id` · no collision |
| Goal sleeps/checkpoints across ≥24h wall | Wave 1, ≤5 days | Goal status trail + receipt |
| Software Repair day-project PASSED | Wave 2, ≤7 days | green draft PR + CI exact-head |
| Research vendor-brief day-project PASSED | Wave 3, ≤14 days | citation gates + artifact |
| Public demo E2E SUCCEEDED (staging) | Wave 3, ≤14 days | enqueue→wake→result receipt |
| First paid pilot offer closed | Wave 4, ≤30 days | CRM/receipt · revenue_path |

---

## Locked invariants (do not redesign)

1. Motor mints `job_id` (`rj_[0-9a-f]{32}`); callers never invent it.
2. Enqueue ≠ execute — wake via authenticated `POST /v1/jobs/{id}/run`.
3. Sandbox is for **command execution + deterministic gates**, not for summarization theatre.
4. Model cannot qualify its own output; verifier is independent.
5. External apply / production promote = founder-gated unless a phase explicitly authorizes staging-only.
6. Secrets = references only; never in specs, prompts, fixtures, or receipts.
7. Video runway remains **cash HOLD** (loss-trap thesis); may run as proof_asset only after Repair + Research day-projects PASS.
8. Unrelated `_wt-*` dirt is protected — never reset/clean/overwrite.

---

# PLAN 1 — Deterministic Sandbox Kernel

**Owner:** Motor / `runway-cloud-runtime`  
**Budget:** staging only until Plan 4 promote gate  
**value_class spine:** `risk_reduction` → `proof_asset`

## Requirements (REQ-SBX)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-SBX-01 | Every job binds a stable `sandbox_id` derived from job scope (no reuse across concurrent tenants) | P0 |
| REQ-SBX-02 | Concurrent isolation: 3 parallel jobs → 3 distinct sandboxes (CI already asserts) | P0 |
| REQ-SBX-03 | Failed deterministic gate **requeues repair**, never marks SUCCEEDED | P0 |
| REQ-SBX-04 | Sandbox checkpoints persist for multi-day resume (`sandbox_checkpoints` D1) | P0 |
| REQ-SBX-05 | No network egress except allowlisted provider + verifier endpoints | P0 |
| REQ-SBX-06 | Cost ledger debit per step; 402 / BUDGET_EXHAUSTED fail-closed | P0 |
| REQ-SBX-07 | Receipts under `receipts/` are append-only evidence (machine_safe merge allowlist) | P1 |

## Day projects (Plan 1)

### Day P1-D1 — Sandbox identity + collision proof
- **Spec:** `specs/p1-d1-sandbox-isolation.specification.json`
- **Done when:** CI concurrent isolation PASS · 3 sandbox_ids unique
- **Stop:** collision or missing sandbox_id → BLOCKED

### Day P1-D2 — Checkpoint / resume across wall-clock
- **Spec:** `specs/p1-d2-sandbox-checkpoint-resume.specification.json`
- **Done when:** kill mid-job → resume from checkpoint → same job_id reaches terminal with continuous receipt chain
- **Stop:** silent restart without checkpoint → FAIL

### Day P1-D3 — Gate fail → repair → verify loop
- **Spec:** `specs/p1-d3-deterministic-gate-repair.specification.json`
- **Done when:** seeded RED verifier never yields Motor success without green repair
- **Stop:** model self-accept without gate → FAIL

**Plan 1 exit:** P1-D1..D3 QUALIFIED receipts filed under `receipts/1111-v3/plan1/`.

---

# PLAN 2 — Goal Pursuit over Days (Runway as Project)

**Owner:** Project Runtime Control Plane · Goal Pursuit `goal.v1`  
**Budget:** ≤ USD 25 / goal default · ≤ 480 wall minutes default · override per project  
**value_class spine:** `proof_asset` → `revenue_path`

## Requirements (REQ-GOAL)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-GOAL-01 | Goal sits **above** immutable Runway Runs; child runs are append-only | P0 |
| REQ-GOAL-02 | Status machine includes SLEEPING / CHECKPOINTING / WAITING_FOR_APPROVAL for multi-day | P0 |
| REQ-GOAL-03 | Acceptance criteria are typed (`content_check`, `http_check`, `artifact_check`, `validation`, `receipt_verification`, `deployment_check`) | P0 |
| REQ-GOAL-04 | Weighted progress is deterministic from criterion weights + PASS results | P0 |
| REQ-GOAL-05 | Autonomy defaults: commit+push feature OK; merge/production = `approval_required` | P0 |
| REQ-GOAL-06 | Write leases prevent two goals writing same path_prefix | P0 |
| REQ-GOAL-07 | TIME_EXHAUSTED / BUDGET_EXHAUSTED are terminal with evidence — no infinite loop | P0 |
| REQ-GOAL-08 | Every day-project intakes a **Requirements MD + specification.json** before RUNNING | P0 |

## Day projects (Plan 2)

### Day P2-D1 — Goal create from Spec pack
- Bind `specificationHash` + `requirementsRef`
- Status DRAFT → READY only after schema validate
- **Done when:** GoalSnapshot shows criteria + budget + autonomy

### Day P2-D2 — Multi-day sleep/checkpoint drill (≥24h simulated or real)
- Force SLEEPING mid-pursuit; wake; continue iteration
- **Done when:** child_runs length ≥2 · receipt chain continuous · wall clock ≥ projected day boundary

### Day P2-D3 — Approval gate day
- Hit WAITING_FOR_APPROVAL for staging deploy
- Founder approve → staging_verify_finalize
- **Done when:** `staging_deployed` criterion PASS with approval evidence

**Plan 2 exit:** Goal PASSED or PARTIAL_PASS with receipt_hash; never “looks done” without acceptance PASS.

---

# PLAN 3 — Runway Portfolio as Day-Projects (full Requirements + Spec)

**Owner:** Runway lanes (software-repair, research, commissioning)  
**Cash priority:** Software Repair first (vertical agentic SaaS — proven Motor)  
**HOLD:** Video cash path  
**value_class spine:** `revenue_path`

## 3A — Software Repair Pilot Project (primary cash runway)

### Requirements (REQ-SR)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-SR-01 | Intake: repo + failing suite id + pilot fee terms | P0 |
| REQ-SR-02 | Motor loop: plan → route cheap model → sandbox execute → verify → repair → draft PR | P0 |
| REQ-SR-03 | Delivery = machine draft PR + exact-head CI green | P0 |
| REQ-SR-04 | Authority: live `approval_required` for merge/promote (autonomous repair OK for draft) | P0 |
| REQ-SR-05 | Customer-facing offer: fixed-fee pilot USD 5–10K / ≤14 days | P0 |
| REQ-SR-06 | ROI receipt: hours saved estimate + CI green proof | P1 |
| REQ-SR-07 | Convert path: annual USD 25–50K for N repairs/mo | P1 |

### Day projects

| Day | Project ID | Spec | Done when |
|-----|------------|------|-----------|
| P3-SR-D1 | Offer + one-pager + proof links | `specs/p3-sr-d1-offer-pack.specification.json` | Offer MD + 3 proof URLs |
| P3-SR-D2 | Live canary repair on fixture | `specs/p3-sr-d2-canary-repair.specification.json` | Draft PR + CI green |
| P3-SR-D3 | Pilot intake workflow | `specs/p3-sr-d3-pilot-intake.specification.json` | Goal RUNNING from customer brief |
| P3-SR-D4 | Pilot execute → ROI receipt | `specs/p3-sr-d4-pilot-roi.specification.json` | QUALIFIED ROI receipt |
| P3-SR-D5 | Annual convert pack | `specs/p3-sr-d5-annual-convert.specification.json` | Contract template + ARR math |

## 3B — Research Day-Projects

### Requirements (REQ-RS)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-RS-01 | Recipes: vendor-decision-brief · spreadsheet-kpi-pack · rfp-response-pack | P0 |
| REQ-RS-02 | Citation / unsupported-claim gates mandatory | P0 |
| REQ-RS-03 | Heavy recipes may use Railway executor; healthz must be 200 before dispatch | P0 |
| REQ-RS-04 | Public demo path: enqueue + wake + result (no hang) | P0 |

### Day projects

| Day | Project ID | Spec | Done when |
|-----|------------|------|-----------|
| P3-RS-D1 | vendor-decision-brief E2E | `specs/p3-rs-d1-vendor-brief.specification.json` | SUCCEEDED + recipe-shaped JSON |
| P3-RS-D2 | citation gate adversarial | `specs/p3-rs-d2-citation-gates.specification.json` | Unsupported claims FAIL closed |
| P3-RS-D3 | spreadsheet-kpi-pack heavy | `specs/p3-rs-d3-kpi-pack.specification.json` | Workbook artifact + gates |

## 3C — Commissioning Day-Projects

| Day | Project ID | Spec | Done when |
|-----|------------|------|-----------|
| P3-CM-D1 | Proof-A QUALIFIED | `specs/p3-cm-d1-proof-a.specification.json` | Terminal QUALIFIED evidence |
| P3-CM-D2 | Proof-B QUALIFIED | `specs/p3-cm-d2-proof-b.specification.json` | Terminal QUALIFIED evidence |

**Plan 3 exit:** ≥1 Software Repair day-project PASSED + ≥1 Research day-project PASSED.

---

# PLAN 4 — Proof, Commercial Gate, Deterministic API

**Owner:** Founder (promote) · Motor staging · `nf-deterministic-api-v1`  
**value_class spine:** `revenue_path` · `proof_asset`

## Requirements (REQ-COM)

| ID | Requirement | Priority |
|----|-------------|----------|
| REQ-COM-01 | Staging E2E: demo → HMAC job → wake → SUCCEEDED (fixes T1–T8 from motor-runways-e2e plan) | P0 |
| REQ-COM-02 | Entitlement budget allows allowlisted public demo recipe | P0 |
| REQ-COM-03 | Proxies on www + standalone both wake `/run` | P0 |
| REQ-COM-04 | Deterministic API staging: OpenAI base_url swap + credits ledger | P1 |
| REQ-COM-05 | No production claim without QUALIFIED promote receipt | P0 |
| REQ-COM-06 | Sell surface honesty: paid delivery not claimed on free demo | P0 |

## Day projects

| Day | Project ID | Spec | Done when |
|-----|------------|------|-----------|
| P4-D1 | Entitlement + wake unblock | `specs/p4-d1-e2e-unblock.specification.json` | Not 402; job wakes |
| P4-D2 | Dual-surface E2E receipt | `specs/p4-d2-dual-surface-e2e.specification.json` | Both sites SUCCEEDED |
| P4-D3 | Det API staging smoke | `specs/p4-d3-det-api-smoke.specification.json` | chat.completions schema-valid |
| P4-D4 | Founder promote gate dry-run | `specs/p4-d4-promote-dry-run.specification.json` | Dry-run receipt only (no prod) |

**Plan 4 exit:** Staging E2E PASS receipt + Det API smoke PASS; production still founder-gated.

---

## Parallel execution board (founder view)

| Lane | Now | Owner | Repo |
|------|-----|-------|------|
| A | Validate machine JSON + specs | SG / Motor | SSOT + RUNWAY |
| B | P1-D1 sandbox isolation CI | Motor Worker | NOETFIELD-RUNWAY |
| C | P2-D1 Goal from Spec pack | Project Runtime | `_wt-goal-pursuit-v1` → main lane |
| D | P3-SR-D1 offer pack | Commercial / Founder | RUNWAY + sell site |
| E | P4-D1 entitlement/wake | Motor + Noetfield Pages | RUNWAY + Noetfield |
| F | TF/SF 1111 v2 tracks | unchanged | continue parallel |

Lanes A–E run **in parallel**. Plan 3 cash days after Plan 1 D1 + Plan 2 D1 green.

---

## Kill / freeze criteria

| Trigger | Action |
|---------|--------|
| Sandbox collision | Freeze concurrent dispatch |
| Gate bypass / self-accept | Freeze runway; file risk_reduction receipt |
| Budget > ceiling without revenue | Pause hygiene days; never pause intake of paid pilot |
| Production apply without approval | Auto-revert intent; BLOCKED_DESTRUCTIVE_AUTHORITY |
| Video cash push before Repair+Research PASS | Reject; cite HOLD |

---

## Proof bundle v3

```bash
# Machine SSOT present
test -f ~/Desktop/Noetfield-Systems/NOETFIELD-RUNWAY/data/nf_1111_deterministic_runway_projects_v3.json && echo V3_JSON_OK

# Spec pack count
find ~/Desktop/Noetfield-Systems/NOETFIELD-RUNWAY/governance/1111-deterministic-runway-projects.v3/specs -name '*.json' | wc -l

# Schema lint (when script shipped)
node --experimental-strip-types ~/Desktop/Noetfield-Systems/NOETFIELD-RUNWAY/scripts/validate-1111-v3.mts

# Motor doctor
cd ~/Desktop/Noetfield-Systems/NOETFIELD-RUNWAY && node --experimental-strip-types scripts/runway-doctor/src/cli.ts

# Goal pursuit types present
test -f ~/Desktop/Noetfield-Systems/NOETFIELD-RUNWAY/_wt-goal-pursuit-v1/apps/project-runtime-control-plane/src/goal-types.ts && echo GOAL_TYPES_OK
```

---

## Mapping to prior research (cash)

| Research runway | v3 home | Note |
|-----------------|---------|------|
| Vertical agentic SaaS (Fathom-shaped) | Plan 3A Software Repair | You already have Motor proof |
| Brand content factory | Deferred | Capital/team shape ≠ current stack |
| Eval “sell shovels” | Deferred | Needs community moat |
| Agentic support | Later vertical after Repair cash | Same Motor pattern |
| Automation agency | Plan 3A pilots | Outcome retainers |

---

## Artifact index

| Artifact | Path |
|----------|------|
| This human plan | `sina-governance-SSOT/docs/1111_UPGRADE_PLANS_v3_DETERMINISTIC_SANDBOX_RUNWAY_PROJECTS.md` |
| Machine SSOT | `NOETFIELD-RUNWAY/data/nf_1111_deterministic_runway_projects_v3.json` |
| Specs | `NOETFIELD-RUNWAY/governance/1111-deterministic-runway-projects.v3/specs/*.specification.json` |
| Requirements | `NOETFIELD-RUNWAY/governance/1111-deterministic-runway-projects.v3/requirements/*.md` |
| Parent 1111 v2 | `docs/1111_UPGRADE_PLANS_v2.md` |
| E2E defect plan | `NOETFIELD-RUNWAY/.agent/execplans/motor-runways-e2e-readiness-v1.md` |

---

*v3.0 — 2026-07-22 — Deterministic sandbox + multi-day runway projects; extends v2 TF/SF tracks.*
