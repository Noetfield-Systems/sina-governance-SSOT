#!/usr/bin/env python3
"""Language gate pipeline: regex lint → agent plain-English rewrite."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATE_DIR))

from language_gate_agent_rewrite_v1 import plain_english_pass, write_sidecar  # noqa: E402
from language_gate_core_v1 import (  # noqa: E402
    decide,
    infer_surface,
    load_dictionary,
    scan,
    write_receipt,
)


def run_pipeline(
    file_path: Path,
    *,
    surface: str = "auto",
    write: bool = False,
    skip_agent: bool = False,
) -> dict:
    dictionary = load_dictionary()
    resolved_surface = infer_surface(str(file_path), None if surface == "auto" else surface)
    text = file_path.read_text(encoding="utf-8")
    findings, regex_rewritten = scan(text, resolved_surface, dictionary)
    decision, blockers = decide(findings)

    regex_applied = False
    working = text
    if decision != "FAIL" and regex_rewritten != text:
        working = regex_rewritten
        regex_applied = True
        if write:
            file_path.write_text(working, encoding="utf-8")

    agent_applied = False
    agent_actions: list = []
    sidecar = None
    if decision != "FAIL" and not skip_agent:
        agent_text, agent_actions = plain_english_pass(working, resolved_surface, dictionary, findings)
        if agent_text != working:
            agent_applied = True
            working = agent_text
            if write:
                file_path.write_text(working, encoding="utf-8")
        sidecar = write_sidecar(file_path, agent_actions)

    if agent_applied and decision == "PASS":
        decision = "PASS_WITH_REWRITE"

    receipt_path, receipt = write_receipt(
        str(file_path),
        resolved_surface,
        findings,
        decision,
        blockers,
        rewrite_applied=regex_applied or agent_applied,
        agent_rewrite_applied=agent_applied,
        dictionary_source="SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md",
        extra={"agent_actions_count": len(agent_actions), "sidecar": str(sidecar) if sidecar else None},
    )
    return {
        "decision": decision,
        "surface": resolved_surface,
        "findings": [f.as_dict() for f in findings],
        "blockers": [f.as_dict() for f in blockers],
        "receipt_path": str(receipt_path),
        "receipt": receipt,
        "agent_actions": agent_actions,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", type=Path)
    ap.add_argument("--surface", default="auto", choices=["auto", "internal", "public", "website", "contract", "prompt", "receipt"])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--skip-agent", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if not args.file.is_file():
        print(f"FAIL: file not found: {args.file}", file=sys.stderr)
        return 1

    result = run_pipeline(args.file, surface=args.surface, write=args.write, skip_agent=args.skip_agent)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"FILE: {args.file}")
        print(f"SURFACE: {result['surface']}")
        print(f"DECISION: {result['decision']}")
        for f in result["findings"]:
            tag = "BLOCK" if f["type"] in {"BANNED_REGISTER", "OVERCLAIM", "BANNED_SURFACE", "UNDEFINED_TERM"} else "AUTO-FIX"
            fix = f" -> '{f['fix']}'" if f.get("fix") else ""
            print(f"  [{tag}] {f['type']}: '{f['term']}' (line {f['line']}){fix}")
        if result["agent_actions"]:
            print(f"AGENT_REWRITE actions={len(result['agent_actions'])}")
        print(f"RECEIPT: {result['receipt_path']}")

    return 1 if result["decision"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
