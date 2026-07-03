# NOOS integrator rules v1

**Status:** LOCKED — SG mirror  
**Saved:** 2026-07-03  
**Authority:** SG (SSSOT) routes; **canonical** in `noetfeld-os`  
**Canonical protocol:** `~/Projects/noetfeld-os/docs/_NOOS_AGENT/[NOOS-AGENT-20260703-001]_INTEGRATOR_AGENT_PROTOCOL_v1.md`  
**Machine SSOT:** `~/Projects/noetfeld-os/data/noos-integrator-role-v1.json`

Applies to **any agent/IDE/session** that mutates NOOS integrator state (claim, complete, heartbeat, task open, agent register).

---

## Three laws (non-negotiable)

### 1. Local session exit

Any agent/IDE/session that **changes integrator state** must run integrator sync before stopping.

```bash
cd ~/Projects/noetfeld-os
python3 scripts/noos_integrator_sync_v1.py sync --agent-id <agent_id>
# or full closeout:
python3 scripts/noos_integrator_sync_v1.py session-exit --agent-id <agent_id>
# or:
make local-closeout TASK=<task_id> AGENT_ID=<agent_id> IDE=cursor
```

**SG / SourceA / TrustField sessions:** if you did **not** touch integrator state, sync is not required.

Violations → `BLOCKED_WITH_REASON` on next NOOS lane claim (machine loop, not founder).

### 2. Cloud owner

Cloud integrator ownership belongs **only** to the configured NOOS automation/orchestrator for that repo.

| Field | Path |
|-------|------|
| Config | `noetfeld-os/data/noos-integrator-role-v1.json` → `cloud_owner` |
| Owner workflow (when enabled) | `noos-cross-repo-orchestrator` |

If `cloud_owner.enabled` is **false** (current default):

- **Repo-local** `.noos-runtime/integrator/noos-integrator-state-v1.json` is authoritative
- Supabase / cloud mirror **writes are blocked** for IDE agents
- Only read replicas unless operator explicitly promotes

Agents must **not** write integrator state to Supabase or cloud paths without matching `owner_agent_id`.

### 3. Mirror

| Layer | Path | Role |
|-------|------|------|
| **Primary truth** | `.noos-runtime/integrator/noos-integrator-state-v1.json` | Mutable coordination state |
| **Home mirror** | `~/.sina/noos-integrator-state-v1.json` | Shared local copy for other worktrees/IDEs |
| **Optional cloud** | Supabase `noos_integrator_agent_state` | Observer/mirror only when cloud owner enabled |

Home mirror is a **shared local coordination copy**, not primary truth unless explicitly promoted.

---

## Truth order (integrator domain)

1. Repo-local runtime state (current checkout)  
2. Tracked protocol JSON (`data/noos-integrator-role-v1.json`)  
3. Home mirror (read for cross-worktree visibility)  
4. Supabase row (if enabled and cloud owner active)  
5. Chat / session memory (never authority)

---

## SG agent note

SG (`sg_sssot_cursor`) does **not** own integrator writes. When dispatch touches NOOS integrator:

- Open **noetfeld-os** chat or run commands there
- End session with `sync` or `session-exit`
- Do not mirror integrator state into SG repo

Cross-link: [FOUNDER_CANON_v1.md](FOUNDER_CANON_v1.md) §9 Truth & memory · [MACHINE_AUTONOMY_LOOPS_v1.md](MACHINE_AUTONOMY_LOOPS_v1.md) L7 receipt proof
