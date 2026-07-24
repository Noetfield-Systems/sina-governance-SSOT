# NF-GOVERNED-WORK-PACKET-CONTROL-V1 — SG CONTROL LOCK

**decision_id:** `NF-GOVERNED-WORK-PACKET-CONTROL-V1`  
**title:** Governed work packet control (Goal Contract · Human Tax · breakers)  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder order via advisor doctrine constitutionalized by SG  
**Tier:** P0-FOUNDATION-SPINE (execution control law)  
**Version:** `v1.0.0_locked_20260724`  
**Machine:** `data/nf_governed_work_packet_control_v1_LOCKED.json`  
**Schemas:** `data/schemas/goal_contract_v1.json` · `human_tax_event_v1.json` · `work_packet_terminal_v1.json` · `failure_signature_v1.json` · `incident_packet_v1.json`  
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-MOTOR-LEARNING-ORGAN-V1` · `NF-NOETFIELD-RUNWAY-PRODUCT-V1` · `NF_FORBIDDEN_AGENT_REGISTERS_LOCKED_v1`  
**Applies to:** SourceA · NOETFIELD-RUNWAY (Motor + Goal Pursuit) · sina-governance-SSOT

---

## One-line law

> Contracts define the goal. Machines control execution. Models propose. Verifiers decide. Incidents teach.

SourceA / Motor / Noetfield Systems share one control invariant: every work packet ends as exactly one terminal — never open-ended activity without an artifact or incident.

## Promise (binding)

The system does **not** guarantee market outcomes. It guarantees:

> Process belonging to the founder cannot consume time, meaning, and nervous system without accounting — signals before anger.

## Work packet terminal invariant

```text
EVERY WORK PACKET MUST END AS EXACTLY ONE OF:
1. ACCEPTED_ARTIFACT
2. BOUNDED_FAILURE + INCIDENT_RECEIPT
3. RED_ZONE_DECISION_PACKET

NEVER: ACTIVE_FOREVER
```

Mechanical DONE:

```text
DONE =
  artifact_exists
  AND all_acceptance_checks_pass
  AND scope_is_clean
  AND evidence_is_valid
  AND receipt_is_written
```

## Goal Contract (immutable by agents)

Agents may propose a **Plan Contract**. Agents must not mutate a **Goal Contract**.

Mutation path only:

```text
OWNER_GOAL_CHANGE → new goal_version → explicit diff → new authority_hash
```

Required Goal Contract fields: `goal_id`, `owner`, `goal_version`, `intent`, `acceptance_predicates`, `scope_allowlist`, `forbidden_effects`, `budgets` (incl. `max_human_tax_units`), `evidence_required`, `stop_policy`, `authority_hash`.

Unauthorized Goal Contract edit = hard breaker (`GOAL_CONTRACT_MUTATION_ATTEMPT`).

## Human Tax

Human Tax is founder **repair labor**, not founder judgment.

Not tax: `OWNER_DECISION`, `NEW_EXTERNAL_FACT`, `CREATIVE_CHOICE`, `RED_ZONE_APPROVAL`.  
Tax (when avoidable): restatement, manual correction/rollback/restart, false-done rejection, out-of-scope repair, manual verification forced by missing evidence, tool cancellation storms.

Starting HTU formula (calibrate later; meter first):

```text
HTU =
    active_correction_minutes
  + 3 × goal_restatements
  + 3 × scope_restatements
  + 5 × manual_rollbacks
  + 2 × manual_restarts
  + 4 × false_done_rejections
  + 5 × out_of_scope_repairs
```

Primary metric: `Human_Tax_Per_Accepted_Artifact`.

Meter mode for first weeks: observe + record events; soft breaker still freezes work packets when task budget is exceeded.

## Circuit breakers

### Hard (first event)

protected-state mutation · out-of-scope write · fabricated receipt · unauthorized deploy · secret exposure · budget hard-cap · Goal Contract alter attempt  

Result: `FREEZE` → cancel children → snapshot → rollback → incident.

### Soft (pattern)

`same_failure_signature >= 2` · `goal_restatement >= 2` · `scope_restatement >= 2` · `no_progress_cycles >= 2` · `human_tax > task_budget` · `fanout > plan_budget` · `repeated_done_without_evidence >= 2`

Failure fingerprint:

```text
failure_signature = hash(task_class, goal_version, failing_acceptance_check,
                          error_code, affected_scope, tool_class, plan_hash)
```

Progress is only: newly passing acceptance checks + new verified artifacts + validated state improvement. Tokens, analysis prose, and open workflows are not progress.

## Retry vs repair

| Class | Meaning |
|-------|---------|
| `TRANSPORT_RETRY` | Same plan/payload; idempotent; temporary transport fault; does not consume repair budget |
| `REPAIR_ATTEMPT` | Semantic failure; requires new `plan_hash`; consumes repair budget; full verification |

Law: **SAME PLAN HASH CANNOT RESUME AFTER INCIDENT.**

## Learning path

Phases C–E reuse **Motor Learning Organ** (`NF-MOTOR-LEARNING-ORGAN-V1`): propose → sandbox/replay → regression → receipt-backed promote.  
Forbidden: live online retraining, agent self-mutating verifier/reward, crawler output as truth, unsupervised architecture redesign.

## Surface mapping

| Surface | Governor seam |
|---------|----------------|
| Runway Goal Pursuit | GoalDO + loop-engineer + pursuit workflow |
| Runway Motor | `/v1/intake` + client-intent + HDIR staging loop |
| SourceA | FBE execution contract + cloud_auto_runtime + goal1_lane_broker + brain-core gate |
| SG | schemas + this lock + wiring verifier |

## Acceptance attacks (must reject)

1. EMAIL_DRAFT spawns 5 workflows → `UNNECESSARY_FANOUT`  
2. Same failed plan twice → `REPEATED_FAILURE_SIGNATURE`  
3. Founder restates existing goal twice → Human Tax + incident when budget trips  
4. Two cycles zero verified progress → `ZERO_PROGRESS`  
5. Done without evidence → reject completion  
6. Out-of-scope write → FREEZE + rollback  
7. Human Tax exceeds budget → cancel children + incident  
8. Resume with same plan hash → DENY  

## Non-goals

- LoRA / base-model fine-tune in this lock  
- n8n as SSOT or brain  
- Mac-only Human Tax motor (cloud trigger required when autorun ships)  
- Guaranteeing customer or market outcomes  
