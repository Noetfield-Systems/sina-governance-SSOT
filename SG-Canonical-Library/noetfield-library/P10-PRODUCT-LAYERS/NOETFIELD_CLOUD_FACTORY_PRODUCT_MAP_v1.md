# Noetfield / SourceA Cloud Factory — Commercial Product Map (v1)

**Status:** `PRODUCT_CATEGORY_MAP_READY_FOR_RATIFICATION` · **Locked:** 2026-07-09T07:06:11Z · **Status patch:** `PRODUCT_CATEGORY_LOCK_STATUS_PATCH_v1` (CAT-03/04/06) · **Authority:** SG-owned (Sina Governance SSOT)
**Registry (source of truth):** [`PRODUCT_CATEGORY_REGISTRY_v1.json`](PRODUCT_CATEGORY_REGISTRY_v1.json) · **Library mirror:** `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/`
**Evidence:** 20-agent evidence + adversarial-verify pass (run `wf_0e4cdcf8-c34`), 0 status downgrades, all high-confidence.

> This map LOCKS the identity of the commercial product categories. It is **not** a build claim. It fixes what each category *is*, how it differs, and the receipt that gates its activation. Execution resumes **only** against the registry above.

---

## North Star

Noetfield / SourceA **Cloud Factory Platform** lets Sina or clients **issue orders** that are converted by **P0-PGR** into governed **prompt packets**, routed through **cloud factory lines**, executed in **isolated sandboxes/worktrees**, verified with **receipts**, and surfaced through **Studio IDE / client workspace**.

## The factory flow (and where each category lives)

```
   ORDER ──▶ [CAT-03 P0-PGR] ──▶ [CAT-04 Factory Lines] ──▶ [CAT-05 Sandboxes] ──▶ RESULT
   (Sina/client)   compile packet      governed cloud run       isolated workcell     branch/PR/preview
        │                │                     │                      │
        │           [CAT-01 Governed Agent Memory] feeds authority + freshness + provenance into every step
        │                                     │
        └────────────▶ [CAT-08 Studio IDE / Cockpit] surfaces orders, approvals, runs, receipts, deploys
                                              │
        [CAT-06 Workflow Builder] composes multi-step governed work · [CAT-07 App Builder] emits governed internal tools
                                              │
                          [CAT-09 Receipt / Trust / Audit Layer] proves every action (spine under all)
                                              │
                          [CAT-02 RepoGraph L0] gives agents zero-token orientation across the whole factory
                                              │
                          [CAT-10 Vertical Proof] = TrustField · AI Value Governance · SourceA · WitnessBC
```

- **Runtime spine:** CAT-03 (prompt runtime) → CAT-04 (lines) → CAT-05 (sandboxes).
- **Governance memory:** CAT-01 (what's authoritative/fresh) + CAT-02 (repo orientation).
- **Trust spine:** CAT-09 (receipts) under everything; CAT-08 is the operator cockpit.
- **Surfaces:** CAT-06 (workflows), CAT-07 (apps) sit on top of the runtime.
- **Proof:** CAT-10 lanes demonstrate the factory in real verticals.

## Status at a glance

| # | Category | Product name | Build status | Ladder | Domain target |
|---|----------|--------------|--------------|--------|---------------|
| 01 | Governed Agent Memory | MemoryGate / DecisionGraph | built-not-activated | P3 | standalone-later |
| 02 | Repo / Code Graph Memory | **RepoGraph L0** | **live-running** ✅ | **P4** | standalone-later |
| 03 | Prompt Governance Runtime | P0-PGR | built-not-activated · **R2 cloud PASS** | P3 | umbrella |
| 04 | Cloud Factory Lines | Forge Factory | built-not-activated · **not VERIFIED** | P3 | standalone-later |
| 05 | Sandbox / Worktree Execution | Forge Workcells | partial-scaffold | P2 | standalone-later |
| 06 | Agentic Workflow Builder | Noetfield Workflow Builder | partial-scaffold | P2 | standalone-later |
| 07 | No-code App Builder | Noetfield App Factory | **concept-only** | P0 | standalone-later |
| 08 | Studio IDE / Control Cockpit | Noetfield Studio IDE | built-not-activated | P3 | subdomain |
| 09 | Receipt / Trust / Audit Layer | ReceiptGraph | built-not-activated | P3 | umbrella |
| 10 | Vertical Proof Products | TrustField · AI Value Gov · SourceA · WitnessBC | built-not-activated* | P3* | mixed per-lane |

\*CAT-10 per-lane: TrustField software-live (receipt-attested, pre-revenue); AI Value Governance pre-launch; SourceA internal/stale; WitnessBC preview-only (cutover pending). **No revenue on any lane.**

## Category map (one line each)

- **01 · Governed Agent Memory** — authority-scoped memory with provenance/freshness/receipts/gates; a governance layer *over* memory, not a store. Real internal lanes, not unified into a product.
- **02 · RepoGraph L0** — zero-token structural repo memory + a broad-read gate; ~2–6k orientation tokens vs a ~371k blind pass. **The only live-running category.**
- **03 · P0-PGR** — evidence-based prompt compiler → router → critic → ROI judge → receipt verifier. **R1 + R2 cloud PASS** (2 GitHub cloud runs, verified); R3 cron HOLD, R4/R5 not active; LLM stages not wired. Built-not-activated as a product (R3+ founder-gated).
- **04 · Cloud Factory Lines** — governed execution lines (gate + cost token + receipt) *overlaying* GitHub Actions/workers. No real cloud execution proven yet.
- **05 · Sandbox / Worktree Execution** — isolated workcells with branch/PR/preview/rollback. Git-worktree isolation today; core spec still on another branch, unbuilt.
- **06 · Agentic Workflow Builder** — governed multi-step workflows with approvals/receipts/cost/regulated-action gates. No builder UI; internal motors only.
- **07 · No-code App Builder** — prompt-to-app for governed internal tools. **Concept-only**; decide whether it folds into the Studio IDE before any build.
- **08 · Studio IDE / Cockpit** — the operator cockpit for orders→approvals→runs→receipts→deploys. Real Next.js app; autonomous loop not yet green; local-first.
- **09 · Receipt / Trust / Audit Layer** — every action emits an independently-verifiable receipt (proof+authority+cost+files+deploy+outcome). Thousands of receipts; auditor never run; no unified index.
- **10 · Vertical Proof Products** — four proof lanes demonstrating the factory in real verticals; TrustField stays a decision/governance layer (never touches value).

## Governing constraints (canon)

1. **Noetfield's public GTM = 3 contract SKUs only** (Trust Brief, Copilot Governance Pack, Bank Pilot). These 10 categories are **platform/internal** products, not new public SKUs.
2. **"Noetfield never touches value — only policy, compliance logic, and traceability."** TrustField's payment/onboarding framing is a governance/decision layer, never money movement.
3. **Product/canon boundary:** product docs describe *what is sold*; they cross-reference canon (*how it runs*) but never compete with it.
4. This lock makes **no public claim, buys no domain, merges/deploys nothing, and defines no new category.**

## Lock rules

Do not build code · Do not buy domains · Do not create public claims · Do not merge or deploy · Do not let workers define new categories · **Lock categories first; execution resumes only against the registry.**

---

**FINAL STATUS: `PRODUCT_CATEGORY_MAP_READY_FOR_RATIFICATION`** — lock receipt: [`../receipts/SG_PRODUCT_CATEGORY_LOCK_RECEIPT_v1.json`](../receipts/SG_PRODUCT_CATEGORY_LOCK_RECEIPT_v1.json) · status patch: [`../receipts/PRODUCT_CATEGORY_LOCK_STATUS_PATCH_v1.json`](../receipts/PRODUCT_CATEGORY_LOCK_STATUS_PATCH_v1.json)

> **Ratification precondition (reverse-drift):** the CAT-03/04 proving receipts currently live only in the archived clone `~/Projects/sina-governance-ssot.MIGRATED-2026-07-08` and must be synced into canonical before commit. See the status-patch receipt.
