# NOOS SourceA observe loop triage v1

**Saved:** 2026-07-03T10:30Z  
**Authority:** SG observation → dispatch to NOOS lane  
**Owner agent:** `noos_agent`  
**Root:** `~/Projects/noetfeld-os`  
**Do not edit in SG repo** — paste this prompt into the noetfeld-os Cursor chat.

---

## Symptom

`noos-sourcea-observe-loop` GH workflow fails on schedule (`15,45 * * * *`) and CF fleet dispatch.

| Field | Value |
|-------|-------|
| Last failure | 2026-07-03T10:01:15Z |
| State | `FAILED_WITH_RECEIPT` |
| Blocker | `steps_failed:['sourcea_supabase_observe']` |
| Step exit | 1 |

---

## Root cause (confirmed from GH logs)

`scripts/observe_sourcea_supabase_v1.py` returns `ok: false` because **portfolio spine Supabase is not configured in CI**:

```json
"truth_log": { "ok": false, "skipped": true, "reason": "portfolio_spine_not_configured" },
"cycle_receipts": { "ok": false, "skipped": true, "reason": "portfolio_spine_not_configured" },
"telemetry_logs": { "ok": false, "skipped": true, "reason": "portfolio_spine_not_configured" }
```

The script reads credentials from:

1. `~/.sourcea-secrets/portfolio-spine.env` (Mac only — absent on `ubuntu-latest`), or
2. Env vars `SUPABASE_URL` + `SUPABASE_SERVICE_ROLE_KEY` (or `SUPABASE_SERVICE_KEY`)

The workflow `.github/workflows/noos-sourcea-observe-loop.yml` **does not pass** those env vars. Factory autorun succeeds because it uses `NOETFIELD_SUPABASE_*` via `autorun_status_v1.py` / `supabase_profiles` — a **different credential path**.

This is **not** Supabase down. Factory + inbox + chain loops prove the sink is live.

---

## Lane prompt (copy into noetfeld-os chat)

```
Task: Fix noos-sourcea-observe-loop — wire portfolio-spine Supabase read-only in CI.

Path: ~/Projects/noetfeld-os

Target:
  - .github/workflows/noos-sourcea-observe-loop.yml
  - scripts/observe_sourcea_supabase_v1.py (only if env mapping insufficient)

Action (pick smallest valid fix):
  A) Preferred: add workflow env mapping from existing org secrets:
       SUPABASE_URL: ${{ secrets.NOETFIELD_SUPABASE_URL }}
       SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.NOETFIELD_SUPABASE_SERVICE_ROLE_KEY }}
     Confirm portfolio-spine tables (truth_log, cycle_receipts, telemetry_logs) are readable
     with that key (read-only observe — no writes).

  B) Alternative: teach observe_sourcea_supabase_v1.py to resolve supabase_profiles.portfolio_spine
     from workflows doc (same pattern as autorun_status_v1.py) so one secret naming convention.

  C) Hygiene-only fallback (if spine is intentionally Mac-local): treat portfolio_spine_not_configured
     as non-fatal in noos_loop_runner for sourcea_observe lane only — mirror gel-ci observe fix pattern.
     Only use if A/B are blocked by schema/RLS separation.

Check:
  - python3 scripts/observe_sourcea_supabase_v1.py --json --write-receipt  (with env set)
  - gh workflow run noos-sourcea-observe-loop.yml OR wait for next 15/45 cron
  - Expect: step sourcea_supabase_observe exit 0; loop state not FAILED_WITH_RECEIPT
  - gel-ci ALL PASS (no parallel_conflict regression)

Constraints:
  - Read-only observe — phase_reconciler_v1 remains sole control authority
  - Do not deploy SourceA CF workers from NOOS
  - Do not weaken factory autorun sink invariants

Stop: one green observe-loop GH run + receipt in .noos-runtime/observe/sourcea/
```

---

## Verification commands (NOOS repo)

```bash
# Local dry-run (after exporting env)
export SUPABASE_URL="$NOETFIELD_SUPABASE_URL"
export SUPABASE_SERVICE_ROLE_KEY="$NOETFIELD_SUPABASE_SERVICE_ROLE_KEY"
python3 scripts/observe_sourcea_supabase_v1.py --json --write-receipt

# Trigger manual dispatch if workflow supports it, or:
gh workflow run noos-sourcea-observe-loop.yml --repo Noetfield-Systems/noetfeld-os

# Confirm
gh run list --workflow=noos-sourcea-observe-loop.yml --limit 3
```

---

## Related registry rows

| Artifact | Path |
|----------|------|
| Loop definition | `data/noos-24-7-loops-v1.json` → `sourcea_observe` |
| Trigger | `data/trigger-registry-v1.json` → `NOOS-T6-sourcea-observe` |
| Workflow | `.github/workflows/noos-sourcea-observe-loop.yml` |
| Observe script | `scripts/observe_sourcea_supabase_v1.py` |
| Runner | `scripts/noos_loop_runner_v1.py` |

---

## SG note

Observe failure is **hygiene lane** (`value_class: hygiene`). It does not block NOOS factory, SourceA deploy, or brain promote. Fix for observability completeness, not incident response.
