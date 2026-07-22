# Dispatch — wake-path conflict policy (all repos)

**Authority:** `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_WAKE_PATH_CONFLICT_POLICY_LOCKED_v1.md`  
**Machine:** `data/nf_wake_path_conflict_policy_v1_LOCKED.json`  
**decision_id:** `NF-WAKE-PATH-CONFLICT-POLICY-V1`  
**Status:** `SG_ACCEPTED`

## One-liner (paste into any agent session)

```text
Wake path: event-driven authenticated HTTP job_id → Worker → Workflow → receipt → sleep is DEFAULT (Cloudflare Workers first). Cron / Workflow schedule / Railway poll / GHA schedule ALLOWED when schedule passport exists. Do NOT emit MOTOR_PRODUCTION_PATH_BLOCKED solely because scheduled() exists. Missing passport = WARN_SCHEDULE_PASSPORT_MISSING (require passport PR). Hard ban remains: GHA unpaid continuous product muscle, feature-branch CI spam, idle LLM ticks. HOLD preserved. Cite NF-WAKE-PATH-CONFLICT-POLICY-V1.
```
