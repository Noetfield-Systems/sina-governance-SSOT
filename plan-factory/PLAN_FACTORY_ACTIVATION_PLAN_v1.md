# PLAN FACTORY — ACTIVATION PLAN v1 (PF-A → PF-E)

**Version:** 1.0.0
**Status:** PROPOSED — design-only. Nothing in this plan is built, active, or verified. Every component below is TO BE BUILT unless it cites an existing path.
**Era:** `PHASE_2_CLOUD_ONLY_ROI_TRACK`
**Authority:** `plan-factory/PLAN_FACTORY_ARCHITECTURE_v1.md` ← Cloud Factory Substrate v0 (`cloud-factory/`) ← P0-PGR runtime v1.1 ← FOUNDER_CANON v1
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
**canon_version:** `founder_canon_v1.0.0`
**Founder authorization:** `founder-order-1000-plan-cloud-factory-20260709T014708Z`, deliverable set revised to five files by `founder-order-1000-plan-l0-first-5file-20260709T021931Z` (`receipts/p0pgr/founder/`) — design-only unlock. Each build phase below requires its own founder work_order + receipt.
**Companion files:** `PLAN_SCHEMA_v1.json` · `PLAN_LIBRARY_SEED_1000_v1.json` · `PLAN_RANKING_ROI_MODEL_v1.json`

---

## 0. Doctrine (binding on every step below)

**Ladder step discipline.** Every step: Preconditions → Artifacts → Verification → Receipt → Founder point. A step is DONE only when its receipt exists (`docs/ACTIVATION_LADDER_v1.md` rule). Agent claims, chat summaries, and PR descriptions are not receipts.

**Phases ride the substrate ladder.** PF phases never open a parallel ungoverned track: PF-B/PF-C ride CF-P1 (internal founder-only substrate), PF-D rides CF-P2 (authenticated client workspace), PF-E rides CF-P3+ — each CF phase gate in `cloud-factory/MVP_ACTIVATION_PLAN_v0.md` remains a hard precondition here.

**Phase unlock.** A phase opens only on an FT-PHASE-UNLOCK founder receipt AND the prior phase's exit criteria (§7). Autonomy expands only on receipt streaks (L8 earned-autonomy `expansion_rules`), never chat approval.

**No cron anywhere.** All plan-factory triggers are `dispatch`/`event`. `automation_cron` plans compile and dry-run ONLY; installing any schedule is double-locked: `FOUNDER-UNLOCK-CF-CRON` + per-workflow founder activation (`recurring_copilot_automation` is a forbidden action today). `cron_schedule` sits in every plan's mandatory `forbidden_actions`.

**No code / no deploy in this package.** This activation plan schedules FUTURE build packets; it builds nothing itself. Production deploy is absent from the substrate in every phase (FL7 preview-only; HARD_BLOCK reason 2).

**Continuity law.** Never default to STOP. Degrade: tag confidence → reduce scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue. BLOCKED_WITH_REASON only with a cited HARD_BLOCK reason.

---

## 1. Phase map

| Phase | Name | Rides | Product surface | Status |
|---|---|---|---|---|
| PF-A | Library seed (design) | — | none (design package) | THIS PACKAGE — awaiting founder ratification |
| PF-B | Plan compiler + ranking glue + library validator | CF-P1 | internal | PROPOSED — locked behind PF-A ratification + CF-P1 unlock |
| PF-C | First founder plan runs (Mode 0 only) | CF-P1 | internal | PROPOSED — locked behind PF-B exit |
| PF-D | Client plan catalog | CF-P2 | authenticated client workspace | PROPOSED — locked behind PF-C exit + CF-P2 unlock |
| PF-E | Per-template auto-dispatch unlocks | CF-P3+ | internal + client | PROPOSED — locked behind PF-D exit; per-template founder receipts only |

---

## 2. PF-A — Library seed (this package)

- **Preconditions:** founder order receipts (header); v0 package receipted (`CLOUD_FACTORY_SUBSTRATE_v0-20260709T015408Z`) and locked on branch (commit `b4e4cdd2`); L0-graph-first orientation receipts (verifier PASS `receipts/l0-repo-graph-verify-20260709T021931Z.json`, compact map `receipts/l0-map-1000-plan-5file-20260709T022035Z.json`).
- **Artifacts:** the five package files, including 30 complete seed plans (3 per type, first three ids of each band, status `seed`, `auto_dispatch.eligible: false` everywhere).
- **Verification:** structural review + deterministic checks only (JSON parses; 30/30 records carry every `PLAN_SCHEMA_v1` required field; band/id allocation correct; line plans subsets of band spines or justified; ROI-model examples recompute exactly). The machine validator does not exist yet (B11) — PF-A verification is honest review, not a machine PASS claim.
- **Receipt:** package receipt sha256-pinning the five files (v0 package-receipt pattern).
- **Founder point:** FT-PHASE-UNLOCK — founder ratifies via work_order + receipt through repo fences.

## 3. PF-B — Plan compiler + ranking glue + library validator (rides CF-P1)

- **Preconditions:** PF-A receipt + founder ratification; CF-P1 unlock; fence stack landed on main (blocker B10); CF-P1-B/C substrate items (sandbox ledger + allocator + walls checker, order→packet compiler glue) built per `cloud-factory/MVP_ACTIVATION_PLAN_v0.md`.
- **Artifacts (all TO BE BUILT, each its own packet):** library validator (`scripts/validate_*_v1.py` convention) enforcing `PLAN_SCHEMA_v1` + band/line rules + rule-5 required fields; plan-match + instantiation glue extending the existing p0pgr compiler path (packet labels `FACTORY_RUN` + `PLAN:<plan_id>`); ranking glue applying the `PLAN_RANKING_ROI_MODEL_v1` modifiers over `scripts/p0pgr_phase2_rank_v1.py` output into the SAME queue (`receipts/p0pgr/phase2_queue_v1.json`).
- **Verification:** all 30 seeds validate with zero errors; a dummy order matches a plan, instantiates its mission_template, and compiles lint-clean through R1–R9; a seeded lint-fail files a repair candidate and the lane continues; ranking glue reproduces the two hand-computed examples exactly (66.0 → 71.0; 56.0 → 21.0).
- **Receipt:** execution receipts per packet + a PF-B completion receipt.
- **Founder point:** FT-PHASE-UNLOCK to PF-C.

## 4. PF-C — First founder plan runs (rides CF-P1, Mode 0 only)

- **Preconditions:** PF-B receipts; CF-P1 dispatch workflow live (`workflow_dispatch` only, motor registered before first run).
- **Artifacts:** ≥3 plan types exercised end to end as internal founder runs from the seed library — low/medium risk only (e.g. `research` PLAN-0201, `verification` PLAN-0501/0503, one medium band such as `workflow_builder` PLAN-0102); each run a full envelope + cell + receipt chain; costs within caps (≤2.00/line, ≤5.00/run).
- **Verification:** FL8 external PASS on each run (secondary CF account edge receipt — never builder self-report); zero W1–W9 wall violations; `reuse_bonus` counters begin accumulating from these receipts.
- **Receipt:** run receipts + a PF-C summary receipt.
- **Founder point:** authorizes each `ORD` (founder_session channel); FT-PHASE-UNLOCK to PF-D.

## 5. PF-D — Client plan catalog (rides CF-P2)

- **Preconditions:** PF-C receipt; CF-P2 unlock (Railway API + Supabase auth workspace per v0 §3); envelope `plan_ref` amendment founder-ratified (B12).
- **Artifacts:** catalog surface listing `active` plans by plan type (seed/draft/testing plans not client-visible); order intake wired to plan match; client visibility wall enforced (a client sees ONLY their own runs — asset-gate discipline).
- **Verification:** one client order → plan match → run under a founder-controlled test identity with zero cross-client visibility events; catalog copy passes the claim-ladder lint (no legal/equity/payment claims without founder approval).
- **Receipt:** catalog activation receipt.
- **Founder point:** FT-PHASE-UNLOCK; FT-LEGAL additionally required before any pricing/payment copy appears.

## 6. PF-E — Per-template auto-dispatch unlocks (rides CF-P3+)

- **Preconditions:** PF-D receipt; candidate templates satisfying the full `auto_dispatch_gate` on real receipts: `risk_class == low` AND `reuse_bonus == 5` (≥5 runs with FL8 external PASS) AND zero wall violations across those runs AND cost under cap in all runs.
- **Artifacts:** per-template founder receipts, each naming exactly one `plan_id` + `plan_version`; the corresponding founder-ratified record amendment flipping that single template's `auto_dispatch.eligible` (the schema const relaxes per template via amendment — never class-wide).
- **Verification:** gate re-check at every auto-dispatch; any wall violation revokes eligibility (contain → receipt → critique → repair) with a revocation receipt.
- **Receipt:** per-template unlock receipts; revocation receipts if triggered.
- **Founder point:** FT-PHASE-UNLOCK + one founder receipt PER template. Auto-dispatch never unlocks scheduling — `cron_schedule` stays forbidden regardless; `automation_cron` templates are effectively never eligible under the low-risk-only gate.

---

## 7. Per-phase exit criteria (receipt streaks)

| Phase | Exit criteria (ALL required) | Unlock to next |
|---|---|---|
| PF-A | 5 package files receipted with sha256 pins · deterministic checks green · founder ratification work_order signed | FT-PHASE-UNLOCK PF-B (with CF-P1) |
| PF-B | 30/30 seeds machine-validate · dummy order compiles lint-clean · ranking reproduces hand-computed scores exactly · seeded failure files a repair candidate, lane continues | FT-PHASE-UNLOCK PF-C |
| PF-C | ≥3 plan types run end-to-end · FL8 external PASS each · zero wall violations · costs under caps · complete receipt chains | FT-PHASE-UNLOCK PF-D (with CF-P2) |
| PF-D | ≥3 client orders under test identities · zero cross-client visibility events · catalog copy claim-lint clean · 100% non-founder orders carry auth_ref | FT-PHASE-UNLOCK PF-E (with CF-P3) |
| PF-E | steady state — each unlock is one founder receipt per template; FT-PHASE-UNLOCK retires only per L8 expansion_rules (N=8 promote-class streak); FT-L5-IRREVERSIBLE never retires | — |

---

## 8. Known blockers (honest, current as of 2026-07-09)

**Inherited by reference:** B1–B10 from `cloud-factory/MVP_ACTIVATION_PLAN_v0.md` §8 apply unchanged — notably B1 (approval-queue endpoints NOT BUILT; interim `receipts/factory/approval_queue_v0.json`), B2 (`ANTHROPIC_API_KEY` not wired — `claude_cloud_agent` dormant; ranking `blocked_target_penalty` applies), B4 (R3 cron locked), B8 (`cf.*` prompt-id amendment PROPOSED), B10 (fence stack committed on branch `cursor/machine-autonomy-loops-v1` at `b4e4cdd2` but not yet merged to main — rule 1 is convention until it lands on main).

| # | Blocker | Impact | Path out |
|---|---|---|---|
| B11 | Library validator TO BE BUILT | PF-A seeds are review-verified only; no machine PASS claim | PF-B build packet (§9) |
| B12 | Envelope `plan_ref` amendment PROPOSED (`client_order_to_factory_run_v0` has no plan field) | Plan matching recorded only as packet label `PLAN:<plan_id>` | Founder-ratified v0→v1 envelope amendment (PF-D precondition) |
| B13 | `sandbox_ledger_v0` v1 columns (`plan_id`, `cell_kind`) PROPOSED | Cell-to-plan attribution unavailable | Founder-ratified ledger amendment alongside the sandbox allocator build |
| B14 | `plan-factory/` not in `scripts/build_repo_graph_v1.py` SUBSYSTEM_DIRS | This package is invisible to L0 graph queries | One-line builder amendment + rebuild + verify receipt (deferred — current order forbids code) |

---

## 9. NEXT — the single NEXT BUILD PACKET

**PF-B plan compiler + library validator** (compiles to a standard `p0_prompt_packet_v1.1` through the existing compiler path; all nine gates apply; founder-dispatched build).

- **Mission:** build the plan library validator (every `PLAN_LIBRARY_SEED_1000_v1.json` record against `PLAN_SCHEMA_v1.json` + band/line rules + rule-5 required fields) and the plan compiler glue (order → plan match → mission_template instantiation → existing p0pgr compile path → ranking modifiers over the existing queue).
- **Route:** `CLOUD_WORKER`.
- **Acceptance:** (1) 30/30 seed plans validate with zero errors; (2) a dummy order matches a plan and compiles lint-clean through R1–R9; (3) the ranking glue reproduces the model's two worked examples exactly (66.0 → 71.0 and 56.0 → 21.0).

STOP.
