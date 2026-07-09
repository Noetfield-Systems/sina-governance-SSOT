# CLIENT ORDER TO PLAN PIPELINE v1

**Version:** 1.0.0 · **Status:** PROPOSED (design-only; nothing in this document is built or active)
**Era:** `PHASE_2_CLOUD_ONLY_ROI_TRACK`
**Authority chain:** FOUNDER_CANON v1 → P0-PGR runtime v1.1 (command brain) → cloud-factory v0 substrate → `plan-factory/PLAN_FACTORY_ARCHITECTURE_v1.md` → this document
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
**canon_version:** `founder_canon_v1.0.0`
**Founder authorization:** receipt `founder-order-1000-plan-cloud-factory-20260709T014708Z` (`receipts/p0pgr/founder/`) — design-only unlock. Building, activating, and scheduling are NOT unlocked.
**Amends:** extends the v0 envelope lifecycle (`cloud-factory/CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`) WITHOUT changing its status enum. Plan matching happens inside `CLASSIFIED`. v0 files stay live; v1 wins only on direct conflict — this pipeline is designed to have none.

---

## §0 Position — six stages on the unchanged v0 lifecycle

The v0 envelope status enum is reused verbatim:
`RECEIVED → CLASSIFIED → PACKET_COMPILED → QUEUED → SANDBOX_ALLOCATED → RUNNING → PREVIEW_READY → VERIFYING → AWAITING_APPROVAL → APPROVED → RECEIPTED → HARVESTED → CLOSED`
Exception states: `REPAIR_CANDIDATE`, `HOLD_CLOUD_UNSAFE`, `QUEUED_FOUNDER_REVIEW`, `BLOCKED_WITH_REASON`, `KILLED`. No new state is added.

| Stage | Name | Envelope status covered |
|---|---|---|
| 1 | Order intake | `RECEIVED` |
| 2 | Plan match | inside `CLASSIFIED` |
| 3 | Instantiate | inside `CLASSIFIED` (produces the compiler input) |
| 4 | Compile | `PACKET_COMPILED` |
| 5 | Rank | `QUEUED` |
| 6 | Run + verify + receipt + harvest | `SANDBOX_ALLOCATED` → `CLOSED` |

**Dispatch law for v1.** `auto_dispatch.eligible` is const `false` on every plan. Every transition
`QUEUED → SANDBOX_ALLOCATED` is a founder action (founder session or manual `workflow_dispatch`) —
no automated executor exists (M4 LOCKED) and none is assumed here. Per-template auto-dispatch
arrives LATER only via a per-template founder receipt naming `plan_id` + `plan_version`, never
class-wide (PF-E).

---

## §1 Stage 1 — Order intake

- **Inputs:** order file `receipts/factory/orders/<ORD-ID>.json` + founder authorization receipt
  in `receipts/p0pgr/founder/`. Channels are v0 §3, unchanged: `founder_session` is the only
  CF-P1 channel; `founder_control_desk` / `client_workspace` / `api` arrive CF-P2 and
  `studio_ide` CF-P2+ — all non-founder channels NOT BUILT.
- **Deterministic rules:** assign `ORD-NNNN(-slug)`; create envelope `FR-NNNN(-slug)` at status
  `RECEIVED`; validate the v0 `order` required fields exactly (`order_id`, `received_at`,
  `channel`, `principal`, `venture`, `product_mode`, `order_text`, `budget`); non-founder order
  without `auth_ref` identity binding → `BLOCKED_WITH_REASON`; timestamps machine-generated
  (`datetime.now(timezone.utc)`), never typed.
- **LLM-assisted:** none. Intake is fully deterministic.
- **Failure path (continuity law):** malformed optional fields → tag confidence and continue;
  missing required fields → reduce scope (ask nothing of the founder mid-run; file to review
  queue). Only identity-binding failure is a HARD_BLOCK-cited `BLOCKED_WITH_REASON`. Never
  default to STOP.
- **Receipt:** the order file itself + the founder authorization receipt + the envelope created
  at `RECEIVED`.

## §2 Stage 2 — Plan match

- **Inputs:** envelope `order` block; `plan-factory/1000_PLAN_LIBRARY_SEED_v1.json` (schema
  `plan_library_v1`); `plan-factory/FACTORY_LINE_REGISTRY_v1.json` band maps.
- **Deterministic rules:**
  - deterministic-first matching: `plan_type` resolution by type/keyword tables against the 10
    bands (app_builder PLAN-0001–0100 … automation_cron PLAN-0901–1000);
  - candidate filter: plan `status` in `seed|testing|active`, `venture` compatible, `line_plan`
    resolvable against FACTORY_LINE_REGISTRY_v1 — a plan naming a line not in the registry is a
    lint reject;
  - match → record `{plan_id, plan_version}` for the run. Carrier: see §7 — the envelope-level
    `plan_ref` field is a PROPOSED amendment, NOT assumed; until ratified the binding rides the
    packet label `PLAN:<plan_id>` and the stage receipts;
  - no match → custom plan draft (status `draft`) written as a run artifact + harvest note; the
    library grows only through FL10 DRAFT rows via PR, founder ratifies activation — never a
    direct write to `plan-factory/` or `data/`.
- **LLM-assisted:** intent extraction and plan_type suggestion over `order_text` only. LLM output
  is a proposal; the deterministic validator gates persistence (D7). No P0 CORE judgment text
  enters this step; any packet-bound text the LLM drafts is confined to the seven task-spec keys
  (`goal, files, constraints, done_criteria, verify_method, receipts_required, decision_verdict`).
- **Failure path (continuity law):** ambiguous match → tag confidence LOW and proceed with the
  deterministic candidate; contradictory signals → reduce scope to a research-band plan; still
  unresolved → review queue (`QUEUED_FOUNDER_REVIEW` only if a founder trigger is genuinely
  implicated). Lint reject on line resolution → repair candidate, lane continues.
- **Receipt:** the v0 `classification` block recorded in the envelope — `intent`, `product_mode`,
  `venture`, `line_plan`, `risk_flags`, `hold_labels`, `classified_by`, `classified_at`; the
  no-match path additionally writes the draft plan record under `receipts/factory/artifacts/<FR-ID>/`.

## §3 Stage 3 — Instantiate

- **Inputs:** matched plan record (PLAN_SCHEMA_v1); envelope `order` block.
- **Deterministic rules:**
  - `mission_template` `{{placeholders}}` filled from order fields → packet mission text; an
    unfillable placeholder is an instantiation failure (below) — no placeholder is silently dropped;
  - plan `authority_scope.allowed_scope` → sandbox `allowed_scope`; plan `forbidden_actions`
    (always including `direct_main_write`, `external_send`, `production_deploy`,
    `legal_equity_payment_claims`, `cron_schedule`) → run `risk_flags`/`hold_labels` inputs;
  - plan `approvals_required` → envelope `factory_run.approvals_required` rows
    (`approver_kind` founder|client, verbatim `scope`);
  - **budget law:** effective run cap = `min(order.budget.cost_cap_usd, plan.cost_cap_usd)`. An
    order budget may LOWER a plan cap; it may NEVER raise a cap above the plan's `cost_cap_usd`
    without a founder receipt naming the raise. Per-line 2.00 / per-run 5.00 v0 defaults inherit
    unless the plan says lower. Runtime breach: line halts, PARTIAL receipt, run →
    `QUEUED_FOUNDER_REVIEW` (FT-CAPITAL) — unchanged v0 rule;
  - `model_policy` copied from the plan; `judgment` tier permitted only under the plan's
    `premium_rule` (roi_priors weighted score ≥ 60 OR an explicit founder order names it) — "no
    premium models unless ROI justifies" is enforced here and again as a ranking penalty (§5).
- **LLM-assisted:** placeholder value extraction from `order_text` where the mapping is not
  literal. Output confined to the seven task-spec keys; validator gates persistence; P0 CORE
  text never enters.
- **Failure path (continuity law):** unfillable placeholder → reduce scope (drop the optional
  sub-goal) → provisional instantiation with `limitations[]`; order asks above the plan cap →
  proceed at the plan cap and file the raise request to the founder approval path;
  irreconcilable scope vs. `forbidden_actions` → `BLOCKED_WITH_REASON` citing the HARD_BLOCK.
- **Receipt:** instantiation record as run artifact
  `receipts/factory/artifacts/<FR-ID>/plan-instantiation-<ISO8601Z>.json` (writer = the PF-B
  compiler, TO BE BUILT) + effective caps recorded in envelope `order.budget` and later in
  `sandbox.cost_cap_usd`.

## §4 Stage 4 — Compile

- **Inputs:** instantiated mission + plan fields; the existing P0-PGR compiler path (compilation
  is operator/skill work today; the automated order→packet compiler is TO BE BUILT — PF-B).
- **Deterministic rules:**
  - compile a standard `p0_prompt_packet_v1.1` packet — `packet_id` `PKT-NNNN`, all nine gates
    (`cloud_only, read_only_or_reversible, roi_positive, no_deploy, no_external_send,
    no_legal_financial_commitment, no_p0_leakage, no_authority_change,
    founder_authorization_receipt`), five-axis ROI 0–5, route from the EXISTING enum
    `CLOUD_WORKER | CLOUD_RESEARCH | SESSION_EMBEDDED | REVIEW_QUEUE`;
  - packet labels: `FACTORY_RUN` + `PLAN:<plan_id>` + `FL-plan:<FL ids>`;
  - the envelope wraps the packet by reference (`packet_ref {packet_id, packet_path, route,
    lint_verdict}`); factory and plan metadata live in the envelope and labels, never inside
    P0-PGR schema fields; lint R1–R9 applies unchanged.
- **LLM-assisted:** mission and task-spec phrasing only, confined to the seven task-spec keys.
  R7 forbids routing validation/review/uncertainty to the founder; R6 forbids vague-verb
  missions without measurable acceptance.
- **Failure path (continuity law):** lint fail → repair candidate
  `receipts/p0pgr/repair_candidates/repair-<packet_id>-<ts>.json`, lane continues — never STOP
  on lint. Cloud-unsafe content → `HOLD_CLOUD_UNSAFE` (stays visible and re-rankable).
- **Receipt:** packet file `receipts/p0pgr/outbox/<packet_id>.json` + loop-state
  `loop-state-cycle-<ts>.json`; envelope status `PACKET_COMPILED` with
  `packet_ref.lint_verdict` set.

## §5 Stage 5 — Rank

- **Inputs:** packet ROI axes; plan record (`risk_class`, `cost_cap_usd`, `model_policy`, reuse
  history); `plan-factory/PLAN_RANKING_ROI_MODEL_v1.json`.
- **Deterministic rules — NO LLM anywhere in the formula:**
  - `score_base` = existing `p0pgr_phase2_rank_v1` model: weights revenue 35 / trust 25 /
    workload_relief 15 / cloud_now 15 / reversibility 10, each axis 0–5, max 100;
  - v1 modifiers, all bounded: `risk_penalty` (low 0 / medium −5 / high −15); `reuse_bonus`
    (+1 per prior run of this `plan_id` with FL8 external PASS, capped +5);
    `cost_efficiency_bonus` (+5 if `score_base / max(cost_cap_usd, 0.01) ≥ 20`);
    `premium_model_penalty` (−10 if `default_tier == judgment` and `score_base < 60`);
    `blocked_target_penalty` (−10 if any line in `line_plan` has a dormant/unusable primary
    target today — `claude_cloud_agent` dormant per blocker B2, `cloudflare_worker`
    CF-law-deferred for FL7);
  - `score_v1 = clamp(score_base + Σ modifiers, 0, 100)`; tie-break `(-score_v1, plan_id)`;
  - the queue stays `receipts/p0pgr/phase2_queue_v1.json` — the plan factory consumes the SAME
    queue and its `next_move` field, never a private one.
- **LLM-assisted:** none.
- **Failure path (continuity law):** missing reuse history → `reuse_bonus` 0 (conservative
  default) and tag confidence; unknown target availability → apply `blocked_target_penalty`
  (worst-case deterministic); a plan whose line resolution fails ranks nowhere — it is already a
  lint reject at Stage 2.
- **Receipt:** the queue row itself (shared queue file); ranking thresholds live in the model
  file's `constants` block so future amendments are one-line diffs.

## §6 Stage 6 — Run + verify + receipt + harvest

- **Inputs:** ranked queue `next_move`; founder dispatch action (v1: always manual — §0); the v0
  substrate unchanged (FL lines, sandbox cells, walls W1–W9, env profiles).
- **Deterministic rules:**
  - sandbox cell allocated per v0: `sbx-fr-NNNN-SS`, worktree `.worktrees/factory/<sandbox_id>`,
    branch `sandbox/factory/fr-NNNN(-slug)`, ledger CAS one-writer rule, second writer →
    REJECTED receipt; plan `authority_scope.allowed_scope` becomes the cell's `allowed_scope`;
    effective caps from Stage 3;
  - lines execute in `line_plan` order; every line writes
    `receipts/factory/<FR-ID>/<line_key>-<ISO8601Z>.json` (schema `factory_line_receipt_v0`);
  - FL8 PASS only from the secondary CF account edge receipt (worker
    `sina-governance-ssot-advisory`) — never builder self-report; FL8 FAIL writes a HOLD row
    blocking further line dispatch for the run;
  - bands without FL7: `preview.kind` is `dry_run_trace` (when FL6 present) or `none`;
  - bands without FL10: `HARVESTED` is a pass-through (`harvest.done` false, `report_path`
    null); plan reuse counters update from the FL9 run receipt instead;
  - FL10, where present, harvests reusable patterns AND new/amended plan drafts back to the
    library as DRAFT rows via branch + PR through full repo fences — never direct `data/` or
    `plan-factory/` writes;
  - run receipt `receipts/factory/<FR-ID>-run-<ISO8601Z>.json` (schema `factory_run_receipt_v0`;
    plans reuse the v0 receipt schemas — a plan may ADD a `plan_receipt_note`, never removes
    fields); run cannot reach `CLOSED` unless `receipts.chain_complete` is true; receipts and
    artifacts are NEVER deleted.
- **LLM-assisted:** worker execution inside cells only. Every worker prompt is assembled through
  the soup wall — the seven allowed task-spec keys and nothing else; P0 CORE judgment text never
  enters a factory worker prompt.
- **Failure path (continuity law):** line failure degrades in order — tag confidence → reduce
  scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue. Timeout → kill
  + PARTIAL receipt with `limitations[]`. Cost breach → line halt + PARTIAL +
  `QUEUED_FOUNDER_REVIEW` (FT-CAPITAL). Wall trip at exit → contain, receipt, critique, repair.
  `BLOCKED_WITH_REASON` only citing a HARD_BLOCK reason.
- **Receipt:** the full v0 chain — line receipts + run receipt with all nine `gates_checked`,
  `quality_state` (`PASS|PARTIAL|PROVISIONAL|FAIL`), evidence with sha256, and cost roll-up
  line receipt → run receipt → `phase2_scorecard_v1.json` `counters.cost_usd`.

---

## §7 The `plan_ref` amendment — PROPOSED, never assumed

The v0 `classification` block has no plan field. This package PLANS an OPTIONAL envelope schema
v0→v1 amendment: `classification.plan_ref {plan_id, plan_version}`. Status: **PROPOSED** — it
requires founder ratification of a `client_order_to_factory_run` v1 schema and is not silently
assumed anywhere in this pipeline. Until ratified, the plan binding is carried by (a) the packet
label `PLAN:<plan_id>`, (b) the Stage 3 instantiation artifact, and (c) line/run receipts.
Nothing breaks if the amendment never lands; runs merely stay label-bound.

## §8 Order-rule mapping (all eight, structural)

| Order rule | Mechanism in this pipeline |
|---|---|
| No direct main writes | sandbox branches + PR through full repo fences (W1); FL10 library growth via PR only |
| No send/contact without approval | `no_external_send` gate + deny-by-default env secret policy (no send credentials in cells) |
| No public legal/equity/payment claims without approval | `no_legal_financial_commitment` gate + `legal_equity_payment_claims` in every plan's `forbidden_actions` + claim ladder |
| No premium models unless ROI justifies | `model_policy.premium_rule` at Stage 3 + `premium_model_penalty` at Stage 5 |
| Every plan has cost cap + authority scope + sandbox target + receipt schema | PLAN_SCHEMA_v1 required fields, checked at Stages 2–3 |
| Every execution through cloud line or controlled sandbox | `line_plan` resolution against FACTORY_LINE_REGISTRY_v1 + cell ledger; no other execution path exists |
| Founder/client approves high-risk transitions | `risk_class` + `approvals_required` rows + `AWAITING_APPROVAL` gate; production/spend/sends/legal/schedule always founder |
| Auto-dispatch per-template only, later | `auto_dispatch.eligible` const false in v1; unlock only via per-template founder receipt naming `plan_id` + `plan_version` |

---

## §9 Worked example — ORD-0002 weekly lead-report automation (illustrative; nothing here has run)

1. **Stage 1 — intake.** Founder drops `receipts/factory/orders/ORD-0002-weekly-lead-report.json`
   (channel `founder_session` — the only CF-P1 channel; the client's request is relayed by the
   founder), `product_mode: workflow_builder`, `venture: trustfield`,
   `budget.cost_cap_usd: 3.00`. Founder authorization receipt present. Envelope
   `FR-0002-weekly-lead-report` at `RECEIVED`.
2. **Stage 2 — plan match.** Keywords "weekly … report … automation" → `plan_type:
   automation_cron` (band PLAN-0901–1000). Deterministic candidate: `PLAN-0901` v1.0.0
   (automation_cron seed: scheduled report definition template; seed content authoritative in
   `1000_PLAN_LIBRARY_SEED_v1.json`). `classification.line_plan: [FL1, FL2, FL5, FL6, FL8, FL9]`
   (band spine), `risk_flags: ["cron_schedule"]`, `hold_labels: []`. Status `CLASSIFIED`.
   Binding carried as label `PLAN:PLAN-0901` (§7 — no envelope `plan_ref` yet).
3. **Stage 3 — instantiate.** `mission_template` placeholders filled from the order (report
   subject = leads, cadence = weekly, output = report automation definition DRAFT). Effective
   run cap = min(3.00 order, 5.00 plan) = **3.00** — the order lowered the cap; raising above
   5.00 would have required a founder receipt. `forbidden_actions` includes `cron_schedule`;
   the plan's `approvals_required` adds a founder row.
4. **Stage 4 — compile.** Packet `PKT-0310-weekly-lead-report` (next free PKT id — packet ids
   never encode plan ids): nine gates, route `CLOUD_WORKER`, labels `FACTORY_RUN` +
   `PLAN:PLAN-0901` + `FL-plan:FL1,FL2,FL5,FL6,FL8,FL9`. Lint R1–R9 → `lint_verdict: ROUTED`.
   Status `PACKET_COMPILED`.
5. **Stage 5 — rank.** roi_priors (revenue 3, trust 3, workload_relief 4, cloud_now 4,
   reversibility 4) → `score_base` = 21+15+12+12+8 = **68**. Modifiers: `risk_penalty` −15
   (automation_cron = high); `reuse_bonus` 0 (no prior FL8-verified runs of PLAN-0901);
   `cost_efficiency_bonus` 0 (68 / 5.00 = 13.6 < 20, computed on the plan's `cost_cap_usd`);
   `premium_model_penalty` 0 (`default_tier: standard`); `blocked_target_penalty` −10
   (FL1/FL2/FL5 primary `claude_cloud_agent` dormant — B2, ANTHROPIC_API_KEY not wired).
   `score_v1 = clamp(68 − 15 + 0 + 0 − 10) =` **43**. Queued in
   `receipts/p0pgr/phase2_queue_v1.json`. Status `QUEUED`.
6. **Stage 6 — run.** Founder dispatches (manual — no auto-dispatch in v1). Cell
   `sbx-fr-0002-01`, branch `sandbox/factory/fr-0002-weekly-lead-report`, `env_profile: none`
   (draft-writing needs no secrets), cap 3.00. FL1 research digest → FL2 architecture note →
   FL5 produces the governed workflow definition DRAFTS: `cf.*` prompt-registry row drafts +
   automation-registry row drafts + GH Actions workflow YAML draft **with the cron block
   commented out** (precedent: the P0-PGR shadow workflow keeps its cron commented until a
   founder unlock receipt exists). FL6 contract tests + dry-run trace →
   `preview {available: true, kind: "dry_run_trace", ref: <artifact>}`, status `PREVIEW_READY`.
   FL8 external verify PASS via secondary CF account edge receipt, status `VERIFYING` →
   `AWAITING_APPROVAL`.
7. **Approval.** `approvals_required`: `[{approver_kind: "founder", scope: "accept
   weekly-lead-report workflow definition DRAFT — deliverable only; no schedule installed"}]`.
   Founder approves via the interim `receipts/factory/approval_queue_v0.json` (L8
   approval-queue endpoints NOT BUILT). Status `APPROVED`.
8. **Receipt + close.** FL9 run receipt: nine `gates_checked`, `quality_state: PASS`, cost
   roll-up under 3.00, `plan_receipt_note: "PLAN-0901 v1.0.0 run 1"`. Status `RECEIPTED`;
   `HARVESTED` passes through (`harvest.done: false` — no FL10 in the automation_cron band;
   PLAN-0901's reuse counter updates from this run receipt); `CLOSED` with
   `chain_complete: true`.
9. **What did NOT happen — the double lock, shown honestly.** No schedule was installed and none
   can be:
   - **Lock 1:** `FOUNDER-UNLOCK-CF-CRON` receipt — does not exist;
   - **Lock 2:** per-workflow founder activation receipt for this workflow — does not exist;
   - `recurring_copilot_automation` is a forbidden action today; `cron_schedule` is in the
     plan's `forbidden_actions`; automation_cron plans compile + preview ONLY;
   - the activation request is filed as a row in the interim approval queue and the run
     receipt's `limitations[]` records: "schedule activation HOLD — double-locked". Activation,
     if ever, is a separate later founder-gated step outside any factory run.

---

## NEXT — follow-on work orders (packet candidates, none dispatched)

1. **PF-B plan compiler + library validator** (route `CLOUD_WORKER`): implement Stages 2–4 as
   code — deterministic matcher, instantiation writer (`plan-instantiation-<ISO8601Z>.json`),
   packet compilation glue. Acceptance: 30 seed plans validate against PLAN_SCHEMA_v1; a dummy
   order matches a plan and compiles lint-clean; ranking reproduces hand-computed scores (the §9
   arithmetic is the test vector).
2. **Envelope v0→v1 `plan_ref` amendment proposal** (§7) — drafted for founder ratification;
   not assumed by anything above.
3. **Ranking-glue wiring** so `PLAN_RANKING_ROI_MODEL_v1` modifiers apply over the shared
   `phase2_queue_v1.json` without forking the queue.
4. **Interim approval-queue conventions** for plan runs (`receipts/factory/approval_queue_v0.json`)
   until L8 ladder step D endpoints exist.
