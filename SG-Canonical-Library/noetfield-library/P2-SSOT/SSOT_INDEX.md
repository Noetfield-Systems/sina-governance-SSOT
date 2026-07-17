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
| **Architecture Finalization Gate** | `../P8-MACHINE-LOOPS/ARCHITECTURE_FINALIZATION_GATE_LOCKED_v1.md` | Major architecture becomes canonical only after SG packet + authority SHA. Machine `data/architecture_finalization_gate_v1_LOCKED.json`. |
| **Unified Motor Core architecture** | `../P0-FOUNDATION-SPINE/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCKED_v1.md` | `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` SG_ACCEPTED; Client-Zero profile; Agents≠Workflows; waves in `docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md`. |
| **Versioning law** | `SSOT_VERSIONING_LAW_v0.1.1.md` | Every edited artifact carries `v{major}.{minor}.{edit}_{YYYYMMDD-HHMM}` in **filename + in-file header + edit-log**. major=scope/phase change; minor=founder-approved substantive change; edit=every saved pass. No silent re-saves. Superseded versions retained unless founder says clean up. |
| **Library custody matrix** | `LIBRARY_CUSTODY_MATRIX_LOCKED_v1.md` | Custody chain: Master SSOT → Library → NOOS → runtime → verifier. Tier namespace law. Invalid receipt patterns. |
| **Founder reasoning authority graph** | `AUTHORITY_GRAPH_FOUNDER_REASONING_LOCKED_v1.md` | Authority routing for §0.7 motor; lane sequence; four required integrator components (names). |
| **Founder reasoning continuation** | `../P8-MACHINE-LOOPS/founder-reasoning-continuation-doctrine-LOCKED_v1.md` | Escalation = continuation; park rules; packet + ingestion minimums; subscription vs API automation. |
| **Cost execution doctrine** | `../P10-PRODUCT-LAYERS/COST_EXECUTION_DOCTRINE_LOCKED_v1.md` | COST-T0/T1/T2 lanes; caps; degradation vocabulary; deterministic loops without LLM. |
| **Motor commissioning standard** | `../P8-MACHINE-LOOPS/MOTOR_COMMISSIONING_AND_ACCEPTANCE_STANDARD_LOCKED_v1.md` | Cold proof runs A+B; `FULLY_COMMISSIONED` acceptance law. Design ≠ commissioned. |
| **NOOS operational binding** | `Noetfield-Systems/noetfeld-OS` → `noetfield-org/FOUNDER_REASONING_MOTOR_OPERATIONAL_BINDING_v1.md` | Full operational spec; commit-pinned via `CUSTODY_AUTHORITY_PINS_v1.json`. **Not library SSOT.** |
| **NOOS motor schemas** | `Noetfield-Systems/noetfeld-OS` → `noetfield-org/schemas/` | Packet, result, job contract, private binding JSON schemas. P7 §12 harmonization. |

## QUICK-REFERENCE derivations (for agents)
- `R_DOMAIN_SPLIT.md` — the R1–R7 portability table (which rules cross into brain contexts).
- `VERSIONING_RULE.md` — the filename+header pattern, copy-paste form.
- `OPEN_BLOCKERS.md` — the current real blockers (per targets-vs-blockers: only genuine harm/impossible stops the system).
- `../P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md` — mandatory short vocabulary (Tier 0).
- `../P7-DOCTRINE/NOETFIELD_DICTIONARY_v1.md` — long-form word SSOT (escalation).
- `../P0-FOUNDATION-SPINE/P0-CORE/LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md` — living vs stale axis (P0-CORE).
- `LIBRARY_CUSTODY_MATRIX_LOCKED_v1.md` — who locks what (P2 custody law).
- `AUTHORITY_GRAPH_FOUNDER_REASONING_LOCKED_v1.md` — §0.7 authority routing graph.

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

- `../P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md` — terminology vs dictionary vs doctrine routing.

---
*v0.4 (2026-07-10) — Option C: P7 §12 harmonization, P8 commissioning, NOOS schemas index.*

*v0.3 (2026-07-10) — Founder reasoning custody chain: custody matrix, authority graph, P8 continuation, P10 cost execution, NOOS operational binding index.*

*v0.2 (2026-07-07) — Living System doctrine indexed.*

*v0.1 (2026-07-03 12:34 PDT) — first write. Indexes the two ratified SSOT items + portability table.*
