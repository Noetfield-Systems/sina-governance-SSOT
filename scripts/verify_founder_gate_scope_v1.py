#!/usr/bin/env python3
"""Founder-gate scope checker (doctrine #139, enforced).

Law: ssot/FOUNDER_GATE_SCOPE_v1.md
An escalation to the founder is legitimate ONLY when:
  1. its reason_code is on the closed set, AND
  2. all five decision-point questions are answered "no", AND
  3. the founder packet is compressed and readable (doctrine #53).
Anything else is a MACHINE_DECISION: take the default, act, write a receipt.

Usage:
  python3 scripts/verify_founder_gate_scope_v1.py --self-test
  python3 scripts/verify_founder_gate_scope_v1.py --check escalation.json [--receipt]

Exit codes: 0 = legit founder gate. 1 = rejected (machine decision / bad packet).
            3 = malformed input.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RECEIPT_DIR = REPO_ROOT / "receipts"

# The closed set. Agents may not extend this list (that act is itself
# an authority-plane change, i.e. reason 7, i.e. a founder decision).
ALLOWED_REASON_CODES = {
    "destructive_operation": "Destructive repo or file operation",
    "production_deploy_without_authority": "Production deploy without commissioned authority",
    "money_movement": "Money movement",
    "legal_financial_commitment": "Legal or financial commitment",
    "credential_security_exposure": "Credential or security exposure",
    "irreversible_external_send": "Irreversible external send",
    "authority_plane_change": "Authority-plane change (keys, identity, permissions, HOLD)",
    "merge_l5_phase_unlock": "Merge / L5 / phase-unlock decision",
}

# Doctrine #139: if ANY of these is true, it is not a founder decision.
CHECKLIST_KEYS = (
    "ssot_resolvable",   # the SSOT or a lock doc already answers it
    "testable",          # a test or command answers it
    "has_default",       # a sane default exists
    "reversible",        # branch/config/retry can undo it
    "boundable",         # a small bounded experiment answers it
)

MACHINE_DECISION_MSG = (
    "Not a founder decision. Take the default, do the work, write a receipt. "
    "Raising this to the founder violates FOUNDER_GATE_SCOPE_v1 "
    "(P0_DISPATCH_BRAIN_RUNTIME v1.1: a block without an allowed reason is malformed)."
)


def evaluate(escalation):
    """Return (verdict, problems). verdict: LEGIT_FOUNDER_GATE | MACHINE_DECISION | MALFORMED."""
    problems = []

    reason = escalation.get("reason_code")
    checklist = escalation.get("checklist")
    packet = escalation.get("packet")

    if not isinstance(reason, str) or not isinstance(checklist, dict) or not isinstance(packet, dict):
        return "MALFORMED", ["escalation must carry reason_code (str), checklist (obj), packet (obj)"]

    missing = [k for k in CHECKLIST_KEYS if not isinstance(checklist.get(k), bool)]
    if missing:
        return "MALFORMED", ["checklist answers missing or non-boolean: " + ", ".join(missing)]

    if reason not in ALLOWED_REASON_CODES:
        problems.append(
            "reason_code '%s' is not on the closed set %s" % (reason, sorted(ALLOWED_REASON_CODES))
        )

    for key in CHECKLIST_KEYS:
        if checklist[key]:
            problems.append("checklist.%s is yes -> the machine can resolve this itself" % key)

    if problems:
        return "MACHINE_DECISION", problems

    # Reason is legitimate; now the packet must be readable (doctrine #53).
    packet_problems = []
    options = packet.get("options")
    why = packet.get("why")
    for field in ("what_happened", "recommended", "if_no_decision"):
        if not isinstance(packet.get(field), str) or not packet.get(field).strip():
            packet_problems.append("packet.%s missing" % field)
    if not isinstance(options, list) or not 2 <= len(options) <= 3:
        packet_problems.append("packet.options must list 2-3 options")
    if not isinstance(why, list) or not 1 <= len(why) <= 3:
        packet_problems.append("packet.why must be 1-3 short lines")

    if packet_problems:
        return "MACHINE_DECISION", packet_problems + [
            "reason is legitimate but the packet is not compressed/readable -> fix the packet, then re-check"
        ]

    return "LEGIT_FOUNDER_GATE", []


def write_receipt(escalation, verdict, problems):
    RECEIPT_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RECEIPT_DIR / ("founder_gate_scope_check_%s.json" % stamp)
    path.write_text(json.dumps({
        "schema": "founder_gate_scope_check_v1",
        "checked_at": stamp,
        "law": "ssot/FOUNDER_GATE_SCOPE_v1.md",
        "reason_code": escalation.get("reason_code"),
        "verdict": verdict,
        "problems": problems,
    }, indent=2) + "\n")
    return path


def self_test():
    legit = {
        "reason_code": "merge_l5_phase_unlock",
        "checklist": {k: False for k in CHECKLIST_KEYS},
        "packet": {
            "what_happened": "PR 82 is green and verified; it changes merge law.",
            "options": ["A: merge it", "B: leave it open"],
            "recommended": "A: merge it",
            "why": ["All checks pass", "Independent verify receipt exists"],
            "if_no_decision": "PR stays open; downstream wiring waits.",
        },
    }
    fake_reason = dict(legit, reason_code="pick_file_name")
    fake_default = dict(legit, checklist=dict(legit["checklist"], has_default=True))
    jargon_packet = dict(legit, packet=dict(legit["packet"], why=["a", "b", "c", "d", "e"]))
    malformed = {"reason_code": "money_movement", "checklist": {"testable": False}, "packet": {}}

    cases = [
        ("legit merge gate", legit, "LEGIT_FOUNDER_GATE"),
        ("invented gate (reason off-list)", fake_reason, "MACHINE_DECISION"),
        ("invented gate (default exists)", fake_default, "MACHINE_DECISION"),
        ("legit reason, uncompressed packet", jargon_packet, "MACHINE_DECISION"),
        ("malformed escalation", malformed, "MALFORMED"),
    ]
    failures = 0
    for name, esc, expected in cases:
        verdict, _ = evaluate(esc)
        ok = verdict == expected
        failures += 0 if ok else 1
        print("%s %s -> %s (expected %s)" % ("PASS" if ok else "FAIL", name, verdict, expected))
    print("self-test: %d/%d passed" % (len(cases) - failures, len(cases)))
    return 1 if failures else 0


def main():
    ap = argparse.ArgumentParser(description="Founder-gate scope checker (doctrine #139)")
    ap.add_argument("--check", metavar="FILE", help="escalation JSON to validate")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--receipt", action="store_true", help="write a receipt for the verdict")
    args = ap.parse_args()

    if args.self_test:
        sys.exit(self_test())
    if not args.check:
        ap.print_help()
        sys.exit(3)

    try:
        escalation = json.loads(Path(args.check).read_text())
    except (OSError, ValueError) as exc:
        print("MALFORMED: cannot read escalation JSON: %s" % exc)
        sys.exit(3)

    verdict, problems = evaluate(escalation)
    print(verdict)
    if verdict == "LEGIT_FOUNDER_GATE":
        print("This is one of the eight real founder gates. Raise the packet as written.")
    elif verdict == "MACHINE_DECISION":
        print(MACHINE_DECISION_MSG)
    for p in problems:
        print(" - " + p)
    if args.receipt:
        print("receipt: %s" % write_receipt(escalation, verdict, problems))
    sys.exit(0 if verdict == "LEGIT_FOUNDER_GATE" else 1 if verdict == "MACHINE_DECISION" else 3)


if __name__ == "__main__":
    main()
