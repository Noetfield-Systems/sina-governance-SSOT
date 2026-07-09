# L0 Graph-First Operator Rule v1

**Status:** MANDATORY for future Architect / Claude Code workflows in this repo.
**Supersedes:** ad hoc / best-effort framing in `AGENTS.md` and
`docs/L0_REPO_GRAPH_MEMORY_v1.md` — this file is the one-page operator handoff;
those remain the design record and rationale.
**Applies to:** any broad architecture review, audit, repo/subsystem map, or
multi-agent reader workflow (Explore fan-out, `general-purpose` research agents,
Workflow-tool `parallel`/`pipeline` reader stages) run against
`sina-governance-ssot`.

## The rule

No broad architecture, audit, repo-map, or multi-agent reader workflow may start
by reading files directly. It must go through the graph first, in this exact
order:

1. **Refresh the graph if stale.** Rebuilding is a local, offline, sub-second,
   zero-token operation — when in doubt, just run it rather than judging
   staleness. (See "Staleness check" below if you want to skip a redundant
   rebuild.)
2. **Query the graph for the target task** — by subsystem name and/or keyword —
   before opening any file.
3. **Produce a compact file/subsystem map** from the report + query output
   (which files exist, how big, what references what) as the actual scoping
   artifact for the task.
4. **Only then** may reader agents be spawned (Explore, `general-purpose`,
   Workflow `parallel`/`pipeline` stages) — and only scoped to the specific
   files/subsystems the graph named in step 3, never "read everything under
   docs/ and data/" as a first move.

This was made mandatory by founder order after the Cloud Factory Substrate v0
architecture pass (`receipts/p0pgr/founder/founder-order-1000-plan-cloud-factory-20260709T014708Z.json`):
*"This must be the last blind multi-agent repo-understanding pass. Future
architecture/audit passes must use L0 Repo Graph Memory first, then only read
narrowed files."*

## Exact commands

**Build / refresh the graph:**
```
python3 scripts/build_repo_graph_v1.py
```
Writes `graph-out/graph_index_v1.json` (full index, queryable) and
`graph-out/GRAPH_REPORT.md` (compact map, read this first). Takes about a
second for the whole repo; safe to re-run any time.

**Query the graph:**
```
python3 scripts/query_repo_graph_v1.py <subsystem-name|keyword|path-fragment>
python3 scripts/query_repo_graph_v1.py --stats   # index-wide totals only
```
Subsystem names: `data`, `docs`, `ssot`, `scripts`, `receipts`, `p0-pgr`,
`cloud-factory`, `packages`, `policy`, `gates`, `ledger`, `proposals`, `reports`,
`tests`, `verifier`, `workers`, `.github`. Anything else is treated as a
keyword/path-fragment search over file paths and edges.

**Verify the graph is wired and current:**
```
bash scripts/verify_l0_repo_graph_memory_v1.sh
```
Rebuilds, checks both outputs exist and parse, checks the report has its
required sections, checks the timestamp is fresh, checks both query modes
work, and checks the broad-read-gate + token-budget rules are still present in
`AGENTS.md`. Writes a PASS/FAIL receipt to `receipts/`. Exit 0 = PASS.

**Staleness check** (optional — skip if you'd rather just rebuild):
```
python3 -c "import json; print(json.load(open('graph-out/graph_index_v1.json'))['generated_at'])"
git log -1 --format=%cI
```
If the last commit timestamp is newer than `generated_at`, or a new
subsystem/large batch of files was added since, refresh before querying.

## Example: Cloud Factory Substrate

Target task: "map the Cloud Factory Substrate architecture." Query the
`cloud-factory` subsystem before opening any of its five files:

```
$ python3 scripts/query_repo_graph_v1.py cloud-factory
# subsystem: cloud-factory  (files=5, bytes=112223)
  cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md  (32161B, ...)
  cloud-factory/SANDBOX_MANAGER_SPEC_v0.md  (22836B, ...)
  cloud-factory/MVP_ACTIVATION_PLAN_v0.md  (22543B, ...)
  cloud-factory/CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json  (17852B, ...)
  cloud-factory/FACTORY_LINE_REGISTRY_v0.json  (16831B, ...)
# edges touching cloud-factory/ (89)
  cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md -> p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md
  cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md -> data/cloud_line_registry_v1.json
  cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md -> cloud-factory/FACTORY_LINE_REGISTRY_v0.json
  cloud-factory/FACTORY_LINE_REGISTRY_v0.json -> data/machine_autonomy_loops_v1.json
  cloud-factory/FACTORY_LINE_REGISTRY_v0.json -> scripts/check_sandbox_walls_v0.py
  ... 84 more (see graph_index_v1.json)
```
Result: the scope is 5 files (~110KB) plus a named set of external
dependencies (p0-pgr runtime, `data/cloud_line_registry_v1.json`,
`scripts/check_sandbox_walls_v0.py`, `policy/repo_fences_v1.yaml`, etc.) — that
list, not a blind `docs/` + `data/` + `cloud-factory/` sweep, is what should be
handed to reader agents.

## Example: 1000-Plan Cloud Factory

Target task: draft the seven 1000-Plan Cloud Factory v1 deliverables
authorized in `receipts/p0pgr/founder/founder-order-1000-plan-cloud-factory-20260709T014708Z.json`
(`PLAN_FACTORY_ARCHITECTURE_v1.md`, `PLAN_SCHEMA_v1.json`,
`FACTORY_LINE_REGISTRY_v1.json`, `SANDBOX_WORKTREE_MANAGER_v1.md`,
`CLIENT_ORDER_TO_PLAN_PIPELINE_v1.md`, `PLAN_RANKING_ROI_MODEL_v1.json`,
`1000_PLAN_LIBRARY_SEED_v1.json`). None of these seven files exist yet — the
graph-first move here is checking what predecessor/brain material already
exists so the new deliverables build on it instead of re-deriving it blind:

```
$ python3 scripts/query_repo_graph_v1.py FACTORY_LINE_REGISTRY
# files matching 'FACTORY_LINE_REGISTRY' (1)
  cloud-factory/FACTORY_LINE_REGISTRY_v0.json  (16831B, ...)
# edges matching 'FACTORY_LINE_REGISTRY' (12)
  cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md -> cloud-factory/FACTORY_LINE_REGISTRY_v0.json
  cloud-factory/FACTORY_LINE_REGISTRY_v0.json -> data/cloud_line_registry_v1.json
  cloud-factory/FACTORY_LINE_REGISTRY_v0.json -> scripts/check_sandbox_walls_v0.py
  ...

$ python3 scripts/query_repo_graph_v1.py p0-pgr
# subsystem: p0-pgr  (files=6, bytes=14156)
  p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md  (4525B, ...)
  p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json  (2695B, ...)
  p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json  (2053B, ...)
  ...
```
Result: `FACTORY_LINE_REGISTRY_v1.json` is a version bump of an existing
16.8KB v0 file (read that one file, don't re-derive its schema from scratch),
and the "P0-PGR is the brain" principle in the founder order maps directly to
the 6-file, 14KB `p0-pgr/` subsystem — not something to rediscover via a
repo-wide search. `PLAN_SCHEMA_v1.json` / `SANDBOX_WORKTREE_MANAGER_v1.md` /
etc. have no existing matches (confirm with a query before drafting, not
assumption) — those are genuinely new files, not extensions of something
already indexed.

## What this rule does not change

- It does not block deep reads once the graph has named the relevant files —
  reading `cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md` in full after the query
  above named it is expected and correct.
- It is a convention enforced by instruction (`AGENTS.md`) and after-the-fact
  verification (`scripts/verify_l0_repo_graph_memory_v1.sh`), not a runtime
  hook — Claude Code has no tool-call interception point to block a broad read
  before it happens.
- It does not cover other repos (SourceA, NOOS, TrustField, Noetfield website,
  Studio IDE / Forge Factory) — rollout to those is planned but not executed;
  see `docs/L0_REPO_GRAPH_MEMORY_v1.md` § Rollout plan.
