# Commission — Circuit A (deterministic internal Motor)

**commission_id:** `NF-CIRCUIT-A-DETERMINISTIC-MOTOR-PROOF-001`  
**Status:** `CIRCUIT_A_PROVEN`  
**Proven at:** `2026-07-18T01:09:30Z`  
**Evidence:** NOOS `receipts/proof/nf-circuit-a-deterministic-motor-proof-001-v1.json` · job `MOTOR-CIRCUITA-001` · SG authority `d2c2e6ab9de8d91179aed694abac649866950b33` · NOOS main `291789bc3d40dad8ea165f68a29ff026a000bd26`  
**Depends on:** Unified Motor foundation / Gateway v2 drafts as available; Issue/CI ownership may remain `NOT_WIRED` for automatic routing — prefer receipt-writer path if CI ownership not ratified  
**Target:** builders / sandbox + NOOS route  
**Deploy:** only if job recipe already authorizes bounded non-production proof; **no production weaken**

## Objective

One complete T0 Motor job with before/after evidence and P99 receipt without founder mid-job management.

## Preferred first job

`receipt_writer_completion_evidence_repair` → `NF-MOTOR-RECEIPT-WRITER-REPAIR-001`

Fallback: CI repair recipe only when Issue Manager / CI Reliability ownership is SG-ACTIVE.

## Success criteria

- no Sina intervention mid-job  
- no runtime restart  
- no test weakening  
- no missing evidence  
- exact before/after result  
- seven truth dimensions populated  

## Final status

`CIRCUIT_A_PROVEN`

Live T0 path: `DISPATCHING_COMPLETION_UNPROVEN` → keyed evidence-sink repair (cycle 1351) → observer before/after PASS → recovery PROVEN. No founder mid-job, no runtime restart, no test weakening. Organic writer-B cron recovery is **not** claimed (lifecycle remains `POST_VERIFYING`).
