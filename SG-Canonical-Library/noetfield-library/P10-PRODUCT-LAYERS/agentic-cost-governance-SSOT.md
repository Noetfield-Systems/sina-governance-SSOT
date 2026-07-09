# AGENTIC COST GOVERNANCE — SSOT (Draft)

**Version:** v0.1.0_draft_20260705  
**Status:** DRAFT SSOT (pilot-ready vocabulary)  
**Authority:** FOUNDER_CANON v1 → this SSOT → agentic-cost-governance-service.md  
**Scope:** Vocabulary, policy rules, ROI metrics for Tier 1–4 offers  

---

## 1. VOCABULARY (binding in service context)

| Term | Definition |
|------|------------|
| **Agentic spend** | Token + API cost attributable to agent workflows (multi-step, tool-calling, batch) |
| **Cost leak** | Spend above policy baseline without measured ROI signal |
| **Model tier** | Commodity (fast/cheap) vs premium (reasoning/expensive) routing class |
| **Policy pack** | Documented guardrails: per-task model rules, budgets, fallback chains |
| **Spend ledger** | Customer-owned record of actual vs policy vs ROI (we advise; customer holds data) |
| **Firewall (pilot)** | Sandbox policy enforcement test — not live production unless receipted |
| **Agentic FinOps** | Governance layer for AI automation spend (audit + policy + visibility) |

## 2. POLICY RULES (minimum set)

1. **Audit before enforce** — Tier 1 diagnostic required before Tier 3 firewall pilot
2. **Customer implements** — Noetfield delivers policy packs; customer deploys in their infra
3. **No custody** — No PSP/MSB; no holding customer funds
4. **Receipt-gated claims** — Live firewall / production enforcement claims require customer receipt
5. **Model ROI signal** — Every premium-model route must have documented task class + success metric
6. **Commodity default** — Unless ROI proof exists, default routing favors commodity tier

## 3. ROI METRICS (reporting)

| Metric | Unit | Use |
|--------|------|-----|
| Cost per successful task | USD / completion | Compare model tiers |
| Leak rate | % spend above policy | Tier 1 audit headline |
| Policy compliance | % routes matching pack | Tier 2 validation |
| Premium justification rate | % premium routes with ROI doc | Tier 4 advisory |

## 4. TIER BINDING

| Tier | SSOT applies |
|------|--------------|
| Tier 1 AI Spend Leak Audit | Vocabulary + leak rate + top-5 targets |
| Tier 2 Policy Pack | Full policy rules + templates |
| Tier 3 Firewall Pilot | Policy rules + sandbox receipt schema |
| Tier 4 ROI Router Advisory | All metrics + ongoing review cadence |

## 5. OUT OF SCOPE (explicit)

- Platform deployment on customer infra
- Guaranteed savings percentages
- Real-time production enforcement without pilot receipt
- Banking / payment processing

---

*Draft for pilot. Ratify at v0.9 Pass 4 or first customer engagement.*
