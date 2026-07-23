# MACHINE_LOOPS v1 — Zero-Founder Operational Design

**Status:** machine_wired · E2E gate: `scripts/validate-machine-loops-e2e-v1.sh`
**Parents:** `docs/FOUNDER_CANON_v1.md` · governed-autorun v3 · `data/machine-process-loops-v1.json`
**Purpose:** practical mechanics of canon §6–§8 — validation, critique, repair, audit, research as machine loops; founder triggers retired via receipts.

---

## 0. TWO STRUCTURAL RULES ALL LOOPS OBEY

**R1 — Fresh context per role.** Every loop actor starts with: canon pointer line, dispatch template, live repo state. Never chat history as truth.

**R2 — Machine dispatch from templates.** Templates in `.agent-policy/dispatch-templates/` (versioned). Reconciler instantiates from receipts and queue state. Failure receipts are valid dispatch sources.

---

## Implementation map (repo wiring)

| Loop | Canon § | Script | Receipt |
|------|---------|--------|---------|
| Worker execution | §1 | `scripts/worker_execution_gate_v1.py` | `receipts/proof/worker-execution-gate-latest-v1.json` |
| Machine validation | §2 | `scripts/validate-machine-process-v1.sh` | `receipts/proof/machine-validation-latest-v1.json` |
| Machine merge T0–T1 | §2 | `scripts/machine_merge_gate_v1.py` | `receipts/proof/machine-merge-gate-latest-v1.json` |
| Adversarial critique | §3 | `scripts/adversarial_critique_gate_v1.sh` | `receipts/proof/adversarial-critique-latest-v1.json` |
| Critic verdict | §3 | `scripts/adversarial_critic_receipt_v1.py` | `receipts/proof/adversarial-critic-latest-v1.json` |
| Second critic (T2) | §3 | `scripts/adversarial_critic_second_v1.py` | `receipts/proof/adversarial-critic-second-latest-v1.json` |
| Receipt chain audit | §5 | `scripts/receipt_chain_hmac_audit_v1.py` | `receipts/proof/receipt-chain-audit-latest-v1.json` |
| Dispatch reconciler | R2 | `scripts/dispatch_template_reconciler_v1.py` | `receipts/proof/dispatch-instantiated-latest-v1.json` |
| Self-repair | §4 | `scripts/self_repair_ci_to_kaizen_v1.py` | `receipts/proof/self-repair-latest-v1.json` |
| Outside audit | §5 | `scripts/spine_live_probe_v1.py` | `receipts/proof/spine-live-probe-latest-v1.json` |
| Deep research | §6 | `scripts/uncertainty_research_enqueue_v1.py` | `receipts/proof/uncertainty-research-latest-v1.json` |
| Kaizen growth | §7 | `scripts/autorun_kaizen_queue_v1.py` | `receipts/cloud/kaizen/kaizen-pick-latest-v1.json` |
| Autonomy expansion | §8 | `scripts/founder_trigger_retirement_evaluator_v1.py` | `receipts/proof/founder-trigger-retirement-latest-v1.json` |
| Cycle rollup | — | `scripts/machine_cycle_receipt_v1.py` | `receipts/proof/machine-cycle-latest-v1.json` |
| **E2E gate** | all | `scripts/validate-machine-loops-e2e-v1.sh` | `receipts/proof/machine-loops-e2e-latest-v1.json` |

**Motor:** `scripts/loop_specialist_tick_v1.py` → `run_machine_process_cycle()` (piggyback SA-T-machine-cycle on */15 loop-specialist tick).

**Retirement SSOT:** `data/founder-trigger-retirement-registry-v1.json` · shadow-decision ledger: `data/founder-trigger-ledger-v1.json`

---

## 1–8. Loop definitions

See Desktop origin and `docs/FOUNDER_CANON_v1.md`. Machine substitutes are live; founder triggers are tracked technical debt with retirement contracts.

### Merge authority (§2 — implemented)

| Tier | Change class | Gate |
|------|--------------|------|
| T0 | docs, tests, receipts, lint | `machine_merge_gate_v1.py --tier T0` on criteria 1–4 |
| T1 | scoped app code | `machine_merge_gate_v1.py --tier T1` + critic APPROVE |
| T2 | deps, CI files | primary + second critic APPROVE + HMAC receipt chain green |
| T3 | schema, gates, governance | founder (never auto-retire) |

Bootstrap retirement: `FT-MERGE-T0-T1` in retirement registry — 5 consecutive E2E greens flips T0–T1 to machine merge.

---

## Failure flow

```
failure → contain → critic → repair → [2× fail] → research + audit
→ validate externally → receipt → merge by tier → continue
→ Sina ONLY IF: capital/legal ∨ irreversible-L5 ∨ phase unlock
```

---

## E2E check

```bash
bash scripts/validate-machine-loops-e2e-v1.sh
```

All loops must emit receipts with `canon_version: "FOUNDER_CANON_v1"`.
