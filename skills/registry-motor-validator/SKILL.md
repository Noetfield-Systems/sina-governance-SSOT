---
name: registry-motor-validator
description: >
  Run and interpret the two scripts that enforce this repo's "one writer per
  task cell" law (L1) and workflow-registration law (L4): a duplicate
  motor_id, an unregistered GitHub Actions workflow, or a missing required
  task cell is a live governance defect, not a style nit. Use this whenever
  the user asks to "validate the registry," "check the motors," "is anything
  unregistered," before registering a new GitHub Action / Cursor worker /
  Copilot workflow, before claiming any automation-surface change is DONE, or
  whenever a PR touches data/github_automation_registry_v1.json or
  data/automation_surface_inventory_v1.json. Wraps
  scripts/validate_parallel_automation_governance_v1.py and
  scripts/audit_automation_surface_v1.py so an agent can't claim a
  registry/workflow change is safe without actually running both and reading
  the real failures, not just assuming PASS.
compatibility: >
  Requires scripts/validate_parallel_automation_governance_v1.py,
  scripts/audit_automation_surface_v1.py, data/github_automation_registry_v1.json,
  data/automation_surface_inventory_v1.json, and ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md.
  Python 3.
---

# Registry / Motor Validator

`ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md` names five laws for this repo's
parallel-motor system; two scripts mechanically enforce the two laws that are
actually checkable from files on disk:

- **L1 (one writer per task cell)** and **L4 (registry is routing truth)** →
  `scripts/validate_parallel_automation_governance_v1.py`
- The fuller cross-repo picture (GH Actions, CF workers, Mac launchd, Copilot
  lanes) → `scripts/audit_automation_surface_v1.py`

Neither script fixes anything — they're read-only checks. Fixing a failure
means editing the registry/workflow files, then re-running to confirm.

## Running both

```bash
python3 scripts/validate_parallel_automation_governance_v1.py
python3 scripts/audit_automation_surface_v1.py
```

Both print a one-line verdict (`... ALL PASS` or `... FAIL` with a bulleted
list of errors to stderr/stdout) plus a small JSON summary of what was
checked. Run both, not just one — they check different things:
`validate_parallel_automation_governance_v1` is the strict registry-shape
check (duplicate motor_id, unregistered SG workflow, required task cells,
schema); `audit_automation_surface_v1` is the broader surface audit across
every repo in `data/automation_surface_inventory_v1.json` and writes its own
receipt (`automation-surface-audit-<UTC>`) as it goes.

## What a failure actually means

- **`duplicate motor_id: <id>`** — this is a live L1 violation: two motors
  registered under the same ID, which means the registry itself can no longer
  answer "who owns this." This is not a formatting issue; treat it the same
  way pr-conflict-resolver treats a same-task-cell merge conflict — don't
  silently rename one to make the error go away without knowing which
  registration is the real one.
- **`unregistered workflow: <path>`** — a `.github/workflows/*.yml` file
  exists that no entry in `github_automation_registry_v1.json`'s `motors`
  list points to. Per the governance doc's L4, an unregistered workflow is a
  defect by definition, even if the workflow itself is harmless — either
  register it (add a motor row, set `must_not_own` explicitly) or delete it.
  Don't leave it running unregistered "for now."
- **`<mid>: workflow missing <path>`** — the registry claims a motor's
  workflow file exists at a path that isn't actually there. Either the
  workflow was removed without updating the registry, or the registry entry
  has a typo'd path — both mean the registry is currently lying about what's
  real.
- **`repo path missing (skip disk check)`** (a warning from the surface
  audit, not an error) — one of the inventoried venture repos isn't present
  on this disk/session. Expected when running from an environment that
  doesn't have every venture repo checked out (e.g. a sandboxed session); not
  expected if this is the Mac session where all ventures normally live.

## Before registering something new

If the user is about to add a new GitHub Action, Cursor worker, or Copilot
workflow, walk the governance doc's checklist (§5) before writing anything:
pick a `motor_id` that doesn't collide with existing `owns` entries, add the
row to `github_automation_registry_v1.json`, set `must_not_own` explicitly,
then run both scripts above — don't register first and validate later.

## Reporting

State the real numbers from the JSON summaries (`motor_count`,
`task_cell_count`, `checked_workflows`, `warnings`) alongside PASS/FAIL, and
quote the exact error lines for anything that failed. "Validator passed" with
no numbers is a claim; the numbers plus the exit code are the receipt (L5).
