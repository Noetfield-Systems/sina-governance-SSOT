# Incident — SG-AUTHORITY-IDENTITY-P0

**Severity:** P0 governance / invalid authority chain  
**Opened:** 2026-07-18  
**Current:** `CONTAINMENT=ENFORCED`

## Finding

The Canonical Library exists, but no organization-owned deterministic SG authority runtime is commissioned. Legacy advisory App `4179901` / installation `143449507` is personal, non-authoritative, stale, and its latest receipt is `FAIL` with `pass_claimed=false`. `noetfield-motor` App `4275961` is a proven executor identity, not SG and not proof of Unified Motor Core commissioning.

## Runtime containment executed

- GitHub Actions workflow `brain-loop-autorun-v1` manually disabled.
- Active/queued runs checked; none existed to cancel. Scheduled run #178 had completed.
- Mac hold file created: `~/.sina/enforcement/brain-autonomous-hold-v1.flag`.
- Mac autonomous deploy and ship-window flags removed.
- `com.sina.brain-loop-autorun-v1` booted out.
- Legacy App retained for forensic continuity.

## Preserved evidence

Directory: `receipts/incidents/SG_AUTHORITY_IDENTITY_P0_20260718/`

- run #178 API metadata and artifact metadata
- downloaded run #178 receipt artifact
- latest legacy advisory receipt
- legacy Worker health response
- Cloudflare Worker deployment and version metadata

## Containment verdict

```text
SYSTEM_AUTHORITY_STATUS=BLOCKED_NOT_COMMISSIONED
SG_RUNTIME_STATUS=BLOCKED_STALE_IDENTITY
UNIFIED_MOTOR_STATUS=ARCHITECTURE_ONLY_NOT_COMMISSIONED
AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD
LEGACY_ADVISORY_AUTHORITY=DENIED
LEGACY_ADVISORY_APP=DECOMMISSION_PENDING
```

Allowed work is read-only observation, inventory, evidence, proposals, draft PRs, dry runs, lint/schema validation, and non-mutating shadow evaluation. Autonomous production mutation remains denied.
