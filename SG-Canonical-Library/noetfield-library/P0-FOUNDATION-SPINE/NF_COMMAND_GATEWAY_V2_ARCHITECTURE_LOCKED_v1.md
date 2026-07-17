# NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1 — SG FINALIZATION PACKET

**decision_id:** `NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1`  
**title:** Noetfield Founder Command & Motor Gateway API v2  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` (commission `NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001` only; no production deploy in that commission)  
**Authority:** Architecture Finalization Gate  
**Tier:** P0-FOUNDATION-SPINE (control-plane API architecture)  
**Version:** v1.0.0_locked_20260717  
**Machine:** `data/nf_command_gateway_v2_architecture_v1_LOCKED.json`  
**Commission:** `docs/dispatch/nf-command-gateway-v2-motor-control-001.md`  
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-SINAGPT-FOUNDER-BRAIN-ARCHITECT-V1`  
**Packet id:** `SG-FINALIZATION-COMMAND-GATEWAY-V2-V1`  
**effective_at:** 2026-07-17  
**proposed_by:** Founder + Brain/Architect  
**Implementation home:** `noetfield-cloud-factory-infra` (Gateway Worker + OpenAPI). SG holds canon; other repos get `noetfield.sg-authority-ref.v1` pointers.  
**sg_authority_sha:** `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0`  
**decision_artifact_sha:** `792eb6c6fdbf9b063b29dd5672ab66d91f9da37b`  
**canonical_main_sha:** `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0`  
**merge_strategy:** merge_commit (PR #18)
**supersedes:** none for `/v1` (compatibility preserved)

---

## Decision

```text
Keep Command Gateway v1 operational
        ↓
Add Command Gateway v2 for Unified Motor + Issues + CI + SG authority
        ↓
Finalize v2 with SG (this packet)
        ↓
Implement via NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001 (draft PR; no deploy)
```

Do **not** discard the current `/v1` schema.

## Current v1 role (preserved)

```text
SinaGPT → Command Gateway v1
  ├── status queries
  ├── workflow dispatch (internalized for GPT surface in v2)
  ├── lane visibility
  ├── receipts
  ├── promotion packets
  ├── founder approvals
  ├── GitHub bridge
  └── infrastructure status
```

v1 = Cloud Factory command/control API.  
v1 is **missing**: Unified Motor objects, Issue Manager, CI Solver resources, SG decision reads, seven-truth model, founder OAuth split; GPT-facing raw workflow surface is too broad.

## Target chain (v2)

```text
SinaGPT
  → Commission / founder intent
  → NOOS Issue Manager
  → SourceA job compiler
  → Unified Motor
  → Recipe · Owner · Sandbox · Worker · Verification
  → Approval · Promotion · Outcome
  → Receipt / P99
```

## Four binding corrections

### 1. Founder identity split

API-key auth is acceptable for server-to-server Gateway authentication. It does **not** prove the human approver is Sina.

| Action set | Auth |
|------------|------|
| Noetfield Read Gateway | API key — cockpit/job/issue/receipt/PR/workflow/SG/infra reads |
| Noetfield Founder Command Gateway | OAuth tied to Sina — commissions, repair requests, founder gates, SG finalization proposals, cancel/hold |

Public/link-shared GPTs with Actions also need a valid privacy-policy URL.

### 2. Natural language must not directly execute

`POST /v1/commands` must not immediately become merge/deploy/unrestricted workflow.

Safer path:

```text
Natural-language command → Interpretation → Commission draft
→ Policy/authority resolution → Motor job or approval request
```

`POST /v2/commands` creates only: `CommandPlan` | `Commission` | `ApprovalRequest` | `StatusQuery`.  
Gateway—not SinaGPT—decides the category.

### 3. Remove raw workflow dispatch from GPT surface

`POST /v1/github/workflow-dispatch` stays **internal** (Motor/NOOS after recipe + authority).  
SinaGPT calls `POST /v2/commissions` or issue repair-request endpoints.

### 4. PASS/FAIL is not enough

Receipt / truth vocabulary must include:

```text
PASS · FAIL · BLOCKED · UNPROVEN · STALE · DIVERGED · INCONCLUSIVE · CANCELLED
```

Motor jobs require seven independent truth fields (`MotorJobTruth`):

```text
dispatch · execution · verification · evidence · authority · promotion · outcome
```

A stale evidence writer must not become `execution = FAILED`.  
A successful merge must not become `outcome = PROVEN`.

## Required v2 SinaGPT-facing operations (approx.)

```text
getCockpit
getCurrentSGAuthority · getSGDecision
listIssues · getIssue · requestIssueRepair
listMotorJobs · getMotorJob · getMotorJobTruth
submitCommission
listApprovals · submitFounderDecision
listReceipts · getReceipt
getPullRequestStatus · getWorkflowRunStatus
```

Keep internal: raw GitHub workflow dispatch, direct PR creation, Cloudflare deploy primitives, Railway restart, Supabase writes, secret rotation, queue deletion, direct Motor state transition.

## Idempotency + stale approval protection

Every consequential POST requires header `Idempotency-Key` (16–128 chars).  
Founder decisions require `expected_subject_version`; mismatch → `409 subject_version_conflict`.

## Approval kinds (extend)

```text
motor_job · production_promotion · workflow_dispatch · pull_request_merge
secret_rotation · database_migration · sg_architecture · commercial_model_escalation
cost_budget_exception · content_publication
```

## Canonical schemas (implement in OpenAPI)

### TruthDimension

Required: `state`, `observed_at`, `source`.  
States: `NOT_STARTED` | `IN_PROGRESS` | `PROVEN` | `FAILED` | `BLOCKED` | `UNPROVEN` | `STALE` | `DIVERGED` | `CANCELLED`.  
`PROVEN` requires `evidence_refs` ≥ 1.  
`FAILED|BLOCKED|UNPROVEN|STALE|DIVERGED` require `reason`.

### MotorJobTruth

Required: dispatch, execution, verification, evidence, authority, promotion, outcome — each a TruthDimension.

### MotorJob

Required: job_id, recipe_id, recipe_version, owner_role_id, sg_decision_id, sg_authority_sha (40 hex), lifecycle_status, truth, created_at, updated_at.  
Lifecycle enum matches Unified Motor foundation state machine (`RECEIVED` … `RECEIPT_COMPLETE` + `BLOCKED` + `CANCELLED`).

### Issue

Required: issue_id, title, status, classification, manager_role_id=`noetfield:noos.issue-manager`, created_at, updated_at.

## Ownership through the API

| Layer | Role |
|-------|------|
| SinaGPT | Founder-facing command and explanation |
| Command Gateway | Auth, normalization, policy front door |
| SG | Authority and canon |
| NOOS Issue Manager | Issue ownership and classification |
| CI Reliability Owner | CI infrastructure and flake |
| SourceA | Commission-to-recipe compiler |
| Unified Motor | Creates and runs jobs |
| SANDBOX Builder Owner | Bounded build/repair execution |
| Codex/open model | Replaceable worker |
| CI | Deterministic verification |
| P99 | Evidence destination |

SinaGPT must never select itself as issue owner, solver, verifier, or promoter.

## SG answers (gate questions)

1. **P0 preserved?** Yes — Author≠Subject; Sina owns DECIDE; Gateway re-derives truth; no self-PASS.
2. **Conflict?** No — extends Unified Motor + Finalization Gate; preserves `/v1`.
3. **Superseded?** None ACTIVE replaced; GPT-facing raw workflow dispatch deprecated for SinaGPT Actions.
4. **Authority?** SG for architecture; founder OAuth for consequential commands; Motor executes.
5. **Machine-safe?** Reads; commission drafts; repair requests (NOOS classifies).
6. **Founder-only?** Approvals, promote, secret rotation, production deploy, SG architecture accept (via SG SHA).
7. **Boundaries?** Secrets not in GPT; no direct infra primitives on GPT surface.
8. **Evidence → P99?** Via Motor receipts; Gateway must not trust SinaGPT-supplied PASS claims.
9. **Rollback?** Disable `/v2` Actions; keep `/v1`; revert authority pointer.
10. **Authority SHA?** Stamp after this packet lands on SG `main`.

## non_goals

- Deploying v2 to production in the first commission
- Rewriting recipes through Command API
- Making SinaGPT a persistent Issue Manager
- Discarding `/v1`

## Commission scope pointer

See `docs/dispatch/nf-command-gateway-v2-motor-control-001.md`.
