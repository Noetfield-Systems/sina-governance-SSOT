
"""End-to-end W1 Motor Learning pipeline (fixture/dry-run). No live promotion."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .normalize import normalize_many
from .extract import extract_many
from .mine import mine_patterns
from .prior_store import PriorStore
from .similarity import rank as rank_similarity
from .confidence import compute_confidence
from .shadow import evaluate_shadow
from .ecqr import validate_ecqr_decision
from .lifecycle import transition, PROPOSED, SHADOW, RATIFIED, REJECTED, ROLLED_BACK, OBSERVED
from .receipt import build_learning_receipt, validate_learning_receipt, write_receipt
from .errors import GovernanceBlock, IllegalTransition, MotorLearningError, SchemaError
from .hashutil import canonical_json
from . import ALGORITHM_VERSION


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def run_pipeline(
    *,
    events: list[dict],
    store_dir: Path,
    out_dir: Path,
    ecqr_decision: dict | None = None,
    min_occurrences: int = 3,
    dry_run: bool = True,
    merge_near_duplicate_threshold: float = 0.92,
) -> dict[str, Any]:
    """
    Execute: ingest→normalize→extract→mine→prior search→similarity→
    candidate→shadow→confidence→ECQR→prior+receipt.

    dry_run=True (default): never claims live production mutation.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    store = PriorStore(Path(store_dir))

    seen: set[str] = set()
    # seed seen from previous run marker if present
    seen_path = out_dir / "seen_idempotency_keys.json"
    if seen_path.exists():
        seen = set(_load_json(seen_path))

    accepted, duplicates = normalize_many(events, seen_keys=seen)
    seen_path.write_text(canonical_json(sorted(seen)) + "\n")

    signals = extract_many(accepted)
    candidates = mine_patterns(signals, min_occurrences=min_occurrences)

    # Pick primary candidate: first that meets threshold, else first observed
    primary = None
    for c in candidates:
        if c.get("meets_threshold"):
            primary = c
            break
    if primary is None and candidates:
        primary = candidates[0]

    similarity_rankings: list[dict] = []
    near_duplicate = None
    if primary:
        # Similarity may inspect expired for lineage, but near-duplicate merge/reject
        # applies only to active/shadow (expired is lineage-only).
        searchable = store.search(
            action=primary["fingerprint"].get("action_attempted"),
            status={"active", "shadow", "proposed", "rejected", "expired"},
            include_expired=True,
        )
        similarity_rankings = rank_similarity(primary, searchable)
        active_like = store.search(
            action=primary["fingerprint"].get("action_attempted"),
            status={"active", "shadow"},
        )
        active_rankings = rank_similarity(primary, active_like)
        if active_rankings and active_rankings[0]["total_score"] >= merge_near_duplicate_threshold:
            if "outcome" not in active_rankings[0]["conflicting_fields"]:
                near_duplicate = active_rankings[0]

    shadow_report = None
    confidence = None
    receipt = None
    prior = None
    final_state = None
    blocked_reason = None
    ecqr_validated = None

    if primary and primary.get("meets_threshold") and not primary.get("contradiction"):
        # lifecycle: OBSERVED/PROPOSED → SHADOW
        entity = dict(primary)
        if entity["state"] == OBSERVED:
            # insufficient was already filtered; contradiction path stays observed
            pass
        if entity["state"] == PROPOSED:
            entity = transition(
                entity, SHADOW,
                actor="motor_learning_w1_orchestrator",
                reason="enter_shadow_evaluation",
                evidence=entity["evidence_refs"],
                require_receipt=False,
            )
        shadow_report = evaluate_shadow(entity, accepted)
        (out_dir / "shadow_report.json").write_text(json.dumps(shadow_report, indent=2) + "\n")

        confidence = compute_confidence(
            occurrence_count=entity["occurrence_count"],
            outcomes_seen=entity.get("outcomes_seen") or [],
            evidence_refs=entity.get("evidence_refs") or [],
            shadow_report=shadow_report,
            confidence_before=0.0,
            scope=entity.get("scope") or {},
        )
        (out_dir / "confidence.json").write_text(json.dumps(confidence, indent=2) + "\n")

        # Near-duplicate handling: reject new candidate as duplicate of existing prior
        if near_duplicate and ecqr_decision and ecqr_decision.get("decision") == "RATIFIED":
            # force rejection path for duplicate unless explicit supersede
            if not ecqr_decision.get("supersedes"):
                ecqr_decision = dict(ecqr_decision)
                ecqr_decision["decision"] = "REJECTED"
                ecqr_decision["rationale"] = (
                    f"near_duplicate_of:{near_duplicate['compared_prior_id']} "
                    f"score={near_duplicate['total_score']}; " + ecqr_decision.get("rationale", "")
                )

        if ecqr_decision:
            try:
                ecqr_decision = dict(ecqr_decision)
                ecqr_decision.setdefault("candidate_id", entity["candidate_id"])
                ecqr_decision.setdefault("shadow_result_ref", f"shadow:{shadow_report['shadow_id']}")
                ecqr_decision.setdefault("confidence_before", confidence["confidence_before"])
                ecqr_decision.setdefault("confidence_after", confidence["confidence_after"])
                ecqr_decision.setdefault("evidence_reviewed", entity["evidence_refs"])
                ecqr_validated = validate_ecqr_decision(
                    ecqr_decision, confidence=confidence, shadow=shadow_report
                )
            except (GovernanceBlock, SchemaError) as exc:
                blocked_reason = str(exc)
                ecqr_validated = None

        if ecqr_validated:
            decision = ecqr_validated["decision"]
            ts = ecqr_validated["effective_at"]
            prior_id = ecqr_validated.get("prior_id") or f"prior-{entity['candidate_id']}"
            mapped_decision = {"RATIFIED": "accepted", "REJECTED": "rejected", "ROLLED_BACK": "rolled_back"}[decision]

            # Build receipt FIRST — transition requires it
            receipt = build_learning_receipt(
                decision=decision,
                prior_id=prior_id,
                candidate_id=entity["candidate_id"],
                reviewer=ecqr_validated["reviewer"],
                rationale=ecqr_validated["rationale"],
                evidence_links=list(ecqr_validated["evidence_reviewed"]) + [f"shadow:{shadow_report['shadow_id']}"],
                confidence_before=confidence["confidence_before"],
                confidence_after=confidence["confidence_after"],
                affected_loops=list(ecqr_validated["affected_loops"]),
                applicable_runways=list(ecqr_validated["applicable_runways"]),
                repositories=list(ecqr_validated.get("repositories") or []),
                origin_event=entity["source_event_ids"][0],
                decision_timestamp=ts,
                expiry=ecqr_validated.get("expires_at"),
                supersedes=ecqr_validated.get("supersedes"),
                rollback_target=ecqr_validated.get("rollback_target"),
                snapshot_id=prior_id,
                shadow_evidence_path=str(out_dir / "shadow_report.json"),
                similarity_score=(similarity_rankings[0]["total_score"] if similarity_rankings else None),
            )
            validate_learning_receipt(receipt)
            receipt_path = out_dir / f"learning_receipt-{receipt['receipt_id']}.json"
            if not dry_run:
                # still no live promo — dry_run False only writes artifacts under out_dir/store
                pass
            write_receipt(receipt, receipt_path)
            # also mirror under receipts/learning when out_dir is inside repo runs
            mirror = Path(out_dir).parent.parent / "receipts" / "learning" / receipt_path.name
            # only mirror if conventional path exists relative to repo runs
            try:
                if "runs" in str(out_dir) or out_dir.name.startswith("run"):
                    write_receipt(receipt, Path(out_dir) / ".." / ".." / "receipts" / "learning" / receipt_path.name)
            except Exception:
                pass

            target_state = {"RATIFIED": RATIFIED, "REJECTED": REJECTED, "ROLLED_BACK": ROLLED_BACK}[decision]
            entity = transition(
                entity, target_state,
                actor=ecqr_validated["reviewer"],
                reason=ecqr_validated["rationale"],
                evidence=ecqr_validated["evidence_reviewed"],
                learning_receipt_id=receipt["receipt_id"],
                timestamp=ts,
            )
            final_state = entity["state"]

            prior = {
                "prior_id": prior_id,
                "status": entity["status"],
                "state": entity["state"],
                "action_attempted": entity["fingerprint"].get("action_attempted"),
                "recommended_action": entity["recommended_action"],
                "expected_outcome": entity.get("expected_outcome") or "success",
                "error_class": entity["fingerprint"].get("error_class"),
                "recovery_path": entity["fingerprint"].get("recovery_path"),
                "fingerprint": entity["fingerprint"],
                "scope": entity["scope"],
                "evidence_refs": entity["evidence_refs"],
                "source_event_ids": entity["source_event_ids"],
                "learning_receipt_id": receipt["receipt_id"],
                "candidate_id": entity["candidate_id"],
                "confidence_after": confidence["confidence_after"],
                "expires_at": ecqr_validated.get("expires_at"),
                "supersedes": ecqr_validated.get("supersedes"),
                "version": 1,
                "transition_history": entity.get("transition_history"),
                "dry_run": dry_run,
                "live_promotion": False,
            }
            store.update(prior)
            (out_dir / "prior.json").write_text(json.dumps(prior, indent=2) + "\n")
        else:
            final_state = entity.get("state")
            if not blocked_reason:
                blocked_reason = "no_ecqr_decision_or_blocked"
    elif primary:
        final_state = primary.get("state")
        blocked_reason = primary.get("not_ratifiable_reason") or "candidate_not_ready"
    else:
        blocked_reason = "no_candidates"

    summary = {
        "schema": "nf_motor_learning_w1_run_summary_v1",
        "algorithm_version": ALGORITHM_VERSION,
        "dry_run": dry_run,
        "live_promotion": False,
        "model_learning": False,
        "events_in": len(events),
        "events_accepted": len(accepted),
        "events_duplicate": len(duplicates),
        "signals": len(signals),
        "candidates": [{"candidate_id": c["candidate_id"], "state": c["state"], "n": c["occurrence_count"], "reason": c.get("not_ratifiable_reason")} for c in candidates],
        "primary_candidate_id": primary["candidate_id"] if primary else None,
        "similarity_top": similarity_rankings[0] if similarity_rankings else None,
        "near_duplicate": near_duplicate,
        "shadow_result": shadow_report["result"] if shadow_report else None,
        "confidence_after": confidence["confidence_after"] if confidence else None,
        "ecqr_decision": ecqr_validated["decision"] if ecqr_validated else None,
        "final_state": final_state,
        "prior_id": prior["prior_id"] if prior else None,
        "receipt_id": receipt["receipt_id"] if receipt else None,
        "blocked_reason": blocked_reason,
        "out_dir": str(out_dir),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (out_dir / "candidates.json").write_text(json.dumps(candidates, indent=2) + "\n")
    if similarity_rankings:
        (out_dir / "similarity.json").write_text(json.dumps(similarity_rankings, indent=2) + "\n")
    return summary


def run_from_fixture_dir(fixture_dir: Path, *, out_dir: Path, store_dir: Path, dry_run: bool = True) -> dict:
    fixture_dir = Path(fixture_dir)
    events = _load_json(fixture_dir / "events.json")
    ecqr_path = fixture_dir / "ecqr_decision.json"
    ecqr = _load_json(ecqr_path) if ecqr_path.exists() else None
    meta = _load_json(fixture_dir / "meta.json") if (fixture_dir / "meta.json").exists() else {}
    return run_pipeline(
        events=events,
        store_dir=store_dir,
        out_dir=out_dir,
        ecqr_decision=ecqr,
        min_occurrences=int(meta.get("min_occurrences", 3)),
        dry_run=dry_run,
    )
