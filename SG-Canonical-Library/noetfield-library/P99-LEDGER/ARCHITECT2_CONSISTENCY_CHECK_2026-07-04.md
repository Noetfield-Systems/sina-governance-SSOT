# ARCHITECT-TWO DOCS — CONSISTENCY CHECK vs library (2026-07-04)

**Checked:** AGENT_LAYERED_LAW v1, FOUNDER_JUDGMENT_PATTERNS v1 (P0 CORE), SINA_GATEWAY v1 — locked in a parallel Architect-Two session — against this chat's library thread.
**Verdict: FULLY CONSISTENT. Same thread. These are the AUTHORITATIVE LOCKED versions of things this chat built read-surface drafts of.**

---

## 1. THE MAP (Architect-Two locked ↔ this-chat library)
| Architect-Two LOCKED doc | This-chat library equivalent | Relationship |
|---|---|---|
| **AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE** (P0, LOCKED) | `P7-DOCTRINE/layered-agents.md` (read-surface) | **A2 is authoritative.** Same law; A2 adds the formal Tier 0/1/2/3 model + least-knowledge + dispatch contract. layered-agents.md → demote to derived/read-surface pointing at the P0 primary. |
| **FOUNDER_JUDGMENT_PATTERNS v1** (P0 CORE, LOCKED) | scattered across `P7-DOCTRINE/*` | **A2 is the MIND.** Its 10 patterns INCLUDE my doctrine laws: target-vs-blocker, mechanical-not-prose, negative-proof, authority-from-registry, master-as-reconciler, one-canonical-never-two, sell/build-sequencing. The doctrine files are the *expanded* form; P0 CORE is the *judgment seed* (harvested, case-attached). Complementary, not duplicate. |
| **SINA_GATEWAY_BLUEPRINT** (product, LOCKED) | (new — no equivalent) | **New product line.** Mirror→Route→Capture→Tag. Installed P10. |

**No conflict. No competing SSOT.** A2 formalized/locked what this chat drafted. Exactly the "same thread, each layer after" pattern.

## 2. WHAT A2's DOCS ADD THAT THE LIBRARY WAS MISSING
1. **The Tier 0/1/2/3 least-knowledge model** — formal, with the dispatch contract. The library had layered-agents as *doctrine*; A2 made it *enforceable law*. → the library's layered-agents.md should point to it as primary.
2. **P0 CORE (the judgment layer / the mind)** — the single biggest addition. The library had the *thinking laws* (P7); P0 CORE is *how Sina judges when no law fits*, harvested from real cases. This is the founder-independence layer. **The library had no "mind" doc — now it does.**
3. **The harvest rule** — P0 CORE grows ONLY from real decisions, never speculative philosophy. This is itself Pattern 10 (harvest-don't-invent) and it's the anti-sprawl law for the judgment layer.
4. **The Gateway product** — a concrete, shippable Tier-1 product with a locked security rule (anon key + insert-only RLS, NEVER service-role key in frontend).

## 3. TWO A2 SECURITY/GOVERNANCE ITEMS TO CARRY FORWARD
- **SECURITY (hard rule, from the Gateway):** never put the Supabase service-role key in frontend JS = public DB breach. Use anon key + RLS insert-only, or a server function with the key in env. → add to any product-layer doc touching Supabase. (Relevant to the SUPABASE_URL blocker wiring too.)
- **⚠ GOVERNANCE DECISION TO CONFIRM (Architect-Two flagged this):** the SG audit resolved `SSOT versioning law v0.1.1 stays PROPOSED because gov-structure-authority-v1 wins on direct conflict` — the **`sg_wins`** call. This means the structure-authority doc (not the versioning law) is the version tiebreaker **permanently**. **Founder: confirm you made this call.** It's the one place SG resolved a conflict between two of your own laws. If intended → consistent, keep. If unsure → 30-second review. (This reconciles with this-chat's earlier "SG P0 authority wins; v0.1.1 read-surface/PROPOSED" — SAME decision, so it IS consistent across both sessions. ✅ likely intended.)

## 4. LIBRARY UPDATES MADE
- AGENT_LAYERED_LAW installed → `P0-FOUNDATION-SPINE/` (+ P2 cross-ref stub).
- FOUNDER_JUDGMENT_PATTERNS → `P0-FOUNDATION-SPINE/P0-CORE/` (protected: Base-Brain + high-agents only; workers NEVER load).
- SINA_GATEWAY → `P10-PRODUCT-LAYERS/`.
- `P7-DOCTRINE/layered-agents.md` should be re-tagged: DERIVED / read-surface; primary = the P0 LOCKED law. (Note for SG, not overwriting A2's authority.)

## 5. THE COMPLETE 3-PART ARCHITECTURE (now all on disk)
```
WORKERS EXECUTE   → Tier 0 + role law + mission brief + mechanical gates   (P8, P5, tiers)
SG KEEPS COHERENCE→ registry / reconciler / authority-from-registry        (SG, P2)
P0 CORE JUDGES    → the founder-judgment mind, harvested, case-attached     (P0-CORE)  ← was missing, NOW IN
```
This is the founder-independent architecture: workers already run without Sina; P0 CORE is the layer that will eventually *decide* without Sina, in his way.

## 6. HONEST NOTES (echoing A2's discipline)
- **Don't write Pattern 11 speculatively.** P0 CORE grows by harvest from the next real decision only. (Its own law.)
- **Don't let locked-law-writing become churn.** P0 is now complete at constitution level. Next locks = Tier-1 role laws (motor/site/capture) as needed, not more P0.
- **Authority = SG registry ACTIVE, not file existence.** These 3 docs say LOCKED, but they're authoritative only once SG-registered. (This is Pattern 9 / the meta-rule.)

---
*v0.1 (2026-07-04 16:13 PDT) — consistency check: A2's 3 locked docs are the authoritative versions of library drafts (layered-agents, doctrine) + the missing P0-CORE mind + a new Gateway product. Fully consistent, same thread. One founder-confirm: sg_wins version call (likely intended, matches this-chat's earlier decision).*
