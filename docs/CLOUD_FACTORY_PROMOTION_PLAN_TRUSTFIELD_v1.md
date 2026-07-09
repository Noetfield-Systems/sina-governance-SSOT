# CLOUD FACTORY PROMOTION PLAN — TRUSTFIELD v1

**Status:** ARCHITECTURE PACKAGE (no code in this pass)
**Authority:** Founder architect order 2026-07-08 · P0-PGR era PHASE_2_CLOUD_ONLY_ROI_TRACK
**Companion artifacts:** `data/cloud_line_registry_v1.json` · `data/prompt_registry_schema_v1.json` · `docs/ACTIVATION_LADDER_v1.md`
**Principle:** The Mac and chat are the cockpit. Every recurring loop executes in cloud, writes a receipt, and only founder-authority transitions wait for a human.

---

## 0. Existing cloud substrate (what we promote onto — nothing invented)

| Substrate | Already live | Used for |
|---|---|---|
| Railway `trustfield-api` (FastAPI + Supabase Postgres, schema `trustfield`) | ✅ api.trustfield.ca, alembic, `/health`, `/api/readiness`, admin token gate | Event lines, data model, approval actions |
| Cloudflare Workers | ✅ `trustfield-www` + existing fleet pattern (deadman, fleet-tick, verify-recipes workers) | Cron probes, edge checks |
| GitHub Actions (repo `Noetfield-Systems/TrustField-Technologies`, main protected by review discipline) | ✅ CI patterns exist in org | Scheduled python loops (health, eval, drift), post-deploy verification |
| Supabase | ✅ auth (platform sign-in), Postgres | Approval queue storage, asset-view logging |
| Deployed today | ✅ Team Bench program (commit `4663bc6`), verifiers repaired (`96e6cb3..46d394a`), `PLATFORM_PACKAGE_PASS` | Ladder step A is already complete |
| Governance | ✅ P0-PGR runtime in sina-governance-ssot (packets, receipts, scorecards) | Receipt doctrine, founder receipts |

---

## 1. Cloud line map

Every line: name · owner role · trigger · schedule/event · input → output · receipt · failure behavior · founder points.
Machine-readable version: `data/cloud_line_registry_v1.json`.

### L1 — Platform Health Line
- **Owner role:** NOOS runtime (machine)
- **Trigger:** schedule, every 30 min + on-demand after any deploy
- **Execution target:** GitHub Actions cron running `scripts/monitor_partner_access_health_v1.py` against production
- **Input:** live www + api endpoints · **Output:** health JSON
- **Receipt:** row in `ops_receipts` (type `health_check`) via API ops endpoint; GH Actions artifact as backup
- **Failure behavior:** 1 fail = warn receipt; 2 consecutive = Telegram ops alert + GitHub issue; never auto-rollback; lane keeps probing (continuity law)
- **Founder points:** none (read-only)

### L2 — Candidate Intake Line
- **Owner role:** Platform (Railway)
- **Trigger:** event — `POST /api/partner-access/apply` (live today); nightly re-score sweep
- **Execution target:** Railway API (event) + GitHub Actions (nightly sweep)
- **Input:** application payloads · **Output:** scored candidate rows, high-score Telegram notify (exists)
- **Receipt:** candidate row itself + nightly `intake_summary` receipt (counts, score distribution, anomalies)
- **Failure behavior:** validation 422s are normal; scoring exceptions file repair candidates, never block intake
- **Founder points:** none at intake; humans enter at FOUNDER_REVIEW status (L8)

### L3 — Team Bench Sourcing Line
- **Owner role:** Sourcing agent (cloud LLM w/ web search)
- **Trigger:** schedule weekly + founder-dispatched runs
- **Execution target:** scheduled cloud agent (Claude Code cloud routine) posting to `/api/partner-access/team-bench/admin` with `ADMIN_TOKEN` secret
- **Input:** role-lane sourcing prompts from prompt registry (`tb.sourcing.r1/r3/r4` …) · **Output:** SOURCED rows only — structurally cannot set CONTACTED (API CASL gate)
- **Receipt:** `TEAM_BENCH_SOURCED_ROWS` run receipt: rows created, dedup vs existing, evidence URLs, cost
- **Failure behavior:** unverifiable candidates dropped (fewer > padded); zero-row run files a finding, not a stop
- **Founder points:** every transition beyond SOURCED (`approve_to_contact` is founder-only, enforced in API today)

### L4 — Agentic Evaluation Line
- **Owner role:** Evaluation agent
- **Trigger:** nightly + on status change to FOUNDER_REVIEW
- **Execution target:** Railway (deterministic scoring — exists as `build_agentic_evaluation`/bench scores) + GitHub Actions invoking registry prompt for qualitative review packs
- **Input:** candidate + prospect rows · **Output:** risk flags, fit deltas, founder-review question packs, rank ordering
- **Receipt:** `evaluation_run` receipt per sweep (rows evaluated, flags raised, prompt version + cost)
- **Failure behavior:** LLM failure degrades to deterministic-scores-only output, tagged PARTIAL
- **Founder points:** none — advisory output only; decisions stay in L8

### L5 — Prompt Registry Line
- **Owner role:** Architect (change control) / machine (execution)
- **Trigger:** event — PR touching registry; every prompt run
- **Execution target:** GitHub (versioned registry file + CI contract tests) + Railway serving active versions; every run logged to `prompt_runs`
- **Input:** prompt definitions per `PROMPT_REGISTRY_SCHEMA_v1` · **Output:** versioned, testable prompts with input/output contracts
- **Receipt:** `prompt_run` rows (prompt_id, version, cost class, tokens, outcome); registry change = PR diff + CI receipt
- **Failure behavior:** contract-test failure blocks version activation only (old version keeps running — rollback rule)
- **Founder points:** activating a new version of any prompt whose lane can spend money or touch candidates

### L6 — Deploy Truth Line
- **Owner role:** Verifier (machine)
- **Trigger:** event — every push to main / every deploy; + daily cron
- **Execution target:** GitHub Actions running `verify_partner_access_platform_package_v1.sh` (repaired today) + build-marker drift check (repo `SITE_BUILD_ID` vs live)
- **Input:** git main, live www/api · **Output:** PLATFORM_PACKAGE_PASS/PARTIAL verdict
- **Receipt:** `deploy_truth` receipt per run (HEAD, live marker, verdict, missing[])
- **Failure behavior:** drift detected → alert + `deploy_truth` HOLD flag row (blocks L3/L4 autoruns until resolved) — the working-tree-publish incident (Noetfield `/structure/`) is the founding case for this line
- **Founder points:** drift resolution; any rollback/redeploy decision

### L7 — Asset Gate Line
- **Owner role:** Verifier (machine)
- **Trigger:** schedule — inside every L1 run; + weekly deep audit
- **Execution target:** GH Actions (probe invalid/expired token access on every gated asset; assert 401/404) + Railway logging `asset_views` on legit deliveries
- **Input:** `ASSET_GATES` map (8 assets) + NDA-gated Team Bench materials · **Output:** gate audit verdicts, anomalous access flags
- **Receipt:** `asset_gate_audit` receipt (assets × probes matrix)
- **Failure behavior:** any gate leak = SEV-1 alert + immediate founder notification; probing continues
- **Founder points:** none unless leak found

### L8 — Founder Approval Queue
- **Owner role:** Founder (decisions) / machine (aggregation)
- **Trigger:** event — anything entering an approval state; daily digest at 15:00 UTC
- **Execution target:** Railway API (`approval_queue` table + admin dashboard section) + GH Actions daily digest → Telegram
- **Input:** bench `approve_to_contact` requests · candidates at FOUNDER_REVIEW · deploy-drift holds · prompt version activations · spend unlocks · offer/trial-MOU stages
- **Output:** single ordered queue with decision buttons (approve / reject / defer), each mapped to an existing gated API action
- **Receipt:** every decision = `approval_decision` receipt (who, what, verbatim scope, timestamp) — the M03 lesson, systematized
- **Failure behavior:** queue never auto-approves; stale items age visibly in digest
- **Founder points:** this IS the founder surface — one place, minutes per day

---

## 2. Execution targets (summary)

| Line | Primary target | Secondary |
|---|---|---|
| L1 Health | GitHub Actions cron (30 min) | CF deadman worker (is-Actions-alive) |
| L2 Intake | Railway API (event) | GH Actions nightly sweep |
| L3 Sourcing | Claude Code cloud scheduled agent | GH Actions fallback runner |
| L4 Evaluation | Railway (deterministic) | GH Actions + Claude API (narrative) |
| L5 Prompt Registry | GitHub (registry + CI) | Railway (serving + `prompt_runs`) |
| L6 Deploy Truth | GH Actions (push + daily) | CF verify-recipes worker (edge marker check) |
| L7 Asset Gate | GH Actions (within L1) | Railway `asset_views` logging |
| L8 Approval Queue | Railway API + admin dashboard | GH Actions daily Telegram digest |

Rule: **Mac executes nothing on schedule.** The existing Mac launchd brain-loop is out of scope for TrustField lines; TrustField crons live in GH Actions/CF/Railway only.

---

## 3. Data model

| Store | Status | Notes |
|---|---|---|
| `partner_acquisition_candidates` (candidates) | ✅ EXISTS | v1.4 funnel + scores; system of record for intake |
| `team_bench_prospects` (team_bench_tracker) | ✅ EXISTS (deployed today, migration `20260708_0005`) | CASL gate fields + bench scores |
| candidate_scores | ✅ EXISTS as columns on both tables | keep embedded; expose as API view — no duplicate table |
| `prompt_registry` | 🆕 table + versioned JSON mirror in git | schema: `data/prompt_registry_schema_v1.json` |
| `prompt_runs` | 🆕 table | prompt_id, version, trigger, tokens, cost_class, outcome, receipt ref |
| `asset_views` | 🆕 table | asset_id, candidate_ref, timestamp, gate state at delivery |
| `approval_queue` | 🆕 table | item_type, subject_ref, requested_action, evidence_ref, status, decided_at, decision_receipt |
| `ops_receipts` (receipts) | 🆕 table | unifies health_check / deploy_truth / evaluation_run / sourcing_run / asset_gate_audit / approval_decision — one table, `receipt_type` discriminator; mirrors to SSOT for governance-grade items |
| health_checks | 🆕 = `ops_receipts` type `health_check` | no separate table |
| deploy_truth | 🆕 = `ops_receipts` type `deploy_truth` + HOLD flag row | consumed by L3/L4 gate |

One alembic migration (`20260709_0006_cloud_factory_tables`) covers the four new tables. SSOT keeps governance mirrors (founder receipts, scorecards); Postgres holds operational truth.

---

## 4. Prompt registry design

Full JSON Schema: `data/prompt_registry_schema_v1.json`. Every prompt record carries:

| Field | Rule |
|---|---|
| `prompt_id` | stable kebab id, lane-prefixed (`tb.sourcing.r3`, `pa.eval.review-pack`, `ops.health.narrative`) |
| `version` | semver; immutable once activated |
| `lane` | L1–L8 line id |
| `owner` | architect / founder / machine |
| `input_contract` | JSON Schema of required inputs |
| `output_schema` | JSON Schema the run MUST validate against (retry on mismatch) |
| `model_tier` | `determine` (no LLM) / `fast` / `standard` / `judgment` — judgment tier reserved for evaluation & architecture |
| `cost_class` | `zero` / `cents` / `dollars` — dollars requires founder-activated budget line |
| `run_trigger` | cron expr / event name / manual |
| `receipt_path` | `ops_receipts.prompt_run` + optional SSOT mirror |
| `rollback_rule` | previous active version auto-restores on contract-test failure or founder rollback; two versions never active at once |

Change control: registry lives in git; a version activates only after CI contract tests pass; activation of candidate-touching or paying prompts is an L8 queue item.

---

## 5. Autorun design

**Runs automatically (no human in loop):**
- health checks (L1, 30 min)
- intake scoring on apply (L2, live)
- candidate classification / re-score sweeps (L2/L4, nightly)
- source candidate research → SOURCED rows only (L3, weekly)
- drift detection (L6, per-push + daily)
- asset gate checks (L7, per L1 run + weekly deep)
- prompt contract test runs (L5, on registry change)
- daily receipt summary + approval digest (L8, daily)

**Waits for founder approval (structurally, in API — not by convention):**
- contacting candidates (CASL gate: `approve_to_contact` → `mark_contacted`)
- sending any email (email defer stays ON until founder flips it)
- publishing public pages / changing public copy
- changing legal/equity/positioning copy (RPAA rules)
- activating paid tools or any `cost_class: dollars` prompt
- offers / trial MOU / any status beyond FOUNDER_REVIEW

---

## 6. Tomorrow activation ladder (summary — full detail in `docs/ACTIVATION_LADDER_v1.md`)

- **A. Commit/deploy current Team Bench Platform Program — ✅ DONE today** (`4663bc6` deployed, `PLATFORM_PACKAGE_PASS`, receipt `TEAM_BENCH_PLATFORM_PROD_DEPLOY_v1-20260708T233943Z`)
- **B. Cloud prompt registry** — migration + seed registry (sourcing/eval/health prompts) + CI contract tests
- **C. Cloud scheduled loops** — GH Actions: health (30m), deploy truth (push+daily), nightly eval sweep
- **D. Founder approval queue** — `approval_queue` table + admin section + daily Telegram digest
- **E. First cloud sourcing run** — scheduled agent, SOURCED rows only, run receipt (seeded by today's 3-agent sourcing output once verified)
- **F. Receipt dashboard** — admin page over `ops_receipts` + daily summary receipt

---

## 7. Success definition (measurable)

| Criterion | Check |
|---|---|
| No local chat needed for routine loops | GH Actions/Railway cron logs show L1/L4/L6/L7 runs with zero session involvement for 48h |
| Cloud writes receipts | `ops_receipts` rows machine-timestamped by runners, not sessions |
| Candidates route through platform | 100% of new tracker rows created via API; SSOT tracker file is mirror-only |
| Agents produce SOURCED rows automatically | ≥1 scheduled L3 run creating verified SOURCED rows with evidence URLs |
| Founder only approves transitions | zero CONTACTED/sends/deploys without an `approval_decision` receipt |
| Deploy drift auto-detected | L6 catches a seeded drift test within one cycle |
| Prompt changes versioned | no prompt runs outside registry versions; `prompt_runs` FK to registry |
| Site health continuous | L1 cadence unbroken 48h; deadman worker alarms if Actions goes silent |
