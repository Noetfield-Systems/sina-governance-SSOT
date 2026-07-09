# SANDBOX MANAGER SPEC v0

**Version:** 0.1.0
**Status:** PROPOSED — design only. Nothing in this file is built, active, or verified. Every component below is TO BE BUILT unless explicitly marked as an existing precedent.
**Era:** PHASE_2_CLOUD_ONLY_ROI_TRACK
**Authority:** `cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md` (package authority). Chain: FOUNDER_CANON v1 → P0-PGR runtime v1.1 (command brain) → this package (execution substrate).
**Founder authorization:** receipt `founder-order-cloud-factory-substrate-20260709T011955Z` (`receipts/p0pgr/founder/`) — design-only unlock; building/deploying NOT unlocked.
**canon_version:** `founder_canon_v1.0.0`
**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.

---

## 1. Purpose

The Sandbox Manager is the isolation layer of the Cloud Factory Substrate: it allocates one bounded workspace per factory run, records the allocation in a ledger, enforces hard walls at the boundary, and guarantees a receipt at exit. It implements canon §5 verbatim: **"Autonomy inside sandbox. Hard walls at boundary. Receipt at exit."** Inside a dispatched lane there are zero mid-cycle permission requests; walls fire on escape, not on normal work.

Three existing precedents are generalized — nothing here is invented from zero:

| Precedent | What exists today | What this spec generalizes |
|---|---|---|
| `data/brain_domain_sandboxes_v1.json` | Named sandboxes with `sandbox_id`, gate profiles, and `sandbox_branch_prefix: "sandbox/brain/"` | Same `sandbox_id` + branch-prefix pattern, extended with a new `sandbox/factory/` prefix for factory runs |
| TrustField `ensure_worktree_sandbox()` (`scripts/bridge_loops_intake_www_upgrade_v1.py`, TrustField-Technologies repo) | One fixed detached worktree at `.worktrees/www-upgrade-sandbox`, env kill-switch, container delegation escape hatch | Per-run allocation under `.worktrees/factory/<sandbox_id>` with a ledger, per-line scope, timeout, cost cap, and cleanup rules |
| FOUNDER_CANON v1 §5 walls (G1–G8 classes, prose only today) | Wall doctrine: main writes, governance writes, approval language, token handling, hidden state, global installs, deploys, destructive git, out-of-scope files | Machine-readable wall list W1–W9 (§4) with a mechanical exit-gate script (TO BE BUILT) |

Scope: this spec governs isolation for all ten factory lines FL1–FL10 wherever `sandbox_required` is true in `cloud-factory/FACTORY_LINE_REGISTRY_v0.json`, across every execution target (§11).

---

## 2. Identity and allocation

### 2.1 sandbox_id

Format: `sbx-fr-NNNN-SS` where `NNNN` is the factory run number (from run id `FR-NNNN`) and `SS` is a 2-digit allocation sequence within the run (first allocation `01`). Example: `sbx-fr-0001-01`. One run may hold multiple sequential allocations (e.g. re-allocation after crash recovery, §8.4); allocations are never reused.

### 2.2 Sandbox ledger

- Path: `receipts/factory/sandbox_ledger_v0.json` (SG repo, always — the ledger is a governance record even when the sandbox itself lives in a venture repo).
- Schema: `sandbox_ledger_v0` (TO BE BUILT). Fields per allocation row:
  `sandbox_id`, `run_id`, `repo`, `worktree_path`, `branch`, `allowed_scope[]`, `env_profile`, `timeout_seconds`, `cost_cap_usd`, `status`, `allocated_at`, `expires_at`, `cleanup_state`, `artifact_dir`, `receipt_dir`.
- Row-state values defined by this spec (PROPOSED): `status` ∈ ALLOCATED | RUNNING | CLOSED | KILLED; `cleanup_state` ∈ HELD | PRUNE_ELIGIBLE | PRUNED | ARCHIVED.
- **One-writer law:** one writer per task cell (PARALLEL_AUTOMATION_GOVERNANCE L1). Ledger writes are compare-and-swap: re-read and hash-compare before write. A second concurrent writer for the same cell does not overwrite — it writes a REJECTED receipt and stops that attempt. Silent overwrite is a defect.
- Timestamps machine-generated at event time (`datetime.now(timezone.utc)`) — never typed.

### 2.3 Repo targeting rules

Which repo a run's sandbox lives in is decided at classification, before allocation:

1. **Venture deliverables** (Mode A workflow definitions, Mode B app code, any artifact that ships in a venture product) → sandbox in that venture's repo (Noetfield-Systems org). The order envelope's `venture` field decides.
2. **Governance artifacts** (registries, SSOT mirrors, substrate policy, receipts) → sandbox in SG (`sina-governance-ssot`) only.
3. **Never both.** One actor · one repo · one scope (`ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`); a mixed-scope order is a classification defect and must be split into separate runs before allocation.
4. Venture-repo sandbox output exits as branch + PR only: `write_to_venture_repo` is a `never_auto` merge action (`data/governance_repo_map_v1.json`); merge is a venture-owner/founder point.
5. The ledger row records the target `repo` explicitly; SG routes, it does not build venture workers.

### 2.4 Allocation algorithm (TO BE BUILT — CF-P1 packet)

1. Preconditions: run status is QUEUED; compiled packet exists (`packet_ref` in the run envelope); all nine gates passed at routing; a founder authorization receipt exists in `receipts/p0pgr/founder/`.
2. Resolve target repo per §2.3.
3. Compute `sandbox_id` = `sbx-fr-NNNN-SS` (next `SS` for this run).
4. CAS-claim the ledger row: verify no ALLOCATED/RUNNING row exists for the same task cell (`run_id` + `repo`); append the row with `status: ALLOCATED` and all §2.2 fields. On CAS conflict: REJECTED receipt, stop (do not retry-loop the ledger).
5. Create the worktree in the target repo:
   `git worktree add .worktrees/factory/<sandbox_id> -b sandbox/factory/<fr-id>`
6. Create `artifact_dir` (`receipts/factory/artifacts/<FR-ID>/`) and `receipt_dir` (`receipts/factory/<FR-ID>/`) in SG.
7. Set `expires_at` = `allocated_at` + the line's `timeout_seconds` (§6), never exceeding the remaining run-level 4h budget.
8. Flip ledger `status` → RUNNING; run status → SANDBOX_ALLOCATED then RUNNING.
9. Hand the worker ONLY the seven allowed task-spec keys (`goal`, `files`, `constraints`, `done_criteria`, `verify_method`, `receipts_required`, `decision_verdict`) — soup-wall law, gate precedent `scripts/verify_p0_core_output_soup_wall_gate_v1.py`. P0 CORE judgment text never enters a factory worker prompt.

---

## 3. Branch naming law

- Factory sandbox branches: `sandbox/factory/<fr-id>` (e.g. `sandbox/factory/fr-0001-intake-form`). Extends the existing `sandbox/brain/` prefix from `data/brain_domain_sandboxes_v1.json`.
- **NOT fence-exempt in v0 — deliberate.** `sandbox/factory/*` is not added to `draft_branch_patterns` in `policy/repo_fences_v1.yaml`; every merge to main passes full repo fences (RF_RECEIPT_REQUIRED, RF_POLICY_LAW_MUTATION, RF1/RF2/RF3) plus CODEOWNERS review. Adding the prefix to the exempt list would be a policy/law mutation — if ever wanted, it must be flagged as a PROPOSED amendment with work_order_id + receipt + founder ratification, never assumed.
- Archive tag on retirement: `factory-archive/<fr-id>` (§8.2).

Relationship to existing prefixes:

| Prefix | Use today | Fence treatment at merge to main |
|---|---|---|
| `cursor/*` | IDE builder lane (live use) | Full fences |
| `copilot/*` | Assist-lane drafts | Fence-exempt draft pattern (`policy/repo_fences_v1.yaml`) |
| `loops/*` | TrustField cloud-loop build branches (e.g. `loops/p0-cloud-factory-foundation`) | Full fences (venture repo discipline) |
| `sandbox/brain/*` | Brain domain sandbox lanes (`data/brain_domain_sandboxes_v1.json`) | Full fences |
| `sandbox/factory/*` | Factory run sandboxes — THIS SPEC, PROPOSED | Full fences (deliberately not exempt in v0) |

---

## 4. Allowed file scope and walls W1–W9

Per-line file scope is declared at allocation as `allowed_scope[]` (glob list) in the ledger row, derived from the line's scope map in `cloud-factory/FACTORY_LINE_REGISTRY_v0.json` plus the packet's `files` key. Enforcement is a **boundary check at sandbox exit**, not a mid-run permission loop — canon intent filter Q3: any design that produces permission loops during normal dispatched work is a defect.

Exit gate: `scripts/check_sandbox_walls_v0.py` — **TO BE BUILT (CF-P1 packet)**. It models canon §5 wall classes (G1–G8) as the mechanical checks below and runs once per line completion, before the line receipt is finalized.

| Wall | Blocks | Exit check (mechanical) | On violation |
|---|---|---|---|
| W1 main writes | Any commit/push landing on `main`; any ref update of `main` from inside the sandbox | Branch head ancestry check: all sandbox commits live on `sandbox/factory/<fr-id>` only; no push targets `main` | Contain + receipt + BLOCKED_WITH_REASON; repo fences + CODEOWNERS remain the independent backstop at merge |
| W2 governance/SSOT/ledger writes | Changes under `ssot/`, `data/`, `policy/`, `scripts/`, `.noos/`, `packages/noos-control-desk-v1/` unless the path is explicitly in `allowed_scope[]` (parity with `policy/repo_fences_v1.yaml` `protected_zones` — `scripts/` included because validator/gate code is FT-L5 territory) | Diff path list vs protected zones minus declared scope | Contain + receipt + BLOCKED_WITH_REASON |
| W3 approval language in outputs | Approval/sign-off/status-promotion text in any artifact or receipt (agents produce evidence, never approvals — canon §4; forged L5 sign-off incident 2026-07-03) | Text scan of artifacts + receipts for approval/sign-off markers | Contain + receipt + BLOCKED_WITH_REASON |
| W4 token/secret handling | Secrets or tokens copied into the worktree, artifacts, or receipts; credential mutation | Pattern scan of diff + artifacts; env_profile audit (§5) confirms no raw secret entered the sandbox env | Contain + receipt + BLOCKED_WITH_REASON; HARD_BLOCK class (identity/credential mutation) |
| W5 hidden state | Writes outside `worktree_path` and `artifact_dir` (all state must be in-repo — canon §9) | file_stat sweep of declared dirs vs actual write set | Contain + receipt + BLOCKED_WITH_REASON |
| W6 global installs | Global package installs / system-level mutation | Command-log scan for global-scope install commands; system paths untouched check | Contain + receipt + BLOCKED_WITH_REASON |
| W7 deploys | Any production deploy/promote command from inside a sandbox (HARD_BLOCK reason 2; production deploy is absent from the v0 substrate — FL7 is preview-only) | Command-log scan for deploy verbs (e.g. `wrangler deploy`, `railway up`, deploy-workflow dispatch) | Contain + receipt + BLOCKED_WITH_REASON; FOUNDER_ONLY path untouched |
| W8 destructive git | Force-push, history rewrite, deletion of branches/tags outside the sandbox's own branch | Reflog + ref audit of the target repo | Contain + receipt + BLOCKED_WITH_REASON; HARD_BLOCK class (destructive loss of canonical records) |
| W9 out-of-scope files | Any changed file not matched by `allowed_scope[]` | Diff file list vs `allowed_scope[]` globs | Contain + receipt + BLOCKED_WITH_REASON |

Violation protocol (all walls, no exceptions): **contain** (halt the line, quarantine the branch — never delete it), **receipt** (violation receipt naming the wall, machine-timestamped), **BLOCKED_WITH_REASON** on the line verdict, then machine-first escalation per canon §6 (detect → contain → critique → audit → deep_research → repair → validate → receipt → continue_or_escalate). Never silent, never history-rewritten, never routed to the founder except through the four founder triggers. Repeat scope/authority violations retire the session/tool (canon §10).

---

## 5. Env and secret policy

**Deny-by-default.** A sandbox env contains nothing unless its `env_profile` grants it. Raw secrets NEVER enter the worktree environment, files, or artifacts.

**Secrets-stay-at-target law:** execution that requires a secret runs where the secret already lives (GH Actions secret env, CF worker secret, Railway env) — the secret is never exported to another environment.

**Send-credential exclusion (structural no-send):** build/code lines (FL3, FL4, FL5 and all `claude_cloud_agent` work) receive NO send-capable credentials — no `ADMIN_TOKEN`, no `TELEGRAM_*`, no mail keys. This makes "no sends without approval" structural rather than conventional, reinforcing the `no_external_send` gate.

`env_profile` enum (exactly four values in v0):

| env_profile | Contents | Used by |
|---|---|---|
| `none` (default) | No network credentials, no secrets, local toolchain only. Deterministic work. | Any line not needing network; all `repo_worktree` work by default |
| `read_public_web` | Outbound HTTPS GET to public web only; no auth headers, no tokens; every fetched URL produces `url_fetch` evidence with status + body sha256 | FL1 research; FL8 read/verify paths |
| `gh_actions_scoped` | The run executes AS a registered GH Actions job in the repo where the secrets already live; the job sees only the secrets its registered workflow declares; nothing is copied into worktree or artifacts | FL6 test, FL9 receipt, GH-Actions-target lines |
| `preview_deploy_scoped` | Scoped credential capable of preview publication only (PR + GH Actions artifact + optional preview URL); no production deploy target reachable | FL7 deploy-preview only |

**Current secret inventory (reality, not design):** GH Actions (TrustField fleet) repo secrets wired: `ADMIN_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `NOETFIELD_SUPABASE_URL`, `NOETFIELD_SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `VERCEL_DEPLOY_HOOK_URL` — note the deploy-capable hook and the DB service-role keys are exactly the send/deploy-credential classes the exclusion above and walls W4/W7 are designed around. (`VERIFY_BASE_URL`/`API_BASE`/`WWW_BASE` are non-secret public-URL env values hardcoded in workflow files, not secrets.) `ANTHROPIC_API_KEY` is NOT wired — `claude_cloud_agent` lines are dormant until the founder wires it (activation dependency, not a design assumption). **No SG-side secrets inventory exists** (`requires_secrets` appears on only one motor in `data/github_automation_registry_v1.json`) — flagged gap; inventory artifact is a CF-P1 packet candidate (NEXT).

---

## 6. Timeout policy

Per-line `timeout_seconds` (defaults, founder-adjustable per order):

| Line | line_key | timeout_seconds |
|---|---|---|
| FL1 | research | 900 |
| FL2 | architecture | 1800 |
| FL3 | code | 3600 |
| FL4 | app_builder | 3600 |
| FL5 | workflow_builder | 1800 |
| FL6 | test | 1800 |
| FL7 | deploy_preview | 900 |
| FL8 | verifier | 900 |
| FL9 | receipt | 300 |
| FL10 | harvest | 900 |

Run-level cap: **4 hours** total across all lines of one run. `expires_at` on each ledger row is bounded by both the line timeout and the remaining run budget.

Timeout behavior: kill the line process, write a **PARTIAL** line receipt with `limitations[]` describing what completed and what did not (continuity law: partial beats lost — never discard completed work). The run continues per the failure_behavior degrade order (tag confidence → reduce scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue); it does not default to STOP.

---

## 7. Cost caps

- Per-line default: `cost_cap_usd` **2.00**. Per-run default: **5.00** USD.
- Override: the order envelope's budget field (founder-adjustable per order) may raise or lower both; the ledger row records the effective cap.
- **Breach behavior:** the line halts immediately, writes a PARTIAL receipt with `limitations[]`, the run moves to QUEUED_FOUNDER_REVIEW, and the event is classed **FT-CAPITAL** (capital/spend beyond caps is one of the four founder triggers). No line restarts on the same budget.
- **Cost rollup chain:** line receipt `cost` → run receipt `cost` (sum over lines) → `receipts/p0pgr/phase2_scorecard_v1.json` `counters.cost_usd`. Every hop is machine-written; no typed cost figures.
- **Metered honesty (governed-autorun L11):** cost tables report what was actually metered. Deterministic scripts (`model_tier: determine`, `cost_class: zero`) report `llm_calls: 0` truthfully with a `metered_note` stating the basis; estimates are labeled as estimates, never presented as metered.

---

## 8. Cleanup rules

### 8.1 Worktree prune preconditions

A worktree may be pruned ONLY after all three hold:
(a) the run receipt is written; (b) all artifacts are stored per §9; (c) every artifact's sha256 is recorded in its line receipt.
Until then `cleanup_state` stays HELD. When all three hold it becomes PRUNE_ELIGIBLE; after `git worktree remove` + `git worktree prune` it becomes PRUNED.

### 8.2 Branch retention

The `sandbox/factory/<fr-id>` branch is retained **≥ 30 days** after run close, then archived as tag `factory-archive/<fr-id>` BEFORE the branch is deleted. `cleanup_state` → ARCHIVED. The tag is permanent.

### 8.3 Never-delete law

Receipts and artifacts are NEVER deleted — founder law: rejection ≠ permission to delete. Cleanup applies to worktrees and (after archival) branches only. Quarantined branches from wall violations (§4) are archived, never removed.

### 8.4 Orphan / GC sweep and crash recovery

- Sweep trigger: **dispatch-only in v0** (manual `workflow_dispatch` or session dispatch). No cron — no scheduled automation without explicit founder approval; R3 remains locked.
- Stale detection: a ledger row with `expires_at` in the past, `status` RUNNING, and no line receipt is a stale allocation (crashed run).
- Recovery: the sweep salvages any recoverable output into `artifact_dir`, writes a PARTIAL receipt with `limitations[]` for the dead line, flips the row to KILLED, and writes a **ledger repair receipt** documenting the state change. The worktree is preserved until salvage completes (§8.1 preconditions apply). Re-allocation for the run, if attempted, takes the next `SS` sequence — the stale row is never edited in place beyond its status/cleanup fields.

---

## 9. Artifact storage

| Store | Path / id | Role |
|---|---|---|
| In-repo (SG) | `receipts/factory/artifacts/<FR-ID>/` | Small/text artifacts; canonical location |
| GH Actions artifacts | upload-artifact per run | Build outputs; 90-day default retention |
| CF KV mirror | namespace `RECEIPTS`, id `cf97659f15f14d06be4400caad4823c2` (worker `sina-governance-ssot-advisory`, secondary CF account) | Cloud mirror of governance-grade artifacts |

- Every artifact gets a **sha256 recorded in its line receipt** (evidence kind `hash`), regardless of store.
- No R2/S3 bucket exists for large binary artifacts — **flagged gap, CF-P2+**. v0 designs within the three stores above.

---

## 10. Receipt paths and schemas

- Line receipt: `receipts/factory/<FR-ID>/<line_key>-<ISO8601Z>.json`, schema `factory_line_receipt_v0` (TO BE BUILT).
- Run receipt: `receipts/factory/<FR-ID>-run-<ISO8601Z>.json`, schema `factory_run_receipt_v0` (TO BE BUILT).

Both schemas carry, required:

- `schema` (const), `receipt_id`, `canon_version` (`founder_canon_v1.0.0`), `packet_id`, `run_id`
- `gates_checked` — all NINE gates as PASS|FAIL strings: `cloud_only`, `read_only_or_reversible`, `roi_positive`, `no_deploy`, `no_external_send`, `no_legal_financial_commitment`, `no_p0_leakage`, `no_authority_change`, `founder_authorization_receipt`
- `quality_state` — PASS | PARTIAL | PROVISIONAL | FAIL
- `evidence[]` — items require `claim` + `kind` (kind ∈ `url_fetch` | `script_run` | `file_stat` | `hash`; optional `url`, `status`, `sha256`, `saved_path`)
- `cost` — `{llm_calls, metered_note}`
- `accounting_note`, `executor_route_note` (route deviation recorded here — silent deviation = authority drift), `commit_flag`

Line receipt additionally: `line_id`, `line_key`, `sandbox_id`, line verdict (PASS | PARTIAL | FAIL | BLOCKED_WITH_REASON | SKIPPED), `artifacts[]` `{path, sha256}`, optional `limitations[]`, `findings[]`.
Run receipt additionally: ordered `line_receipts[]` references, terminal run status (lifecycle enum in `CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`), cost rollup, any HOLD references.

Timestamps in both are machine-generated at event time (`datetime.now(timezone.utc)`) — never typed. A run cannot reach CLOSED without its complete receipt chain.

---

## 11. Execution-target notes

How sandboxing maps per execution target (enum from the substrate authority doc):

| Target | Sandbox mapping |
|---|---|
| `repo_worktree` | This spec directly: worktree + `sandbox/factory/<fr-id>` branch + ledger row + exit-gate walls. |
| `github_actions` / `github_actions_runner` | The ephemeral runner IS the sandbox. A ledger row is still written (`env_profile: gh_actions_scoped`; `worktree_path` records the runner checkout). Walls checked by a job step running `scripts/check_sandbox_walls_v0.py` before artifact upload. |
| `claude_cloud_agent` | Cloud sandbox session; the session workspace is recorded in the ledger row. Dormant until `ANTHROPIC_API_KEY` is wired in GH Actions secrets (activation dependency, not a design assumption). |
| `cloudflare_worker` / `railway_api` / `supabase` | No worktree — execution is config-scoped at the target where the secrets already live (§5). A ledger row is still required (worktree/branch fields recorded as not-applicable). Cloudflare tool_law defers CF to Phase 3/4 control plane: v0 uses ONLY the existing verifier worker read/verify path (`sina-governance-ssot-advisory`), no new CF control plane. Railway/Supabase are not yet motor `kind`s in `data/github_automation_registry_v1.json` — registry amendment flagged for when they are built. |
| `session_embedded` | Founder-visible session under the light shell law (INCIDENT-039: max one light shell ≤ 90s per turn). If repo files are touched, `repo_worktree` rules apply; otherwise a ledger row records the session-scoped allocation. |
| `container_runner` | FUTURE — not available in v0. No design commitments here. |

Registry law applies to every target: any motor executing sandbox allocations (e.g. `gh_actions_factory_dispatch_v0`) must be registered in `data/github_automation_registry_v1.json` BEFORE its first run (PARALLEL_AUTOMATION L4: registry is routing truth). None are registered in the v0 design.

---

## NEXT — follow-on work orders (packet candidates)

Each item below is a candidate `p0_prompt_packet_v1.1` packet (route CLOUD_WORKER, all nine gates, five-axis ROI), not committed work:

1. **Sandbox allocator script** — proposed `scripts/factory_sandbox_allocate_v0.py`: §2.4 algorithm, CAS ledger claim, REJECTED-receipt path for second writers, worktree creation. CF-P1.
2. **Walls checker** — `scripts/check_sandbox_walls_v0.py`: W1–W9 mechanical exit checks per §4, violation receipts, BLOCKED_WITH_REASON verdicts. CF-P1.
3. **Ledger validator** — proposed `scripts/validate_sandbox_ledger_v0.py`: `sandbox_ledger_v0` schema check, one-writer invariant, `expires_at` staleness detection feeding §8.4. CF-P1.
4. **Negative test battery** — proposed `tests/factory_sandbox/run_negative_tests.py` per the `tests/repo_fences/run_negative_tests.py` pattern: seed one known-bad mutation per wall W1–W9 and assert the checker FAILS with the right wall id. CF-P1.
5. **SG-side secrets inventory** — close the §5 flagged gap: a governance artifact inventorying which secret lives at which target, feeding `env_profile` audits. CF-P1.
