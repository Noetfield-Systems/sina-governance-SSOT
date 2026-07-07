#!/usr/bin/env python3
"""Rebuild language_gate/dictionary_index.json from A-Z dictionary batch markdown."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATE_DIR.parent
DEFAULT_SRC = REPO_ROOT / "SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_DRAFT.md"
OUT_PATH = GATE_DIR / "dictionary_index.json"


def parse_batch(text: str) -> dict:
    entry_re = re.compile(r"^\*\*(.+?)\*\*(?:\s*—\s*(.+))?$", re.MULTILINE)
    matches = list(entry_re.finditer(text))
    entries = []
    for i, m in enumerate(matches):
        term_raw = m.group(1).strip()
        tag_raw = (m.group(2) or "").strip()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        body = text[start:end].strip()
        if not body or term_raw.lower().startswith("noetfield dictionary"):
            continue
        if term_raw == "" or "exceptions requiring" in term_raw.lower():
            continue

        def grab(field: str, body: str = body) -> str | None:
            pat = re.compile(
                rf"{field}:\s*(.+?)(?=\n\*\*|\n[A-Z][a-z]+ (?:source|phrasing|surfaces):|\Z)",
                re.DOTALL,
            )
            mm = pat.search(body)
            return mm.group(1).strip().replace("\n", " ") if mm else None

        entries.append(
            {
                "term": term_raw,
                "tag": tag_raw or None,
                "meaning": grab("Meaning"),
                "in_our_system": grab("In our system"),
                "is_not": grab("Is NOT"),
                "example": grab("Example"),
                "public_phrasing": grab("Public phrasing") or grab("Public-safe rewrite"),
                "doctrine_source_file": grab("Doctrine source file"),
                "allowed_surfaces": grab("Allowed surfaces"),
                "banned_surfaces": grab("Banned surfaces"),
                "related": grab("Related"),
            }
        )

    tombstones: dict[str, str] = {}
    private_only: list[str] = []
    code_alias: list[str] = []
    for e in entries:
        tag = e["tag"] or ""
        if "TOMBSTONE" in tag:
            m = re.search(r"replaced by (.+)", tag)
            if m:
                repl = re.sub(r'[`"]', "", m.group(1).strip().rstrip(")").strip()).rstrip("`")
                tombstones[e["term"].lower()] = repl
        if "PRIVATE_ONLY" in tag:
            private_only.append(e["term"])
        if "CODE_ALIAS" in tag:
            code_alias.append(e["term"])

    return {
        "terms": entries,
        "tombstone_map": tombstones,
        "private_only": private_only,
        "code_alias": code_alias,
    }


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC
    if not src.is_file():
        print(f"FAIL: batch source not found: {src}", file=sys.stderr)
        print("Commit dictionary_index.json or place A-Z batch at default path.", file=sys.stderr)
        return 1
    index = parse_batch(src.read_text(encoding="utf-8"))
    OUT_PATH.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(index['terms'])} entries -> {OUT_PATH}")
    print(f"Tombstones: {index['tombstone_map']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
