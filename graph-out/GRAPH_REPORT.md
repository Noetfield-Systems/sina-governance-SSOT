# L0 Repo Graph Report — sina-governance-ssot

Generated (last indexed): `2026-07-09T06:03:04Z`
Total files: 5401 · Total size: 14.1MB · Edges detected: 12130

**Read this file first.** Do not spawn broad repo-reading agents ("understand the repo", "map subsystem X", "audit Y") until you have read this report and, if you need more detail, queried the index with `python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. This report + a query response should answer routing questions ("which files touch X", "how big is subsystem Y") without opening every file in the subsystem.

## Subsystem map (sorted by size, descending)

| subsystem | files | size | largest files |
|---|---:|---:|---|
| language_gate/ | 4662 | 6.0MB | `language_gate/dictionary_index.json`, `language_gate/receipts/tmpukwyusc5.md.8a9a5c25a87e3656.receipt.json`, `language_gate/receipts/tmpqltl94vy.json.e13e84f9915307e4.receipt.json`, `language_gate/receipts/SG-Canonical-Library.library_scan.056cec9f66a064c7.details.json`, `language_gate/sourcea_dictionary_overlay_index_v1.json`, `language_gate/language_gate_core_v1.py` |
| SG-Canonical-Library/ | 299 | 4.8MB | `SG-Canonical-Library/noetfield-library-v0.9-SG-RATIFIED-2026-07-05.zip`, `SG-Canonical-Library/noetfield-library/P4-CLOUD-KERNEL-L1-L8/SOURCEA_SSOT_v1.2_MASTER_ARCH_LOCKED.pdf`, `SG-Canonical-Library/noetfield-library/P4-CLOUD-KERNEL-L1-L8/SOURCEA_CLOUD_KERNEL_v1.3_TARGET_ARCH.pdf`, `SG-Canonical-Library/noetfield-library/P99-LEDGER/TRUSTFIELD_LANGUAGE_CLEANUP_INVENTORY_v1.json`, `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md`, `SG-Canonical-Library/noetfield-library/P1-CANON/NOETFIELD_SYSTEMS_OPERATING_PLAN.md` |
| decision_language_machine_v1/ | 108 | 1.5MB | `decision_language_machine_v1/test_fixtures/form_official_80_open_v1.json`, `decision_language_machine_v1/output/3a35ff4a96c3488c.processed.json`, `decision_language_machine_v1/output/5150a5519a094825.processed.json`, `decision_language_machine_v1/output/7b90b51ae52d4a51.processed.json`, `decision_language_machine_v1/output/b0111f62f1a143e4.processed.json`, `decision_language_machine_v1/output/d6dd991de74c4cf4.processed.json` |
| skills/ | 57 | 369.0KB | `skills/p0pgr-skills-workspace/iteration-2/review.html`, `skills/p0pgr-skills-workspace/iteration-1/review.html`, `skills/pr-conflict-resolver/evals/benchmark.json`, `skills/p0pgr-skills-workspace/iteration-1/eval-2-receipt-verify/without_skill/outputs/verdict.md`, `skills/p0pgr-skills-workspace/iteration-1/eval-2-receipt-verify/with_skill/outputs/verdict.md`, `skills/pr-conflict-resolver/SKILL.md` |
| scripts/ | 57 | 321.7KB | `scripts/p0pgr_campaign_planner_v1.py`, `scripts/tf_language_cleanup_v1.py`, `scripts/workflow_census_v1.py`, `scripts/gen_auth_upgrade_214_v1.py`, `scripts/living_system_chain_validate_v1.py`, `scripts/verify_auth_surfaces_e2e_v1.py` |
| receipts/ | 101 | 300.7KB | `receipts/workflow-census-20260706T093358Z.json`, `receipts/workflow-census-20260706T090917Z.json`, `receipts/p0pgr/campaigns/P0PGR-CAMPAIGN-20260708-001.json`, `receipts/parallel-candidate-batch-20260702T093706Z.json`, `receipts/parallel-candidate-batch-20260702T094707Z.json`, `receipts/agent-read-staleness-20260707T234503Z.json` |
| data/ | 22 | 295.3KB | `data/auth_upgrade_214_v1.json`, `data/living_system_110_plans_v1.json`, `data/living_system_110_plans_v1_LOCKED.json`, `data/agent_read_surfaces_v1.json`, `data/automation_surface_inventory_v1.json`, `data/github_automation_registry_v1.json` |
| docs/ | 37 | 199.2KB | `docs/LIVING_SYSTEM_110_UPGRADE_PLANS_v1.md`, `docs/LIVING_SYSTEM_110_UPGRADE_PLANS_v1_LOCKED.md`, `docs/SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md`, `docs/AUTH_UPGRADE_214_PLANS_v1.md`, `docs/1111_UPGRADE_PLANS_v2.md`, `docs/1111_UPGRADE_PLANS_v1.md` |
| desktop-app/ | 12 | 108.0KB | `desktop-app/PR-Conflict-Resolver-Report.app/Contents/Resources/report.html`, `desktop-app/Receipt-Ledger-Auditor.app/Contents/Resources/generate.py`, `desktop-app/Staleness-Gate-Auditor.app/Contents/Resources/generate.py`, `desktop-app/Registry-Motor-Validator.app/Contents/Resources/generate.py`, `desktop-app/Registry-Motor-Validator.app/Contents/MacOS/launcher`, `desktop-app/Receipt-Ledger-Auditor.app/Contents/MacOS/launcher` |
| p0-pgr/ | 10 | 49.1KB | `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_LOOP_STATE_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_GOVERNANCE_RUNTIME_v1.md`, `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`, `p0-pgr/P0_PROMPT_REGISTRY_SCHEMA_v1.json`, `p0-pgr/P0_PROMPT_COMPILER_MVP_PLAN_v1.md` |
| ssot/ | 6 | 40.2KB | `ssot/strategy-ssot-v6-split.md`, `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`, `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`, `ssot/sg-guardrails-trustfield-v1.md`, `ssot/noos-doctrine-trustfield-v1.md`, `ssot/sg-guardrails-signal-factory-v1.md` |
| gates/ | 2 | 32.0KB | `gates/promotion_gate.py`, `gates/cf_tokens.py` |
| workers/ | 1 | 24.2KB | `workers/github-app-advisory/index.js` |
| tests/ | 6 | 15.4KB | `tests/test_verify_auth_surfaces_e2e_v1.py`, `tests/test_p0pgr_phase0.py`, `tests/test_commercial_pulse_dispatch_check_v1.py`, `tests/test_chess_pass_cli_v1.py`, `tests/test_living_system_chain_validate_v1.py`, `tests/test_auth_upgrade_214_v1.py` |
| .github/ | 7 | 9.8KB | `.github/workflows/p0pgr-shadow-cycle-v1.yml`, `.github/workflows/sg-auth-surface-probe-v1.yml`, `.github/workflows/workflow-census-weekly-v1.yml`, `.github/workflows/brain-loop-autorun-v1.yml`, `.github/workflows/agent-read-staleness-weekly-v1.yml`, `.github/pull_request_template.md` |
| verifier/ | 5 | 8.1KB | `verifier/knowledge-bundle-spec-v0.1.md`, `verifier/step7-manual-live-deploy-note-v0.1.md`, `verifier/independent-verifier-birth-receipt-61d95d74.json`, `verifier/brain-worker-code-spec-v0.1.md`, `verifier/brain-config-artifact-descriptor-schema-v0.1.json` |
| ledger/ | 1 | 4.4KB | `ledger/session-decision-ledger.md` |
| infrastructure/ | 1 | 1.9KB | `infrastructure/supabase/migrations/001_workflow_census_v1.sql` |
| proposals/ | 1 | 732B | `proposals/step4-submitted-knowledge-bundle/knowledge-bundle.json` |
| (root files) | 6 | 18.7KB | `PHASE_LOOP_BUILD_PLAN_v0.1.md`, `check.py`, `AGENTS.md`, `README.md`, `.gitignore`, `wrangler.github-app-advisory.jsonc` |

## Dependency / reference edges

12130 static repo-relative path references were detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex scan, not a real import graph — this is a governance/docs-heavy repo, not a single-language codebase). Full edge list is in `graph_index_v1.json`; query by file or subsystem with the query script rather than reading it directly.

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
