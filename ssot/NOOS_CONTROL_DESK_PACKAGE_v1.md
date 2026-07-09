# NOOS Control Desk Package v1 — Master Layer Map

**Status:** ACTIVE (structure authority)  
**Package status:** `SCAFFOLD_READY_AUDIT_PENDING`  
**Owner:** SG (`sina-governance-ssot`)  
**Install root:** `packages/noos-control-desk-v1/`  
**Authority:** [GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md](GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md)

## Purpose

One local cockpit to audit, validate, sync, and submit workflow state — **without founder-as-runtime**.  
Install first in SG; rollout after local install test passes.

**Rollout order:** 1) `sina-governance-ssot` → 2) `noetfeld-os` → 3) `SourceA` → 4) `Noetfield` → 5) `TrustField-Technologies`

Each repo receives **only its module slice**, not the full law stack.

---

## Policy stack (5 layers — cheat sheet alignment)

```
POLICY (P8) → REGISTRY (P8) → UI (P3) → VALIDATION (P8) → SYNC (P2) → PR PREP (P8/P99)
```

| Stack level | Artifact | SG path |
|-------------|----------|---------|
| L1 Master Law | `SMART_PRODUCTION_COST_LAW_v2.md` | `packages/noos-control-desk-v1/` |
| L2 Copilot sub-policy | `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md` | `packages/noos-control-desk-v1/` |
| L3 Control ledger | `.noos/workflow_registry_v1.json` | `packages/noos-control-desk-v1/.noos/` |
| L4 Local UI | NOOS Control Desk MVP | `packages/noos-control-desk-v1/control-desk/` (Phase 1) |
| L5 Execution | GitHub Actions / Cloudflare / NOOS Integrator / Copilot manual | per-repo workflows |

---

## Layer placement (master structure)

| # | Artifact | Primary layer | Domain | Role / affects | Status | Registry ID |
|---|----------|---------------|--------|----------------|--------|-------------|
| 0 | `ssot/NOOS_CONTROL_DESK_PACKAGE_v1.md` | **P0** | package_authority | Package authority tying P2/P3/P7/P8/P99 | ACTIVE | `noos-control-desk-package-v1` |
| 1 | `SMART_PRODUCTION_COST_LAW_v2.md` | **P8** | automation | L1 Master Law · P0, P2, P3, P4, P8 | SCAFFOLD_READY_AUDIT_PENDING | `smart-production-cost-law-v2` |
| 2 | `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md` | **P8** | automation | L2 Copilot sub-policy · P8 | LOCKED POLICY ARTIFACT / rollout SCAFFOLD_READY_AUDIT_PENDING | `copilot-automation-cost-profile-v1` |
| 3 | `.noos/workflow_registry_v1.json` | **P8** | automation | L3 Control ledger | SCAFFOLD (23× `last_audited: TODO`) | `noos-workflow-registry-v1` |
| 4 | `policy/cost_policy.yaml` | **P8** | automation | Machine policy config | SCAFFOLD_READY_AUDIT_PENDING | `noos-cost-policy-v1` |
| 5 | `scripts/check_cost_policy.py` | **P8** | automation | Policy gate · P8, P99 | SCAFFOLD_READY_AUDIT_PENDING | `noos-check-cost-policy-v1` |
| 6 | `NOOS_CONTROL_DESK_MVP_SPEC.md` | **P3** | mac_runtime | L4 Local UI blueprint · P3, P8 | PROPOSED | `noos-control-desk-mvp-spec-v1` |
| 7 | `.noos/copilot_attestation_schema_v1.json` | **P8** | automation | Attestation contract | PROPOSED | `noos-copilot-attestation-schema-v1` |
| 8 | `.noos/receipt_schema_v1.json` | **P99** | ledger | Schema-validated receipt contract · P8, P99 | PROPOSED | `noos-receipt-schema-v1` |
| 9 | `NOOS_INTEGRATOR_SYNC_RULE_v1.md` | **P2** | integrator | Sync law · P2, P3 | ACTIVE (SG mirror) | `noos-integrator-sync-rule-v1` |
| 10 | `WORK_ORDER_NOOS_CONTROL_DESK_MVP_v1.md` | **P7** | governance_structure | Execution contract · P3, P8 | PROPOSED | `work-order-noos-control-desk-mvp-v1` |

### Layer rationale

- **P0** owns package authority — `NOOS_CONTROL_DESK_PACKAGE_v1.md` ties P2/P3/P7/P8/P99 into one installable package.
- **P8** owns automation law, Copilot sub-policy, workflow registry, cost policy, checker, attestation schema — machine loops and process registries.
- **P3** owns the local Control Desk UI (localhost FastAPI + React/Vite) — Mac runtime reality, not cloud/Electron/Selenium.
- **P2** owns integrator sync law — repo-local vs home mirror vs cloud owner; cross-repo coordination plane.
- **P99** owns receipt schema — every check/submit/sync must leave audit proof.
- **P7** owns the work order — execution contract for builders, not live base law.

### What is NOT live yet

- Status stays **`SCAFFOLD_READY_AUDIT_PENDING`** until registry audit + self-scan PASS.
- 23 workflows ship raw `last_audited: TODO` — **no fake audit**.
- Activation requires checker PASS + receipt + bounded branch + PR prep — **no direct main**.

---

## Sovereign stack (operating law)

| Owner | Role |
|-------|------|
| GitHub Actions | Automation engine (`model:none` default for scheduled) |
| Cloudflare | Control plane / coordination |
| NOOS Integrator | Sync state (session exit hook) |
| Copilot | Manual GPT-5 mini / Low / Manual only |

**Forbidden:** Auto mode, GPT-5.4, Claude, direct main merge, premium fallback, scheduled Copilot Autopilot.

---

## Workflow classes (registry `class` enum)

| Class | Owner default | Model | Output |
|-------|---------------|-------|--------|
| observe | GitHub Actions / scripts | `model:none` | receipt / artifact |
| triage | Copilot manual | `gpt-5-mini-low` | root cause |
| safe_fix | Copilot / script | `gpt-5-mini-low` or `model:none` | branch + PR + receipt |
| verify | GitHub Actions | `model:none` | PASS / FAIL |
| deploy | GitHub Actions (gated) | `model:none` | gated deploy |
| reconcile | NOOS Integrator | `model:none` | synced state |

---

## Agent build lanes (each reads only its layer)

| Order | Agent | Layer | Tool | Scope | Status |
|-------|-------|-------|------|-------|--------|
| 1 | Architect / Spec Keeper | — | — | **RETIRED** | Build phase only |
| 2 | Policy Checker Agent | P8 | Cursor | checker + QA-A negative tests | **done** |
| 3 | Backend Builder | P3+P8 | Cursor | API routes | **done** |
| 4 | Frontend Builder | P3 | Cursor | 7 tiles UI | **11/11 PASS** |
| — | Integrator / **NOOS Copilot** | **P2** | Control Desk API | Cross-repo sync dispatcher · root repos | **13/13 PASS ACCEPTED** |

### Canonical package steps (remaining)

| Step | Name | Scope |
|------|------|-------|
| **5** | NOOS Sync Mode Patch | **COMPLETE / RECORDED** — mode-gated; SG pointers only |
| **6** | Machine-Enforceable Repo Fences | **COMPLETE / Phase 1** — CODEOWNERS + CI checker; fleet deferred |
| **7** | Real 23-Workflow Audit | **COMPLETE / HONEST_BLOCKED** — 7F-B partial UI evidence (`AUTOMATIONS_DISABLED_UI_ATTESTED_PARTIAL`); draft **22 PASS / 1 BLOCKED** |
| **8** | Policy Check | **blocked** — final Copilot re-attestation + branch-only main merge pending |
| **9** | Lock Candidate | **blocked** — not submittable until all 23 PASS |
| **10** | SG Records Result | registry + receipt proof |

### Package QA (optional gates — not canonical steps)

| QA | Name | Tool |
|----|------|------|
| **QA-A** | negative tests | Cursor + GHA |
| **QA-B** | auditor pass | chat review |
| **QA-C** | packager receipt | Cursor README/zip |

**NOOS Copilot may:** integrator status/sync, receipts, status, drift reports, draft branch/PR prep (scope-gated).  
**NOOS Copilot may not:** fleet rollout, ACTIVE promotion, direct main write, policy/law mutation, audit-pending registry propagation, recurring Copilot automation.

---

## Phase gates

| Phase | Scope | Exit criteria |
|-------|-------|---------------|
| 0 | SG scaffold install | **ACCEPTED** — files on disk, registry rows, patched wording, layer map complete |
| 1 | Control Desk MVP build | Backend + Frontend — Steps 2–3 **PASS** (11/11 frontend smoke) |
| 2 | Local install test | bad model → FAIL visible; checker aggregate; receipt |
| 3 | 23 workflow attestation | observed reality entered; drafts saved |
| 4 | Integrator / NOOS Copilot | **ACCEPTED 13/13** — P2 dispatcher recorded |
| 5 | NOOS Sync Mode Patch | **COMPLETE / RECORDED** |
| 6 | Machine-Enforceable Repo Fences | **COMPLETE / Phase 1** |
| 7 | Real 23-Workflow Audit | **COMPLETE / HONEST_BLOCKED** — 7F-B partial UI evidence; 22 PASS / 1 BLOCKED |
| 8 | Policy Check | **blocked** (backend re-attestation + branch-only main) |
| 9 | Lock Candidate | **blocked** |
| 10 | SG Records Result | pending |
| — | Rollout (post-Step 10) | per-repo module slice only |

---

## Machine SSOT

- Package map JSON: `data/noos_control_desk_package_map_v1.json`
- **API contract (Phase 1):** `data/noos_control_desk_api_contract_v1.json`
- **NOOS Copilot dispatcher (P2):** `data/noos_copilot_dispatcher_v1.json`
- Registry: `data/governance_artifact_registry_v1.json`
- Intake sink rules: `data/governance_intake_sink_rules_v1.json`

**Cross-link:** [NOOS_INTEGRATOR_RULES_v1.md](NOOS_INTEGRATOR_RULES_v1.md) · [GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md](GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md)
