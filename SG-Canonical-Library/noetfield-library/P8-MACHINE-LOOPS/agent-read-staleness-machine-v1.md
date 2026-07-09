# MACHINE LOOP — AGENT READ STALENESS v1

**Pattern:** alive-doc governance (stale law = disaster)  
**First written:** 2026-07-07  
**Trigger host:** `cloud` (GHA weekly) + `founder-manual` on demand  
**Receipt lane:** `receipts/agent-read-staleness-*.json`

## Purpose

Machine-repeatable loop that inspects which docs/laws agents actually read, detects stale pointers (retired deploy surfaces, dead motors), and blocks authority surfaces from carrying retired law.

## Closed loop

```
Observe (registry + authority scan)
  → Detect (missing read surfaces, stale patterns, retired workflows)
  → Critique (BLOCKER vs WARN)
  → Repair (founder/agent fixes pointers in ACTIVE surfaces)
  → Re-deploy (re-run verify)
  → Observe (receipt + registry upsert)
```

| Phase | Script / artifact | Output |
|-------|-------------------|--------|
| Observe | `data/agent_read_surfaces_v1.json` | Per-lane must_read list |
| Detect | `scripts/agent_read_staleness_engine_v1.py` | Findings JSON |
| Critique | `data/stale_law_guard_patterns_v1.json` | BLOCKER/WARN classes |
| Repair | Edit ACTIVE ssot/registry only | Pointer refresh |
| Re-deploy | `scripts/verify_agent_read_staleness_v1.sh` | PASS receipt |
| Observe | `receipts/agent-read-staleness-*.json` | Closure token |

## Registry row

| Field | Value |
|-------|-------|
| `motor_id` | `gh_actions_agent_read_staleness_weekly_v1` |
| Cadence | Weekly Mon 09:00 UTC |
| `loop_id` | `sg-agent-read-staleness-v1` |
| Deadman | workflow failure alert |
| Receipt | `receipts/agent-read-staleness-*.json` |

## Law

- **ACTIVE** surfaces may not reference retired deploy motors.
- **READ_SURFACE** indexes are not deploy authority.
- Retired surfaces belong in `retired_deploy_surfaces`, not `owns` arrays.
