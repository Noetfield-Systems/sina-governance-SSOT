# SANDBOX WORKTREE MANAGER v1

**Version:** 1.0.0
**Status:** PROPOSED — design only. Nothing in this file is built, active, or verified. Every new component below is TO BE BUILT unless explicitly marked as an existing precedent.
**Era:** PHASE_2_CLOUD_ONLY_ROI_TRACK
**Authority:** `plan-factory/PLAN_FACTORY_ARCHITECTURE_v1.md` (package authority). Chain: FOUNDER_CANON v1 → P0-PGR runtime v1.1 (command brain) → cloud-factory v0 (execution substrate) → this package (plan layer).
**Amends:** `cloud-factory/SANDBOX_MANAGER_SPEC_v0.md` (v0.1.0, PROPOSED).
**Amendment law:** v0 remains the base law in full — identity and allocation (v0 §2), branch naming (v0 §3), walls W1–W9 (v0 §4, `scripts/` included in W2), env profiles (v0 §5), timeouts (v0 §6), cost caps (v0 §7), cleanup (v0 §8), artifact storage (v0 §9), receipt paths and schemas (v0 §10), execution-target notes (v0 §11). This v1 ADDS; on direct conflict v1 wins — and this delta is designed so that **zero direct conflicts exist**. Nothing in v0 is restated here; v0 sections are cited by number.
**Founder authorization:** receipt `founder-order-1000-plan-cloud-factory-20260709T014708Z` (`receipts/p0pgr/founder/`) — design-only unlock; building/deploying/scheduling NOT unlocked.
**canon_version:** `founder_canon_v1.0.0`
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.

---

## 12. Execution cells and `cell_kind` (v1 addition a)

**Cell** = one allocated sandbox — exactly one ledger row in the v0 sandbox ledger (v0 §2.2). No new id namespace: a cell is keyed by its `sandbox_id` (v0 §2.1 format `sbx-fr-NNNN-SS`), allocated by the v0 algorithm (v0 §2.4), and closed by the v0 cleanup rules (v0 §8). "Cell" is vocabulary, not a new object; every rule that binds a sandbox allocation in v0 binds a cell unchanged.

`cell_kind` enum (exactly five values in v1):

| cell_kind | What it is | v0 §11 execution-target row(s) | Notes (honest state) |
|---|---|---|---|
| `worktree_cell` | Repo worktree + `sandbox/factory/<fr-id>` branch | `repo_worktree`; also `session_embedded` when repo files are touched (v0 §11 rule) | The v0 spec's direct case; walls checked at exit (v0 §4) |
| `runner_cell` | One GH Actions job as the sandbox | `github_actions`, `github_actions_runner` | `env_profile: gh_actions_scoped` (v0 §5); walls checked by job step (v0 §11) |
| `agent_cell` | One `claude_cloud_agent` session | `claude_cloud_agent` | DORMANT — `ANTHROPIC_API_KEY` not wired (v0 §5; blocker B2 inherited via `cloud-factory/MVP_ACTIVATION_PLAN_v0.md` §8); ranking model applies `blocked_target_penalty` |
| `edge_cell` | Cloudflare read/verify execution, config-scoped | `cloudflare_worker` | Read/verify path only (`sina-governance-ssot-advisory`), per CF tool_law deferral (v0 §11); no new CF control plane |
| `service_cell` | Railway/Supabase config-scoped execution at the target where secrets live | `railway_api`, `supabase` | No worktree; ledger row still required with worktree/branch fields not-applicable (v0 §11); not yet motor kinds in `data/github_automation_registry_v1.json` (registry amendment flagged in v0 §11) |

- `session_embedded` work that touches no repo files keeps its v0 §11 treatment unchanged (ledger row records the session-scoped allocation); its `cell_kind` column may be omitted — the column is OPTIONAL (§18).
- `container_runner` remains FUTURE (v0 §11); no `cell_kind` value is assigned to it in v1. No design commitments.
- Every cell kind — including config-scoped `edge_cell` / `service_cell` — still gets a ledger row, a receipt at exit (v0 §10), and the wall protocol on violation (v0 §4). No receipt sink = no cell.

---

## 13. Multi-repo cell targeting (v1 addition b)

Extends v0 §2.3 from single-repo runs to plan runs that span repos. The v0 rules stand; v1 adds the cell framing:

1. **One actor · one repo · one scope** (`ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`, already cited in v0 §2.3) now binds per cell: each cell targets exactly one repo with exactly one `allowed_scope[]`.
2. **Venture deliverables allocate cells in the venture repo** (v0 §2.3 rule 1). The plan's `sandbox_target.repo` (PLAN_SCHEMA_v1) plus the order envelope's `venture` field decide the target at classification, before allocation.
3. **SG repo cells only for governance artifacts** (v0 §2.3 rule 2): registries, SSOT mirrors, substrate policy, receipts. Never venture product code in an SG cell.
4. **Cross-repo runs = one cell per repo.** A plan whose `line_plan` produces artifacts in more than one repo allocates one cell per repo, one writer per cell (v0 §2.2 one-writer law), and the run envelope references all of its cells by `sandbox_id`. A single cell spanning two repos is a classification defect (v0 §2.3 rule 3: never both — split before allocation).
5. Venture-repo cell output exits as branch + PR only (v0 §2.3 rule 4); merge is a venture-owner/founder point. The ledger (SG, always — v0 §2.2) records every cell's target `repo` regardless of where the cell lives.

---

## 14. Concurrency law (v1 addition c)

v0 is silent on concurrent allocations beyond the one-writer CAS law (v0 §2.2). v1 sets explicit limits:

| Limit | Value (v1 default) | Enforcement point |
|---|---|---|
| Max concurrent cells per run | **3** | Allocation precondition — extends v0 §2.4 step 4: CAS-claim fails if 3 cells for this `run_id` are already ALLOCATED/RUNNING |
| Writer cells per repo | **1** at any time, across all runs (PARALLEL_AUTOMATION L1 — the v0 §2.2 one-writer law, widened from task cell to repo) | Same allocation precondition: no second writer cell may be ALLOCATED/RUNNING for the same target `repo`; second writer → REJECTED receipt (v0 §2.2), never silent overwrite |
| Read cells | Unlimited in count | Bounded only by cost caps (§15) and timeouts (v0 §6) |

- **Writer cell** = a cell whose `allowed_scope[]` permits any file mutation in its target repo. **Read cell** = a cell with no repo write scope (e.g. `read_public_web` research, `edge_cell` verify). The distinction is derivable from existing ledger fields; no new field is required.
- The concurrency check is mechanical and lives in the allocator (v0 NEXT item 1, `scripts/factory_sandbox_allocate_v0.py` — TO BE BUILT, CF-P1); v1 adds these two preconditions to its spec, not a new script.
- Queueing beyond the limits follows the continuity law degrade order (v0 §6 behavior): a blocked allocation waits in QUEUED, never defaults to STOP.

---

## 15. Plan-scoped cost caps (v1 addition d)

v0 §7 caps stand unchanged: per-line `cost_cap_usd` 2.00 default, per-run 5.00 default, breach → line halt + PARTIAL receipt + QUEUED_FOUNDER_REVIEW + FT-CAPITAL. v1 adds the plan dimension:

1. **The plan's `cost_cap_usd`** (PLAN_SCHEMA_v1; default 5.00, per-line 2.00 inherited from v0) **distributes over the run's cells**: effective per-cell cap = min(line `cost_cap_usd`, remaining plan budget for this run). The ledger row records the effective cap (v0 §7).
2. An order budget may LOWER a cap, never raise it above the plan cap without founder approval (CLIENT_ORDER_TO_PLAN_PIPELINE_v1 stage 3 rule).
3. **Cell overrun** = the v0 §7 breach path verbatim (line halt, PARTIAL receipt with `limitations[]`, run → QUEUED_FOUNDER_REVIEW, FT-CAPITAL) — **plus a plan-level rollup**: cell/line receipt `cost` → run receipt `cost` (v0 §7 rollup chain) → plan-level accumulation keyed by `plan_id`, feeding `reuse_bonus`, `cost_efficiency_bonus`, and the "cost under cap in all runs" clause of the `auto_dispatch_gate` in `plan-factory/PLAN_RANKING_ROI_MODEL_v1.json`. An overrun run is disqualifying evidence for that plan's auto-dispatch eligibility (`auto_dispatch.eligible` is const false in v1 regardless).
4. Plans reuse v0 receipt schemas unchanged (`factory_line_receipt_v0` + `factory_run_receipt_v0`); a plan may ADD a `plan_receipt_note` but never removes fields (PLAN_SCHEMA_v1 receipt rule). Metered honesty per v0 §7 (governed-autorun L11): no typed cost figures anywhere in the rollup.

---

## 16. `automation_cron` cells — double lock (v1 addition e)

Cells serving plan band 10 (`automation_cron`, PLAN-0901–1000) carry a hard ceiling:

- **May:** compile workflow definitions (GH Actions YAML drafts, prompt-registry row drafts), validate them, and produce **dry-run traces** as preview artifacts (the FL7 dry-run trace precedent, v0 substrate Mode A).
- **May NEVER install a schedule.** No `cron:` trigger added to any installed workflow, no enabling of a scheduled workflow, no crontab or scheduled-task/scheduled-agent creation, no Cloudflare cron trigger. `recurring_copilot_automation` is forbidden today. This is a **W7-adjacent wall**: the v0 §4 exit gate's W7 command-log scan extends to schedule-install verbs, with the same violation protocol (contain + receipt + BLOCKED_WITH_REASON) — an extension of the W7 check, not a new wall id.

Activation of any schedule is **double-locked**; both locks are founder receipts and neither alone suffices:

| Lock | Scope | Class |
|---|---|---|
| 1. `FOUNDER-UNLOCK-CF-CRON` | Phase-level: cron capability for the factory as such | FT-PHASE-UNLOCK founder receipt (NOT ISSUED — R3 cron remains locked, v0 §8.4) |
| 2. Per-workflow founder activation | One named workflow definition, one receipt | Founder activation receipt naming the specific workflow (never class-wide) |

Even with both locks present, schedule installation happens on a founder-activated path outside the cell — a cell's ceiling stays build + dry-run permanently. This makes "no scheduled automation without explicit founder approval" (v0 line rules; scorecard directive) structural rather than conventional.

---

## 17. Control-surface bindings (v1 addition f)

Two control surfaces bind to the cell model — both **TO BE BUILT, CF-P2+**; neither exists as wiring today:

| Surface | What exists today | v1 binding (designed, NOT BUILT) |
|---|---|---|
| **Studio IDE** | Repo `noetfield-studio-ide` exists; no wiring | Read-only cell/run views + order/dispatch submit |
| **Forge Terminal** | Founder/operator session + manual `workflow_dispatch` (the interim reality) | Named terminal surface: read-only cell/run views + dispatch submit |

Binding law (Control Desk precedent: frontend displays, backend computes):

1. Surfaces **DISPLAY and SUBMIT only.** They render ledger rows, cell status, run envelopes, and receipts; they file dispatch/order submissions into the existing intake path.
2. Surfaces **never mutate ledger rows directly** and never compute verdicts, gate results, wall outcomes, or status transitions — the backend computes; every state change flows through the allocator/exit-gate/receipt machinery of v0 §§2, 4, 10.
3. A surface-submitted dispatch is a request, not an execution: it enters the same nine-gate, lint, ranking, and allocation pipeline as any other order. No surface bypasses a gate.
4. Client-facing views inherit asset-gate discipline (v0 substrate law): a client sees only their own runs' cells and artifacts.

---

## 18. Ledger amendment flag — `sandbox_ledger_v0` → `sandbox_ledger_v1` (PLANNED, PROPOSED)

A **PLANNED** amendment, flagged here and NOT assumed anywhere above:

- `sandbox_ledger_v0` (v0 §2.2) → `sandbox_ledger_v1` adds exactly two **OPTIONAL** columns per allocation row:
  - `plan_id` — pattern `^PLAN-[0-9]{4}$`; the plan a cell's run was instantiated from, when any.
  - `cell_kind` — the §12 enum.
- Optionality is the zero-conflict design: every valid v0 row remains a valid v1 row; rows written before ratification simply lack the columns; `cell_kind` stays derivable from the §12 mapping table whenever the column is absent, so no section of this spec depends on the amendment landing.
- Status: **PROPOSED** — requires founder ratification (work_order + receipt) before any schema or validator change; the v0 ledger validator (v0 NEXT item 3) would gain the two optional columns in the same packet.

---

## NEXT — follow-on work orders (packet candidates)

Each item is a candidate `p0_prompt_packet_v1.1` packet (route CLOUD_WORKER, all nine gates, five-axis ROI), not committed work:

1. **Ledger v1 amendment packet** — `sandbox_ledger_v1` schema with optional `plan_id`/`cell_kind` columns (§18) + validator update extending v0 NEXT item 3. Rides CF-P1 / PF-B; founder ratification receipt required.
2. **Concurrency preconditions in the allocator** — add the §14 checks (max 3 cells per run; 1 writer cell per repo) to the `scripts/factory_sandbox_allocate_v0.py` spec (v0 NEXT item 1). CF-P1.
3. **W7-adjacent schedule-install scan** — extend the `scripts/check_sandbox_walls_v0.py` spec (v0 NEXT item 2) with §16 schedule-install verbs + one negative test per the v0 NEXT item 4 battery. CF-P1.
4. **Plan-level cost rollup spec** — the §15 `plan_id`-keyed accumulation feeding `plan-factory/PLAN_RANKING_ROI_MODEL_v1.json` reuse/cost-efficiency inputs. Rides PF-B (plan compiler + library validator).
5. **Control-surface read-only cell view contract** — §17 display-and-submit API surface for Studio IDE / Forge Terminal, per the Control Desk contract precedent. CF-P2+ / PF-D; NOT BUILT until its phase unlock receipt exists.
