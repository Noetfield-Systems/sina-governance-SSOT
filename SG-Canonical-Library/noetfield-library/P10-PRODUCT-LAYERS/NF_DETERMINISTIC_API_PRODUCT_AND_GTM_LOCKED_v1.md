# NF — DETERMINISTIC API PRODUCT & GTM — LOCKED v1

**Version:** v1.1.0_locked_20260719
**Status:** LOCKED / RATIFIED · **COMMERCIAL PLANE LIVE**
**Authority:** Founder order ("SAVE AND LOCK") + founder order to ship standalone Cloudflare landing
**Tier:** P10-PRODUCT-LAYERS (external product surface + go-to-market)
**Depends on:** `NF_NOETFIELD_RUNWAY_PRODUCT_LOCKED_v1.md` · `COST_EXECUTION_DOCTRINE_LOCKED_v1.md` · `AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED`
**Relationship:** External commercial framing of the same Unified Motor. Does **not** reopen Motor architecture or Runway internal taxonomy.

**Live commercial plane (canonical):**
- Landing: https://www.noetfield.com/deterministic-api/
- Catalog: https://www.noetfield.com/deterministic-api/catalog.json
- API (production): https://nf-deterministic-api-v1.sina-kazemnezhad-ca.workers.dev
- Source: `Noetfield` → `deterministic-api/`

**Retired (redirect-only):** `nf-deterministic-api.pages.dev` → www landing (temporary duplicate removed).

---

## One line

> Clients do not buy a model, agents, Runways, or the Motor. They buy a **deterministic API that returns guaranteed, usable outcomes** — and we fulfill it at near-zero cost.

## What is sold (external product)

**The Noetfield API** — specialized, task-specific, OpenAI-compatible endpoints. Multi-model underneath (DeepSeek / Kimi / GLM / HF-open), with deterministic gates that guarantee schema / tool-call / structure correctness, auto-repair or escalate on failure before the response leaves the API.

Internal names (Motor, Runway, NOOS, SourceA, DAG, recipe) are **not** buyer-facing.

## Product line (ship order)

| # | Endpoint | Promise | Status |
|---|----------|---------|--------|
| 1 | `POST /v1/chat/completions` — Bulletproof drop-in | Cheaper models, **valid JSON / tool calls guaranteed**; auto-repair on failure | **FLAGSHIP — build first** |
| 2 | `POST /v1/extract` — Mess → structure | Raw text/email/PDF → clean structured JSON row | Backlog (ads may tease) |
| 3 | `POST /v1/webhooks/...` — Stateful task worker | Turnkey durable agent on webhook, no orchestration code | Backlog |

**One SKU live first (API 1).** Do not build 2 and 3 before API 1 ships and sells.

## Why it is profitable (measured, not estimated)

Ground truth = Motor replay fixtures (`packages/runway-core/tests/fixtures/motor-replay/`, NRF-004):

| Outcome | Metered model cost |
|---------|-------------------|
| QUALIFIED | **$0.000060** and **$0.000050** |
| NOT_QUALIFIED (2 bounded repairs) | **$0.000210** |

Qualified example `motor-verify-29676246208`: diagnose `$0.000024` + fix `$0.000036` = **$0.000060**.

Deterministic Motor/NOOS work (auth, schema, verify, heartbeat, COST-T0) = **$0.0**.
Intelligence ceiling = **< $0.001 exclusive** per call/job.

### Margin law
```text
Most of the Motor       = $0 (deterministic, COST-T0)
LLM only on thin slice  = ~$0.00005–$0.00006 per qualified job
Charge in cents         → structural ~98–99% gross on qualified path
```

If a client pays **$0.005** for a guaranteed result and fulfillment is **~$0.00005–$0.00006**, gross ≈ **~98–99%**. Even with some NOT_QUALIFIED / repair traffic at `$0.000210`, blended gross stays **~98%+**.

## Go-to-market (locked)

### Website (one job)
- Headline: **drop-in OpenAI replacement · cheaper · guaranteed valid JSON / tool calls**
- Proof: change one line — `base_url` → Noetfield endpoint
- CTA: **Get API key** + starter credits
- Referral line (public): **Refer a friend → you both get +$10 Noetfield API credit**

### Referral economics
$10 credit ≈ **~$0.10–$0.20 real fulfillment cost** if fully burned at measured qualified rate. Referral is free-to-cheap acquisition; it is a marketing line, not a cash payout.

### Ads (intent-based only)
Target buyers already searching to buy:
- DeepSeek / Kimi JSON schema reliability
- OpenAI → cheap-model migration (tool calling)
- structured output / function-calling failures
- cutting LLM / inference API bills

Buyer: CTO / VP Eng at SaaS over $5k/mo LLM spend · AI dev-agency founders · AI FinOps leads.
Landing target = the single API page. **No** "AI agent platform", **no** Motor/Runway language in ads.

### Loop
```text
Intent ads → API landing → key + credits → ship traffic → refer friends (+$10 each) → top-up
```

## Billing (minimal, no redesign)
- API key + credit balance (D1 or existing store); meter each call against measured cost; `402` at zero balance.
- Stripe top-up link adds credits via webhook.
- Reuse existing metering; do **not** open a pricing/Stripe/credit-metering redesign (respect `NF_RUNWAY_CORE_FAMILIES_COMPOSITION_LOCKED_v1` non-goals).

## Forbidden by this lock
- Selling Motor / Runways / governance as the SKU
- Exposing internal vocabulary (Motor, Runway, NOOS, recipe, DAG) on buyer surfaces
- Building API 2 / API 3 before API 1 is live and sold
- Brand/awareness ads instead of intent ads
- Paying referral in cash (credit only)
- Frontier/paid-premium models on the automatic hot path (cheap-first per COST doctrine)
- API keys in chat or git — runtime secret store only
- Reopening Unified Motor architecture or Runway taxonomy

## Authority / scope answers
1. **P0 preserved?** Yes — one Unified Motor; cheap-first; deterministic gates; receipts.
2. **Conflict?** No — external commercial framing; internal architecture unchanged.
3. **Supersedes?** Nothing. Adds the external API product + GTM layer.
4. **Founder-only?** Final price points, Stripe live keys, ad budget, production promote.
5. **Evidence → P99?** Per-call cost receipts; referral credit ledger; ad → key → spend funnel.

---

*v1.0.0_locked_20260719 — first write. Founder "SAVE AND LOCK". Margin figures cite measured Motor replay fixtures ($0.000050 / $0.000060 qualified; $0.000210 not-qualified), not advisor estimates.*
*v1.1.0_locked_20260719 — standalone Cloudflare Pages commercial plane live at nf-deterministic-api.pages.dev with /adapt/ + catalog for sister sites; staging API Worker linked.*
*v1.2.0_locked_20260721 — canonical landing consolidated to www.noetfield.com/deterministic-api/; pages.dev redirect-only; $10 starter + referral credits; product name Noetfield API.*
