# NF-DECISION-CAPACITY-V1 — SG CONTROL LOCK

**decision_id:** `NF-DECISION-CAPACITY-V1`  
**title:** Decision Capacity (gap → proposal → policy candidate → Learning Organ replay)  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder order via Advisor doctrine (organizational OS / Decision Frontier)  
**Tier:** P0-FOUNDATION-SPINE (decision substrate)  
**Version:** `v1.0.0_locked_20260724`  
**Machine:** `data/nf_decision_capacity_v1_LOCKED.json`  
**Schemas:** `data/schemas/decision_capacity_gap_v1.json` · `decision_capacity_proposal_v1.json` · `decision_policy_candidate_v1.json`  
**Depends on:** `NF-GOVERNED-WORK-PACKET-CONTROL-V1` · `NF-MOTOR-LEARNING-ORGAN-V1`  
**Applies to:** SourceA · NOETFIELD-RUNWAY · sina-governance-SSOT

---

## One-line law

> Human Tax that names repeated founder micro-choices must become Decision Capacity — not another chat turn.

## Closed path (binding)

```text
MISSING_DECISION_CAPACITY
      ↓
Decision Capacity Gap (which choices repeated)
      ↓
Decision Capacity Proposal (versioned policy draft)
      ↓
Decision Policy Candidate (OPEN mutation)
      ↓
Motor Learning Organ learning_record (draft → shadow → ratify)
      ↓
Verified promotion (GATED) · future autonomous decisions
```

Forbidden shortcuts:

- Asking “what do you want to do next?” after capacity gap is named
- Promoting candidate to live without Learning Organ shadow/replay
- Letting Coding Agent or Advisor write Policy Registry directly
- Treating token spend or workflow count as capacity growth

## Decision Classes (initial)

`EMAIL_DRAFT` · `WEBPAGE_CHANGE` · `WEBPAGE_REPAIR` · `CRAWL_AND_EXTRACT` · `DATA_SYNC` · `DEPLOYMENT`

Each class ships a policy template with: `when` · `select` · `limits` · `verify` · `escalate_when`.

## Capacity gap trigger

Emit `MISSING_DECISION_CAPACITY` when Governed Work Packet soft/hard tax patterns show repeated founder micro-choices (map from Human Tax events) and `existing_policy_coverage <` high threshold.

Work packet state: `FROZEN`. Incident route: `CREATE_OR_EXTEND_POLICY`.

## Learning Organ seam

Policy candidates enter as `learning_record` with:

- `layer`: `policy`
- `status`: `draft`
- `mutation_class`: `OPEN`
- `source_event`: `MISSING_DECISION_CAPACITY`

Promotion to live priors remains `GATED` per `NF-MOTOR-LEARNING-ORGAN-V1`.

## Metrics (observe)

| Metric | Direction |
|--------|-----------|
| Policy Coverage | ↑ |
| Decision Reuse Ratio | ↑ |
| Founder Translation Rate | ↓ |
| Human Tax per Accepted Outcome | ↓ |
| Autonomous Closure Rate | ↑ |

## Non-goals

- Base-model fine-tune / LoRA in this lock
- Unsupervised architecture redesign
- Advisor with execution authority
- Auto-merge of policy candidates to production SSOT
