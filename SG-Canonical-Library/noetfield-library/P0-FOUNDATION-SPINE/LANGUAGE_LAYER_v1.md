# LANGUAGE LAYER — how words work in Noetfield

**Status:** v1 foundational · **Tier:** P0 (routes all other text)  
**Updated:** 2026-07-06

---

## Two authorities (not one file wearing two hats)

### TERMINOLOGY — **wording authority**

- Daily · mandatory · machine-enforceable  
- **One line per term** · loaded on **every output**  
- Answers: **“What word do I write, right now?”**  
- Enforced by lint: **synonym rewrite + banned register**

**File:** `P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md`

### DICTIONARY — **meaning authority**

- Foundational · broader · **escalation-only** (not loaded on every worker tick)  
- **Long entry:** plain meaning · why it exists · wrong readings · example · **conflict rule** · **public rewrite**  
- Answers: **“What does this really mean, and is it allowed to exist?”**  
- **Source that terminology entries are minted FROM** — never the reverse

**File:** `P7-DOCTRINE/NOETFIELD_DICTIONARY_v1.md`

---

## The minting rule (hard gate)

**No new job, task, specialist, role, product page, contract clause, or receipt field enters the system without:**

1. An **existing dictionary entry**, or  
2. A **new dictionary entry authored and versioned first** (founder lock → bump dictionary version)

**Then** — and only then — mint the one-line terminology row from that dictionary entry.

```
Dictionary (meaning)  →  Terminology (wording)  →  artifact / page / schema field
         ↑                        ✗ never reverse
   authored first
```

Terminology is **compressed from** dictionary. Doctrine explains *why we operate*; it does not mint words. P6 `locked-definitions-v1` holds **brain public claims** only — not system vocabulary.

---

## Authority stack (on conflict)

```
1. NOETFIELD_DICTIONARY_v1      ← meaning wins; tombstone old readings here
2. NOETFIELD_TERMINOLOGY_v1     ← wording must match dictionary; update same change set if drift
3. P7 DOCTRINE                  ← operating law, not ad-hoc definitions
4. P6 locked-definitions-v1     ← SourceA public claims / forbidden_public
5. P2 SSOT / P0 constitution    ← structure (R-split, versioning, invariants)
```

---

## Load order for agents

```
Tier 0:  AGENT_LAYERED_LAW (universal laws)
         + NOETFIELD_TERMINOLOGY_v1 (every output — wording authority)
Tier 1:  Role law only
Tier 2:  Mission brief only
Authoring / dispute:  NOETFIELD_DICTIONARY_v1 (meaning authority — dispatch may set load_dictionary: true)
```

Workers **do not** load the full dictionary unless authoring a new term, role, page, clause, or field — or resolving a meaning dispute.

---

## Lint enforcement (terminology only)

Machine checks (present or planned):

- **Synonym rewrite** — terminology §6 map (e.g. `model-agnostic` → `vendor-neutral`)  
- **Banned register** — terminology §7 (hype, needy tone, public `%`, unprovable roster)  
- **Mint gate** — new schema field / task cell name must reference dictionary entry id or block merge

Dictionary is **not** linted line-by-line; it is **locked by version** and founder sign-off.

---

## Change control

| Action | Order |
|--------|--------|
| New word | Dictionary entry (long) → founder lock → bump dictionary version → mint terminology line → SSOT_INDEX |
| Change meaning | Edit dictionary · tombstone old reading · update terminology same PR · never silent |
| Public page | Dictionary public-rewrite section + terminology tone §7 before publish |

**Audit ledger:** `P99-LEDGER/TERMINOLOGY_DICTIONARY_FULL_AUDIT_2026-07-06.md`
