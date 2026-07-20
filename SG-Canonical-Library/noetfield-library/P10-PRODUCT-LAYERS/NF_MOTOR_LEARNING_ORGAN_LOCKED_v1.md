# NF-MOTOR-LEARNING-ORGAN-V1 — SG FINALIZATION PACKET

**decision_id:** `NF-MOTOR-LEARNING-ORGAN-V1`
**Status:** `SG_ACCEPTED` · learning-organ addendum (does **not** reopen Unified Motor architecture or Runway product locks)
**Authority:** Architecture Finalization Gate
**Tier:** P10-PRODUCT-LAYERS
**Version:** v1.3.0_locked_20260720
**Machine:** `data/nf_motor_learning_organ_v1_LOCKED.json`
**Contracts:** `data/nf_motor_learning_organ_contracts_v1.json`
**Learning receipt:** `data/nf_motor_learning_receipt_v1.json`
**Pass checks:** `data/nf_motor_learning_organ_pass_checks_v1.json`
**Packet id:** `SG-FINALIZATION-MOTOR-LEARNING-ORGAN-V1`
**effective_at:** 2026-07-20
**proposed_by:** Founder + SG (Motor Learning Organ plan)
**sg_decision:** `SG_ACCEPTED` — W0 scaffold + W1 **SG reference implementation** (fixture/dry-run); propose→shadow→ratify + mandatory learning_receipt; no live promote; no Model Learning; no Data Runway unlock
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-NOETFIELD-RUNWAY-PRODUCT-V1` · `NF-RUNWAY-PORTFOLIO-ROUTING-INTELLIGENCE-V1` · `BRAIN_REGISTRY_LEARNING_GATE_v0.1.4` (learning_record shape)
**supersedes:** none (closes the “patterns exist but unwired to Motor” gap named in `AGENTIC_DOCTRINE_DISK_AUDIT_v1`)

---


## Implementation maturity (binding honesty)

| Capability | Status |
|------------|--------|
| Canon / contracts / loop identity / dispatch / deadman | COMPLETE (W0) |
| Heartbeat stub (non-promotional) | COMPLETE (W0) |
| Event normalize + idempotency | IMPLEMENTED (W1 SG reference) |
| Signal/pattern extraction | IMPLEMENTED (W1 SG reference) |
| Prior repository + retrieval | IMPLEMENTED (W1 file-backed reference) |
| Pattern mining | IMPLEMENTED (W1 SG reference) |
| Similarity (explainable field Jaccard) | IMPLEMENTED (W1 SG reference) |
| Confidence (versioned components) | IMPLEMENTED (W1 SG reference) |
| Shadow evaluation | IMPLEMENTED (W1 SG reference) |
| ECQR gate + lifecycle | IMPLEMENTED (W1 SG reference) |
| learning_receipt on ratify/reject/rollback | IMPLEMENTED (W1 SG reference) |
| End-to-end orchestrator (fixture/dry-run) | IMPLEMENTED (W1 SG reference) |
| Terminal receipt non-bypassable | IMPLEMENTED |
| Dry-run store immutability | IMPLEMENTED |
| Persistence governance gate | IMPLEMENTED |
| Independent shadow evidence | IMPLEMENTED |
| Rollback e2e | IMPLEMENTED |
| SourceA live pattern export | NOT_IMPLEMENTED (dispatch W1→SourceA) |
| NOETFIELD-RUNWAY live prior consume | NOT_IMPLEMENTED (W2) |
| NOOS Kaizen surface | NOT_IMPLEMENTED (W3) |
| Live production promotion from heartbeat | FORBIDDEN |
| Model Learning / ML training / deep learning | FORBIDDEN |

**Boundary:** Motor Learning improves governed execution priors. It does **not** train models.

### W1 local commands

```bash
python3 -m unittest tests.test_motor_learning_organ_w1 -v
python3 scripts/validate_motor_learning_organ_w1.py
python3 scripts/motor_learning_organ_w1_run.py \
  --fixture fixtures/motor_learning_w1/01_repeated_success_ratify \
  --out /tmp/mlo-w1-out --store /tmp/mlo-w1-store --dry-run
```

### State machine

```text
OBSERVED → PROPOSED → SHADOW → RATIFIED | REJECTED
RATIFIED → SUPERSEDED | EXPIRED | ROLLED_BACK
```

Illegal: OBSERVED→RATIFIED, PROPOSED→RATIFIED (fail closed).  
RATIFIED/REJECTED/ROLLED_BACK always require a valid `learning_receipt`.

## One-line law

> Mine operational receipts and patterns into ECQR routing/recovery priors — propose, shadow, ratify — so Runways and the Motor get cheaper and more reliable over time without silent self-mutation.

## Purpose

Close the learning loop so Machines / Systems / Motor / Runways improve from real data:

```text
Observe receipts + patterns
→ Detect failure/success signatures and ECQR deltas
→ Critique (confidence / sample_n)
→ Propose learning_record + Kaizen + draft policy_snapshot
→ Shadow apply
→ Founder or gated policy ratify
→ Live prior consumed by Motor stage markets
→ Observe again
```

This is **statistical / deterministic pattern mining + policy priors**, not base-model fine-tuning and not an unsupervised Evolution Agent.

## Ops home (not a product SKU)

| Ops id | Role in this organ |
|--------|--------------------|
| O6 Healing & Repair | failure-classifier + recovery-policy consume learned signatures |
| O8 ROI Optimization | `routing/roi/*` policy snapshots (shadow → live) |
| O10 Monitoring & Continuation | NOOS observe + deadman on `motor_learning_organ_v1` |

Operational learning is a Motor/NOOS **capability**, not a seventh core Runway family and not a permanent Resident Role.

## Mutation classes

| Class | Surfaces | Rule |
|-------|----------|------|
| **OPEN** | Append-only Motor receipts, pattern exports, draft `learning_record` | May write without gate review |
| **GATED** | Policy snapshot promote (shadow → live), Kaizen acceptance that changes routing priors | Gate + receipt; founder for consequential envelopes |
| **LOCKED** | SSOT vocabulary, Unified Motor architecture, HOLD / authority / secrets | Proposals only — never auto-apply |

## Auto-apply allowlist (narrow)

Auto-apply is allowed **only** when all of the following hold:

1. Target is a **low-risk stage-market cold-start prior** (reliability / est_cost / failure-signature suppression weight).
2. `sample_n` ≥ `min_samples` (default **30** per stage market).
3. Shadow ECQR improves vs live prior by ≥ `min_ecqr_improve_pct` (default **5%**) over the evaluation window.
4. Mutation class is not LOCKED; action is not promote/merge/deploy/secret/authority change.
5. High-risk Level-3 bandit remains **FORBIDDEN**.

Everything else stays propose → shadow → human/gate ratify.

## Contracts (binding)

Machine truth: `data/nf_motor_learning_organ_contracts_v1.json`.

### learning_record → policy_snapshot → Motor consume

```text
learning_record (OPEN draft)
  → ranked Kaizen item (ECQR delta estimate)
  → policy_snapshot status=shadow
  → (gate/founder) policy_snapshot status=live
  → Motor ModelRouter / stage market / recovery-policy loads live prior
```

Fields (minimum):

**learning_record**

- `record_id`, `source_event`, `layer`, `asset_affected`
- `failure_description` or `pattern_description`
- `proposed_correction`, `ssot_consistency_check`, `critic_reviewed`
- `status`: `draft` | `proposed` | `approved` | `rejected` | `promoted`
- `receipt_id`, `ecqr_delta_estimate`, `stage_market_id`, `sample_n`, `confidence`

**policy_snapshot**

- `snapshot_id`, `stage_market_id`, `prior_kind` (`reliability` | `est_cost` | `recovery` | `gallery_reuse_bias`)
- `priors` (map), `derived_from_records[]`, `sample_n`, `ecqr_before`, `ecqr_shadow`
- `status`: `draft` | `shadow` | `live` | `rolled_back`
- `ratified_by`, `ratified_at`, `rollback_pointer`

**Motor consume**

- Live selector reads `routing/roi/{stage_market_id}.live.json` (or equivalent store).
- Shadow selector may score without mutating live route choice unless allowlist auto-apply fires.
- Missing live prior → fall back to stage-local static failover prior (portfolio routing rollback law).

## First improvement targets (P0 usefulness)

1. Recompute router `reliability` / `est_cost` from real receipts (replace static `1.0`).
2. Failure-signature suppression → recovery policy (stop repeating known-bad routes).
3. Distill one expensive verified fix into one reusable cheap artifact (fixture / negative rule / prompt fragment) referenced by Motor.

## Closed loop (24/7)

| Field | Value |
|-------|-------|
| Trigger host | `cloud` |
| `loop_id` | `motor_learning_organ_v1` |
| Cadence | daily mine (`0 6 * * *`) + weekly ROI snapshot (`0 7 * * 1`) |
| `last_fired_at` target | `loop_registry` / `noos_loop_registry` |
| Deadman | `sourcea-deadman-v1` (staleness `2×` cadence) |
| Receipt | `receipts/learning/motor-learning-organ-*.json` |
| Registry motor | `gh_actions_motor_learning_organ_v1` (stub until workflow live) |

## Implementation home

| Wave | Repo | Work |
|------|------|------|
| W0 | `sina-governance-SSOT` | This lock + contracts + pass checks + registry row + dispatch |
| W1 | `SourceA` | Export durable patterns from live `execution_patterns`; emit `learning_record` drafts |
| W2 | `NOETFIELD-RUNWAY` | `packages/runway-core/src/routing/{failure-classifier,recovery-policy,roi}` — shadow + live prior consume |
| W3 | NOOS | Observe ECQR / qualification / pattern concentration; surface Kaizen |
| W4 | Cloud | Daily miner + deadman + 48h laptop-closed liveness |

Dispatch: `docs/dispatch/nf-motor-learning-organ-all-repos.md`


## learning_receipt (institutional memory)

Every accept / reject / rollback of a prior **must** emit `receipts/learning/learning_receipt-*.json` per `data/nf_motor_learning_receipt_v1.json`.

Minimum fields:

- `prior_id` · `origin_event` · `evidence_links`
- `confidence_before` · `confidence_after`
- `why_accepted_or_rejected` · `reviewer` · `decision`
- `affected_loops` · `applicable_runways` · `applicable_customers` (optional)
- `expiry` · `supersedes` · `superseded_by`
- `snapshot_id` · `ratified_at`

This turns every learned behavior into auditable institutional memory.

## W1 pipeline (SG reference — implemented)

See `scripts/motor_learning/` and fixtures. Cross-repo live wiring remains next.

## Next milestone (W2 — Runway live consume)

```text
Motor Event → Normalizer → Pattern Extractor → Prior Search → Similarity Score
→ Candidate Improvements → Shadow Execution → Evidence → ECQR Review
→ Ratified Prior + learning_receipt
```

Goal question: **"Have we seen something like this before?"**  
Zero model training. Everything is evidence.

## PASS checks

Machine truth: `data/nf_motor_learning_organ_pass_checks_v1.json`.

1. Motor can load a **shadow** policy snapshot derived from ≥ `min_samples` real job receipts.
2. Kaizen queue shows ranked learning proposals with ECQR delta estimate.
3. After founder/gate ratify, live prior changes stage routing and a receipt proves before/after ECQR.
4. Deadman sees `motor_learning_organ_v1` heartbeats within `2×` cadence.
5. Every accept/reject/rollback emits a complete `learning_receipt` (MLO-05).

## Forbidden

- Unsupervised architecture redesign / Evolution Agent self-redesign
- Data family product Runway build before `future_runway_gate`
- Base-model training checkpoints as a Phase-1 deliverable
- Unsupervised Level-3 bandit on high-risk tasks
- Wiring that bypasses HOLD / SG authority / promote-merge
- Treating this organ as a new product SKU or permanent Resident Role
- New Video product upgrade (Gallery cost-supply remains the media-economics path)

## SG answers

1. **P0 preserved?** Yes — observation/propose/shadow; no HOLD lift.
2. **Conflict?** No — addendum under portfolio routing O6/O8/O10.
3. **Superseded?** None.
4. **Authority?** SG for this packet; Motor executes live priors; founder for envelopes and consequential promote.
5. **Rollback?** Disable live ROI selection; fall back to stage-local static failover prior; mark snapshot `rolled_back`.
