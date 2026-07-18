# MACHINE LOOP — SG AUTH SURFACE PROBE v1

**Pattern:** cross-domain auth verification (SG verifies; ventures implement UI)  
**First written:** 2026-07-08  
**Trigger host:** `cloud` (GHA every 6h) + `founder-manual` on demand  
**Receipt lane:** `receipts/auth-surface-probe-*.json`

## Purpose

Tiered HTTP probe of live auth surfaces + Supabase identity plane. Ensures contract SKUs stay public (tier-0), gated routes enforce auth when live, and redirect allow-list matches venture domains.

## Closed loop

```
Observe (auth_surface_matrix + live URLs)
  → Detect (tier-0 FAIL, login-wall, gated public 200 when live)
  → Critique (PASS / WARN / FAIL)
  → Repair (venture repo ships gate or SG matrix update)
  → Re-deploy (venture deploy)
  → Observe (probe receipt + GHA artifact)
```

| Phase | Script / artifact | Output |
|-------|-------------------|--------|
| Observe | `data/auth_surface_matrix_v1.json` | Tier 0–3 surface list |
| Detect | `scripts/verify_auth_surfaces_e2e_v1.py` | Per-surface status |
| Critique | tier-0 FAIL blocks; WARN for planned gates | overall status |
| Repair | `docs/dispatch/auth-phase-*.md` venture chats | Product PR |
| Re-deploy | venture CI deploy | live gate |
| Observe | `receipts/auth-surface-probe-*.json` | Closure token |

## Registry row

| Field | Value |
|-------|-------|
| `motor_id` | `gh_actions_sg_auth_surface_probe_v1` |
| `loop_id` | `sg_auth_surface_probe_v1` |
| Cadence | `0 */6 * * *` (6h) |
| Deadman | `sourcea-deadman-v1` at 2× interval (12h) — pending LS-075 loop_registry upsert; workflow remains cloud-live and receipt-backed until the shared registry sink lands |
| Receipt | `receipts/auth-surface-probe-*.json` |
| Value class | GUARD |

## Law

- Tier-0 public pages must never redirect to sign-in.
- `getClaims()` on server — not `getSession()` alone (venture implementers).
- SG never ships auth UI.
- One venture per PR.
