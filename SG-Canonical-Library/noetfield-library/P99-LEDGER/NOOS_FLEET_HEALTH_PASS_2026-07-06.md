# NOOS Fleet Health Pass — 14 Targets

**Date:** 2026-07-06T09:50Z  
**Scope:** NOOS loop fleet only (SG guard observation — not commercial)  
**Motor:** `noos-loop-fleet-tick-v1` CF cron `*/5`  
**Execution plane:** `railway:noos-loop-runner` (per motor health)

---

## Motor verdict: **GREEN**

| Check | Result |
|-------|--------|
| CF `/health` | `ok: true` |
| `executor_url_ready` | true |
| `loop_secret_ready` | true |
| Target count | 14 |
| Trigger host | **cloud** (CF → Railway dispatch) |

**Not 24/7 on this pass:** Cursor session, Mac launchd, founder manual, weekly SG census.

---

## Target summary (14)

| Verdict | Count | Meaning |
|---------|------:|---------|
| **RUNNING** | 8 | Supabase `noetfield_factory_cycle_runs` fresh within 2× interval |
| **GHA_FAIL_STALE** | 10 | Last GHA workflow conclusion = failure, but run is **>16h old** |
| **STALE** | 2 | Supabase receipt older than 2× interval |
| **NO_RECEIPT** | 2 | No Supabase row (factory_autorun, kaizen_daily) |
| **CF_ONLY** | 1 | kaizen_daily — CF slot, no GHA workflow |

---

## Per-target table

| dispatch_id | interval | Supabase last | age (min) | GHA last | GHA result | Verdict |
|-------------|---------:|---------------|----------:|----------|------------|---------|
| inbox | 5 | 2026-07-06 06:30 | 199 | 2026-07-05 17:35 | failure | **STALE** |
| runtime | 15 | 2026-07-06 09:37 | 12 | 2026-07-05 17:30 | failure | **RUNNING** (Railway receipt; GHA stale fail) |
| surface | 20 | 2026-07-06 09:37 | 12 | 2026-07-05 17:20 | failure | **RUNNING** |
| chain | 30 | 2026-07-06 09:37 | 12 | 2026-07-05 17:30 | failure | **RUNNING** |
| self_heal | 10 | 2026-07-06 09:38 | 12 | 2026-07-05 17:30 | failure | **RUNNING** |
| sourcea_observe | 30 | 2026-07-06 09:38 | 12 | 2026-07-05 17:30 | failure | **RUNNING** |
| agent_nerve | 60 | 2026-07-06 09:38 | 12 | 2026-07-05 17:00 | failure | **RUNNING** |
| workflow_audit | 15 | 2026-07-06 06:30 | 199 | 2026-07-05 17:16 | failure | **STALE** |
| self_heal_safe_fixes | 30 | 2026-07-06 06:31 | 199 | 2026-07-05 16:18 | failure | **STALE** |
| researcher | 60 | 2026-07-06 06:28 | 202 | n/a | n/a | **STALE** |
| specialist | 120 | 2026-07-06 06:28 | 202 | n/a | n/a | **STALE** (within 2× for 120m — borderline) |
| orchestrator | 180 | 2026-07-06 09:39 | 10 | n/a | n/a | **RUNNING** |
| factory_autorun | 10 | — | — | 2026-07-05 17:30 | failure | **NO_RECEIPT** |
| improve_kaizen_daily | 1440 | — | — | n/a | CF slot | **CF_ONLY** |

---

## Honest read (no theater)

1. **CF fleet motor is live** — this IS real 24/7 cloud infrastructure.
2. **Railway executor is firing** — 8 targets have Supabase receipts **≤12 min** old (runtime, surface, chain, self_heal, sourcea_observe, agent_nerve, orchestrator).
3. **GHA conclusion column is misleading** — last GHA runs are **2026-07-05 ~17:30 UTC**, all `failure`. Execution appears to have moved to **`railway:noos-loop-runner`**; GHA status is **stale artifact**, not current truth.
4. **3 targets STALE on Supabase:** inbox, workflow_audit, self_heal_safe_fixes (~3h), researcher/specialist (~3h).
5. **factory_autorun:** motor dispatches but **no factory cycle row** — investigate `noos-gel-factory` sink.
6. **This is NOT “full auto healthy”** — motor green + partial loop receipts + stale GHA + 3 stale loops = **YELLOW overall**.

---

## What is NOT counted as 24/7 here

- Cursor chat / Cursor Automations (T1/T2 — complement)
- Mac launchd brain loop (complement)
- SG weekly census GHA
- Founder manual anything

---

## Recommended guard actions (SG lane only)

1. **Reconcile GHA vs Railway** — update health pass to probe Railway executor receipts, not stale GHA conclusion.
2. **Fix stale loops:** inbox, workflow_audit, self_heal_safe_fixes, researcher (why no dispatch in 3h?).
3. **factory_autorun receipt sink** — no row in `noetfield_factory_cycle_runs`.
4. **Do not** conflate this with revenue/outbound — NOOS loops are GUARD/META/hygiene, not sales.

**Evidence JSON:** `receipts/noos-fleet-health-pass-20260706T095009Z.json` (SG repo, local)

**Signer:** NOOS health pass — SG guard observation only
