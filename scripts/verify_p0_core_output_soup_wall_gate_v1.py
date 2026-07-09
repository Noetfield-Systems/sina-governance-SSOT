#!/usr/bin/env python3
"""Negative-proof gate: P0 CORE decision reasoning must not leak into worker prompts."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data/p0_core_decision_use_contract_v1.json"
ARTIFACT_ID = "founder-judgment-patterns-v1"
CONTRACT_ID = "p0-core-decision-use-contract-v1"

ALLOWED_WORKER_TASK_SPEC_KEYS = frozenset(
    {
        "goal",
        "files",
        "constraints",
        "done_criteria",
        "verify_method",
        "receipts_required",
        "decision_verdict",
    }
)

FORBIDDEN_LEAKAGE_MARKERS = (
    "matched_patterns",
    "reasoning_summary",
    "PATTERN 1",
    "PATTERN 2",
    "PATTERN 3",
    "PATTERN 4",
    "PATTERN 5",
    "PATTERN 6",
    "PATTERN 7",
    "PATTERN 8",
    "PATTERN 9",
    "PATTERN 10",
    "PATTERN 11",
    "founder-judgment-patterns-v1",
    "FOUNDER_JUDGMENT_PATTERNS",
    "P0 CORE",
    "Old-Lawyer Judgment",
    "harvest_proposed",
    "judgment layer",
    "in Sina's way",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate_worker_prompt_bundle(bundle: dict) -> dict:
    """BLOCK if P0 reasoning leaks; ALLOW only scoped task-spec fields."""
    forbidden_keys = {
        "matched_patterns",
        "reasoning_summary",
        "harvest_proposed",
        "harvest_note",
        "invocation_triggers",
        "lower_tier_facts",
        "p0_core_text",
        "internal_decision_analysis",
    }
    extra_keys = set(bundle.keys()) - ALLOWED_WORKER_TASK_SPEC_KEYS
    if extra_keys:
        return {
            "decision": "BLOCK",
            "blocked": True,
            "reason": f"BLOCKED_WITH_REASON: worker bundle has forbidden keys {sorted(extra_keys)}",
        }

    for key in forbidden_keys:
        if key in bundle:
            return {
                "decision": "BLOCK",
                "blocked": True,
                "reason": f"BLOCKED_WITH_REASON: forbidden P0 field in worker bundle: {key}",
            }

    high_risk_fields = ("goal", "decision_verdict")
    high_risk_markers = (
        "matched_patterns",
        "reasoning_summary",
        "PATTERN 1",
        "PATTERN 2",
        "PATTERN 3",
        "PATTERN 4",
        "PATTERN 5",
        "PATTERN 6",
        "PATTERN 7",
        "PATTERN 8",
        "PATTERN 9",
        "PATTERN 10",
        "PATTERN 11",
        "founder-judgment-patterns-v1",
        "FOUNDER_JUDGMENT_PATTERNS",
        "Old-Lawyer Judgment",
        "harvest_proposed",
        "in Sina's way",
        "judgment layer",
    )

    for field in high_risk_fields:
        text = str(bundle.get(field, "")).lower()
        for marker in high_risk_markers:
            if marker.lower() in text:
                return {
                    "decision": "BLOCK",
                    "blocked": True,
                    "reason": f"BLOCKED_WITH_REASON: P0 leakage in {field}: {marker}",
                }
        if re.search(r"pattern\s+1[01]", text):
            return {
                "decision": "BLOCK",
                "blocked": True,
                "reason": f"BLOCKED_WITH_REASON: pattern id leakage in {field}",
            }

    blob = json.dumps(bundle, ensure_ascii=False).lower()
    for marker in ("founder_judgment_patterns", "matched_patterns", "reasoning_summary"):
        if marker in blob:
            return {
                "decision": "BLOCK",
                "blocked": True,
                "reason": f"BLOCKED_WITH_REASON: P0 reasoning leakage marker detected: {marker}",
            }

    return {
        "decision": "ALLOW",
        "blocked": False,
        "reason": "worker bundle contains only scoped execution task-spec",
    }


def run_tests() -> list[dict]:
    sample_p0_output = {
        "decision": "Option B — labeling error",
        "matched_patterns": ["PATTERN 4 — Negative Proof", "PATTERN 9 — Authority from Registry"],
        "reasoning_summary": "Apply negative proof and registry authority — founder judgment layer.",
        "chosen_next_action": "Write reconciliation receipt",
        "harvest_proposed": False,
    }

    leaked_bundle = {
        "goal": "Fix receipt chain",
        "matched_patterns": sample_p0_output["matched_patterns"],
        "reasoning_summary": sample_p0_output["reasoning_summary"],
        "files": ["receipts/foo.json"],
    }

    clean_bundle = {
        "goal": "Write chronology reconciliation receipt and link audit chain",
        "files": [
            "receipts/founder-judgment-patterns-v1-chronology-reconciliation-20260704T043000Z.json",
            "data/governance_artifact_registry_v1.json",
        ],
        "constraints": ["preserve original receipts", "no P0 CORE edits", "no worker prompt changes"],
        "done_criteria": ["reconciliation receipt on disk", "registry audit pointers updated"],
        "verify_method": "python3 scripts/verify_p0_core_read_scope_gate_v1.py",
        "receipts_required": ["receipts/founder-judgment-patterns-v1-chronology-reconciliation-20260704T043000Z.json"],
        "decision_verdict": "CONTINUE — labeling error only; preserve history",
    }

    tests = [
        {
            "name": "block_p0_reasoning_in_worker_bundle",
            "bundle": leaked_bundle,
            "expected": "BLOCK",
        },
        {
            "name": "block_pattern_11_reference",
            "bundle": {
                "goal": "Harvest",
                "decision_verdict": "ESCALATE",
                "matched_patterns": ["PATTERN 11 — fabricated"],
            },
            "expected": "BLOCK",
        },
        {
            "name": "allow_scoped_task_spec_only",
            "bundle": clean_bundle,
            "expected": "ALLOW",
        },
        {
            "name": "block_founder_judgment_filename",
            "bundle": {
                "goal": "Load FOUNDER_JUDGMENT_PATTERNS_v1.md into worker",
                "files": [],
                "constraints": [],
                "done_criteria": [],
                "verify_method": "none",
                "receipts_required": [],
                "decision_verdict": "RUN",
            },
            "expected": "BLOCK",
        },
    ]

    results = []
    for t in tests:
        outcome = evaluate_worker_prompt_bundle(t["bundle"])
        actual = outcome["decision"]
        results.append(
            {
                **t,
                "actual": actual,
                "blocked": outcome["blocked"],
                "reason": outcome["reason"],
                "pass": actual == t["expected"],
            }
        )
    return results


def main() -> int:
    contract = load_json(CONTRACT_PATH)
    results = run_tests()
    all_pass = all(r["pass"] for r in results)

    receipt = {
        "schema": "p0-core-output-soup-wall-negative-proof-v1",
        "action": "p0_core_output_soup_wall_negative_proof",
        "repo": "sina-governance-ssot",
        "timestamp": utc_now(),
        "artifact_id": ARTIFACT_ID,
        "contract_id": CONTRACT_ID,
        "contract_path": str(CONTRACT_PATH.relative_to(ROOT)),
        "verification_result": "PASS" if all_pass else "FAIL",
        "policy_pass": all_pass,
        "soup_wall_rule": "P0 reasoning stays above gate; workers receive scoped task-spec only",
        "allowed_worker_task_spec_keys": sorted(ALLOWED_WORKER_TASK_SPEC_KEYS),
        "forbidden_leakage_markers_sample": list(FORBIDDEN_LEAKAGE_MARKERS[:8]),
        "tests": results,
        "expected_result": "BLOCK on P0 leakage; ALLOW on clean task-spec",
        "actual_result": "PASS" if all_pass else "FAIL",
        "sg_did_not": [
            "edit_p0_core_file",
            "modify_worker_prompts",
            "create_pattern_11",
        ],
    }

    receipt_path = ROOT / "receipts" / f"p0-core-output-soup-wall-negative-proof-{utc_stamp()}.json"
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"P0 CORE output soup-wall negative-proof @ {receipt['timestamp']}")
    for r in results:
        mark = "PASS" if r["pass"] else "FAIL"
        print(f"  [{mark}] {r['name']}: expected={r['expected']} actual={r['actual']}")
    print(f"  ALL: {'PASS' if all_pass else 'FAIL'}")
    print(f"  Receipt: {receipt_path}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
