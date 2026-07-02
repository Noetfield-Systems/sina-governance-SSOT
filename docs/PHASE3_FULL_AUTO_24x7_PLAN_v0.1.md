# Phase 3 — Full Auto 24/7 Plan v0.1

**Status:** LOCKED — execute top-down. Step 10 requires founder DECIDE + `~/.sina/brain-autonomous-deploy-v1.flag`.

**Saved:** 2026-07-02

## Baseline (proven)

- Self-heal, parallel 4/4 PASS, E2E matrix ALL PASS, independence PASS, rollback EXECUTE PASS
- Verifier ref: `7ffd0766…` · bundle: `642c151ee61ae1ddaaddd0163f668b6b90b41b88eabb7adbb6e15f7e02502ded`
- Step 10b posture target: **Brain-only FULL AUTO 24/7** (heal → verify → promote on PASS; auto-stop on fail)

## Step 1 — Land Phase 2 on SG origin/main

Commit + push registry, brain-loop scripts, gate sandbox profiles, docs, receipts (no secrets, no `__pycache__`).

**Done when:** Fresh clone runs `validate_brain_domain_registry_v1.py` ALL PASS.

## Step 2 — Land SourceA loop wrappers

Commit `sg_brain_loop_v1.sh`, rollback drill, propose script, contract 301 fix. Exclude crawl dirt.

**Done when:** `bash scripts/sg_brain_loop_v1.sh matrix` ALL PASS.

## Step 3 — Brain deploy dirty-tree guard

Add `brain_worker` scope to `deploy_dirty_tree_guard_v1.py`; gate pre-check.

**Done when:** Promote refuses brain-scoped dirty; crawl-only dirt OK if `dirty_total <= 200`.

## Step 4 — First confirm-each-time promote

Promote signed `7ffd0766…` from clean `main`. Receipt: `receipts/phase3-step4-promote-receipt.json`.

**Done when:** SHA identity match + brain-live PASS.

## Step 5 — Implement `--autonomous-deploy`

Gate flag + `~/.sina/brain-autonomous-deploy-v1.flag` + safety bounds.

**Done when:** Dry-run autonomous path; failure refuses with rollback hint.

## Step 6 — 24/7 autorun motor (launchd)

Upgrade `brain_loop_autorun_v1.sh` — 6h cycle; doc `BRAIN_LOOP_LAUNCHD_v0.1.md`.

**Done when:** Full autorun cycle receipt with autonomous flag.

## Step 7 — Sandbox branch → main lane

Feature branches verify-only; auto-promote `main` only.

**Done when:** sandbox → verify → merge → autorun promote.

## Step 8 — CI mirror

`.github/workflows/brain-loop-autorun-v1.yml` — 6h schedule + manual dispatch.

**Done when:** One CI autorun receipt.

## Step 9 — Auto-stop hold flag

`brain-autonomous-hold-v1.flag` on fail; clear on matrix ALL PASS.

**Done when:** Simulated fail sets hold; matrix clears.

## Step 10 — Founder DECIDE: enable 24/7

Create autonomous flag, install launchd, update STEP10B + PHASE_LOOP docs.

**Done when:** 24h observation — autorun every 6h; no silent failures.

## Out of scope (Phase 4)

Mac nerve mesh, Cloud Forge autorun, W3 commercial RED, auto-commit crawl refresh.
