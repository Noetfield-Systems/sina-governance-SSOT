# Step 10b Autonomous Deploy — DECIDE Boundary v0.1

Status: **LIFT (Brain-only 24/7)** — enabled 2026-07-02 per founder GO AHEAD.

## Purpose

Unattended Step 10b: sandboxes propose, verifier gates, PASS auto-deploys to live Brain with no per-deploy founder confirmation when `~/.sina/brain-autonomous-deploy-v1.flag` is active.

## Authorized modes

| Mode | Status |
|------|--------|
| Dry-run (`APPROVED_DRY_RUN`) | Enabled |
| Confirm-each-time (`CONFIRM DEPLOY`) | Enabled |
| Semi-auto window (`--semi-auto-window`) | Enabled, bounded |
| `--autonomous-deploy` (10b) | **Enabled** with founder flag + hold auto-stop |
| Unattended `--execute-deploy` | **Disabled** |

## Autonomous controls

- **Enable:** `~/.sina/brain-autonomous-deploy-v1.flag`
- **Auto-stop:** `~/.sina/enforcement/brain-autonomous-hold-v1.flag` on smoke/identity/promote fail
- **Clear hold:** matrix ALL PASS + manual rm or successful autonomous cycle
- **Mutation guard:** refuses when `SOURCEA_PHASE2_MUTATION_TRIALS` is true

## Gate invocation

```bash
bash scripts/promote_brain_worker_v1.sh --autonomous-deploy
```

Or via autorun motor: `scripts/brain_loop_autorun_v1.sh` (6h launchd — see [BRAIN_LOOP_LAUNCHD_v0.1.md](BRAIN_LOOP_LAUNCHD_v0.1.md)).

## Sandbox branch rule

`sandbox/brain/*` branches are **verify-only**. Autonomous promote runs on `main` only after merge.

## Evidence index

- Sandbox registry: [data/brain_domain_sandboxes_v1.json](data/brain_domain_sandboxes_v1.json)
- Independence proof: [receipts/verifier-independence-proof-latest.json](receipts/verifier-independence-proof-latest.json)
- Rollback drill: [receipts/brain-rollback-drill-latest.json](receipts/brain-rollback-drill-latest.json)
- Phase 3 plan: [PHASE3_FULL_AUTO_24x7_PLAN_v0.1.md](PHASE3_FULL_AUTO_24x7_PLAN_v0.1.md)

## Founder DECIDE

> Enable Step 10b autonomous deploy (no per-deploy CONFIRM) under semi-auto bounds only, with automatic stop on smoke/identity failure?

**Answer: LIFT (Brain-only 24/7)**
