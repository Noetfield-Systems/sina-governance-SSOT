# Dispatch — Motor Learning Organ (all repos)

**Authority:** `NF-MOTOR-LEARNING-ORGAN-V1`  
**Canon:** `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/NF_MOTOR_LEARNING_ORGAN_LOCKED_v1.md`  
**Machine:** `data/nf_motor_learning_organ_v1_LOCKED.json`  
**Contracts:** `data/nf_motor_learning_organ_contracts_v1.json`  
**Pass checks:** `data/nf_motor_learning_organ_pass_checks_v1.json`

## One line

W0 = governance scaffold. **W1 SG reference pipeline is executable** (fixture/dry-run). Pattern → prior → improve: mine receipts into ECQR routing/recovery priors via propose → shadow → ratify. No unsupervised redesign. No Data Runway unlock.

## Instruction by repo

| Repo | Wave | Action |
|------|------|--------|
| **sina-governance-SSOT** | W0 | Lock packet, contracts, pass checks, registry row `gh_actions_motor_learning_organ_v1` / `loop_id=motor_learning_organ_v1`, this dispatch |
| **SourceA** | W1 | Export durable patterns from `~/.sina/execution_patterns.json` (+ decisions jsonl) into repo/SSOT-shaped artifacts; emit `learning_record` drafts per contracts; keep planner bias local until Motor consume exists |
| **NOETFIELD-RUNWAY** | W2 | Implement `packages/runway-core/src/routing/{failure-classifier,recovery-policy,roi}` — load shadow/live policy snapshots; fall back to stage-local static failover; emit route-change receipts |
| **NOOS** | W3 | Observe ECQR / qualification / pattern concentration; surface ROI-ranked Kaizen queue; upsert `last_fired_at` visibility for `motor_learning_organ_v1` |
| **SourceB / SinaGPT** | — | ROI summary surface only (catalog · estimate · progress · qualified result · ROI) — no learning mutation UI that bypasses gate |
| **Cloud (GHA or CF)** | W4 | Daily miner cron + weekly ROI snapshot; deadman `sourcea-deadman-v1` at `2×` cadence; receipts under `receipts/learning/` |

## SourceA (W1) — pattern export detail

1. Read live `~/.sina/execution_patterns.json` and `~/.sina/execution_decisions.jsonl`.
2. Write durable export: `SourceA/data/motor_learning/pattern_export_*.json` (no secrets).
3. For each high-confidence failure/success/repetition pattern, emit `learning_record` with `status: draft`, `stage_market_id` when known, `sample_n`, `confidence`, `ecqr_delta_estimate` if computable.
4. Do **not** promote to live Motor priors from SourceA alone.
5. Validate with existing `validate-pattern-engine-v1.sh` / `validate-feedback-loop-v1.sh` where present.

## NOETFIELD-RUNWAY (W2) — ROI consume detail

1. Store paths: `routing/roi/{stage_market_id}.shadow.json` and `.live.json`.
2. Shadow selector scores candidates; live selector only after GATED promote or narrow auto-apply allowlist.
3. Recovery policy consumes failure-signature suppression weights from live recovery priors.
4. On live promote: write receipt with `snapshot_id`, `stage_market_id`, `ecqr_before`, `ecqr_after`, `ratified_by`.
5. Rollback: disable live ROI; restore `rollback_pointer`; mark snapshot `rolled_back`.

## First improvement targets (all implementers)

1. Recompute router `reliability` / `est_cost` from receipts (kill static `1.0`).
2. Failure-signature suppression → recovery policy.
3. Distill one expensive verified fix → one reusable cheap artifact referenced by Motor.



## W1 SG reference (landed in this repo)

| Artifact | Path |
|----------|------|
| Package | `scripts/motor_learning/` |
| CLI | `scripts/motor_learning_organ_w1_run.py` |
| Validator | `scripts/validate_motor_learning_organ_w1.py` |
| Tests | `tests/test_motor_learning_organ_w1.py` |
| Fixtures | `fixtures/motor_learning_w1/` |

Cross-repo still outstanding:

| Owner | Status |
|-------|--------|
| SourceA live export | NOT_IMPLEMENTED — consume `~/.sina/execution_patterns.json` into learning_record drafts |
| NOETFIELD-RUNWAY | NOT_IMPLEMENTED — load `routing/roi/*.live.json` from ratified priors |
| NOOS | NOT_IMPLEMENTED — Kaizen/ECQR operator surface |
| Cloud heartbeat | PARTIAL — observe-only; must never ratify/promote |

## Next milestone — W2 Runway live consume (not done)

W0 is approved as foundational scaffold only. W1 must implement:

```text
Motor Event → Normalizer → Pattern Extractor → Prior Search → Similarity Score
→ Candidate Improvements → Shadow Execution → Evidence → ECQR Review
→ Ratified Prior + learning_receipt
```

| Owner | W1 deliverable |
|-------|----------------|
| SourceA | Normalizer + pattern extractor from live `execution_patterns`; emit draft learning_records |
| NOETFIELD-RUNWAY | Prior search + similarity score over `routing/roi/*`; shadow execution hook |
| NOOS | Surface similarity candidates + Kaizen ECQR review queue |
| All | On every ratify/reject: write `learning_receipt` per `data/nf_motor_learning_receipt_v1.json` |

Do not claim learning-organ liveness until MLO-01..05 have real (non-example) evidence.

## learning_receipt (add immediately — schema locked)

Path: `receipts/learning/learning_receipt-*.json`  
Schema: `data/nf_motor_learning_receipt_v1.json`

Required: prior_id, origin_event, evidence_links, confidence_before/after, why_accepted_or_rejected, reviewer, decision, affected_loops, applicable_runways, ratified_at, snapshot_id.  
Optional: applicable_customers, expiry, supersedes, superseded_by.

## Hold / forbidden

- Data Runway before `future_runway_gate`
- Base-model training as Phase-1 deliverable
- Unsupervised Level-3 bandit on high-risk tasks
- Architecture self-redesign
- Bypass HOLD / SG authority / auto-promote-merge
- New product SKU or permanent Resident Role for this organ
- Video product upgrade (Gallery cost-supply remains media-economics path)

## PASS checks (when runtime exists)

| ID | Check |
|----|-------|
| MLO-01 | Shadow prior load from ≥30 receipt samples |
| MLO-02 | Kaizen ranked with ECQR delta |
| MLO-03 | Ratified live prior + before/after ECQR receipt |
| MLO-04 | Deadman heartbeat within `2×` cadence |
| MLO-05 | Complete `learning_receipt` on every ratify/reject/rollback |

## Loop registry

| Field | Value |
|-------|-------|
| `loop_id` | `motor_learning_organ_v1` |
| Trigger host | `cloud` |
| Cadence | daily mine `0 6 * * *` · weekly ROI `0 7 * * 1` |
| Deadman | `sourcea-deadman-v1` |
| Receipt | `receipts/learning/motor-learning-organ-*.json` |
| Motor id | `gh_actions_motor_learning_organ_v1` |
