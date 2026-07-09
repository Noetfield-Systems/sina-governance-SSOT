# L0 Repo Graph Report — sina-governance-ssot

Generated (last indexed): `2026-07-09T02:16:34Z`
Total files: 719 · Total size: 4.1MB · Edges detected: 2365

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| data/ | 232 | 1.6MB | `data/governance_review_queue_v1.json`, `data/l0_repo_graph_memory_v1.json`, `data/governance_intake_staging_v1/deep_research_report/deep-research-report.md`, `data/governance_artifact_registry_v1.json`, `data/governance_intake_staging_v1/manifest.json`, `data/team_bench_sourced_rows_v1.json` |
| receipts/ | 203 | 932.4KB | `receipts/governance-intelligence-20260704T013119Z.json`, `receipts/l0-graph-query-1000-plan-20260709T020940Z.json`, `receipts/p0pgr/artifacts/execution-PKT-0002-20260708T164627Z/www.noetfield.com.html`, `receipts/governance-intelligence-20260704T013325Z.json`, `receipts/p0pgr/artifacts/CLOUD_FACTORY_SUBSTRATE_v0-20260709T015408Z/verifier_findings_v1.json`, `receipts/parallel-candidate-batch-20260702T103251Z.json` |
| packages/ | 119 | 586.4KB | `packages/noos-control-desk-v1/control-desk/static/assets/index-BUsr7EfJ.js`, `packages/noos-control-desk-v1/control-desk/frontend/package-lock.json`, `packages/noos-control-desk-v1/.noos/registry_draft.json`, `packages/noos-control-desk-v1/control-desk/backend/handler.py`, `packages/noos-control-desk-v1/receipts/step7_workflow_audit_2026-07-03.json`, `packages/noos-control-desk-v1/scripts/run_step7_workflow_audit_v1.py` |
| scripts/ | 66 | 402.3KB | `scripts/governance_intelligence_engine_v1.py`, `scripts/governance_thread_intelligence_v1.py`, `scripts/governance_intake_path_intelligence_v1.py`, `scripts/governance_registry_ops_v1.py`, `scripts/governance_promote_library_drafts_v1.py`, `scripts/governance_intake_sink_v1.py` |
| docs/ | 46 | 269.3KB | `docs/SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md`, `docs/governance_drafts_tag_v1/SMART_PRODUCTION_COST_LAW_v2.md`, `docs/TRUSTFIELD_CLOUD_LOOPS_IMPLEMENTATION_PACKETS_v1.md`, `docs/CLOUD_FACTORY_PROMOTION_PLAN_TRUSTFIELD_v1.md`, `docs/governance_drafts_tag_v1/SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0_1_4_IMPLEMENTATION_PROMPT_20260629-1753.md`, `docs/governance_drafts_tag_v1/SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0_1_4_20260629-1753.md` |
| cloud-factory/ | 5 | 114.4KB | `cloud-factory/CLOUD_FACTORY_SUBSTRATE_v0.md`, `cloud-factory/MVP_ACTIVATION_PLAN_v0.md`, `cloud-factory/SANDBOX_MANAGER_SPEC_v0.md`, `cloud-factory/CLIENT_ORDER_TO_FACTORY_RUN_SCHEMA_v0.json`, `cloud-factory/FACTORY_LINE_REGISTRY_v0.json` |
| ssot/ | 16 | 110.0KB | `ssot/strategy-ssot-v6-split.md`, `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`, `ssot/GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md`, `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`, `ssot/DAILY_GOVERNANCE_MACHINE_RUNBOOK_v1.md`, `ssot/AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE_SSOT_LOCKED_v1.md` |
| gates/ | 2 | 32.0KB | `gates/promotion_gate.py`, `gates/cf_tokens.py` |
| workers/ | 1 | 24.2KB | `workers/github-app-advisory/index.js` |
| p0-pgr/ | 6 | 13.8KB | `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`, `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json`, `p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_COMPILER_MVP_PLAN_v1.md`, `p0-pgr/P0_PROMPT_LOOP_STATE_SCHEMA_v1.json`, `p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md` |
| tests/ | 2 | 12.3KB | `tests/repo_fences/run_negative_tests.py`, `tests/test_p0pgr_phase0.py` |
| verifier/ | 5 | 8.1KB | `verifier/knowledge-bundle-spec-v0.1.md`, `verifier/step7-manual-live-deploy-note-v0.1.md`, `verifier/independent-verifier-birth-receipt-61d95d74.json`, `verifier/brain-worker-code-spec-v0.1.md`, `verifier/brain-config-artifact-descriptor-schema-v0.1.json` |
| .github/ | 5 | 5.7KB | `.github/workflows/repo-fences-v1.yml`, `.github/workflows/brain-loop-autorun-v1.yml`, `.github/CODEOWNERS`, `.github/copilot-instructions.md`, `.github/pull_request_template.md` |
| reports/ | 2 | 4.7KB | `reports/trustfield-copilot-agent-resolution-v1.jsonl`, `reports/trustfield-copilot-ui-attestation-pointer-v1.json` |
| ledger/ | 1 | 4.4KB | `ledger/session-decision-ledger.md` |
| policy/ | 1 | 2.3KB | `policy/repo_fences_v1.yaml` |
| proposals/ | 1 | 732B | `proposals/step4-submitted-knowledge-bundle/knowledge-bundle.json` |
| (root files) | 6 | 17.0KB | `PHASE_LOOP_BUILD_PLAN_v0.1.md`, `check.py`, `AGENTS.md`, `README.md`, `wrangler.github-app-advisory.jsonc`, `.gitignore` |

## Dependency / reference edges

2365 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph — this is a governance/docs-heavy repo, not a single-language codebase). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

## Ignored directories

`.cache`, `.git`, `.noos_cache`, `.pytest_cache`, `.venv`, `.wrangler`, `__pycache__`, `build`, `dist`, `graph-out`, `node_modules`, `venv`

## Query command

```
python3 scripts/query_repo_graph_v1.py <subsystem-name|keyword|path-fragment>
```

## Rebuild command

```
python3 scripts/build_repo_graph_v1.py
```

Rebuild whenever the file layout changes materially (new subsystem, large doc/data additions) — this report drifts from truth otherwise. See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token budget rule and the broad-read prevention rule.
