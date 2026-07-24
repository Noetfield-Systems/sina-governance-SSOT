#!/usr/bin/env python3
"""Decision Capacity — MISSING_DECISION_CAPACITY → proposal → policy candidate → Learning Organ draft."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

DECISION_CLASSES = frozenset(
    {
        "EMAIL_DRAFT",
        "WEBPAGE_CHANGE",
        "CRAWL_AND_EXTRACT",
        "DATA_SYNC",
        "DEPLOYMENT",
        "WEBPAGE_REPAIR",
        "UNKNOWN",
    }
)

# Human-tax / breaker signal → founder micro-choice that should become policy
EVENT_TO_CHOICE = {
    "GOAL_RESTATEMENT": "restate_goal_intent",
    "SCOPE_RESTATEMENT": "redefine_scope",
    "MANUAL_CORRECTION": "select_target_files",
    "MANUAL_ROLLBACK": "choose_retry_or_stop",
    "MANUAL_RESTART": "choose_retry_or_stop",
    "FALSE_DONE_REJECTION": "choose_verification_method",
    "TOOL_CANCELLATION": "select_executor",
    "OUT_OF_SCOPE_REPAIR": "select_target_files",
    "MANUAL_VERIFICATION": "choose_verification_method",
}

CLASS_POLICY_TEMPLATES: dict[str, dict[str, Any]] = {
    "WEBPAGE_CHANGE": {
        "when": {"task_type": "webpage_change", "risk": "low_or_medium"},
        "select": {
            "workflow": "deterministic_web_change_v1",
            "executor": "cheapest_passing_executor",
        },
        "limits": {"max_files": 5, "max_attempts": 2, "max_fanout": 0},
        "verify": [
            "build_passes",
            "target_issue_absent",
            "unrelated_pages_unchanged",
            "receipt_written",
        ],
        "escalate_when": [
            "positioning_change_detected",
            "protected_file_required",
            "two_distinct_plans_failed",
        ],
    },
    "WEBPAGE_REPAIR": {
        "when": {"task_type": "webpage_repair", "risk": "low_or_medium"},
        "select": {
            "workflow": "deterministic_web_repair_v1",
            "executor": "cheapest_passing_executor",
        },
        "limits": {"max_files": 5, "max_attempts": 2, "max_fanout": 0},
        "verify": [
            "build_passes",
            "visual_diff_present",
            "target_issue_absent",
            "unrelated_pages_unchanged",
        ],
        "escalate_when": [
            "positioning_change_detected",
            "protected_file_required",
            "two_distinct_plans_failed",
        ],
    },
    "EMAIL_DRAFT": {
        "when": {"task_type": "email_draft", "risk": "low"},
        "select": {"workflow": "deterministic_email_draft_v1", "executor": "cheap_writer"},
        "limits": {"max_files": 1, "max_attempts": 2, "max_fanout": 0},
        "verify": ["draft_exists", "no_send_without_owner", "receipt_written"],
        "escalate_when": ["legal_claim_detected", "external_send_requested"],
    },
    "CRAWL_AND_EXTRACT": {
        "when": {"task_type": "crawl_and_extract", "risk": "low_or_medium"},
        "select": {"workflow": "deterministic_crawl_v1", "executor": "crawl_node"},
        "limits": {"max_attempts": 2, "max_fanout": 0, "max_minutes": 30},
        "verify": ["artifact_json_valid", "source_urls_recorded", "receipt_written"],
        "escalate_when": ["authwall_detected", "robots_block"],
    },
    "DATA_SYNC": {
        "when": {"task_type": "data_sync", "risk": "medium"},
        "select": {"workflow": "deterministic_data_sync_v1", "executor": "sync_node"},
        "limits": {"max_attempts": 2, "max_fanout": 0},
        "verify": ["row_count_delta_recorded", "checksum_present", "receipt_written"],
        "escalate_when": ["schema_drift", "destructive_write_required"],
    },
    "DEPLOYMENT": {
        "when": {"task_type": "deployment", "risk": "high"},
        "select": {"workflow": "deterministic_deploy_v1", "executor": "deploy_node"},
        "limits": {"max_attempts": 1, "max_fanout": 0},
        "verify": ["health_ok", "release_sha_match", "receipt_written"],
        "escalate_when": ["secret_change_required", "production_authority_missing"],
    },
    "UNKNOWN": {
        "when": {"task_type": "unknown", "risk": "unknown"},
        "select": {"workflow": "bounded_diagnose_v1", "executor": "critic"},
        "limits": {"max_attempts": 1, "max_fanout": 0},
        "verify": ["incident_packet_written", "capacity_gap_named"],
        "escalate_when": ["novel_decision_class"],
    },
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def map_events_to_founder_choices(event_types: Sequence[str]) -> list[str]:
    choices: list[str] = []
    seen: set[str] = set()
    for et in event_types:
        choice = EVENT_TO_CHOICE.get(et)
        if choice and choice not in seen:
            seen.add(choice)
            choices.append(choice)
    return choices


def detect_capacity_gap(
    *,
    decision_class: str,
    event_types: Sequence[str],
    existing_policy_coverage: float = 0.0,
    min_occurrences: int = 2,
    task_id: str = "",
    human_tax_units: float = 0.0,
    evidence_refs: Sequence[str] | None = None,
) -> dict[str, Any] | None:
    """Return a capacity gap when founder micro-choices repeat without policy coverage."""
    dc = decision_class if decision_class in DECISION_CLASSES else "UNKNOWN"
    choices = map_events_to_founder_choices(event_types)
    taxish = [e for e in event_types if e in EVENT_TO_CHOICE]
    occurrences = max(len(taxish), len(choices))
    if occurrences < min_occurrences and existing_policy_coverage >= 0.8:
        return None
    if occurrences < min_occurrences and existing_policy_coverage > 0.5:
        return None
    if not choices:
        return None
    if existing_policy_coverage >= 0.95 and occurrences < 4:
        return None
    return {
        "schema": "noetfield.decision_capacity_gap.v1",
        "gap_id": _id("dcg"),
        "incident_type": "MISSING_DECISION_CAPACITY",
        "decision_class": dc,
        "repeated_founder_choices": choices,
        "occurrences": max(occurrences, min_occurrences),
        "existing_policy_coverage": float(max(0.0, min(1.0, existing_policy_coverage))),
        "proposed_action": "CREATE_OR_EXTEND_POLICY",
        "work_status": "FROZEN",
        "task_id": task_id or None,
        "human_tax_units": human_tax_units,
        "evidence_refs": list(evidence_refs or []),
    }


def build_capacity_proposal(
    gap: Mapping[str, Any],
    *,
    status: str = "draft",
) -> dict[str, Any]:
    dc = str(gap.get("decision_class") or "UNKNOWN")
    template = CLASS_POLICY_TEMPLATES.get(dc) or CLASS_POLICY_TEMPLATES["UNKNOWN"]
    choices = gap.get("repeated_founder_choices") or []
    repeated = (
        "founder repeatedly chooses: " + ", ".join(str(c) for c in choices)
        if choices
        else "founder repeatedly supplies micro-decisions"
    )
    name = f"{dc.lower()}_routing"
    return {
        "schema": "noetfield.decision_capacity_proposal.v1",
        "proposal_id": _id("dcp"),
        "gap_id": gap["gap_id"],
        "capacity_gap": {"name": name, "repeated_decision": repeated},
        "proposed_policy": json.loads(json.dumps(template)),
        "status": status,
        "decision_class": dc,
        "created_at": _now(),
    }


def to_policy_candidate(proposal: Mapping[str, Any]) -> dict[str, Any]:
    dc = str(proposal.get("decision_class") or "UNKNOWN")
    body = proposal.get("proposed_policy") or {}
    digest = hashlib.sha256(
        json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()[:12]
    learning_record_id = _id("lr")
    return {
        "schema": "noetfield.decision_policy_candidate.v1",
        "candidate_id": _id("dpc"),
        "proposal_id": proposal["proposal_id"],
        "decision_class": dc,
        "policy_version": f"{dc.lower()}.v1.candidate.{digest}",
        "body": body,
        "replay_status": "queued",
        "learning_record_id": learning_record_id,
        "mutation_class": "OPEN",
        "created_at": _now(),
    }


def to_learning_organ_record(
    candidate: Mapping[str, Any],
    *,
    stage_market_id: str = "decision_capacity",
    sample_n: int = 1,
    confidence: float = 0.55,
) -> dict[str, Any]:
    """OPEN-class learning_record draft for Motor Learning Organ propose→shadow→ratify."""
    return {
        "record_id": candidate["learning_record_id"],
        "source_event": "MISSING_DECISION_CAPACITY",
        "layer": "policy",
        "proposed_correction": {
            "kind": "decision_policy_candidate",
            "candidate_id": candidate["candidate_id"],
            "decision_class": candidate["decision_class"],
            "policy_version": candidate["policy_version"],
            "body": candidate["body"],
        },
        "ssot_consistency_check": "pending_replay",
        "critic_reviewed": False,
        "status": "draft",
        "stage_market_id": stage_market_id,
        "sample_n": sample_n,
        "confidence": confidence,
        "pattern_description": f"Decision capacity gap for {candidate['decision_class']}",
        "mutation_class": "OPEN",
        "created_at": _now(),
    }


def close_capacity_loop(
    *,
    decision_class: str,
    event_types: Sequence[str],
    existing_policy_coverage: float = 0.35,
    task_id: str = "",
    human_tax_units: float = 0.0,
    evidence_refs: Sequence[str] | None = None,
) -> dict[str, Any] | None:
    """Full Phase-B path: gap → proposal → candidate → learning draft (or None)."""
    gap = detect_capacity_gap(
        decision_class=decision_class,
        event_types=event_types,
        existing_policy_coverage=existing_policy_coverage,
        task_id=task_id,
        human_tax_units=human_tax_units,
        evidence_refs=evidence_refs,
    )
    if not gap:
        return None
    proposal = build_capacity_proposal(gap)
    candidate = to_policy_candidate(proposal)
    learning = to_learning_organ_record(candidate)
    return {
        "incident_type": "MISSING_DECISION_CAPACITY",
        "gap": gap,
        "proposal": proposal,
        "policy_candidate": candidate,
        "learning_record": learning,
        "work_status": "FROZEN",
    }


__all__ = [
    "DECISION_CLASSES",
    "EVENT_TO_CHOICE",
    "CLASS_POLICY_TEMPLATES",
    "map_events_to_founder_choices",
    "detect_capacity_gap",
    "build_capacity_proposal",
    "to_policy_candidate",
    "to_learning_organ_record",
    "close_capacity_loop",
]
