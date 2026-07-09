# Migration record — Projects clone → canonical Desktop workspace (2026-07-08)

**What happened:** a full day of `sina-governance` work was done in the wrong clone,
`~/Projects/sina-governance-ssot`, instead of the canonical workspace
`~/Desktop/Noetfield-Systems/sina-governance-SSOT`. Both were divergent clones of the
same GitHub repo (`Noetfield-Systems/sina-governance-SSOT`), each with unique work, so
the fix was git-native (preserve + relocate), **not** a filesystem overwrite. Nothing
was deleted.

## Where the wrong-place output now lives (three copies, zero loss)

| Location | Ref | Notes |
|---|---|---|
| Canonical Desktop clone | branch `cursor/machine-autonomy-loops-v1` | fetched in, tree-hash verified identical to source |
| GitHub | `origin/cursor/machine-autonomy-loops-v1` @ `2f2f38b` | pushed `51a9ae9..2f2f38b` |
| Archived source | `~/Projects/sina-governance-ssot.MIGRATED-2026-07-08` | kept as backup, not deleted |

- **Merge base** (where the two clones diverged): `5d08b68` (2026-07-03).
- **WIP snapshot commit** capturing the day's 785 loose files: `2f2f38b`.
- Undo point (pre-WIP HEAD of the wrong clone): `8df5e4e`.

## The output, organized (523 files unique to the wrong-place branch)

Headline deliverables (the actual work product):

| Deliverable | Path (on `cursor/machine-autonomy-loops-v1`) |
|---|---|
| Cloud Factory Substrate v0 (5 files) | `cloud-factory/` — `CLOUD_FACTORY_SUBSTRATE_v0.md`, `SANDBOX_MANAGER_SPEC_v0.md`, `MVP_ACTIVATION_PLAN_v0.md`, `CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`, `FACTORY_LINE_REGISTRY_v0.json` |
| 1000-Plan Factory v1 (8 files) | `plan-factory/` — `PLAN_FACTORY_ARCHITECTURE_v1.md`, `PLAN_SCHEMA_v1.json`, `FACTORY_LINE_REGISTRY_v1.json`, `PLAN_RANKING_ROI_MODEL_v1.json`, `PLAN_LIBRARY_SEED_1000_v1.json`, `CLIENT_ORDER_TO_PLAN_PIPELINE_v1.md`, `SANDBOX_WORKTREE_MANAGER_v1.md`, `PLAN_FACTORY_ACTIVATION_PLAN_v1.md` |
| Founder Canon v1 | `ssot/FOUNDER_CANON_v1.md`, `data/founder_canon_v1.json`, `scripts/validate_founder_canon_e2e_v1.py` |
| Machine Autonomy Loops v1 | `ssot/MACHINE_AUTONOMY_LOOPS_v1.md`, `data/machine_autonomy_loops_v1.json`, `scripts/run_machine_autonomy_cycle_v1.py` |
| NOOS Integrator Rules v1 | `ssot/NOOS_INTEGRATOR_RULES_v1.md`, `packages/noos-control-desk-v1/` |
| L0 Repo Graph Memory | `scripts/build_repo_graph_v1.py`, `scripts/query_repo_graph_v1.py`, `graph-out/` — **activated separately on the working branch** (see below) |
| Founder orders (audit trail) | `receipts/p0pgr/founder/` — 1000-plan / cloud-factory directives (2026-07-09) |

Breakdown by subsystem: data 225, packages 119, receipts 94, scripts 31, docs 23,
ssot 10, plan-factory 8, cloud-factory 5, reports 2, graph-out 2, .github 2, tests 1,
policy 1.

## Status / next step

- The whole body of work is **preserved and on GitHub** as a branch. It is **not yet
  merged** into the working line (`cursor/language-layer-v1`) — that integration was
  deliberately deferred (founder chose "preserve & relocate, merge later").
- The **L0 Repo Graph Memory** subsystem was pulled forward onto the working branch and
  activated there (verified green, 5,401 files / 19 subsystems) — see
  `docs/L0_GRAPH_FIRST_OPERATOR_RULE_v1.md`.
- To integrate the rest later, from this clone:
  `git checkout cursor/language-layer-v1 && git merge cursor/machine-autonomy-loops-v1`.
