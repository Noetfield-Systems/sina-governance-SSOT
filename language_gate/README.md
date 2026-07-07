# Language Gate v1

Mechanical **wording authority** enforcement for terminology (not meaning NLU).

- **Dictionary index:** `dictionary_index.json` (91 terms from A-Z batch; rebuild via `build_dictionary_index.py`)
- **Scanner:** `language_gate_v1.py`
- **Meaning SSOT:** `../SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_v1.md`
- **Daily wording:** `../SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md`

## Usage

```bash
python3 language_gate_v1.py <file> [--surface public|internal] [--write]
```

| Exit | Decision | Meaning |
|------|----------|---------|
| 0 | PASS | Clean |
| 0 | PASS_WITH_REWRITE | Auto-fixed tombstone/synonym (--write applies) |
| 1 | FAIL | Blocked — fix or add dictionary entry first |

Every run writes `receipts/<file>.<scan_id>.receipt.json`.

## Checks

1. Tombstoned words → auto-rewrite  
2. Terminology §6 synonym drift → auto-rewrite  
3. Terminology §7 banned register → block  
4. Overclaims (100% guaranteed, certified, unprovable customer counts) → block  
5. PRIVATE_ONLY on public surface → block  
6. Title-Case / ALLCAPS system-looking term with no dictionary entry → block (fail-closed)

## Test fixtures

```bash
python3 language_gate_v1.py test_files/clean_example.md                    # PASS
python3 language_gate_v1.py test_files/violations_example.md --surface public  # FAIL
cp test_files/tombstone_only.md /tmp/t.js.md && python3 language_gate_v1.py /tmp/t.js.md --write  # PASS_WITH_REWRITE
```

## Known gap (documented, not hidden)

Regex pattern matching — not language understanding. Will miss disguised jargon; may false-positive on ordinary Title Case. **Mechanical first pass only.** Agent-level exception review still required for edge cases.

## Wire as hook

Pre-commit, CI on `SG-Canonical-Library/**`, or Cursor pre-save on public copy paths. Mint rule unchanged: new terms need dictionary entry before terminology line.
