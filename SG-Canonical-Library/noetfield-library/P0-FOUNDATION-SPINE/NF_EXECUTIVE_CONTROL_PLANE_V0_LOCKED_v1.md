# NF-EXECUTIVE-CONTROL-PLANE-V0 — SG CONTROL LOCK

**decision_id:** `NF-EXECUTIVE-CONTROL-PLANE-V0`  
**title:** SourceA Executive Control Plane v0 (deterministic Executive Office)  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder order via Advisor doctrine (Executive Governor / Next Action Compiler)  
**Tier:** P0-FOUNDATION-SPINE (execution control law)  
**Version:** `v0.1.0_locked_20260724`  
**Machine:** `data/nf_executive_control_plane_v0_LOCKED.json`  
**Depends on:** `NF-GOVERNED-WORK-PACKET-CONTROL-V1` · `NF-DECISION-CAPACITY-V1` · `NF-MOTOR-LEARNING-ORGAN-V1` · `NF_FORBIDDEN_AGENT_REGISTERS_LOCKED_v1`  
**Applies to:** SourceA (kernel implement) · sina-governance-SSOT (lock + secretariat) · NOETFIELD-RUNWAY (consume later; not wired in v0)

---

## One-line law

> The always-present operator is a deterministic, memory-bearing Executive Governor — not an always-on LLM. Next prompts are compiled from state, not freely invented.

## Role separation (binding)

| Role | Actor | Authority |
|------|-------|-----------|
| Founder | human | charter, values, RED_ZONE, delegation envelope |
| SG | secretariat | Agenda, commitments tracking, Founder Decision Packets — does not code or mutate product files under this lock |
| Executive Governor | TS kernel | applies policy; emits exactly one DecisionResult; never executes work |
| Planner / Critic | external advisors | untrusted proposals only |
| Next Action Compiler | TS kernel | DecisionRecord → typed WorkPacket |
| Executor | Coding Agent / workflow | CapabilityGrant only |
| Verifier | TS kernel | ACCEPTED_ARTIFACT or failure — never trust agent-says-done |

## Core invariant

```text
Same State + Same Event + Same Policy Version = Same Decision
```

## Closed executive loop

```text
EVENT / TIMER
  → reconcile state
  → GoalController · CommitmentController · DriftMonitor
  → known Decision Class? PolicyEngine : AMBER/RED path
  → ConflictResolver
  → ExecutiveGovernor Decision
  → NextActionCompiler → WorkPacket
  → Executor (untrusted)
  → EvidenceVerifier
  → close Commitment or IncidentMotor → Learning Organ hook
```

## Decision zones

- **GREEN:** known policy · reversible · within budget · no protected state · no external commitment · verifier available → Governor may finalize.
- **AMBER:** bounded ambiguity · reversible · plan + critic evidence required · sandbox/canary + rollback → finalize only when review evidence present.
- **RED:** goal/governance change · legal · large finance · protected data · public positioning · irreversible · value conflict · unknown Decision Class → never finalize; emit Founder Decision Packet.

## Work packet terminal reuse

Terminals remain those of `NF-GOVERNED-WORK-PACKET-CONTROL-V1`:

1. `ACCEPTED_ARTIFACT`
2. `BOUNDED_FAILURE` + `INCIDENT_RECEIPT`
3. `RED_ZONE_DECISION_PACKET`

Never `ACTIVE_FOREVER`.

## Decision Capacity bridge

Repeated Founder micro-choices continue to open `MISSING_DECISION_CAPACITY` under `NF-DECISION-CAPACITY-V1`. Live policies (`WEBPAGE_CHANGE`, `WEBPAGE_REPAIR`) are GREEN DecisionPolicy inputs to this plane. GATED promote remains founder-authorized; cron cannot promote.

## Package home (v0)

SourceA: `packages/executive-control-plane-v0/` — TypeScript strict, no network, no LLM on decision path, in-memory repository, deterministic tests.

## Explicit non-goals (v0)

- Super-Agent / agent swarm / prompt chains / model routing
- Cloudflare Durable Object or live pulse (document pulse later; no background loops in v0)
- Wiring this package into Runway GoalDO
- Auto-promote remaining Decision Classes
- Unsupervised architecture redesign / base-model finetune

## Future pulse (document only)

| Item | Value |
|------|-------|
| Trigger host | `cloud` |
| Registry row | `loop_id=sourcea_executive_pulse_v0` |
| Deadman | SourceA deadman pattern (2× interval) |
| Receipt | `receipts/executive/` |

v0 ships **no** pulse motor.

## Forbidden

- LLM inside decision path
- Free-form next-step chat after capacity gap named
- Executor mutating canonical state
- Closing Commitment without required EvidenceReceipt
- Finalizing RED without Founder Decision Packet
