# Category Registry Drift Guard — Cloud Architecture (GHA + Cloudflare + Railway + Supabase)

**Status:** `PHASE-1-BUILT` (code only, not deployed) · **Date:** 2026-07-09 · **Authority:** Founder directive "START BUILDING Isolated (worktree) Autorun ON GHA CLOUDFLARE RAILWAY SUPABASE"
**Lane:** `cursor/product-category-lock-v1` (isolated worktree)

## Big picture

The 10-category `PRODUCT_CATEGORY_REGISTRY_v1.json` is only honest as long as something re-checks it. The prior fix (`category-registry-drift-guard`, an `mcp scheduled-tasks` local routine) only runs while Claude Code is open on this Mac — not truly cloud, not isolated-worktree, single point of failure. This build replaces the *execution* layer with the same governance pattern already proven live in this repo for P0-PGR (`.github/workflows/p0pgr-shadow-cycle-v1.yml`: `workflow_dispatch` → independent Cloudflare verify → receipt), rather than inventing a new one.

## Why these 4 services, and what each one actually does (no service added without a distinct job)

| Service | Role | Why it's not redundant with the others |
|---|---|---|
| **GHA** | Executes the drift-check in an isolated ephemeral runner + explicit `git worktree add` scratch checkout | The only layer that reads the repo/filesystem |
| **Cloudflare Worker** | Independently re-validates the receipt's shape/logic on a separate account + runtime before it's trusted (matches `workers/github-app-advisory` doctrine: never trust a job's self-reported PASS) | Different account (`SECONDARY_CF_ACCOUNT_ID`), different runtime, proven via `cf-ray` edge header — same independence proof already used for the SSOT verifier |
| **Supabase** | Durable, queryable run history (`category_drift_status_v1` + `category_drift_runs_v1`, following the exact `<subject>_v1`/`<subject>_runs_v1` pattern from `workflow_census_v1.sql`) | GHA artifacts expire; Cloudflare KV is a cache, not a queryable history table |
| **Railway** | Dead-man's-switch monitor: independently polls the Worker's `/category-drift/latest` on its own clock and alerts if it's gone stale | Catches the ONE failure mode nothing else catches — GHA itself going silent (outage, quota, cron never enabled) |

## CHESS — adversarial lenses

1. **Machine lens (mechanical failure):** GHA cron misfires or Actions is down → Railway's independently-scheduled monitor detects staleness (`last_checked_at` older than `max_age`), not dependent on the same trigger.
2. **Adversarial lens (fake-green):** the drift-check job could self-report "no drift" even when something's off → Cloudflare Worker independently re-validates the receipt shape (all 10 category_ids present, `observed_status` in the fixed enum, `drifted` boolean logically consistent with `registry_build_status != observed_status`) and only marks it verified if it agrees — same "never trust the cycle's own claim" doctrine as the P0-PGR shadow cycle.
3. **Adversarial lens (authority creep):** a scheduled job silently editing the registry is exactly the drift this whole lock exists to prevent → **read-only enforced at 3 independent layers**: GHA workflow permission is `contents: read` (cannot commit back), the drift-check script never opens `product/` in write mode, the Cloudflare Worker has no GitHub write scope, and the Supabase tables have no foreign key back into `product/`.
4. **Adversarial lens (premature automation):** going live on an unattended schedule without sign-off → the GHA `schedule:` trigger stays **commented out**, `workflow_dispatch` only, until a `FOUNDER-UNLOCK-DRIFT-CRON` receipt exists — the exact same R3 gate already codified for P0-PGR (`P0_PGR_CLOUD_ACTIVATION_LADDER_v1.md`).
5. **Cost lens:** a full web-research re-verification every week would be expensive and noisy → scope stays file-existence + receipt-appearance checks only (no LLM calls in the cloud job).

## Phased plan

- **Phase 1 (this turn — DONE):** build the 4 artifacts + this doc + a build receipt in the isolated worktree, commit locally. **No deploy. No live cron. No real GHA run. No live Cloudflare/Railway/Supabase resource touched or created.**
- **Phase 2 (founder-gated):** wire real credentials — GitHub Actions repo secrets, a Cloudflare KV namespace + API token + account, a Railway project, a Supabase service-role key — then manually trigger via `workflow_dispatch` to prove R1→R2, exactly like P0-PGR's cloud-manual proof.
- **Phase 3 (founder-gated):** only after a `FOUNDER-UNLOCK-DRIFT-CRON` receipt, uncomment the GHA `schedule:` line.

## Not-now boundary

- No deploy, no push to any live cloud resource, this turn.
- No real secrets committed anywhere — only referenced env var names, matching `gates/cf_tokens.py`'s `~/.sina/secrets` pattern.
- The local `mcp scheduled-tasks` drift-guard (`category-registry-drift-guard`) is **left running as a fallback** until Phase 2/3 are proven — not disabled, since it's the only layer that actually works today.

## Files built (Phase 1)

1. `scripts/category_registry_drift_check_v1.py` — the actual check (file-existence + receipt-appearance, no web calls)
2. `.github/workflows/category-drift-guard-v1.yml` — GHA orchestration (`workflow_dispatch` only, cron commented)
3. `workers/category-drift-verifier/index.js` + `wrangler.toml` — Cloudflare independent verifier + KV cache + status API
4. `infrastructure/supabase/migrations/002_category_drift_guard_v1.sql` — durable run history
5. `autorun/category-drift-guard/railway-monitor/` — dead-man's-switch monitor service
6. `autorun/category-drift-guard/BUILD_RECEIPT_v1.json` — sha256 of every artifact + explicit boundaries
