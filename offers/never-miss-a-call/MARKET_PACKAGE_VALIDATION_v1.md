# Market Package Validation — "Never Miss a Call" AI Receptionist (v1)

**Status:** `LOCKED` · **Date:** 2026-07-09 · **Authority:** Founder (Market Package Validator) · **Lane:** `cursor/product-category-lock-v1` (isolated worktree)
**Evidence:** 10-agent research + adversarial-verify workflow (run `wf_9efe2b46-1f1`), 158 live web fetches. Machine-readable: [`SUPPLIER_EVIDENCE_v1.json`](SUPPLIER_EVIDENCE_v1.json).
**Offer:** *Never Miss a Call — AI Receptionist for local service businesses* (plumbers, HVAC, electricians, salons; Canada + US).

> Prices are vendors' **published end-customer** rates; reseller/wholesale rates are sales-gated unless noted. "⚠︎ unverified" = research-only. Vendor terms change — reconfirm before signing.

---

## 1 · SUPPLIER_COMPARISON_TABLE

| Criterion | My AI Front Desk (→"Frontdesk") | Trillet | OnCallClerk | ai-receptionist.com (0x4d2 LLC) | NextPhone → Synthflow¹ |
|---|---|---|---|---|---|
| Pricing | $20 / $99 (200 min) / custom | $49 / $99 / $299 | $0 / $29 / $99–299 | $14 / $39 / $99 / $199 | NextPhone $199 flat; Synthflow WL gated "$30k/yr" floor |
| White-label / reseller | ✅ full | ✅ full (Studio/Agency) ⚠︎ | ✅ full | ❌ none (/white-label 404) | NextPhone ❌ / Synthflow ✅ full |
| CA + US numbers | ✅ both (416/249/807 confirmed) | US ✅ / CA unconfirmed | US ✅ / CA gap confirmed | ✅ both | Synthflow ✅ both |
| Forwarding + porting | ✅ both | ✅ fwd / port US+AU | ✅ both | fwd ✅ / port unconfirmed | ✅ both |
| Calendar booking | Google + Calendly | Google/Calendly/Cal.com ⚠︎ | Google + Outlook | Google only | Google/Cal.com via Zapier |
| SMS/email lead summary | ✅ | ✅ | ✅ | partial | ⚠︎ via webhooks (not native) |
| CRM / Sheets / Zapier | ✅ 6,000+ Zapier | ✅ Zapier; webhooks "soon" | ✅ HubSpot/Zapier/webhooks | ❌ CRM "coming soon" | ✅ CRM/webhooks/Zapier |
| Stripe / bill our clients | ✅ one-click rebilling | ✅ claimed ⚠︎ | ✅ we invoice directly | ❌ | ✅ sub-accounts + rebilling |
| Setup time | ~5 min/client | ~5 min | ~5 min / <1 hr | <1 day | few days (builder) |
| Demo quality | ✅ live line 864-619-0619 | ⚠︎ no public demo # | ✅ live 888-885-5251 | ✅ 3 live demo lines | ❌ contact-sales |
| Cancellation risk | ⚠︎ "refunds generally not provided" + revocable license | 28-day money-back ⚠︎ | no-refund; 0 reviews | no-refund | ⚠︎ "billed 5+ mo after cancel" |
| Hidden per-min cost | $0.25/min after 200 | $0.12/min after 100/300 | undisclosed | $0.25/min after 60 | BYOK ~$0.15–0.37 (2–3× ad) |
| Resell as SourceA/Noetfield | ✅ but MAP price-floor clause | ✅ ⚠︎ unverified | ✅ (no anti-resale clause) | ❌ cannot | Synthflow ✅ (own domain) |
| **Verify verdict** | WL confirmed · resell **limited** · 7-day maybe | resell yes ⚠︎ **(verify FAILED)** | resell yes · conf **LOW** · **CA gap** | **resell NO** | resell yes · price **sales-gated** |

¹ NextPhone (getnextphone.com) is **not resellable** (affiliate-only, Pure Labs Inc). Synthflow researched as the white-label equivalent.
⚠︎ Trillet's adversarial verifier returned a placeholder — its resale/Stripe/Canada claims are **research-only, not verified**.

---

## 2 · RECOMMENDED_SUPPLIER → **My AI Front Desk** (white-label / "Frontdesk")

Only supplier that clears all three hard gates for a 7-day, resell-under-our-brand, turnkey launch:

| Hard gate | MAFD | Others fail because |
|---|---|---|
| Genuine full white-label + resell under our brand | ✅ | ai-receptionist ❌; NextPhone ❌ |
| Canada AND US numbers | ✅ confirmed | OnCallClerk ❌ (CA gap); Trillet ⚠︎ (CA unconfirmed) |
| Turnkey + ~5 min/client | ✅ | Synthflow ⚠︎ (builder + WL gated behind ~$30k/yr) |

Plus one-click Stripe rebilling of our own clients, unlimited sub-accounts, calendar + SMS/email + 6,000 Zapier integrations, a live demo line, lowest entry cost of the qualified set.

**Frame as a validation pilot, not a commitment** — MAFD's flags are contractual/economic (containable via offer design + small pilot); the others fail on capability. Do **not** build a large branded book until reseller terms are in writing.

**Backups:** Synthflow (power/scale, if cost absorbable); OnCallClerk/Trillet only after they confirm Canadian numbers in writing.

---

## 3 · RISK_FLAGS

**MAFD — verified deal-breakers:**
- 🔴 Revocable license / inverse lock-in — ToS: license "revocable at any time," vendor may terminate "with or without notice," "not liable for any losses." → keep our own client contracts + data export.
- 🔴 Wholesale sales-gated + MAP price floor — no published reseller rate; MAP caps our pricing autonomy. → get rate card before pricing publicly.
- 🔴 Per-minute overage $0.25/min after 200 min — margin killer for high-call trades. → cap included minutes + transparent pass-through.
- 🟠 "Refunds generally not provided" + third-party billing complaints — under white-label they hit our brand. → run our own Stripe + refund/support SLA.
- 🟠 No HIPAA/SOC2/TCPA published → exclude medical/legal/financial. 20 outbound calls/day cap. Mid-rebrand (URL churn).

**Cross-vendor:**
- 🔴 Canada number gap eliminates OnCallClerk, endangers Trillet for a CA+US market.
- 🟠 Trillet not adversarially verified (verifier placeholder) — treat its claims as unconfirmed.
- 🟠 Synthflow BYOK ≈ 2–3× advertised per-minute; white-label behind ~$30k/yr gate.

---

## 4 · EXACT FIRST OFFER SPECS

**Name:** *Never Miss a Call — AI Receptionist for Local Service Businesses*
**Target (first cohort):** plumbers, HVAC, electricians, roofers, landscapers, salons — CA + US. **Exclude** medical/legal/financial until compliance exists.
**Promise:** *"Every call answered in 2 rings, 24/7 — booked, texted to you, and logged — or it's free this month."*

**Client gets:**
1. Branded AI receptionist on a new local number or forwarding their existing line (24/7, after-hours, overflow).
2. Answers FAQs, books jobs into their Google Calendar, captures caller name/number/reason.
3. Instant SMS + email lead summary after every call.
4. Leads pushed to their CRM / Google Sheet via Zapier.
5. Monthly "calls answered / jobs booked / leads captured" report.

**Pricing (our retail — profitable even at vendor retail cost):**
- Setup **$497 one-time** (config, number, branding, calendar wiring).
- **$297/mo**, includes **up to 500 answered minutes**; overage **$0.49/min** transparent pass-through.
- Month-to-month, cancel anytime (we offer this regardless of vendor terms; we absorb vendor risk).
- Guarantee: 14-day "answered or refunded" — honored via **our own Stripe** (never rely on vendor no-refund).

**Economics guardrail:** platform cost ≈ $99/mo + overage; 500-min cap + pass-through keeps margin positive in a busy month. **Pilot 1–3 clients first** to measure real minute usage + confirm wholesale before scaling.
**Billing:** our own Stripe. **Setup SLA:** live within 72 hours (inside 7 days).
**Compliance line (mandatory):** AI-disclosed, call-recording/consent notice, no medical/legal/financial claims.

---

## Next action (open)
Reseller terms are sales-gated → the only way to lock true margin is to apply and get the wholesale + MAP + overage rate card in writing. Request drafted: [`RESELLER_RATE_CARD_REQUEST_v1.md`](RESELLER_RATE_CARD_REQUEST_v1.md). Landing page build spec: [`SONNET_BUILD_PACKET_LANDING_v1.yaml`](SONNET_BUILD_PACKET_LANDING_v1.yaml).
