#!/usr/bin/env python3
"""CLI for decision_language_machine_v1."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from dlm_pipeline_v1 import run_pipeline


def main() -> int:
    ap = argparse.ArgumentParser(
        description="decision_language_machine_v1 — messy backlog to founder sheet",
    )
    ap.add_argument("input", type=Path, help="JSON backlog, form export, or markdown bullet list")
    ap.add_argument("--validated-picks", type=Path, default=None, help="Founder-validated picks JSON")
    ap.add_argument("--skip-apply-map", action="store_true", help="Stop before apply map stage")
    ap.add_argument("--no-partial-batch", action="store_true", help="Block apply map if picks incomplete")
    ap.add_argument("--json", action="store_true", help="Print summary JSON")
    args = ap.parse_args()

    if not args.input.exists():
        print(f"input not found: {args.input}", file=sys.stderr)
        return 2

    summary = run_pipeline(
        args.input,
        validated_picks_path=args.validated_picks,
        partial_batch=not args.no_partial_batch,
        skip_apply_map=args.skip_apply_map,
    )
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"run_id: {summary['run_id']}")
        print(f"items: {summary['item_count']}")
        print(f"classification: {summary['classification']}")
        print(f"founder_sheet: {summary['founder_sheet']}")
        print(f"manifest: {summary['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

