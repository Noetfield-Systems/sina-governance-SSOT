
#!/usr/bin/env python3
"""CLI: run Motor Learning Organ W1 fixture pipeline (no live promotion)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from motor_learning.orchestrator import run_from_fixture_dir, run_pipeline  # noqa: E402
from motor_learning.errors import MotorLearningError  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Motor Learning Organ W1 reference runner")
    ap.add_argument("--fixture", type=Path, help="Fixture directory with events.json")
    ap.add_argument("--events", type=Path, help="Path to events.json")
    ap.add_argument("--ecqr", type=Path, help="Path to ecqr_decision.json")
    ap.add_argument("--out", type=Path, required=True, help="Output directory")
    ap.add_argument("--store", type=Path, help="Prior store directory")
    ap.add_argument("--min-occurrences", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--no-dry-run", action="store_true", help="Write store artifacts (still no live promo)")
    args = ap.parse_args()

    dry_run = not args.no_dry_run
    store = args.store or (args.out / "prior_store")
    try:
        if args.fixture:
            summary = run_from_fixture_dir(args.fixture, out_dir=args.out, store_dir=store, dry_run=dry_run)
        else:
            if not args.events:
                ap.error("--fixture or --events required")
            events = json.loads(args.events.read_text())
            ecqr = json.loads(args.ecqr.read_text()) if args.ecqr else None
            summary = run_pipeline(
                events=events,
                store_dir=store,
                out_dir=args.out,
                ecqr_decision=ecqr,
                min_occurrences=args.min_occurrences,
                dry_run=dry_run,
            )
    except MotorLearningError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    print(json.dumps({"ok": summary.get("blocked_reason") is None or summary.get("receipt_id") is not None or summary.get("final_state") in ("OBSERVED", "PROPOSED", "SHADOW"), "summary": summary}, indent=2))
    # Non-zero if governance failure when decision was attempted and blocked
    if summary.get("ecqr_decision") is None and args.ecqr and summary.get("blocked_reason"):
        # attempted decision but blocked — still may be success for insufficient-evidence fixtures
        if "insufficient" in (summary.get("blocked_reason") or ""):
            return 0
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
