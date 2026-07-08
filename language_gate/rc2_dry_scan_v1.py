#!/usr/bin/env python3
"""RC2 dry scan — five controlled surfaces from RC1, no --write."""

from __future__ import annotations

import difflib
import json
import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
REPO = GATE_DIR.parent
sys.path.insert(0, str(GATE_DIR))

from language_gate_agent_rewrite_v1 import plain_english_pass  # noqa: E402
from language_gate_core_v1 import decide, load_dictionary, scan  # noqa: E402
from language_gate_pipeline_v1 import run_pipeline  # noqa: E402

FILES = [
    ("internal doctrine", "SG-Canonical-Library/noetfield-library/P7-DOCTRINE/mechanical-not-prose.md", "internal"),
    ("public website copy", "SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/sourcea.md", "website"),
    ("prompt/work-order", "SG-Canonical-Library/noetfield-library/P1-CANON/WORK_ORDER_IDE_LANE_v1.md", "prompt"),
    ("contract/private", "SG-Canonical-Library/noetfield-library/P99-LEDGER/REVENUE_WORK_AUTHORIZATION_2026-07-05.md", "contract"),
    ("receipt/ledger", "SG-Canonical-Library/noetfield-library/P99-LEDGER/FIRST_REVENUE_RECEIPT_2026-07-06.md", "receipt"),
]


def meaning_changed(before: str, after: str) -> bool:
    ratio = difflib.SequenceMatcher(None, before, after).ratio()
    return ratio < 0.985 and before != after


def main() -> int:
    dictionary = load_dictionary()
    report: dict = {"schema": "language_gate_rc2_dry_scan_v1", "files": []}

    for label, rel, surface in FILES:
        path = REPO / rel
        if not path.is_file():
            report["files"].append({"label": label, "path": rel, "error": "missing"})
            continue

        text = path.read_text(encoding="utf-8")
        findings, regex_rw = scan(text, surface, dictionary)
        decision, blockers = decide(findings)

        pipeline = run_pipeline(path, surface=surface, write=False, skip_agent=False, strict_undefined=False)

        agent_preview, agent_actions = plain_english_pass(regex_rw if decision != "FAIL" else text, surface, dictionary, findings)
        row = {
            "label": label,
            "path": rel,
            "surface": surface,
            "decision": pipeline["decision"],
            "findings_count": len(findings),
            "undefined_count": sum(1 for f in findings if f.type == "UNDEFINED_TERM"),
            "undefined_terms": sorted({f.term for f in findings if f.type == "UNDEFINED_TERM"}),
            "blockers": pipeline["blockers"],
            "agent_actions_count": len(pipeline["agent_actions"]),
            "agent_preview_changed": agent_preview != text,
            "meaning_changed_preview": meaning_changed(text, agent_preview),
            "receipt_path": pipeline["receipt_path"],
        }
        report["files"].append(row)

    out = GATE_DIR / "receipts" / "rc2_dry_scan_report.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"\nREPORT: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
