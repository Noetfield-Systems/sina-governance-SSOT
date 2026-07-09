# HANDOFF — SG Worker 1: Backend Builder

**Package:** `noos-control-desk-v1` · **Phase:** 1 · **Lane:** `sg_sssot_cursor`  
**Architect:** RETIRED — do not redesign architecture. Execute this handoff only.  
**Primary tool:** Cursor · **Repo:** `~/Projects/sina-governance-ssot` only

---

## API contract (Phase 1 canonical)

Authority: `data/noos_control_desk_api_contract_v1.json`

```
GET  /api/dashboard
GET  /api/registry/load
POST /api/registry/save-draft
POST /api/attestation/save
POST /api/policy/check
GET  /api/integrator/status
POST /api/integrator/sync
GET  /api/receipts/list
GET  /api/pr/prepare
POST /api/lock-candidate/submit
```

No duplicate public route names in Phase 1. Phase 2 replaces routes only via explicit refactor doc.

---

## Copy-paste prompt for new worker

```
You are SG Backend Builder for NOOS Control Desk MVP Phase 1.

Repo: ~/Projects/sina-governance-ssot
Package root: packages/noos-control-desk-v1/
Authority: ssot/NOOS_CONTROL_DESK_PACKAGE_v1.md
API contract (canonical Phase 1): data/noos_control_desk_api_contract_v1.json
Role map: data/noos_control_desk_builder_roles_v1.json

DO NOT:
- Redesign architecture (Architect is retired)
- Build cloud deploy, Electron, Selenium
- Write to cloud mirror (read-only readout only)
- Push to main or open PRs from backend
- Use Copilot as primary builder

MUST DELIVER — localhost FastAPI/stdlib backend at control-desk/app.py:

1) Registry
   GET  /api/registry/load          → workflow_registry_v1.json
   POST /api/registry/save-draft    → .noos/workflow_registry_draft.json (never overwrites live registry)

2) Attestation (server computes verdict — client never sends PASS)
   POST /api/attestation/save       → .noos/registry_draft.json per workflow
   Observed fields free-text (gpt-5.4, Auto, High allowed — record leaks, mark FAIL/BLOCKED)

3) Policy
   POST /api/policy/check           → subprocess check_cost_policy.py, aggregate errors JSON

4) Integrator (Phase 1 scope)
   POST /api/integrator/sync        → repo-local sync ONLY via scripts/noos_integrator_sync_v1.py sync
   GET  /api/integrator/status      → summary --json (no sync)
   Include in every integrator response:
     - repo_local freshness
     - home_mirror status if ~/.sina/noos-integrator-state-v1.json or NOOS_HOME_MIRROR_PATH configured
     - cloud_mirror readout if NOOS_CLOUD_MIRROR_STATUS_PATH file exists (READ ONLY)
     - cloud_write_scope: gated — unrestricted fleet/cloud propagation blocked before full PASS
     - cloud_write_scope_gate + gate_note on every integrator response (see NOOS_COPILOT_DISPATCHER_v1.md)

5) Receipts
   GET /api/receipts/list           → receipts/*.json

6) PR prep (plan only)
   GET  /api/pr/prepare             → suggested branch + commit plan, git status, NO push
   POST /api/lock-candidate/submit  → only when all attestations PASS; runs checker; bounded local branch+commit only

Security:
- Bind 127.0.0.1 only
- Allowlisted subprocesses only: check_cost_policy.py, noos_integrator_sync_v1.py, git (checkout/add/commit — no push)

Files you own:
- packages/noos-control-desk-v1/control-desk/app.py
- packages/noos-control-desk-v1/scripts/noos_integrator_sync_v1.py (SSOT adapter; canonical integrator lives in noetfeld-os later)

Read only (do not mutate law):
- .noos/workflow_registry_v1.json
- policy/cost_policy.yaml
- .noos/copilot_attestation_schema_v1.json
- .noos/receipt_schema_v1.json

Acceptance:
- python3 packages/noos-control-desk-v1/tests/run_negative_tests.py → 9/9 PASS
- POST attestation with gpt-5.4 → SAVED + policy_verdict FAIL (not rejected)
- GET /api/integrator/status → home_mirror + cloud_mirror fields honest (unconfigured if not set)
- Every sync response includes cloud_write_scope=gated and cloud_write_unrestricted_allowed=false
- Lock candidate rejects when TODO/FAIL/BLOCKED present
- No direct main write

Run:
  cd packages/noos-control-desk-v1
  python3 control-desk/app.py --port 17877 --repo-root .
```

---

## API contract (Phase 1 canonical)

Authority: `data/noos_control_desk_api_contract_v1.json` — use these routes only:

| Method | Path |
|--------|------|
| GET | `/api/dashboard` |
| GET | `/api/registry/load` |
| POST | `/api/registry/save-draft` |
| POST | `/api/attestation/save` |
| POST | `/api/policy/check` |
| GET | `/api/integrator/status` |
| POST | `/api/integrator/sync` |
| GET | `/api/receipts/list` |
| GET | `/api/pr/prepare` |
| POST | `/api/lock-candidate/submit` |

---

## API contract (for Frontend worker)

| Method | Path | Body | Response keys |
|--------|------|------|---------------|
| GET | `/api/dashboard` | — | `registry_entries`, `pass_count`, `fail_count`, `blocked_count`, `todo_count`, `ready_for_lock_candidate`, `git` |
| GET | `/api/registry/load` | — | full registry JSON |
| POST | `/api/registry/save-draft` | `{ workflows: [...] }` | `status`, `path`, `entries`, `receipt` |
| POST | `/api/attestation/save` | attestation fields + `workflow_id`, `last_audited` | `policy_verdict`, `verdict_reasons`, `receipt` |
| POST | `/api/policy/check` | — | `report.status`, `report.violations_active[]` |
| GET | `/api/integrator/status` | — | `repo_local`, `home_mirror`, `cloud_mirror`, `cloud_write_scope`, `cloud_write_unrestricted_allowed`, `cloud_write_scope_gate`, `gate_note` |
| POST | `/api/integrator/sync` | — | `summary`, `receipt`, `cloud_write_scope`, `cloud_write_unrestricted_allowed`, `cloud_write_scope_gate`, `gate_note` |
| GET | `/api/receipts/list` | — | `receipts: string[]` |
| GET | `/api/pr/prepare` | — | `suggested_branch`, `suggested_commit`, `git`, `note` |
| POST | `/api/lock-candidate/submit` | `{}` | `LOCK_CANDIDATE_READY` or `409 BLOCKED` |

---

## Env vars (optional mirrors)

| Var | Purpose |
|-----|---------|
| `NOOS_HOME_MIRROR_PATH` | Override home mirror file path |
| `NOOS_CLOUD_MIRROR_STATUS_PATH` | Read-only JSON snapshot for cloud mirror status display |

---

## Current baseline (already on disk)

- `control-desk/app.py` — stdlib HTTP server, routes above partially implemented
- `scripts/noos_integrator_sync_v1.py` — repo-local sync + mirror readout
- `scripts/check_cost_policy.py` — aggregate checker
- `tests/run_negative_tests.py` — 9/9 PASS

Extend and harden; do not restart from scratch.
