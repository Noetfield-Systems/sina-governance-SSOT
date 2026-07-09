# NOOS Control Desk MVP Spec v1

**Status:** PROPOSED  
**Layer:** P3 (Mac runtime)  
**Package:** `noos-control-desk-v1`  
**Depends on:** `SMART_PRODUCTION_COST_LAW_v2`, `.noos/workflow_registry_v1.json`

## Objective

Local-only cockpit (localhost) to observe, attest, validate, sync, and prepare PRs — **no cloud, no Electron, no Selenium, no fake audit**.

## Stack

| Part | Choice |
|------|--------|
| Backend | FastAPI (`control-desk/app.py`) |
| Frontend | React/Vite (`control-desk/frontend/`) — Phase 1 |
| Bind | `127.0.0.1` only |
| Policy verdict | Backend only — frontend displays, never computes |

## Seven tiles (pages)

1. **Dashboard** — package status, workflow counts, last receipt
2. **Workflow Registry** — load/save draft of `workflow_registry_v1.json`
3. **Copilot UI Attestation** — capture observed vs desired per `copilot_attestation_schema_v1.json`
4. **Policy Validator** — run `scripts/check_cost_policy.py` (aggregate errors)
5. **NOOS Integrator Sync** — `python3 scripts/noos_integrator_sync_v1.py sync` + `summary --json`
6. **Receipts** — list receipts from `receipts/`
7. **PR Prep** — bounded branch, commit message, no direct main

## Backend routes — Phase 1 canonical API

**SSOT contract:** `data/noos_control_desk_api_contract_v1.json`  
**Implementation:** `control-desk/backend/handler.py`

Phase 1 uses these routes only. No duplicate public route names.

| Method | Route | Action |
|--------|-------|--------|
| GET | `/api/dashboard` | Dashboard counts + lock readiness + git summary |
| GET | `/api/registry/load` | Read workflow registry |
| POST | `/api/registry/save-draft` | Write draft registry (never marks audited) |
| POST | `/api/attestation/save` | Save attestation row (server computes verdict) |
| POST | `/api/policy/check` | Run checker, return aggregate errors + verdict |
| GET | `/api/integrator/status` | Read-only integrator + mirror readouts |
| POST | `/api/integrator/sync` | Repo-local integrator sync (no cloud write) |
| GET | `/api/receipts/list` | List receipt JSON files |
| GET | `/api/pr/prepare` | PR prep plan only (no push) |
| POST | `/api/lock-candidate/submit` | Lock candidate when all PASS + checker PASS |

Phase 2 may replace routes only via explicit refactor — do not add duplicate names in Phase 1.

## Core actions

- Load registry (23× TODO state ships as-is)
- Save Draft
- Run Validator (FAIL must show all errors, not hide)
- Run Integrator Sync
- Submit Lock Candidate (only when all required workflows PASS)
- Write Receipt
- Prepare Branch/Commit

## Observed vs desired

UI captures **observed** Copilot reality separately from **desired** policy defaults:

- `desired_trigger = manual`
- `desired_model = gpt-5-mini`
- `desired_effort = low`

Server computes `policy_verdict`: `PASS` | `FAIL` | `BLOCKED` | `TODO`

Example FAIL: observed `hourly + autopilot + gpt-5.4 + high`

## Validation / submit flow

1. Load registry → 2. Attest observed reality → 3. Save Draft → 4. Run checker → 5. Write receipt → 6. Bounded branch → 7. Commit → 8. PR Prep

**No direct main write. No fake pre-audited data.**

## Acceptance (Phase 2 local test)

- App starts locally
- Loads 23 TODO workflows
- Bad model (GPT-5.4/High) saves and shows FAIL
- Checker aggregates all errors
- Receipt written
- Lock candidate rejects incomplete audits
