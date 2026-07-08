# PATTERN — OPERATIONAL LANGUAGE GOVERNANCE v1

**Status:** Captured from SG language-layer RC1→RC3 + SourceA overlay incident (2026-07-07). Reusable across repos/clients.  
**First written:** 2026-07-07  
**Authority:** SG SSOT · meaning authority stays `NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md` — this pattern does **not** redefine it.

---

## What we learned

Operational language debt is not a copy-editing problem. It is a **governance failure mode** that shows up as:

| Symptom | Root cause | Fix class |
|---------|------------|-----------|
| FORM_OFFICIAL confusion | Form treated as UI, not decision corpus | Overlay + authority rules; form stays evidence-only |
| 80-row decision collapse | One surface mixing picks, gathers, fragments, status | DLM triage + classify before rewrite |
| Dictionary gaps | Undefined terms scanned as violations | Pile split: canon / allowlist / gate-skip |
| `language_gate` RC1 false positives | Everything flagged as `UNDEFINED_TERM` | RC2 triage piles; RC3 allowlists + 131-term batch |
| Unsafe auto-rewrite | `PASS_WITH_REWRITE` masked latent WARN | Separate safe (`ALIAS_RETIRED`) from risky (jargon, form JSON) |
| Venture overlay drift | Local ops terms competing with SG canon | Local overlay index — SG wins on meaning |

**Core insight:** Extract → classify → index → scan → **safe vs risky** → receipts → escalate **only** real conflicts. Never bulk-rewrite forms or competing dictionaries from an incident.

---

## Core pattern (repeatable loop)

```
messy operational language
  → extract terms / conflicts
  → classify (7 buckets)
  → build machine-readable index
  → scan repo (dry, then apply)
  → separate safe rewrites from risky rewrites
  → write receipts
  → escalate only real conflicts
```

### Seven classification buckets

| Bucket | Meaning | Action |
|--------|---------|--------|
| **Dictionary term** | SG canon meaning | Point to `dictionary_index.json`; align copy |
| **Local overlay term** | Venture/form glue only | Define in venture overlay; never mint SG |
| **Status label** | Pick tokens (DEFER, SHIP, …) | Gate allowlist only — not dictionary |
| **Form option** | UI/vendor option text | Audit only — not mintable |
| **Command fragment** | Instruction phrases | Gate skip / fragment allowlist |
| **Conflict phrase** | Known confusion | Fix guards or prose — not vocabulary |
| **Needs canon entry** | Real system word, no SG row | Queue for SG pile approval + **named source** |

---

## Reusable checklist

Use this for every new repo or client engagement.

- [ ] **Input corpus** — forms, decision exports, hub scripts, open picks, DLM fixtures, founder receipts (read-only)
- [ ] **Term extraction** — unique tokens + counts + surfaces (form row, script, doc)
- [ ] **Dictionary authority check** — match against `dictionary_index.json`; SG wins
- [ ] **Local overlay creation** — venture-local terms only (`SOURCEA_DICTIONARY_OVERLAY_v1` pattern)
- [ ] **Conflict phrase detection** — authority inversion, gather/pick confusion, agent-submit risk
- [ ] **Repo dry scan** — `language_gate` / `rc2_dry_scan_v1` — no writes
- [ ] **Safe rewrite plan** — `ALIAS_RETIRED` regex, retired entity names, known alias map
- [ ] **Receipt output** — JSON with SHA256, stats, scope exclusions, checkpoint ref
- [ ] **Escalation queue** — `NEEDS_SG_ENTRY` + `CONFLICT_PHRASE` only; defer form reopen

---

## What machine we built

| Layer | Artifact | Role |
|-------|----------|------|
| Gate | `language_gate/language_gate_core_v1.py` | Scan, pile allowlists, rewrite hints |
| Pipeline | `language_gate/language_gate_pipeline_v1.py` | Library-wide scan + sidecars |
| Index | `language_gate/dictionary_index.json` | Machine-readable canon (225 terms @ RC3) |
| DLM triage | `P99-LEDGER/DLM_DICTIONARY_GAP_TRIAGE_RC2_*.json` | 80-row form gap map |
| Overlay | `language_gate/sourcea_dictionary_overlay_index_v1.json` | 127 classified SourceA terms |
| Cold proof | `language_gate/cold_session_proof_v1.sh` | Disk-only gate — no chat context |
| Machine recipe | `P8-MACHINE-LOOPS/decision-language-cleanup-machine-v1.md` | Step-by-step repeat |

Full machine loop doc: **`P8-MACHINE-LOOPS/decision-language-cleanup-machine-v1.md`**.

---

## Evidence that proves it

| Evidence | Location | What it proves |
|----------|----------|----------------|
| `LANGUAGE_LAYER_RC3_CHECKPOINT` | git tag @ `8c0293b` | Pile-1 dictionary batch + gate RC3 baseline |
| Commit `8c0293b` | branch `cursor/language-layer-v1` | 131 dictionary entries; 225 indexed terms |
| Commit `ce3fd4a` | same branch | Cold-session proof; safe rewrites; 158-file scan 0 WARN |
| Commit `bf40045` | same branch | SourceA overlay v1 (127 entries, no SG redefinition) |
| RC3 final receipt | `receipts/LANGUAGE_LAYER_RC3_FINAL_2026-07-07.json` | Library scan PASS; rewrite pass accounting |
| Overlay receipt | `receipts/receipt_sourcea_dictionary_overlay_v1.json` | Overlay SHA256 + class stats |
| SourceA 757-file cleanup scan | **incident scope** (formal receipt pending) | Scale dry-scan on venture repo — classify before apply |

**RC3 numbers (SG library):** 158 files scanned · 0 WARN · 0 FAIL · 15 PASS_WITH_REWRITE (sidecar-only).

---

## How to repeat it (new repo / client)

1. **Do not reopen live forms** — export fixtures + receipts as read-only corpus.
2. Run DLM or equivalent term extraction on decision surfaces.
3. Triage into seven buckets; never define form options as dictionary entries.
4. Build or extend `dictionary_index.json` only via SG pile approval (named sources).
5. Create venture overlay if local ops vocabulary exists (overlay ≠ competing dictionary).
6. Dry-scan entire target tree; review `PASS_WITH_REWRITE` for latent `UNDEFINED_TERM`.
7. Apply **safe** rewrites only; risky rows stay sidecar / founder queue.
8. Emit receipt JSON with SHA256 + scope exclusions.
9. Escalate `CONFLICT_PHRASE` and `NEEDS_SG_ENTRY` — nothing else.

**Forbidden on repeat:** reopening FORM_OFFICIAL from SG; asking venture to rebuild SG dictionary; unsupervised jargon rewrites on history files.

---

## How to sell it

Commercial surface: **`P10-PRODUCT-LAYERS/operational-language-governance-audit.md`**

**Offer name:** Agentic Ops Language & Decision Cleanup Audit

Positioning: Tier-1 diagnosis — map decision-language drift, term conflicts, and unsafe automation vocabulary **before** implementation. Same lane as Brain Audit: expert diagnosis + machine receipts, not platform deployment.

Ladder: Language Audit → Policy Pack (overlay + gate config) → Managed Language Loop (continuous scan + deadman).

---

## What still needs follow-up

| Gap | Owner | Blocker |
|-----|-------|---------|
| **`sa-decision-apply-v2` evidence flag wiring** | SG + SourceA apply lane | Machine-validatable decision rows cannot auto-close until evidence flags wire through apply |
| SourceA 757-file cleanup receipt | SG receipts | Formal JSON receipt for scale scan not yet filed |
| `violations_example.md` | SG library | Still FAIL by design — example corpus, not production gate |
| Overlay rebuild script | `build_sourcea_overlay_index_v1.py` | Documented as future; manual regen from DLM + scripts today |
| `NEEDS_SG_ENTRY` queue (23 rows) | Founder pile approval | Named locked file required per SG rule |

---

## Incident scope exclusions (locked)

- Do **not** reopen SourceA FORM_OFFICIAL from this pattern.
- Do **not** ask SourceA to rebuild SG Dictionary.
- Do **not** redefine SG Dictionary meanings in overlay or pattern docs.

---

## Cross-references

- Overlay: `P10-PRODUCT-LAYERS/SOURCEA_DICTIONARY_OVERLAY_v1.md`
- Form terminology audit: `P99-LEDGER/SOURCEA_FORM_TERMINOLOGY_AUDIT_v1.md`
- Machine loop: `P8-MACHINE-LOOPS/decision-language-cleanup-machine-v1.md`
- Product / GTM: `P10-PRODUCT-LAYERS/operational-language-governance-audit.md`
- Doctrine: `P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md`

---
*v1.0 (2026-07-07) — Pattern Factory capture from language-layer RC3 + SourceA overlay incident. Reusable; SG canon authority preserved.*
