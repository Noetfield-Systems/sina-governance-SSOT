# L0 Repo Graph Memory v1 (pilot)

**Status:** PILOT — scoped to `sina-governance-ssot` only. No deploy, no cloud schedule, no other repo touched.
**Owner:** SG (sina-governance-ssot) · **Related:** `docs/GRAPH_TOOL_DECISION_v1.md`, `receipts/GRAPHIFY_OR_GRAPHITI_PILOT_RECEIPT_v1.json`

## Problem

Claude Code / Architect / agents were repeatedly re-reading the full repo (docs, data
registries, receipts, scripts) to answer routing questions like "where does X live" or
"what touches Y" before doing any real work. The last multi-agent "understand repo"
pass burned ~371k tokens doing this. That cost is repeated on every session and does
not scale to Cloud Factory / 1000-plan execution, where dozens of agents each pay it
independently.

This repo is not a typical single-language application — it is dominated by Markdown
docs, JSON registries/receipts, and Python/shell scripts (703 files, ~3.9MB at time of
indexing, spread across 17 top-level subsystems). A generic import-graph tool built for
JS/TS/Java codebases does not model it well; what agents actually need is a compact,
static **subsystem + file + cross-reference map** they can query before opening files.

## What this pilot adds

A local, offline, stdlib-only **L0 repo graph memory layer**:

| Piece | Path |
|---|---|
| Graph builder (index command) | `scripts/build_repo_graph_v1.py` |
| Graph query command | `scripts/query_repo_graph_v1.py` |
| Full machine index (JSON) | `graph-out/graph_index_v1.json` |
| Compact human/agent report (Markdown) | `graph-out/GRAPH_REPORT.md` |
| Broad-read prevention + token budget rule | `AGENTS.md` (§ "L0 repo graph memory — read before broad reads") |
| Verifier | `scripts/verify_l0_repo_graph_memory_v1.sh` |

No external database, no Docker, no network calls, no LLM calls are required to build
or query the graph — see `docs/GRAPH_TOOL_DECISION_v1.md` for why Graphify and
Graphiti were evaluated and rejected for this pilot in favor of a small custom script.

This is **file-level graph memory** (what files exist, how big, who references whom).
It is distinct from and complementary to `data/governance_repo_map_v1.json` /
`data/governance_structure_tree_v1.json`, which are cross-repo **authority/ownership**
maps (who is allowed to write where across ventures), not file/token-level maps of
this repo's contents.

## How it works

1. `build_repo_graph_v1.py` walks the repo once (skipping `.git`, `node_modules`,
   `__pycache__`, build/dist output, etc.), and for each of the 17 subsystem
   directories (`data/`, `docs/`, `ssot/`, `scripts/`, `receipts/`, `p0-pgr/`,
   `cloud-factory/`, `packages/`, `policy/`, `gates/`, `ledger/`, `proposals/`,
   `reports/`, `tests/`, `verifier/`, `workers/`, `.github/`) records file path,
   size, and mtime.
2. For text files with extensions `.py .sh .md .json .yaml .yml .jsonc`, it
   regex-scans for repo-relative path references (e.g. a script's docstring
   pointing at `data/founder_canon_v1.json`) and records them as `edges` — a
   best-effort reference graph, not a real import/call graph, appropriate for a
   docs+data-heavy repo.
3. Output is two artifacts:
   - `graph_index_v1.json` — full detail, meant to be **queried**, not read whole.
   - `GRAPH_REPORT.md` — compact (~6KB) subsystem map + top files + edge count +
     ignored dirs + last-indexed timestamp, meant to be **read** at the start of
     any broad task.
4. `query_repo_graph_v1.py <subsystem-or-keyword>` returns a bounded (≤40 files,
   ≤30 edges) slice of the index — enough to route ("open these 3 files") without
   loading the rest.

## Rule: broad-read gate

> Before starting any "understand the repo", "map subsystem X", "architecture
> review", "audit Y", or similarly broad task, read `graph-out/GRAPH_REPORT.md` and
> run `scripts/query_repo_graph_v1.py <term>` for anything not already answered by
> the report. Only open individual files, or spawn Explore/general-purpose agents to
> read them, for files the graph query actually names as relevant. Do not spawn
> blind multi-agent "read everything under docs/ and data/" passes as a first step.

This is enforced as an instruction in `AGENTS.md`, not as a hook — Claude Code has no
built-in mechanism to block tool calls on file content, so this is a **read-the-map
first** convention, verified after the fact by `verify_l0_repo_graph_memory_v1.sh`
checking the instruction text is present, not by runtime interception.

## Token budget rule

- Orientation step (routing questions) should cost **roughly 2k-6k tokens**,
  measured, not guessed: `GRAPH_REPORT.md` is ~1.4k tokens (5.7KB), and query
  responses measured at build time ranged from ~0.7k tokens (`query founder_canon`,
  a narrow keyword) to ~2.1k tokens (`query data`, the largest subsystem at 231
  files) — a report read plus 1-3 targeted queries lands in the 2k-6k range
  depending on which subsystems are touched.
- Only after the graph has named specific files should an agent read those files in
  full, or a broad-reader subagent be spawned — and it should be scoped to the named
  files/subsystem, not the whole repo.
- If a task genuinely requires reading most of a subsystem (e.g. a real content
  audit), that is expected to cost real tokens — the graph's job is to avoid paying
  that cost **just to find out where to look**.

## Maintenance

The graph is a point-in-time snapshot (`generated_at` timestamp in both output
files). Rebuild with `python3 scripts/build_repo_graph_v1.py` after adding a new
subsystem or a large batch of docs/data files; a few days of drift on receipts/data
churn is acceptable since those are usually queried by exact keyword (e.g. an
artifact id), not by fresh listing.

## Rollout plan (not executed in this pilot)

Pilot is scoped to `sina-governance-ssot` only per the architect order (no deploy,
no cloud schedule, no other repo touched). If the pilot verifier stays green and the
token-reduction estimate in the pilot receipt holds up in real sessions, the same
three files (`build_repo_graph_v1.py`, `query_repo_graph_v1.py`, an `AGENTS.md`/
`CLAUDE.md` broad-read-gate section) can be copied into each target repo with only
the `SUBSYSTEM_DIRS` list edited to match that repo's actual top-level layout:

| Repo | Path | Notes for rollout |
|---|---|---|
| SourceA | `~/Projects/SourceA` | Brain/Worker code — likely has real Python import edges in addition to path-string edges; consider extending edge scan to parse `import`/`from` statements with `ast` before rollout. |
| NOOS | `~/Projects/noetfeld-os` | Doctrine + integrator state; subsystem list will differ (doctrine/, integrator/, etc. — confirm actual top-level dirs before copying). |
| TrustField loops | `~/Desktop/trustfield-loops` | Cloud loop registries/receipts — similar shape to this repo (docs/data/receipts heavy); low-risk next pilot. |
| Noetfield website | `~/Desktop/Noetfield/.../Noetfield/` | Likely a JS/TS app — `SUBSYSTEM_DIRS` and edge-scan extensions need `.ts/.tsx/.jsx` added, and real import-statement parsing would add more value here than in the SSOT repos. |
| Studio IDE / Forge Factory repos | (not yet located in this session) | Confirm repo paths and top-level layout first; do not assume the same subsystem list applies. |

Each rollout repo should get its **own** `scripts/build_repo_graph_v1.py` /
`graph-out/` — this is intentionally not a shared cross-repo service (no deploy, no
central DB), consistent with the "do not deploy" constraint on this pilot.
