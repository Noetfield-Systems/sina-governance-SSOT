# PLAN FACTORY ARCHITECTURE v1 — PACKAGE AUTHORITY (1000-PLAN CLOUD FACTORY)

**Version:** 1.0.0 · **Status:** PROPOSED (design-only, nothing in this package is built or active)
**Era:** `PHASE_2_CLOUD_ONLY_ROI_TRACK`
**Authority chain:** FOUNDER_CANON v1 → P0-PGR runtime v1.1 (command brain) → Cloud Factory Substrate v0 (`cloud-factory/`, execution substrate) → this package (plan library + plan pipeline)
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
**canon_version:** `founder_canon_v1.0.0`
**Founder authorization:** receipt `founder-order-1000-plan-cloud-factory-20260709T014708Z` (`receipts/p0pgr/founder/`), resumed by `founder-order-resume-1000-plan-l0-20260709T020915Z`, deliverable set revised to FIVE files by `founder-order-1000-plan-l0-first-5file-20260709T021931Z` — design-only unlock. Building, activating, scheduling, and deploying are NOT unlocked by these receipts.
**L0 provenance (no-blind-pass law):** designed L0-graph-first — verifier PASS `receipts/l0-repo-graph-verify-20260709T021931Z.json`; ordered queries (cloud-factory, FACTORY_LINE_REGISTRY, p0-pgr, sandbox, client order, plan factory + fragment retries); compact map `receipts/l0-map-1000-plan-5file-20260709T022035Z.json`; earlier query receipt `receipts/l0-graph-query-1000-plan-20260709T020940Z.json` (graph `data/l0_repo_graph_memory_v1.json`). Drafting read only graph-named files; no broad reader agents were spawned.
**Builds on:** the receipted Cloud Factory Substrate v0 package (five files, PROPOSED, receipt `CLOUD_FACTORY_SUBSTRATE_v0-20260709T015408Z`). Version law: newer versions AMEND and win only on direct conflict; v0 files stay live and are NOT superseded. Nothing in this package mutates P0-PGR schemas or the v0 package files.
**Ratification path:** RF1/RF2/RF3 fence rules forbid self-promotion to ACTIVE. This package moves to ACTIVE only via founder work_order + receipt.

## Package file map

The ordered package is exactly FIVE files (founder order 2026-07-08, 5-file layout):

| File (all in `plan-factory/`) | Role |
|---|---|
| `PLAN_FACTORY_ARCHITECTURE_v1.md` | This document — package authority, plan model, pipeline, execution lines, cell model, client product model, safety doctrine |
| `PLAN_SCHEMA_v1.json` | JSON Schema draft-07 for one plan record (`$id`: `plan_schema_v1`) |
| `PLAN_LIBRARY_SEED_1000_v1.json` | The plan library, capacity 1000, band maps + 30 seed records (schema `plan_library_v1`) |
| `PLAN_RANKING_ROI_MODEL_v1.json` | Deterministic plan ranking over the p0pgr base model (schema `plan_ranking_roi_model_v1`) |
| `PLAN_FACTORY_ACTIVATION_PLAN_v1.md` | PF-A → PF-E activation ladder, exit criteria, known blockers |

**Unratified addenda (NOT package members):** three supplementary drafts from the earlier 7-file layout remain on disk (never deleted; rejection ≠ deletion): `FACTORY_LINE_REGISTRY_v1.json`, `SANDBOX_WORKTREE_MANAGER_v1.md`, `CLIENT_ORDER_TO_PLAN_PIPELINE_v1.md`. Their load-bearing content is summarized in §4, §6, and §7 of THIS document, which is authoritative where they differ. Line-plan resolution runs against the v0 registry (`cloud-factory/FACTORY_LINE_REGISTRY_v0.json`) plus the band maps in `PLAN_LIBRARY_SEED_1000_v1.json`.

---

## §1 Core principle — the five-role model

One sentence: **the brain decides, the engine builds, the surfaces display, the cells isolate, the workspace sells.**

1. **P0-PGR is the brain.** Classify, gate, compile, rank, route — nine gates, R1–R9 lint, five-axis ROI ranker (`p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`). This package adds a plan library IN FRONT of the brain's compiler path; it never re-implements the queue (integration law, census F3) and never ranks privately.
2. **Forge Factory is the engine.** The v0 substrate: factory lines FL1–FL10 plus the sandbox manager. "Forge Factory" is the venture-facing NAME for the execution substrate — Forge is the SourceA Cloud Forge lineage (lane `sourcea_cloud_forge` exists in `data/github_automation_registry_v1.json`). The name adds no new machinery.
3. **Studio IDE / Forge Terminal are control surfaces** — order entry + run monitoring. Studio IDE = repo `noetfield-studio-ide` (exists, no wiring — CF-P2+). Forge Terminal = the founder/operator terminal surface (today: session + manual `workflow_dispatch`; as a NAMED control surface it is TO BE BUILT, CF-P2+). Control surfaces DISPLAY and SUBMIT; they never compute verdicts (Control Desk precedent: frontend displays, backend computes).
4. **Sandboxes/worktrees are execution cells.** One cell = one allocated sandbox ledger row (v0 sandbox manager law). Cell kinds and multi-repo targeting: `SANDBOX_WORKTREE_MANAGER_v1.md`.
5. **Client workspace is the product.** The CF-P2+ authenticated workspace where a client browses the plan catalog, places orders, and sees ONLY their own runs.

What v1 adds on top of v0: a governed library of up to 1000 reusable PLAN templates, so that most orders instantiate a proven plan instead of being hand-compiled from scratch. What v1 does NOT add: any new brain, any new schema mutation of P0-PGR, any production deploy machinery, any cron.

---

## §2 Relationship to v0

**Amended by this package** (designed so there are NO direct conflicts; everything below is a PROPOSED amendment requiring founder ratification):

| v0 artifact | v1 amendment | Vehicle |
|---|---|---|
| `cloud-factory/FACTORY_LINE_REGISTRY_v0.json` | v0 registry stays the resolution registry, UNCHANGED. Plan-aware additions (band maps `plan_type_default_line_plans` / `plan_type_risk_defaults`) live in `PLAN_LIBRARY_SEED_1000_v1.json` §bands. A fuller amendment registry exists as unratified addendum draft `FACTORY_LINE_REGISTRY_v1.json` | Band maps in the library seed (this package); addendum draft retained |
| `cloud-factory/SANDBOX_MANAGER_SPEC_v0.md` | v0 spec remains the base law unchanged (identity, allocation, walls W1–W9, env profiles, timeouts, cost caps, cleanup, artifact storage, receipt paths); the execution-cell delta is summarized in §7 of this document; a fuller delta exists as unratified addendum draft `SANDBOX_WORKTREE_MANAGER_v1.md` | §7 of this document; addendum draft retained |
| `client_order_to_factory_run_v0` envelope | Classification gains OPTIONAL `plan_ref {plan_id, plan_version}` — a PLANNED v0→v1 envelope amendment, flagged PROPOSED, never silently assumed. The lifecycle enum is unchanged; plan matching happens inside the existing `CLASSIFIED` state | PLANNED amendment (§11 blocker B12) |
| `sandbox_ledger_v0` | OPTIONAL columns `plan_id`, `cell_kind` — PLANNED v0→v1 ledger amendment, PROPOSED | PLANNED amendment (§11 blocker B13) |

**Untouched by this package:**
- P0-PGR schemas, gates, routes, lint rules, and ranker — the v0 wrap-by-reference decision stands verbatim (`no_authority_change` gate; FT-L5-IRREVERSIBLE).
- TrustField cloud lines L1–L8 (`data/cloud_line_registry_v1.json`) — sha256-pinned in a founder receipt; not edited.
- v0 receipt schemas `factory_line_receipt_v0` / `factory_run_receipt_v0` — plans REUSE them; a plan may ADD a `plan_receipt_note` but never removes fields.
- v0 walls W1–W9, run lifecycle enum, exception states, line verdicts, the nine gates, and the four founder triggers.

---

## §3 The PLAN object, the library, and the bands

### 3.1 The PLAN object (`PLAN_SCHEMA_v1.json`, required properties)

A plan is a reusable, founder-governable template that compiles into a standard factory run. Required fields:

- `plan_id` — pattern `^PLAN-[0-9]{4}$` (PLAN-0001..PLAN-1000).
- `plan_version` — semver, immutable once active (prompt-registry precedent: version immutable once activated; two versions never active at once).
- `plan_type` — enum of exactly 10 (§3.3).
- `title`, `venture` — venture enum `noetfield|sourcea|forge|trustfield|sg|client`.
- `mission_template` — string with `{{placeholders}}`, minLength 16; filled at instantiation (§4).
- `line_plan` — ordered array of FL1–FL10 ids, minItems 1; must be composable per the v0 registry consumes/produces chain; a plan naming a line not in `cloud-factory/FACTORY_LINE_REGISTRY_v0.json` is a lint reject.
- `sandbox_target` — `{repo, sandbox_required (bool), env_profile}` with env_profile enum `none|read_public_web|gh_actions_scoped|preview_deploy_scoped` (v0 enum, unchanged).
- `cost_cap_usd` — number, default 5.00 per run; per-line 2.00 inherited from v0. An order budget may LOWER a cap, never raise it above the plan cap without founder approval.
- `model_policy` — `{default_tier, premium_rule}`; default_tier enum `determine|fast|standard|judgment`; premium_rule: judgment tier allowed ONLY if roi_priors weighted score ≥ 60 OR an explicit founder order names it ("no premium models unless ROI justifies").
- `authority_scope` — `{allowed_scope[] (path globs), forbidden_actions[], approvals_required[]}`. `forbidden_actions` MUST include: `direct_main_write`, `external_send`, `production_deploy`, `legal_equity_payment_claims`, `cron_schedule`. `approvals_required[]` entries are `{approver_kind: founder|client, scope}` — same shape as the v0 envelope's approvals_required.
- `receipt_schema` — const-like ref `"factory_line_receipt_v0 + factory_run_receipt_v0"`: plans reuse the v0 receipt schemas; a plan may ADD a `plan_receipt_note`, never removes fields.
- `roi_priors` — `{revenue, trust, workload_relief, cloud_now, reversibility}`, each 0–5: the same five axes and 35/25/15/15/10 weights as `scripts/p0pgr_phase2_rank_v1.py`. The plan ranker NEVER invents a new base model.
- `risk_class` — enum `low|medium|high` (defaults per type, §3.3; overridable per plan).
- `auto_dispatch` — `{eligible: false}` (const false in v1) + `unlock_rule`: "per-template founder receipt naming the plan_id + plan_version; never class-wide". Low-risk templates can LATER be founder-approved per template (§9 rule 8, §10 PF-E).
- `status` — enum `draft|seed|testing|active|retired`. `seed` = shipped in the library seed, not yet founder-ratified. `retired` plans are never deleted.
- `inputs[]` / `outputs[]` — artifact-type strings from the v0 chain: `order_brief`, `research_brief`, `architecture_package`, `code_change_set`, `app_manifest`, `workflow_definition`, `test_report`, `preview_artifact`, `verification_verdict`, `receipt_chain`, `harvest_report`.
- `evidence_required` — array, minItems 1.
- `notes`.

### 3.2 The library (`PLAN_LIBRARY_SEED_1000_v1.json`)

Schema `plan_library_v1`, capacity 1000, status PROPOSED. Seeded with EXACTLY 30 complete records — 3 per plan type, the first three ids of each band — every one conforming to `PLAN_SCHEMA_v1`, status `seed`, `auto_dispatch.eligible: false`. Growth law: plans enter as `draft` via FL10 harvest or architect order; a founder receipt ratifies `seed→testing→active`; version immutable once active; retired never deleted. Authority for the library is THIS document.

### 3.3 The 10 plan types and PLAN-ID bands (100 ids each, fixed order)

| band | plan_type | id range | default line_plan spine | default risk_class |
|---|---|---|---|---|
| 1 | app_builder | PLAN-0001–0100 | FL1,FL2,FL4,FL6,FL7,FL8,FL9,FL10 | medium |
| 2 | workflow_builder | PLAN-0101–0200 | FL1,FL2,FL5,FL6,FL7,FL8,FL9,FL10 | medium |
| 3 | research | PLAN-0201–0300 | FL1,FL2,FL9,FL10 | low |
| 4 | compliance_governance | PLAN-0301–0400 | FL1,FL2,FL3,FL6,FL8,FL9,FL10 | high |
| 5 | deploy | PLAN-0401–0500 | FL6,FL7,FL8,FL9 (preview only; production stays FOUNDER_ONLY outside the substrate) | high |
| 6 | verification | PLAN-0501–0600 | FL8,FL9 | low |
| 7 | revenue | PLAN-0601–0700 | FL1,FL2,FL5\|FL4,FL6,FL7,FL8,FL9,FL10 (offers/funnels as DRAFTS; no sends, no pricing claims without founder) | high |
| 8 | client_onboarding | PLAN-0701–0800 | FL1,FL2,FL5,FL6,FL7,FL8,FL9 | medium |
| 9 | site_app_repair | PLAN-0801–0900 | FL1,FL2,FL3,FL6,FL7,FL8,FL9 | medium |
| 10 | automation_cron | PLAN-0901–1000 | FL1,FL2,FL5,FL6,FL8,FL9 — compiles + previews ONLY; activation of any schedule is double-locked: `FOUNDER-UNLOCK-CF-CRON` + per-workflow founder activation (`recurring_copilot_automation` is forbidden today) | high |

High-risk transitions (founder/client approval REQUIRED — order rule 7): anything touching production, spend, sends, legal/equity/payment claims, schedule activation, or governance zones. Every seed plan's line_plan must be a subset of its band's default spine (or justify the deviation in `notes`).

---

## §4 Pipeline — canonical summary

This section is the canonical pipeline spec for the 5-file package (a fuller narrative exists as unratified addendum draft `CLIENT_ORDER_TO_PLAN_PIPELINE_v1.md`). Six stages, extending the v0 envelope lifecycle WITHOUT changing its enum — plan matching happens inside `CLASSIFIED`:

1. **Order intake** — v0 §3 channels, unchanged.
2. **Plan match** — the classifier searches the 1000_PLAN_LIBRARY by plan_type + intent; match → `plan_ref {plan_id, plan_version}` (PLANNED envelope amendment, §2); no match → custom plan draft (status `draft`) + harvest note. Matching is deterministic-first (type/keyword); LLM-assisted only within soup-wall limits.
3. **Instantiate** — mission_template placeholders filled from the order → packet mission; plan authority_scope → sandbox allowed_scope; plan cost_cap → order budget floor/ceiling rules (budget may lower, never raise without founder).
4. **Compile** — the existing p0pgr compiler path; packet labels `FACTORY_RUN` + `PLAN:<plan_id>`.
5. **Rank** — `PLAN_RANKING_ROI_MODEL_v1` modifiers over the p0pgr base score; the queue stays `receipts/p0pgr/phase2_queue_v1.json`.
6. **Dispatch / run / verify / receipt / harvest** — the v0 substrate unchanged: FL lines, sandbox cells, FL8 external verify, FL9 receipts, FL10 harvest-back-to-library as DRAFT rows via PR (never direct `data/` writes).

**Worked example:** the addendum pipeline draft walks ORD-0002 ("client wants weekly lead-report automation") end to end — it matches the `automation_cron` band, is instantiated, compiled, and ranked, and its schedule activation lands honestly on the double-locked HOLD path (no schedule installs; `FOUNDER-UNLOCK-CF-CRON` + per-workflow founder activation both absent today).

---

## §5 Ranking model summary

Full spec: `PLAN_RANKING_ROI_MODEL_v1.json`. Deterministic — no LLM in the formula; all thresholds live in a `constants` block so future amendments are one-line diffs.

- **Base:** `p0pgr_phase2_rank_v1` — weights `{revenue:35, trust:25, workload_relief:15, cloud_now:15, reversibility:10}`, `score_base = sum(w * clamp(axis,0,5)/5)`, max 100. Identical to `scripts/p0pgr_phase2_rank_v1.py`; the plan ranker consumes the SAME queue, never a private one.
- **v1 modifiers (additive, bounded):** `risk_penalty` {low: 0, medium: −5, high: −15} · `reuse_bonus` +1 per prior run of this plan_id with FL8 external PASS, capped +5 · `cost_efficiency_bonus` +5 if `(score_base / max(cost_cap_usd, 0.01)) ≥ 20` else 0 · `premium_model_penalty` −10 if `model_policy.default_tier == "judgment"` AND `score_base < 60` · `blocked_target_penalty` −10 if any line in line_plan has a dormant/unusable primary target today (`claude_cloud_agent` dormant, blocker B2; `cloudflare_worker` CF-law-deferred for FL7).
- **Score:** `score_v1 = clamp(score_base + sum(modifiers), 0, 100)`; tie-break `(-score_v1, plan_id)`.
- **auto_dispatch_gate** (machine-checkable; ALL must hold, and dispatch STILL requires the per-template founder receipt): `risk_class == low` AND `reuse_bonus == 5` (≥5 verified runs) AND zero wall violations in those runs AND cost under cap in all runs. The model computes ELIGIBILITY only; approval is a founder receipt per template. `auto_dispatch.eligible` stays false everywhere in v1.

---

## §6 Execution lines

The resolution registry is `cloud-factory/FACTORY_LINE_REGISTRY_v0.json`, UNCHANGED — every plan run resolves its line_plan against it; a plan naming a line not in that registry is a lint reject. Plan-aware routing lives in `PLAN_LIBRARY_SEED_1000_v1.json`: `plan_type_default_line_plans` (the §3.3 band table) and `plan_type_risk_defaults`. A fuller amendment registry (same 10 FL rows plus `plan_types_served[]` and `plan_notes` per row) exists as unratified addendum draft `FACTORY_LINE_REGISTRY_v1.json` — a future founder-ratified amendment may promote it; nothing in this package depends on it.

All v0 line rules stand: dispatch/event triggers only (no cron), every line writes a receipt, FL8 pass only from the secondary CF account edge receipt, FL7 preview-only, continuity-law failure behavior, `autonomy_state: assist_only` at entry.

---

## §7 Sandbox / execution-cell model

Base law: `cloud-factory/SANDBOX_MANAGER_SPEC_v0.md`, unchanged. This section is the canonical v1 cell-model delta (a fuller delta exists as unratified addendum draft `SANDBOX_WORKTREE_MANAGER_v1.md`). v1 additions only:

- **Cell vocabulary:** cell = one ledger row; `cell_kind` enum `worktree_cell` (repo worktree), `runner_cell` (GH Actions job), `agent_cell` (claude_cloud_agent session), `edge_cell` (CF read/verify), `service_cell` (railway/supabase config-scoped). Every cell kind still gets a ledger row; the ledger gains OPTIONAL columns `plan_id`, `cell_kind` (`sandbox_ledger_v0` → v1 PLANNED amendment, PROPOSED).
- **Multi-repo cell targeting:** venture deliverables allocate cells in the venture repo (one actor · one repo · one scope); SG repo cells only for governance artifacts; cross-repo runs = one cell per repo, one writer per cell, run envelope references all cells.
- **Concurrency:** max 3 concurrent cells per run (v1 default); 1 writer cell per repo (PARALLEL_AUTOMATION L1); read cells unlimited within cost caps.
- **Plan-scoped caps:** plan `cost_cap_usd` distributes over cells; cell overrun = line halt + PARTIAL receipt (v0 rule) + plan-level rollup.
- **automation_cron cells:** may BUILD and DRY-RUN workflow definitions; may NEVER install a schedule (W7-adjacent wall; double lock per §3.3 band 10).
- **Control-surface bindings:** Studio IDE / Forge Terminal get read-only cell/run views + dispatch submit; surfaces never mutate ledger rows directly (backend computes; TO BE BUILT, CF-P2+).

---

## §8 Client product model — the workspace is the product

The client workspace (CF-P2+, Railway API + Supabase auth per v0 §3) is what a client buys: a governed place to order factory runs from a catalog of proven plans.

- **Modes** — unchanged from v0 §7: Mode 0 `factory_task` (internal founder/governance deliverable, no client surface — the only mode exercised in PF-C), Mode A `workflow_builder`, Mode B `app_builder`. Plans of every type compile into one of these three deliverable shapes.
- **Plan-type catalog:** the client browses the 10 plan types and the `active` plans within them (status `seed|draft|testing` plans are not client-visible). Catalog listings show scope, cost cap, and approval points — no legal/equity/payment claims without founder approval (claim ladder VERIFIED/DECLARED/PLANNED applies to catalog copy).
- **Visibility wall:** a client sees ONLY their own runs and artifacts (asset-gate discipline, L7 Asset Gate precedent). Client authority never exceeds their run scope.
- **Approvals model:** each plan's `authority_scope.approvals_required[]` (`{approver_kind: founder|client, scope}`) is resolved at instantiation into the run's approval rows. Client approval gates their run's preview→deliver step. Founder approval gates anything touching production, spend, sends, legal/equity/payment claims, schedule activation, or governance zones — always. Until ladder step D endpoints exist, approvals flow through the interim `receipts/factory/approval_queue_v0.json` + `QUEUED_FOUNDER_REVIEW` (blocker B1).

---

## §9 Safety rules mapping — the eight order rules

Binding for every package file. Every rule maps to a structural mechanism, not a convention:

| # | Order rule | Structural mechanism |
|---|---|---|
| 1 | No direct main writes | repo fences (`policy/repo_fences_v1.yaml`) + CODEOWNERS + `sandbox/factory/*` branches + wall W1 + `direct_main_write` in every plan's mandatory `forbidden_actions` (fence stack itself is blocker B10 — staged, uncommitted) |
| 2 | No send/contact without approval | `no_external_send` gate + env secret policy (no send-capable credentials in any sandbox cell) + `external_send` in mandatory `forbidden_actions` + guardrails `ssot/sg-guardrails-*.md` |
| 3 | No public legal/equity/payment claims without approval | `no_legal_financial_commitment` gate + claim ladder VERIFIED/DECLARED/PLANNED + FT-LEGAL routing + deliverable-text lint (CF-P1 build item) + `legal_equity_payment_claims` in mandatory `forbidden_actions` |
| 4 | No premium models unless ROI justifies | `model_policy.premium_rule` (judgment tier only if roi_priors weighted score ≥ 60 OR explicit founder order) + ranking `premium_model_penalty` −10 (§5) |
| 5 | Every plan has cost cap + authority scope + sandbox target + receipt schema | `PLAN_SCHEMA_v1` REQUIRED fields `cost_cap_usd`, `authority_scope`, `sandbox_target`, `receipt_schema` — a record missing any of them does not validate; the library validator (PF-B) rejects it |
| 6 | Every execution through cloud line or controlled sandbox | `line_plan` resolution against `cloud-factory/FACTORY_LINE_REGISTRY_v0.json` (unknown line = lint reject) + every execution cell is a sandbox ledger row (v0 CAS, one writer per cell) — there is no lineless, cell-less execution path |
| 7 | Founder/client approves high-risk transitions | `risk_class` + `approvals_required[]` resolved into run approval rows + `AWAITING_APPROVAL` state + `QUEUED_FOUNDER_REVIEW`; high-risk transition list fixed in §3.3 |
| 8 | Auto-dispatch per-template only, later | `auto_dispatch.eligible` const false in v1 + `auto_dispatch_gate` (§5: low risk, 5× FL8-verified reuse, zero wall violations, cost under cap) computes eligibility only + unlock is a per-template founder receipt naming plan_id + plan_version, never class-wide (PF-E) |

Plus, inherited verbatim from v0: all NINE P0-PGR gates on every packet and receipt (`cloud_only`, `read_only_or_reversible`, `roi_positive`, `no_deploy`, `no_external_send`, `no_legal_financial_commitment`, `no_p0_leakage`, `no_authority_change`, `founder_authorization_receipt`); the four founder triggers ONLY (FT-CAPITAL, FT-LEGAL, FT-L5-IRREVERSIBLE, FT-PHASE-UNLOCK); the default question "How does the process solve this without Sina?" — any design element that makes the founder a runtime is a defect.

---

## §10 MVP phases PF-A → PF-E (riding the CF-P1 → CF-P5 ladder)

Full ladder steps, exit criteria, and blocker detail: `PLAN_FACTORY_ACTIVATION_PLAN_v1.md` (this section is the summary). Activation-ladder step discipline throughout: **Preconditions → Artifacts → Verification → Receipt → Founder point.** A phase is DONE only when its receipt exists; each phase boundary is an FT-PHASE-UNLOCK founder receipt. Nothing below is built.

### PF-A — Library seed (THIS package; design-only, pre-build)
- **Preconditions:** founder order receipt `founder-order-1000-plan-cloud-factory-20260709T014708Z`; v0 package receipted (`CLOUD_FACTORY_SUBSTRATE_v0-20260709T015408Z`); L0 graph query receipt (header).
- **Artifacts:** the five package files, including 30 complete seed plans (3 per type, status `seed`).
- **Verification:** structural review only — every seed record carries all `PLAN_SCHEMA_v1` required fields; every line_plan is a subset of its band spine. Machine validation does not exist yet (validator is PF-B); PF-A verification is honest review, not a PASS claim.
- **Receipt:** package receipt sha256-pinning the five files (v0 package-receipt pattern).
- **Founder point:** FT-PHASE-UNLOCK — founder ratifies the package via work_order + receipt through repo fences.

### PF-B — Plan compiler + ranking glue + library validator (rides CF-P1)
- **Preconditions:** PF-A receipt; CF-P1 unlock; fence stack landed on main (blocker B10).
- **Artifacts:** library validator (TO BE BUILT; naming convention `scripts/validate_*_v1.py`) validating every library record against `PLAN_SCHEMA_v1` + band/line rules; plan-match + instantiation glue extending the existing p0pgr compiler path; ranking glue applying the §5 modifiers over `p0pgr_phase2_rank_v1` output into the SAME queue.
- **Verification:** the NEXT BUILD PACKET acceptance criteria (below) — 30/30 seeds validate; a dummy order matches, instantiates, and compiles lint-clean (R1–R9); ranking reproduces hand-computed scores.
- **Receipt:** execution receipt(s) under the `receipts/p0pgr/` conventions + a PF-B completion receipt.
- **Founder point:** FT-PHASE-UNLOCK to PF-C.

### PF-C — First founder plan runs (rides CF-P1, Mode 0 only)
- **Preconditions:** PF-B receipts; CF-P1 substrate build items live (FL9 receipt engine, sandbox ledger + allocator, walls check — v0 NEXT items 1–3).
- **Artifacts:** ≥3 plan types exercised end to end as internal founder runs (low/medium risk only — e.g. research, verification, and one medium band), each a full envelope + cell + receipt chain.
- **Verification:** FL8 external PASS on each run (secondary CF account edge receipt, never self-report); `reuse_bonus` counters begin accumulating from these receipts.
- **Receipt:** run receipts + a PF-C summary receipt.
- **Founder point:** FT-PHASE-UNLOCK to PF-D.

### PF-D — Client plan catalog (rides CF-P2)
- **Preconditions:** PF-C receipt; CF-P2 unlock (authenticated client workspace: Railway API + Supabase auth); envelope `plan_ref` amendment founder-ratified (blocker B12).
- **Artifacts:** catalog surface listing `active` plans by type; order intake wired to plan match; client visibility wall enforced.
- **Verification:** a client order → plan match → run in which the client sees only their own run; catalog copy passes the deliverable-text claim lint.
- **Receipt:** catalog activation receipt.
- **Founder point:** FT-PHASE-UNLOCK; FT-LEGAL additionally required before any pricing/payment copy appears (no public legal/equity/payment claims without approval).

### PF-E — Per-template auto-dispatch unlocks (rides CF-P3+)
- **Preconditions:** PF-D receipt; candidate templates satisfying the full `auto_dispatch_gate` (§5) with receipt evidence.
- **Artifacts:** per-template founder receipts, each naming exactly one `plan_id` + `plan_version`; the corresponding record amendment flipping that template's `auto_dispatch.eligible` (requires a founder-ratified v1.x schema amendment relaxing the const, per template — never class-wide).
- **Verification:** gate re-check at every auto-dispatch; any wall violation revokes eligibility (violation law: contain, receipt, critique, repair).
- **Receipt:** per-template unlock receipts + revocation receipts if triggered.
- **Founder point:** FT-PHASE-UNLOCK + one founder receipt PER template. Auto-dispatch of `automation_cron` plans additionally stays behind the cron double lock — likely never eligible under the low-risk-only gate.

---

## §11 Known blockers (honest)

**Inherited by reference:** B1–B10 from `cloud-factory/MVP_ACTIVATION_PLAN_v0.md` §8 apply to this package unchanged — notably B1 (approval-queue endpoints NOT BUILT), B2 (`ANTHROPIC_API_KEY` not wired; `claude_cloud_agent` lines dormant → §5 `blocked_target_penalty`), B4 (R3 cron locked — no schedule activation), B8 (`cf.*` prompt-id amendment PROPOSED), B10 (fence stack staged, uncommitted — rule 1 is convention until it lands).

**PF-specific additions:**

| # | Blocker | Impact | Path out |
|---|---|---|---|
| B11 | Library validator TO BE BUILT — nothing machine-checks plan records today | PF-A seeds are review-verified only; no PASS claim possible | PF-B NEXT BUILD PACKET (below) |
| B12 | Envelope `plan_ref` amendment PROPOSED — `client_order_to_factory_run_v0` has no plan field | Plan matching cannot be recorded in the envelope; interim: `PLAN:<plan_id>` packet label only | Founder-ratified v0→v1 envelope amendment (PF-D precondition) |
| B13 | `sandbox_ledger_v0` v1 columns (`plan_id`, `cell_kind`) PROPOSED | Cell-to-plan attribution and cell-kind accounting unavailable | Founder-ratified ledger amendment alongside the sandbox allocator build |

---

## NEXT — the single NEXT BUILD PACKET

**PF-B plan compiler + library validator** (one packet candidate; compiles to a standard `p0_prompt_packet_v1.1` through the existing compiler path; all nine gates apply; `auto_dispatch` irrelevant — this is a founder-dispatched build).

- **Mission:** build the plan library validator (validate every `PLAN_LIBRARY_SEED_1000_v1.json` record against `PLAN_SCHEMA_v1.json` + §3.3 band/line rules + §9 rule-5 required fields) and the plan compiler glue (order → plan match → mission_template instantiation → existing p0pgr compile path → §5 ranking modifiers over the existing queue).
- **Route:** `CLOUD_WORKER`.
- **Acceptance:** (1) all 30 seed plans validate against `PLAN_SCHEMA_v1` with zero errors; (2) a dummy order matches a plan and compiles lint-clean through R1–R9; (3) the ranking glue reproduces hand-computed `score_v1` values for the seed set exactly.

STOP.
