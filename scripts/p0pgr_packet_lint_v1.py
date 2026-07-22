#!/usr/bin/env python3
"""P0-PGR Packet Lint v1 (Phase-0) + HDIR prompt packet / Loop Engineer contract.

Validates:
  - P0 prompt packets against P0_PROMPT_PACKET_SCHEMA_v1.json (default / --kind p0pgr)
  - HDIR compiled packets (--kind hdir) for runtime-shaped fields
  - Loop Engineer contracts (--kind loop_engineer)

RUNTIME_CONTINUITY_LAW_v1 (P0-PGR only): a malformed P0 packet NEVER freezes the lane.
Verdict is PASS or REPAIR_CANDIDATE — exit code is 0 either way; nonzero
exit means the linter itself crashed, nothing else.

For --kind hdir|loop_engineer: exit 1 on invalid (runtime reject mirror).
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_PATH = ROOT / "p0-pgr" / "P0_PROMPT_PACKET_SCHEMA_v1.json"
P0_CORE_DIR = (
    ROOT / "SG-Canonical-Library" / "noetfield-library"
    / "P0-FOUNDATION-SPINE" / "P0-CORE"
)

HARD_BLOCK_REASONS = {
    "destructive_action", "production_deploy_without_authority",
    "money_movement", "legal_financial_commitment",
    "credential_or_security_exposure", "irreversible_external_send",
    "authority_change", "merge_L5_phase_unlock",
}
DELIVERY_REQUIRED = [
    "execution_mode", "delivery_route", "target_executor", "repo",
    "worktree_required", "local_secrets_required", "cloud_safe",
    "fallback_route", "quality_handling",
]
AUTHORITY_CHANGE_HINTS = re.compile(
    r"\b(merge to main|flip authority|authority change|phase unlock|L5)\b", re.I
)
WORKER_TEXT_FIELDS = ("context_summary", "task")

HDIR_REQUIRED_LISTS = (
    "evidence_refs",
    "constraints",
    "allowed_tools",
    "never_rules",
    "acceptance_criteria",
    "stop_conditions",
)
HDIR_SCHEMA = "hdir.prompt_packet.v1"
LOOP_SCHEMA = "goal.loop_engineer.v1"


def p0_fingerprints() -> list[str]:
    """Distinctive verbatim lines from P0-CORE docs (leak detector)."""
    prints: list[str] = []
    if P0_CORE_DIR.is_dir():
        for f in sorted(P0_CORE_DIR.glob("*.md")):
            for line in f.read_text(errors="replace").splitlines():
                line = line.strip().lstrip("#>-* ").strip()
                if len(line) >= 60:
                    prints.append(line)
    return prints


def lint_packet(packet: dict) -> dict:
    reasons: list[str] = []
    degraded = False

    # 1. JSON Schema validation (structural + conditionals)
    try:
        from jsonschema import Draft202012Validator
        schema = json.loads(SCHEMA_PATH.read_text())
        for err in Draft202012Validator(schema).iter_errors(packet):
            reasons.append(f"schema: {err.message}")
    except ImportError:
        # Continuity: degrade to built-in structural checks, tag the gap
        # (checks 2-7 below still run; a clean packet lints PASS-degraded,
        # it is not stopped for a missing dev dependency).
        degraded = True

    # 2. Delivery fields present (explicit, even when schema caught it)
    for field in DELIVERY_REQUIRED:
        if field not in packet:
            msg = f"missing:{field}"
            if msg not in reasons and not any(field in r for r in reasons):
                reasons.append(f"missing required delivery field: {field}")

    qh = packet.get("quality_handling") or {}

    # 3. HARD_BLOCK only with allowed reason
    for reason in qh.get("hard_block_allowed_reasons", []):
        if reason not in HARD_BLOCK_REASONS:
            reasons.append(f"hard_block reason not in allowed enum: {reason}")

    # 4. CLOUD_ONLY invalid when cloud_safe is false
    if packet.get("cloud_safe") is False and packet.get("execution_mode") == "CLOUD_ONLY":
        reasons.append("cloud_safe=false cannot use execution_mode CLOUD_ONLY")

    # 5. HYBRID_MAC needs canonical_path + mac_required_reason
    if packet.get("execution_mode") == "HYBRID_MAC":
        if not packet.get("canonical_path"):
            reasons.append("HYBRID_MAC packet missing canonical_path")
        if not packet.get("mac_required_reason"):
            reasons.append("HYBRID_MAC packet missing mac_required_reason")

    # 6. deploy / merge / authority-change require FOUNDER_ONLY
    text = " ".join(str(packet.get(f, "")) for f in WORKER_TEXT_FIELDS)
    if packet.get("authority_scope") == "deploy" and packet.get("execution_mode") != "FOUNDER_ONLY":
        reasons.append("authority_scope deploy requires execution_mode FOUNDER_ONLY")
    if AUTHORITY_CHANGE_HINTS.search(text) and packet.get("execution_mode") != "FOUNDER_ONLY":
        reasons.append("merge/L5/authority-change task requires FOUNDER_ONLY gate")

    # 7. P0 leakage into worker prompt text
    for fp in p0_fingerprints():
        if fp in text:
            reasons.append(f"P0 leakage: worker prompt contains P0-CORE line: {fp[:60]}...")
            break

    verdict = "PASS" if not reasons else "REPAIR_CANDIDATE"
    return {
        "schema": "p0pgr-lint-result-v1",
        "packet_id": packet.get("id", "UNKNOWN"),
        "verdict": verdict,
        "degraded_mode": degraded,
        "reasons": reasons,
        "hard_block_configured": bool(qh.get("hard_block_allowed_reasons")),
        "runtime_action": "continue",  # continuity law: never lane STOP
    }


def lint_hdir_packet(packet: dict) -> dict:
    reasons: list[str] = []
    if packet.get("schema") != HDIR_SCHEMA:
        reasons.append("schema_version_mismatch")
    if not isinstance(packet.get("role"), str) or not str(packet.get("role")).strip():
        reasons.append("role_required")
    obj = packet.get("exact_objective")
    if not isinstance(obj, str) or len(obj.strip()) < 8:
        reasons.append("exact_objective_too_short")
    for key in HDIR_REQUIRED_LISTS:
        val = packet.get(key)
        if not isinstance(val, list) or len(val) < 1:
            reasons.append(f"{key}_required")
    if not isinstance(packet.get("output_schema"), dict):
        reasons.append("output_schema_required")
    never = packet.get("never_rules") or []
    if isinstance(never, list) and not any("NEVER" in str(r).upper() for r in never):
        reasons.append("never_rules_must_include_NEVER")
    ok = not reasons
    return {
        "schema": "hdir-prompt-packet-lint-result-v1",
        "verdict": "PASS" if ok else "REJECT",
        "reasons": reasons,
        "runtime_action": "continue" if ok else "reject_packet",
        "packet_hash_required_on_attempt": True,
        "packet_hash_required_on_receipt": True,
    }


def lint_loop_engineer(contract: dict) -> dict:
    reasons: list[str] = []
    if contract.get("schema") != LOOP_SCHEMA:
        reasons.append("schema_mismatch")
    if not isinstance(contract.get("loop_id"), str) or not str(contract.get("loop_id")).strip():
        reasons.append("loop_id_required")
    max_i = contract.get("max_iterations")
    if not isinstance(max_i, (int, float)) or max_i < 1:
        reasons.append("max_iterations_invalid")
    retry = contract.get("retry_limits") or {}
    if not isinstance(retry, dict) or "max_child_run_failures" not in retry or "max_repair_purposes" not in retry:
        reasons.append("retry_limits_required")
    deadman = contract.get("deadman") or {}
    hb = deadman.get("heartbeat_interval_seconds")
    stale = deadman.get("stale_after_seconds")
    if not isinstance(hb, (int, float)) or not isinstance(stale, (int, float)) or stale < 2 * hb:
        reasons.append("deadman_invalid")
    checkpoint = contract.get("checkpoint") or {}
    if checkpoint.get("on_child_run_complete") is not True or checkpoint.get("before_approval") is not True:
        reasons.append("checkpoint_required")
    if not isinstance(contract.get("approval_points"), list) or not contract.get("approval_points"):
        reasons.append("approval_points_required")
    if not isinstance(contract.get("stop_conditions"), list) or not contract.get("stop_conditions"):
        reasons.append("stop_conditions_required")
    ok = not reasons
    return {
        "schema": "loop-engineer-lint-result-v1",
        "verdict": "PASS" if ok else "REJECT",
        "reasons": reasons,
        "runtime_action": "continue" if ok else "reject_contract",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet", type=Path)
    ap.add_argument(
        "--kind",
        choices=("p0pgr", "hdir", "loop_engineer"),
        default="p0pgr",
        help="Packet/contract kind (default: p0pgr continuity lint)",
    )
    args = ap.parse_args()
    packet = json.loads(args.packet.read_text())
    if args.kind == "hdir":
        result = lint_hdir_packet(packet)
        print(json.dumps(result, indent=2))
        return 0 if result["verdict"] == "PASS" else 1
    if args.kind == "loop_engineer":
        result = lint_loop_engineer(packet)
        print(json.dumps(result, indent=2))
        return 0 if result["verdict"] == "PASS" else 1
    result = lint_packet(packet)
    print(json.dumps(result, indent=2))
    return 0  # continuity: REPAIR_CANDIDATE is a result, not a failure


if __name__ == "__main__":
    sys.exit(main())
