# Brain Loop Autorun v0.1

Bounded Brain-domain autorun for SG promotion loop. **Brain-only** — no Mac nerve mesh, no Cloud Forge self-heal.

## Sequence

1. `brain_loop_self_heal_v1.sh` — detect stale verifier receipt; re-trigger `/run` when `BRAIN_SELF_HEAL_TRIGGER=1`
2. `run_parallel_brain_candidates_v1.sh --all` — parallel verifier batch
3. `validate_brain_domain_e2e_matrix_v1.sh` — only when ship-window or CI
4. Gate promote — **manual** unless `BRAIN_SANDBOX_SEMI_AUTO=brain_worker` and ship-window flag set

## Guards

| Guard | Behavior |
|-------|----------|
| `~/.sina/asf-ship-window-v1.flag` | Required for E2E matrix + semi-auto promote path |
| Mac founder session (no flag) | Observe-only: self-heal + parallel run receipts only |
| `SOURCEA_PHASE2_MUTATION_TRIALS` | Must stay `false` — autorun never sets it |
| `--autonomous-deploy` | **NOT enabled** — Step 10b HOLD |

## Schedule (launchd + GitHub Actions)

| Motor | Cadence |
|-------|---------|
| Mac launchd | **30m** (`1800s`) + RunAtLoad |
| GitHub Actions `brain-loop-autorun-v1` | ***/30** (24/7 cloud mirror) |

When `CF_MAIN_TOKEN` + `CF_VERIFIER_TOKEN` present in CI: `BRAIN_CI_AUTONOMOUS=1` enables promote path (gate CAS still applies).

## Commands

```bash
# Observe-only (Mac founder session)
bash scripts/brain_loop_autorun_v1.sh

# With ship window
touch ~/.sina/asf-ship-window-v1.flag
export BRAIN_SANDBOX_SEMI_AUTO=brain_worker
bash scripts/brain_loop_autorun_v1.sh
```

Receipts: `receipts/brain-loop-autorun-<timestamp>.json`
