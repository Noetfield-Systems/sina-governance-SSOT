# Commission — NF-UNIFIED-MOTOR-V1-FOUNDATION (T0 Builder)

**Dispatch to:** SG-designated builders / sandbox implementation lane (**not** noetfeld-OS)  
**When:** only after Wave 0 DONE (`docs/dispatch/wave-0-nf-unified-motor-merge-packet.md`)  
**Canonical decision:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1`  
**Prior accept SHA (historical):** `8b476f721b1fe21f16036c84437f16de60434618`  
**Authority SHA:** *must be ancestor of `sina-governance-SSOT@main` after Wave 0 — refuse if only on doctrine branch*  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` (foundation wave only)  
**Laws:** FOUNDER_CANON v1 + governed-autorun v3. Violations = `BLOCKED_WITH_REASON`.  
**Receipts:** SUBMITTED for independent verification (author ≠ verifier; no self-PASS).

---

## Preconditions (refuse to build if any fails)

1. Read:
   - `P0-FOUNDATION-SPINE/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCKED_v1.md`
   - `data/nf_unified_motor_architecture_v1_LOCKED.json`
   - `docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md`
   - `docs/dispatch/nf-unified-motor-architecture-all-repos.md`
   - this commission + Wave 0 packet
2. Confirm `sg_authority_sha` is an **ancestor** of `sina-governance-SSOT@main`. If only on a doctrine branch → STOP (Wave 0 not done).
3. Build in builders/sandbox lane — **not** noetfeld-OS (observe/classify/route only).
4. Refuse if another ACTIVE SG decision conflicts.
5. Claim the authorized implementation lane before editing.

---

## Build only (T0 deterministic vertical slice)

1. Cloudflare event gateway  
2. `NoetfieldResidentRoleAgent` base  
3. Five Resident Role instances (SG Registrar, NOOS Portfolio, SourceA Dispatch, SANDBOX Builder, Verifier)  
4. `MotorJobWorkflow`  
5. Motor Registry loader  
6. Job state store  
7. SG/Hub policy adapter  
8. Durable receipt ledger/outbox  
9. NOOS event adapter  
10. `SandboxAdapter` interface  
11. `GitWorktreeSandbox` adapter  
12. `GitHubActionsSandbox` adapter  
13. Deterministic verification adapter  
14. Founder approval wait/resume  
15. Outcome probe  
16. P99 receipt adapter  

---

## Architecture law (do not redesign)

- Cloudflare Agents = persistent Resident Role owners (identity)
- Cloudflare Workflows = durable Motor jobs (execution). Agent ≠ job
- Motor Registry = recipe/job contract
- NOOS = observe/classify/route · SG/Hub = authority + policy
- SandboxAdapter = replaceable backends; GitWorktree + GitHubActions first
- P99 = evidence destination

## Foundation state machine

Lifecycle label is **derived** from the 7 truth dimensions (dispatch, execution, verification, evidence, authority, promotion, outcome); it must never overwrite them:

```text
RECEIVED → AUTHORITY_RESOLVING → RECIPE_VALIDATED → JOB_CREATED →
SANDBOX_PROVISIONING → EXECUTING → VERIFYING → REPAIRING|ESCALATING →
AWAITING_AUTHORITY → PROMOTING → OUTCOME_OBSERVING → RECEIPT_COMPLETE
```

## First cold proof (deterministic, non-production, no GPU)

```text
controlled NOOS event → NOOS Resident Owner → SourceA selects registered recipe
→ SG/Hub validates authority SHA → Motor Workflow creates job → git-worktree sandbox
→ deterministic operation → deterministic verifier → receipt persisted → P99
```

Every Motor job record carries:

```json
{
  "sg_decision_id": "NF-UNIFIED-MOTOR-ARCHITECTURE-V1",
  "sg_authority_sha": "<ancestor of SG main>"
}
```

Required artifacts: one job ID · one recipe version · one SG authority SHA · one sandbox ID · one execution artifact · one verification result · one final receipt · one P99 evidence pointer.

## Excluded

RunPod / vLLM / GPU · commercial model APIs · multi-customer tenancy · dozens of agents · Kubernetes · universal tool execution · autonomous production deployment · broad knowledge graphs.

## Guardrails

Do not deploy production. Do not add GPU. Do not call commercial models. Do not merge. Do not redefine architecture. Open a **DRAFT** PR with CI and a concise Builder receipt.

**Final status label:** `FOUNDATION_BUILT_FOR_FOCUSED_REVIEW`

## After cold proof (Track D / first machine-safe job)

Wire `receipt_writer_completion_evidence_repair` → `NF-MOTOR-RECEIPT-WRITER-REPAIR-001` with a named Resident Role owner.  
Website re-run through the foundation = first founder-gated job. Keep `MOTOR-WEB-001` as historical Client-Zero job — do not claim the Runner executed it.
