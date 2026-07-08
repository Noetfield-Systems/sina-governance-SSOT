# MACHINE LOOP — DECISION-LANGUAGE CLEANUP v1

**Pattern:** `P9-PATTERN-FACTORY/operational-language-governance-pattern-v1.md`  
**Product:** `P10-PRODUCT-LAYERS/operational-language-governance-audit.md`  
**First written:** 2026-07-07  
**Trigger host:** `founder-manual` (initial) · `cloud` mirror optional via GHA weekly scan  
**Receipt lane:** `receipts/` + P99 ledger rows

---

## Purpose

Machine-repeatable loop that turns messy operational language (forms, decisions, scripts, docs) into a classified index, a gated repo scan, safe rewrite application, and JSON receipts — without reopening live forms or redefining SG canon.

---

## Closed loop

```
Observe (corpus + scan)
  → Detect (UNDEFINED_TERM, CONFLICT_PHRASE, pile misclass)
  → Critique (safe vs risky rewrite split)
  → Repair (safe aliases only; overlay rows)
  → Re-deploy (re-scan library)
  → Observe (receipt + checkpoint tag)
```

| Phase | Script / artifact | Output |
|-------|-------------------|--------|
| Observe | Form export, DLM fixtures, hub scripts (read-only) | Input corpus manifest |
| Detect | `language_gate_core_v1.py`, `rc2_dry_scan_v1.py` | Scan JSON + sidecars |
| Critique | Human or agent review of `PASS_WITH_REWRITE` | Safe / risky table |
| Repair | `language_gate_agent_rewrite_v1.py` (safe class only) | Disk edits (scoped) |
| Re-deploy | `language_gate_pipeline_v1.py` | 0 WARN target on canon tree |
| Observe | Receipt JSON + optional git tag | `LANGUAGE_LAYER_RC*_CHECKPOINT` |

---

## Registry row (when cloud-mirrored)

| Field | Value |
|-------|-------|
| `loop_id` | `sg-decision-language-cleanup-v1` |
| Cadence | Weekly (library) + on-demand (client audit) |
| `last_fired_at` | Upsert on successful scan receipt |
| Deadman | `noos-deadman-v1` or GHA failure alert |
| Receipt | `receipts/language-layer-rc*-*.json` |

---

## Step-by-step recipe

### 1. Input corpus (read-only)

Collect without mutating live surfaces:

- Decision form exports (`FORM_OFFICIAL_*` fixtures in P99)
- DLM test corpus (`decision_language_machine_v1/test_fixtures/`)
- Venture scripts (hub submit, live form — **read-only** from venture repo)
- Existing receipts (`hub-form-submit-receipt`, partial submit maps)
- Target repo tree for scan (SG library and/or client repo)

**Gate:** If corpus requires reopening a live form → stop; use export/fixture only.

### 2. Term extraction

- Run DLM gap triage or equivalent token counter on corpus.
- Output: term, count, surfaces, suggested action.
- Reference: `P99-LEDGER/DLM_DICTIONARY_GAP_TRIAGE_RC2_2026-07-07.json` (80-row incident).

### 3. Dictionary authority check

```bash
python3 language_gate/build_dictionary_index.py
```

- Match extracted terms against `language_gate/dictionary_index.json`.
- SG meaning authority: `NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md`.
- Unmatched system words → `NEEDS_SG_ENTRY` queue (named source required).

### 4. Pile split (gate noise reduction)

| Pile | Content | Gate treatment |
|------|---------|----------------|
| Pile 1 | Real system words | Dictionary batch approval |
| Pile 2 | Status labels | `language_gate_rc3_pile_v1` allowlist |
| Pile 3 | Fragments / tech noise | Gate skip |

RC3 result: 131 dictionary entries · 102 status labels · 120 fragments.

### 5. Local overlay creation (venture-specific)

When target is a venture repo (e.g. SourceA):

- Write overlay MD + JSON index (`sourcea_dictionary_overlay_index_v1.json`).
- Classes: `SG_DICTIONARY_TERM`, `SOURCEA_LOCAL_TERM`, `STATUS_LABEL`, `FORM_OPTION`, `COMMAND_FRAGMENT`, `CONFLICT_PHRASE`, `NEEDS_SG_ENTRY`.
- **Rule:** SG wins on meaning; overlay defines local glue only.

Rebuild (today): regenerate from DLM triage + script reads. Future: `build_sourcea_overlay_index_v1.py`.

### 6. Conflict phrase detection

Flag rows where:

- Gather tier treated as founder pick
- Agent recommendation overrides `FOUNDER PICK` supremacy
- `agent_live_submit` risk (INCIDENT-037 class)
- Retired entity aliases in user-facing copy

Output: `CONFLICT_PHRASE` rows → escalation queue, not auto-rewrite.

### 7. Repo dry scan

```bash
python3 language_gate/language_gate_pipeline_v1.py
# or scoped:
python3 language_gate/rc2_dry_scan_v1.py <target_root>
```

- No disk writes from scan.
- Review: PASS / WARN / FAIL / PASS_WITH_REWRITE per file.
- **Critical:** `PASS_WITH_REWRITE` may mask latent `UNDEFINED_TERM` — never apply jargon rewrites blindly.

### 8. Safe rewrite plan

**Safe (apply to disk):**

- `ALIAS_RETIRED` — Motor→Scheduler, TrustField entity cleanup, least-knowledge→Need-to-know
- Known regex map in `language_gate_agent_rewrite_v1.py`

**Risky (sidecar / founder only):**

- Form JSON / option_slots
- Audit docs quoting retired terms for evidence
- Agent jargon (`leverage→use`) on files with latent undefined terms
- Long-sentence `AGENT_REVIEW` hints

RC3 safe pass: 14 files applied; 5 form/audit files sidecar-only.

### 9. Cold-session proof

```bash
bash language_gate/cold_session_proof_v1.sh
```

Proves gate reads dictionary from disk with no prior chat context (`machine_reads_disk: true`).

### 10. Receipt output

Emit JSON with:

- `schema`, `verdict`, `checkpoint` / `commit`
- SHA256 of dictionary batch, overlay, index
- Scan stats (files, PASS, WARN, FAIL, PASS_WITH_REWRITE)
- `scope_excluded` array (form reopen, venture repo edits, SG redefinition)

Templates: `receipts/LANGUAGE_LAYER_RC3_FINAL_2026-07-07.json`, `receipts/receipt_sourcea_dictionary_overlay_v1.json`.

### 11. Escalation queue

Only these rows leave the machine loop for founder:

- `CONFLICT_PHRASE` (9 in SourceA overlay v1)
- `NEEDS_SG_ENTRY` (23 in SourceA overlay v1)
- Rows blocked on `sa-decision-apply-v2` evidence flags

Everything else: allowlist, overlay local term, or safe alias.

---

## Evidence commits (incident proof)

| Commit | Content |
|--------|---------|
| `8c0293b` | RC3 checkpoint — pile-1 batch, gate allowlists |
| `ce3fd4a` | Cold proof + safe rewrites + final library scan |
| `bf40045` | SourceA dictionary overlay v1 |

Tag: `LANGUAGE_LAYER_RC3_CHECKPOINT` @ `8c0293b`.

---

## Known blocker — apply lane

**`sa-decision-apply-v2`** must wire evidence flags before machine-validatable decision rows can close automatically.

Until wired:

- `decision_apply_v1` handles SG machine-closable rows manually (see `SOURCEA_FORM_OFFICIAL_PARTIAL_SUBMIT_RECEIPT_2026-07-07.json`)
- 757-file venture cleanup scan remains classify-first; bulk apply blocked

---

## Scale scan note (SourceA 757-file)

Incident included a full-tree dry scan scope (~757 files) on SourceA. Pattern: run gate pipeline in dry mode → classify all hits → **no** bulk rewrite until overlay + safe plan approved. Formal receipt for this scale pass is follow-up work.

---

## Forbidden

- Reopen live FORM_OFFICIAL from SG
- Write new SG dictionary entries without named locked source
- Auto-apply rewrites to form JSON or gather-phase rows
- Claim PASS while `violations_example.md` FAIL (example corpus — separate)

---
*v1.0 (2026-07-07) — Machine recipe for Operational Language Governance Pattern v1.*
