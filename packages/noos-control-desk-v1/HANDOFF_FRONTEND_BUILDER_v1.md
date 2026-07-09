# HANDOFF — SG Worker 2: Frontend Builder

**Package:** `noos-control-desk-v1` · **Phase:** 1 · **Lane:** `sg_sssot_cursor`  
**Architect:** RETIRED — consume backend API only; never compute policy verdicts client-side.  
**Primary tool:** Cursor · **Repo:** `~/Projects/sina-governance-ssot` only  
**Depends on:** Backend handoff `HANDOFF_BACKEND_BUILDER_v1.md` API contract

---

## Copy-paste prompt for new worker

```
You are SG Frontend Builder for NOOS Control Desk MVP Phase 1.

Repo: ~/Projects/sina-governance-ssot
Package root: packages/noos-control-desk-v1/
UI root: packages/noos-control-desk-v1/control-desk/
Spec: packages/noos-control-desk-v1/NOOS_CONTROL_DESK_MVP_SPEC.md
API contract (canonical Phase 1): data/noos_control_desk_api_contract_v1.json
Backend handoff: packages/noos-control-desk-v1/HANDOFF_BACKEND_BUILDER_v1.md

DO NOT:
- Compute policy_verdict in the browser (backend only)
- Hide observed bad values (gpt-5.4, Auto, High must be typeable and show FAIL/BLOCKED)
- Build Electron, Selenium, cloud deploy
- Call any API except localhost backend (127.0.0.1:17877)
- Redesign architecture

MUST BUILD — 7 tiles (single-page app OK):

1. Dashboard
   GET /api/dashboard
   Show: registry count, pass/fail/blocked/todo, lock-candidate readiness, git summary

2. Workflow Registry
   GET /api/registry/load
   POST /api/registry/save-draft
   Display 23 workflows; save draft without claiming audited

3. Copilot UI Attestation
   POST /api/attestation/save
   Observed fields = FREE TEXT (record reality)
   Desired fields = dropdown constrained (gpt-5-mini, low, manual)
   Display server-returned policy_verdict + verdict_reasons (never client-computed)

4. Policy Validator
   POST /api/policy/check
   Show ALL violations_active from checker (aggregate list, not first error only)

5. NOOS Integrator Sync
   GET  /api/integrator/status  — show repo_local, home_mirror, cloud_mirror readouts
   POST /api/integrator/sync    — run repo-local sync
   Always show cloud_write_scope, cloud_write_unrestricted_allowed, and gate_note
   If home/cloud unconfigured → display "unconfigured" honestly

6. Receipts
   GET /api/receipts/list
   List + view receipt JSON files

7. PR Prep
   GET  /api/pr/prepare — show suggested branch/commit plan only
   POST /api/lock-candidate/submit — disabled until dashboard.ready_for_lock_candidate
   Never show push-to-main; show gate: validator PASS + receipt + bounded branch required

Stack choice (pick one, stay localhost):
- Option A: extend control-desk/static/index.html (baseline exists)
- Option B: React/Vite under control-desk/frontend/ served by backend static

UX rules:
- Bad attestation saves successfully with FAIL/BLOCKED badge visible
- Lock Candidate button disabled with explicit blocker list (todo_ids, fail_ids, blocked_ids)
- cloud_write_scope=gated and cloud_write_unrestricted_allowed=false always shown in Integrator tile
- No fake PASS states

Files you own:
- control-desk/static/index.html (and/or control-desk/frontend/**)
- control-desk/static/*.css, *.js if split

Do NOT edit:
- control-desk/app.py (Backend Builder)
- scripts/check_cost_policy.py
- ssot law files

Acceptance:
- App loads at http://localhost:17877 with all 7 tiles navigable
- Enter gpt-5.4 + high + hourly → save → FAIL visible, not hidden
- Enter unknown model → BLOCKED visible
- Policy Validator shows full violation list when registry has TODO audits
- Integrator tile shows repo_local + home_mirror + cloud_mirror status fields
- cloud_write_scope=gated and cloud_write_unrestricted_allowed=false always visible on Integrator tile
- Lock Candidate disabled until all PASS (test with partial attestations)

Run backend first (separate terminal):
  cd packages/noos-control-desk-v1
  python3 control-desk/app.py --port 17877 --repo-root .
```

---

## Tile → API map

| Tile | Primary calls |
|------|----------------|
| Dashboard | `GET /api/dashboard` |
| Workflow Registry | `GET /api/registry/load`, `POST /api/registry/save-draft` |
| Copilot Attestation | `POST /api/attestation/save` |
| Policy Validator | `POST /api/policy/check` |
| Integrator Sync | `GET /api/integrator/status`, `POST /api/integrator/sync` |
| Receipts | `GET /api/receipts/list` |
| PR Prep | `GET /api/pr/prepare`, `POST /api/lock-candidate/submit` |

---

## Verdict display rules (non-negotiable)

| Server `policy_verdict` | UI badge |
|-------------------------|----------|
| `PASS` | green |
| `FAIL` | red + show `verdict_reasons[]` |
| `BLOCKED` | red/orange + show reasons |
| missing / TODO | yellow |

Client must **never** send `policy_verdict` in POST body.

---

## Integrator tile copy (show verbatim)

- **Repo-local:** `{repo_local}` + age hours  
- **Home mirror:** `{home_mirror}` + path if configured  
- **Cloud mirror:** `{cloud_mirror.status}` read-only — never a "Sync to cloud" button  
- **Gate:** scope-gated cloud writes per NOOS Copilot — receipts/status/drift/draft PR prep allowed; fleet rollout, ACTIVE promotion, direct main write, policy/law mutation blocked  

---

## Current baseline

- `control-desk/static/index.html` — v2 patch UI with 7 nav buttons exists; extend to full Phase 1 contract
- Backend routes live — wire all tiles to API map above

Do not rebuild from zero unless static file is broken; prefer extend.
