# ACTIVATION LADDER v1 — Cloud Factory, TrustField

**Authority:** `docs/CLOUD_FACTORY_PROMOTION_PLAN_TRUSTFIELD_v1.md` · founder architect order 2026-07-08
**Rule per step:** preconditions → artifacts → verification → receipt. A step is DONE only when its receipt exists. No step contacts anyone, sends email, or publishes public UX.

---

## A. Commit/deploy current Team Bench Platform Program — ✅ DONE (2026-07-08)

- Commit `4663bc6` + verifier repairs `96e6cb3..46d394a`, pushed to protected main
- Railway deploy SUCCESS, migration `20260708_0005` applied, Cloudflare www deployed
- Canonical verifier: `PLATFORM_PACKAGE_PASS`
- **Receipt:** `receipts/p0pgr/TEAM_BENCH_PLATFORM_PROD_DEPLOY_v1-20260708T233943Z.json`

## B. Create cloud prompt registry (est. 1 lane, 20–30 files incl. tests)

- **Preconditions:** A done; `data/prompt_registry_schema_v1.json` approved as contract
- **Artifacts:** alembic `20260709_0006_cloud_factory_tables` (prompt_registry, prompt_runs, approval_queue, ops_receipts, asset_views) · seed registry JSON in TrustField repo (`data/prompt_registry_v1.json`) with first prompts: `tb.sourcing.r1/r3/r4` (from today's sourcing prompts), `pa.eval.review-pack`, `ops.health.narrative` — all `status: testing` · CI contract-test job
- **Verification:** migration applies on Railway; CI green on registry PR; GET registry endpoint serves active versions
- **Receipt:** `ops_receipts.prompt_registry_seeded` + SSOT mirror
- **Founder point:** none (all seeds `testing`; activation of candidate-touching prompts queues in L8 once D exists)

## C. Create cloud scheduled health/eval loops (est. 0.5 day)

- **Preconditions:** B (receipts table exists to write into)
- **Artifacts:** GH Actions workflows in TrustField repo: `pa-health-cron.yml` (30 min, monitor script, posts `ops_receipts.health_check`) · `pa-deploy-truth.yml` (push-to-main + daily, package verifier) · `pa-eval-nightly.yml` (re-score sweep + evaluation packs) · repo secrets: `ADMIN_TOKEN`, `TELEGRAM_*` (already on Railway side)
- **Verification:** two consecutive green scheduled runs each; seeded-drift test caught by deploy-truth job; Mac untouched
- **Receipt:** `ops_receipts.health_check` + `deploy_truth` rows machine-written by Actions
- **Founder point:** none

## D. Create founder approval queue (est. 0.5 day)

- **Preconditions:** B (approval_queue table)
- **Artifacts:** Railway endpoints (`GET/POST /api/ops/approvals`) mapping decisions to existing gated actions (`approve_to_contact`, admin candidate actions, prompt activation, drift resolution) · admin dashboard section under `/admin/partner-access` · daily digest workflow → Telegram
- **Verification:** a bench `approve_to_contact` request appears in queue; decision fires the existing API action and writes `approval_decision` receipt; nothing auto-approves
- **Receipt:** first `ops_receipts.approval_decision`
- **Founder point:** this step CREATES the founder surface — founder reviews queue UX once

## E. Create first sourcing run into SOURCED only (est. 0.25 day)

- **Preconditions:** B (prompts `tb.sourcing.*`), D (approval queue live), `ADMIN_TOKEN` as cloud secret
- **Artifacts:** Claude Code cloud scheduled routine (weekly) running registry sourcing prompts → POST SOURCED rows; seed import: today's verified 3-agent sourcing output via `scripts/team_bench_import_sourced_v1.py`
- **Verification:** rows visible in admin tracker with evidence URLs; zero rows in any state beyond SOURCED; CASL fields populated; dedup vs existing rows
- **Receipt:** `ops_receipts.sourcing_run` (TEAM_BENCH_SOURCED_ROWS class)
- **Founder point:** approving any candidate to `approved_to_contact` — via L8 queue only

## F. Create receipt dashboard (est. 0.25 day)

- **Preconditions:** C running (receipts flowing)
- **Artifacts:** admin page section reading `ops_receipts` (filter by type/line/date) · daily `receipt_summary` roll-up written by Actions · SSOT scorecard sync note
- **Verification:** founder sees yesterday's runs in one screen; summary counts match row counts
- **Receipt:** first `ops_receipts.receipt_summary`
- **Founder point:** none

---

## Order & dependencies

```
A(done) → B → C → D → E
                └→ F (after C)
```

**Definition of ladder complete:** success table in plan §7 all green for 48 consecutive hours.
