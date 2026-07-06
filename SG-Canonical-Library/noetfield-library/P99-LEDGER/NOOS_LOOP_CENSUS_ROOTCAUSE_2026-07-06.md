# NOOS Loop Census Root-Cause — 5 Stale/No-Receipt Targets

**Date:** 2026-07-06T10:10Z  
**Scope:** SG guard observation + scoped NOOS fix (workflow_audit + schedule gate only)  
**Law applied:** WORKFLOW_CENSUS_v1 — receipt → consumer → FIX only if GUARD/REVENUE consumer; else RETIRE

---

## Census table (5 loops)

| Loop | Receipt produced | Consumer (type) | Census class | Verdict | Root cause (if FIX) |
|------|------------------|-----------------|--------------|---------|---------------------|
| **inbox** | `loop-inbox` cycle in `noetfield_factory_cycle_runs`; inbox items processed/skipped | NOOS factory internal queue (no R path) | **META** | **RETIRE** | Stale ~3h: Railway motor green but selective dispatch gap after 06:30Z. Mislabeled `revenue_path` — drains `noetfield_worker_inbox_queue`, not customer revenue. |
| **workflow_audit** | `noos-workflow-audit-v1` report + `data/noos-audit-findings-v1.json` | Guard layer (census, heartbeat, triage) | **GUARD** | **FIX** | Exit code 1 on blocking findings → loop_runner `FAILED_WITH_RECEIPT` → Railway executor stopped refreshing Supabase row. Findings file never written to handoff path. |
| **self_heal_safe_fixes** | safe-fix execution receipt / handoff JSON | researcher escalation (internal META chain) | **META** | **RETIRE** | Upstream findings file absent; self-groom chain with no GUARD/R consumer. Stale co-travels with audit stall. |
| **researcher** | `noos-research-findings-v1` (partial mock) | specialist_proposals (META) | **META** | **RETIRE** | Mock investigation theater (`noos_researcher_v1.py`); no GUARD/R consumer. Stale co-travels with audit stall. |
| **factory_autorun** | `noetfield_factory_cycle_runs` for `noos-gel-factory` | legacy gel factory motor (superseded) | **META** | **RETIRE** | Superseded by `noos-loop-fleet-tick-v1` (14 targets). Motor dispatches but **no Supabase sink row** — duplicate META motor. |

**Score:** FIX 1 · RETIRE 4 (META or no GUARD/REVENUE consumer)

---

## Fixes applied (GUARD only)

### 1. workflow_audit — receipt-first critique

**Repo:** `noetfeld-os` (branch `cursor/cheap-worker-kernel-v1`)

- `noos_workflow_audit_v1.py`: writes `data/noos-audit-findings-v1.json`; exit **0** when report produced (findings live in receipt, not exit code).
- Registry step: `--write-findings` on audit cmd.
- **Verified receipt:** `2026-07-06T10:08:58Z` — `status=ok`, `exit_code=0`, `supabase_sink.ok=true`, interval 15m ✓

Evidence: `receipts/noos-loop-census-workflow-audit-fix-20260706T100858Z.json` (SG)

### 2. self_heal schedule drift — one home + deploy fail-closed

**Schedule home:** `data/noos-24-7-loops-v1.json` → `self_heal.interval_minutes: 10` (`every_10m`)

| Surface | Before | After |
|---------|--------|-------|
| Registry | 10m | 10m (unchanged — home) |
| `noos-self-heal-loop.yml` cron | `0 */1 * * *` (hourly) | `*/10 * * * *` |
| Deploy gate | none | `verify_noos_loop_schedule_registry_v1.py` in deploy script + GHA deploy workflow |

**Gate class:** L12 drift — same fail-closed pattern as config-hash gates (committed vs deployed mismatch → exit 1, deploy blocked).

Post-fix gate: `verify_noos_loop_schedule_registry_v1.py --skip-missing` → **ok=true, mismatches=0**

---

## RETIRE proposals (do not repair)

| Loop | Retirement action |
|------|-------------------|
| inbox | Remove from fleet motor; keep manual `cloud_inbox_worker_v1.py` on demand. Fix mislabel `revenue_path` → `hygiene` if kept. |
| self_heal_safe_fixes | Retire loop + GHA workflow; guard findings visible via audit receipt only. |
| researcher | Retire; remove mock deep-dive from 24/7 fleet. |
| factory_autorun | Retire legacy motor slot; `factory_autorun` target in live CF health is duplicate of loop fleet. |

**Note:** Live CF motor (`execution_plane: railway:noos-loop-runner`, 14 targets) is **ahead of disk** `cloud/workers/noos-loop-fleet-tick-v1/src/index.js` (7 GitHub-dispatch loops). Do not redeploy CF worker from disk without reconciling Railway executor source — would regress production.

---

## Honest state after pass

- **workflow_audit:** fixed locally + Supabase receipt fresh ≤15m.
- **4 META loops:** RETIRE proposed; not repaired per census rule.
- **self_heal schedule drift:** aligned + gated.
- **Overall fleet:** still YELLOW until Railway picks up workflow_audit fix deploy and META loops are retired from motor.

**Signer:** SG guard — census-first root-cause, no commercial execution
