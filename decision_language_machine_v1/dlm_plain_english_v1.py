#!/usr/bin/env python3
"""Plain-English rewrite pass for decision items."""

from __future__ import annotations

import re

from dlm_core_v1 import DecisionItem

JARGON_REPLACEMENTS = [
    (r"\bleverage\b", "use"),
    (r"\butilize\b", "use"),
    (r"\bin order to\b", "to"),
    (r"\bat this point in time\b", "now"),
    (r"\bMotor\b", "scheduler and executor"),
    (r"\bmodel-agnostic\b", "vendor-neutral"),
    (r"\bleast-knowledge\b", "need-to-know access"),
    (r"\bSSOT\b", "single source of truth"),
    (r"\bNOOS\b", "operations scheduler"),
    (r"\bFBE\b", "cloud factory builder"),
    (r"\bLOI\b", "letter of intent"),
    (r"\bSOW\b", "statement of work"),
    (r"\bMCP\b", "tool connection layer"),
    (r"\bDNS\b", "domain name setup"),
]

ACRONYM_EXPAND = {
    "ROI": "return on investment",
    "NDA": "non-disclosure agreement",
    "MSA": "master services agreement",
}


def _expand_acronyms(text: str) -> str:
    out = text
    for acr, full in ACRONYM_EXPAND.items():
        out = re.sub(rf"\b{acr}\b", f"{full} ({acr})", out, flags=re.IGNORECASE)
    return out


def _simplify_options(options: list[str]) -> list[str]:
    simplified: list[str] = []
    for opt in options:
        o = re.sub(r"^[A-E]\s*[—\-]\s*", "", opt)
        o = re.sub(r"\s*\(recommended\)", "", o, flags=re.IGNORECASE)
        simplified.append(o.strip())
    return simplified


def rewrite_item(item: DecisionItem) -> str:
    parts: list[str] = []
    if item.title and item.title != item.question:
        parts.append(item.title.rstrip("?") + ".")
    core = item.question or item.raw_text
    core = _expand_acronyms(core)
    for pat, repl in JARGON_REPLACEMENTS:
        core = re.sub(pat, repl, core, flags=re.IGNORECASE)
    parts.append(core.strip())
    if item.effect:
        eff = item.effect
        for pat, repl in JARGON_REPLACEMENTS:
            eff = re.sub(pat, repl, eff, flags=re.IGNORECASE)
        parts.append(f"Effect: {eff}")
    if item.options:
        opts = _simplify_options(item.options[:4])
        if opts:
            parts.append("Options: " + " · ".join(opts))
    text = " ".join(parts)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text.split()) > 45:
        text = text[:320].rsplit(" ", 1)[0] + "…"
    return text

