# ARCHITECTURE FINALIZATION GATE — LOCKED v1

**Status:** LOCKED · ACTIVE  
**Authority:** SG (SSSOT) — constitutional finalization law  
**Tier:** P8-MACHINE-LOOPS (acceptance / finalization law; not a Motor kernel)  
**Version:** v1.0.0_locked_20260717  
**Machine:** `data/architecture_finalization_gate_v1_LOCKED.json`  
**Decision id prefix:** `NF-*` architecture decisions finalized under this gate  

---

## Canonical authority chain

```text
Founder intent
→ Brain/Architect design
→ Technical evaluation
→ SG finalization
→ Canonical authority SHA
→ Implementation
→ Evidence
→ P99 preservation
```

### Permanent rule

> No major architecture is final merely because it was designed, an advisor recommended it, or a Builder implemented it. It becomes Noetfield architecture only after Sina Governance SSOT validates and records it.

### Role separation

| Layer | Responsibility |
|-------|----------------|
| Founder + Brain/Architect | Objective, design, compare alternatives, propose architecture |
| Advisors | Challenge assumptions; specialist analysis |
| SG | Validate alignment, authority, invariants, P0–P99 consequences; make the decision canonical |
| NOOS | Operationalize, schedule, observe, route approved architecture |
| Motor | Execute approved recipes under the SG authority contract |
| Builders | Implement bounded changes |
| P99 | Preserve decisions, evidence, outcomes, institutional memory |

Neither an advisor, Claude, Codex, Cursor, Fable, nor NOOS may independently redefine Noetfield’s canonical architecture.

### One-line law

> The Brain designs. SG constitutionalizes. NOOS operationalizes. The Motor executes. P99 remembers.

---

## Status vocabulary (binding)

```text
ARCHITECTURE_DRAFT
→ SG_REVIEW_REQUIRED
→ SG_ACCEPTED
→ IMPLEMENTATION_AUTHORIZED
→ IMPLEMENTED
→ OPERATIONALLY_PROVEN
→ P99_PRESERVED
```

Rejection / terminal alternate states:

```text
SG_REJECTED
SG_CONFLICT
SG_REVISION_REQUIRED
SUPERSEDED
```

Before `SG_ACCEPTED`, agents must not call a decision:

- canonical
- locked (as architecture)
- final
- authoritative
- Noetfield-wide policy

It is only a **proposed architecture**.

---

## Required packet: SG Architecture Finalization Packet

Every major design must produce a packet containing at least:

```yaml
decision_id:
title:
status: PROPOSED | SG_REVIEW_REQUIRED | SG_ACCEPTED | …

founder_intent:
problem:
scope:
non_goals:

architecture:
components:
responsibility_boundaries:
data_flows:
authority_flows:
execution_flows:

p0_core_alignment:
protected_invariants:
forbidden_states:
founder_only_actions:
machine_safe_actions:

p0_to_p99_impact:
  p0:
  p1_p9:
  p10_p98:
  p99:

security:
privacy:
data_sovereignty:
secrets:
model_policy:
sandbox_policy:

operational_model:
failure_modes:
recovery:
rollback:
evidence_requirements:

dependencies:
vendor_boundaries:
portability:
cost_boundaries:

migration:
existing_systems_preserved:
superseded_components:
compatibility:

implementation_waves:
acceptance_conditions:

open_questions:
risks:

proposed_by:
reviewed_by:
sg_decision:
sg_authority_sha:
effective_at:
supersedes:
```

---

## SG must answer (before ACTIVE)

1. Does it preserve the P0 core?
2. Does it conflict with an existing ACTIVE decision?
3. Which prior decisions become superseded?
4. Who has authority at each stage?
5. Which operations are machine-safe?
6. Which operations remain founder-only?
7. What data, secrets, and production boundaries exist?
8. How does evidence move into P99?
9. What is the rollback path?
10. Exact SG SHA that authorizes implementation?

---

## Cross-repo projection rule

Other repositories must not duplicate the full architecture.

They receive only a generated pointer:

```json
{
  "schema": "noetfield.sg-authority-ref.v1",
  "decision_id": "<DECISION_ID>",
  "authority_source": "Noetfield-Systems/sina-governance-SSOT",
  "authority_sha": "<canonical-sg-sha>",
  "status": "ACTIVE",
  "generated": true
}
```

SG remains the source. Every other repository receives only the projection.

---

## Scope of major architecture

This gate applies to significant architecture including:

- Unified Motor Core and Motor profiles
- NOOS control-plane changes
- SourceA dispatch architecture
- Resident Role owners
- Model Router / open-model policy
- Sovereign AI posture
- SandboxAdapter authority
- P99 evidence routes
- Customer Motor commissioning

Routine scoped fixes, copy locks, and recipe patches do not require a full finalization packet unless they redefine system boundaries.

---

## Relation to Motor commissioning

| Law | Plane | Proves |
|-----|-------|--------|
| This gate | Constitutional finalization | Architecture may be called ACTIVE |
| `MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md` | Cold operational proof | Motor may be called `FULLY_COMMISSIONED` |

`SG_ACCEPTED` ≠ `FULLY_COMMISSIONED`. Design lock ≠ operational proof.
