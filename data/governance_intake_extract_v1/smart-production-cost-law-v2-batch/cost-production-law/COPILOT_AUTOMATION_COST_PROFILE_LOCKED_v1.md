# COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md

**Status:** LOCKED POLICY ARTIFACT — bound as **Level 2 Sub-Policy Module** under `SMART_PRODUCTION_COST_LAW_v2.md` (Level 1 Master Law). This file retains sole ownership of Copilot UI toggle values (model, effort, trigger, mode). Structural rules (workflow classes, registry schema, budgets, refusal conditions) belong to Level 1 — if this file and the master law ever disagree on a Copilot-specific setting, this file wins for that setting only.

**Date:** 2026-07-03
**Scope:** GitHub Copilot app automations, Copilot sessions, GitHub/Copilot agent tasks, and related repo automation strategy.
**Purpose:** Prevent uncontrolled token burn while preserving useful automation, safe repair loops, and machine coordination.

---

## 0. Prime Rule

Copilot does not own autorun.

Copilot is a bounded helper and repair worker.
GitHub Actions / scripts / machine gates own recurring automation.

**Default allowed Copilot model:** `GPT-5 mini`
**Default effort:** `Low`
**Default trigger:** `Manual`
**Default recurring automation engine:** GitHub Actions / scripts with `model:none`

---

## 1. Hard Model Lock

### Allowed by default
```text
GPT-5 mini
```

### Forbidden by default
```text
Auto
GPT-5.4
GPT-5.4 mini
GPT-5.3-Codex
Auto: GPT-5.4
Auto: GPT-5.3-Codex
Claude Haiku
Claude Sonnet
Claude Opus
Anthropic
Gemini
Kimi
MAI-Code
Coding Agent model
Unknown model
Any fallback model
Any premium/high model route
```

### Exception rule
Exceptions are not normal workflow. Any non-`GPT-5 mini` model requires a separate explicit exception with: `reason, task_id, model, max_cost, max_tokens, expiry, receipt`. No permanent exception. No silent fallback. No Auto.

---

## 2. Effort Lock

**Default:** `Low`
**Allowed only by explicit task need:** `Medium` — only for manual diagnosis or bounded repair when Low clearly cannot complete the task.
**Forbidden by default:** `High`, `Extra High`, unknown effort, auto effort.

---

## 3. Trigger Lock

**Copilot automation default:** `Manual`
**Forbidden by default for Copilot automations:** Hourly, Daily, Weekly, Background, Keep awake, Unpinned schedule, Autopilot recurring.
**Scheduled work belongs to:** GitHub Actions, repo scripts, cost-policy scanners, deterministic validators, receipt validators, `model:none` jobs.

---

## 4. Mode Lock

**Autopilot is allowed when all are true:** Trigger=Manual, Model=GPT-5 mini, Effort=Low, task is bounded, task is read-only OR safe-fix scoped, no direct merge, no premium tools, no background process.

**Use Plan mode when:** deployment, production risk, model routing change, secrets/provider config, governance/SSOT change, database/runtime migration, unclear blast radius.

**Interactive mode:** only when human collaboration is intentionally needed. Not a hidden permission loop for normal machine work.

---

## 5. Workflow Classes (Copilot-specific settings only — see Level 1 for class ownership/engine)

**A. Manual Read-Only Diagnostics** — Trigger: Manual · Mode: Autopilot · Model: GPT-5 mini · Effort: Low · Edits: No.

**B. Manual Planning** — Trigger: Manual · Mode: Plan · Model: GPT-5 mini · Effort: Low · Edits: No · Output: plan only.

**C. Safe Auto-Fix** — allowed, not report-only forever. Trigger: Manual or audit-triggered by machine artifact · Mode: Autopilot · Model: GPT-5 mini · Effort: Low · Scope: explicit allowed files/paths · Output: bounded branch/PR + receipt · Merge: never direct · Verifier: required.

**D. High-Risk Repair** (deploy workflows, runtime kernel, secrets, provider config, model router, governance/SSOT, database migration, production behavior) — Trigger: Manual · Mode: Plan first · Model: GPT-5 mini · Effort: Low or Medium by exception · Edits only after plan passes machine policy · Merge: never direct.

**E. Recurring Observers** — should normally be GitHub Actions/scripts, not Copilot Automations. Engine: GitHub Actions/script · Model: none · LLM not used by default. If a recurring observer truly requires language interpretation: GitHub Actions triggers a bounded GPT-5-mini job, Effort Low, frequency justified, receipt required, budget capped. **Copilot scheduled Autopilot remains forbidden by default.**

---

## 6. NOOS Integrator Sync Rule (Copilot's role in it)

Integrator sync is machine coordination, not human reporting. Preferred owner: repo-local NOOS integrator script, GitHub Actions `model:none`, or configured NOOS cloud runner. **Copilot may assist only as a manual diagnostic or scoped repair worker** — never as the integrator's cloud owner unless pinned and explicitly disabled from Autopilot-recurring behavior.

Local exit rule:
```bash
python3 scripts/noos_integrator_sync_v1.py sync
python3 scripts/noos_integrator_sync_v1.py summary --json
```

---

## 7. Copilot Coordination Sessions

Coordination sessions are useful workers when pinned: Trigger Manual unless justified, Model GPT-5 mini, Effort Low, Mode Autopilot only for bounded work. No Auto, no GPT-5.4, no Claude, no High effort. Don't delete useful coordination blindly — pin it, cheapen it, scope it.

---

## 8. Automation Inventory Requirement (feeds Level 1's `last_audited` field)

A cost audit is incomplete unless it checks the actual Copilot automation UI state — repo scans alone are insufficient. Required audit surfaces: Copilot app Automations list, each automation's Trigger/Mode/Model/Effort/Workspace/last run, session logs showing model changes, GitHub Actions workflows, repo scripts, cloud cron, secrets/provider availability, model router fallback behavior.

Any automation showing Auto, GPT-5.4, Claude, Codex, Gemini, Kimi, MAI-Code, High, Extra High, Unknown model, or Unknown effort is `COST_POLICY_FAIL`. **This is the audit that produces the `last_audited` date written into `.noos/workflow_registry_v1.json` under Level 1 — this file defines what "audited" means; the registry field just records when it last happened.**

---

## 9. Settings Blueprint by Automation Type

| Automation type | Trigger | Mode | Model | Effort | Owner |
|---|---|---|---|---|---|
| Bug triage/root cause | Manual | Autopilot | GPT-5 mini | Low | Copilot |
| Implementation plan | Manual | Plan | GPT-5 mini | Low | Copilot |
| Evidence/PR/release readiness | Manual | Autopilot | GPT-5 mini | Low | Copilot |
| Integrator sync audit | Manual | Autopilot | GPT-5 mini | Low | Copilot helper / script owner |
| Safe fixer | Manual/audit-triggered | Autopilot | GPT-5 mini | Low | Copilot + verifier |
| High-risk repair | Manual | Plan first | GPT-5 mini | Low/Medium exception | Copilot + verifier |
| Daily repo health | Scheduled | script | none | none | GitHub Actions |
| Daily/weekly proof/docs/security | Scheduled | script | none | none | GitHub Actions |
| Deploy | Manual | Plan/gate | none / GPT-5 mini for review only | Low | GitHub Actions + gates |

---

## 10. UI Checklist for Every Copilot Automation

```text
Trigger = Manual unless explicitly justified
Mode = Autopilot only for bounded task; Plan for risky task
Model = GPT-5 mini
Effort = Low
No Auto / No High / No Claude / No GPT-5.4 / No Codex/Kimi/Gemini/MAI
Prompt matches the task only
No unrelated governance/cost/policy contamination inside task prompt
```
If any required setting is unavailable: disable or delete the automation until it can be controlled.

---

## 11. Final Locked Sentence

```text
Automation stays.
Auto model selection dies.
Copilot stays GPT-5-mini-only.
GitHub Actions and scripts own recurring work.
Safe fixers may repair.
Verifiers judge.
No direct merge.
```
