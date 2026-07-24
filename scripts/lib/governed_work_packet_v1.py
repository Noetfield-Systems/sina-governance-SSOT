#!/usr/bin/env python3
"""Governed work packet control — shared Phase A helpers (SG reference)."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

TERMINALS = frozenset(
    {"ACCEPTED_ARTIFACT", "BOUNDED_FAILURE", "RED_ZONE_DECISION_PACKET"}
)
NON_TAX = frozenset(
    {"OWNER_DECISION", "NEW_EXTERNAL_FACT", "CREATIVE_CHOICE", "RED_ZONE_APPROVAL"}
)
TAX_TYPES = frozenset(
    {
        "GOAL_RESTATEMENT",
        "SCOPE_RESTATEMENT",
        "MANUAL_CORRECTION",
        "MANUAL_ROLLBACK",
        "MANUAL_RESTART",
        "FALSE_DONE_REJECTION",
        "OUT_OF_SCOPE_REPAIR",
        "MANUAL_VERIFICATION",
        "TOOL_CANCELLATION",
    }
)

HTU_WEIGHTS = {
    "goal_restatements": 3,
    "scope_restatements": 3,
    "manual_rollbacks": 5,
    "manual_restarts": 2,
    "false_done_rejections": 4,
    "out_of_scope_repairs": 5,
}

SOFT = {
    "same_failure_signature": 2,
    "goal_restatement": 2,
    "scope_restatement": 2,
    "no_progress_cycles": 2,
    "repeated_done_without_evidence": 2,
}


def authority_hash(contract: Mapping[str, Any]) -> str:
    payload = {
        k: contract[k]
        for k in (
            "goal_id",
            "owner",
            "goal_version",
            "intent",
            "acceptance_predicates",
            "scope_allowlist",
            "forbidden_effects",
            "budgets",
            "evidence_required",
            "stop_policy",
        )
        if k in contract
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def failure_signature(
    *,
    task_class: str,
    goal_version: int,
    failing_acceptance_check: str,
    error_code: str,
    affected_scope: Sequence[str],
    tool_class: str,
    plan_hash: str,
) -> str:
    material = "|".join(
        [
            task_class,
            str(goal_version),
            failing_acceptance_check,
            error_code,
            ",".join(affected_scope),
            tool_class,
            plan_hash,
        ]
    )
    digest = hashlib.sha256(material.encode()).hexdigest()[:32]
    return f"sig_{digest}"


def compute_htu(
    *,
    active_correction_minutes: float = 0.0,
    goal_restatements: int = 0,
    scope_restatements: int = 0,
    manual_rollbacks: int = 0,
    manual_restarts: int = 0,
    false_done_rejections: int = 0,
    out_of_scope_repairs: int = 0,
) -> float:
    return (
        float(active_correction_minutes)
        + HTU_WEIGHTS["goal_restatements"] * goal_restatements
        + HTU_WEIGHTS["scope_restatements"] * scope_restatements
        + HTU_WEIGHTS["manual_rollbacks"] * manual_rollbacks
        + HTU_WEIGHTS["manual_restarts"] * manual_restarts
        + HTU_WEIGHTS["false_done_rejections"] * false_done_rejections
        + HTU_WEIGHTS["out_of_scope_repairs"] * out_of_scope_repairs
    )


def event_is_tax(event_type: str, *, avoidable: bool) -> bool:
    if event_type in NON_TAX:
        return False
    if event_type not in TAX_TYPES:
        return False
    return bool(avoidable)


def mechanical_done(
    *,
    artifact_exists: bool,
    all_acceptance_checks_pass: bool,
    scope_is_clean: bool,
    evidence_is_valid: bool,
    receipt_is_written: bool,
) -> bool:
    return all(
        [
            artifact_exists,
            all_acceptance_checks_pass,
            scope_is_clean,
            evidence_is_valid,
            receipt_is_written,
        ]
    )


def map_goal_status_to_terminal(status: str) -> str | None:
    accepted = {"PASSED", "SUCCEEDED", "ACCEPTED"}
    bounded = {
        "FAILED",
        "BUDGET_EXHAUSTED",
        "TIME_EXHAUSTED",
        "CANCELLED",
        "BLOCKED",
        "PARTIAL_PASS",
    }
    red = {
        "WAITING_FOR_APPROVAL",
        "WAITING_FOR_EXTERNAL_EVENT",
        "RED_ZONE",
    }
    if status in accepted:
        return "ACCEPTED_ARTIFACT"
    if status in red:
        return "RED_ZONE_DECISION_PACKET"
    if status in bounded:
        return "BOUNDED_FAILURE"
    return None


def soft_breaker_trips(
    *,
    failure_signature_count: int = 0,
    goal_restatements: int = 0,
    scope_restatements: int = 0,
    no_progress_cycles: int = 0,
    human_tax_units: float = 0.0,
    human_tax_budget: float = 1e9,
    fanout: int = 0,
    fanout_budget: int = 1e9,
    false_done_count: int = 0,
) -> list[str]:
    trips: list[str] = []
    if failure_signature_count >= SOFT["same_failure_signature"]:
        trips.append("REPEATED_FAILURE_SIGNATURE")
    if goal_restatements >= SOFT["goal_restatement"]:
        trips.append("GOAL_RESTATEMENT")
    if scope_restatements >= SOFT["scope_restatement"]:
        trips.append("SCOPE_RESTATEMENT")
    if no_progress_cycles >= SOFT["no_progress_cycles"]:
        trips.append("ZERO_PROGRESS")
    if human_tax_units > human_tax_budget:
        trips.append("HUMAN_TAX_BUDGET_EXCEEDED")
    if fanout > fanout_budget:
        trips.append("UNNECESSARY_FANOUT")
    if false_done_count >= SOFT["repeated_done_without_evidence"]:
        trips.append("FALSE_DONE_WITHOUT_EVIDENCE")
    return trips


def may_resume_after_incident(*, prior_plan_hash: str, new_plan_hash: str) -> bool:
    if not new_plan_hash or not prior_plan_hash:
        return False
    return new_plan_hash != prior_plan_hash


def progress_delta(
    *,
    newly_passing_acceptance_checks: int = 0,
    new_verified_artifacts: int = 0,
    validated_state_improvement: int = 0,
) -> int:
    return (
        int(newly_passing_acceptance_checks)
        + int(new_verified_artifacts)
        + int(validated_state_improvement)
    )


def reject_unnecessary_fanout(*, max_workers: int, requested_workers: int) -> str | None:
    if requested_workers > max_workers:
        return "UNNECESSARY_FANOUT"
    return None


def reject_false_done(*, claim_done: bool, evidence_valid: bool) -> str | None:
    if claim_done and not evidence_valid:
        return "FALSE_DONE_WITHOUT_EVIDENCE"
    return None


def reject_out_of_scope(*, path: str, allowlist: Iterable[str]) -> str | None:
    for prefix in allowlist:
        if path == prefix or path.startswith(prefix.rstrip("*").rstrip("/")):
            if prefix.endswith("/**") or prefix.endswith("/*"):
                root = prefix[:-3] if prefix.endswith("/**") else prefix[:-2]
                if path == root or path.startswith(root + "/"):
                    return None
            elif path == prefix or path.startswith(prefix + "/"):
                return None
            elif path.startswith(prefix.replace("/**", "/")):
                return None
    # simple glob: apps/site/** style
    for prefix in allowlist:
        root = prefix.replace("/**", "").replace("/*", "")
        if path == root or path.startswith(root + "/"):
            return None
    return "OUT_OF_SCOPE_WRITE"


__all__ = [
    "TERMINALS",
    "authority_hash",
    "failure_signature",
    "compute_htu",
    "event_is_tax",
    "mechanical_done",
    "map_goal_status_to_terminal",
    "soft_breaker_trips",
    "may_resume_after_incident",
    "progress_delta",
    "reject_unnecessary_fanout",
    "reject_false_done",
    "reject_out_of_scope",
]
