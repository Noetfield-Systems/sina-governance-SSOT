# Graph Tool Decision v1 — L0 Repo Graph Memory pilot

**Decision:** custom stdlib-only local script (`scripts/build_repo_graph_v1.py` +
`scripts/query_repo_graph_v1.py`), not Graphify, not Graphiti.
**Date:** 2026-07-09 · **Scope:** `sina-governance-ssot` pilot only.
**Research method:** two independent web-grounded research passes (WebSearch/WebFetch
against primary sources — GitHub repos, GitHub API, package registries, project docs),
run in parallel, verifying claims rather than trusting training-data memory or
third-party marketing pages. Full findings archived in this session's workflow journal
(`wf_0efc0ed2-99b`); summarized below.

## Hard constraints (from the architect order)

1. No new deployed service, container, or database.
2. No cloud schedule / background daemon.
3. No paid or external LLM API calls just to *build* the index (defeats the point of
   a pilot meant to reduce token/cost burn).
4. Fully local/offline, CLI-scriptable, static git-diffable output (JSON + Markdown).
5. "Equivalent local repo graph tool if safer" is explicitly pre-approved as a
   fallback — there is no obligation to force-fit either named candidate.

## Candidate 1: Graphify — REJECTED

"Graphify" turned out to name three distinct, unrelated real projects. Verified via
GitHub, GitHub API, and package registries (npm/PyPI):

- **kbastani/graphify** (neo4j-contrib lineage): archived since 2020. A Neo4j
  unmanaged extension that uses Stanford CoreNLP to classify unlabeled text via
  graph-based pattern recognition. It is a document classifier, not a code/repo graph
  indexer, and requires standing up a Neo4j server + JVM + Maven + CoreNLP models —
  violates constraint 1 outright, and is unmaintained besides.
- **neo4j-contrib/graphify**: a near-empty 2013 stub, 0 stars, not a working tool.
- **rhanka/graphify** (npm `@sentropic/graphify`, PyPI `graphifyy`): the one that
  actually matches "repo graph for AI agents" — created April 2026, tree-sitter-based
  code parsing plus *optional* LLM calls for docs/images/papers/entity
  reconciliation, emitting `.graphify/graph.json`, `GRAPH_REPORT.md`, and a compiled
  HTML "studio". Verified via the GitHub API at **12 real stars** — multiple
  third-party marketing pages (graphify.net, augmentcode.com, skillsllm.com, dev.to)
  report fabricated counts of 58K–80K stars for this same 3-month-old repo. That
  inconsistency is an unresolved trust red flag independent of the technical
  evaluation, for a tool that would hook into the agent's own tool-call flow.

Even setting the trust concern aside, rhanka/graphify fails on fit: this repo is
dominated by Markdown docs and JSON registries/receipts, not import-graph-rich code.
Graphify's zero-LLM path (tree-sitter) only covers the small `scripts/` slice;
extracting anything useful from the docs/JSON majority requires its LLM-driven
extraction/reconciliation path — violating constraint 3. It also adds a new Node.js
runtime + global package install to a Python/shell/JSON repo, and its natural feature
set (`graphify watch` daemon mode, optional live Neo4j push) trends toward exactly the
daemon/service footprint constraint 2 excludes.

**Verdict: reject**, for both the archived NLP-classifier lineage (wrong domain, needs
a DB) and the active tree-sitter tool (LLM-dependent for the majority of this repo's
content, new runtime dependency, unresolved credibility issue on its own metrics).

## Candidate 2: Graphiti (getzep/graphiti, `graphiti-core`) — REJECTED

Verified via the project's GitHub repo and docs. Graphiti is a temporally-aware
knowledge graph framework for **LLM agent memory over conversational/document
episodes** — it ingests episodes, uses an LLM with structured output to extract
entities and fact triplets, and writes them to a graph database with temporal
validity windows. It supports hybrid retrieval (semantic + BM25 + graph traversal).

- **Infra**: requires a running graph database — Neo4j 5.26+ (default), FalkorDB (via
  Docker), or Amazon Neptune. The one embedded/serverless option, Kuzu, is called out
  in Graphiti's own docs as deprecated/being phased out. There is no supported
  flat-file-only deployment. Violates constraint 1 directly.
- **LLM calls**: mandatory, not optional — every ingested episode costs at least one
  LLM structured-output call for entity/edge extraction (~0.5–2s each), plus further
  calls for deduplication and summarization on incremental updates. Concurrency is
  deliberately throttled via `SEMAPHORE_LIMIT` specifically to respect LLM provider
  rate limits — underscoring how central the dependency is. Violates constraint 3
  directly, and would scale with corpus size and every re-index.
- **Domain mismatch**: built for facts that become true/invalid over time in
  conversation/document memory, with no code-aware parsing (no AST/import-graph/
  tree-sitter support) — not a fit for representing static file trees, JSON registry
  contents, or script relationships.

**Verdict: reject** — fails constraints 1 and 3 simultaneously and independently, on
top of a semantic mismatch with what this pilot actually needs (a static structure
map, not an evolving fact graph).

## Candidate 3: custom local script — CHOSEN

A small stdlib-only Python script pair:

- `scripts/build_repo_graph_v1.py` — walks the repo (skipping `.git`, `node_modules`,
  `__pycache__`, build/dist output), records per-subsystem file inventories
  (path/size/mtime) for the 17 top-level subsystem directories, and regex-scans
  `.py/.sh/.md/.json/.yaml/.yml/.jsonc` files for repo-relative path references as a
  best-effort edge graph. Emits `graph-out/graph_index_v1.json` (full detail, meant
  to be queried) and `graph-out/GRAPH_REPORT.md` (compact, ~6KB, meant to be read).
- `scripts/query_repo_graph_v1.py` — bounded lookups (≤40 files, ≤30 edges per query)
  by subsystem name or keyword/path fragment against the JSON index.

This satisfies every constraint the other two candidates failed on: zero deploy, zero
daemon, zero LLM calls to build or query, fully offline, plain CLI, output is pure
git-diffable JSON + Markdown. It is also a better structural fit — this repo's graph
is dominated by docs/data/receipts, and what agents need from it is "what exists,
how big, what references what," not semantic entity extraction or AST-level import
graphs (which would matter more for a rollout target like the Noetfield website — see
`docs/L0_REPO_GRAPH_MEMORY_v1.md` § Rollout plan).

## What would change this decision

- If a rollout target is a large, single-language codebase (e.g. the Noetfield
  website) where real import/call edges matter more than doc/registry cross
  references, extending the custom script with `ast`-based Python import parsing or a
  lightweight JS/TS import regex is a smaller, safer increment than adopting
  rhanka/graphify's Node dependency + LLM path — revisit only if the regex-based edge
  detection proves too noisy there.
- If rhanka/graphify's star-count discrepancy gets resolved/explained and it adds a
  zero-LLM, no-daemon, single-invocation mode with genuinely local-only output, it
  would be worth a second look for code-heavy repos specifically — not for this
  docs/JSON-heavy pilot repo.
