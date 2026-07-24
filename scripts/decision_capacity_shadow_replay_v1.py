#!/usr/bin/env python3
"""Decision Capacity Phase B — structural shadow replay into Learning Organ queue.

Advances OPEN policy candidates from draft → shadow → structural pass.
Does NOT promote live priors (GATED — NF-MOTOR-LEARNING-ORGAN-V1).
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

from lib.decision_capacity_v1 import CLASS_POLICY_TEMPLATES, DECISION_CLASSES  # noqa: E402

COVERAGE_PATH = ROOT / "data" / "decision_class_policy_coverage_v1.json"
LEARNING_DIR = ROOT / "receipts" / "learning"
SHADOW_DIR = LEARNING_DIR / "decision-capacity-shadow"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def structural_replay_checks(candidate_body: dict, decision_class: str) -> list[str]:
    """Deterministic policy-shape replay — independent of LLM."""
    fails: list[str] = []
    if decision_class not in DECISION_CLASSES and decision_class != "UNKNOWN":
        fails.append("unknown_decision_class")
    for key in ("when", "select", "limits", "verify", "escalate_when"):
        if key not in candidate_body:
            fails.append(f"missing_{key}")
    verify = candidate_body.get("verify")
    if not isinstance(verify, list) or len(verify) < 1:
        fails.append("verify_empty")
    escalate = candidate_body.get("escalate_when")
    if not isinstance(escalate, list) or len(escalate) < 1:
        fails.append("escalate_when_empty")
    limits = candidate_body.get("limits") or {}
    if not isinstance(limits, dict):
        fails.append("limits_not_object")
    else:
        if "max_fanout" in limits and int(limits["max_fanout"]) > 0 and decision_class in {
            "EMAIL_DRAFT",
            "WEBPAGE_CHANGE",
            "WEBPAGE_REPAIR",
        }:
            fails.append("fanout_must_be_zero_for_class")
    # Template fidelity: required verify predicates from class template must remain
    template = CLASS_POLICY_TEMPLATES.get(decision_class) or CLASS_POLICY_TEMPLATES["UNKNOWN"]
    required = set(template.get("verify") or [])
    have = set(verify or [])
    missing = sorted(required - have)
    if missing:
        fails.append("missing_template_verify:" + ",".join(missing))
    return fails


def iter_enqueue_packets(paths: list[Path]) -> list[tuple[Path, dict]]:
    out: list[tuple[Path, dict]] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            row = _load_json(path)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        if row.get("policy_candidate") or row.get("schema") in {
            "noetfield.decision_capacity_replay_enqueue.v1",
            "motor_learning_organ.learning_record_draft.v1",
        }:
            out.append((path, row))
    return out


def normalize_packet(row: dict) -> dict | None:
    """Accept enqueue fixture or bare learning_record draft."""
    if row.get("policy_candidate") and row.get("learning_record"):
        return row
    if row.get("schema") == "motor_learning_organ.learning_record_draft.v1" or (
        row.get("source_event") == "MISSING_DECISION_CAPACITY" and row.get("proposed_correction")
    ):
        corr = row.get("proposed_correction") or {}
        return {
            "schema": "noetfield.decision_capacity_replay_enqueue.v1",
            "incident_type": "MISSING_DECISION_CAPACITY",
            "policy_candidate": {
                "schema": "noetfield.decision_policy_candidate.v1",
                "candidate_id": corr.get("candidate_id"),
                "proposal_id": row.get("record_id"),
                "decision_class": corr.get("decision_class") or "UNKNOWN",
                "policy_version": corr.get("policy_version"),
                "body": corr.get("body") or {},
                "replay_status": "queued",
                "learning_record_id": row.get("record_id"),
                "mutation_class": "OPEN",
            },
            "learning_record": row,
            "proposal": {"status": "draft"},
            "gap": {"decision_class": corr.get("decision_class") or "UNKNOWN"},
        }
    return None


def shadow_one(packet: dict) -> dict:
    cand = packet.get("policy_candidate") or {}
    body = cand.get("body") or {}
    dc = str(cand.get("decision_class") or packet.get("gap", {}).get("decision_class") or "UNKNOWN")
    fails = structural_replay_checks(body, dc)
    learning = dict(packet.get("learning_record") or {})
    cand_out = dict(cand)
    if fails:
        cand_out["replay_status"] = "failed"
        learning["status"] = "rejected"
        learning["ssot_consistency_check"] = "structural_replay_failed"
        learning["replay_failures"] = fails
        verdict = "SHADOW_REPLAY_FAILED"
    else:
        cand_out["replay_status"] = "shadow"
        learning["status"] = "proposed"
        learning["ssot_consistency_check"] = "structural_replay_passed"
        learning["critic_reviewed"] = False
        learning["shadow_at"] = _now()
        # structural pass advances to passed-for-shadow queue (still not live)
        cand_out["replay_status"] = "passed"
        verdict = "SHADOW_REPLAY_PASSED"
    return {
        "verdict": verdict,
        "decision_class": dc,
        "policy_candidate": cand_out,
        "learning_record": learning,
        "failures": fails,
        "mutation_class_promote": "GATED",
        "live_promote": False,
    }


def bump_coverage(decision_class: str, policy_version: str | None, *, passed: bool) -> dict:
    cov = _load_json(COVERAGE_PATH) if COVERAGE_PATH.exists() else {"classes": {}}
    classes = cov.setdefault("classes", {})
    row = classes.setdefault(
        decision_class,
        {"coverage": 0.0, "active_policy_version": None, "shadow_policy_versions": [], "status": "capacity_gap_open"},
    )
    if passed and policy_version:
        shadows = list(row.get("shadow_policy_versions") or [])
        if policy_version not in shadows:
            shadows.append(policy_version)
        row["shadow_policy_versions"] = shadows
        # Shadow pass raises coverage toward 0.7 ceiling until GATED promote
        row["coverage"] = round(min(0.7, float(row.get("coverage") or 0) + 0.05), 3)
        row["status"] = "shadow_policy_present"
    cov["updated_at"] = _now()
    COVERAGE_PATH.write_text(json.dumps(cov, indent=2) + "\n", encoding="utf-8")
    return cov


def run(*, inputs: list[Path], write_receipt: bool) -> dict:
    packets = iter_enqueue_packets(inputs)
    results = []
    for path, raw in packets:
        packet = normalize_packet(raw)
        if not packet:
            continue
        result = shadow_one(packet)
        result["source_path"] = str(path)
        try:
            result["source_path"] = str(path.relative_to(ROOT))
        except ValueError:
            pass
        if result["verdict"] == "SHADOW_REPLAY_PASSED":
            bump_coverage(
                str(result["decision_class"]),
                (result["policy_candidate"] or {}).get("policy_version"),
                passed=True,
            )
        # Persist advanced learning record beside shadows
        SHADOW_DIR.mkdir(parents=True, exist_ok=True)
        lr = result["learning_record"]
        rid = lr.get("record_id") or "unknown"
        out_lr = SHADOW_DIR / f"{rid}.shadow.json"
        out_lr.write_text(
            json.dumps(
                {
                    "schema": "noetfield.decision_capacity_shadow_result.v1",
                    "at": _now(),
                    **result,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        result["shadow_receipt"] = str(out_lr.relative_to(ROOT))
        results.append(result)

    summary = {
        "schema": "noetfield.decision_capacity_phase_b_replay_v1",
        "at": _now(),
        "loop_id": "decision_capacity_shadow_replay_v1",
        "trigger_host": "cloud",
        "inputs": [str(p) for p, _ in packets],
        "processed": len(results),
        "passed": sum(1 for r in results if r["verdict"] == "SHADOW_REPLAY_PASSED"),
        "failed": sum(1 for r in results if r["verdict"] == "SHADOW_REPLAY_FAILED"),
        "results": results,
        "live_promote": False,
        "verdict": "PASS_PHASE_B_SHADOW"
        if results and all(r["verdict"] == "SHADOW_REPLAY_PASSED" for r in results)
        else ("PASS_PHASE_B_PARTIAL" if results else "PASS_PHASE_B_NO_INPUT"),
    }
    if write_receipt:
        LEARNING_DIR.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = LEARNING_DIR / f"decision-capacity-phase-b-replay-{stamp}.json"
        out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        summary["receipt_path"] = str(out.relative_to(ROOT))
    return summary


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--input",
        type=Path,
        nargs="*",
        default=[],
        help="Enqueue JSON paths (default: receipts/learning/decision-capacity*.json)",
    )
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    inputs = list(args.input)
    if not inputs:
        inputs = sorted(LEARNING_DIR.glob("decision-capacity*.json"))
        inputs = [p for p in inputs if "phase-b-replay" not in p.name and "shadow" not in str(p)]
    summary = run(inputs=inputs, write_receipt=args.write_receipt)
    print(json.dumps(summary, indent=2))
    return 0 if summary["verdict"].startswith("PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
