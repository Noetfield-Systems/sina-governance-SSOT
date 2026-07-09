# SOURCEA_FORM_TERMINOLOGY_AUDIT_v1

**Schema:** `sourcea-form-terminology-audit-v1`  
**At:** 2026-07-07  
**Corpus:** FORM_OFFICIAL 80-open export + DLM RC2 triage + SourceA submit scripts (read-only)  
**Overlay:** `SOURCEA_DICTIONARY_OVERLAY_v1.md` · index `language_gate/sourcea_dictionary_overlay_index_v1.json`

---

## Executive summary

| Class | Count | Action |
|-------|------:|--------|
| SG_DICTIONARY_TERM | 21 | Point to SG index — do not redefine in SourceA |
| SOURCEA_LOCAL_TERM | 19 | Keep in SourceA overlay only |
| STATUS_LABEL | 16 | Allowlist in gate — not dictionary |
| FORM_OPTION | 26 | Form UI/vendor noise — not dictionary |
| COMMAND_FRAGMENT | 17 | Gate skip — not dictionary |
| CONFLICT_PHRASE | 9 | Fix guards/copy |
| NEEDS_SG_ENTRY | 23 | SG pile queue — named source required |
| **Total indexed** | **127** | |

**SG dictionary indexed:** 225 terms (RC3 checkpoint)  
**DLM dictionary_fix_needed on form corpus:** 51 items → 91 unique tokens (RC2 triage)

---

## High-risk findings (machine-submit & authority)

| ID | Finding | Severity | Fix lane |
|----|---------|----------|----------|
| F-001 | `recommended` column treated as pick | **P0** | INCIDENT-037 + `FOUNDER PICK supremacy` |
| F-002 | Partial submit without `partial_batch=true` → `INCOMPLETE_FOUNDER_PICKS` | **P0** | Document in submit map; CLI guard exists |
| F-003 | Agent paths must not set `agent_live_submit: true` | **P0** | Receipt law on partial submit receipt |
| F-004 | Gather-phase disk rows vs founder picks | **P1** | `gathering_phase` overlay term |
| F-005 | DLM `apply_map` from open form without validated picks | **P1** | DLM pipeline law (existing) |
| F-006 | TF/NF blocks field — must read as serves not vs | **P1** | SG dictionary `TF/NF` row |
| F-007 | TrustField entity aliases in form copy | **P1** | SG alias retired → TrustField |
| F-008 | Duplicate/overlapping questions in 80-row corpus | **P2** | DLM cluster pass |

---

## NEEDS_SG_ENTRY queue (23 — do not define in SourceA)

Form corpus terms with no SG row yet. Require pile-style approval + named source file before dictionary write:

- INBOX, Worker INBOX, RUN INBOX, Next INBOX, Pause INBOX, Delete INBOX, Run INBOX  
- Proof Lab, WitnessBC Proof Lab  
- CREED, CREED SSOT, CREED/CHURCH  
- Governance Platform, Trust Center, Trust Ledger, Witness AI  
- Worker Hub, Remove Worker Hub, Retire Worker Hub  
- Worker BUILD, Worker Mac, Worker WORK  
- Cloud Workers, Screen Studio, Noetfield Copilot  
- RT LIVE, Prompt OS  
- SourceA Forge Governance (partial overlap — see SG `SourceA Forge`)

---

## SG_DICTIONARY_TERM hits in form corpus (21)

Already in SG — SourceA must cite, not redefine:

- TF/NF, TrustField, Brain Worker, System Architect, SourceA Worker  
- Premium Model Firewall, Queue SSOT  
- Plus ONE / PLUS ONE INDEX / Plus ONE Hub (manual map)  
- Chat Unify (from UNIFY / Brain UNIFY)  
- Gateway Railway (from Railway FBE)  
- Merge Hub (from Restore Hub)  
- One Proof Layer (from Proof Layer / SourceA Forge Proof Layer)  
- Worker RUN INBOX (from Worker INBOX / RUN INBOX)  
- SourceA Forge (from SourceA Forge Governance)  
- Skip Proof Lab (form fragment maps to defer — SG pile-3 skip)

---

## COMMAND_FRAGMENT & FORM_OPTION (not terms)

**COMMAND_FRAGMENT examples:** Instrument TF, Keep Witness AI, Manual LinkedIn, Record Screen Studio, Update LinkedIn, Cloud Workers Proceed, PLAN WITH NO ASF, Nov Options, PICKs Options, Approve Phase.

**FORM_OPTION examples:** vendor/infra option strings (Closes Gemini, Cloud SSE, CNAME, Paid Cloudflare Pages, Supabase Edge, Cursor Card, …).

**STATUS_LABEL examples:** DEFER, CANCEL, SHIP, APPROVE, YES, NO, BLOCK, SHIPPED, LOCKED, recommended, confirmed, applied_now, open_remaining.

---

## SourceA script tokens (overlay-local)

From `hub_form_submit_v1.py` / `live_founder_decision_form_v1.py`:

- Submit guards: `INCOMPLETE_FOUNDER_PICKS`, `FOUNDER_PICKS_REQUIRED`, `FOUNDER_ACTOR_REQUIRED`  
- Paths: `disk_fast_apply`, `partial_batch`, `cascade_hub`, `background_wire`  
- Receipts: `hub-form-submit-receipt-v1`, `hub-form-submit-background-v1`  
- Form mirror: `form_official_line`, `DRIFT_FLOOR`, `nerve_map`

---

## Recommended cleanup order

1. **P0** — Enforce INCIDENT-037 on all submit paths; verify partial_batch docs match CLI.  
2. **P1** — Lint form exports against overlay index (class → rule).  
3. **P2** — Process `NEEDS_SG_ENTRY` through SG dictionary pile (not SourceA repo).  
4. **P2** — Keep form frozen; use P99 exports + DLM for terminology evidence only.

---

## Scope exclusions

- SourceA product repo not edited in this audit (read-only script extract).  
- FORM_OFFICIAL live form not reopened.  
- No new SG dictionary entries written in this pass.

---

*v1 audit (2026-07-07) — post LANGUAGE_LAYER_RC3_CHECKPOINT.*
