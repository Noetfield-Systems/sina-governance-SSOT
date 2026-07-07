#!/usr/bin/env python3
"""Term extraction and dictionary/terminology check."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

GATE_DIR = Path(__file__).resolve().parents[1] / "language_gate"
sys.path.insert(0, str(GATE_DIR))

from language_gate_core_v1 import (  # noqa: E402
    COMMON_WORD_ALLOWLIST,
    ENTITY_ALLOWLIST,
    KNOWN_VENDOR_ALLOWLIST,
    LEADING_STOPWORDS,
    STRUCTURAL_ALLOWLIST,
    TERM_RE,
    is_skippable_undefined,
    line_text_at,
    load_dictionary,
    protected_spans,
)

STOP_TERMS = COMMON_WORD_ALLOWLIST | KNOWN_VENDOR_ALLOWLIST | STRUCTURAL_ALLOWLIST | ENTITY_ALLOWLIST | {
    "yes", "no", "defer", "approve", "never", "pick", "form", "row", "option",
    "recommended", "founder", "worker", "brain", "build", "wait", "ship",
}


def extract_terms(text: str) -> list[dict[str, Any]]:
    spans = protected_spans(text)
    seen: set[str] = set()
    terms: list[dict[str, Any]] = []
    for m in TERM_RE.finditer(text):
        term = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if not term or len(term) < 3:
            continue
        start, end = m.start(), m.end()
        line = line_text_at(text, start)
        if is_skippable_undefined(term, line=line, text=text, start=start, end=end, spans=spans):
            continue
        low = term.lower()
        if low in seen or low in STOP_TERMS:
            continue
        if low.split()[0] in LEADING_STOPWORDS if " " in low else False:
            continue
        seen.add(low)
        terms.append({"term": term, "normalized": low})
    # also pull quoted tokens
    for m in re.finditer(r"`([^`]{3,40})`", text):
        t = m.group(1).strip()
        low = t.lower()
        if low not in seen:
            seen.add(low)
            terms.append({"term": t, "normalized": low})
    return terms


def check_terms(terms: list[dict[str, Any]], dictionary=None) -> tuple[list[dict[str, Any]], bool]:
    dictionary = dictionary or load_dictionary()
    flags: list[dict[str, Any]] = []
    fix_needed = False
    for row in terms:
        low = row["normalized"]
        if low in dictionary.terms:
            flags.append({**row, "status": "DICTIONARY_OK", "canonical": row["term"]})
        elif low in dictionary.alias_map:
            flags.append({
                **row,
                "status": "ALIAS_RETIRED",
                "canonical": dictionary.alias_map[low],
                "fix": "use canonical term",
            })
            fix_needed = True
        elif low in dictionary.code_alias:
            flags.append({**row, "status": "CODE_ALIAS_OK", "canonical": row["term"]})
        elif low in dictionary.retired_terms:
            flags.append({**row, "status": "RETIRED", "fix": "remove or replace"})
            fix_needed = True
        else:
            flags.append({
                **row,
                "status": "DICTIONARY_FIX_NEEDED",
                "fix": "add dictionary entry before minting terminology",
            })
            fix_needed = True
    return flags, fix_needed

