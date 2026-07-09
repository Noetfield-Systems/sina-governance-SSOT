# L0 Repo Graph Memory — Maintenance & Upgrade Playbook v1

How to evolve the L0 repo-graph system across all installed repos **without drift**.
The whole point: L0 lives as a separate copy in each repo (no shared runtime), so
upgrades must be *propagated*, not hand-patched. This playbook + the sync tool make
that a one-command, sandbox-tested, driftless operation.

## The three pieces (single source of truth lives in this repo)

| Piece | Path | Role |
|---|---|---|
| Canonical template | `scripts/l0-graph-template/*.template.*` | the shared LOGIC (edit here, nowhere else) |
| Registry | `data/l0_repo_graph_registry_v1.json` | per-repo CONFIG + which repos are installed |
| Sync tool | `scripts/sync_l0_repo_graph_v1.py` | renders template+config → each repo, checks drift, rebuilds, verifies |
| Sandbox | `~/Desktop/Noetfield-Systems/sg-sandbox` | test bed — try upgrades here first |

Every installed copy (`scripts/build_repo_graph_v1.py` etc. in each repo) is a
**render** of template + that repo's registry config. The builder stamps
`template_version` into `graph-out/graph_index_v1.json` so drift is detectable.

## Golden rules

1. **Never hand-edit an installed copy's shared logic.** Edit the template. If you
   change a repo's subsystems/keyword, edit the registry. Then run the sync.
2. **Sandbox first.** Test every template change in `sg-sandbox` before `--apply`.
3. **Commit receipts.** Receipts that live only in a working tree vanish when the
   clone is deleted (learned the hard way: on the 2026-07-09 `~/Projects` cleanup,
   the 4 committed verify receipts survived, the 2 uncommitted ones did not). The
   L0 verify writes to `receipts/` — commit it. Do not gitignore L0 verify receipts.
4. **The index follows the registry's `index_strategy`.** Large/build-heavy repos
   (`gitignore`) commit only `GRAPH_REPORT.md`; small repos (`commit`) commit both.
5. **One PR per repo.** `main` is protected everywhere. The sync never commits.

## Task: upgrade the shared logic (found a new improvement)

Example: add real `ast`/JS-import edge parsing, or a new ignore dir.

```
# 1. edit the canonical builder logic
$EDITOR scripts/l0-graph-template/build_repo_graph.template.py
#    bump L0_TEMPLATE_VERSION (e.g. 1.1.0 -> 1.2.0) and the registry's template_version

# 2. SANDBOX FIRST — render into sg-sandbox, build, verify (see the tool's test path)
#    confirm build + queries pass before going wider

# 3. see who will change
python3 scripts/sync_l0_repo_graph_v1.py --check      # lists repos drifted from the new version

# 4. apply everywhere (renders + rebuilds + verifies each; NO commits)
python3 scripts/sync_l0_repo_graph_v1.py --apply

# 5. per repo: review diff, commit the L0 files (+ receipt), open PR, merge
#    (index committed or not per registry index_strategy)
```

## Task: add a new repo

```
# 1. add an entry to data/l0_repo_graph_registry_v1.json:
#    { name, path, subsystem_mode: "list"|"auto", subsystem_dirs|auto_exclude,
#      index_strategy: "commit"|"gitignore", verify_subsystem, verify_keyword, instruction_file }
#    - pick verify_subsystem = a dir that always exists (e.g. "data"/"src")
#    - pick verify_keyword = a token present repo-wide (e.g. "README")
#    - repos with no data/ dir: set verify_subsystem to a real one (studio-ide uses "src")

python3 scripts/sync_l0_repo_graph_v1.py --apply --repo <name>

# 2. add the broad-read gate to that repo's AGENTS.md (verify needs it — see below)
#    and a docs/L0_REPO_GRAPH_MEMORY_v1.md. If it has no receipts/ dir, create one.
# 3. if index_strategy=gitignore, add graph-out/graph_index_v1.json to its .gitignore
# 4. commit + PR
```

**Verify depends on the AGENTS.md gate.** 3 of the 12 checks assert the broad-read
gate + token-budget text is in `AGENTS.md`. A fresh repo (or the sandbox) will show
those 3 failing until the gate section is added. That is by design — the gate is
what makes agents actually use the graph.

## Task: update docs or memories

- Per-repo design doc: `docs/L0_REPO_GRAPH_MEMORY_v1.md` in each repo (repo-specific
  tuning). The gate text lives in each repo's `AGENTS.md`.
- Cross-repo memory: `~/.claude/.../memory/graphity-graph-is-l0-repo-graph-memory.md`
  and `canonical-workspace-location.md`. Update these when the install set or the
  canonical workspace changes.
- This playbook + the registry are the operational source of truth — keep them current.

## Task: remove a stale repo

```
# 1. delete its entry from data/l0_repo_graph_registry_v1.json  (it drops out of --check/--apply)
# 2. optional: strip the install from that repo
#      rm scripts/{build,query,verify}_*graph* graph-out/GRAPH_REPORT.md docs/L0_REPO_GRAPH_MEMORY_v1.md
#      remove the AGENTS.md gate section
# 3. if the whole clone is being deleted: FIRST confirm nothing unique is unpushed
#    (git log --branches --not --remotes) and commit/push any receipts you want to keep.
```

## Detecting & fixing drift routinely

`python3 scripts/sync_l0_repo_graph_v1.py --check` in CI or a weekly loop reports any
repo whose installed scripts have drifted from the current template version. Any
`[DRIFT]` line means someone hand-edited an install or a repo missed an upgrade —
re-`--apply` that repo and PR.
