# UPLOADED ZIP RECONCILIATION — 2026-07-04
**Purpose:** decide which uploaded library package is the latest reliable base before producing the true-final SG intake package.

## Inputs inspected
| Uploaded file | Nested library zip | Nested file count | SHA256 prefix | Verdict |
|---|---|---:|---|---|
| `files (11).zip` | `noetfield-library-v0.5-SPINE-INSTALLED.zip` | 87 | `74b69a0d706d06d1` | duplicate v0.5 |
| `files (10).zip` | `noetfield-library-v0.6-P0CORE-INSTALLED.zip` | 92 | `55c493d8034971d2` | superseded |
| `files (9)(1).zip` | `noetfield-library-FINAL-v0.7-E2E-AUDITED.zip` | 94 | `458f1116c4670273` | latest base |
| `files (8).zip` | `noetfield-library-FINAL-v0.6.zip` | 93 | `82dce78388d0eac5` | superseded |
| `files (7).zip` | `noetfield-library-v0.5-SPINE-INSTALLED.zip` | 87 | `74b69a0d706d06d1` | duplicate v0.5 |

## Selection

`noetfield-library-FINAL-v0.7-E2E-AUDITED.zip` was selected as the base because it is the newest superset: 94 files, includes the E2E audit, D-U-N-S product update, P0 CORE founder judgment patterns, AGENT_LAYERED_LAW, and the v0.6/v0.5 content lineage.

## Superseded package differences against v0.7

### `noetfield-library-v0.5-SPINE-INSTALLED.zip`
- File count: 87
- Missing vs v0.7: 7
  - `P0-FOUNDATION-SPINE/AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE_SSOT_LOCKED_v1.md`
  - `P0-FOUNDATION-SPINE/P0-CORE/FOUNDER_JUDGMENT_PATTERNS_v1.md`
  - `P10-PRODUCT-LAYERS/SINA_GATEWAY_BLUEPRINT_LOCKED_v1.md`
  - `P2-SSOT/AGENT_LAYERED_LAW_xref.md`
  - `P99-LEDGER/ARCHITECT2_CONSISTENCY_CHECK_2026-07-04.md`
  - `P99-LEDGER/E2E_AUDIT_2026-07-04.md`
  - `P99-LEDGER/THE_REAL_DIAGNOSIS_revenue-organ_2026-07-04.md`
- Changed vs v0.7: 6
  - `00-INDEX.md`
  - `ARCHITECT_START_HERE.md`
  - `P2-SSOT/OPEN_BLOCKERS.md`
  - `P7-DOCTRINE/layered-agents.md`
  - `P99-LEDGER/2026-06-30-deep-mined-gems.md`
  - `P99-LEDGER/LIBRARY_STATE_FOR_SG_2026-07-04.md`

### `noetfield-library-v0.6-P0CORE-INSTALLED.zip`
- File count: 92
- Missing vs v0.7: 2
  - `P99-LEDGER/E2E_AUDIT_2026-07-04.md`
  - `P99-LEDGER/THE_REAL_DIAGNOSIS_revenue-organ_2026-07-04.md`
- Changed vs v0.7: 7
  - `00-INDEX.md`
  - `ARCHITECT_START_HERE.md`
  - `P2-SSOT/AGENT_LAYERED_LAW_xref.md`
  - `P2-SSOT/OPEN_BLOCKERS.md`
  - `P7-DOCTRINE/layered-agents.md`
  - `P99-LEDGER/2026-06-30-deep-mined-gems.md`
  - `P99-LEDGER/LIBRARY_STATE_FOR_SG_2026-07-04.md`

### `noetfield-library-FINAL-v0.6.zip`
- File count: 93
- Missing vs v0.7: 1
  - `P99-LEDGER/E2E_AUDIT_2026-07-04.md`
- Changed vs v0.7: 7
  - `00-INDEX.md`
  - `ARCHITECT_START_HERE.md`
  - `P2-SSOT/AGENT_LAYERED_LAW_xref.md`
  - `P2-SSOT/OPEN_BLOCKERS.md`
  - `P7-DOCTRINE/layered-agents.md`
  - `P99-LEDGER/2026-06-30-deep-mined-gems.md`
  - `P99-LEDGER/LIBRARY_STATE_FOR_SG_2026-07-04.md`

### `noetfield-library-v0.5-SPINE-INSTALLED.zip`
- File count: 87
- Missing vs v0.7: 7
  - `P0-FOUNDATION-SPINE/AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE_SSOT_LOCKED_v1.md`
  - `P0-FOUNDATION-SPINE/P0-CORE/FOUNDER_JUDGMENT_PATTERNS_v1.md`
  - `P10-PRODUCT-LAYERS/SINA_GATEWAY_BLUEPRINT_LOCKED_v1.md`
  - `P2-SSOT/AGENT_LAYERED_LAW_xref.md`
  - `P99-LEDGER/ARCHITECT2_CONSISTENCY_CHECK_2026-07-04.md`
  - `P99-LEDGER/E2E_AUDIT_2026-07-04.md`
  - `P99-LEDGER/THE_REAL_DIAGNOSIS_revenue-organ_2026-07-04.md`
- Changed vs v0.7: 6
  - `00-INDEX.md`
  - `ARCHITECT_START_HERE.md`
  - `P2-SSOT/OPEN_BLOCKERS.md`
  - `P7-DOCTRINE/layered-agents.md`
  - `P99-LEDGER/2026-06-30-deep-mined-gems.md`
  - `P99-LEDGER/LIBRARY_STATE_FOR_SG_2026-07-04.md`

## Rule

Older packages are retained as lineage only. Do not install v0.5/v0.6 over v0.8 unless SG explicitly needs historical diff evidence.
