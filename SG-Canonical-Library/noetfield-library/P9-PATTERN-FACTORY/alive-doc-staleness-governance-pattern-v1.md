# PATTERN — ALIVE DOC & STALE POINTER GOVERNANCE v1

**Status:** SG governance law — stale ACTIVE pointers downgrade every venture to last week's mistakes.  
**First written:** 2026-07-07  
**Authority:** `data/agent_read_surfaces_v1.json` + `data/stale_law_guard_patterns_v1.json`

## What we learned

| Symptom | Root cause | Fix class |
|---------|------------|-----------|
| Agent repairs retired platform | ACTIVE law still names dead motor | Edit ACTIVE ssot/registry only |
| Deploy truth drift | Agent reads index not runtime_truth | Register deploy_truth in must_read |
| Missing skill path | AGENTS.md pointer stale | Fix agent_read_surfaces |
| Workflow motor ghost | File on disk, CF is primary | **Retire** motor — do not repair |
| Library index lie | LIBRARY_REGISTRY → missing file | Sync registry or restore file |

**Core insight:** Separate **alive** (ACTIVE), **index** (READ_SURFACE), **dead** (RETIRED). Machines inspect authority only — not P99 ledgers or form exports.

## Core pattern

```
register must_read surfaces per agent lane
  → scan ACTIVE authority roots
  → detect stale patterns + retired motors + missing paths
  → reason (repair_lane, action, priority)
  → write repair queue
  → receipt + weekly autorun
```

## Seven finding classes

| Class | Meaning | Typical action |
|-------|---------|----------------|
| missing_read_surface | Lane points at missing file | Restore file or update registry |
| missing_skill | Skill path broken | Fix skills_resolve |
| stale_law_pattern | Retired term in ACTIVE law | Replace pointer in ssot/data |
| retired_workflow_motor | Dead GHA motor on disk | Disable schedule — venture handoff |
| library_registry_drift | Index → missing file | Sync LIBRARY_REGISTRY |
| superseded_still_active | SUPERSEDED doc in ACTIVE scan | Demote status |
| unclassified | Other | Manual review |

## Reuse

- SG: full stack (`agent_read_staleness_engine_v1.py`)
- Ventures: register must_read in SG; fix handoffs from queue
- Never bulk-edit P99/form exports from this loop
