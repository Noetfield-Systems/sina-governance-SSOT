# CLOUD FACTORY SUBSTRATE — MVP ACTIVATION PLAN v0

**Version:** 0.1.0
**Status:** PROPOSED — design-only. Nothing in this plan is built, active, or verified. Every component below is TO BE BUILT unless it cites an existing path.
**Era:** `PHASE_2_CLOUD_ONLY_ROI_TRACK`
**Authority:** `cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md` ← P0-PGR runtime v1.1 (command brain) ← FOUNDER_CANON v1
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
**canon_version:** `founder_canon_v1.0.0`
**Founder authorization:** `receipts/p0pgr/founder/founder-order-cloud-factory-substrate-20260709T011955Z` — design-only unlock. Building and deploying are NOT unlocked by this receipt; each build phase requires its own founder work_order + receipt.
**Companion artifacts:** `cloud-factory/FACTORY_LINE_REGISTRY_v0.json` · `cloud-factory/SANDBOX_MANAGER_SPEC_v0.md` · `cloud-factory/CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`

---

## 0. Doctrine (binding on every step below)

**Ladder step discipline.** Every step: Preconditions → Artifacts → Verification → Receipt → Founder point. A step is DONE only when its receipt exists (`docs/ACTIVATION_LADDER_v1.md` rule). Agent claims, chat summaries, and PR descriptions are not receipts.

**Phase unlock.** A phase opens only on an FT-PHASE-UNLOCK founder receipt AND the prior phase's receipt-streak exit criteria (§7). Streaks follow the L8-EARNED-AUTONOMY `expansion_rules` pattern (`data/machine_autonomy_loops_v1.json`): 3× verifier PASS + 3× drift PASS for widening; N=8 streak for promote-class trigger retirement. Autonomy expands only on receipt streaks, never chat approval.

**Every motor enters `assist_only`.** Every factory line and every new motor starts at autonomy_state `assist_only`. Promotion to `registered_motor` requires `workflow_audit_pass` + `no_parallel_conflict`; registration in `data/github_automation_registry_v1.json` precedes first run (PARALLEL_AUTOMATION L4: registry is routing truth).

**DECLARED vs VERIFIED.** A line is DECLARED at merge and VERIFIED only after a 24h zero-manual window of scheduled, externally-written receipts closes green. Manual green ≠ cron green. Because v0 is dispatch-only (no cron), no substrate line can reach VERIFIED before the cron unlock — every CF-P1 line honestly stays DECLARED.

**No cron anywhere until founder unlock receipt.** All triggers in v0 are `dispatch` or `event`. Scheduled automation for the substrate requires a founder unlock receipt named `FOUNDER-UNLOCK-CF-CRON` (precedent naming: `FOUNDER-UNLOCK-R3-CRON-SHADOW`). Scorecard directive stands: ladder_r3 "HOLD — cron disabled".

**Continuity law.** Never default to STOP. Degrade in order: tag confidence → reduce scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue. HARD_BLOCK only with a cited HARD_BLOCK reason, as BLOCKED_WITH_REASON.

**Gates and triggers.** All nine P0-PGR gates verbatim on every packet and receipt: `cloud_only, read_only_or_reversible, roi_positive, no_deploy, no_external_send, no_legal_financial_commitment, no_p0_leakage, no_authority_change, founder_authorization_receipt`. Founder touchpoints are exactly four: FT-CAPITAL, FT-LEGAL, FT-L5-IRREVERSIBLE, FT-PHASE-UNLOCK. Default question on every design element: "How does the process solve this without Sina?" — a founder-as-runtime element is a defect.

---

## 1. Phase map

| Phase | Name | Product surface | Status |
|---|---|---|---|
| CF-P1 | Internal founder-only cloud factory | founder_session orders only | PROPOSED — first build phase |
| CF-P2 | Authenticated client workspace | client_workspace + api channels | PROPOSED — locked behind CF-P1 exit |
| CF-P3 | Workflow builder (Mode A GA) | FL5 governed workflow definitions | PROPOSED — locked behind CF-P2 exit |
| CF-P4 | No-code app builder (Mode B GA) | FL4 template-stack apps, preview only | PROPOSED — locked behind CF-P3 exit |
| CF-P5 | Paid client platform | contracts + payment rails | PROPOSED — locked behind CF-P4 exit + FT-LEGAL + FT-CAPITAL |

Each phase beyond CF-P1 compiles its own ladder steps at unlock time under the same step discipline. Only CF-P1 steps are specified in full here.

---

## 2. Phase CF-P1 — internal founder-only cloud factory

**Goal:** one order (`ORD-NNNN`) from the founder flows order → packet → sandbox → lines → verified receipt chain, entirely in cloud, with zero client exposure and zero cron.

**Scope:**
- Channels: `founder_session` ONLY — order file at `receipts/factory/orders/<ORD-ID>.json` + founder authorization receipt. No network intake exists in CF-P1.
- Triggers: `workflow_dispatch` and `event` only.
- Minimum viable line set: FL1 (research), FL2 (architecture), FL3 (code), FL6 (test), FL8 (verifier), FL9 (receipt). FL7 (deploy_preview) runs as PR + GH Actions artifact preview only. FL10 (harvest) runs as manual-dispatch harvest. FL4/FL5 are NOT in CF-P1 scope.
- All lines `assist_only`; all runs end at PREVIEW/RECEIPTED — production deploy is absent from the substrate (HARD_BLOCK reason 2).

### CF-P1-A. Package ratification (three synchronized fence edits + registry pointers)

- **Preconditions:** design-only founder receipt exists (header); founder signs a NEW ratification work_order — the design receipt does not unlock build; the five `cloud-factory/` package files merged as PROPOSED via PR passing repo fences.
- **Artifacts:** the three synchronized zone edits (zone list is duplicated in three places and all must change together): `policy/repo_fences_v1.yaml` protected_zones += `cloud-factory/`; the hardcoded CODEOWNERS-coverage zone list inside `.github/workflows/repo-fences-v1.yml`; a `.github/CODEOWNERS` row assigning `cloud-factory/` to `@Noetfield-Systems/sg-governance`. Plus registry pointers: `data/founder_canon_v1.json` pointer rows for the substrate package (pattern: existing governance_* pointers). RF_POLICY_LAW_MUTATION applies: PR body carries work_order_id + receipt references.
- **Verification:** `scripts/check_repo_fences_v1.py` PASS on the ratification PR; `tests/repo_fences/run_negative_tests.py` green; CODEOWNERS-coverage step green with the new zone.
- **Receipt:** `receipts/cloud-factory-cf-p1-a-ratification-<ISO8601Z>.json` (carries receipt_id + canon_version).
- **Founder point:** signs the ratification work_order and merges (no direct main writes; CODEOWNERS review on main).

### CF-P1-B. Sandbox allocator + ledger + walls checker + negative tests

- **Preconditions:** CF-P1-A receipt exists.
- **Artifacts (all TO BE BUILT):** sandbox allocator implementing `cloud-factory/SANDBOX_MANAGER_SPEC_v0.md` (`git worktree add .worktrees/factory/<sandbox_id> -b sandbox/factory/<fr-id>`; generalizes TrustField `ensure_worktree_sandbox()` from `scripts/bridge_loops_intake_www_upgrade_v1.py`); ledger `receipts/factory/sandbox_ledger_v0.json` (schema `sandbox_ledger_v0`, one writer per task cell, second writer → REJECTED receipt, CAS per PARALLEL_AUTOMATION L1); walls checker `scripts/check_sandbox_walls_v0.py` (W1–W9 as mechanical exit checks, not mid-run permission loops — canon intent filter Q3); negative-test battery modeled on `tests/repo_fences/run_negative_tests.py` — one known-bad mutation per wall W1–W9, each expected FAIL with its wall id.
- **Verification:** allocate → release cycle on a dummy `sbx-fr-0000-01` writes and clears ledger rows; concurrent second allocation of the same cell yields a REJECTED receipt; all W1–W9 negative tests fire; env_profile defaults to `none` and no send-capable credential (ADMIN_TOKEN, TELEGRAM_*, mail keys) is reachable from the worktree environment.
- **Receipt:** `receipts/cloud-factory-cf-p1-b-sandbox-manager-<ISO8601Z>.json`.
- **Founder point:** none.

### CF-P1-C. Order → packet compiler glue

- **Preconditions:** CF-P1-A receipt exists.
- **Artifacts (TO BE BUILT):** order intake convention `receipts/factory/orders/<ORD-ID>.json`; classification output (intent, product_mode, venture, line_plan[], risk_flags[], hold_labels[]); compilation into a standard `p0_prompt_packet_v1.1` packet via the EXISTING compiler path (packet_id `PKT-NNNN`, all nine gates, five-axis ROI 0–5, route from the existing enum CLOUD_WORKER | CLOUD_RESEARCH | SESSION_EMBEDDED | REVIEW_QUEUE); packet labels `FACTORY_RUN` + `FL-plan:<FL ids>`; envelope `client_order_to_factory_run_v0` wrapping the packet by reference (`packet_ref {packet_id, packet_path}`) — factory metadata lives in the envelope, never inside the packet (no P0-PGR schema mutation in v0; `no_authority_change`). Worker prompts assembled from the packet carry ONLY the seven allowed task-spec keys (goal, files, constraints, done_criteria, verify_method, receipts_required, decision_verdict) — gated by `scripts/verify_p0_core_output_soup_wall_gate_v1.py`.
- **Verification:** dummy `ORD-0001` compiles lint-clean under existing R1–R9 lint (`scripts/p0pgr_packet_lint_v1.py`); a seeded lint-fail order files `receipts/p0pgr/repair_candidates/repair-<packet_id>-<ts>.json` and the lane continues; soup-wall gate PASS on the assembled worker prompt; ROI ranking via `scripts/p0pgr_phase2_rank_v1.py` places the packet in `receipts/p0pgr/phase2_queue_v1.json`.
- **Receipt:** `receipts/cloud-factory-cf-p1-c-compiler-glue-<ISO8601Z>.json`.
- **Founder point:** none.

### CF-P1-D. Dispatch workflow (workflow_dispatch only)

- **Preconditions:** CF-P1-B and CF-P1-C receipts exist.
- **Artifacts (TO BE BUILT):** GH Actions dispatch workflow patterned on the R2 cloud-proven shadow-cycle workflow (`.github/workflows/p0pgr-shadow-cycle-v1.yml` — existed only on the now-deleted branch `cursor/language-layer-v1`, not on main; evidence: `receipts/p0pgr/P0PGR_R2_CLOUD_MANUAL_PASS_v1-20260709T001540Z.json`, runs 28984157746/28984159107) and, for a readable in-repo dispatch skeleton, `.github/workflows/brain-loop-autorun-v1.yml` (its `schedule:` block must NOT be copied) — `workflow_dispatch` ONLY, no cron line (cron stays absent until `FOUNDER-UNLOCK-CF-CRON`), minimal permissions, and an independent receipt-validation job step (jsonschema over the produced receipts — "never trust the cycle's own claim"); motor `gh_actions_factory_dispatch_v0` registered in `data/github_automation_registry_v1.json` with owns/must_not_own BEFORE first run; autonomy_state `assist_only`.
- **Verification:** one manual dispatch runs lint → route → sandbox allocation dry pass and the independent validation step PASSes against `factory_line_receipt_v0` / `factory_run_receipt_v0` schemas; grep proves zero `schedule:` triggers in the workflow; registry row exists before the first run timestamp.
- **Receipt:** `receipts/cloud-factory-cf-p1-d-dispatch-workflow-<ISO8601Z>.json`.
- **Founder point:** none (dispatch itself is founder-manual by construction in CF-P1).

### CF-P1-E. First end-to-end run — FR-0001

- **Preconditions:** CF-P1-B/C/D receipts exist; founder order `ORD-0001` + authorization receipt in `receipts/p0pgr/founder/`; if `claude_cloud_agent` lines are used, ANTHROPIC_API_KEY wired by founder — otherwise those lines degrade to their secondary target (continuity law: reduce scope), recorded in `executor_route_note`.
- **Artifacts:** run `FR-0001` — an internal governance deliverable (zero client exposure) through FL1 → FL2 → FL3 → FL6 → FL7 (PR + artifact preview) → FL8 → FL9, with FL10 as a separate manual-dispatch harvest; sandbox `sbx-fr-0001-01` on branch `sandbox/factory/fr-0001`; line receipts `receipts/factory/FR-0001/<line_key>-<ISO8601Z>.json`; run receipt `receipts/factory/FR-0001-run-<ISO8601Z>.json`; artifacts under `receipts/factory/artifacts/FR-0001/` with sha256 per artifact.
- **Verification:** run traverses RECEIVED → … → RECEIPTED without manual state edits; `scripts/check_sandbox_walls_v0.py` exit PASS (zero W1–W9 violations); costs within caps (2.00 USD/line, 5.00 USD/run) and rolled up line → run → `phase2_scorecard_v1.json` counters.cost_usd; every line receipt carries all nine `gates_checked` + evidence items (url_fetch|script_run|file_stat|hash).
- **Receipt:** the FR-0001 run receipt (schema `factory_run_receipt_v0`) IS this step's receipt.
- **Founder point:** authorizes `ORD-0001` (founder_session channel); resolves any production-facing HOLD row raised during the run.

### CF-P1-F. Verifier + receipt chain proof

- **Preconditions:** CF-P1-E receipt exists.
- **Artifacts:** FL8 verification of FR-0001 via the EXISTING secondary-CF-account read/verify path only (account `b7282b4a5c17b84d62e3ef8866b878f8`, worker `sina-governance-ssot-advisory`) — no new CF control plane in v0; independence evidence per the `scripts/prove_verifier_independence_v1.py` pattern; receipt-chain completeness proof (every line receipt referenced by the run receipt; every artifact sha256 present; scorecard counters incremented).
- **Verification:** FL8 pass_rule holds — PASS only from the secondary CF account edge receipt, never builder self-report (autonomy loop L3 law); adversarial test: a seeded builder self-report PASS with verifier FAIL must leave the run in HOLD, blocking further line dispatch for that run until resolved (deploy_truth_hold semantics).
- **Receipt:** `receipts/cloud-factory-cf-p1-f-verifier-proof-<ISO8601Z>.json`.
- **Founder point:** none.

---

## 3. Phase CF-P2 — authenticated client workspace

All items PROPOSED / TO BE BUILT. Ladder steps compiled at unlock.

- **Auth:** Supabase auth on project `tkgpapowwplupyekpivy`, following the `002_trustfield_auth_profiles_v1.sql` auth_profiles migration precedent.
- **Order intake API:** Railway `/api/factory/orders` family (submit/status/list). Motor `railway_factory_intake_v0` registered before first run — requires the registry `kind` enum amendment (blocker B6). Any Control Desk surface for orders requires the contract's mandated Phase-2 "explicit refactor doc" plus new route registration in `data/noos_control_desk_api_contract_v1.json` (the 10 canonical routes contain no intake surface today).
- **Identity binding:** every non-founder order carries `auth_ref` → Supabase auth user id; actor kinds `founder | client | api_client | studio_ide`. Client authority never exceeds their own run scope; client approval gates only their run's preview→deliver step; founder approval gates anything touching production, spend, sends, legal.
- **Artifact visibility:** client sees ONLY their run's artifacts — asset-gate discipline (L7 Asset Gate precedent: probe-based audits, anomalous-access flags).
- **Status page:** read-only order→run status view over the run lifecycle enum (RECEIVED … CLOSED + exception states).
- **Founder points:** FT-PHASE-UNLOCK CF-P2 receipt to open the phase; approval of ANY client-facing copy before it ships.

---

## 4. Phase CF-P3 — workflow builder (Mode A GA)

All items PROPOSED / TO BE BUILT.

- **Line:** FL5 (workflow_builder) GA. Flow: order → FL1/FL2 → FL5 produces a governed workflow definition (prompt registry rows `cf.*` + automation registry row drafts + GH Actions workflow YAML draft) → FL6 contract tests → FL7 preview as dry-run trace artifact → FL8 verify → client approve.
- **Activation is a SEPARATE founder-gated step** per prompt L5 line rules: founder approval to activate anything touching candidates, spend, or public copy. Client approval of the preview never activates anything.
- **Recurring automation — flagged honestly:** `recurring_copilot_automation` is a forbidden action today (`data/noos_copilot_dispatcher_v1.json`) and github_actions tool_law is "model:none" recurring automation. A client workflow that runs on a schedule therefore needs BOTH a new authority grant (PROPOSED amendment, founder-ratified) AND `FOUNDER-UNLOCK-CF-CRON`. Until then Mode A delivers dispatch/event-triggered definitions only.
- **Schema dependency:** `cf.<line_key>.<name>` prompt ids require the PROPOSED prompt_registry schema v2 amendment (blocker B8) before any `cf.*` row can be registered.
- **Founder points:** FT-PHASE-UNLOCK CF-P3; every workflow activation touching candidates/spend/public copy; the recurring-automation authority grant itself.

---

## 5. Phase CF-P4 — no-code app builder (Mode B GA)

All items PROPOSED / TO BE BUILT.

- **Line:** FL4 (app_builder) GA. Flow: order → FL1/FL2 → FL4 builds from the governed template stack (Railway service + Supabase schema + CF Pages/Worker front) → FL6 tests → FL7 preview URL → FL8 verify → client approves preview.
- **Preview only:** FL7 produces PR + artifact + preview URL. Production deploy is NOT part of the substrate — it stays FOUNDER_ONLY via existing paths (HARD_BLOCK reason 2), in every phase including this one.
- **Cloudflare law note:** tool_law currently defers Cloudflare to Phase 3/4 control plane; CF Pages/Worker front templates beyond the existing verifier read/verify path require that law advanced or amended — flagged as a PROPOSED amendment, not assumed.
- **Founder points:** FT-PHASE-UNLOCK CF-P4; every production deploy of a client app (outside substrate, per-deploy founder authorization).

---

## 6. Phase CF-P5 — paid client platform

All items PROPOSED. This phase cannot open on receipts alone.

- **Gates:** FT-LEGAL (client contracts, terms of service, jurisdiction review) AND FT-CAPITAL (payment rails, pricing, spend caps) founder receipts, in addition to FT-PHASE-UNLOCK CF-P5.
- **Guardrails law (LOCKED):** no payment, custody, settlement, MSB, PSP, or banking capability claims until legally established (`ssot/sg-guardrails-trustfield-v1.md` / `ssot/sg-guardrails-signal-factory-v1.md`). All external claims ride the claim ladder VERIFIED / DECLARED / PLANNED — no class upgrades without evidence. `no_legal_financial_commitment` gate + deliverable-text lint (spec'd in CF-P1) enforce this on every client deliverable.
- **Founder points:** FT-LEGAL, FT-CAPITAL, and all client-facing paid-offer copy.

---

## 7. Per-phase exit criteria (receipt streaks)

| Phase | Exit criteria (ALL required) | Unlock to next |
|---|---|---|
| CF-P1 | ≥3 FR runs with FL8 external PASS (secondary CF account edge receipt) · zero W1–W9 wall violations across all runs · every run cost under caps (≤2.00/line, ≤5.00/run) · complete receipt chain per run (line → run → scorecard) · all six CF-P1-A..F step receipts exist | FT-PHASE-UNLOCK CF-P2 founder receipt |
| CF-P2 | ≥3 client_workspace orders end-to-end under founder-controlled test identities · zero cross-client artifact-visibility events · 3× asset-gate audit PASS · 100% non-founder orders carry auth_ref | FT-PHASE-UNLOCK CF-P3 founder receipt |
| CF-P3 | ≥3 Mode A workflow definitions delivered with FL8 PASS · zero activations without a founder approval receipt · 3× drift PASS on activated definitions | FT-PHASE-UNLOCK CF-P4 founder receipt |
| CF-P4 | ≥3 Mode B apps with preview URLs and FL8 PASS · zero production deploys originating from the substrate · 3× verifier PASS streak on template stack | FT-PHASE-UNLOCK CF-P5 + FT-LEGAL + FT-CAPITAL founder receipts |
| CF-P5 | steady state — FT-PHASE-UNLOCK retires only per L8 expansion_rules (N=8 promote-class receipt streak); FT-L5-IRREVERSIBLE never retires | — |

---

## 8. KNOWN BLOCKERS (honest, current as of 2026-07-09)

| # | Blocker | Impact | Resolution path |
|---|---|---|---|
| B1 | L8 Founder Approval Queue endpoints NOT BUILT (`GET/POST /api/ops/approvals`, ladder step D of `docs/ACTIVATION_LADDER_v1.md`) | No live founder-decision surface for AWAITING_APPROVAL | Interim: `receipts/factory/approval_queue_v0.json` + QUEUED_FOUNDER_REVIEW state; build step D in TrustField repo |
| B2 | ANTHROPIC_API_KEY not wired in GH Actions secrets | All `claude_cloud_agent` lines dormant; runs degrade to secondary targets | Founder wires the secret (activation dependency, not a design assumption) |
| B3 | Dispatcher full PASS not earned (`pre_pass_gate: full_PASS_not_yet_earned`) | Substrate cloud writes limited to pre-PASS scope: receipts, status, drift reports, draft-branch/PR-prep | Resolve `trustfield_copilot_cloud_agent` 7F-B evidence; until then run inside pre-PASS modes |
| B4 | R3 cron locked (`ladder_r3: HOLD — cron disabled`); no scheduled automation | No VERIFIED status reachable; dispatch-only operation | `FOUNDER-UNLOCK-CF-CRON` founder receipt |
| B5 | Control Desk has no order route (10 canonical routes only); Phase-2 changes require an explicit refactor doc | No cockpit order intake | Write the refactor doc + route registration as CF-P2 work |
| B6 | Railway and Supabase are not motor `kind`s in `data/github_automation_registry_v1.json` | `railway_factory_intake_v0` cannot be registered lawfully | Registry kind-enum amendment (founder-ratified) when built |
| B7 | No R2/S3 artifact bucket | Large build artifacts have no durable store | Interim: GH Actions upload-artifact (90-day) + CF KV RECEIPTS mirror; R2 bucket flagged for CF-P2+ |
| B8 | prompt_id pattern `^(tb|pa|ops)\.` excludes `cf.*` | No substrate prompt can be registered | PROPOSED prompt_registry schema v2 amendment, founder-ratified |
| B9 | `data/p0_core_invocation_scope_v1.json` status shows conflicting readings (ACTIVE vs PROPOSED) | Command-brain invocation scope may not yet be law | Verify status + record a reconciliation receipt before relying on it |
| B10 | Repo-fences stack (`policy/repo_fences_v1.yaml`, `.github/workflows/repo-fences-v1.yml`, `.github/CODEOWNERS`) exists only as staged, UNCOMMITTED working-tree files — never merged, never run in CI | CF-P1-A's verification depends on a fence stack that is not yet merged law; "no direct main writes" is convention until it lands | Land the fence stack on main (founder-visible commit + PR) before or within the CF-P1-A ratification PR |

---

## 9. NEXT — first packet candidates (CF-P1 step 1 work orders)

Compile via the existing p0pgr compiler path (`p0_prompt_packet_v1.1`, packet_id assigned as `PKT-NNNN` at compile time, all nine gates, R1–R9 lint). Labels: `FACTORY_RUN` deferred until runs exist; these are build packets.

1. **Ratify cloud-factory package (CF-P1-A).** Mission: land the three synchronized fence edits (`policy/repo_fences_v1.yaml`, CODEOWNERS-coverage step in `.github/workflows/repo-fences-v1.yml`, `.github/CODEOWNERS`) + `data/founder_canon_v1.json` pointer rows via one PR carrying work_order_id + receipt refs. Route: CLOUD_WORKER. Acceptance: fences checker PASS, negative tests green, ratification receipt written. Founder point: work_order signature + merge.
2. **Build sandbox manager v0 (CF-P1-B).** Mission: allocator per `SANDBOX_MANAGER_SPEC_v0.md`, `receipts/factory/sandbox_ledger_v0.json` ledger with CAS, `scripts/check_sandbox_walls_v0.py`, W1–W9 negative-test battery. Route: CLOUD_WORKER. Acceptance: allocate/release cycle proven, REJECTED receipt on second writer, all nine wall negative tests fire.
3. **Build order→packet compiler glue (CF-P1-C).** Mission: `receipts/factory/orders/` intake convention, classification output, `client_order_to_factory_run_v0` envelope wiring around the existing compiler + lint, soup-wall gate on assembled worker prompts. Route: CLOUD_WORKER. Acceptance: ORD-0001 dummy compiles lint-clean, seeded lint-fail files a repair candidate and the lane continues.
