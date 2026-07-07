#!/usr/bin/env python3
"""Agent rewrite pass — plain English after regex lint (deterministic RC2)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

GATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATE_DIR))

from language_gate_core_v1 import (  # noqa: E402
    Dictionary,
    Finding,
    SURFACE_POLICY,
    is_compound_slug,
    is_json_path,
    is_rewrite_locked,
    load_dictionary,
    normalize_public_phrasing,
    protected_spans,
)


def _substitute_outside_spans(text: str, pattern: re.Pattern[str], replacement: str) -> tuple[str, bool]:
    spans = protected_spans(text)
    changed = False
    parts: list[str] = []
    cursor = 0
    for m in pattern.finditer(text):
        if any(m.start() >= a and m.end() <= b for a, b in spans):
            continue
        if is_compound_slug(text, m.start(), m.end()):
            continue
        parts.append(text[cursor : m.start()])
        parts.append(replacement)
        cursor = m.end()
        changed = True
    parts.append(text[cursor:])
    return "".join(parts), changed


def plain_english_pass(text: str, surface: str, dictionary: Dictionary, findings: list[Finding], *, file_path: str | None = None) -> tuple[str, list[dict[str, Any]]]:
    """Deterministic plain-English rewrite using dictionary public phrasing."""
    if is_rewrite_locked(file_path) or is_json_path(file_path):
        return text, []
    if not SURFACE_POLICY[surface]["plain_rewrite"]:
        return text, []

    actions: list[dict[str, Any]] = []
    out = text

    skip_line_re = re.compile(r"(^|\*\*)(Commercial|Live surface|Governance)\b", re.I)
    technical_assign_re = re.compile(r"=\s*\S")

    if surface in {"public", "website", "contract"}:
        for term_key, phrase in sorted(dictionary.public_phrasing.items(), key=lambda x: -len(x[0])):
            if " " not in term_key and len(term_key) <= 8:
                continue
            replacement = normalize_public_phrasing(phrase) or phrase
            if "`" in replacement or "CODE_ALIAS" in replacement:
                continue
            if not replacement or replacement.lower() == term_key.lower():
                continue
            pat = re.compile(rf"\b{re.escape(term_key)}\b", re.IGNORECASE)
            if not pat.search(out):
                continue

            new_parts: list[str] = []
            cursor = 0
            changed = False
            for m in pat.finditer(out):
                line_start = out.rfind("\n", 0, m.start()) + 1
                line_end = out.find("\n", m.start())
                if line_end < 0:
                    line_end = len(out)
                line = out[line_start:line_end]
                if "`" in line or skip_line_re.search(line):
                    continue
                tail = out[m.end() : m.end() + 3]
                if technical_assign_re.match(tail):
                    continue
                if any(m.start() >= a and m.end() <= b for a, b in protected_spans(out)):
                    continue
                if is_compound_slug(out, m.start(), m.end()):
                    continue
                repl = replacement
                if m.start() == line_start or out[m.start() - 1] in ".:;\n":
                    repl = repl[:1].upper() + repl[1:] if repl else repl
                new_parts.append(out[cursor : m.start()])
                new_parts.append(repl)
                cursor = m.end()
                changed = True
            if changed:
                new_parts.append(out[cursor:])
                out = "".join(new_parts)
                actions.append(
                    {
                        "type": "PLAIN_ENGLISH",
                        "term": term_key,
                        "replacement": replacement,
                        "reason": f"public phrasing for {surface} surface",
                    }
                )

    for idx, line in enumerate(out.splitlines(), start=1):
        words = line.split()
        if len(words) < 28:
            continue
        title_hits = len(re.findall(r"\b[A-Z][a-z]+(?: [A-Z][a-z]+)+\b", line))
        if title_hits >= 2:
            actions.append(
                {
                    "type": "AGENT_REVIEW",
                    "line": idx,
                    "reason": "long sentence with multiple Title Case phrases — rewrite to plain English",
                    "hint": "Use short sentences. One idea per sentence. Prefer dictionary public phrasing.",
                }
            )

    jargon_patterns = [
        (r"\bleverage\b", "use"),
        (r"\butilize\b", "use"),
        (r"\bin order to\b", "to"),
        (r"\bat this point in time\b", "now"),
    ]
    for pat_str, repl in jargon_patterns:
        pat = re.compile(pat_str, re.IGNORECASE)
        new_out, changed = _substitute_outside_spans(out, pat, repl)
        if changed:
            actions.append({"type": "PLAIN_ENGLISH", "pattern": pat_str, "replacement": repl})
            out = new_out

    return out, actions


def write_sidecar(file_path: Path, actions: list[dict[str, Any]], *, warnings: list[dict[str, Any]] | None = None) -> Path | None:
    review = [a for a in actions if a.get("type") == "AGENT_REVIEW"]
    if not review and not warnings:
        return None
    payload: dict[str, Any] = {"file": str(file_path), "agent_review": review}
    if warnings:
        payload["dictionary_warnings"] = warnings
    sidecar = file_path.with_suffix(file_path.suffix + ".language_gate_review.json")
    sidecar.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return sidecar


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", type=Path)
    ap.add_argument("--surface", default="internal")
    ap.add_argument("--findings-json", type=Path, help="regex findings JSON array")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    text = args.file.read_text(encoding="utf-8")
    dictionary = load_dictionary()
    findings: list[Finding] = []
    if args.findings_json and args.findings_json.is_file():
        for row in json.loads(args.findings_json.read_text(encoding="utf-8")):
            findings.append(Finding(**{**row, "auto_fixed": row.get("auto_fixed", False)}))

    rewritten, actions = plain_english_pass(text, args.surface, dictionary, findings)
    sidecar = write_sidecar(args.file, actions)

    if args.write and rewritten != text:
        args.file.write_text(rewritten, encoding="utf-8")

    report = {
        "schema": "language_gate_agent_rewrite_v1",
        "file": str(args.file),
        "surface": args.surface,
        "actions_count": len(actions),
        "actions": actions,
        "sidecar": str(sidecar) if sidecar else None,
        "changed": rewritten != text,
    }
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"AGENT_REWRITE actions={len(actions)} changed={report['changed']}")
        for action in actions[:20]:
            print(f"  {action['type']}: {action}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
