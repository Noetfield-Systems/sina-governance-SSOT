# SERVICE LAYER — OPERATIONAL LANGUAGE GOVERNANCE AUDIT

**Service name:** Agentic Ops Language & Decision Cleanup Audit  
**Category:** Agentic Ops Governance / Decision-Language Hygiene / Terminology Authority  
**Status:** Service definition — proven on SG RC3 + SourceA overlay incident  
**First written:** 2026-07-07  
**Pattern:** `P9-PATTERN-FACTORY/operational-language-governance-pattern-v1.md`  
**Machine:** `P8-MACHINE-LOOPS/decision-language-cleanup-machine-v1.md`  
**Authority:** Noetfield Systems Inc. / FOUNDER_CANON v1

---

## WHAT IT IS (Buyer Promise)

**We map where your agents, forms, decisions, and docs disagree about words — then separate safe fixes from authority conflicts before anyone rewrites production.**

For teams running agentic ops (founder decision forms, hub submits, worker scripts, SSOT libraries): identify terminology drift, undefined system words, form/decision collapse, and unsafe vocabulary — deliver a machine-readable index, gated scan results, safe rewrite plan, and escalation queue. **Diagnosis first; no unsupervised bulk rewrite.**

Positioning: **Agentic Ops Language Governance** — the layer between "we have a glossary" and "our agents and forms actually use the same words." Not a CMS. Not a generic linter. A governed audit with receipts.

---

## WHAT WE DIAGNOSE

| Pain | What buyer feels | What audit finds |
|------|------------------|------------------|
| Decision form chaos | 80 rows, unclear what's decided | Pick vs gather vs fragment classification |
| Dictionary gaps | Linter flags everything | Pile split: canon / status / skip |
| False-positive gates | CI noise blocks merges | Allowlist + overlay without dumbing down canon |
| Venture overlay drift | Product invents parallel meanings | Local overlay under SG authority |
| Unsafe auto-fix | "Clean" pass creates new WARN | Safe vs risky rewrite separation |
| Agent submit risk | Machine closes human decisions | CONFLICT_PHRASE + evidence-flag gaps |

---

## DELIVERABLES

### Tier 1 — Agentic Ops Language & Decision Cleanup Audit (launch tier)

**Scope (fixed):**

1. Input corpus inventory (forms, exports, key scripts, doc tree — read-only)
2. Term extraction report (unique tokens, counts, surfaces)
3. Seven-bucket classification index (JSON + human summary)
4. Full-tree dry scan (PASS / WARN / FAIL / PASS_WITH_REWRITE)
5. Safe rewrite plan (apply-ready aliases only)
6. Escalation queue (`CONFLICT_PHRASE` + needs-canon entries only)
7. JSON receipt with SHA256 + scope exclusions

**Engagement:** 1–2 week diagnostic · 8–16 hours consulting  
**Price band:** $4K–$8K (pilot); fixed scope stated upfront per UNLOCK doctrine  
**Risk:** Low — no production writes without explicit safe-class approval  
**Maturity claim:** Proven on SG library (158 files, 0 WARN @ RC3) and SourceA overlay (127 classified terms). Client results depend on corpus quality and founder escalation throughput.

**No overclaim:** "We mapped your language debt and gave you a safe fix order" — not "we fixed every file."

### Tier 2 — Language Policy Pack

- Venture overlay template (local terms under canon authority)
- Gate config (allowlists, fragment skips, alias map)
- Implementation guide for customer's `language_gate` equivalent
- Validation checklist for new terms

**Engagement:** 2–3 weeks · $8K–$15K

### Tier 3 — Managed Language Loop (ongoing)

- Weekly gated scan on agreed tree
- Receipt + deadman staleness alert
- Quarterly canon pile review for `NEEDS_SG_ENTRY` queue
- Founder escalation SLA for conflict phrases only

**Engagement:** $1.5K–$3K/mo retainer

---

## SERVICE BOUNDARY

### In-scope

- Terminology and decision-language audit
- Classification index (machine-readable)
- Dry scan + safe rewrite plan
- Overlay design (venture-local vocabulary under canon)
- Receipts and escalation queue
- Advisory on apply-lane evidence flags

### Out-of-scope

- Redefining client's canon without named authority sources
- Reopening live production forms without client explicit request
- Bulk unsupervised rewrite of form JSON or decision rows
- Competing dictionary that overrides SG / client meaning authority
- Live agent autonomy over founder picks
- Guarantee of zero WARN without client approving canon additions

---

## NOETFIELD ROLE

- **Ownership:** Noetfield Systems Inc.
- **Delivery:** Audit report, classification index, scan receipts, escalation queue
- **Authority:** SG Pattern Factory + `operational-language-governance-pattern-v1`
- **Positioning:** "Governance auditor for agentic ops language" — SME-facing, outcome-driven

---

## SOURCEA ROLE (Delivery factory — optional)

When client uses SourceA stack:

- DLM fixtures and form export tooling (read-only ingest)
- Hub submit / apply-map scripts as corpus sources
- Future: `sa-decision-apply-v2` evidence wiring for machine-validatable row close

SourceA builds apply tooling; **SG retains meaning authority** for Noetfield canon engagements.

---

## REUSABLE CHECKLIST (client-facing)

Ship this with every Tier 1 audit:

- [ ] Input corpus collected (read-only)
- [ ] Terms extracted with counts
- [ ] Dictionary authority check complete
- [ ] Local overlay drafted (if venture vocabulary exists)
- [ ] Conflict phrases flagged
- [ ] Repo dry scan complete
- [ ] Safe rewrite plan approved by client
- [ ] Receipt JSON delivered
- [ ] Escalation queue handed to founder (conflicts only)

---

## PROOF ARTIFACTS (Noetfield internal — cite in proposals)

| Artifact | Proves |
|----------|--------|
| `LANGUAGE_LAYER_RC3_CHECKPOINT` @ `8c0293b` | Canon batch + gate baseline |
| `receipts/LANGUAGE_LAYER_RC3_FINAL_2026-07-07.json` | 158-file scan, 0 WARN |
| `receipts/receipt_sourcea_dictionary_overlay_v1.json` | 127-term overlay without SG redefinition |
| `P10-PRODUCT-LAYERS/SOURCEA_DICTIONARY_OVERLAY_v1.md` | Venture overlay pattern |
| Commits `ce3fd4a`, `bf40045` | Safe rewrite + overlay delivery |

SourceA 757-file scale scan: incident reference; formal client-facing receipt pending.

---

## GTM NOTES

- **Lead with diagnosis** — same ladder honesty as Brain Audit and Agentic Cost Governance Tier 1
- **Sell the escalation queue** — buyers pay to know what **not** to auto-fix
- **Receipts are the product proof** — SHA256 + scope exclusions beat slides
- **Cross-sell:** Brain Audit (stack chaos) → Language Audit (word chaos) → Operating Brain Install

Canonical GTM invariants: `P7-DOCTRINE/UNLOCK_DOCTRINE_v2.md` §5.1 — fixed name, fixed price, fixed scope, pay/start CTA.

---

## FOLLOW-UP GAP (internal — do not sell as done)

**`sa-decision-apply-v2` evidence flag wiring** — required before machine-validatable decision rows auto-close. Until wired, Tier 1 deliverable ends at escalation queue + manual apply instructions.

---

## CROSS-REFERENCES

- Pattern: `P9-PATTERN-FACTORY/operational-language-governance-pattern-v1.md`
- Machine: `P8-MACHINE-LOOPS/decision-language-cleanup-machine-v1.md`
- Overlay example: `SOURCEA_DICTIONARY_OVERLAY_v1.md`
- Sibling offer: `agentic-cost-governance-service.md`, `P9-PATTERN-FACTORY/brain-audit-v1.md`

---
*v1.0 (2026-07-07) — Commercial layer for Operational Language Governance Pattern v1.*
