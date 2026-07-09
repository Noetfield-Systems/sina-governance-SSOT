# Category → Phase Ladder (v1)

**Status:** `READY_FOR_RATIFICATION` (part of `PRODUCT_CATEGORY_MAP_READY_FOR_RATIFICATION`) · **Locked:** 2026-07-09T07:06:11Z · **Status patch:** `PRODUCT_CATEGORY_LOCK_STATUS_PATCH_v1` (CAT-03/04/06) · **Authority:** SG-owned
**Source of truth:** [`PRODUCT_CATEGORY_REGISTRY_v1.json`](PRODUCT_CATEGORY_REGISTRY_v1.json) → `categories[].status_ladder_phase` / `next_build_phase` / `receipt_required_to_activate`

> The ladder maps each category to a maturity rung and names the **single receipt** that advances it. A category may not advance a rung without producing that receipt. Rungs beyond internal execution are **founder-gated**.

## The ladder

| Rung | Meaning |
|------|---------|
| **P0 CONCEPT** | Named and reasoned about; no product artifact exists. |
| **P1 SPEC-LOCKED** | Schema/spec/plan committed; nothing runnable. |
| **P2 BUILT-SCAFFOLD** | Runnable pieces exist; not wired end-to-end. |
| **P3 BUILT-NOT-ACTIVATED** | Wired/runnable internally; no external/commercial activation. |
| **P4 LIVE-RUNNING (internal)** | Real executions emit receipts inside the factory. |
| **P5 PROOF-LANE VALIDATED** | External/vertical proof with outcome receipts. |
| **P6 COMMERCIAL-ACTIVATION-GATED** | Packaged; founder + receipt gate to sell. |

**Mechanism (grounded in the real loop):** sandbox proposes → independent verifier checks → promotion gate → only **PASS** reaches live; STEP-10-class actions are **founder-gated** (`PHASE_LOOP_BUILD_PLAN_v0.1.md`, `P0_PGR_CLOUD_ACTIVATION_LADDER_v1.md`).

## Current rung → next rung → activation receipt

| Category | Current | Next | Activation receipt (advances the rung) |
|----------|---------|------|----------------------------------------|
| 01 Governed Agent Memory | **P3** | P4 | `MEMORYGATE_COMPOSITE_GATE_RECEIPT` — one action gated by combined authority + freshness + provenance, + a non-founder consumer, + one ROI line. |
| 02 RepoGraph L0 | **P4** ✅ | P5 | `REPOGRAPH_TOKEN_TAX_RECEIPT` — measured before/after tokens from a real session + a green build+verify receipt in a second repo. |
| 03 P0-PGR | **P3** (R1+R2 cloud PASS) | R3 | R2 cloud PASS ✅ achieved (`P0PGR_R2_CLOUD_MANUAL_PASS_v1-20260709T001540Z`). Next: `FOUNDER-UNLOCK-R3-CRON-SHADOW` + canonical lane DECLARED→VERIFIED after a 24h green window. |
| 04 Cloud Factory Lines | **P3** (line R2 PASS; loops DECLARED_ACTIVE) | P4 | `FACTORY_LINE_VERIFIED` — 24h zero-manual scheduled-receipt window (pa-health-cron + pa-deploy-truth) + secrets wired → DECLARED_ACTIVE→VERIFIED. |
| 05 Sandbox / Worktree | **P2** | P3 | `WORKCELL_FACTORY_RUN_RECEIPT` — a real (non-synthetic) factory-run: ledger row allocated, wall hit (BLOCKED_WITH_REASON), exit via branch/PR (no auto-merge) + founder build-unlock. |
| 06 Workflow Builder | **P2** | P3 | `WORKFLOW_GOVERNED_APPROVAL_RECEIPT` — one partner-authored workflow packet run with an approval gate + a schema-valid receipt. **DIRECT evidence only — P0-PGR R2 PASS does NOT advance this.** |
| 07 App Builder | **P0** | P1 | `APP_FACTORY_SPEC_LOCK_RECEIPT` — a locked scope-decision spec + one real prompt→governed internal tool (deployed/viewable, approval-gated, generation receipt). |
| 08 Studio IDE / Cockpit | **P3** | P4 | `STUDIO_LOOP_GREEN_RECEIPT` — a real non-synthesized sandbox→gate→verify(PASS)→promote receipt (verify.ok=true) + a run from an installed/notarized app. |
| 09 Receipt / Trust / Audit | **P3** | P4 | `RECEIPTGRAPH_SELF_AUDIT_RECEIPT` — first `audit_receipt_ledger_v1.py --write-receipt` across all 3 receipt stores, ok=true, countersigned by the independent verifier. |
| 10 Vertical Proof (per lane) | **P3** | P4/P5 | `PROOF_LANE_LIVE_TRUTH_RECEIPT` (per lane) — HTTP 200 on production domain, expected_build==live_build, committed in-repo; commercial activation additionally needs a **revenue receipt** (signed SOW / paid invoice). |

## Rung notes & founder gates

- **CAT-02** is the only category whose PRODUCT is at **P4** (live-running). CAT-03's runtime now has real R2 cloud executions (PASS), but the category stays **P3** as a product (R3+ founder-gated); everything else is P3 or below.
- **CAT-03 / CAT-04 (P0-PGR R2) are DONE:** R2 cloud-manual PASS executed on 2 GitHub cloud runs (verified, receipt `P0PGR_R2_CLOUD_MANUAL_PASS_v1-20260709T001540Z`). CAT-03 now waits on `FOUNDER-UNLOCK-R3-CRON-SHADOW`; CAT-04's TrustField loops are DECLARED_ACTIVE (PR #10 built, RECONCILED_PASS) and wait on a 24h zero-manual window to reach VERIFIED. **CAT-06 is explicitly NOT advanced by the R2 PASS** — it stays P2 until it has its own direct workflow-builder receipt.
- **Reverse-drift:** the CAT-03/04 proving receipts live only in the archived clone `~/Projects/sina-governance-ssot.MIGRATED-2026-07-08`; sync to canonical is a ratification precondition.
- **CAT-05** core spec exists only on branch `cursor/machine-autonomy-loops-v1`; it is not on disk on the current HEAD — reconcile before building.
- **CAT-07** is the only **P0**; it must not advance to any build without a scope-decision spec (candidate to fold into CAT-08).
- **CAT-10** lanes: a **live domain is not a rung** — TrustField is software-live (receipt-attested) but still **P4 pending revenue**; WitnessBC is preview-only; AI Value Governance is pre-launch; SourceA is internal/stale.
- **No rung above P4 for any category** without an explicit founder-unlock receipt in `receipts/p0pgr/founder/`. Commercial activation (P6) is a separate, explicit founder decision — never automatic on receipt.

## Rule

**No category advances a rung without producing its named receipt.** Cron / auto-dispatch / real deploy / send / merge remain founder-gated regardless of rung. Shadow (zero-execution) cycles do **not** count as real executions.
