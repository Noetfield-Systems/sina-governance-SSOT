# NOOS Integrator Sync Rule v1 (package slice)

**Status:** ACTIVE — SG package mirror  
**Layer:** P2 (SSOT / integrator plane)  
**SG canonical:** `ssot/NOOS_INTEGRATOR_RULES_v1.md`  
**Package:** `noos-control-desk-v1`

## Law

Every session that **mutates integrator state** must sync at exit. Founder is never the sync owner.

| Owner | Scope |
|-------|-------|
| Repo-local | `python3 scripts/noos_integrator_sync_v1.py sync` in owning repo |
| Home mirror | `~/.sina/noos-integrator-state-v1.json` (read/coordination) |
| Cloud | GitHub Actions / Cloudflare / NOOS cloud runner when `cloud_owner.enabled` |

## Session exit (mandatory when state changed)

```bash
python3 scripts/noos_integrator_sync_v1.py sync
python3 scripts/noos_integrator_sync_v1.py summary --json
```

## Truth order

1. Repo-local runtime state  
2. Tracked protocol JSON  
3. Home mirror  
4. Cloud mirror (if enabled)  
5. Chat memory (never authority)

## Control Desk integration

Tile **NOOS Integrator Sync** invokes sync + summary; writes receipt per `receipt_schema_v1.json`.  
Does not perform cost audit or UI attestation — integrator lane only.
