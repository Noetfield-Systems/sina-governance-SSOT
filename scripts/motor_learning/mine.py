
"""Governed pattern aggregation across signals. Produces proposal candidates only."""
from __future__ import annotations

from typing import Any

from .hashutil import content_hash


def _pattern_key(fingerprint: dict) -> str:
    """Family key excludes outcome so contradictions surface within one group."""
    key = {
        "action_attempted": fingerprint.get("action_attempted"),
        "error_class": fingerprint.get("error_class"),
        "recovery_path": fingerprint.get("recovery_path"),
        "runway": fingerprint.get("runway"),
        "repository": fingerprint.get("repository"),
        "stage": fingerprint.get("stage"),
        "loop_id": fingerprint.get("loop_id"),
    }
    return content_hash(key)


def mine_patterns(
    signals: list[dict],
    *,
    min_occurrences: int = 3,
    temporal_window: tuple[str, str] | None = None,
) -> list[dict]:
    """Group by pattern family; emit candidates only when min_occurrences met and consistent."""
    groups: dict[str, list[dict]] = {}
    for sig in signals:
        if temporal_window:
            start, end = temporal_window
            if not (start <= sig["last_seen"] <= end):
                continue
        pk = _pattern_key(sig["fingerprint"])
        groups.setdefault(pk, []).append(sig)

    candidates = []
    for pk, members in sorted(groups.items()):
        event_ids = []
        evidence = []
        first_seen = members[0]["first_seen"]
        last_seen = members[0]["last_seen"]
        outcomes = set()
        for m in members:
            event_ids.extend(m["source_event_ids"])
            evidence.extend(m["evidence_refs"])
            first_seen = min(first_seen, m["first_seen"])
            last_seen = max(last_seen, m["last_seen"])
            outcomes.add(m["observed_outcome"])
        event_ids = sorted(set(event_ids))
        evidence = sorted(set(evidence))
        contradictions = len(outcomes) > 1
        occurrence = len(event_ids)
        # Prefer success fingerprint if mixed; else first
        fp = dict(members[0]["fingerprint"])
        if "success" in outcomes and not contradictions:
            for m in members:
                if m["observed_outcome"] == "success":
                    fp = dict(m["fingerprint"])
                    break
        candidate_id = "cand-" + content_hash({"fp": pk, "events": event_ids})[:16]
        state = "OBSERVED"
        if occurrence >= min_occurrences and not contradictions:
            state = "PROPOSED"
        candidates.append({
            "schema": "nf_motor_learning_candidate_v1",
            "candidate_id": candidate_id,
            "state": state,
            "fingerprint": fp,
            "fingerprint_hash": pk,
            "occurrence_count": occurrence,
            "min_occurrences_required": min_occurrences,
            "meets_threshold": occurrence >= min_occurrences and not contradictions,
            "contradiction": contradictions,
            "outcomes_seen": sorted(outcomes),
            "source_event_ids": event_ids,
            "evidence_refs": evidence,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "scope": members[0]["scope"],
            "recommended_action": fp.get("recovery_path") or f"prefer_route_for:{fp.get('action_attempted')}",
            "expected_outcome": "success" if outcomes == {"success"} else None,
            "live_prior": False,
            "not_ratifiable_reason": (
                "contradictory_outcomes" if contradictions
                else ("insufficient_evidence" if occurrence < min_occurrences else None)
            ),
        })
    return candidates
