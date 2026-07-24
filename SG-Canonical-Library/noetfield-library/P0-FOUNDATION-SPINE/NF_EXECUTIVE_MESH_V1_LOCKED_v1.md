# NF-EXECUTIVE-MESH-V1 — SG CONTROL LOCK

**decision_id:** `NF-EXECUTIVE-MESH-V1`  
**title:** SourceA Executive Mesh v1 (deterministic kernel + Agentic Role Pods on production plane)  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder order via Advisor doctrine (Executive Mesh on existing CF / Railway / Supabase)  
**Tier:** P0-FOUNDATION-SPINE  
**Version:** `v1.0.0_locked_20260724`  
**Machine:** `data/nf_executive_mesh_v1_LOCKED.json`  
**Depends on:** `NF-EXECUTIVE-CONTROL-PLANE-V0` · `NF-DECISION-CAPACITY-V1` · `NF-GOVERNED-WORK-PACKET-CONTROL-V1` · `NF-MOTOR-LEARNING-ORGAN-V1`  
**Applies to:** SourceA (mesh + Governor Worker) · sina-governance-SSOT (lock) · NOETFIELD-RUNWAY (execution consumer for webpage-repair slice)

---

## One-line law

> Models deliberate inside Role Pods. Pods recommend typed packets. Only the Executive Governor commits canonical state. Verifiers determine reality. SSOT records the result.

## Composition (binding)

```text
SourceA =
    Deterministic Executive Kernel (ECP v0)
  + Agentic Role Pods (L0–L4 deliberation)
  + Governed Memory Fabric
  + Production Execution Plane (existing CF / Railway / Runway Goal Kernel)
  + Evidence & Promotion Plane
```

Do not choose between deterministic and agentic. Compose both. Do not invent a parallel SSOT, queue, or Railway executor.

## Authority boundary

| Actor | May |
|-------|-----|
| Models / Role Pods | Deliberate, retrieve, criticize, recommend |
| Executive Governor | Commit DecisionRecord; compile WorkPacket |
| Verifier | ACCEPTED / FAILED / INCIDENT |
| Supabase | Canonical authority for executive runs |
| Durable Object | Serialized coordinator cache only |
| Redis | Hot operational state only (not SSOT) |

Forbidden: LLM Authority; model self-promotion to CANONICAL; second Railway heavy executor; unbounded subagent fanout.

## Slice-1 vertical path

```text
EVENT → SG Pod → Memory ContextPack → Planner Pod → Critic Pod
  → Governor commit → Next Action Compiler → RUNWAY_GOAL_KERNEL
  → HDIR webpage-build-deploy → Independent verify → canonical commit → Digest
```

## Deliberation levels

| Level | Meaning |
|-------|---------|
| L0 | Deterministic policy only |
| L1 | Fast model + schema/evidence validation |
| L2 | Primary reasoner + independent critic |
| L3 | Multi-model council + integrator |
| L4 | Founder required |

Slice-1 requires L0; L1 optional behind flag. L2–L4 schemas may exist without being the required E2E path.

## Ops (cloud)

| Item | Value |
|------|-------|
| Trigger host | `cloud` |
| Registry row | `loop_id=sourcea_executive_pulse_v1` |
| Deadman | `sourcea-deadman-v1` |
| Receipt | `receipts/executive/` |

## Explicit non-goals (slice-1)

- Full nine-pod mesh beyond SG · Memory · Planner · Critic
- New vector database / second Supabase project
- Replacing GoalDO or HDIR
- Auto-promote remaining Decision Classes
- Mac-only 24/7 motor
