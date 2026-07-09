#!/usr/bin/env python3
"""P0-PGR Packet Lint v1 (Phase-0).

Validates prompt packets against P0_PROMPT_PACKET_SCHEMA_v1.json (internal
version 1.1, delivery-aware) plus semantic rules the schema cannot express.

RUNTIME_CONTINUITY_LAW_v1: a malformed packet NEVER freezes the lane.
Verdict is PASS or REPAIR_CANDIDATE — exit code is 0 either way; nonzero
exit means the linter itself crashed, nothing else.
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


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("packet", type=Path)
    args = ap.parse_args()
    packet = json.loads(args.packet.read_text())
    result = lint_packet(packet)
    print(json.dumps(result, indent=2))
    return 0  # continuity: REPAIR_CANDIDATE is a result, not a failure


if __name__ == "__main__":
    sys.exit(main())
