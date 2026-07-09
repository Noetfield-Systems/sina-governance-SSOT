# WORKFLOW_CENSUS_v1 — Dispatch Receipt

**Date:** 2026-07-06  
**Authority:** Architect dispatch (goal-function judging layer)  
**Status:** **DISPATCHED** — script + migration + weekly GHA wired  
**Goal:** First payment receipt from a stranger without founder as runtime component.

---

## The dispatch (verbatim intent)

Build **WORKFLOW_CENSUS_v1**: crawl Cloudflare (workers + crons), Railway (services + crons), GitHub (workflows), Supabase (loop_registry) → one table per loop:

| Field | Purpose |
|-------|---------|
| name | Human label |
| host | cloudflare \| railway \| github \| supabase \| traffic \| mac |
| schedule | cron / always_on |
| invocations/day | measured or estimated |
| cost/mo | USD estimate |
| last receipt produced | timestamp + id |
| value_class | REVENUE \| GUARD \| META \| NONE |

Write to Supabase (`workflow_census_v1`). Rerun **weekly** by cron.

Add traffic row: `www traffic → intake conversion rate`.

---

## What shipped (SG repo)

| Artifact | Path |
|----------|------|
| Migration | `infrastructure/supabase/migrations/001_workflow_census_v1.sql` |
| Apply script | `scripts/apply_workflow_census_migration_v1.py` |
| Census Scheduler and executor | `scripts/workflow_census_v1.py` |
| Value-class rules | `data/workflow_census_value_class_rules_v1.json` |
| Gateway/traffic extensions | `data/workflow_census_extensions_v1.json` |
| Weekly GHA | `.github/workflows/workflow-census-weekly-v1.yml` (Mon 08:00 UTC) |

**Supabase tables:** `workflow_census_v1` (current row per loop), `workflow_census_runs_v1` (weekly rollup + audit flags).

---

## Standing audit (deterministic — agent applies weekly)

1. **NONE for 14 days** → propose retirement (founder-gated kill, machine-drafted).
2. **META cost > GUARD+REVENUE cost** → `audit_status RED` (system grooming itself).
3. **Every loop must name `receipt_target`** — blank → flag rule 3.
4. **REVENUE lane gaps** — missing `gateway_outbound` Scheduler and executor or REVENUE loops with zero receipts → flag rule 4.

---

## Expected first-table diagnosis (confirmed 2026-07-06 first run)

First local census: `workflow-census-20260706T090917Z` · **37 loops** · `audit_status RED`

| Class | Count | Cost/mo |
|-------|------:|--------:|
| REVENUE | 2 | $5 |
| GUARD | 4 | $0 |
| META | 22 | $10 |
| NONE | 9 | $20 |

**Rule 4:** `gateway_outbound` Scheduler and executor **missing** — nothing sends offers.  
**Rule 2:** META+NONE spend > GUARD+REVENUE — system grooming itself.  
**Traffic row:** 11,250 visits/24h · **0 non-test leads** — funnel or bot question.

Fix remains UNLOCK §7: **25 offers out the door**.

---

## Run locally

```bash
python3 scripts/apply_workflow_census_migration_v1.py
python3 scripts/workflow_census_v1.py --write-receipt --write-supabase --traffic-visits-24h 11250
```

Requires `~/.sourcea-secrets/noetfield.env` (REST) and `noetfield-db.env` (migration).

---

## Integration path

- Census **RED on rule 2/4** → file Kaizen item (`machine_safe` consolidate/kill, `founder-gated` outbound)
- Heartbeat amendment (UNLOCK §6): merge `offers_sent · replies · L2_receipts` into census metadata
- Do **not** duplicate census in Mac launchd — GHA weekly on public SG repo

---

*Filed 2026-07-06 — judging layer over monitoring layer.*
