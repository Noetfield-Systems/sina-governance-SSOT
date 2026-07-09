# L0 Repo Graph Report — sg-sandbox

Generated (last indexed): `2026-07-09T08:05:59Z` · template `v1.1.0`
Total files: 764 · Total size: 8.4MB · Edges detected: 1934

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| SG-Canonical-Library/ | 291 | 4.8MB | `SG-Canonical-Library/noetfield-library-v0.9-SG-RATIFIED-2026-07-05.zip`, `SG-Canonical-Library/noetfield-library/P4-CLOUD-KERNEL-L1-L8/SOURCEA_SSOT_v1.2_MASTER_ARCH_LOCKED.pdf`, `SG-Canonical-Library/noetfield-library/P4-CLOUD-KERNEL-L1-L8/SOURCEA_CLOUD_KERNEL_v1.3_TARGET_ARCH.pdf`, `SG-Canonical-Library/noetfield-library/P99-LEDGER/TRUSTFIELD_LANGUAGE_CLEANUP_INVENTORY_v1.json`, `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md`, `SG-Canonical-Library/noetfield-library/P1-CANON/NOETFIELD_SYSTEMS_OPERATING_PLAN.md` |
| decision_language_machine_v1/ | 108 | 1.5MB | `decision_language_machine_v1/test_fixtures/form_official_80_open_v1.json`, `decision_language_machine_v1/output/3a35ff4a96c3488c.processed.json`, `decision_language_machine_v1/output/5150a5519a094825.processed.json`, `decision_language_machine_v1/output/7b90b51ae52d4a51.processed.json`, `decision_language_machine_v1/output/b0111f62f1a143e4.processed.json`, `decision_language_machine_v1/output/d6dd991de74c4cf4.processed.json` |
| catalog/ | 75 | 617.6KB | `catalog/source/_raw_bundle.json`, `catalog/planning/chess_forecast_full.json`, `catalog/source/CATALOG.md`, `catalog/FULL_CATALOG.md`, `catalog/full-catalog.html`, `catalog/source/map-d4-independent-verifier-promotion-gate.json` |
| scripts/ | 53 | 292.0KB | `scripts/p0pgr_campaign_planner_v1.py`, `scripts/tf_language_cleanup_v1.py`, `scripts/workflow_census_v1.py`, `scripts/living_system_chain_validate_v1.py`, `scripts/agent_read_staleness_engine_v1.py`, `scripts/verify_auth_surfaces_e2e_v1.py` |
| language_gate/ | 19 | 287.8KB | `language_gate/dictionary_index.json`, `language_gate/receipts/SG-Canonical-Library.library_scan.056cec9f66a064c7.details.json`, `language_gate/sourcea_dictionary_overlay_index_v1.json`, `language_gate/language_gate_core_v1.py`, `language_gate/dictionary_rc2_supplement.json`, `language_gate/trustfield_dictionary_overlay_index_v1.json` |
| receipts/ | 92 | 238.6KB | `receipts/p0pgr/campaigns/P0PGR-CAMPAIGN-20260708-001.json`, `receipts/parallel-candidate-batch-20260702T093706Z.json`, `receipts/parallel-candidate-batch-20260702T094707Z.json`, `receipts/agent-read-staleness-20260707T234503Z.json`, `receipts/auth-surface-probe-20260708T071022Z.json`, `receipts/p0pgr/evidence/evidence-dd61a460b6927e46.json` |
| data/ | 20 | 216.4KB | `data/living_system_110_plans_v1.json`, `data/living_system_110_plans_v1_LOCKED.json`, `data/agent_read_surfaces_v1.json`, `data/automation_surface_inventory_v1.json`, `data/github_automation_registry_v1.json`, `data/auth_surface_matrix_v1.json` |
| docs/ | 33 | 165.9KB | `docs/LIVING_SYSTEM_110_UPGRADE_PLANS_v1.md`, `docs/LIVING_SYSTEM_110_UPGRADE_PLANS_v1_LOCKED.md`, `docs/SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md`, `docs/1111_UPGRADE_PLANS_v2.md`, `docs/1111_UPGRADE_PLANS_v1.md`, `docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md` |
| desktop-app/ | 12 | 110.7KB | `desktop-app/PR-Conflict-Resolver-Report.app/Contents/Resources/report.html`, `desktop-app/Receipt-Ledger-Auditor.app/Contents/Resources/generate.py`, `desktop-app/Staleness-Gate-Auditor.app/Contents/Resources/generate.py`, `desktop-app/Registry-Motor-Validator.app/Contents/Resources/generate.py`, `desktop-app/Registry-Motor-Validator.app/Contents/MacOS/launcher`, `desktop-app/Receipt-Ledger-Auditor.app/Contents/MacOS/launcher` |
| skills/ | 10 | 62.0KB | `skills/pr-conflict-resolver/evals/benchmark.json`, `skills/pr-conflict-resolver/SKILL.md`, `skills/p0pgr-operator/SKILL.md`, `skills/staleness-gate-auditor/SKILL.md`, `skills/p0pgr-receipt-verifier/SKILL.md`, `skills/p0pgr-packet-compiler/SKILL.md` |
| p0-pgr/ | 10 | 49.1KB | `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_LOOP_STATE_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_GOVERNANCE_RUNTIME_v1.md`, `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`, `p0-pgr/P0_PROMPT_REGISTRY_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_COMPILER_MVP_PLAN_v1.md` |
| ssot/ | 6 | 40.2KB | `ssot/strategy-ssot-v6-split.md`, `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`, `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`, `ssot/sg-guardrails-trustfield-v1.md`, `ssot/noos-doctrine-trustfield-v1.md`, `ssot/sg-guardrails-signal-factory-v1.md` |
| gates/ | 2 | 32.0KB | `gates/promotion_gate.py`, `gates/cf_tokens.py` |
| workers/ | 1 | 24.2KB | `workers/github-app-advisory/index.js` |
| tests/ | 3 | 11.0KB | `tests/test_verify_auth_surfaces_e2e_v1.py`, `tests/test_p0pgr_phase0.py`, `tests/test_chess_pass_cli_v1.py` |
| .github/ | 7 | 9.8KB | `.github/workflows/p0pgr-shadow-cycle-v1.yml`, `.github/workflows/sg-auth-surface-probe-v1.yml`, `.github/workflows/workflow-census-weekly-v1.yml`, `.github/workflows/brain-loop-autorun-v1.yml`, `.github/workflows/agent-read-staleness-weekly-v1.yml`, `.github/pull_request_template.md` |
| verifier/ | 5 | 8.1KB | `verifier/knowledge-bundle-spec-v0.1.md`, `verifier/step7-manual-live-deploy-note-v0.1.md`, `verifier/independent-verifier-birth-receipt-61d95d74.json`, `verifier/brain-worker-code-spec-v0.1.md`, `verifier/brain-config-artifact-descriptor-schema-v0.1.json` |
| .cursor/ | 5 | 5.1KB | `.cursor/rules/plans-24-7-cloud-loops.mdc`, `.cursor/hooks/language_gate_pre_write_v1.py`, `.cursor/hooks/language-gate-after-edit.sh`, `.cursor/hooks.json`, `.cursor/hooks/language-gate-pre-write.sh` |
| ledger/ | 1 | 4.4KB | `ledger/session-decision-ledger.md` |
| infrastructure/ | 1 | 1.9KB | `infrastructure/supabase/migrations/001_workflow_census_v1.sql` |
| proposals/ | 1 | 732B | `proposals/step4-submitted-knowledge-bundle/knowledge-bundle.json` |
| .githooks/ | 1 | 621B | `.githooks/pre-commit` |
| .noetfield/ | 1 | 474B | `.noetfield/agent_manifest.yml` |
| (root files) | 7 | 17.7KB | `PHASE_LOOP_BUILD_PLAN_v0.1.md`, `check.py`, `AGENTS.md`, `README.md`, `.gitignore`, `wrangler.github-app-advisory.jsonc` |

## Dependency / reference edges

1934 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

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

Rebuild whenever the file layout changes materially (new subsystem, large doc/data additions). See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token budget rule and the broad-read prevention rule.
