# LANGUAGE LAYER — how words work in Noetfield

**Status:** v1 foundational · **Tier:** P0 (routes all other text)  
**Updated:** 2026-07-06

---

## Why three layers exist

Agents confuse **logs with receipts**, **always-on with governed loops**, and **governed as decoration**. Customers hear **arrogance** where we mean **selective**. The fix is not “write better prompts once” — it is a **language SSOT** that every artifact, job spec, specialist brief, and public page must obey.

---

## The stack (authority on conflict)

```
1. NOETFIELD_TERMINOLOGY_v1     ← short, mandatory, machine-enforceable (every agent, every day)
2. NOETFIELD_DICTIONARY_v1       ← long plain-English + reasoning (escalation, disputes, new roles)
3. P7 DOCTRINE files             ← why we operate this way (not word definitions)
4. P6 locked-definitions-v1      ← brain public meaning only (claims, terms, forbidden_public)
5. P2 SSOT / P0 constitution     ← structural rules (R-split, versioning, invariants)
```

**Rule:** Terminology wins over synonym habit. Dictionary wins over terminology when they disagree — then terminology must be updated in the same change set. Doctrine explains; it does not redefine words casually.

---

## Terminology vs dictionary

| | **Terminology** | **Dictionary** |
|---|-----------------|----------------|
| **Purpose** | Same word → same meaning everywhere, fast | Understand deeply when stakes are high |
| **Length** | One line + IS NOT + example | Paragraphs: meaning, reasoning, edge cases, links |
| **Who loads** | **Every agent** (Tier 0) | Architect, founder, dispute resolution, new job/specialist authoring |
| **Enforcement** | Lint, census, deploy gates, banned-register | Human judgment + founder lock |
| **Add a word** | Founder locks → bump terminology version | Long entry first → compress into terminology if daily-use |

---

## Load order for agents

```
Tier 0:  AGENT_LAYERED_LAW (6 universal laws)
         + NOETFIELD_TERMINOLOGY_v1 (mandatory before any output)
Tier 1:  Role law only
Tier 2:  Mission brief only
Escalation: NOETFIELD_DICTIONARY_v1 when meaning is disputed or a new specialist role is defined
```

Workers **never** load the full dictionary unless the dispatch explicitly says `load_dictionary: true`.

---

## Artifact types (receipt family)

| Type | When to use | Counts as “receipt” in terminology? |
|------|-------------|-------------------------------------|
| **Proof receipt** | Fielded machine record with schema, op_key, sink ack | Yes |
| **Observation record** | SG guard pass, health pass, census run — honest snapshot | Only if labeled; default call it **observation record** |
| **Claim** | Agent or log says PASS/done without fielded proof | Never |

---

## Change control

- New daily word → dictionary entry (long) → terminology line → SSOT_INDEX row.
- Tombstone old meaning in dictionary; never silently rewrite terminology.
- Public website copy: terminology §7 tone + dictionary commercial entries before publish.

**Files:** `P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` · `P7-DOCTRINE/NOETFIELD_DICTIONARY_v1.md`  
**Audit ledger:** `P99-LEDGER/TERMINOLOGY_DICTIONARY_FULL_AUDIT_2026-07-06.md`
