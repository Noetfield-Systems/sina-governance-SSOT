# NF-SG-AUTHORITY-IDENTITY-V2 — FOUNDER CONTAINMENT AMENDMENT

**decision_id:** `NF-SG-AUTHORITY-IDENTITY-V2`  
**Status:** `FOUNDER_DIRECTIVE_ACCEPTED` · `CONTAINMENT_IMPLEMENTATION_AUTHORIZED`  
**Runtime status:** `NOT_COMMISSIONED`  
**Version:** v1.0.0_locked_20260718  
**Machine:** `data/nf_sg_authority_identity_v2_LOCKED.json`  
**Runtime truth:** `data/runtime_reality_v1.json`

## Binding correction

The historical `repository_identity.app_count = 1` in `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` is semantically superseded. It meant one canonical Motor execution App; it may not collapse executor and authority credentials.

```text
motor_execution_app_count = 1
sg_authority_app_count = 1
total security principals = 2
```

`noetfield-motor` is a proven Motor executor identity. It is not SG authority and is not proof that Unified Motor Core is commissioned. The future `noetfield-sg-authority` App is a deterministic authority identity and may not execute repository or production mutations.

## Authority chain

```text
Brain / NOOS proposes
→ canonical request + evidence
→ deterministic SG evaluates
→ exact signed permit
→ Motor executes exact permitted action
→ P99 preserves evidence
```

Motor may not issue or spoof SG decisions. Candidate SG may not approve itself. `SG-N` authorizes `SG-N+1`; bootstrap commissioning requires founder or threshold custody.

## Current containment

```text
NOETFIELD_MOTOR_IDENTITY_BINDING=PROVEN
NOETFIELD_MOTOR_UNIFIED_CORE_COMMISSIONING=NOT_PROVEN
NOETFIELD_MOTOR_SG_AUTHORITY=false
UNIFIED_MOTOR_RUNTIME=NOT_COMMISSIONED
SG_RUNTIME=NOT_COMMISSIONED
AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD
```

The legacy personal App `4179901` / installation `143449507`, its former personal repository identity, and `REMOTE_CHECK_ADVISORY` receipts are forbidden authority sources. Preserve them for forensics until SG v2 commissioning and rollback proof are complete.

## SG v2 floor

Every decision pins App ID, installation ID, repository, commit, action, target, artifact hash, policy hash, schema hash, evaluator hash, Worker version, signing-key ID, nonce, issuance time, and expiry. Webhook HMAC and GitHub delivery replay are verified. Permit replay is rejected. `merge_group` evaluates the merge-group head SHA. Public repository visibility never substitutes for installation proof.

The required check is `Noetfield SG / P0 Authority` from the exact `noetfield-sg-authority` App. No routine bypass actors. No exact fresh signed permit means no production mutation.

## Bootstrap break-glass

Break-glass is exact-SHA, exact-PR, time-limited, containment-only, founder/threshold recorded in P99, and cannot commission SG, lift HOLD, deploy, mutate secrets, or revoke the legacy identity.
