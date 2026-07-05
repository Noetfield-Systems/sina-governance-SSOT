# Governed Autorun Laws v3

**Schema:** `governed-autorun-laws-v3`  
**Saved at (UTC):** 2026-07-02T12:30:00Z  
**Owner:** SourceA Loop Specialist (standing assignment)  
**Skill SSOT:** governed-autorun v3 (Cursor skill)  
**Determinism reference:** `.cursor/skills/governed-autorun/references/deterministic-loops.md` (D1–D8)  
**Scope:** CF cron worker · Railway FBE motor · queue batches · cycle receipts · sink invariants · heartbeats · external verification · Kaizen improvement backlog

Operating system for continuous, parallel, self-improving multi-sandbox execution. v3 adds **L13 — Loops are deterministic** (D1–D8) on top of v2 ROI layer (L11).

## L1 — One reconciler

One control authority per sandbox. New supervisors/registries extend `scripts/phase_reconciler_v1.py` or emit desired-state artifacts it consumes. Independent run/lock/state authority = rejected. Every consolidation report carries `reconciler authority: ONE / DUPLICATE`.

## L2 — IDLE_NO_WORK is healthy

Empty queue → `IDLE_NO_WORK` receipt. Never manufactured work, never fake PASS, never silence. States: `RUNNING` · `IDLE_NO_WORK` · `BLOCKED_WITH_REASON` · `COMPLETE` · `FAILED_WITH_RECEIPT` · `TRIAGE_REQUIRED` · `THROTTLED_ROI`.

## L3 — No decision without a reason

Every gate emission = `{decision, reason, evidence: command + output}`. Bare NO/BLOCKED is malformed. Summaries derive from actual row IDs; producer output validated against reality post-write, fail closed.

## L4 — Verify from outside

PASS is valid only from a probe the building agent does not control: **GitHub Action** `external-verify.yml` posting `EXTERNAL_VERIFY_PASS` to **Supabase `truth_log`** (payload: run_id, run_url, conclusion, per-check verdicts, body hashes, determinism gate). Disk receipt is a mirror. Local dist, same-machine curls, preview URLs, and “check Actions UI” are INVALID. Verify-time minus publish-time < 60s = auto-reject.

## L5 — Verifier freeze

Verifiers and pass criteria are founder-gated. A failing agent fixes the system, never the test. Weakening a failing check = immutability violation = BLOCKED until founder approves the diff.

## L6 — Commit before deploy

Deploys run from a clean committed SHA. Dirty guard fails closed; scoped exceptions only via founder-reviewed `dirty_scope_map`. Receipts live in repo under `receipts/cloud/`, not home directories only.

## L7 — Founder items never block, never vanish

Status `founder_blocked` (never `cancelled`) is for **founder decisions only** — excluded from machine scan, present in every cycle receipt with count/oldest/priority/age.

**Observations are not founder tasks.** Action run status, page content, deploy SHA, and receipt rows must be machine-retrievable via `scripts/read_action_runs_v1.py` + Supabase `truth_log`. An agent that blocks on “founder please check X” when an API exists is a **defect**.

## L8 — Sinks are acked or blocked

Advance never decouples from sink ack. Invariant per cycle: `Σ(origin counts) == sink_count`, provenance-tagged per row. Mismatch → `BLOCKED_WITH_REASON`.

## L9 — Fail-closed refill

Expansion admits only rows passing the current rubric unmodified. 0 admitted is valid and reportable.

## L10 — Cross-sandbox reads via shared sink only

No sandbox reads another's disk/repo. Status flows through Supabase. Rows older than freshness window → `STALE_DATA`, never guessed.

## L11 — Every cycle has a cost; every loop earns its keep

Each cycle receipt carries `cost` (provider, model, tokens in/out, unit cost, $ total) and `value_class` (`revenue_path` · `proof_asset` · `risk_reduction` · `hygiene` · `none`). Loops report rolling cost-per-COMPLETE and spend-by-value_class in heartbeat. >30% trailing-window spend on `none` → `THROTTLED_ROI` (frequency cut, founder notified).

## L12 — Drift is detected, not discovered

Each heartbeat compares deployed truth to committed truth: live config hash vs repo hash, Railway deploy SHA vs `git rev-parse HEAD`, wrangler worker name vs `CF_VERSION_METADATA`, cron last-fire vs `*/10` schedule. Any mismatch → drift receipt with diff.

## L13 — Loops are deterministic

Same inputs → same transitions → same receipts, replayable from the event log. Idempotency keys on every side effect, single writer + compare-and-swap per state cell, IDs from actuals never inference, advance as a pure function of acks, LLM output as proposal never transition, verification as a pure function.

**Full rules:** `references/deterministic-loops.md` (D1–D8) · **CI gate:** `scripts/verify_autorun_determinism_v1.py` (4 tests in `external-verify.yml`).

| Rule | Summary |
|------|---------|
| D1 | Idempotency keys on side effects; sinks upsert on `op_key` |
| D2 | Single writer per state cell; CAS advance |
| D3 | IDs from max(actual) + 1; post-write range validator |
| D4 | Advance = f(execute_ok ∧ validate_ok ∧ sink_acked) |
| D5 | Event log is truth; derived state must replay-match |
| D6 | Jitter/time quarantined to scheduling edge |
| D7 | LLM proposes; validator accepts before event log |
| D8 | Verify is pure function; runner divergence = escalation |

## L14 — Trigger registry co-commit (T-REG)

Every new autonomous trigger — CF cron, GHA schedule/push/dispatch, Railway cron, or piggyback hook — MUST add or update `data/trigger-registry-v1.json` in the **same commit**. `scripts/sandbox_health_sweep_v1.py` MUST pass before merge (enforced in `determinism-gate.yml` and `.githooks/pre-commit` on trigger paths). A live trigger without a registry entry = defect (L12 drift). Piggyback triggers register the hook path, not a duplicate cron worker.

## L15 — One integrator per repo (agent-D2)

**Cloud Loop Specialist** owns integration to `main`. Local Worker and Brain agents implement on branches only — never push `main` directly. Non-fast-forward merge attempts must **rebase**, not force-push.

Before starting any task: read `main` and open branches for existing implementation. **Duplicate implementation = defect** (same severity as unregistered trigger · L14).

Enforcement: GitHub branch protection on `main` (founder P4) + `.githooks/pre-push` warning when pushing local commits to `main`.

## L16 — Mac agents are spine citizens (MAC-CLOUD BRIDGE)

Mac Cursor/Worker agents MUST register on the portfolio spine every cycle:

| Wire | Requirement |
|------|-------------|
| W1 fresh-main | Session gate `git fetch origin`; local `main` ≠ `origin/main` → `BLOCKED_WITH_REASON` `stale_local_main` until rebased; receipt + `MAC_FRESH_MAIN_SYNC` truth_log |
| W2 heartbeat | Session gate + Hub keepalive POST `mac_agent_heartbeat` `{agent_id, repo, sha, dirty_count, at}`; dashboard mac lane → `STALE_DATA` when last row >30m |
| W3 spine inbox | `worker_inbox` Supabase SSOT (incl. `founder_blocked`); Brain W-LBA inserts rows; `.sina-loop/INBOX.md` = generated READ-ONLY mirror |
| W4 dual-write | Proof-grade Mac receipts self-register to `truth_log` (`mac_agent` source); `~/.sina/` mirror only |

**Registry:** `SA-T-mac-agent-heartbeat` in `data/trigger-registry-v1.json` (L14). **Module:** `scripts/mac_spine_bridge_v1.py`. **Migration:** `006_mac_spine_bridge_v1.sql`.

An agent invisible to the spine (no heartbeat, no fresh-main receipt, no inbox row when delivering) **may not write**.

## L17 — Cost-tiered worker routing (COST-TIER)

Route every task to the **lowest plausible tier** first. Escalation requires a `TIER_ESCALATION` receipt with `{from_tier, to_tier, reason, evidence}` — bare tier jumps are defects.

| Tier | Worker | Typical work | Cost |
|------|--------|--------------|------|
| **T0** | Scripts / no LLM | grep audit · registry sweep · doc/law sync · W-LBA-009 vocab | ~$0 |
| **T1** | GitHub Copilot pilot | Kaizen `machine_safe` backlog PRs · CODEOWNERS-fenced | low · after founder **P4** |
| **T2** | Cursor Auto / Composer | Branch builds · scoped sa · open W-LBA plane items | included pool |
| **T3** | Cloud Loop Specialist | Integration · merge to `main` · deploy→verify | L15 · cloud/API |

**Session cost receipt (every agent session):** post `{agent_id, tier, model, tokens, usd_est, tasks}` to `truth_log` as `AGENT_SESSION_COST` (`scripts/agent_session_cost_v1.py` · session gate hook).

**Brain digest:** weekly `spend_by_tier` + `cost_per_merged_change` trend (`scripts/brain_digest_cost_tier_v1.py` → `data/brain-digest-cost-tier-latest-v1.json`).

**Queue SSOT:** `data/worker-cost-tier-queue-v1.json` · **Boot pack:** `docs/AGENT_BOOT_PACK_v1.md` (tool-agnostic manifest).

## Parallel orchestration (Tier 1+ — founder trigger required)

Lanes · concurrency keys · lock ordering · priority within tick · jitter · backpressure. **BLOCKED** until founder triggers Tier 1.

## Cycle anatomy (per tick)

1. Lock (per-sandbox)
2. Select one eligible item or `IDLE_NO_WORK`
3. Execute inside sandbox scope
4. Meter — capture tokens/cost at call site (L11)
5. Verify — internal checks may gate advance; only external proves ship (L4)
6. Ack sink (L8)
7. Receipt — `autonomous-forge-run-cycle-receipt-v2` + `idempotency_key` (D1)
8. Heartbeat (daily): loops, states, sink invariants, cost table, drift (L12), founder_blocked escalations

## Kaizen — ROI-ranked self-improvement

Failed checks, DRIFT, `THROTTLED_ROI`, audit findings auto-file improvement candidates. `machine_safe` vs `founder_gated`. One highest-ROI `machine_safe` item per cycle. `founder_gated` → weekly digest in heartbeat.

## Standing duties (each session)

1. Read latest heartbeat + last 3 cycle receipts. Report: loops, states, sink invariant, drift, cost window (5 lines).
2. Surface `founder_blocked` (count, oldest, age). Never process or cancel.
3. If `BLOCKED_WITH_REASON` exists: fix or escalate before new work.
4. **Auto-note pending** — read `receipts/cloud/autorun-pending/pending-latest-v1.json` every cycle.

## Auto-pending (machine law)

`scripts/autorun_pending_v1.py` runs on every cycle receipt, heartbeat refresh, loop-specialist tick, and observer build.

## Work rules

- One improvement per cycle, highest expected ROI, `machine_safe` only.
- Reports: SHAs, receipt paths, counts before/after, cost table, dirty state, gate receipts `{decision, reason, evidence}`.
- No narrative claims without command + output.
- **CI fix law:** every workflow fix commit MUST quote the failing step log excerpt in the commit message. Blind retrigger commits without quoted error = defect.

## L4 CI bisect law

1. `external-verify.yml` = minimal buyer-surface lane only (curl + forbidden scan → artifact).
2. Supabase `truth_log` POST = separate step/commit (REST `curl`, never `psql` on runner).
3. Determinism gate = separate workflow `determinism-gate.yml` — never block L4 again.
4. Before push: `bash scripts/validate-github-workflows-v1.sh` (yamllint + actionlint).

## Wired artifacts

| Artifact | Path |
|----------|------|
| Laws v3 (this doc) | `docs/GOVERNED_AUTORUN_LAWS_v3.md` |
| Determinism reference | `.cursor/skills/governed-autorun/references/deterministic-loops.md` |
| Determinism CI gate | `scripts/verify_autorun_determinism_v1.py` |
| Legal transitions | `scripts/autorun_legal_transitions_v1.py` |
| Cloud runtime SSOT | `data/cloud-auto-runtime-v1.json` |
| Phase reconciler | `scripts/phase_reconciler_v1.py` |
| Autorun verifier | `scripts/verify_autorun_zero_manual_v1.py` |
| External verify Action | `.github/workflows/external-verify.yml` |
| CF cron worker | `cloud/workers/cloud-auto-runtime-tick-v1/` |
| Cycle receipts (repo) | `receipts/cloud/autonomous-forge-run-cycles/` |
| Heartbeat (repo) | `receipts/cloud/autonomous-forge-run-heartbeat/` |
| Loop specialist | `scripts/loop_specialist_tick_v1.py` |
| Cost-tier queue | `data/worker-cost-tier-queue-v1.json` |
| Agent boot pack | `docs/AGENT_BOOT_PACK_v1.md` |
| Spine migrations CI | `scripts/apply_portfolio_spine_migrations_v1.sh` |

## Out of scope

Sales copy · LinkedIn · product pages · NOOS repo · founder decisions.
