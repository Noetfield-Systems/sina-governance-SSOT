# LINE ENGINE — BLUEPRINT REGISTRY (govern blueprint explosion)

**Status:** Scaling-control mechanism. Source: Cloud Kernel v1.3 §7.
**First written:** 2026-07-03 12:34 PDT

## The problem
The biggest scaling risk is not the DB or cloud — it is **Blueprint Explosion**. 10 → 50 → 500 → 5,000 blueprints without a registry = uncontrollable versions, dependencies, guards, contracts.

## The 4 governing tables
| Table | Controls |
|---|---|
| `blueprint_versions` | Immutable history — every change is a new frozen version, never edit-in-place. |
| `blueprint_dependencies` | Acyclic dependency graph — a change surfaces every blueprint it affects. |
| `blueprint_tests` | Fixtures + last result — cannot promote to active with failing tests. |
| `blueprint_status` | Lifecycle gate (draft|testing|active|deprecated|frozen) — only `active` runs in prod. |

## The data hierarchy
```
Tenant (Org) → Project (Brand: Noetfield|Forge|TrustField|WitnessBC|777)
  → Factory (Pipeline: Board Review|Risk Scan|Ad Generator)
    → Blueprint (immutable, versioned contract) — governed by Blueprint Registry
      → Run (live execution instance)
        → Task (atomic node, MANDATORY idempotency_key)
          → Artifact | Evidence | Decision
```

## Relation
- Immutable-floor: versions are frozen, never edited — the registry is part of the floor.
- Content-identity: a frozen version = the committed==verified==shipped artifact.
- Merge-tiers: promotion to `active` is gated (tests must pass) — same as T0–T3.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. 4 registry tables (versions/dependencies/tests/status) + data hierarchy. From Kernel v1.3 §7–§8.*
