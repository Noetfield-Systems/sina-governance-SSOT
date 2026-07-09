# SINA GATEWAY — Locked Blueprint v1

**What it is:** Sina's public opportunity gateway — a smart agentic front door that mirrors the visitor, routes them to the right venture, and captures every person/opportunity as a structured row in a database. Not a personal-branding site, not a static page, not an overbuilt CRM.

**One-line:** *Mirror → Route → Capture → Tag.* Every visitor becomes structured, queryable intelligence.

**Status:** **BUILT & LIVE** (2026-07-06). **Personal founder project** — not Noetfield Systems Inc. Repo authority: `~/Desktop/SINA GATEWAY` (`kazemnezhadsina144-dot/sina-gateway`). Production: `https://sina-gateway-production.up.railway.app`. SG mirror is read-surface only; on conflict repo wins.

---

## 1. The three layers

1. **The Mirror (front door)** — agentic wizard, not static. Visitor enters → answers a short structured wizard → the page reshapes to reflect *them* and routes them to the right venture. Each segment receives value (not just a form), so capture feels like being understood, not harvested. *(Same law as SourceA: give value first, capture as byproduct.)*
2. **The Brain (database)** — every interaction writes one structured row to Supabase. This is the core value, live from v1 — not deferred.
3. **The Strategy (output)** — the accumulated DB feeds Sina's next business moves. Read raw from the Supabase table view in v1; sorting/scoring engine + dashboard come later, tuned on real data.

---

## 2. The intake wizard (the spine)

Five layers, captured in order. This structure is what makes the DB intelligent vs a flat contact list.

| Layer | Question | Options |
| :-- | :-- | :-- |
| **Identity** | Who are you? | friend · client · investor · builder/collaborator · construction |
| **Intent** | What do you want? | hire · invest · partner · refer · learn |
| **Value** | What could we create? | deal · project · lead · capital · talent |
| **Urgency** | Timeline? | now · soon · exploring |
| **Contact** | How should Sina follow up? | name + email/phone/social |

The mirror reshapes based on **Identity** (a founder sees the founder path; a construction lead sees BuildMatch; a friend sees the human). Intent/Value/Urgency/Contact enrich the row.

---

## 3. Venture routing

Each visitor is routed to the right destination based on Identity + Intent:

- **SourceA** — governed AI execution / agent runs
- **Noetfield** — parent company / big picture
- **TrustField** — trust/compliance lane (independence in progress)
- **BuildMatch** — construction & home-services marketplace (Vancouver; not built yet → "coming / join early" capture)
- **Forge** — agent/factory tooling
- **Personal** — friend / network / human

`venture_route` is stored on every row.

---

## 4. Rule-based tagging (v1 — deterministic, NOT learned scoring)

Light tags derived directly from explicit answers. These are rules reading what the visitor stated, not predictions.

Fields written per row:
- `lead_type` — from Identity (client / investor / collaborator / construction / friend)
- `venture_route` — which venture they were sent to
- `urgency` — now / soon / exploring
- `priority_tag` — derived rule:
  - **high** = urgency `now` OR intent in {invest, hire, partner} OR value in {deal, capital, lead} AND contact provided
  - **medium** = soon, or interested but no contact
  - **low** = browsing / friend-only / no intent

*Advanced/learned scoring is deferred — tune it on real rows, never guess thresholds before data exists.*

---

## 5. Database schema (Supabase, v1)

Table `gateway_leads`:

| Column | Type | Notes |
| :-- | :-- | :-- |
| id | uuid (pk, default) | |
| created_at | timestamptz (default now) | |
| identity | text | friend/client/investor/builder/construction |
| intent | text | hire/invest/partner/refer/learn |
| value | text | deal/project/lead/capital/talent |
| urgency | text | now/soon/exploring |
| name | text | |
| contact | text | email/phone/social |
| venture_route | text | which venture |
| lead_type | text | tag |
| priority_tag | text | high/medium/low |
| source | text | online/real/referral/etc (optional) |
| raw_notes | text | optional free text |

Read raw from Supabase table view in v1. No custom dashboard.

---

## 6. SECURITY — hard rule, non-negotiable

- **NEVER put the Supabase service-role key in the frontend.** A public site with a service key = anyone can read/write/wipe the whole DB.
- Use **one of**:
  - **(a)** Supabase `anon` key + **Row-Level-Security insert-only policy** on `gateway_leads` (public can insert, cannot read/update/delete), or
  - **(b)** a **server function / API route** that holds the key in **env vars** and writes server-side.
- Either is fine; (a) is simplest for a static front-end. The frontend must never hold a key that can read or delete rows.

---

## 7. v1 SCOPE (build tonight) vs DEFERRED

**BUILD TONIGHT (v1):**
1. Agentic gateway page — mirror wizard, reshapes per visitor
2. Identity → Intent → Value → Urgency → Contact wizard
3. Supabase capture (secure: anon+RLS insert-only, or server function)
4. Rule-based tags (`lead_type`, `venture_route`, `urgency`, `priority_tag`)
5. Venture routing (SourceA / Noetfield / TrustField / BuildMatch / Forge / Personal)
6. Read leads raw from Supabase table view

**DEFERRED (next, after rows exist):**
- Learned/weighted scoring engine
- Custom admin dashboard
- Sorting/segmentation UI
- Cross-venture matching logic
- Analytics on conversion by segment

**Why deferred:** the intelligence layer must be tuned on real data, not guessed before any leads exist. Capture rich data now; build the brain that sorts it once there's something to sort.

---

## 8. Design principles

- **Mirror first, capture second** — give each segment value; profiling feels like understanding, not harvesting.
- **Feels like a smart platform**, not a webpage — agentic, responsive, reshaping.
- **One build, auto-collecting** — once live, the DB fills with no further work.
- **Honest** — BuildMatch isn't built; present it as "join early / coming," not as live.
- **Secure by default** — no key in frontend that can read/delete.

---

## 9. Build-tonight decisions (confirm before build)

1. **Intake structure** — Identity/Intent/Value/Urgency/Contact as above. ✅ (confirm or adjust)
2. **Ventures** — SourceA, Noetfield, TrustField, BuildMatch, Forge, Personal. ✅ (confirm or adjust)
3. **Supabase** — keys ready tonight (live capture) OR build capture-ready to wire after? Security path: anon+RLS insert-only (recommended for static front-end) or server function.

---

*Gateway Blueprint · LOCKED v1 · mirror → route → capture → tag · Supabase capture from v1 · scoring/dashboard deferred to data-informed next phase.*
