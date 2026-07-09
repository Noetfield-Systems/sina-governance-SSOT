# SMART_PRODUCTION_COST_LAW_v2.md

**Status:** SCAFFOLD_READY_AUDIT_PENDING
**Version:** 2.0.0 (Machine-Enforced, Verification Pending)
**Date:** 2026-07-03
**Core Objective:** Deterministic refusal conditions, zero-token-by-default automation, and enforced operational boundaries across the multi-repo fleet.

---

## 0. Executive Summary (status-grounded)

The transition from conceptual design to a **machine-enforced scaffold** has been completed. Runtime activation is strictly pending a physical workflow audit and a passing self-scan — it is not yet "production reality," and this document does not claim otherwise.

The validation suite proves its rules via negative-test execution (9/9 cases pass as of this version — see `receipts/`). The architecture is currently, correctly, flagged **SCAFFOLD_READY_AUDIT_PENDING**: the checker rejects the active registry because all 23 seeded workflows are initialized with `last_audited: TODO`. This is by design — the system refuses to let a newly declared registry claim audited status without physical verification.

## 1. The Policy Hierarchy (formalized)

This law does not compete with or suppress the Copilot-specific cost profile. It binds it as a named sub-policy:

- **Level 1 — Master Law:** `SMART_PRODUCTION_COST_LAW_v2.md` (this file). Owns global routing, GitHub Actions, Cloudflare, NOOS state gates, workflow classes, and the six refusal conditions.
- **Level 2 — Sub-Policy Module:** `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md`. Retains sole ownership of the specific Copilot UI toggle values (model, effort, trigger, mode) referenced by this law but detailed there.
- **Level 3 — Control Ledger:** `.noos/workflow_registry_v1.json`. The machine-readable target matrix mapping all 23 seeded workflows across the fleet.

If Level 1 and Level 2 ever disagree on a Copilot-specific setting, Level 2 wins for that setting (it's the more specific document); Level 1 wins on everything structural (classes, registry schema, budgets, refusal conditions).

## 2. The Sovereign Stack Layers

```
             ┌────────────────────────────────────────┐
             │       GitHub Actions Engine            │
             │       - Heavy Automation Exec          │
             │       - Strict Minute Capping          │
             └───────────────────┬────────────────────┘
                                 │
                     [Deterministic Execution]
                                 │
                                 ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  Cloudflare Always-On Control Plane                  │
│  - Micro-Routing & Global Cron Orchestration                         │
│  - State Ledger Monitoring & Cumulative Circuit Breakers             │
└────────────────────────────────┬─────────────────────────────────────┘
                                 │
                       [State Synchronization]
                                 │
                                 ▼
             ┌────────────────────────────────────────┐
             │         NOOS Integrator State          │
             │       - Workspace Coordination         │
             │       - Strict Local Exit Hooks        │
             └───────────────────┬────────────────────┘
                                 │
                       [Escalated Novel Anomaly]
                                 │
                                 ▼
             ┌────────────────────────────────────────┐
             │        Manual Copilot Sandbox         │
             │       - GPT-5 mini / Low Effort        │
             │       - UI Attestation Required        │
             └────────────────────────────────────────┘
```

- **Layer A — GitHub Actions:** default heavy automation engine. `model:none` baseline. Every workflow executes deterministic code unless routed through an authorized cost gateway.
- **Layer B — Cloudflare:** always-on control plane. Ultra-cheap compute (Workers, Cron Triggers, KV, D1, Queues) synchronizes ledger state, manages execution frequency, and evaluates circuit breakers without token overhead.
- **Layer C — NOOS Integrator:** the **coordination authority** for repo-local, home-mirror, and configured cloud-mirror state (not an "absolute authority" — the active cloud owner can shift between GitHub Actions and Cloudflare depending on active system clustering). Every active agent/session mutation must invoke the local integrator sync hook on exit.
- **Layer D — Copilot Automations:** sandboxed, non-autonomous diagnostic workers. Manual triggers only, narrow operational profiles. They do not own loops, cannot trigger continuous deployment, and cannot choose models autonomously.

## 3. The Six Machine Refusal Conditions

1. **Global Registry Collision Prevention** — every entry needs a globally unique `workflow_id` bound to `single_owner_lock`. Duplicate resource claims trip an immediate validation failure. *(checker rule: `RCP2_unique_workflow_id`)*
2. **Mandatory Safe-Fixer Receipts** — `safe_fix_allowed: true` without `receipt_required: true` is a hard rejection at validation time, not an audit-time surprise. *(checker rule: `RCP1_safe_fix_needs_receipt`)*
3. **Cumulative Rate Limiting & Circuit Breakers** — global daily budget caps and PR/task caps block execution lines when cumulative invocation thresholds are exceeded, independent of any single call looking cheap. *(policy: `budgets` block)*
4. **GitHub Actions Execution Accounting** — Actions minutes are metered like a token budget, not treated as free infrastructure. *(policy: `github_actions_daily_minutes_cap`)*
5. **Immutable Leash Governance** — no automated workflow may edit `policy/cost_policy.yaml`, `scripts/check_cost_policy.py`, or the registry itself. Changes to this law require the same Verify-class gates as any other governance change.
6. **Audit Staleness Decay** — every registry entry needs a valid `last_audited` date; entries older than 30 days (or still `TODO`) are flagged, not silently trusted. *(checker rule: `RCP5_audit_staleness`)*

## 4. Workflow Class Taxonomy

| Class | Primary Engine | Model Policy | Safety Gate | Primary Output |
|---|---|---|---|---|
| 1: Observe | GHA / Cloudflare Cron | `model:none` | Immutable state | Machine-readable JSON + receipt |
| 2: Triage | Manual Copilot | `gpt-5-mini-low` | Low effort only | Root-cause analysis + single next machine action |
| 3: Safe Fix | Bounded GHA script or Copilot manual | `model:none` / `gpt-5-mini-low` | Never direct merge | Isolated patch branch + PR + schema-validated receipt |
| 4: Verify | GitHub Actions gates | `model:none` | Independent verification | Binary PASS/FAIL + receipt |
| 5: Deploy | GHA pipeline + host | `model:none` | Direct-merge block, gate-only promotion | Verified release + deploy receipt |
| 6: Reconcile | NOOS Integrator | `model:none` first | Workspace sync | Synchronized mirrors, consistent global state |
| 7: Circuit Breaker *(governor, not a worker)* | GHA or Cloudflare Worker | `model:none` | Rate governance | Halt signal when aggregate caps exceeded |

## 5. Copilot Execution & UI Attestation Rule

```text
Allowed:    gpt-5-mini (Low effort, Manual trigger, Autopilot for read-only/safe-fix)
Forbidden:  Auto-model selection, GPT-5.4, Claude, Gemini, Kimi, High/Extra High effort, scheduled Autopilot
```

Full toggle-level detail (mode lock, exception format, per-automation-type settings blueprint) lives in the Level 2 sub-policy: `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md`. This section states the boundary; that file states the exact UI values.

> ### ⚠️ Copilot UI Attestation Rule
> Copilot UI settings are external-unreadable by the current checker, so they require **UI-attested configurations, bootstrapped manually until a machine-readable Copilot automation inventory bridge exists.**
>
> Manual UI audit is our temporary bootstrap mechanism; machine-readable attestation remains the design target. Checking the UI by hand is a bridge, not permanent doctrine — it stays only until an export/API/screenshot-parser bridge exists, and this document should be re-patched the day that bridge ships.

## 6. Cost Intelligence Lock & Registry Specification

`.noos/workflow_registry_v1.json` is the authoritative ledger of allowed processes. Schema contract (draft-07 style, matching `policy/cost_policy.yaml`'s `registry_schema`):

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "NOOSWorkflowRegistry",
  "type": "object",
  "required": ["workflows"],
  "properties": {
    "workflows": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "workflow_id", "repo", "class", "owner", "trigger",
          "model_policy", "writes", "risk", "receipt_required",
          "safe_fix_allowed", "escalation", "last_audited"
        ],
        "properties": {
          "workflow_id": { "type": "string" },
          "repo": { "type": "string" },
          "class": { "type": "string", "enum": ["observe", "triage", "safe_fix", "verify", "deploy", "reconcile"] },
          "owner": { "type": "string", "enum": ["github_actions", "cloudflare_worker", "copilot_manual", "noos_integrator"] },
          "trigger": { "type": "string", "enum": ["schedule", "manual", "event"] },
          "model_policy": { "type": "string", "enum": ["model:none", "gpt-5-mini-low"] },
          "writes": { "type": "string", "enum": ["artifacts_only", "branch_pr", "direct"] },
          "risk": { "type": "string", "enum": ["low", "medium", "high"] },
          "receipt_required": { "type": "boolean" },
          "safe_fix_allowed": { "type": "boolean" },
          "escalation": { "type": "string" },
          "last_audited": { "type": "string" }
        }
      }
    }
  }
}
```

**Receipt scope note (corrected):** receipts produced by this system are **schema-validated receipts** — a receipt is trusted because its structure and required fields validate against the schema above, and because an independent verifier ran the check. This is not a claim of cryptographic signing; no HMAC or ledger-anchoring signature exists yet. If that capability is added later, this section gets patched then, not before.

## 7. The Failure-Aggregating Checker

`scripts/check_cost_policy.py` runs a **candidate failure-aggregating checker loop**: it walks every registry entry and every scanned file, collects *every* violation found, and reports the full list in one pass — it does not stop at the first failure. This matters for a 23+ workflow fleet: an early-exit checker would force 23 separate fix-rerun cycles instead of one visible worklist.

Core loop shape (see the actual script for the complete implementation, including text-pattern scanning and exception handling):

```python
errors = []
seen_workflow_ids = set()

for wf in registry.get("workflows", []):
    w_id = wf.get("workflow_id", "UNKNOWN_ID")

    if w_id in seen_workflow_ids:
        errors.append(f"[RULE_COLLISION] '{w_id}' duplicated - single_owner_lock violated.")
    else:
        seen_workflow_ids.add(w_id)

    if wf.get("last_audited") == "TODO":
        errors.append(f"[STALE_AUDIT] '{w_id}' still has placeholder audit timestamp.")

    if wf.get("safe_fix_allowed") and not wf.get("receipt_required"):
        errors.append(f"[RECEIPT_MISSING] '{w_id}' allows safe-fix without a required receipt.")

    # ...30-day decay check, schema checks, etc. - full logic in the script itself.

# Nothing short-circuits here: every entry is checked, every violation is collected.
```

Status this law reports is never "PASS" unless `errors` is empty across the **entire** registry, not just the first entry checked.

## 8. Future Horizon: Shadow State Ledger (SSL) — deferred

Implementation of a Shadow State Ledger (hash-indexed failure signatures → deterministic fix lookup) is deferred to Phase 3/4. We will not write hashing/lookup logic over a registry that hasn't itself passed clean validation yet — that would be building a recovery engine on top of unverified state, which is the exact class of mistake this law exists to prevent.

```text
[Observe Failure Signature] --> [Lookup Hash in D1 Ledger] --> [Execute Deterministic Script Fix]
```

Parked until the registry is genuinely green.

## 9. Master Fleet Rollout Sequence

```
[Deploy to sina-governance-SSOT] --> [Manual UI Audit] --> [Green Self-Scan] --> [Distribute Fleet Mirrors]
```

**Step 1 — Initialize Core Authority.** Install this file, `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md`, `policy/cost_policy.yaml`, `.noos/workflow_registry_v1.json`, and the script suite directly into `sina-governance-SSOT`.

**Step 2 — Establish Registry Sandbox State.** Repo status stays `SCAFFOLD_READY_AUDIT_PENDING`. Do not run live automation modifications while self-scan is reporting placeholder errors.

**Step 3 — UI Settings Reconciliation.** Perform a comprehensive audit of the 23 seeded workflows across the five repos (`sina-governance-SSOT`, `noetfeld-os`, `SourceA`, `Noetfield`, `TrustField-Technologies`) to populate the registry with **UI-attested configurations, bootstrapped manually until a machine-readable Copilot automation inventory bridge exists.** Inspect: GitHub Actions workflow parameter files, the actual Copilot Automations UI panel (trigger/mode/model/effort), and active Cloudflare cron parameters.

**Step 4 — Pass the Systemic Validation Gate.** Replace `TODO` placeholders with real ISO date strings (`YYYY-MM-DD`). Run:
```bash
python3 scripts/check_cost_policy.py . --json receipts/self_scan_v2.json
```

**Step 5 — Activate and Mirror Fleet.** Only when self-scan returns a clean PASS may the status flag move to `ACTIVE`. Then copy the validated checker and config to the remaining repos to lock the fleet.

## 10. Final Operating Law

```
GitHub Actions automate.
Cloudflare coordinates.
NOOS Integrator is coordination authority, not absolute authority.
Copilot assists manually, gpt-5-mini-low only, UI-attested until a real bridge exists.
model:none is default for scheduled jobs.
Safe fixers repair; every safe fixer emits a schema-validated receipt or is not registered.
Verifiers judge independently and aggregate every failure, not just the first.
A circuit breaker governs aggregate rate, not just per-call cost.
No workflow_id is owned by two automations at once.
No automation edits its own cost policy.
No direct merge. No founder runtime.
Status stays SCAFFOLD_READY_AUDIT_PENDING until the self-scan is actually green.
```
