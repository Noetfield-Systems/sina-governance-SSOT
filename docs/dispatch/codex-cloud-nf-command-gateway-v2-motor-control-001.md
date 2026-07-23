# Dispatch — Codex Cloud: NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001

**Send to:** `noetfield:sandbox.builder-owner` · worker `openai.codex-cloud`  
**After:** NOOS re-pin to `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0` (or concurrent if Builder reads SG main directly)

```yaml
commission_id: NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001

architect:
  - founder.sina
  - sinagpt

canonical_authority:
  repository: Noetfield-Systems/sina-governance-SSOT
  decision_id: NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1
  sha: "b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0"
  decision_artifact_sha: "792eb6c6fdbf9b063b29dd5672ab66d91f9da37b"
  also_decisions:
    - NF-SINAGPT-FOUNDER-BRAIN-ARCHITECT-V1

implementation_repository: Noetfield-Systems/noetfield-cloud-factory-infra

builder_owner: noetfield:sandbox.builder-owner
worker_adapter: openai.codex-cloud

constraints:
  preserve_v1: true
  deploy: false
  merge: false
  production_write: false
  draft_pr_only: true

issue_ci_repair_execution: NOT_WIRED
```

## Required `/v2` scope

```text
GET  /v2/cockpit
GET  /v2/sg/authority/current
GET  /v2/sg/decisions/{decision_id}
POST /v2/sg/finalization-packets
GET  /v2/issues
GET  /v2/issues/{issue_id}
POST /v2/issues/{issue_id}/repair-requests
GET  /v2/ci/incidents
GET  /v2/ci/incidents/{incident_id}
POST /v2/ci/incidents/{incident_id}/repair-requests
POST /v2/commissions
GET  /v2/commissions/{commission_id}
GET  /v2/motor/recipes
GET  /v2/motor/recipes/{recipe_id}
GET  /v2/motor/jobs
GET  /v2/motor/jobs/{job_id}
GET  /v2/motor/jobs/{job_id}/truth
GET  /v2/motor/jobs/{job_id}/receipts
GET  /v2/approvals
GET  /v2/approvals/{approval_id}
POST /v2/approvals/{approval_id}/decision
```

POST repair-request endpoints may create requests safely with status `NOT_WIRED` or `AWAITING_OWNER_AUTHORITY` — **no automatic repair execution** until Issue/CI ownership is SG-ratified.

## Focused review (five boundaries only)

1. v1 compatibility  
2. Authentication split (read API-key vs founder OAuth)  
3. No raw infrastructure authority on GPT surface  
4. Idempotency + stale approval protection  
5. Seven-truth integrity  

**Final status:** `GATEWAY_V2_DRAFT_FOR_FOCUSED_REVIEW`
