# TRUSTFIELD CLOUD LOOPS — IMPLEMENTATION PACKETS v1

**Authority:** `docs/CLOUD_FACTORY_PROMOTION_PLAN_TRUSTFIELD_v1.md` + `data/cloud_line_registry_v1.json` (Architect package, verified present 2026-07-08)
**Laws in force:** governed-autorun L1–L13, deterministic core D1–D8
**Target repo:** `Noetfield-Systems/TrustField-Technologies` @ `origin/main` `46d394a` (local checkout is BEHIND — builders must pull before touching anything)
**Doctrine:** every loop is DECLARED until its 24h zero-manual window closes green on externally-written receipts; only then VERIFIED. Manual green ≠ cron green.

**Conflict resolution recorded:** Loop order requested Platform Health "every 6 hours"; Architect registry (authority) specifies `*/30 * * * *`. Registry wins → 30 min.

**Structural guards (all packets):** no candidate contact, no email send, no public copy change. These are API-structural, not conventions: team bench admin create hardcodes `status="sourced"` (`app/routers/team_bench.py:245`), `approve_to_contact`/`mark_contacted` are founder-gated actions, email defer stays ON.

---

## Dependency order

```
P0 (foundation) → P1 Health, P5 Deploy Truth, P7 Prompt Registry
P0 → P2 Intake, P4 Evaluation
P7 + P5 → P3 Sourcing   (needs registry prompts + HOLD-flag contract)
```

---

## P0 — FOUNDATION: cloud factory tables + ops receipts API

Prereq for every loop (L8/L11: no receipt sink = no loop).

- **Files to touch:**
  - `alembic/versions/20260709_0006_cloud_factory_tables.py` (new)
  - `app/models.py` (add `OpsReceipt`, `PromptRegistryRecord`, `PromptRun`, `ApprovalQueueItem`, `AssetView`)
  - `app/routers/ops_receipts.py` (new: `POST /api/ops/receipts` + `GET /api/ops/receipts` behind `require_admin` from `app/deps.py:28`; upsert on `op_key` per D1)
  - `app/main.py` (include router), `app/schemas.py`
- **Env vars:** none new (Railway `ADMIN_TOKEN` exists)
- **Migration:** `20260709_0006_cloud_factory_tables` — `ops_receipts` (with `receipt_type` discriminator + `op_key` unique + `cost` JSON + `value_class`), `prompt_registry`, `prompt_runs` (FK → registry), `approval_queue`, `asset_views`
- **Tests:** `tests/test_ops_receipts_v1.py` — no-token → 401; same `op_key` posted twice → one row (D1); invalid `receipt_type` → 422; cost fields persisted (L11)
- **Deploy command:** PR → `gh pr merge --squash` into protected main → Railway auto-deploy applies alembic
- **Verification command:** `curl -fsS https://api.trustfield.ca/api/readiness` (migration head = `20260709_0006`); POST receipt with token → row readable; POST without token → 401 — from external runner, ≥60s post-deploy (L4)
- **Receipt name:** `ops_receipts.cloud_factory_tables_live` + SSOT mirror `receipts/trustfield-cloud-factory-foundation-v1-<ISO8601Z>.json`

---

## P1 — PLATFORM HEALTH LOOP (L1)

- **Schedule:** GH Actions cron `*/30 * * * *` + `workflow_dispatch` + `repository_dispatch: deploy_completed`
- **Files to touch:**
  - `.github/workflows/pa-health-cron.yml` (new; 0–60s jitter step per orchestration rules)
  - `scripts/monitor_partner_access_health_v1.py` (extend: POST `health_check` receipt to `/api/ops/receipts`; ensure probes cover the full ordered set — `/partner-access` 200, `/partner-access/apply` tracks 200, `/partner-access/platform` auth gate, `/health` + `/api/readiness`, admin gate 401-without-token, NDA gate deny, briefing lock/unlock state, aggregate `PARTNER_ACCESS_HEALTH`)
- **Env vars (GH secrets/env):** `VERIFY_BASE_URL`, `VERIFY_WWW_BASE`, `ADMIN_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- **Migration:** none (uses P0)
- **Tests:** `tests/test_monitor_health_receipt_v1.py` — probe classification; 1-fail=warn / 2-consecutive=alert+issue logic; receipt payload validates; never auto-rollback path absent
- **Deploy command:** merge to main (workflow activates)
- **Verification command:** `gh run list --workflow=pa-health-cron.yml --limit 3` — 2+ consecutive `schedule`-event runs green (bootstrap rule 3); receipt rows machine-timestamped by Actions, not sessions
- **Receipt name:** `ops_receipts.health_check` (artifact id `trustfield-partner-access-health-v3`; GH artifact as backup)

---

## P2 — CANDIDATE INTAKE LOOP (L2)

Event path already live: `POST /api/partner-access/apply` → `score_candidate` (`app/partner_access_service.py:308`) → threshold Telegram notify (`app/routers/partner_access.py:87`). Packet adds the nightly sweep + summary receipt only.

- **Files to touch:**
  - `scripts/pa_intake_nightly_sweep_v1.py` (new: re-score all open candidates, classify track, create admin note, assign next status via existing status machine, collect anomalies; scoring exception → repair-candidate finding, never blocks intake)
  - `.github/workflows/pa-intake-nightly.yml` (new; cron `0 8 * * *` UTC)
- **Env vars:** `ADMIN_TOKEN`, `API_BASE` (GH secrets/env)
- **Migration:** none
- **Tests:** `tests/test_intake_nightly_sweep_v1.py` — re-score idempotent (same input → same scores, D1); exception files repair candidate and continues; summary counts derived from actual row IDs and must equal admin-list counts (L3)
- **Deploy command:** merge to main
- **Verification command:** `gh workflow run pa-intake-nightly.yml` then one `schedule` run; `intake_summary` counts == `GET /api/partner-access/admin/candidates` counts
- **Receipt name:** `ops_receipts.intake_summary` (nightly; candidate row remains the event receipt)
- **Founder notify:** existing score-threshold Telegram only — unchanged.

---

## P3 — TEAM BENCH SOURCING LOOP (L3)

- **Schedule:** Claude Code cloud scheduled routine, weekly Mon 14:00 UTC (primary) + `.github/workflows/tb-sourcing-weekly.yml` fallback runner (`workflow_dispatch`)
- **Files to touch:**
  - `prompts/registry/tb.sourcing.r1_v1.md`, `tb.sourcing.r3_v1.md`, `tb.sourcing.r4_v1.md` (bodies; seeded from today's 3-agent sourcing output once verified)
  - `data/prompt_registry_v1.json` entries (via P7; `status: testing`)
  - `scripts/team_bench_sourcing_runner_v1.py` (new: check `deploy_truth_hold` first — abort BLOCKED_WITH_REASON if HOLD (P5 contract); run registry prompt via `app/prompt_runtime.py` (P7); validate output against `output_schema` — schema-invalid = deterministic REJECT + retry same `op_key` (D7); dedup vs `GET /api/partner-access/team-bench/admin`; POST rows with `casl_basis` + source/warm-intro evidence URL; unverifiable candidates dropped; meter cost at call site (L11))
  - `.github/workflows/tb-sourcing-weekly.yml` (new, fallback)
- **Env vars:** `ANTHROPIC_API_KEY`, `ADMIN_TOKEN`, `API_BASE` (GH + cloud routine secrets)
- **Migration:** none
- **Tests:** `tests/test_team_bench_sourcing_runner_v1.py` — malformed LLM output rejected, never written (D7); dedup; created rows can only be `sourced` (structural — create endpoint hardcodes it); missing `casl_basis` or evidence URL → row dropped; zero-row run → IDLE/finding receipt, not failure (L2/L9); HOLD flag → no run
- **Deploy command:** merge to main + create cloud scheduled routine (weekly)
- **Verification command:** one dispatched run capped at 5 rows; assert all new rows `status=="sourced"` with non-null `casl_basis` + evidence URL; count of rows in any state beyond SOURCED unchanged before/after
- **Receipt name:** `ops_receipts.sourcing_run` (class `TEAM_BENCH_SOURCED_ROWS`: rows created, dedup count, evidence URLs, cost table)
- **Hard guards:** no contact, no email, no message send — runner has no send capability; `approve_to_contact` founder-only in API.

---

## P4 — AGENTIC EVALUATION LOOP (L4)

- **Trigger:** after diligence submission (`POST /api/partner-access/diligence`, `app/routers/partner_access.py:192`) + nightly 09:00 UTC sweep
- **Files to touch:**
  - `scripts/pa_evaluation_sweep_v1.py` (new: deterministic layer = `build_agentic_evaluation` (`app/partner_access_platform.py:130`) + bench `_rescore` (`app/routers/team_bench.py:84`); LLM layer = registry prompt `pa.eval.review-pack` producing risk/conflict flags, role-fit scores, rank ordering, recommended next action, founder review questions; LLM failure → deterministic-only output tagged PARTIAL)
  - `app/routers/partner_access.py` (diligence handler: mark row eval-pending so next sweep picks it up — smallest change, no inline LLM in request path)
  - `.github/workflows/pa-eval-nightly.yml` (new; cron `0 9 * * *` UTC)
- **Env vars:** `ANTHROPIC_API_KEY`, `ADMIN_TOKEN`, `API_BASE`
- **Migration:** none
- **Tests:** `tests/test_evaluation_sweep_v1.py` — PARTIAL degradation path; question-pack schema validates; **advisory-only invariant: sweep never mutates candidate status** (decisions stay in L8); LLM output is proposal, validator gates persistence (D7)
- **Deploy command:** merge to main
- **Verification command:** seed candidate with diligence answers → run sweep → `evaluation_run` receipt lists rows evaluated, flags, prompt version + cost; assert zero status transitions occurred
- **Receipt name:** `ops_receipts.evaluation_run`

---

## P5 — DEPLOY TRUTH LOOP (L6)

- **Trigger:** every push to main + daily 12:00 UTC
- **Files to touch:**
  - `.github/workflows/pa-deploy-truth.yml` (new)
  - `scripts/deploy_truth_check_v1.sh` (new wrapper: run `scripts/verify_partner_access_platform_package_v1.sh`; repo `SITE_BUILD_ID` (`web/lib/site-config.ts`) vs live marker; deployed SHA vs `origin/main` HEAD — dirty/working-tree-publish risk, the Noetfield `/structure/` founding case; Cloudflare cache marker probe with cache-buster; API version via `/api/readiness`; migration status: live alembic head vs repo head; write receipt; on drift write `deploy_truth_hold` row)
- **Env vars:** `VERIFY_BASE_URL`, `VERIFY_WWW_BASE`, `ADMIN_TOKEN`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`
- **Migration:** none (HOLD = `ops_receipts` row type `deploy_truth_hold`)
- **Tests:** seeded-drift test — branch run with bumped `SITE_BUILD_ID` must yield PARTIAL + HOLD row within one cycle (plan §7); redirect policy OFF + full-body marker check in verifier (D8, L4)
- **Deploy command:** merge to main
- **Verification command:** push-triggered run green; then seeded drift caught; confirm P3/P4 runners refuse to start while HOLD row open
- **Receipt name:** `ops_receipts.deploy_truth` (+ `deploy_truth_hold` on drift; hold clearance is a founder point)

---

## P6 — ASSET GATE LOOP (L7)

- **Trigger:** quick matrix inside every P1 run + weekly deep audit Sun 10:00 UTC
- **Files to touch:**
  - `scripts/asset_gate_audit_v1.py` (new: iterate `ASSET_GATES` (`app/partner_access_vault.py:37`, 8 assets); probe each with no/invalid/expired session → assert 401/404; NDA gate: pre-NDA session denied `nda_signed` assets; term-sheet gate asserts offer-stage-only; videos/docs private (no public URL 200s); pull `asset_views` rows and assert legit deliveries logged)
  - `app/partner_access_service.py` (log `asset_views` row on every gated delivery — table from P0)
  - `.github/workflows/pa-asset-gate-weekly.yml` (new) + audit step appended to `pa-health-cron.yml`
- **Env vars:** `ADMIN_TOKEN`, `API_BASE`, `WWW_BASE`
- **Migration:** `asset_views` (in P0's `20260709_0006`)
- **Tests:** `tests/test_asset_gate_audit_v1.py` — matrix completeness == `len(ASSET_GATES)` (a gate added later cannot be silently unprobed); leak → SEV-1 alert path + immediate founder notify, probing continues; view-logging on delivery
- **Deploy command:** merge to main
- **Verification command:** weekly run receipt shows 8/8 assets × probe matrix all-deny; one legit authenticated delivery in staging produces an `asset_views` row
- **Receipt name:** `ops_receipts.asset_gate_audit`

---

## P7 — PROMPT REGISTRY LOOP (L5)

- **Trigger:** PR touching registry; every prompt run
- **Files to touch:**
  - `data/prompt_registry_v1.json` (TrustField repo; seed `tb.sourcing.r1/r3/r4`, `pa.eval.review-pack`, `ops.health.narrative` — all `status: testing`, validated against SSOT `data/prompt_registry_schema_v1.json`)
  - `prompts/registry/*.md` (versioned bodies; `prompt_body_ref` from registry)
  - `scripts/validate_prompt_registry_v1.py` (new: schema validation; every record has ID/version/lane/owner, input/output contract, `contract_tests_ref` exists on disk, `receipt_path` present; no two active versions of one `prompt_id`)
  - `.github/workflows/prompt-registry-ci.yml` (new: on PR touching `data/prompt_registry_v1.json` or `prompts/registry/**`; contract-test failure blocks new version only — previous version keeps running (rollback rule, L5-line))
  - `app/prompt_runtime.py` (new: loads active registry, **refuses any unregistered/inactive `prompt_id`** — the "no unregistered prompt runs in cloud" gate; logs `prompt_runs` row with tokens + cost_class + outcome; used by P3/P4 runners)
  - `GET /api/ops/prompt-registry` in `app/routers/ops_receipts.py` (serve active versions)
- **Env vars:** none new for CI; `ADMIN_TOKEN` for `prompt_runs` writes
- **Migration:** `prompt_registry` + `prompt_runs` (in P0's `20260709_0006`)
- **Tests:** `tests/test_prompt_registry_contract_v1.py` — malformed record → CI red; unregistered `prompt_id` run → refused with receipt; contract-test failure blocks activation while old version serves; two-active-versions → reject; `cost_class: dollars` activation requires `founder_approval_required_to_activate: true` (queues in L8 once built)
- **Deploy command:** registry seed PR → CI green → merge; Railway serves registry endpoint
- **Verification command:** CI green on seed PR; deliberately malformed record on a test branch → CI red; runner invoked with unknown `prompt_id` → refusal receipt; `prompt_runs` rows FK-valid to registry
- **Receipt name:** `ops_receipts.prompt_registry_seeded` (seed) · `prompt_runs` rows (per run) · CI receipt (per activation)

---

## Out of scope (per Loop Specialist order)

- L8 Founder Approval Queue build (ladder step D) — separate order; P3/P4/P7 reference it only as the destination for founder points.
- Candidate contact, email sends, public copy changes — prohibited; structurally gated regardless.
- No further governance docs; this packet list is the sole artifact of this order.

## Completion doctrine per packet

Each packet lands as one PR against `Noetfield-Systems/TrustField-Technologies` main, is verified by external runner only (L4), writes its named receipt, and mirrors an SSOT receipt `receipts/trustfield-cloud-loop-<packet>-v1-<ISO8601Z>.json`. Loop state is DECLARED at merge; VERIFIED only after a 24h zero-manual window of scheduled receipts with sink invariants and cost tables present (L11), drift check present (L12).
