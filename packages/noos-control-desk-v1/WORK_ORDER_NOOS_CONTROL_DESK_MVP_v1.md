# WORK ORDER — NOOS Control Desk MVP v1

**Status:** PROPOSED  
**Layer:** P7 (governance ops / execution contract)  
**Repo:** `sina-governance-ssot`  
**Goal:** Install local control desk scaffold  
**Package status:** `SCAFFOLD_READY_AUDIT_PENDING`

**Phase 0:** ACCEPTED (2026-07-04)  
**Phase 1:** UNBLOCKED — Backend Builder + Frontend Builder may start local Control Desk MVP only.

## Scope

| In scope | Out of scope |
|----------|--------------|
| Local FastAPI + React/Vite scaffold | Cloud deploy |
| 7 UI tiles (spec) | Electron |
| Policy checker + negative tests | Selenium |
| Receipt + attestation schemas | Premium models |
| 23 TODO workflow registry (raw) | Fake audit |
| Bounded branch + PR prep | Direct main write |

## Deliverables

- [x] `SMART_PRODUCTION_COST_LAW_v2.md`
- [x] `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md`
- [x] `.noos/workflow_registry_v1.json`
- [x] `policy/cost_policy.yaml`
- [x] `scripts/check_cost_policy.py`
- [x] `tests/run_negative_tests.py`
- [x] `NOOS_CONTROL_DESK_MVP_SPEC.md`
- [x] `.noos/copilot_attestation_schema_v1.json`
- [x] `.noos/receipt_schema_v1.json`
- [x] `NOOS_INTEGRATOR_SYNC_RULE_v1.md`
- [ ] `control-desk/app.py` (expand Phase 1)
- [ ] `control-desk/frontend/` (Phase 1)
- [ ] `README.md` / `INSTALL.md` / `RUN_LOCAL.md` (Packager)

## Agent execution order

1. Architect / Spec Keeper  
2. Policy Checker Agent  
3. Backend Builder  
4. Frontend Builder  
5. Integrator Agent  
6. Negative Test Agent  
7. Critic / Auditor  
8. Packager  

## Acceptance

- Bad observed model can be saved and marked **FAIL**
- Unknown model becomes **BLOCKED**
- Lock candidate rejects incomplete audits
- All negative tests pass
- Raw 23 TODO state ships — not fake audit
- Local app runs on localhost

## Key commands

```bash
python3 packages/noos-control-desk-v1/scripts/check_cost_policy.py --json receipts/self_scan_v2.json
python3 packages/noos-control-desk-v1/tests/run_negative_tests.py
```
