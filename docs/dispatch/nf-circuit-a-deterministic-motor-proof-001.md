# Commission — Circuit A (deterministic internal Motor)

**commission_id:** `NF-CIRCUIT-A-DETERMINISTIC-MOTOR-PROOF-001`  
**Status:** `IMPLEMENTATION_AUTHORIZED`  
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

`CIRCUIT_A_PROVEN` or `CIRCUIT_A_BLOCKED_WITH_EVIDENCE`
