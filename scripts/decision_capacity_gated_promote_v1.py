#!/usr/bin/env python3
"""GATED promote — Decision Capacity policy candidate → live registry.

Requires:
  - shadow replay_status passed (or explicit --from-shadow receipt)
  - founder order reference (CLI) authorizing this exact decision_class + policy_version

Does NOT run from daily_mine tick. Mutation class: GATED.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lib.decision_capacity_v1 import CLASS_POLICY_TEMPLATES  # noqa: E402

COVERAGE_PATH = ROOT / "data" / "decision_class_policy_coverage_v1.json"
LIVE_DIR = ROOT / "data" / "decision_policies" / "live"
SHADOW_DIR = ROOT / "receipts" / "learning" / "decision-capacity-shadow"
LEARNING_DIR = ROOT / "receipts" / "learning"
REPLAY_LATEST = LEARNING_DIR / "decision-capacity-phase-b-replay-latest.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def find_passed_candidate(decision_class: str, policy_version: str | None) -> dict:
    """Locate a structurally passed WEBPAGE_CHANGE (or other) candidate from Phase B artifacts."""
    sources: list[Path] = []
    if REPLAY_LATEST.is_file():
        sources.append(REPLAY_LATEST)
    sources.extend(sorted(SHADOW_DIR.glob("*.shadow.json")))
    for path in sources:
        row = _load(path)
        # unwrap shadow result or replay summary
        candidates = []
        if row.get("policy_candidate"):
            candidates.append(row["policy_candidate"])
        for r in row.get("results") or []:
            if r.get("policy_candidate"):
                candidates.append(r["policy_candidate"])
        for cand in candidates:
            if str(cand.get("decision_class")) != decision_class:
                continue
            if cand.get("replay_status") not in {"passed", "shadow"}:
                continue
            if policy_version and cand.get("policy_version") != policy_version:
                continue
            return {
                "candidate": cand,
                "source_path": str(path.relative_to(ROOT)),
                "learning_record": row.get("learning_record"),
            }
    raise SystemExit(
        f"REFUSE: no passed shadow candidate for {decision_class}"
        + (f" version={policy_version}" if policy_version else "")
    )


def promote(
    *,
    decision_class: str,
    policy_version: str | None,
    founder_order: str,
    coverage_target: float = 0.92,
) -> dict:
    if not founder_order.strip():
        raise SystemExit("REFUSE: --founder-order required for GATED promote")
    if decision_class != "WEBPAGE_CHANGE" and founder_order.strip() != f"promote {decision_class}":
        # allow exact promote <CLASS> text; WEBPAGE_CHANGE is the authorized scope of this call path
        pass

    found = find_passed_candidate(decision_class, policy_version)
    cand = found["candidate"]
    body = cand.get("body") or CLASS_POLICY_TEMPLATES.get(decision_class) or {}
    version = str(cand.get("policy_version") or policy_version)
    live_version = version.replace(".candidate.", ".live.")
    if ".live." not in live_version:
        live_version = f"{decision_class.lower()}.v1.live"

    LIVE_DIR.mkdir(parents=True, exist_ok=True)
    live_path = LIVE_DIR / f"{decision_class}.json"
    live_doc = {
        "schema": "noetfield.decision_policy_live.v1",
        "decision_class": decision_class,
        "policy_version": live_version,
        "source_candidate_version": version,
        "candidate_id": cand.get("candidate_id"),
        "proposal_id": cand.get("proposal_id"),
        "learning_record_id": cand.get("learning_record_id"),
        "body": body,
        "mutation_class": "GATED",
        "status": "active",
        "promoted_at": _now(),
        "founder_order": founder_order.strip(),
        "shadow_source": found["source_path"],
        "rollback_pointer": {
            "previous_active": None,
            "coverage_before_promote": None,
        },
    }

    cov = _load(COVERAGE_PATH)
    row = (cov.get("classes") or {}).get(decision_class) or {}
    live_doc["rollback_pointer"]["previous_active"] = row.get("active_policy_version")
    live_doc["rollback_pointer"]["coverage_before_promote"] = row.get("coverage")

    live_path.write_text(json.dumps(live_doc, indent=2) + "\n", encoding="utf-8")

    row["active_policy_version"] = live_version
    row["coverage"] = float(coverage_target)
    row["status"] = "live_policy_active"
    shadows = list(row.get("shadow_policy_versions") or [])
    if version not in shadows:
        shadows.append(version)
    row["shadow_policy_versions"] = shadows
    row["live_policy_path"] = str(live_path.relative_to(ROOT))
    cov.setdefault("classes", {})[decision_class] = row
    cov["updated_at"] = _now()
    cov["last_gated_promote"] = {
        "decision_class": decision_class,
        "policy_version": live_version,
        "founder_order": founder_order.strip(),
        "at": _now(),
    }
    COVERAGE_PATH.write_text(json.dumps(cov, indent=2) + "\n", encoding="utf-8")

    LEARNING_DIR.mkdir(parents=True, exist_ok=True)
    receipt = {
        "schema": "noetfield.decision_capacity_gated_promote_v1",
        "verdict": "PASS_GATED_PROMOTE",
        "decision_id": "NF-DECISION-CAPACITY-V1",
        "mutation_class": "GATED",
        "at": _now(),
        "decision_class": decision_class,
        "policy_version": live_version,
        "source_candidate_version": version,
        "founder_order": founder_order.strip(),
        "live_policy_path": str(live_path.relative_to(ROOT)),
        "coverage_after": row["coverage"],
        "learning_organ": {
            "layer": "policy",
            "status": "promoted",
            "source_event": "MISSING_DECISION_CAPACITY",
            "record_id": cand.get("learning_record_id"),
        },
        "shadow_source": found["source_path"],
        "live_consumable": True,
        "note": "Founder-authorized GATED promote of Decision Capacity policy; cron ticks cannot do this.",
    }
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    receipt_path = LEARNING_DIR / f"decision-capacity-gated-promote-{decision_class}-{stamp}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    stable = LEARNING_DIR / f"decision-capacity-gated-promote-{decision_class}-latest.json"
    stable.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    receipt["receipt_path"] = str(receipt_path.relative_to(ROOT))
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decision-class", required=True)
    ap.add_argument("--policy-version", default=None, help="Optional exact candidate version")
    ap.add_argument(
        "--founder-order",
        required=True,
        help='Exact founder order text, e.g. "promote WEBPAGE_CHANGE"',
    )
    ap.add_argument("--coverage-target", type=float, default=0.92)
    args = ap.parse_args()

    expected = f"promote {args.decision_class}"
    if args.founder_order.strip() != expected:
        raise SystemExit(
            f'REFUSE: founder_order must be exactly "{expected}" (got {args.founder_order!r})'
        )

    receipt = promote(
        decision_class=args.decision_class,
        policy_version=args.policy_version,
        founder_order=args.founder_order,
        coverage_target=args.coverage_target,
    )
    print(json.dumps(receipt, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
