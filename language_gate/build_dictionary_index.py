#!/usr/bin/env python3
"""Rebuild language_gate/dictionary_index.json from A-Z dictionary batch markdown."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATE_DIR.parent
DEFAULT_SRC = REPO_ROOT / "SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md"
OUT_PATH = GATE_DIR / "dictionary_index.json"

FIELD_LABELS = [
    "Meaning",
    "In our system",
    "Is NOT",
    "Example",
    "Aliases retired",
    "Public phrasing",
    "Conflict rule",
    "Allowed surfaces",
    "Banned surfaces",
    "Related",
    "Doctrine source file",
    "Code alias",
]


def slug_key(term: str) -> str:
    return term.strip().lower()


def parse_batch(text: str) -> dict:
    header_re = re.compile(r"^\*\*(.+?)\*\*(?:\s*—\s*(.+))?\s*$", re.MULTILINE)
    matches = list(header_re.finditer(text))
    entries: list[dict] = []
    alias_map: dict[str, str] = {}
    retired_terms: list[str] = []
    private_only: list[str] = []
    code_alias: list[str] = []

    for i, m in enumerate(matches):
        term_raw = m.group(1).strip()
        tag_raw = (m.group(2) or "").strip() or None
        if term_raw.lower().startswith("noetfield_dictionary"):
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip().split("\n---")[0].strip()

        fields: dict[str, str | list[str] | None] = {k: None for k in (
            "meaning", "in_our_system", "is_not", "example", "aliases_retired",
            "public_phrasing", "conflict_rule", "allowed_surfaces", "banned_surfaces",
            "related", "doctrine_source_file", "code_alias",
        )}

        for line in body.splitlines():
            line = line.strip()
            if not line or ":" not in line:
                continue
            label, _, val = line.partition(":")
            label = label.strip()
            val = val.strip()
            key_map = {
                "Meaning": "meaning",
                "In our system": "in_our_system",
                "Is NOT": "is_not",
                "Example": "example",
                "Aliases retired": "aliases_retired",
                "Public phrasing": "public_phrasing",
                "Conflict rule": "conflict_rule",
                "Allowed surfaces": "allowed_surfaces",
                "Banned surfaces": "banned_surfaces",
                "Related": "related",
                "Doctrine source file": "doctrine_source_file",
                "Code alias": "code_alias",
            }
            fk = key_map.get(label)
            if not fk:
                continue
            if fk in {"aliases_retired", "code_alias"}:
                fields[fk] = [p.strip() for p in val.split(",") if p.strip()]
            else:
                fields[fk] = val

        entry = {
            "term": term_raw,
            "tag": tag_raw,
            **fields,
        }
        entries.append(entry)

        canonical = term_raw
        if tag_raw and "CANONICAL" in tag_raw:
            aliases = fields.get("aliases_retired") or []
            if isinstance(aliases, list):
                for alias in aliases:
                    alias_map[slug_key(str(alias))] = canonical
                    retired_terms.append(str(alias))
            code = fields.get("code_alias") or []
            if isinstance(code, list):
                code_alias.extend(str(c) for c in code)
        elif tag_raw and "ALIAS RETIRED" in tag_raw:
            m_canon = re.search(r"Use canonical term:\s*(.+?)\.", fields.get("meaning") or "")
            if m_canon:
                alias_map[slug_key(term_raw)] = m_canon.group(1).strip()
            retired_terms.append(term_raw)
        elif tag_raw and "PRIVATE_ONLY" in tag_raw:
            private_only.append(term_raw)

        if fields.get("banned_surfaces") and "public" in str(fields["banned_surfaces"]).lower():
            private_only.append(term_raw)

    # de-dupe
    retired_terms = sorted({t for t in retired_terms if t})
    code_alias = sorted({c for c in code_alias if c})
    private_only = sorted({p for p in private_only if p})

    return {
        "schema": "noetfield-dictionary-index-v1",
        "source": str(DEFAULT_SRC.relative_to(REPO_ROOT)),
        "generated_by": "language_gate/build_dictionary_index.py",
        "terms": entries,
        "alias_map": alias_map,
        "retired_terms": retired_terms,
        "private_only": private_only,
        "code_alias": code_alias,
        # legacy key for older gate readers
        "tombstone_map": alias_map,
    }


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.is_file():
        print(f"FAIL: batch source not found: {src}", file=sys.stderr)
        return 1
    index = parse_batch(src.read_text(encoding="utf-8"))
    OUT_PATH.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(index['terms'])} entries -> {OUT_PATH}")
    print(f"alias_map: {index['alias_map']}")
    print(f"retired: {len(index['retired_terms'])} private_only: {len(index['private_only'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
