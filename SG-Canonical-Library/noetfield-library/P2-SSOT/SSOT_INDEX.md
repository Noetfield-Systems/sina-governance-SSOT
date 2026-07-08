# SSOT INDEX — ratified truth & state rules

**Authority:** subordinate only to FOUNDER_CANON v1. Every agent reads canon first, then the SSOT rules that apply to its layer.
**Updated:** 2026-07-03 12:34 PDT

---

## RATIFIED (binding)

| Rule | File | What it binds |
|---|---|---|
| **SSOT v6 constitution** | `ssot/strategy-ssot-v6-split.md` (repo root — **REMOTE CANONICAL**) | Level 0 invariants + D1–D5 domain SSOTs. Library mirror: `P0-FOUNDATION-SPINE/strategy-ssot-v6-split.md`. Verifier: `check.py`. |
| **R-domain split** | `SSOT_CONFLICT_LOG_R_SPLIT_v0.1.2.md` | Only D4-portable Runtime Rules **R1/R2/R6/R7** import into agentic-brain contexts (Brain Registry, Learning Gate, mutation lanes). **R3/R4/R5 stay control-panel only** (founder-assistant conversation), never inlined into agentic specs. `AUDIT`/`EXECUTE` are control-panel terms, excluded from brain vocabulary. |
| **Cross-domain auth** | `../../docs/CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md` | Tiered Supabase auth law; matrix `data/auth_surface_matrix_v1.json`; SG probe only. |
| **Living System doctrine** | `../P0-FOUNDATION-SPINE/P0-CORE/LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md` | P0-CORE organ law: LIVING vs STALE axis; dual circulatory systems; §8 machine rubric. Execution: `docs/LIVING_SYSTEM_110_UPGRADE_PLANS_v1_LOCKED.md`. |
| **CHESS reasoning machine** | `../P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md` | P0 forecast-before-action machine: Forecast → Patch → Proceed → Verify; labels PROCEED / PROCEED_WITH_PATCH / ASK_IF_IRREVERSIBLE; template `../P0-TEMPLATES/CHESS_PASS_PROMPT_TEMPLATE_v2.0.md`. |
| **Versioning law** | `SSOT_VERSIONING_LAW_v0.1.1.md` | Every edited artifact carries `v{major}.{minor}.{edit}_{YYYYMMDD-HHMM}` in **filename + in-file header + edit-log**. major=scope/phase change; minor=founder-approved substantive change; edit=every saved pass. No silent re-saves. Superseded versions retained unless founder says clean up. |

## QUICK-REFERENCE derivations (for agents)
- `R_DOMAIN_SPLIT.md` — the R1–R7 portability table (which rules cross into brain contexts).
- `VERSIONING_RULE.md` — the filename+header pattern, copy-paste form.
- `OPEN_BLOCKERS.md` — the current real blockers (per targets-vs-blockers: only genuine harm/impossible stops the system).
- `../P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` — mandatory short vocabulary (Tier 0).
- `../P7-DOCTRINE/NOETFIELD_DICTIONARY_v1.md` — long-form word SSOT (escalation).
- `../P0-FOUNDATION-SPINE/P0-CORE/LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md` — living vs stale axis (P0-CORE).
- `../P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md` — terminology vs dictionary vs doctrine routing.

## The R1–R7 portability table (canonical)
| Rule | Domain | Portable to agentic-brain? |
|---|---|---|
| R1 — session start / git truth | D4 | ✅ yes |
| R2 — source-of-truth order | D4 | ✅ yes |
| R3 — mode switch (AUDIT/EXECUTE) | control-panel | ❌ no |
| R4 — prompt size law | control-panel | ❌ no |
| R5 — dirty file law | control-panel | ❌ no |
| R6 — receipt law | D4 | ✅ yes |
| R7 — agent cannot self-verify | D4 | ✅ yes |

---
*v0.2 (2026-07-07) — Living System doctrine indexed.

*v0.1 (2026-07-03 12:34 PDT) — first write. Indexes the two ratified SSOT items + portability table.*
