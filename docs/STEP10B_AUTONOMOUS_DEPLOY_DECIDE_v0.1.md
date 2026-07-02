# Step 10b Autonomous Deploy — DECIDE Boundary v0.1

Status: **HOLD** — proposal only. Do not enable `--autonomous-deploy` without explicit founder DECIDE.

## Purpose

Define prerequisites for unattended Step 10b: sandboxes propose, verifier gates, PASS auto-deploys to live Brain with no per-deploy founder confirmation.

## Prerequisites (all must be proven with receipts)

1. **Steps 1–9 complete**
   - Token auto-load: [brain_cli_v1.sh](/Users/sinakazemnezhad/Desktop/SourceA/scripts/brain_cli_v1.sh), [gates/cf_tokens.py](gates/cf_tokens.py)
   - Live sync deploy: [receipts/phase-next-step2-live-sync-receipt.json](receipts/phase-next-step2-live-sync-receipt.json)
   - Bundle scope guard: `--bundle-artifacts-only` in [promotion_gate.py](gates/promotion_gate.py)
   - Semi-auto window: [receipts/phase-next-step4-semi-auto-proof-receipt.json](receipts/phase-next-step4-semi-auto-proof-receipt.json)
   - Worker bundle verifier: `artifact_type: brain_worker_bundle` in [workers/github-app-advisory/index.js](workers/github-app-advisory/index.js)
   - Brain Core production: [receipts/phase-next-step7-brain-core-prod-receipt.json](receipts/phase-next-step7-brain-core-prod-receipt.json)
   - Post-deploy brain-live smoke in gate receipts

2. **Secondary CF account independence**
   - Verifier on account `b7282b4a5c17b84d62e3ef8866b878f8`; live Brain on `0d0b967b77e2e5535455d39ff3dae72c`
   - Re-prove in a fresh shell/environment (Phase 0.3 Step 2) before 10b

3. **Rollback proven**
   - Gate emits `rollback_hint: wrangler versions deploy <pre_version_id>` on health/identity/smoke failure
   - Founder must run one controlled rollback drill and record receipt before 10b

4. **Mutation guard**
   - `SOURCEA_PHASE2_MUTATION_TRIALS` stays `false` in [data/sourcea-phase2-mutation-trials-v1.json](/Users/sinakazemnezhad/Desktop/SourceA/data/sourcea-phase2-mutation-trials-v1.json)

## Proposed flag (NOT implemented)

```text
--autonomous-deploy
  Requires: active semi-auto window OR standing founder DECIDE file on disk
  Refuses: non-PASS receipts, bundle scope violations, dirty deploy-scoped tree
  Post-deploy: health + brain-live smoke; auto-refuse further deploys on failure
```

## Current authorized modes

| Mode | Status |
|------|--------|
| Dry-run (`APPROVED_DRY_RUN`) | Enabled |
| Confirm-each-time (`CONFIRM DEPLOY`) | Enabled |
| Semi-auto window (`--semi-auto-window`) | Enabled, bounded |
| Unattended `--execute-deploy` | **Disabled** |
| `--autonomous-deploy` (10b) | **NOT enabled — DECIDE required** |

## Evidence index (Phase 2 Parallel Brain)

- Sandbox registry: [data/brain_domain_sandboxes_v1.json](data/brain_domain_sandboxes_v1.json)
- Autorun doc: [docs/BRAIN_LOOP_AUTORUN_v0.1.md](docs/BRAIN_LOOP_AUTORUN_v0.1.md)
- Independence proof: [receipts/verifier-independence-proof-latest.json](receipts/verifier-independence-proof-latest.json)
- Rollback drill: [receipts/brain-rollback-drill-latest.json](receipts/brain-rollback-drill-latest.json)
- Self-heal ticks: `receipts/brain-self-heal-tick-*.json`
- Parallel batches: `receipts/parallel-candidate-batch-*.json`

## Founder DECIDE question (updated 2026-07-02)

> Enable Step 10b autonomous deploy (no per-deploy CONFIRM) under semi-auto bounds only, with automatic stop on smoke/identity failure?

**Current answer: HOLD**

Phase 2 adds Brain-only bounded autorun (heal + parallel verify). Sufficient evidence for LIFT requires:
- Fresh independence receipt (< 30 days)
- Rollback drill PASS receipt
- E2E matrix ALL PASS under ship window
- At least one improvement proposal → parallel run → promote flow

**Mac nerve / Cloud Forge full mesh: DEFER Phase 3.**

## Prior evidence index

- Phase loop plan: [PHASE_LOOP_BUILD_PLAN_v0.1.md](PHASE_LOOP_BUILD_PLAN_v0.1.md)
- Step 2 live sync: `883dbc6e-5333-45e9-ad21-b61d52c7bb62` → Brain Core deploy `81058e04-6b8b-442d-a108-6eebffc60519`
- Verifier latest PASS: `167e3626-2e17-4ffc-a027-1a2d4db8b890` (`brain_worker_bundle`, ref `ff34a8749`)

## Founder DECIDE question

> Enable Step 10b autonomous deploy (no per-deploy CONFIRM) under semi-auto bounds only, with automatic stop on smoke/identity failure?

**Default answer: HOLD until rollback drill + fresh-environment independence re-proof.**
