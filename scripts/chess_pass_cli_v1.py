#!/usr/bin/env python3
"""
chess_pass_cli.py

Lightweight local helper for agents.
Reads a JSON object with mission/raw_move/protected_assets/explicit_removals
and emits a CHESS_PASS skeleton with likely risks.

This tool is heuristic. It is not a blocker.
"""

import json
import sys
from datetime import datetime, timezone

RISK_WORDS = [
    "clean", "minimal", "simplify", "polish", "streamline",
    "reduce clutter", "remove conflicting", "modernize", "make classy"
]

IRREVERSIBLE_HINTS = [
    "delete", "remove feature", "expose", "publish deck", "send email",
    "sign", "spend", "equity", "control", "legal claim", "regulatory claim",
    "destructive migration", "transfer"
]

DEFAULT_PATCH = (
    "Preserve existing working capabilities. "
    "Use REMOVE ONLY for exact removals. "
    "Patch ambiguous wording before execution."
)

def main():
    if len(sys.argv) > 1:
        raw = open(sys.argv[1], "r", encoding="utf-8").read()
    else:
        raw = sys.stdin.read()
    data = json.loads(raw)

    move = data.get("raw_move") or data.get("move") or data.get("mission", "")
    text = move.lower()

    likely_misread = []
    second_move_risk = []
    third_move_consequence = []

    if any(w in text for w in RISK_WORDS):
        likely_misread.append("Agent may treat clarity/polish wording as permission to delete capability.")
        second_move_risk.append("Working CTAs/routes/features may be removed or hidden.")
        third_move_consequence.append("User flow or commercial funnel may regress after deploy.")

    if any(w in text for w in IRREVERSIBLE_HINTS):
        action = "ASK_IF_IRREVERSIBLE"
    elif likely_misread:
        action = "PROCEED_WITH_PATCH"
    else:
        action = "PROCEED"

    protected = data.get("protected_assets", [])
    explicit_removals = data.get("explicit_removals", [])

    patch = data.get("patch_before_execution") or DEFAULT_PATCH
    if protected:
        patch += " Preserve: " + ", ".join(protected) + "."
    if explicit_removals:
        patch += " Remove only: " + ", ".join(explicit_removals) + "."
    else:
        patch += " No removals authorized unless explicitly named."

    out = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "move": move,
        "immediate_goal": data.get("immediate_goal", ""),
        "protected_assets": protected,
        "likely_misread": likely_misread,
        "second_move_risk": second_move_risk,
        "third_move_consequence": third_move_consequence,
        "patch_before_execution": patch,
        "verification_after_execution": data.get("verification_after_execution", []),
        "action": action
    }
    print(json.dumps(out, indent=2))

if __name__ == "__main__":
    main()
