# Product Moat Comparison (v1)

**Status:** `READY_FOR_RATIFICATION` (part of `PRODUCT_CATEGORY_MAP_READY_FOR_RATIFICATION`) · **Locked:** 2026-07-09T07:06:11Z · **Status patch:** `PRODUCT_CATEGORY_LOCK_STATUS_PATCH_v1` (CAT-03/04/06) · **Authority:** SG-owned
**Source of truth:** [`PRODUCT_CATEGORY_REGISTRY_v1.json`](PRODUCT_CATEGORY_REGISTRY_v1.json) → `categories[].comparison_category` / `noetfield_differentiation`

> The single throughline across all 10 categories: **governance + receipts + gates.** Incumbents optimize capability (retrieve, run, automate, edit). Noetfield's wedge is to make every one of those actions **authority-scoped, cost-aware, and receipted** — provable, not just performed.
>
> **Honesty gate (moat status):** `PROVEN` = validated by a real receipt today · `CLAIMED` = built internally but not externally validated · `ASPIRATIONAL` = differentiation is real in principle but the artifact/proof does not exist yet. Most categories are `CLAIMED`; treat externally as unproven until the activation receipt exists.

## Comparison matrix

| Category | Incumbents | What incumbents lack | Noetfield differentiation | Moat status |
|----------|-----------|----------------------|---------------------------|-------------|
| 01 Governed Agent Memory | Graphiti, Zep, Mem0, vector memory | authority-scope, freshness/expiry, provenance, ROI, execution gate | Memory that can **block an action**, not just recall text: authority-scoped surfaces (ACTIVE/SUPERSEDED/RETIRED) + staleness gate + sha256 provenance + decision receipts | **CLAIMED** (lanes real internally; not unified/branded; Graphiti was rejected internally, not beaten as a product) |
| 02 RepoGraph L0 | Graphify, code search, repo-graph tools | a **broad-read gate** that changes agent behavior; token-cost discipline | Zero-token structural memory + an AGENTS.md gate: ~2–6k orientation tokens vs a ~371k blind pass | **PROVEN (internal)** — live-running; but token savings not yet measured by receipt, single-repo, edges are regex not AST |
| 03 P0-PGR | prompt hubs, prompt managers, agent prompt libraries | compile/route/critic/ROI-judge/receipt-verify; governance over dispatched work | Orders → governed, lint-clean packets that are gated, phased, and receipted with founder unlocks | **CLAIMED** — R1+R2 cloud PASS (2 GitHub cloud runs, verified); R3+ founder-gated; LLM critic/ROI stages still not wired (deterministic Python, $0 cost) |
| 04 Cloud Factory Lines | Fly.io, Railway, Modal, GitHub Actions, agent runners | per-run gate + cost token + receipt + ROI control | A governance **overlay** where each line's runs are gated, costed, and receipted (not its own compute plane) | **CLAIMED** — line has R2 cloud PASS; TrustField loops built (PR #10, RECONCILED_PASS) → DECLARED_ACTIVE, **not VERIFIED** (24h zero-manual window pending) |
| 05 Sandbox / Worktree | cloud IDEs, Replit agents, Cursor bg agents, Devin | governed isolation + provable rollback + no-auto-merge law | Isolated workcells with branch/PR/preview/rollback + isolation/wall receipts; never auto-merge to venture repos | **ASPIRATIONAL** — git-worktree isolation only; core spec unbuilt/off-branch; no container/microVM; rollback unevidenced |
| 06 Agentic Workflow Builder | Zapier, Make, n8n, LangGraph, CrewAI | approval gates, receipts, cost control, regulated-action boundaries | Multi-step work with human approvals + receipts + cost/value class + regulated-action gates | **ASPIRATIONAL** — no builder/UI; internal motors only; census audit_status RED; P0-PGR R2 PASS does **not** advance this category |
| 07 No-code App Builder | Lovable, Bolt, Replit, v0, Bubble/Softr | a policy/receipt/approval layer for regulated internal tools | Prompt-to-app for **governed** internal tools/portals/dashboards with gate + generation receipt | **ASPIRATIONAL (concept)** — nothing built; may fold into the Studio IDE |
| 08 Studio IDE / Cockpit | Cursor, VS Code, Retool, internal dev portals | one governed view of orders→approvals→runs→receipts→deploys | Governance-native cockpit surfacing the full order→receipt→deploy chain with worktrees + gate/promote receipts | **CLAIMED** — real app + receipts + worktrees; autonomous loop not green; local-first only |
| 09 Receipt / Trust / Audit | audit logs, LangSmith, observability, SOC2 evidence tools | authority + cost + changed-files + deploy-state + outcome as **independently-verifiable** receipts | Every action → a receipt (proof+authority+cost+files+deploy+outcome) checked by a **separate** verifier | **CLAIMED** — thousands of receipts + independent verifier exist; auditor never run; no unified schema/index |
| 10 Vertical Proof | vertical tools per lane (fintech onboarding, AI-ROI, control-plane, proof/media) | governance + receipts as the throughline; end-to-end proof | Four lanes proving the factory with outcome receipts; TrustField stays a decision layer (never touches value) | **PARTIAL** — TrustField software-live (receipt-attested); others pre-launch/preview/stale; **no revenue on any lane** |

## Moat thesis (locked)

1. **The category is not the capability — it's the governance around it.** Anyone can retrieve, run, automate, or edit. The defensibility is: *every action is authority-scoped, cost-attributed, and receipted, and unsafe actions are gated.*
2. **Receipts compound.** CAT-09 is the spine: as more categories emit uniform, independently-verifiable receipts, the trust surface (and switching cost) grows across the whole factory.
3. **The founder-gate + independent-verifier pattern is the anti-theater moat.** This ecosystem has documented "fake-green" incidents; a moat built on *provable* execution (not claimed capability) is the differentiator competitors optimizing for speed skip.

## Honest moat posture (external)

- **Do not** present any `CLAIMED` or `ASPIRATIONAL` differentiation as a competitive win externally. The only externally-defensible-*today* claim is CAT-02 being live-running — and even that lacks a measured-savings receipt.
- **Do not** benchmark against Graphiti/Zep/Mem0/Zapier/etc. publicly; the internal comparisons are tool-selection decisions, not validated head-to-heads.
- The moat is **real in architecture, unproven in market.** Each category's activation receipt (see [`CATEGORY_TO_PHASE_LADDER_v1.md`](CATEGORY_TO_PHASE_LADDER_v1.md)) is exactly what converts `CLAIMED` → `PROVEN`.
