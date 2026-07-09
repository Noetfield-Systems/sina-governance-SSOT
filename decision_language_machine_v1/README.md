# decision_language_machine_v1

Reusable machine for turning messy decision backlogs into founder-ready language.

**The form is not the product. The machine is the product.**

## Pipeline

1. Intake — form row, chat fork, audit finding, agent question, or backlog JSON/markdown
2. Plain English — rewrite jargon into readable sentences
3. Term extract — pull important terms from each item
4. Dictionary check — compare against language_gate/dictionary_index.json
5. DICTIONARY_FIX_NEEDED — flag undefined or retired terms
6. Cluster — group duplicate or overlapping decisions
7. Classify — MACHINE_VALIDATABLE · ADVISOR_REVIEW · FOUNDER_FACT · DEFER
8. Founder sheet — reduced advisor clusters + founder facts only
9. Apply map — submit/apply map only after picks are validated (never auto-submit FORM_OFFICIAL)
10. Receipts — one JSON receipt per stage under receipts/

## Usage

```bash
cd decision_language_machine_v1

python3 dlm_v1.py test_fixtures/form_official_80_open_v1.json --json

python3 dlm_v1.py test_fixtures/form_official_80_open_v1.json \
  --validated-picks ../SG-Canonical-Library/noetfield-library/P99-LEDGER/FOUNDER_DECISION_BATCH_SIMPLIFIED_FORM_2026-07-07.json

python3 dlm_v1.py my_backlog.md --skip-apply-map
```

## Outputs

- output/{run_id}.manifest.json
- output/{run_id}.founder_sheet.json / .md
- output/{run_id}.processed.json
- output/{run_id}.apply_map.json (when validated picks provided)
- receipts/{run_id}.{stage}.*.receipt.json

