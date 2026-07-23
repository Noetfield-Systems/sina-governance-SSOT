# LIBRARY CUSTODY MATRIX — LOCKED v1

**Version:** v1.0.0_locked_20260710  
**Status:** LOCKED / RATIFIED  
**Authority:** Master SSOT §0.7 + D5 motor plane  
**Plane:** P2-SSOT custody law  

---

## Custody chain (binding)

```text
Master SSOT anchors
→ Library defines (P-layer)
→ NOOS operationalizes
→ Product runtime executes
→ Verifier proves
```

No layer may skip upstream custody. No layer may duplicate downstream operational specification into upstream law.

---

## Layer responsibilities

| Layer | Repo / path | Owns | Must NOT own |
|---|---|---|---|
| **Master SSOT** | `sina-governance-SSOT/ssot/strategy-ssot-v6-split.md` | Level 0 invariants; D1–D5 domain law; constitutional anchors (incl. §0.7) | Queue schemas, provider bindings, worker scripts |
| **Library P2** | `P2-SSOT/` | Custody matrix, authority graph, SSOT index, versioning law | Runtime dispatch code |
| **Library P7** | `P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` | Minted terms for receipts/jobs; tier disambiguation | Implementation details |
| **Library P8** | `P8-MACHINE-LOOPS/` | Continuation doctrine; escalation ≠ stop; park rules | API keys, deploy bindings |
| **Library P10** | `P10-PRODUCT-LAYERS/` | Cost-execution doctrine; commodity default; caps | Customer FinOps product copy (separate draft) |
| **NOOS integrator** | `noetfeld-OS/noetfield-org/` | Operational bindings, routing matrix, packet/result schemas, component registry | Constitutional redefinition |
| **Product runtime** | SourceA, TrustField, Noetfield, … | Private deployment bindings, loop scripts, receipt sinks | Alternate SSOT or custody law |
| **Verifier** | SG `check.py`, independent probes | External proof; author ≠ subject | Motor execution |

---

## Founder reasoning custody (§0.7)

| Artifact class | Custody owner | Canonical path |
|---|---|---|
| Invariant (99/1, no terminal handoff) | Master SSOT §0.7 + D5 | `ssot/strategy-ssot-v6-split.md` |
| Terminology | Library P7 | `P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` §11–§12 |
| Continuation doctrine | Library P8 | `P8-MACHINE-LOOPS/founder-reasoning-continuation-doctrine-LOCKED_v1.md` |
| Commissioning acceptance | Library P8 | `P8-MACHINE-LOOPS/MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md` |
| Cost-execution doctrine | Library P10 | `P10-PRODUCT-LAYERS/COST_EXECUTION_DOCTRINE_LOCKED_v1.md` |
| Operational binding (full spec) | NOOS | `noetfeld-OS/noetfield-org/FOUNDER_REASONING_MOTOR_OPERATIONAL_BINDING_v1.md` |
| Motor JSON schemas | NOOS | `noetfeld-OS/noetfield-org/schemas/` |
| Authority pins | NOOS | `noetfeld-OS/noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json` |
| Wiring receipt | SG receipts | `receipts/custody/CUSTODY_WIRING_FOUNDER_REASONING_v1.json` |
| Option C absorption receipt | SG receipts | `receipts/custody/CUSTODY_ABSORPTION_ADVISOR_PACKAGE_OPTION_C_v1.json` |

---

## Tier namespace law (disambiguation)

Three tier systems coexist. **Never use bare `T0` in receipts.**

| Prefix | Domain | Example |
|---|---|---|
| `MERGE-T0`…`MERGE-T3` | Merge authority (P8) | docs auto-merge vs founder-only governance |
| `EXEC-T0`…`EXEC-T3` | Executor routing (NOOS ROUTING_MATRIX) | GHA vs Copilot vs Cursor vs Codex |
| `COST-T0`…`COST-T2` | Motor cost lanes (P10) | deterministic → cheap API → bounded API |

---

## Invalid patterns (rejected in receipts)

- `HANDOFF_REQUIRED` without `packet_id` and queue stage
- Bare `T0` / `T1` / `T2` without prefix
- Premium API as standing automatic worker
- Terminal stop after cheap-route failure (must queue or park with continuation contract)
- Operational spec pasted into Master SSOT or Library as if constitutional

---

*v1.0.0_locked_20260710 — custody chain installation for founder reasoning motor.*
