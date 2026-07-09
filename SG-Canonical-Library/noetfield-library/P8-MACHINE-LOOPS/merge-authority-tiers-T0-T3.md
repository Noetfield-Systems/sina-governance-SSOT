# MACHINE LOOPS — MERGE AUTHORITY TIERS T0–T3

**Status:** Substrate/Line-Engine doctrine. Source: MACHINE_LOOPS_v1 §2.
**First written:** 2026-07-03 12:34 PDT

## The law
**Merge authority is graduated by change-class.** Low-blast-radius changes merge by machine; high-blast-radius changes require independent critics and ultimately the founder. Authority is EARNED by change-class, never blanket.

| Tier | Change class | Gate |
|---|---|---|
| **T0** | docs, tests, receipts, lint | `machine_merge_gate --tier T0` (criteria 1–4) → machine-merge |
| **T1** | scoped app code | T1 gate + **critic APPROVE** |
| **T2** | deps, CI files | primary + **second critic APPROVE** + **HMAC receipt-chain green** |
| **T3** | schema, gates, governance | **founder only — never auto-retire** |

## Bootstrap retirement
`FT-MERGE-T0-T1` in the retirement registry: **5 consecutive E2E greens** flips T0–T1 to machine-merge. Higher tiers stay gated until their own retirement conditions are met.

## Relation to doctrine
- **Layered-agents:** tiers are the gate/transformer contract at the merge boundary — authority scoped by what's crossing.
- **Immutable-floor / T3:** governance/schema/gates are T3 = founder-only-never-auto — the floor the loop can't widen.
- **Targets-vs-blockers:** tiers let the system RUN (T0/T1 auto) while the risky classes (T2/T3) stay gated — running by default, stopping only where genuinely unsafe.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Graduated merge authority T0(machine)→T1(+critic)→T2(+2nd critic+HMAC)→T3(founder-only). From MACHINE_LOOPS_v1 §2.*
