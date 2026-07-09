# TEAM BENCH FORMATION PACKAGE — v1

**Status:** DRAFT-ACTIVE (founder sign-off required before any offer or external send)
**Lane:** TEAM_BENCH_FORMATION (top ROI lane per founder directive 2026-07-08)
**Objective:** Build the minimum credible team layer before offer/outreach.
**Rule:** Bench = revenue-share operators, not employees. No salaries pre-revenue. Founder keeps control.

---

## 1. Five required roles

| # | Role | Mission | Weekend-minimum bar |
|---|---|---|---|
| R1 | **Delivery Lead — AI Governance Consultant** | Runs diagnostic sprints and client delivery so engagements don't depend on the founder | 1 named person who can co-run a paid diagnostic within 2 weeks |
| R2 | **Platform Engineer — Cloud/Integrations** | Owns NOOS cloud runtime, integrations, and the receipt/evidence pipeline | 1 person who can ship a cloud loop end-to-end unsupervised |
| R3 | **Compliance Advisor — CASL / PIPEDA / AI risk (fractional)** | Signs off outreach templates and governance claims; is the credibility anchor for regulated buyers | 1 advisor willing to be named on the site + review 2 documents/month |
| R4 | **GTM / Partnerships Lead** | Drives TrustField partner funnel and offer pipeline; owns CASL-safe outreach execution | 1 operator with an existing Canadian B2B network who works on commission |
| R5 | **Brand & Content Operator (fractional)** | Website-first assets: proof pages, offer pages, public onboarding — no deck work | 1 person who ships site-ready HTML/copy, not mockups |

Minimum credible bench = R1 + R3 + R4 named and agreed. R2/R5 can lag two weeks.

## 2. Candidate criteria

**Global bar (all roles):**
- Senior operator: ships alone, no management overhead needed
- Evidence-first: has public receipts (portfolio, repos, cases, named clients)
- Accepts revenue-share / commission engagement (no salary expectation pre-revenue)
- Async-first, comfortable with agent-assisted workflows and receipt discipline
- Canada-market aware (CASL/PIPEDA context) or fast to certify — mandatory for R3/R4
- No control demands: no equity ask at bench stage, no veto rights

**Instant disqualifiers:** needs daily sync meetings · "strategy only" profiles · won't be named publicly · asks for retainer before first revenue event.

## 3. Compensation / revenue-share structure (DRAFT — founder sign-off before offer)

| Role | Structure | Cap/Notes |
|---|---|---|
| R1 Delivery Lead | 30% of gross on engagements they deliver; 10% on repeat business they retain | Per-engagement, no base |
| R2 Platform Engineer | 15% of platform/product revenue for systems they built, 12-month trail | Or per-milestone fixed fee once revenue exists |
| R3 Compliance Advisor | 3% of revenue on engagements they certified, or flat per-review fee | Named-advisor credit on site |
| R4 GTM Lead | 12% commission on closed revenue they sourced, 12-month trail | Uncapped; nothing on founder-sourced deals |
| R5 Brand/Content | Per-asset fixed fee, paid from first revenue; 2% trail on offer pages that convert | Small, output-priced |

**Mechanics:** 90-day tryout via one real deliverable · bench points vest per receipt, not per time · all payouts triggered by collected revenue only (no payout on booked-not-paid) · founder authority over pricing, offers, and external sends is non-negotiable.

## 4. Candidate tracker format

Live tracker: `data/team_bench_tracker_v1.json` (seeded, schema below).

| Field | Values |
|---|---|
| candidate_id | CAND-#### |
| role | R1–R5 |
| name / handle / link | — |
| source | one of the 10 sources below |
| status | SOURCED → CONTACTED → REPLIED → TRIAL → BENCHED / PASSED |
| casl_basis | how contact is lawful (existing relationship, published B2B contact, referral consent) |
| evidence | links proving the global bar |
| next_action + date | always populated — no stale rows |

## 5. Short invitation message (CASL-aware, founder sends or approves)

> Subject: Revenue-share bench — governed AI delivery (Canada)
>
> Hi {name} — I'm Sina, founder of Noetfield Systems (Vancouver; noetfield.com). I'm forming a small revenue-share bench for governed-AI consulting delivery in Canada: no salaries, no meetings theater — senior operators who ship, paid a defined % of collected revenue on work they touch. Your {specific_receipt} is why I'm writing. If a {role} seat interests you, reply and I'll send the one-page structure. Not interested? One reply and I won't contact you again.
>
> — Sina Kazemnezhad · Noetfield Systems Inc., Vancouver BC

## 6. Internal onboarding page draft (publish only after deploy fence is confirmed)

**Route (later):** noetfield.com/team/onboarding/ — held here until the review fence exists.

> ### Welcome to the Noetfield bench
> **What this is.** Noetfield Systems runs governed AI delivery for Canadian teams: consulting (Intelligence) and an AI Value Governance OS. You're joining a revenue-share bench, not a payroll.
> **How work happens.** Cloud-first. Work arrives as packets (mission, deliverable, acceptance, evidence required). You ship; every meaningful result leaves a receipt. No receipt, no result.
> **What you never do.** Send external messages, publish pages, commit prices, or speak for the company without founder sign-off. Public site changes go through review — always.
> **Getting paid.** Percentages are in your bench agreement; payouts trigger on collected revenue, automatically tracked against receipts.
> **Week one.** 1) Sign bench terms. 2) Get your first packet. 3) Deliver against acceptance criteria. 4) Receipt lands, you're live on the bench page.

## 7. First 10 candidate sources

1. LinkedIn advanced search — "AI governance consultant" + Canada, 2nd-degree first (warm intro path)
2. Founder's existing network export (past colleagues/clients) — highest CASL safety: existing relationships
3. IAPP (privacy professionals association) member directory & local KnowledgeNet chapters — R3
4. Responsible AI Institute / CIFAR AI-safety community — R1/R3
5. MLOps Community Slack (#jobs, #consulting) — R2
6. GitHub contributors to policy-as-code / compliance tooling repos (OPA, evidence pipelines) — R2
7. Vancouver tech meetups: VanAI, Cloud Native YVR — R1/R2, in-person credibility
8. Contra / Toptal senior fractional profiles filtered to revenue-share tolerance — R5/R2
9. Ex-Big-4 AI-risk consultants recently gone independent (LinkedIn "open to work" + independent) — R1/R3
10. UBC/SFU industry-liaison + alumni consulting groups — R5 and pipeline depth

## 8. Receipt

Formation receipt with file hashes: written by the recording script to `receipts/p0pgr/` (see `team-bench-formation-*.json`). This package is inert until the founder receipt marks it ACTIVE.
