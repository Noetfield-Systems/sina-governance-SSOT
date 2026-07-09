# COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md

**Status:** LOCKED POLICY ARTIFACT  
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

Exceptions are not normal workflow.

Any non-`GPT-5 mini` model requires a separate explicit exception with:

```text
reason
task_id
model
max_cost
max_tokens
expiry
receipt
```

No permanent exception.  
No silent fallback.  
No Auto.

---

## 2. Effort Lock

### Default

```text
Low
```

### Allowed only by explicit task need

```text
Medium
```

Only for manual diagnosis or bounded repair when `Low` clearly cannot complete the task.

### Forbidden by default

```text
High
Extra High
Unknown effort
Auto effort
```

---

## 3. Trigger Lock

### Copilot automation default

```text
Manual
```

### Forbidden by default for Copilot automations

```text
Hourly
Daily
Weekly
Background
Keep awake
Unpinned schedule
Autopilot recurring
```

### Scheduled work belongs to

```text
GitHub Actions
repo scripts
cost-policy scanners
deterministic validators
receipt validators
model:none jobs
```

---

## 4. Mode Lock

### Autopilot is allowed when all are true

```text
Trigger = Manual
Model = GPT-5 mini
Effort = Low
Task is bounded
Task is read-only OR safe-fix scoped
No direct merge
No premium tools
No background process
```

### Use Plan mode when

```text
deployment
production risk
model routing change
secrets/provider config
governance/SSOT change
database/runtime migration
unclear blast radius
```

### Interactive mode

Use only when human collaboration is intentionally needed.  
Do not use Interactive as a hidden permission loop for normal machine work.

---

## 5. Workflow Classes

### A. Manual Read-Only Diagnostics

Examples:

```text
Manual bug triage and root cause
Manual runtime contract review
Manual evidence pack audit
Manual PR readiness review
Manual release readiness
Manual proof demo audit
Manual deployment boundary audit
```

Settings:

```text
Trigger: Manual
Mode: Autopilot
Model: GPT-5 mini
Effort: Low
Edits: No
PR/issues: No unless prompt explicitly asks
Output: diagnosis / state / one next machine action
```

---

### B. Manual Planning

Examples:

```text
Manual implementation plan
Manual commercial unblock
Manual roadmap reconciliation when run manually
```

Settings:

```text
Trigger: Manual
Mode: Plan
Model: GPT-5 mini
Effort: Low
Edits: No
Output: plan only
```

---

### C. Safe Auto-Fix

Safe auto-fix is allowed. The system should not be report-only forever.

Allowed safe fixes:

```text
lint
format
broken links
small YAML correction
missing receipt fields
schema field mismatch
stale mirror sync
docs-truth typo
cost-policy config patch
non-dangerous CI fix
```

Settings:

```text
Trigger: Manual or audit-triggered by machine artifact
Mode: Autopilot
Model: GPT-5 mini
Effort: Low
Scope: explicit allowed files/paths
Output: bounded branch/PR + receipt
Merge: never direct
Verifier: required
```

---

### D. High-Risk Repair

Examples:

```text
deploy workflows
runtime kernel
secrets
provider config
model router
governance/SSOT
database migration
production behavior
```

Settings:

```text
Trigger: Manual
Mode: Plan first
Model: GPT-5 mini
Effort: Low or Medium by exception
Edits: only after plan passes machine policy
Merge: never direct
```

---

### E. Recurring Observers

Recurring observers should normally be GitHub Actions / scripts, not Copilot Automations.

Examples:

```text
daily repo health
daily autorun status
daily proof evidence drift
daily production surfaces health
weekly docs integrity
weekly security dependency review
weekly live sync gate
workflow failure summary
artifact cleanup
cost policy scan
receipt validation
```

Settings:

```text
Engine: GitHub Actions / script
Model: none
LLM: not used by default
Output: artifact / receipt / issue only if needed
```

If a recurring observer truly requires language interpretation:

```text
Engine: GitHub Actions triggers a bounded GPT-5-mini job
Model: GPT-5 mini
Effort: Low
Frequency: justified
Receipt: required
Budget: capped
```

Copilot scheduled Autopilot remains forbidden by default.

---

## 6. NOOS Integrator Sync Rule

Integrator sync is machine coordination, not human reporting.

Preferred owner:

```text
repo-local NOOS integrator script
GitHub Actions model:none
configured NOOS cloud runner if available
```

Copilot may assist only as a manual diagnostic or scoped repair worker.

### Integrator local exit rule

Any repo/session/agent that changes integrator state must run sync before stopping:

```bash
python3 scripts/noos_integrator_sync_v1.py sync
python3 scripts/noos_integrator_sync_v1.py summary --json
```

### Home mirror rule

Home mirror is a shared local coordination copy.

It may be stale if the last real session was many hours ago.  
It is a problem only when current repo-local state is newer and the actor exits without syncing.

### Cloud owner rule

Cloud owner may be:

```text
NOOS GitHub/Copilot automation
GitHub Actions
Cloudflare Worker
NOOS cloud orchestrator
```

Only one cloud owner may be authoritative at a time.

---

## 7. Copilot Coordination Sessions

Purple Copilot sync sessions may be useful coordination workers.

They may coordinate through:

```text
issues
PRs
branches
receipts
repo files
home mirror state
integrator state
```

They are allowed only when pinned:

```text
Trigger: Manual unless justified
Model: GPT-5 mini
Effort: Low
Mode: Autopilot only for bounded work
No Auto
No GPT-5.4
No Claude
No High effort
```

Do not delete useful coordination blindly.  
Pin it, cheapen it, scope it.

---

## 8. Automation Inventory Requirement

A cost audit is incomplete unless it checks the actual Copilot automation UI state.

Repo scans alone are insufficient.

Required audit surfaces:

```text
Copilot app Automations list
each automation Trigger
each automation Mode
each automation Model
each automation Effort
each automation Workspace
each automation last run
session logs showing model changes
GitHub Actions workflows
repo scripts
cloud cron
secrets/provider availability
model router fallback behavior
```

Any automation showing:

```text
Auto
GPT-5.4
Claude
Codex
Gemini
Kimi
MAI-Code
High
Extra High
Unknown model
Unknown effort
```

is `COST_POLICY_FAIL`.

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
| Workflow effectiveness summary | Scheduled if needed | script first | none / GPT-5 mini Low only | Low | GitHub Actions |
| Deploy | Manual | Plan/gate | none / GPT-5 mini only for review | Low | GitHub Actions + gates |

---

## 10. Safe Repair Pipeline

Audits should not only report forever.

Correct loop:

```text
audit detects defect
classifier decides safe/risky
safe fixer patches bounded defect
verifier runs tests/gates
PR/receipt created
no direct merge
```

Short law:

```text
Audits observe.
Safe fixers repair.
Verifiers judge.
GitHub Actions automate.
Copilot stays pinned to GPT-5 mini.
```

---

## 11. UI Checklist for Every Copilot Automation

Before saving any Copilot automation, check:

```text
Trigger = Manual unless explicitly justified
Mode = Autopilot only for bounded task; Plan for risky task
Model = GPT-5 mini
Effort = Low
No Auto
No High
No Claude
No GPT-5.4
No Codex/Kimi/Gemini/MAI
Prompt matches the task only
No unrelated governance/cost/policy contamination inside task prompt
```

If any required setting is unavailable:

```text
Disable or delete the automation until it can be controlled.
```

---

## 12. Activation Rule

This file is active when placed in the relevant SSOT/repo policy location and referenced by automation configuration reviews.

Recommended path:

```text
.noetfield/COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md
```

Suggested policy pointer line:

```text
COST LAW: COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1. Default Copilot model is GPT-5 mini Low. No Auto. No GPT-5.4. No Claude.
```

---

## 13. Final Locked Sentence

```text
Automation stays.
Auto model selection dies.
Copilot stays GPT-5-mini-only.
GitHub Actions and scripts own recurring work.
Safe fixers may repair.
Verifiers judge.
No direct merge.
```
