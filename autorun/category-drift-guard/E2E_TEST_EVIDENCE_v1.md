# Category Drift Guard — Full E2E Test Evidence (v1)

**Status:** `E2E_PROVEN_LOCAL` (still `PHASE_1_BUILT_NOT_DEPLOYED` for live cloud accounts) · **Date:** 2026-07-09
**Authority:** Founder directive "CHECK AND FIX AND UPGRADE THEM FULLY E2E"

> This upgrades verification from "each component unit-tested in isolation" to "the real pipeline proven working together" — using local dev runtimes (Cloudflare Workers local mode via `wrangler dev --local`, a local mock REST server for the Supabase leg) so nothing touches a live cloud account, matching the same boundary already established for this build (Phase 1 = build + prove, Phase 2 = founder-gated go-live).

## Findings checked and fixed

Two proof-asset paths flagged missing by the first drift-check run were investigated (not assumed):

| Category | Path | Root cause | Fix |
|---|---|---|---|
| CAT-03 | `skills/p0pgr-skills-workspace` | Genuinely absent on `cursor/product-category-lock-v1` — this branch predates its addition on `cursor/language-layer-v1`, not a regression | `git checkout cursor/language-layer-v1 -- skills/p0pgr-skills-workspace` (additive, verified via `git cat-file -e` before pulling) |
| CAT-05 | `skills/pr-conflict-resolver/PR_CONFLICT_RESOLVER_SKILL_LOCKED_v1.md` | Same cause | Same method |

Re-ran the actual check script after the fix: `categories_drifted: 0, categories_missing_evidence: 0` (was 2/2). Commit: `e713e9f`.

## Incident during this pass: isolated worktree was removed by a third autonomous agent

Mid-task, `sg-product-lock` (the worktree directory itself) was found deleted. Investigation (read-only, before any action) found:
- A **third agent** ("P0-PGR Runtime (session agent)", co-authored by a different model) had committed `chore(lane): checkpoint product-lock lane before worktree consolidation` (`7774d13`) and removed the worktree as part of automated lane consolidation.
- The branch `cursor/product-category-lock-v1` and all prior commits were **fully intact** in the shared `.git` object store — nothing was lost, only the working-tree checkout.
- Confirmed the branch was not checked out elsewhere, then recreated the worktree with a standard `git worktree add` (non-destructive, no data change).

This is now the **third** instance of concurrent multi-agent activity on this shared workspace this session (L0-maintenance agent, this P0-PGR Runtime lane-consolidation agent, plus an unrelated `claude/product-category-lock-status-7a40a4` worktree/branch observed but not touched). Recorded here as a standing operational reality, not resolved — see Not-fixed section below.

## E2E chain actually exercised (not simulated)

```
category_registry_drift_check_v1.py  →  category-drift-verifier (Cloudflare Worker, LOCAL)  →  railway-monitor
        (real script, real registry)        (real code, wrangler dev --local, real KV)         (real code, real HTTP poll)
                                                          ↓
                                          Supabase REST write path validated against
                                          a local mock server (exact GHA-embedded code)
```

1. **Script → real registry:** re-ran `scripts/category_registry_drift_check_v1.py` against the actual current `product/PRODUCT_CATEGORY_REGISTRY_v1.json` post-fix. Result: `categories_checked: 10, categories_drifted: 0, categories_missing_evidence: 0, categories_with_out_of_scope_evidence: 6` (6 = legitimate cross-repo citations, correctly not counted as drift).

2. **Cloudflare Worker, run for real:** started the actual `workers/category-drift-verifier/index.js` via `wrangler dev --local` (Cloudflare's real local Workers runtime, not a mock). Caught a real bug in the process: the committed `compatibility_date: "2026-07-09"` is correct for a real future Cloudflare deployment but not yet supported by the installed local dev binary (max `2026-06-24`) — a known Wrangler local-dev lag, not a code defect. Worked around it with `--compatibility-date` override for the local test only; the committed config is unchanged and correct for actual deployment.
   - `POST /category-drift/verify` with the real receipt → Worker **independently recomputed** `categories_drifted`/`categories_missing_evidence` from the receipt's own `results` array and got **exact agreement** with the Python script's numbers (0, 0). This is the core "never trust the job's own claim" property, proven against real data, not a synthetic fixture.
   - Result was `status: FAIL` (HTTP 422) — **this is correct, not a bug.** Local dev has no real Cloudflare edge network, so there's no genuine `cf-ray` header; the Worker correctly refuses to claim PASS without independence proof it cannot actually verify. Faking this locally would have been the real bug (fake-green). On real deployment, `cf-ray` will be genuinely present on every edge request and this will legitimately PASS.
   - `GET /category-drift/latest` after the POST returned the same receipt back — confirms real KV write+read round-trip through the actual local Workers runtime, not an in-memory stub.

3. **Railway monitor → real local Worker:** started the actual `autorun/category-drift-guard/railway-monitor/index.js`, pointed its `CATEGORY_DRIFT_VERIFIER_URL` at the running local Worker (`http://localhost:8787`). `GET /status` returned `{"ok":true,"detail":"fresh: last receipt 0.0h old"}` — the monitor correctly read the real Worker's real stored receipt and computed genuine freshness. This is the full 3-leg chain working together, not three services tested in isolation.

4. **Supabase leg:** no local Supabase CLI available. Validated the *exact* Python snippet embedded in `.github/workflows/category-drift-guard-v1.yml` against a local mock REST server that only returns `201` when the request hits `/rest/v1/category_drift_runs_v1` with valid `Authorization`/`apikey` headers (anything else returns `400`, which `urllib.request.urlopen` raises as an exception). Result: `HTTP status: 201`, no exception — the code is REST-API-shape-correct by construction, not just eyeballed.

## Cleanup

All local dev servers (`wrangler dev`, the Railway monitor test instance, the mock Supabase server) were killed and ports confirmed free after testing. No process left running.

## What is still NOT done (unchanged from Phase 1 — this pass raised confidence, it did not cross the deploy boundary)

Same as `BUILD_RECEIPT_v1.json`: no live GHA run, no Worker deployed to a real Cloudflare account, no real KV namespace, no Supabase migration run against the live `noetfield` project, no Railway service created, no real secrets, cron trigger still disabled pending `FOUNDER-UNLOCK-DRIFT-CRON`.

## Not fixed (deliberately, out of scope for this pass)

- The recurring multi-agent worktree-collision pattern in this shared workspace (this is the third incident this session). A durable fix (e.g., a per-agent worktree naming/registration convention, or a lock file) is a real, separate piece of work — flagged, not silently patched here.
