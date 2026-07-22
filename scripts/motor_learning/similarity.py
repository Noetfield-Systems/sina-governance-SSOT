
"""Deterministic explainable similarity (field Jaccard / exact matches). Not ML."""
from __future__ import annotations

from typing import Any

from . import SIMILARITY_VERSION

FIELDS = (
    "action_attempted",
    "outcome",
    "error_class",
    "recovery_path",
    "runway",
    "repository",
    "stage",
    "loop_id",
)

WEIGHTS = {
    "action_attempted": 0.25,
    "outcome": 0.20,
    "error_class": 0.20,
    "recovery_path": 0.15,
    "runway": 0.08,
    "repository": 0.07,
    "stage": 0.03,
    "loop_id": 0.02,
}

DEFAULT_THRESHOLD = 0.75


def _fp_from_signal(signal: dict) -> dict:
    return dict(signal.get("fingerprint") or {})


def _fp_from_prior(prior: dict) -> dict:
    if prior.get("fingerprint"):
        return dict(prior["fingerprint"])
    return {
        "action_attempted": prior.get("action_attempted"),
        "outcome": prior.get("expected_outcome") or prior.get("outcome"),
        "error_class": prior.get("error_class"),
        "recovery_path": prior.get("recovery_path") or prior.get("recommended_action"),
        "runway": (prior.get("scope") or {}).get("runway"),
        "repository": (prior.get("scope") or {}).get("repository"),
        "stage": prior.get("stage"),
        "loop_id": (prior.get("scope") or {}).get("loop_id"),
    }


def compare(candidate: dict, prior: dict, *, threshold: float = DEFAULT_THRESHOLD) -> dict:
    a = _fp_from_signal(candidate) if "fingerprint" in candidate else _fp_from_prior(candidate)
    b = _fp_from_prior(prior)
    components = {}
    matching = []
    conflicting = []
    score = 0.0
    for field in FIELDS:
        va, vb = a.get(field), b.get(field)
        w = WEIGHTS[field]
        if va is None and vb is None:
            components[field] = {"match": True, "weight": w, "contribution": 0.0, "note": "both_absent"}
            continue
        if va is None or vb is None:
            components[field] = {"match": False, "weight": w, "contribution": 0.0, "note": "one_absent"}
            continue
        if va == vb:
            components[field] = {"match": True, "weight": w, "contribution": w, "values": [va, vb]}
            matching.append(field)
            score += w
        else:
            components[field] = {"match": False, "weight": w, "contribution": 0.0, "values": [va, vb]}
            conflicting.append(field)
            # outcome contradiction is material
            if field == "outcome":
                score -= 0.15

    score = max(0.0, min(1.0, round(score, 6)))
    explanation = (
        f"weighted field overlap={score:.3f}; matches={matching}; conflicts={conflicting}; "
        f"threshold={threshold}; version={SIMILARITY_VERSION}"
    )
    return {
        "schema": "nf_motor_learning_similarity_v1",
        "algorithm_version": SIMILARITY_VERSION,
        "candidate_id": candidate.get("signal_id") or candidate.get("candidate_id") or candidate.get("prior_id"),
        "compared_prior_id": prior.get("prior_id"),
        "total_score": score,
        "component_scores": components,
        "matching_fields": matching,
        "conflicting_fields": conflicting,
        "threshold": threshold,
        "passes_threshold": score >= threshold and "outcome" not in conflicting,
        "explanation": explanation,
        "evidence_refs": list(candidate.get("evidence_refs") or []) + list(prior.get("evidence_refs") or []),
        "advisory_only": True,
        "promotion_authority": False,
    }


def rank(candidate: dict, priors: list[dict], *, threshold: float = DEFAULT_THRESHOLD) -> list[dict]:
    ranked = [compare(candidate, p, threshold=threshold) for p in priors]
    ranked.sort(key=lambda x: x["total_score"], reverse=True)
    return ranked
