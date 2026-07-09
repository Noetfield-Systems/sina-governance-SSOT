#!/usr/bin/env python3
"""Negative-proof gate: P0 CORE cannot inject into normal Tier 1 worker dispatches."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READ_SCOPE_PATH = ROOT / "data/founder_judgment_patterns_read_scope_v1.json"
REGISTRY_PATH = ROOT / "data/governance_artifact_registry_v1.json"
ARTIFACT_ID = "founder-judgment-patterns-v1"

PROTECTED_MARKERS = (
    ARTIFACT_ID,
    "FOUNDER_JUDGMENT_PATTERNS_v1.md",
    "P0-FOUNDATION-SPINE/P0-CORE/FOUNDER_JUDGMENT_PATTERNS_v1.md",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_artifact(registry: dict, artifact_id: str) -> dict | None:
    for art in registry.get("artifacts", []):
        if art.get("artifact_id") == artifact_id:
            return art
    return None


def bundle_references_p0_core(law_bundle: list[str]) -> bool:
    lowered = [x.lower() for x in law_bundle]
    for marker in PROTECTED_MARKERS:
        m = marker.lower()
        for item in lowered:
            if m in item:
                return True
    return False


def evaluate_dispatch(
    reader_id: str,
    tier: str,
    law_bundle: list[str],
    read_scope: dict,
    registry_art: dict | None,
) -> dict:
    """Simulate dispatcher gate — BLOCK before execution if forbidden."""
    references_p0 = bundle_references_p0_core(law_bundle)
    allowed = set(read_scope.get("allowed_readers", []))
    forbidden = set(read_scope.get("forbidden_readers", []))
    forbidden_tiers = set(read_scope.get("forbidden_tiers", []))

    if not references_p0:
        return {
            "decision": "ALLOW",
            "reason": "law bundle does not reference protected P0 CORE",
            "blocked": False,
        }

    if registry_art is None or registry_art.get("status") != read_scope.get("registry_status_required", "ACTIVE"):
        return {
            "decision": "BLOCK",
            "reason": "BLOCKED_WITH_REASON: protected artifact not ACTIVE in SG registry",
            "blocked": True,
        }

    if read_scope.get("inject_into_worker_prompts") is False and reader_id in forbidden:
        return {
            "decision": "BLOCK",
            "reason": read_scope.get(
                "dispatcher_action_if_worker_request",
                "BLOCKED_WITH_REASON — P0 CORE forbidden for this reader",
            ),
            "blocked": True,
        }

    if tier in forbidden_tiers and reader_id not in allowed:
        return {
            "decision": "BLOCK",
            "reason": f"BLOCKED_WITH_REASON: tier {tier} forbidden for P0 CORE load",
            "blocked": True,
        }

    if reader_id in allowed:
        return {
            "decision": "ALLOW",
            "reason": f"reader {reader_id} in allowed_readers for P0 CORE",
            "blocked": False,
        }

    return {
        "decision": "BLOCK",
        "reason": f"BLOCKED_WITH_REASON: reader {reader_id} not authorized for P0 CORE",
        "blocked": True,
    }


def run_tests(read_scope: dict, registry_art: dict | None) -> list[dict]:
    tests = [
        {
            "name": "forbidden_tier1_worker_by_artifact_id",
            "reader_id": "tier_1_worker",
            "tier": "tier_1",
            "law_bundle": ["gov-structure-authority-v1", ARTIFACT_ID],
            "expected": "BLOCK",
        },
        {
            "name": "forbidden_tier1_worker_by_filename",
            "reader_id": "normal_worker",
            "tier": "tier_1",
            "law_bundle": [
                "skill-foundational-agentic-systems",
                "FOUNDER_JUDGMENT_PATTERNS_v1.md",
            ],
            "expected": "BLOCK",
        },
        {
            "name": "allowed_base_live_brain",
            "reader_id": "base_live_brain",
            "tier": "tier_0",
            "law_bundle": [ARTIFACT_ID],
            "expected": "ALLOW",
        },
        {
            "name": "allowed_high_decision_agent",
            "reader_id": "high_decision_agent",
            "tier": "tier_0",
            "law_bundle": [
                "P0-FOUNDATION-SPINE/P0-CORE/FOUNDER_JUDGMENT_PATTERNS_v1.md"
            ],
            "expected": "ALLOW",
        },
    ]

    results = []
    for t in tests:
        outcome = evaluate_dispatch(
            t["reader_id"], t["tier"], t["law_bundle"], read_scope, registry_art
        )
        actual = outcome["decision"]
        pass_ = actual == t["expected"]
        results.append({**t, "actual": actual, "blocked": outcome["blocked"], "reason": outcome["reason"], "pass": pass_})
    return results


def main() -> int:
    read_scope = load_json(READ_SCOPE_PATH)
    registry = load_json(REGISTRY_PATH)
    registry_art = registry_artifact(registry, ARTIFACT_ID)

    disposable_dispatch = {
        "dispatch_id": "disposable-negative-proof-tier1-worker",
        "reader_id": "tier_1_worker",
        "tier": "tier_1",
        "role": "policy_checker_worker",
        "law_bundle": [
            "gov-structure-authority-v1",
            ARTIFACT_ID,
            "FOUNDER_JUDGMENT_PATTERNS_v1.md",
        ],
        "note": "disposable test only — never executed",
    }

    primary_block = evaluate_dispatch(
        disposable_dispatch["reader_id"],
        disposable_dispatch["tier"],
        disposable_dispatch["law_bundle"],
        read_scope,
        registry_art,
    )

    control_results = run_tests(read_scope, registry_art)
    all_pass = primary_block["blocked"] and all(r["pass"] for r in control_results)

    receipt = {
        "action": "founder_judgment_patterns_negative_proof",
        "repo": "sina-governance-ssot",
        "timestamp": utc_now(),
        "artifact_id": ARTIFACT_ID,
        "read_scope_path": str(READ_SCOPE_PATH.relative_to(ROOT)),
        "registry_status": registry_art.get("status") if registry_art else None,
        "verification_result": "PASS" if all_pass else "FAIL",
        "policy_pass": all_pass,
        "disposable_dispatch": disposable_dispatch,
        "attempted_forbidden_reader": disposable_dispatch["reader_id"],
        "expected_result": "BLOCK",
        "actual_result": primary_block["decision"],
        "block_reason": primary_block["reason"],
        "allowed_reader_controls": [
            {
                "reader": r["reader_id"],
                "expected": r["expected"],
                "actual": r["actual"],
                "pass": r["pass"],
            }
            for r in control_results
            if r["expected"] == "ALLOW"
        ],
        "all_tests": control_results,
        "sg_did_not": [
            "edit_p0_core_file",
            "modify_worker_prompts",
        ],
    }

    receipt_name = f"founder-judgment-patterns-v1-negative-proof-{utc_now().replace(':', '').replace('-', '')}.json"
    receipt_path = ROOT / "receipts" / receipt_name
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"FOUNDER_JUDGMENT_PATTERNS negative-proof @ {receipt['timestamp']}")
    print(f"  forbidden reader: {receipt['attempted_forbidden_reader']}")
    print(f"  expected: {receipt['expected_result']}  actual: {receipt['actual_result']}")
    for r in control_results:
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"  [{mark}] {r['name']}: expected={r['expected']} actual={r['actual']}")
    print(f"  ALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"  Receipt: {receipt_path}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
