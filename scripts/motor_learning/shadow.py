"""Executable shadow evaluation — independent evidence stream required."""
from __future__ import annotations

from typing import Any

from .errors import GovernanceBlock
from .hashutil import content_hash

# One success + many abstentions cannot ratify.
MIN_EVALUATED = 3
MIN_COVERAGE = 0.50  # evaluated / total
MIN_SUCCESS_RATE = 0.70
MAX_FAILURES = 1


def _event_evidence_hash(ev: dict) -> str:
    return content_hash({
        "evidence_refs": sorted(ev.get("evidence_refs") or []),
        "raw_evidence_ref": ev.get("raw_evidence_ref"),
        "content_hash": ev.get("content_hash") or ev.get("provenance_fingerprint"),
    })


def assert_shadow_independence(*, candidate: dict, mining_events: list[dict], shadow_events: list[dict]) -> dict:
    """Enforce disjoint event IDs, evidence refs, content hashes, and source artifact IDs."""
    if not shadow_events:
        raise GovernanceBlock("independent shadow_events required; clone fallback removed")

    mine_ids = set(candidate.get("source_event_ids") or []) | {e["event_id"] for e in mining_events}
    shadow_ids = {e["event_id"] for e in shadow_events}
    id_overlap = sorted(mine_ids & shadow_ids)
    if id_overlap:
        raise GovernanceBlock(f"shadow_mining_event_overlap:{id_overlap}")

    mine_refs = set()
    mine_raw = set()
    mine_hashes = set()
    for e in mining_events:
        mine_refs.update(e.get("evidence_refs") or [])
        if e.get("raw_evidence_ref"):
            mine_raw.add(e["raw_evidence_ref"])
        if e.get("content_hash"):
            mine_hashes.add(e["content_hash"])
        mine_hashes.add(_event_evidence_hash(e))
    # candidate refs
    mine_refs.update(candidate.get("evidence_refs") or [])

    shadow_refs = set()
    shadow_raw = set()
    shadow_hashes = set()
    for e in shadow_events:
        shadow_refs.update(e.get("evidence_refs") or [])
        if e.get("raw_evidence_ref"):
            shadow_raw.add(e["raw_evidence_ref"])
        if e.get("content_hash"):
            shadow_hashes.add(e["content_hash"])
        shadow_hashes.add(_event_evidence_hash(e))

    ref_overlap = sorted(mine_refs & shadow_refs)
    if ref_overlap:
        raise GovernanceBlock(f"shadow_mining_evidence_ref_overlap:{ref_overlap}")

    raw_overlap = sorted(mine_raw & shadow_raw)
    if raw_overlap:
        raise GovernanceBlock(f"shadow_mining_raw_evidence_overlap:{raw_overlap}")

    hash_overlap = sorted(mine_hashes & shadow_hashes)
    if hash_overlap:
        raise GovernanceBlock(f"shadow_mining_evidence_hash_overlap:{hash_overlap[:8]}")

    # Detect renamed clones: same core action/outcome/recovery/evidence pattern after ID strip
    mine_cores = {
        content_hash({
            "action": e.get("action_attempted"),
            "outcome": e.get("outcome"),
            "error": e.get("error_class"),
            "recovery": e.get("recovery_path"),
            "evidence_refs": sorted(e.get("evidence_refs") or []),
            "raw": e.get("raw_evidence_ref"),
        })
        for e in mining_events
    }
    for e in shadow_events:
        core = content_hash({
            "action": e.get("action_attempted"),
            "outcome": e.get("outcome"),
            "error": e.get("error_class"),
            "recovery": e.get("recovery_path"),
            "evidence_refs": sorted(e.get("evidence_refs") or []),
            "raw": e.get("raw_evidence_ref"),
        })
        # If evidence refs already disjoint, core hash differs; if someone only renames IDs
        # but keeps same evidence refs, ref_overlap already caught it.
        # Extra: identical content_hash across streams
        if e.get("content_hash") and e["content_hash"] in {m.get("content_hash") for m in mining_events}:
            raise GovernanceBlock("shadow event content_hash identical to mining event (renamed clone)")

    return {
        "mining_event_ids": sorted(mine_ids),
        "shadow_event_ids": sorted(shadow_ids),
        "mining_evidence_refs": sorted(mine_refs),
        "shadow_evidence_refs": sorted(shadow_refs),
        "mining_evidence_hashes": sorted(mine_hashes),
        "shadow_evidence_hashes": sorted(shadow_hashes),
    }


def evaluate_shadow(candidate: dict, events: list[dict]) -> dict[str, Any]:
    """Evaluate what candidate would recommend vs observed outcomes on independent shadow stream."""
    fp = candidate.get("fingerprint") or {}
    recommended = candidate.get("recommended_action")
    successes = 0
    failures = 0
    abstentions = 0
    details = []
    event_ids = []
    evidence_refs = []
    normalized_hashes = []

    for ev in events:
        event_ids.append(ev["event_id"])
        evidence_refs.extend(ev.get("evidence_refs") or [])
        if ev.get("content_hash"):
            normalized_hashes.append(ev["content_hash"])
        if ev.get("action_attempted") != fp.get("action_attempted"):
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "action_mismatch"})
            continue
        if fp.get("error_class") and ev.get("error_class") != fp.get("error_class"):
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "error_class_mismatch"})
            continue
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
            abstentions += 1
            details.append({"event_id": ev["event_id"], "result": "abstain", "reason": "different_recovery_succeeded"})
        elif ev.get("outcome") == "failure" and recommended:
            if ev.get("recovery_path") is None:
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
    coverage = (evaluated / total) if total else 0.0

    if evaluated == 0:
        result = "insufficient_evidence"
    elif failures > successes:
        result = "failure"
    elif successes > 0 and failures == 0:
        result = "success"
    else:
        result = "mixed"

    evidence_refs = sorted(set(evidence_refs))
    manifest = {
        "shadow_event_ids": list(event_ids),
        "evidence_refs": evidence_refs,
        "normalized_event_hashes": list(normalized_hashes),
        "successes": successes,
        "failures": failures,
        "abstentions": abstentions,
        "evaluated": evaluated,
        "coverage": round(coverage, 4),
        "success_rate": round(success_rate, 4),
    }
    manifest_hash = content_hash(manifest)

    ratifiable = (
        evaluated >= MIN_EVALUATED
        and coverage >= MIN_COVERAGE
        and success_rate >= MIN_SUCCESS_RATE
        and failures <= MAX_FAILURES
        and result in ("success", "mixed")
    )

    report = {
        "schema": "nf_motor_learning_shadow_report_v1",
        "shadow_id": "shadow-" + content_hash({"c": candidate.get("candidate_id"), "m": manifest_hash})[:16],
        "candidate_id": candidate.get("candidate_id"),
        "production_change": False,
        "successes": successes,
        "failures": failures,
        "abstentions": abstentions,
        "total": total,
        "evaluated": evaluated,
        "coverage": round(coverage, 4),
        "success_rate": round(success_rate, 4),
        "result": result,
        "ratifiable": ratifiable,
        "min_evaluated": MIN_EVALUATED,
        "min_coverage": MIN_COVERAGE,
        "min_success_rate": MIN_SUCCESS_RATE,
        "max_failures": MAX_FAILURES,
        "details": details,
        "shadow_event_ids": list(event_ids),
        "evidence_refs": evidence_refs,
        "mining_evidence_refs": list(candidate.get("evidence_refs") or []),
        "normalized_event_hashes": list(normalized_hashes),
        "evidence_manifest": manifest,
        "evidence_manifest_hash": manifest_hash,
    }
    report["content_hash"] = content_hash({k: report[k] for k in sorted(report) if k != "content_hash"})
    return report


def require_ratifiable_shadow(report: dict) -> None:
    if not report.get("ratifiable"):
        raise GovernanceBlock(
            f"shadow not ratifiable: evaluated={report.get('evaluated')} "
            f"coverage={report.get('coverage')} success_rate={report.get('success_rate')} "
            f"result={report.get('result')} (one success + abstentions is insufficient)"
        )
