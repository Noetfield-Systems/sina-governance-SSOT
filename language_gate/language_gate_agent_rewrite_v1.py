#!/usr/bin/env python3
"""Agent rewrite pass — plain English after regex lint (deterministic v1)."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

GATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATE_DIR))

from language_gate_core_v1 import Dictionary, Finding, SURFACE_POLICY, load_dictionary  # noqa: E402


def _strip_quotes(s: str) -> str:
    return s.strip().strip('"')


def plain_english_pass(text: str, surface: str, dictionary: Dictionary, findings: list[Finding]) -> tuple[str, list[dict[str, Any]]]:
    """Deterministic plain-English rewrite using dictionary public phrasing."""
    if not SURFACE_POLICY[surface]["plain_rewrite"]:
        return text, []

    actions: list[dict[str, Any]] = []
    out = text

    # Replace known canonical terms with public phrasing on outward surfaces.
    if surface in {"public", "website", "contract"}:
        for term_key, phrase in sorted(dictionary.public_phrasing.items(), key=lambda x: -len(x[0])):
            pat = re.compile(rf"\b{re.escape(term_key)}\b", re.IGNORECASE)
            if not pat.search(out):
                continue
            # Only swap multi-word jargon-like keys, not tiny words
            if len(term_key) < 8 and " " not in term_key:
                continue
            replacement = _strip_quotes(phrase)
            if replacement.lower() == term_key.lower():
                continue
            new_out = pat.sub(replacement, out)
            if new_out != out:
                actions.append(
                    {
                        "type": "PLAIN_ENGLISH",
                        "term": term_key,
                        "replacement": replacement,
                        "reason": f"public phrasing for {surface} surface",
                    }
                )
                out = new_out

    # Flag long unclear sentences for agent review (sidecar instructions).
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

    # Convert passive jargon patterns.
    jargon_patterns = [
        (r"\bleverage\b", "use"),
        (r"\butilize\b", "use"),
        (r"\bin order to\b", "to"),
        (r"\bat this point in time\b", "now"),
    ]
    for pat_str, repl in jargon_patterns:
        pat = re.compile(pat_str, re.IGNORECASE)
        if pat.search(out):
            actions.append({"type": "PLAIN_ENGLISH", "pattern": pat_str, "replacement": repl})
            out = pat.sub(repl, out)

    return out, actions


def write_sidecar(file_path: Path, actions: list[dict[str, Any]]) -> Path | None:
    review = [a for a in actions if a.get("type") == "AGENT_REVIEW"]
    if not review:
        return None
    sidecar = file_path.with_suffix(file_path.suffix + ".language_gate_review.json")
    sidecar.write_text(json.dumps({"file": str(file_path), "agent_review": review}, indent=2) + "\n", encoding="utf-8")
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
