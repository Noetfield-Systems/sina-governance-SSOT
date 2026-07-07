# Language Gate v1

Mechanical **wording authority** (terminology) + **agent plain-English rewrite** after regex lint.

## Authority chain

```
NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md  (meaning source — plain English canonical)
        ↓ build_dictionary_index.py
dictionary_index.json
        ↓
language_gate_pipeline_v1.py  (regex lint → agent rewrite)
        ↓
NOETFIELD_TERMINOLOGY_v1.md  (one-line rows minted from dictionary)
```

**Rule:** plain English canonical wins; old jargon → `Aliases retired` / `alias_map`.

## Surfaces

| Surface | Use |
|---------|-----|
| `internal` | Library, ledgers, engineering notes |
| `public` | External-facing docs |
| `website` | Marketing / landing copy (strictest overclaim) |
| `contract` | Statement of work, master services agreement, NDA clauses |
| `prompt` | Agent prompts, `.cursor/` |
| `receipt` | JSON receipt fields |
| `auto` | Infer from path |

## Pipeline

```bash
python3 language_gate/language_gate_pipeline_v1.py <file> [--surface auto|internal|...] [--write]
```

1. **Regex lint** — alias retired, synonym §6, banned §7, overclaim, PRIVATE_ONLY, undefined title-case system terms  
2. **Agent rewrite pass** — deterministic plain English (public phrasing, jargon trims, review sidecar)

Exit `1` = FAIL (fail-closed). Writes `language_gate/receipts/*.receipt.json`.

## Rebuild dictionary index

```bash
python3 language_gate/generate_batch_markdown_v1.py
python3 language_gate/build_dictionary_index.py
```

## Mandatory hooks (Cursor + git)

**Cursor** (`.cursor/hooks.json`):

- `afterFileEdit` → regex + rewrite on save (`--write`)
- `preToolUse` on write tools → block on FAIL before content lands

**Git pre-commit** (repo-local):

```bash
bash scripts/install_language_gate_hooks_v1.sh
```

## Known gap

Regex first pass — not full language understanding. Disguised jargon may slip; title-case phrases may false-positive. Agent review sidecar flags long unclear sentences.


## RC2 (2026-07-07)

Fixes from RC1 dry scan on five controlled canon files:

| RC1 issue | RC2 fix |
|-----------|---------|
| UNDEFINED_TERM noise (headers, doc labels, vendors) | Structural + entity allowlists; skip markdown headers, code spans, link URLs, hyphen fragments |
| Rewrite pass skipped on FAIL | `WARN` for undefined-only; `--soft-undefined` runs rewrite pass for evaluation |
| Agent pass corrupted compounds/links | Protected spans; skip hyphenated slugs; clean public_phrasing footnotes; skip Commercial/technical lines |
| Dictionary gaps (NOOS, lane slugs) | `dictionary_rc2_supplement.json` merged at load |

### RC2 dry scan

```bash
python3 language_gate/rc2_dry_scan_v1.py
# report: language_gate/receipts/rc2_dry_scan_report.json
```

### Strict vs soft undefined

- **Hooks / pre-commit (default):** exit 1 on `WARN` (undefined terms still block minting)
- **Dry scan / readability eval:** `--soft-undefined` exit 0 on `WARN`; rewrites run; sidecar lists dictionary warnings

Tool version: `language_gate_rc2_v1`
