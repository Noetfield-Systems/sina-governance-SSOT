#!/usr/bin/env python3
"""Generate NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md — plain English canonical, aliases retired."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
REPO_ROOT = GATE_DIR.parent
INDEX_PATH = GATE_DIR / "dictionary_index.json"
OUT_PATH = REPO_ROOT / "SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md"

# Plain English canonical wins; old jargon becomes alias/retired.
CANONICAL_PROMOTIONS = {
    "motor": {
        "canonical_term": "Scheduler and executor",
        "meaning": "The cloud scheduler and the process runner that start loops on a timer.",
        "in_our_system": "Cloudflare cron dispatches to the Railway loop runner.",
        "is_not": "The loop body itself or a one-off script.",
        "example": "CF `*/5` cron fires; Railway runs the loop handler.",
        "aliases_retired": ["Motor", "motor"],
        "public_phrasing": "scheduled cloud runner",
        "allowed_surfaces": "internal, receipt, prompt",
        "code_alias": ["motor", "noos-loop-fleet-tick-v1"],
    },
    "least-knowledge": {
        "canonical_term": "Need-to-know access",
        "meaning": "Give an agent only the data and permissions required for its task.",
        "in_our_system": "Tier 0–2 law routing; workers never load founder judgment patterns.",
        "is_not": "Load the whole library so the agent can figure it out.",
        "example": "Inbox worker sees queue rows, not contract drafts.",
        "aliases_retired": ["Least-knowledge", "least-knowledge", "least privilege"],
        "public_phrasing": "minimum access required for the task",
        "allowed_surfaces": "internal, contract, prompt",
    },
    "reserved commercial figure": {
        "canonical_term": "Confidential commercial terms",
        "meaning": "Revenue-share or routing percentages spoken only under NDA and in signed contracts.",
        "in_our_system": "Contract `[●]` variable only; never public copy.",
        "is_not": "A percentage on a website or first-call slide.",
        "example": "NDA deck may discuss structure; public pages omit numbers.",
        "aliases_retired": ["Reserved commercial figure", "reserved commercial figure", "the percentage"],
        "public_phrasing": "confidential commercial terms (under NDA)",
        "allowed_surfaces": "contract",
        "banned_surfaces": "website, public, prompt",
    },
}

SYNONYM_ALIASES = {
    "model-agnostic": "vendor-neutral",
    "agnostic": "vendor-neutral",
    "client base": "governed reference environment",
}


def clean_field(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    for cut in (" Is NOT:", " Example:", " Doctrine source file:", " Public phrasing:", " ---"):
        idx = text.find(cut)
        if idx > 0:
            text = text[:idx].strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def entry_block(
    term: str,
    tag: str | None,
    fields: dict[str, str | list[str] | None],
) -> str:
    lines = [f"**{term}**" + (f" — {tag}" if tag else "")]
    for key, label in (
        ("meaning", "Meaning"),
        ("in_our_system", "In our system"),
        ("is_not", "Is NOT"),
        ("example", "Example"),
        ("aliases_retired", "Aliases retired"),
        ("public_phrasing", "Public phrasing"),
        ("conflict_rule", "Conflict rule"),
        ("allowed_surfaces", "Allowed surfaces"),
        ("banned_surfaces", "Banned surfaces"),
        ("related", "Related"),
        ("doctrine_source_file", "Doctrine source file"),
        ("code_alias", "Code alias"),
    ):
        val = fields.get(key)
        if not val:
            continue
        if isinstance(val, list):
            lines.append(f"{label}: {', '.join(val)}")
        else:
            lines.append(f"{label}: {val}")
    return "\n".join(lines) + "\n"


def main() -> int:
    if not INDEX_PATH.is_file():
        print(f"FAIL: missing {INDEX_PATH}", file=sys.stderr)
        return 1
    raw = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
    retired_keys = set()
    promoted_canonicals: list[str] = []

    parts = [
        "# NOETFIELD_DICTIONARY_BATCH_A-Z_v1",
        "",
        "**Meaning authority source** — plain English canonical terms. Old jargon lives under `Aliases retired`.",
        "Terminology rows are **minted from** this file. Rebuild index: `python3 language_gate/build_dictionary_index.py`.",
        "",
        "---",
        "",
    ]

    # Canonical promotions first (plain English wins)
    for key, promo in CANONICAL_PROMOTIONS.items():
        retired_keys.update(a.lower() for a in promo["aliases_retired"])
        retired_keys.add(key)
        promoted_canonicals.append(promo["canonical_term"].lower())
        parts.append(entry_block(promo["canonical_term"], "CANONICAL", promo))
        parts.append("---\n")

    # Synonym aliases as retired stubs
    for alias, canonical in SYNONYM_ALIASES.items():
        parts.append(
            entry_block(
                alias,
                "ALIAS RETIRED",
                {
                    "meaning": f"Retired wording. Use canonical term: {canonical}.",
                    "aliases_retired": [alias],
                    "conflict_rule": f"Auto-rewrite to {canonical} per terminology §6.",
                },
            )
        )
        parts.append("---\n")
        retired_keys.add(alias.lower())

    skip_terms = retired_keys | set(promoted_canonicals)
    for row in sorted(raw.get("terms") or [], key=lambda r: str(r.get("term") or "").lower()):
        term = str(row.get("term") or "").strip()
        if not term or term.lower() in skip_terms:
            continue
        tag = row.get("tag")
        if tag and "TOMBSTONE" in str(tag):
            continue
        fields = {
            "meaning": clean_field(row.get("meaning")),
            "in_our_system": clean_field(row.get("in_our_system")),
            "is_not": clean_field(row.get("is_not")),
            "example": clean_field(row.get("example")),
            "public_phrasing": clean_field(row.get("public_phrasing")),
            "allowed_surfaces": clean_field(row.get("allowed_surfaces")),
            "banned_surfaces": clean_field(row.get("banned_surfaces")),
            "related": clean_field(row.get("related")),
            "doctrine_source_file": clean_field(row.get("doctrine_source_file")),
        }
        parts.append(entry_block(term, None, fields))
        parts.append("---\n")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(parts).rstrip() + "\n", encoding="utf-8")
    print(f"OK: wrote {OUT_PATH} ({len(parts)} blocks)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
