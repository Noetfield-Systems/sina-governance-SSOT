#!/usr/bin/env python3
"""CLI: Motor Learning Organ W1 reference runner (no live promotion)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from motor_learning.orchestrator import run_from_fixture_dir, run_pipeline, rollback_prior  # noqa: E402
from motor_learning.errors import MotorLearningError, GovernanceBlock  # noqa: E402
from motor_learning.validated import mint_w1_reference_store_capability  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Motor Learning Organ W1 reference runner")
    ap.add_argument("--fixture", type=Path, help="Fixture directory with events.json")
    ap.add_argument("--events", type=Path, help="Path to events.json")
    ap.add_argument("--shadow-events", type=Path, help="Independent shadow events JSON (mandatory for ratification)")
    ap.add_argument("--ecqr", type=Path, help="Path to ecqr_decision.json")
    ap.add_argument("--out", type=Path, required=True, help="Output directory")
    ap.add_argument("--store", type=Path, help="W1 reference prior store directory")
    ap.add_argument("--min-occurrences", type=int, default=3)
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument(
        "--no-dry-run",
        action="store_true",
        help="Persist W1 reference records only (live_consumable=false; requires --allow-store-persist)",
    )
    ap.add_argument(
        "--allow-store-persist",
        action="store_true",
        help="Required with --no-dry-run; enables w1_reference store capability (never live-consumable)",
    )
    ap.add_argument("--rollback-prior", type=str, help="Prior ID to roll back")
    ap.add_argument("--regression-evidence", type=str, nargs="*", help="Evidence IDs for rollback")
    ap.add_argument(
        "--inject-failure-after",
        type=str,
        default=None,
        help="Test hook: receipt_staging|prior_staging|before_index_commit",
    )
    args = ap.parse_args()

    dry_run = not args.no_dry_run
    store = args.store or (args.out / "prior_store")
    store_capability = None
    allow_persist = False

    try:
        if not dry_run:
            if not args.allow_store_persist:
                raise GovernanceBlock(
                    "--no-dry-run requires --allow-store-persist "
                    "(W1 reference store only; live_consumable always false)"
                )
            store_capability = mint_w1_reference_store_capability()
            allow_persist = True

        if args.rollback_prior:
            if not args.ecqr:
                ap.error("--ecqr required with --rollback-prior")
            ecqr = json.loads(args.ecqr.read_text())
            summary = rollback_prior(
                prior_id=args.rollback_prior,
                store_dir=store,
                out_dir=args.out,
                ecqr_decision=ecqr,
                regression_evidence=list(args.regression_evidence or ecqr.get("evidence_reviewed") or []),
                dry_run=dry_run,
                store_capability=store_capability,
                allow_store_persist=allow_persist,
                inject_failure_after=args.inject_failure_after,
            )
        elif args.fixture:
            summary = run_from_fixture_dir(
                args.fixture,
                out_dir=args.out,
                store_dir=store,
                dry_run=dry_run,
                store_capability=store_capability,
                allow_store_persist=allow_persist,
                inject_failure_after=args.inject_failure_after,
            )
        else:
            if not args.events:
                ap.error("--fixture or --events or --rollback-prior required")
            events = json.loads(args.events.read_text())
            shadow = json.loads(args.shadow_events.read_text()) if args.shadow_events else None
            ecqr = json.loads(args.ecqr.read_text()) if args.ecqr else None
            summary = run_pipeline(
                events=events,
                shadow_events=shadow,
                store_dir=store,
                out_dir=args.out,
                ecqr_decision=ecqr,
                min_occurrences=args.min_occurrences,
                dry_run=dry_run,
                store_capability=store_capability,
                allow_store_persist=allow_persist,
                inject_failure_after=args.inject_failure_after,
            )
    except MotorLearningError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    # ok:true only when operation succeeded
    if summary.get("blocked_reason") and not summary.get("receipt_id"):
        print(json.dumps({"ok": False, "summary": summary}, indent=2))
        return 1
    if summary.get("ok") is False:
        print(json.dumps({"ok": False, "summary": summary}, indent=2))
        return 1

    print(json.dumps({"ok": True, "summary": summary}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
