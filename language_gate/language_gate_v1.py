#!/usr/bin/env python3
"""CLI wrapper — prefer language_gate_pipeline_v1.py for full flow."""

from __future__ import annotations

import sys
from pathlib import Path

GATE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(GATE_DIR))

from language_gate_pipeline_v1 import run_pipeline  # noqa: E402


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file")
    ap.add_argument("--surface", default="auto")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--skip-agent", action="store_true")
    args = ap.parse_args()

    result = run_pipeline(
        Path(args.file),
        surface=args.surface,
        write=args.write,
        skip_agent=args.skip_agent,
    )
    print(f"DECISION: {result['decision']} surface={result['surface']}")
    print(f"RECEIPT: {result['receipt_path']}")
    return 1 if result["decision"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
