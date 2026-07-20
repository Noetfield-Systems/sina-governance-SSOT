
"""Executable shadow evaluation — no production side effects."""
from __future__ import annotations

from typing import Any

from .hashutil import content_hash


def evaluate_shadow(candidate: dict, events: list[dict]) -> dict[str, Any]:
    """Evaluate what candidate would recommend vs observed outcomes."""
    fp = candidate.get("fingerprint") or {}
    recommended = candidate.get("recommended_action")
    successes = 0
    failures = 0
    abstentions = 0
    details = []
    for ev in events:
        # only events matching action/error scope
        if ev.get("action_attempted") != fp.get("action_attempted"):
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "action_mismatch"})
            continue
        if fp.get("error_class") and ev.get("error_class") != fp.get("error_class"):
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "error_class_mismatch"})
            continue
        # Would candidate recovery have been applied?
        would_apply = recommended and (
            ev.get("recovery_path") == recommended
            or (ev.get("outcome") == "success" and ev.get("recovery_path") == recommended)
        )
        if would_apply and ev.get("outcome") == "success":
            successes += 1
            details.append({"event_id": ev["event_id"], "result": "success", "reason": "recovery_matched_success"})
        elif would_apply and ev.get("outcome") == "failure":
            failures += 1
            details.append({"event_id": ev["event_id"], "result": "failure", "reason": "recovery_matched_but_failed"})
        elif not would_apply and ev.get("outcome") == "success" and ev.get("recovery_path"):
            # observed success via other path — abstain
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "different_recovery_succeeded"})
        elif ev.get("outcome") == "failure" and recommended:
            # candidate suggests recovery that was not tried — count as potential
            # For shadow honesty: if recommended equals what would be next step, mark success only if fixture says so
            if ev.get("recovery_path") is None:
                # untried recommendation — abstain (cannot claim success without evidence)
                abstentions += 1
                details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "recommendation_untried"})
            else:
                failures += 1
                details.append({"event_id": ev["event_id"], "result": "failure", "reason": "other_recovery_failed"})
        else:
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "insufficient_alignment"})

    total = successes + failures + abstentions
    evaluated = successes + failures
    success_rate = (successes / evaluated) if evaluated else 0.0
    if evaluated == 0:
        result = "insufficient_evidence"
    elif failures > successes:
        result = "failure"
    elif successes > 0 and failures == 0:
        result = "success"
    else:
        result = "mixed"

    report = {
        "schema": "nf_motor_learning_shadow_report_v1",
        "shadow_id": "shadow-" + content_hash({"c": candidate.get("candidate_id"), "n": len(events)})[:16],
        "candidate_id": candidate.get("candidate_id"),
        "production_change": False,
        "successes": successes,
        "failures": failures,
        "abstentions": abstentions,
        "total": total,
        "success_rate": round(success_rate, 4),
        "result": result,
        "details": details,
        "evidence_refs": list(candidate.get("evidence_refs") or []),
    }
    return report
