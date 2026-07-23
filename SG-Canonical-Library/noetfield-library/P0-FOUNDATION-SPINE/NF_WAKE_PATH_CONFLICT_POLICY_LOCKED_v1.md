# NF-WAKE-PATH-CONFLICT-POLICY-V1 — Motor / API wake-path auto-conflict policy

**decision_id:** `NF-WAKE-PATH-CONFLICT-POLICY-V1`  
**title:** Wake-path conflict policy v1 (event-driven default; schedule allowed with passport)  
**Status:** `SG_ACCEPTED`  
**Authority:** Founder order constitutionalized by SG  
**Tier:** P0-FOUNDATION-SPINE (rewrite locked)  
**Version:** `v1.0.0_locked_20260720`  
**Machine:** `data/nf_wake_path_conflict_policy_v1_LOCKED.json`  
**Amends interpretation of:** `NF-COMPUTE-ROI-ALLOCATION-V1` job wake law  
**Does not cancel:** enterprise plan · ROI classes A–D · Cloudflare Workers first hot path  
**Does not activate:** `AUTONOMOUS_PRODUCTION_MUTATIONS=RUN` · unsupervised promote  
**effective_at:** 2026-07-20  
**proposed_by:** Founder  
**sg_decision:** `SG_ACCEPTED`

---

## founder_intent

Event-based wake and Cloudflare Workers first is the **default**, not a strict ban that blocks cron or Workflow schedules when they are needed.

one_line_law:

> Event-driven authenticated HTTP `job_id` wake is default; cron / Workflow / poll / GHA schedule are allowed when a schedule passport exists — never invent `MOTOR_PRODUCTION_PATH_BLOCKED` solely because a schedule exists.

## amends

This lock **amends the interpretation** of `NF-COMPUTE-ROI-ALLOCATION-V1` job wake law:

- Default remains: authenticated HTTP `job_id` → Workflow → receipt → sleep; Cloudflare Workers first for the hot path.
- Schedules are **not** an automatic production-path block.
- Enterprise plan, ROI minute classes A–D, and hard bans on unpaid continuous GHA product muscle / feature-branch CI spam / idle LLM ticks remain in force.

It does **not** cancel or replace `NF-COMPUTE-ROI-ALLOCATION-V1`.

## default_wake_path

```text
authenticated HTTP job_id wake
  → Cloudflare Worker (hot path first)
  → Cloudflare Workflow (if multi-step)
  → receipt
  → sleep
```

Prefer this path whenever a product job wake can use `job_id` HTTP.

## allowed_exceptions

When a **schedule passport** is present (fields below), these hosts may schedule:

| Host | Example use |
|------|-------------|
| Cloudflare cron (`scheduled()`) | Deadman, heal tick, complement to event path |
| Cloudflare Workflow schedules | Multi-step heal / observe loops |
| Railway poll | Heavy / long workers that cannot hold event edge |
| GitHub Actions `schedule` | ROI-class gated CI / founder-manual / canary — not continuous unpaid product muscle |

## hard_ban_remains

Still forbidden (unchanged from compute ROI law):

- GitHub Actions as continuous unpaid product muscle without an ROI class
- Feature-branch CI spam against the 50k minute budget
- Idle LLM ticks / health-model cron that burns tokens with no job

## schedule_passport

Required fields for any **new or kept** schedule (CF cron, Workflow schedule, Railway poll, GHA schedule):

| Field | Meaning |
|-------|---------|
| `purpose` | What the schedule does |
| `expected_value` | Why it exists (revenue, heal, deadman, verify) |
| `estimated_monthly_cost_or_minutes` | Cost or Actions minutes estimate |
| `frequency` | Cadence |
| `why_not_event_driven` | Why HTTP `job_id` / event wake alone is insufficient |
| `why_not_manual` | Why founder-manual / `workflow_dispatch` alone is insufficient |
| `fallback` | What runs if the schedule misses |
| `stop_condition` | When to disable the schedule |
| `owner_loop_id` | Registry / loop owner id |

Missing passport → `WARN_SCHEDULE_PASSPORT_MISSING` (require passport PR). Do **not** invent `MOTOR_PRODUCTION_PATH_BLOCKED`.

## agent_conflict_resolution_table_AUTO

| Situation | Verdict |
|-----------|---------|
| Cron exists + passport present + HOLD preserved | `PASS_ALLOW_SCHEDULE` — do not block production path for "event-only" |
| Cron exists + no passport | `WARN_SCHEDULE_PASSPORT_MISSING` — require passport PR; do not invent `MOTOR_PRODUCTION_PATH_BLOCKED` |
| Merge conflict markers on main | `BLOCKED_MERGE_MARKERS` — fix YAML/code first (separate from wake policy) |
| Agent claims event-only forbids all cron | `REJECT` — cite this lock; default ≠ absolute ban |
| Product job wake without `job_id` HTTP when one exists | Prefer event path; cron may complement for deadman/heal only |

## forbidden_agent_behavior

- Treating empty-cron as sacred forever
- Blocking founder-authorized commercial loops solely for having `scheduled()`
- Emitting `MOTOR_PRODUCTION_PATH_BLOCKED` solely because cron / Workflow schedule / Railway poll / GHA schedule exists
- Claiming "event-only" as an absolute ban on all schedules

## holds_preserved

- `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`
- Promote / production mutation remains founder-gated
- Agents may observe, draft, test, open PRs, and apply this auto table; they may not lift HOLD

## relation_to_prior_locks

- Interprets `NF-COMPUTE-ROI-ALLOCATION-V1` wake default without canceling Enterprise / ROI classes
- Complements unified Motor architecture: Cloudflare Workers + Workflows remain hot path
- Does not authorize unsupervised promote or continuous unpaid GHA product muscle

## sg_decision

`SG_ACCEPTED` under founder order 2026-07-20.
