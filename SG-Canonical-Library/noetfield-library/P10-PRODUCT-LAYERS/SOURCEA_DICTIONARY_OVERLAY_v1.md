# SOURCEA_DICTIONARY_OVERLAY_v1

**Status:** SG-side overlay · **not** a competing dictionary  
**Meaning authority:** `NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md` + `language_gate/dictionary_index.json`  
**Machine index:** `language_gate/sourcea_dictionary_overlay_index_v1.json`  
**First written:** 2026-07-07

---

## Purpose

SourceA forms, Hub, Brain, Worker, apply-map, and submit language are part of the terminology/conflict system. The form is not UI chrome alone — it is a **high-signal corpus** for:

- unclear meaning  
- duplicate decisions  
- authority confusion (gather vs pick vs recommended)  
- machine-submit risk (INCIDENT-037)

This overlay lets SourceA cleanup use **clean local operational names** without corrupting SG canon.

---

## Authority rules

1. **SG Dictionary wins on meaning.** Overlay rows of class `SG_DICTIONARY_TERM` only **point** to SG — they do not redefine.
2. **Define only `SOURCEA_LOCAL_TERM` here** — form/hub/submit glue that has no SG row (e.g. `partial_batch`, `disk_fast_apply`, `nerve_map`).
3. **Never define** `COMMAND_FRAGMENT`, `FORM_OPTION`, or `STATUS_LABEL` as dictionary entries.
4. **`NEEDS_SG_ENTRY`** rows are a queue for SG pile approval with a **named source file** — not defined in this overlay.
5. **`CONFLICT_PHRASE`** rows are audit/guard targets — fix copy or code, not vocabulary.

---

## SourceA-local terms (defined here)

| Term | Meaning |
|------|---------|
| **FORM_OFFICIAL** | Live founder decision form (third_form). DLM is the machine; form is evidence + submit surface. |
| **ASF** | Answer Submission Format — founder reply template (`ASF: FIVE-STEP — PICK: …`). Not agent submit. |
| **Hub Submit** | `hub_form_submit_v1` founder explicit picks → canvas → §ANSWERED. INCIDENT-037 gated. |
| **partial_batch** | Submit picked rows only when form incomplete; `partial_batch=true` required. |
| **disk_fast_apply** | Fast path: apply picks to disk without full hub rebuild; wire in background. |
| **form_official_line** | Telemetry string `FORM_OFFICIAL · N open` from live form mirror. |
| **gathering_phase** | Pre-lock gather tier — disk rows are proposals, not picks. |
| **nerve_map** | `form_official_nerve_map_v1.json` — row ID → machines, blocks, plans. |
| **apply_map** | DLM output from **validated** picks only — never from open form alone. |
| **INCIDENT-037** | Founder submit only; `agent_live_submit` must stay false in receipts. |
| **FOUNDER PICK supremacy** | `FOUNDER PICK > AGENT RECOMMENDATION > DISK GATHER ROW`. |
| **canvas_form_apply** | Post-submit apply to §ANSWERED + machine dispatch. |
| **Worker Hub** / **Machine Hub** | Hub caches invalidated on founder submit. |
| **DRIFT_FLOOR** | Form extraction drift floor (90). |
| **hub-form-submit-receipt** | Schema at `~/.sina/hub-form-submit-receipt-v1.json`. |
| **form-official-question-schema-v1** | JSON schema for form `option_slots`. |
| **CF URL** | Code alias for Cloudflare URL option field — not public vocabulary. |

---

## Class reference

| Class | Treatment |
|-------|-----------|
| `SG_DICTIONARY_TERM` | Cite SG index term; SourceA copy must align |
| `SOURCEA_LOCAL_TERM` | Defined in this overlay only |
| `STATUS_LABEL` | Gate allowlist / form pick tokens (DEFER, SHIP, …) |
| `FORM_OPTION` | UI/vendor option text — not mintable |
| `COMMAND_FRAGMENT` | Instruction phrases (Instrument TF, Keep Witness AI, …) |
| `CONFLICT_PHRASE` | Known confusion — fix guards or prose |
| `NEEDS_SG_ENTRY` | Queue for SG dictionary — needs named locked file |

---

## Inputs (read-only to build v1)

- `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`  
- `decision_language_machine_v1/test_fixtures/form_official_80_open_v1.json`  
- `P99-LEDGER/DLM_DICTIONARY_GAP_TRIAGE_RC2_2026-07-07.json`  
- `SourceA/scripts/hub_form_submit_v1.py`  
- `SourceA/scripts/live_founder_decision_form_v1.py`  
- `P99-LEDGER/SOURCEA_FORM_OFFICIAL_*` receipts and submit maps  

---

## Cleanup usage

1. Load `sourcea_dictionary_overlay_index_v1.json` in SourceA form/hub lint.  
2. For each flagged token: resolve class → apply rule above.  
3. Never write `NEEDS_SG_ENTRY` meanings into SourceA product docs without SG approval.  
4. Run SG `language_gate` on exported form markdown in P99 only — do not reopen live form for dictionary work.

---

*v1 (2026-07-07) — initial overlay after LANGUAGE_LAYER_RC3_CHECKPOINT.*
