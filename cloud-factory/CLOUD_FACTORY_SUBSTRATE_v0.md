# CLOUD FACTORY SUBSTRATE v0 — PACKAGE AUTHORITY

**Version:** 0.1.0 · **Status:** PROPOSED (design-only, nothing in this package is built or active)
**Era:** `PHASE_2_CLOUD_ONLY_ROI_TRACK`
**Authority chain:** FOUNDER_CANON v1 → P0-PGR runtime v1.1 (command brain) → this package (execution substrate)
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
**canon_version:** `founder_canon_v1.0.0`
**Founder authorization:** receipt `founder-order-cloud-factory-substrate-20260709T011955Z` (`receipts/p0pgr/founder/`) — design-only unlock. Building, activating, and deploying are NOT unlocked by this receipt.
**Ratification path:** RF1/RF2/RF3 fence rules forbid self-promotion to ACTIVE. This package moves to ACTIVE only via founder work_order + receipt.

## Package file map

| File (all in `cloud-factory/`) | Role |
|---|---|
| `CLOUD_FACTORY_SUBSTRATE_v0.md` | This document — package authority, layer architecture, safety doctrine |
| `FACTORY_LINE_REGISTRY_v0.json` | Machine registry of factory lines FL1–FL10 (schema `factory_line_registry_v0`) |
| `SANDBOX_MANAGER_SPEC_v0.md` | Sandbox allocation, walls, secrets, timeouts, cost caps, cleanup |
| `CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json` | Order → factory-run envelope schema (schema `client_order_to_factory_run_v0`) |
| `MVP_ACTIVATION_PLAN_v0.md` | Phases CF-P1 → CF-P5, per-phase ladder steps, known blockers |

---

## §1 Mission & position

**What the substrate is.** The execution substrate under the P0-PGR command brain. P0-PGR compiles, lints, gates, and routes prompt packets (`p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`, ACTIVE); the substrate is the factory floor those packets land on: ten venture-generic build lines (FL1–FL10) executing in isolated cloud sandboxes, producing preview artifacts, verified adversarially, receipted end-to-end. The brain decides; the substrate builds.

**What the substrate is NOT.**
- **Not a new brain.** Routing, gating, ROI ranking, and judgment stay in P0-PGR. The substrate never re-implements the queue (integration law, census F3: consume adjacent live systems as inputs, never duplicate their queues).
- **Not a schema mutation.** No P0-PGR schema, gate, or route enum changes in v0 (`no_authority_change` gate; FT-L5-IRREVERSIBLE forbids casual schema/gate mutation). See §4 wrap-by-reference.
- **Not production deploy machinery.** FL7 is preview-only. Production deploy is absent from the substrate in v0 and stays FOUNDER_ONLY via existing paths (HARD_BLOCK reason 2).

**Relationship to existing registries.**
- **TrustField cloud lines L1–L8** (`data/cloud_line_registry_v1.json`, authority `docs/CLOUD_FACTORY_PROMOTION_PLAN_TRUSTFIELD_v1.md`) stay untouched. They are venture OPERATIONS loops for one venture (health, intake, sourcing, evaluation, prompt registry, deploy truth, asset gate, approval queue) — not build stages. Their file is sha256-pinned in receipt `receipts/p0pgr/CLOUD_FACTORY_PROMOTION_PLAN_TRUSTFIELD_v1-20260708T234714Z.json`; in-place edits would invalidate a founder-receipted package.
- **Factory lines FL1–FL10** are venture-generic BUILD lines in a NEW registry, `cloud-factory/FACTORY_LINE_REGISTRY_v0.json`, cloning the proven line record shape from `cloud_line_registry_v1` and adding substrate fields (§5).
- **Three L-namespaces disambiguation.** "L1–L8" already means three different things in this repo: machine autonomy loops L1–L8 (`data/machine_autonomy_loops_v1.json`), TrustField cloud lines L1–L8 (`data/cloud_line_registry_v1.json`), and governance laws (PARALLEL_AUTOMATION L1–L5, governed-autorun L1–L13, deterministic core D1–D8). Factory lines therefore carry the mandatory `FL` prefix. Any bare "L-number" in substrate text is a defect.

---

## §2 Layer architecture

Eight layers. For each: what it does · what exists today · what is net-new · which package file specs it.

### Layer 1 — Order intake
- **Does:** accepts founder/client orders, assigns `ORD-NNNN(-slug)`, binds actor identity.
- **Exists today:** nothing. The Control Desk API contract (`data/noos_control_desk_api_contract_v1.json`) has 10 canonical routes and no order route; no network intake exists anywhere.
- **Net-new:** order file convention `receipts/factory/orders/<ORD-ID>.json`, channel/actor enums, identity binding rules (§3). TO BE BUILT.
- **Spec:** §3 + `CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`.

### Layer 2 — P0-PGR integration
- **Does:** classifies each order, compiles it into a standard packet via the existing compiler path, wraps the packet by reference in a factory-run envelope.
- **Exists today:** the full P0-PGR runtime — packet schema `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json`, linter `scripts/p0pgr_packet_lint_v1.py` (R1–R9), cycle runner `scripts/p0pgr_cycle_v1.py`, ROI ranker `scripts/p0pgr_phase2_rank_v1.py`, outbox `receipts/p0pgr/outbox/`.
- **Net-new:** classification output, envelope wrap, `FACTORY_RUN` labeling. No compiler script exists today (compilation is operator/skill work) — the order→packet compiler is TO BE BUILT.
- **Spec:** §4 + `CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`.

### Layer 3 — Factory line registry
- **Does:** machine-readable truth for FL1–FL10: owner roles, triggers, targets, receipts, timeouts, autonomy states.
- **Exists today:** the record-shape precedent (`data/cloud_line_registry_v1.json`) and the registry-is-authority precedent ("Registry wins", `docs/TRUSTFIELD_CLOUD_LOOPS_IMPLEMENTATION_PACKETS_v1.md`).
- **Net-new:** the registry file itself and every FL row. NOT BUILT.
- **Spec:** `FACTORY_LINE_REGISTRY_v0.json` + §5.

### Layer 4 — Sandbox manager
- **Does:** allocates one isolated worktree + branch per factory run, enforces walls at exit, manages secrets/timeouts/cost caps/cleanup, keeps a ledger.
- **Exists today:** a single-path precedent only — TrustField `scripts/bridge_loops_intake_www_upgrade_v1.py` `ensure_worktree_sandbox()` (fixed detached worktree, no per-order allocation, no ledger, no cleanup); branch-prefix precedent `sandbox/brain/` in `data/brain_domain_sandboxes_v1.json`.
- **Net-new:** ledger `receipts/factory/sandbox_ledger_v0.json` (schema `sandbox_ledger_v0`, one writer per task cell, second writer → REJECTED receipt, CAS per PARALLEL_AUTOMATION L1), allocation `git worktree add .worktrees/factory/<sandbox_id> -b sandbox/factory/<fr-id>`, `sandbox_id` = `sbx-fr-NNNN-SS`, wall check `scripts/check_sandbox_walls_v0.py` (TO BE BUILT in CF-P1).
- **Spec:** `SANDBOX_MANAGER_SPEC_v0.md`.

### Layer 5 — Execution targets
- **Does:** binds each line to primary/secondary cloud runners.
- **Exists today:** GH Actions fleet, the SG verifier worker on the secondary CF account, Railway/Supabase serving TrustField ops (§6 matrix).
- **Net-new:** nothing in v0 — "use existing stack first" doctrine. `container_runner` is FUTURE.
- **Spec:** §6.

### Layer 6 — Client product modes
- **Does:** three deliverable shapes — Mode 0 `factory_task` (internal founder/governance deliverable, no client surface), Mode A `workflow_builder`, Mode B `app_builder`.
- **Exists today:** nothing client-facing; asset-gate discipline precedent (TrustField L7 Asset Gate).
- **Net-new:** both modes. PROPOSED.
- **Spec:** §7.

### Layer 7 — Safety gates
- **Does:** maps every order-level safety guarantee to a structural mechanism.
- **Exists today:** the nine P0-PGR gates, guardrails `ssot/sg-guardrails-*.md`, soup-wall gate `scripts/verify_p0_core_output_soup_wall_gate_v1.py`. The repo-fences stack (`policy/repo_fences_v1.yaml` + `.github/workflows/repo-fences-v1.yml` + `.github/CODEOWNERS`) exists as staged, UNCOMMITTED working-tree files — not yet merged law (MVP blocker B10).
- **Net-new:** sandbox walls W1–W9 as mechanical exit checks, deliverable-text lint, interim approval queue file `receipts/factory/approval_queue_v0.json`. TO BE BUILT.
- **Spec:** §8 + `SANDBOX_MANAGER_SPEC_v0.md`.

### Layer 8 — MVP plan
- **Does:** phases CF-P1 → CF-P5 under activation-ladder step discipline (Preconditions → Artifacts → Verification → Receipt → Founder point; a step is DONE only when its receipt exists).
- **Exists today:** the ladder doctrine (`docs/ACTIVATION_LADDER_v1.md`) and L8 earned-autonomy expansion_rules (`data/machine_autonomy_loops_v1.json`).
- **Net-new:** all five phases. PROPOSED.
- **Spec:** `MVP_ACTIVATION_PLAN_v0.md`.

### End-to-end walkthrough (worked example, Mode A)

Run lifecycle enum (`client_order_to_factory_run_v0`):
`RECEIVED → CLASSIFIED → PACKET_COMPILED → QUEUED → SANDBOX_ALLOCATED → RUNNING → PREVIEW_READY → VERIFYING → AWAITING_APPROVAL → APPROVED → RECEIPTED → HARVESTED → CLOSED`
Exception states: `REPAIR_CANDIDATE`, `HOLD_CLOUD_UNSAFE`, `QUEUED_FOUNDER_REVIEW`, `BLOCKED_WITH_REASON`, `KILLED`. Line verdicts: `PASS | PARTIAL | FAIL | BLOCKED_WITH_REASON | SKIPPED`.

Example: founder order "client wants a lead-intake workflow" (channel = `founder_session`; illustrative full Mode A flow — FL5 runs unlock at CF-P3, since CF-P1's minimum line set excludes FL4/FL5 per `MVP_ACTIVATION_PLAN_v0.md` §2).

1. **Order.** Founder drops `receipts/factory/orders/ORD-0001-lead-intake-workflow.json` + a founder authorization receipt in `receipts/p0pgr/founder/`. Run status `RECEIVED`.
2. **Classification.** Output: intent, `product_mode: workflow_builder` (Mode A), venture, `line_plan: [FL1, FL2, FL5, FL6, FL7, FL8, FL9, FL10]`, `risk_flags: []`, `hold_labels: []`. Status `CLASSIFIED`.
3. **Packet.** Compiled into a standard `p0_prompt_packet_v1.1` packet (e.g. `PKT-0201-lead-intake-workflow`): all nine gates, five-axis ROI 0–5, route from the EXISTING enum (`CLOUD_WORKER`), labels `FACTORY_RUN` + `FL-plan:FL1,FL2,FL5,FL6,FL7,FL8,FL9,FL10`. Lint R1–R9 runs unchanged; a lint fail files a repair candidate and the lane continues (continuity law). Status `PACKET_COMPILED`.
4. **Queue.** ROI ranked by `scripts/p0pgr_phase2_rank_v1.py` (weights 35/25/15/15/10) into `receipts/p0pgr/phase2_queue_v1.json`; the substrate pulls `next_move`, never a private queue. Status `QUEUED`.
5. **Envelope.** `FR-0001-lead-intake-workflow` wraps the packet by reference: `packet_ref {packet_id, packet_path}`. Line plan and sandbox spec live in the envelope, not the packet.
6. **Sandbox.** Ledger row allocated: `sandbox_id sbx-fr-0001-01`, worktree `.worktrees/factory/sbx-fr-0001-01`, branch `sandbox/factory/fr-0001-lead-intake-workflow`, `env_profile: none`, per-line timeouts, cost caps (line 2.00 / run 5.00 USD default). Status `SANDBOX_ALLOCATED`.
7. **FL1 → FL2.** Research digest, then architecture plan. Each line's worker prompt is assembled from the packet through the soup wall — the seven allowed task-spec keys only. Each line writes `receipts/factory/FR-0001-lead-intake-workflow/<line_key>-<ISO8601Z>.json`. Status `RUNNING`.
8. **FL5.** Produces the governed workflow definition: `cf.*` prompt registry row drafts + automation registry row drafts + GH Actions workflow YAML draft. All DRAFT artifacts — nothing activates.
9. **FL6.** Contract tests in GH Actions; failure degrades per continuity law (tag confidence → reduce scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue), never STOP.
10. **FL7.** Preview only: PR from `sandbox/factory/fr-0001-lead-intake-workflow` + GH Actions artifact + dry-run trace. Status `PREVIEW_READY`.
11. **FL8.** Adversarial verify. PASS only from the secondary CF account edge receipt (account `b7282b4a5c17b84d62e3ef8866b878f8`, worker `sina-governance-ssot-advisory`) — never builder self-report. Any FL8 FAIL writes a HOLD row (reusing `deploy_truth_hold` semantics) that blocks further line dispatch for this run. Status `VERIFYING`.
12. **Approval.** Status `AWAITING_APPROVAL`. Until ladder step D is built the founder approves via the interim `receipts/factory/approval_queue_v0.json` (L8 Founder Approval Queue endpoints are ladder step D, NOT BUILT). Activation of the produced workflow is a SEPARATE founder-gated step. Status `APPROVED`.
13. **FL9.** Run receipt `receipts/factory/FR-0001-lead-intake-workflow-run-<ISO8601Z>.json`: all nine `gates_checked`, `quality_state`, evidence with sha256, cost roll-up → `receipts/p0pgr/phase2_scorecard_v1.json` `counters.cost_usd`. Status `RECEIPTED`.
14. **FL10.** Harvest: reusable-pattern candidate rows drafted for `data/governance_library_promote_queue_v1.json` as artifacts under `receipts/factory/artifacts/<FR-ID>/`, delivered as branch + PR through full repo fences — never a direct `data/` write; verifier/drift PASS streaks recorded for L8 earned-autonomy expansion. Status `HARVESTED` → `CLOSED`. Cleanup only after receipt + artifacts + hash recorded; branch retained ≥30 days, then archived as tag `factory-archive/fr-0001-lead-intake-workflow`. Receipts and artifacts are NEVER deleted.

---

## §3 Order intake layer

Channels enum: `founder_session`, `founder_control_desk`, `client_workspace`, `api`, `studio_ide`.

| Channel | Today | Phase |
|---|---|---|
| `founder_session` | Only channel live in CF-P1: order file at `receipts/factory/orders/<ORD-ID>.json` + founder authorization receipt + manual `workflow_dispatch`. Convention itself is NOT BUILT. | CF-P1 |
| `founder_control_desk` | NO order route exists. The Control Desk contract defines exactly 10 canonical Phase-1 routes (observe/attest/validate/sync/receipt/PR-prep only); adding `POST /api/orders/submit` requires the contract's mandated Phase-2 "explicit refactor doc". | CF-P2 |
| `client_workspace` | No network intake exists. Arrives via Railway API + Supabase auth, reusing the TrustField `auth_profiles` migration precedent. | CF-P2 |
| `api` | Same substrate as `client_workspace`; token-bound `api_client` actors. | CF-P2 |
| `studio_ide` | Repo `noetfield-studio-ide` exists; no intake wiring. Arrives via the same Railway API + Supabase auth substrate as `api`, token-bound `studio_ide` actors. | CF-P2+ |

**Identity binding rules.**
- Actor kinds enum: `founder`, `client`, `api_client`, `studio_ide`.
- Non-founder channels require identity binding: `auth_ref` → Supabase auth user id. Unbound non-founder order → `BLOCKED_WITH_REASON`.
- Client authority NEVER exceeds their own run scope: a client sees only their run's artifacts (asset-gate discipline, L7 Asset Gate precedent).
- Client approval gates their run's preview→deliver step. Founder approval gates anything touching production, spend, sends, or legal — always.

---

## §4 P0-PGR integration — the key design decision

**Wrap by reference, mutate nothing.** The substrate does NOT modify P0-PGR schemas in v0 (`no_authority_change` gate; FT-L5-IRREVERSIBLE forbids casual schema/gate mutation).

- Every order is classified then compiled into a standard `p0_prompt_packet_v1.1` packet by the existing compiler path: `packet_id` `PKT-NNNN`, all nine gates, five-axis ROI 0–5, route from the EXISTING enum: `CLOUD_WORKER | CLOUD_RESEARCH | SESSION_EMBEDDED | REVIEW_QUEUE`.
- The factory-run envelope (`client_order_to_factory_run_v0`) WRAPS the packet by reference: `packet_ref {packet_id, packet_path}`. Factory metadata (line_plan, sandbox spec) lives in the envelope, NOT inside the packet. The packet gets label `FACTORY_RUN` + label `FL-plan:<FL ids>`.
- A dedicated route value `CLOUD_FACTORY` is listed as a PROPOSED v1.2 router amendment only (founder-gated; requires synchronized edits to `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json`, `scripts/p0pgr_packet_lint_v1.py` ALLOWED_ROUTES, and `p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md`). It is not assumed anywhere in this package.

**Classification output:** `intent`, `product_mode`, `venture`, `line_plan[]` (ordered FL ids), `risk_flags[]`, `hold_labels[]`.

**ROI scoring:** existing weights 35/25/15/15/10 (revenue / trust / workload_relief / cloud_now / reversibility) via `scripts/p0pgr_phase2_rank_v1.py`. The substrate consumes `phase2_queue_v1.json` `next_move`; it never ranks privately.

**Lint:** existing R1–R9 packet lint applies unchanged. Lint fail → repair candidate in `receipts/p0pgr/repair_candidates/`, lane continues — never STOP on lint.

**Least-knowledge / soup wall:** worker prompts assembled from a packet carry ONLY the seven allowed task-spec keys — `goal, files, constraints, done_criteria, verify_method, receipts_required, decision_verdict`. P0 CORE judgment text never enters factory worker prompts (`scripts/verify_p0_core_output_soup_wall_gate_v1.py` is the gate precedent). Note: `data/p0_core_invocation_scope_v1.json` status shows conflicting readings (ACTIVE vs PROPOSED) — verify before relying on it (blocker listed in `MVP_ACTIVATION_PLAN_v0.md`).

---

## §5 Factory lines FL1–FL10

| line_id | line_key | name | owner_role | primary target | secondary target |
|---|---|---|---|---|---|
| FL1 | research | Research Line | research_agent | claude_cloud_agent | github_actions_runner |
| FL2 | architecture | Architecture Line | architect | claude_cloud_agent | session_embedded |
| FL3 | code | Code Line | factory_worker | claude_cloud_agent | github_actions_runner |
| FL4 | app_builder | No-Code App Builder Line | app_builder_agent | claude_cloud_agent | railway_api |
| FL5 | workflow_builder | Workflow Builder Line | workflow_builder_agent | claude_cloud_agent | github_actions_runner |
| FL6 | test | Test Line | verifier | github_actions | repo_worktree |
| FL7 | deploy_preview | Deploy-Preview Line | verifier | github_actions | cloudflare_worker |
| FL8 | verifier | Verifier Line | verifier | cloudflare_worker (secondary CF account) | github_actions |
| FL9 | receipt | Receipt Line | receipt_engine | github_actions | supabase |
| FL10 | harvest | Harvest Line | harvest_agent | claude_cloud_agent | session_embedded |

**Rules for all lines.** Trigger: `dispatch`, `event`, or `event+dispatch` ONLY in v0 — no cron (scorecard directive: no scheduled automation without explicit founder approval; R3 cron remains locked). Every line writes a receipt (no receipt sink = no line; governed-autorun L8/L11). `autonomy_state: assist_only` on every line at entry. `model_tier` enum `determine|fast|standard|judgment`; `cost_class` enum `zero|cents|dollars`. Timeouts (seconds): FL1 900, FL2 1800, FL3 3600, FL4 3600, FL5 1800, FL6 1800, FL7 900, FL8 900, FL9 300, FL10 900. `failure_behavior` follows the continuity-law degrade order; `BLOCKED_WITH_REASON` only citing a HARD_BLOCK reason. Machine-readable rows: `FACTORY_LINE_REGISTRY_v0.json`.

- **FL1 research.** Consumes the run's soup-walled task spec; produces a research digest artifact (per-URL status + sha256, CLOUD_RESEARCH evidence discipline). Receipt: `research-<ISO8601Z>.json` under the run's receipt dir. Key rule: read-only; every external claim carries an artifact.
- **FL2 architecture.** Consumes FL1 digest; produces the build plan (file map, contracts, line-plan confirmation) as a DRAFT artifact. Receipt per line convention. Key rule: plans propose, never activate.
- **FL3 code.** Consumes FL2 plan; produces code inside the allocated worktree only. Receipt records diff stats + artifact hashes. Key rule: writes confined to `allowed_scope[]`; wall W9 (out-of-scope files) fires at exit.
- **FL4 app_builder.** Mode B line. Consumes FL2 plan; produces an app from the governed template stack (Railway service + Supabase schema + CF Pages/Worker front) as sandbox artifacts. Key rule: no service is provisioned in v0 without its own founder point — output is buildable artifacts, not live infrastructure.
- **FL5 workflow_builder.** Mode A line. Consumes FL2 plan; produces a governed workflow definition: `cf.*` prompt registry row drafts + automation registry row drafts + GH Actions workflow YAML draft. Key rule: everything DRAFT; activation is a separate founder-gated step (prompt L5 line rules).
- **FL6 test.** Consumes FL3/FL4/FL5 outputs; produces contract-test results in GH Actions. Receipt records pass/fail matrix. Key rule: test failure degrades (PARTIAL), never silently passes.
- **FL7 deploy_preview.** Consumes tested artifacts; produces PREVIEW ONLY — PR + GH Actions artifact + optional preview URL. Key rule: production deploy is NOT part of the substrate in v0; it stays FOUNDER_ONLY via existing paths (HARD_BLOCK reason 2).
- **FL8 verifier.** Consumes the preview; produces an independent verification verdict. `pass_rule`: PASS only from the secondary CF account edge receipt (account `b7282b4a5c17b84d62e3ef8866b878f8`, worker `sina-governance-ssot-advisory`) — never builder self-report (autonomy loop L3 law). FAIL or deploy-truth drift → HOLD row blocking further line dispatch for the run; production-facing hold resolution is a founder point.
- **FL9 receipt.** The receipt engine. Produces line receipts (`factory_line_receipt_v0`) and the run receipt (`factory_run_receipt_v0`) with all nine `gates_checked`, `quality_state`, evidence (sha256), cost roll-up: line receipt → run receipt → phase2 scorecard `counters.cost_usd`. Key rule: a run cannot reach CLOSED without a complete receipt chain.
- **FL10 harvest.** Consumes the closed run; produces harvest-entry DRAFTS for `data/governance_library_promote_queue_v1.json` (never a duplicate queue; drafts land as run artifacts and reach `data/` only via branch + PR through full repo fences) and earned-autonomy streak records (verifier PASS / drift PASS counts toward L8 expansion_rules; `receipts/earned-autonomy-expansion-*.json`). Key rule: harvest proposes promotions; it never promotes.

---

## §6 Execution targets

Doctrine: **use existing stack first.** No new runtime kind is introduced in v0.

| Target | Substrate role | Current reality (v0, honest) |
|---|---|---|
| `github_actions` | FL6/FL7/FL9 primary; FL8 secondary | TrustField: 19 live workflows; SG: `brain-loop-autorun-v1.yml` live; `repo-fences-v1.yml` + CODEOWNERS + `policy/repo_fences_v1.yaml` exist as staged, UNCOMMITTED working-tree files — not yet merged law (MVP blocker B10). Dispatch/event only for substrate — no cron. |
| `github_actions_runner` | FL1/FL3/FL5 secondary | Same runners; fallback execution path when `claude_cloud_agent` is dormant. |
| `claude_cloud_agent` | FL1–FL5 primary, FL10 primary | DORMANT: `ANTHROPIC_API_KEY` is NOT wired in GH Actions secrets today. These lines cannot run until the founder wires it — an activation dependency, not a design assumption. |
| `cloudflare_worker` | FL8 primary (secondary CF account), FL7 secondary | CF tool_law (`data/noos_control_desk_builder_roles_v1.json`) defers Cloudflare to Phase 3/4 control plane. v0 uses ONLY the existing verifier worker read/verify path (`sina-governance-ssot-advisory`, KV `RECEIPTS` id `cf97659f15f14d06be4400caad4823c2`) — no new CF control plane. |
| `railway_api` | FL4 secondary | Live for TrustField ops, but Railway is NOT a motor `kind` in `data/github_automation_registry_v1.json` — flag as registry amendment when built (§10). |
| `supabase` | FL9 secondary | Live as backing storage (project `tkgpapowwplupyekpivy`); not a motor kind — same registry amendment. |
| `repo_worktree` | FL6 secondary | Worktree precedent exists (`ensure_worktree_sandbox()`); per-run allocation is TO BE BUILT (Layer 4). |
| `session_embedded` | FL2/FL10 secondary | Live route; INCIDENT-039 rail applies (max one light shell ≤90s per turn, `accounting_note` required). |
| `container_runner` | none | Status FUTURE — not available in v0. Listed only so the enum is stable. |

---

## §7 Client product modes

- **Mode 0 `factory_task`.** Internal founder/governance build deliverable with no client surface — the only mode exercised in CF-P1 (e.g. the FR-0001 internal governance deliverable in `MVP_ACTIVATION_PLAN_v0.md`). Full line discipline applies; no client approval row exists because there is no client.
- **Mode A `workflow_builder`.** Order → FL1/FL2 → FL5 produces a governed workflow definition (prompt registry rows `cf.*` + factory/automation registry row drafts + GH Actions workflow YAML draft) → FL6 contract tests → FL7 preview (dry-run trace artifact) → FL8 verify → client approve → activation is a SEPARATE founder-gated step (prompt L5 line rules: founder approval to activate anything touching candidates/spend/public copy; no recurring automation without founder unlock).
- **Mode B `app_builder`.** Order → FL1/FL2 → FL4 produces an app from the governed template stack (Railway service + Supabase schema + CF Pages/Worker front) → FL6 tests → FL7 preview URL → FL8 verify → client approves the preview → production deploy remains founder-gated (CF-P4+).
- **Both modes:** the client sees ONLY their run's artifacts (asset-gate discipline, L7 Asset Gate precedent).

---

## §8 Safety gates

Order-gate → structural-mechanism mapping (binding for every package file):

| Order gate | Structural mechanism |
|---|---|
| no direct main writes | repo fences (policy/repo_fences_v1.yaml) + CODEOWNERS + sandbox/factory/* branches + W1 wall |
| preview before production | FL7 preview-only line; production deploy absent from v0 substrate; HARD_BLOCK reason 2 |
| founder/client approval before deploy | AWAITING_APPROVAL state + L8 Founder Approval Queue (approval_queue table; endpoints = ladder step D, NOT BUILT — interim: receipts/factory/approval_queue_v0.json + QUEUED_FOUNDER_REVIEW) |
| no sends without approval | no_external_send gate + env secret policy (no send credentials in sandboxes) + guardrails ssot/sg-guardrails-*.md |
| no legal/equity/payment claims | no_legal_financial_commitment gate + claim ladder VERIFIED/DECLARED/PLANNED + FT-LEGAL routing + deliverable-text lint (spec'd check, CF-P1 build item) |
| receipts required | canon receipt_required_fields + governed-autorun L5/L8 + run cannot reach CLOSED without complete receipt chain |

Note on branch fencing: `sandbox/factory/*` is NOT added to the fence-exempt draft patterns in v0 — merges to main always pass full repo fences. Adding it would be a policy/law mutation; flag as a PROPOSED amendment if wanted.

**The nine P0-PGR gates** — verbatim on every packet and receipt, all must pass, nothing executes "a little bit":
`cloud_only`, `read_only_or_reversible`, `roi_positive`, `no_deploy`, `no_external_send`, `no_legal_financial_commitment`, `no_p0_leakage`, `no_authority_change`, `founder_authorization_receipt`.

**The four founder triggers — the ONLY founder touchpoints:** `FT-CAPITAL`, `FT-LEGAL`, `FT-L5-IRREVERSIBLE`, `FT-PHASE-UNLOCK`. Everything else routes to machine loops (L4 self-repair → L6 deep research), never to the founder. Cost-cap breach → line halts, PARTIAL receipt, run → `QUEUED_FOUNDER_REVIEW` (FT-CAPITAL).

**Default question:** "How does the process solve this without Sina?" — any design element that makes the founder a runtime is a defect.

---

## §9 Autonomy & verification doctrine

**Entry state.** Every substrate motor enters at `assist_only` / `observe_only` (L8 earned-autonomy entry state). Expansion happens ONLY on receipt streaks per `expansion_rules` in `data/machine_autonomy_loops_v1.json` (e.g. `assist_only → registered_motor` needs workflow_audit_pass + no_parallel_conflict; `observe_only → autonomous_promote_candidate` needs 3× verifier PASS + 3× drift PASS + gate ALIGNED) — never on chat approval.

**DECLARED vs VERIFIED.** A line is DECLARED at merge and VERIFIED only after a 24h zero-manual window of scheduled, externally-written receipts closes green. Manual green ≠ cron green. Because v0 has no cron (R3 locked), every v0 line remains DECLARED at best; the VERIFIED window opens only after a founder cron unlock in a later phase.

**Adversarial verification (FL8).** Quality claims are self-reports until the secondary CF account edge receipt exists. FL8's `pass_rule` is the substrate-wide law: PASS only from the independent verifier path (`sina-governance-ssot-advisory`), never builder self-report. FL8 FAIL → HOLD row (deploy_truth_hold semantics) → downstream line dispatch blocked for that run.

**Receipt provenance.** Timestamps machine-generated at event time (`datetime.now(timezone.utc)`) — never typed from memory. Every artifact gets a sha256 recorded in its line receipt; external claims store per-URL status + body hash + saved body. Route deviation goes in `executor_route_note` — silent deviation reads as authority drift. Session-embedded LLM cost uses `accounting_note`. New receipts carry `commit_flag` for the next founder-visible commit. Line receipts: `receipts/factory/<FR-ID>/<line_key>-<ISO8601Z>.json` (schema `factory_line_receipt_v0`); run receipt: `receipts/factory/<FR-ID>-run-<ISO8601Z>.json` (schema `factory_run_receipt_v0`); both carry `receipt_id`, `canon_version`, `packet_id`, `run_id`, `gates_checked` (all NINE, PASS|FAIL strings), `quality_state`, `evidence[]`, `cost`, `accounting_note`, `executor_route_note`, `commit_flag`.

---

## §10 Registration & fences plan — PROPOSED follow-ups, none done

When building starts (CF-P1 unlock), the following registrations are mandatory BEFORE any motor's first run (PARALLEL_AUTOMATION L4: registry is routing truth; unregistered automation is a defect):

1. **Motor registration** — add to `data/github_automation_registry_v1.json`: `gh_actions_factory_dispatch_v0`, `cf_factory_verifier_v0`, `railway_factory_intake_v0` (each with `owns[]` / `must_not_own[]` / `task_cell_owners` entry). None are registered in this v0 design. Railway/Supabase are not yet motor `kind`s — the kind-enum extension is part of this amendment.
2. **Fence zone for `cloud-factory/`** — three synchronized edits (zone lists are duplicated across three files with no single source): `policy/repo_fences_v1.yaml` `protected_zones`, the hardcoded zone list in `.github/workflows/repo-fences-v1.yml`'s CODEOWNERS-coverage step, and `.github/CODEOWNERS` (owner `@Noetfield-Systems/sg-governance`).
3. **Artifact registry pointer** — register the five package files in `data/governance_artifact_registry_v1.json`.
4. **Canon pointer** — add substrate pointers to `data/founder_canon_v1.json` the way governance_* pointers were added; every substrate receipt carries `receipt_required_fields` `["receipt_id", "canon_version"]`.
5. **Prompt-id amendment** — factory prompt ids use `cf.<line_key>.<name>`, which requires extending the `^(tb|pa|ops)\.` pattern in `data/prompt_registry_schema_v1.json` → PROPOSED schema v2 amendment (founder-gated).
6. **Router amendment** — the `CLOUD_FACTORY` route value, PROPOSED v1.2 amendment per §4 (founder-gated).

All six are founder-ratified changes (work_order + receipt through repo fences RF_RECEIPT_REQUIRED / RF_POLICY_LAW_MUTATION). This package proposes; it does not register.

---

## NEXT — ordered packet candidates (work orders to implement CF-P1)

Each candidate compiles to a standard `p0_prompt_packet_v1.1` packet through the existing compiler path; routes from the existing enum; all nine gates apply.

1. **PKT candidate: FL9 receipt engine.** Build `factory_line_receipt_v0` / `factory_run_receipt_v0` writers + jsonschema validators. Route `CLOUD_WORKER`. Receipts precede everything (no receipt sink = no line).
2. **PKT candidate: sandbox ledger + allocator.** `receipts/factory/sandbox_ledger_v0.json` writer with CAS (one writer per task cell), worktree/branch allocation per `SANDBOX_MANAGER_SPEC_v0.md`. Route `CLOUD_WORKER`.
3. **PKT candidate: sandbox walls check.** `scripts/check_sandbox_walls_v0.py` — W1–W9 as mechanical exit checks, plus negative tests per `tests/repo_fences/run_negative_tests.py` pattern. Route `CLOUD_WORKER`.
4. **PKT candidate: order intake convention.** `receipts/factory/orders/` schema validation + classification output (intent, product_mode, venture, line_plan, risk_flags, hold_labels). Route `CLOUD_WORKER`.
5. **PKT candidate: envelope compiler.** Order → packet (via existing compiler path) → `client_order_to_factory_run_v0` envelope with `packet_ref`; soup-wall gate invoked on every worker prompt assembly. Route `CLOUD_WORKER`.
6. **PKT candidate: FL8 verifier path.** Wire the run-verify request/receipt flow through the existing secondary CF account worker (`sina-governance-ssot-advisory`) — read/verify only, no new CF control plane. Route `CLOUD_WORKER`.
7. **PKT candidate: deliverable-text lint.** Scan run deliverables for legal/equity/payment/employment claim language (claim ladder VERIFIED/DECLARED/PLANNED; FT-LEGAL routing). Route `CLOUD_WORKER`.
8. **PKT candidate: interim approval queue file.** `receipts/factory/approval_queue_v0.json` + `QUEUED_FOUNDER_REVIEW` wiring until ladder step D endpoints exist. Route `CLOUD_WORKER`.
9. **PKT candidate (founder-gated): registration bundle.** §10 items 1–4 as one work_order: motors, fence zone (three synchronized edits), artifact registry pointer, canon pointer. Route `REVIEW_QUEUE` until the founder signs the work_order.
10. **PKT candidate (founder-gated): schema amendments.** `cf.` prompt-id pattern (prompt registry schema v2) + `CLOUD_FACTORY` route (router rules v1.2, synchronized packet-schema/linter/router edits). Route `REVIEW_QUEUE` — `no_authority_change` holds until founder ratification.

STOP.
