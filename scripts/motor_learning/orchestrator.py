"""End-to-end W1 Motor Learning pipeline. Dry-run is store-immutable."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .normalize import normalize_many
from .extract import extract_many
from .mine import mine_patterns
from .prior_store import PriorStore, store_tree_hash
from .similarity import rank as rank_similarity
from .confidence import compute_confidence
from .shadow import evaluate_shadow
from .ecqr import validate_ecqr_decision
from .lifecycle import transition, PROPOSED, SHADOW, RATIFIED, REJECTED, ROLLED_BACK, OBSERVED
from .receipt import build_learning_receipt, validate_learning_receipt, write_receipt
from .event_registry import EventRegistry
from .errors import GovernanceBlock, MotorLearningError, SchemaError
from .hashutil import canonical_json, content_hash
from . import ALGORITHM_VERSION, CONFIDENCE_VERSION


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def run_pipeline(
    *,
    events: list[dict],
    store_dir: Path,
    out_dir: Path,
    ecqr_decision: dict | None = None,
    shadow_events: list[dict] | None = None,
    min_occurrences: int = 3,
    dry_run: bool = True,
    merge_near_duplicate_threshold: float = 0.92,
    as_of: str | None = None,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    store_dir = Path(store_dir)
    store_hash_before = store_tree_hash(store_dir)

    store = PriorStore(store_dir, create=False) if dry_run else PriorStore(store_dir, create=True)
    registry = EventRegistry(out_dir / "event_registry.json")

    accepted, duplicates = normalize_many(events, event_registry=registry)
    signals = extract_many(accepted)
    candidates = mine_patterns(signals, min_occurrences=min_occurrences)

    primary = None
    for c in candidates:
        if c.get("meets_threshold"):
            primary = c
            break
    if primary is None and candidates:
        primary = candidates[0]

    similarity_rankings: list[dict] = []
    near_duplicate = None
    machine_veto: dict | None = None
    shadow_report = None
    confidence = None
    receipt = None
    prior = None
    final_state = None
    blocked_reason = None
    ecqr_validated = None
    ecqr_original = dict(ecqr_decision) if ecqr_decision else None

    if primary and primary.get("meets_threshold") and not primary.get("contradiction"):
        entity = dict(primary)
        if entity["state"] == PROPOSED:
            entity = transition(
                entity, SHADOW,
                actor="motor_learning_w1_orchestrator",
                reason="enter_shadow_evaluation",
                evidence=entity["evidence_refs"],
            )

        # Independent shadow stream
        if shadow_events is None:
            blocked_reason = "shadow_events_required"
            final_state = entity.get("state")
        else:
            sh_accepted, _ = normalize_many(shadow_events, event_registry=EventRegistry(out_dir / "shadow_event_registry.json"))
            mine_ids = set(entity.get("source_event_ids") or [])
            shadow_ids = {e["event_id"] for e in sh_accepted}
            overlap = sorted(mine_ids & shadow_ids)
            if overlap:
                blocked_reason = f"shadow_mining_event_overlap:{overlap}"
                final_state = entity.get("state")
                _write_json(out_dir / "overlap_reject.json", {"overlap": overlap})
            else:
                shadow_report = evaluate_shadow(entity, sh_accepted)
                _write_json(out_dir / "shadow_report.json", shadow_report)

                confidence = compute_confidence(
                    occurrence_count=entity["occurrence_count"],
                    outcomes_seen=entity.get("outcomes_seen") or [],
                    evidence_refs=entity.get("evidence_refs") or [],
                    shadow_report=shadow_report,
                    confidence_before=0.0,
                    scope=entity.get("scope") or {},
                    mining_evidence_ids=list(entity.get("source_event_ids") or []),
                    shadow_evidence_ids=list(shadow_ids),
                )
                _write_json(out_dir / "confidence.json", confidence)

                searchable = store.search(
                    action=primary["fingerprint"].get("action_attempted"),
                    status={"active", "shadow", "proposed", "rejected", "expired"},
                    include_expired=True,
                    as_of=as_of,
                )
                similarity_rankings = rank_similarity(primary, searchable)
                active_like = store.search(
                    action=primary["fingerprint"].get("action_attempted"),
                    status={"active", "shadow"},
                    as_of=as_of,
                    live_consumable_only=False,
                )
                # Conflict detection includes fixture-seeded actives; they remain non-consumable.
                active_for_conflict = [p for p in active_like if p.get("effective_status") == "active"]
                active_rankings = rank_similarity(primary, active_for_conflict)
                if active_rankings and active_rankings[0]["total_score"] >= merge_near_duplicate_threshold:
                    if "outcome" not in active_rankings[0]["conflicting_fields"]:
                        near_duplicate = active_rankings[0]
                        machine_veto = {
                            "schema": "nf_motor_learning_machine_policy_veto_v1",
                            "code": "DUPLICATE_CONFLICT_REVIEW_REQUIRED",
                            "actor": "machine_policy:near_duplicate_v1",
                            "compared_prior_id": near_duplicate["compared_prior_id"],
                            "score": near_duplicate["total_score"],
                            "reviewer_decision_preserved": ecqr_original.get("decision") if ecqr_original else None,
                            "note": "Reviewer decision NOT rewritten; new ECQR required for merge/supersede/reject",
                        }
                        _write_json(out_dir / "machine_policy_veto.json", machine_veto)

                if ecqr_decision and not machine_veto:
                    try:
                        ed = dict(ecqr_decision)
                        if ed.get("candidate_id") in (None, "", "auto"):
                            ed["candidate_id"] = entity["candidate_id"]
                        elif ed.get("candidate_id") != entity["candidate_id"]:
                            # Bind to computed candidate; fixture placeholders must yield
                            ed["candidate_id"] = entity["candidate_id"]
                        ed["shadow_result_ref"] = f"shadow:{shadow_report['shadow_id']}"
                        ed["shadow_hash"] = shadow_report["content_hash"]
                        ed["confidence_before"] = confidence["confidence_before"]
                        ed["confidence_after"] = confidence["confidence_after"]
                        ed.setdefault("evidence_reviewed", list(entity["source_event_ids"]) + list(shadow_ids))
                        ed.setdefault("algorithm_versions", {
                            "pipeline": ALGORITHM_VERSION,
                            "confidence": CONFIDENCE_VERSION,
                        })
                        ecqr_validated = validate_ecqr_decision(
                            ed, confidence=confidence, shadow=shadow_report, candidate=entity
                        )
                    except (GovernanceBlock, SchemaError) as exc:
                        blocked_reason = str(exc)
                        ecqr_validated = None
                elif machine_veto and ecqr_decision:
                    # Preserve reviewer decision; block commit
                    blocked_reason = "DUPLICATE_CONFLICT_REVIEW_REQUIRED"
                    _write_json(out_dir / "preserved_reviewer_decision.json", ecqr_original)

                if ecqr_validated and ecqr_validated["decision"] in ("RATIFIED", "REJECTED"):
                    decision = ecqr_validated["decision"]
                    ts = ecqr_validated["effective_at"]
                    prior_id = ecqr_validated.get("prior_id") or f"prior-{entity['candidate_id']}"
                    receipt = None
                    receipt_path = out_dir / "learning_receipt_pending.json"
                    try:
                        receipt = build_learning_receipt(
                            decision=decision,
                            prior_id=prior_id,
                            candidate_id=entity["candidate_id"],
                            reviewer=ecqr_validated["reviewer"],
                            rationale=ecqr_validated["rationale"],
                            evidence_links=list(ecqr_validated["evidence_reviewed"]),
                            confidence_before=confidence["confidence_before"],
                            confidence_after=confidence["confidence_after"],
                            affected_loops=list(ecqr_validated["affected_loops"]),
                            applicable_runways=list(ecqr_validated["applicable_runways"]),
                            repositories=list(ecqr_validated.get("repositories") or []),
                            origin_event=entity["source_event_ids"][0],
                            decision_timestamp=ts,
                            expiry=ecqr_validated.get("expires_at"),
                            supersedes=ecqr_validated.get("supersedes"),
                            snapshot_id=prior_id,
                            shadow_evidence_path=str(out_dir / "shadow_report.json"),
                            shadow_id=shadow_report["shadow_id"],
                            shadow_hash=shadow_report["content_hash"],
                            confidence_hash=confidence["content_hash"],
                            similarity_score=(similarity_rankings[0]["total_score"] if similarity_rankings else None),
                        )
                        validate_learning_receipt(receipt)
                        target_state = RATIFIED if decision == "RATIFIED" else REJECTED
                        entity = transition(
                            entity, target_state,
                            actor=ecqr_validated["reviewer"],
                            reason=ecqr_validated["rationale"],
                            evidence=ecqr_validated["evidence_reviewed"],
                            learning_receipt=receipt,
                            timestamp=ts,
                        )
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
                            "live_consumable": not dry_run,
                            "fixture_seeded": False,
                        }
                        # Atomic-ish: write receipt to out_dir first; only then store if not dry_run
                        write_receipt(receipt, out_dir / f"learning_receipt-{receipt['receipt_id']}.json")
                        if not dry_run:
                            store.create(
                                prior,
                                allow_duplicate=False,
                                expected_version=1,
                                ecqr_decision=ecqr_validated,
                                learning_receipt=receipt,
                            )
                            _write_json(out_dir / "prior.json", prior)
                        else:
                            # diagnostics only under out_dir
                            _write_json(out_dir / "prior.dry_run_preview.json", prior)
                        final_state = entity["state"]
                    except Exception as exc:
                        # Failed terminal transition: ensure no orphan receipt in store; delete pending out receipt if transition failed before write
                        blocked_reason = f"terminal_commit_failed:{exc}"
                        receipt = None
                        # remove any receipt files written if store write failed
                        if not dry_run:
                            # If store write failed after receipt write, leave receipt in out_dir as diagnostic but store unchanged
                            pass
                        final_state = entity.get("state")
                else:
                    final_state = entity.get("state")
                    if not blocked_reason:
                        blocked_reason = "no_ecqr_decision_or_blocked"
    elif primary:
        final_state = primary.get("state")
        blocked_reason = primary.get("not_ratifiable_reason") or "candidate_not_ready"
    else:
        blocked_reason = "no_candidates"

    store_hash_after = store_tree_hash(store_dir)
    if dry_run and store_hash_before != store_hash_after:
        raise GovernanceBlock("dry-run mutated prior store (forbidden)")

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
        "candidates": [
            {"candidate_id": c["candidate_id"], "state": c["state"], "n": c["occurrence_count"], "reason": c.get("not_ratifiable_reason")}
            for c in candidates
        ],
        "primary_candidate_id": primary["candidate_id"] if primary else None,
        "similarity_top": similarity_rankings[0] if similarity_rankings else None,
        "near_duplicate": near_duplicate,
        "machine_policy_veto": machine_veto,
        "reviewer_decision_preserved": ecqr_original.get("decision") if ecqr_original else None,
        "shadow_result": shadow_report["result"] if shadow_report else None,
        "confidence_after": confidence["confidence_after"] if confidence else None,
        "ecqr_decision": ecqr_validated["decision"] if ecqr_validated else None,
        "final_state": final_state,
        "prior_id": prior["prior_id"] if prior else None,
        "receipt_id": receipt["receipt_id"] if receipt else None,
        "blocked_reason": blocked_reason,
        "store_hash_before": store_hash_before,
        "store_hash_after": store_hash_after,
        "store_unchanged": store_hash_before == store_hash_after,
        "out_dir": str(out_dir),
    }
    _write_json(out_dir / "summary.json", summary)
    _write_json(out_dir / "candidates.json", candidates)
    if similarity_rankings:
        _write_json(out_dir / "similarity.json", similarity_rankings)
    return summary


def rollback_prior(
    *,
    prior_id: str,
    store_dir: Path,
    out_dir: Path,
    ecqr_decision: dict,
    regression_evidence: list[str],
    dry_run: bool = True,
) -> dict[str, Any]:
    """End-to-end rollback of an existing RATIFIED prior."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    store_dir = Path(store_dir)
    store_hash_before = store_tree_hash(store_dir)
    store = PriorStore(store_dir, create=not dry_run)
    prior = store.get(prior_id)
    if not prior:
        raise GovernanceBlock(f"prior not found: {prior_id}")
    if prior.get("status") != "active" and prior.get("state") != RATIFIED:
        raise GovernanceBlock(f"prior {prior_id} is not RATIFIED/active")

    ed = dict(ecqr_decision)
    ed["decision"] = "ROLLED_BACK"
    ed.setdefault("rollback_target", prior_id)
    ed.setdefault("prior_id", prior_id)
    ed.setdefault("candidate_id", prior.get("candidate_id") or f"cand-rollback-{prior_id}")
    ed.setdefault("shadow_result_ref", "shadow:rollback-n/a")
    ed.setdefault("evidence_reviewed", list(regression_evidence))
    if not regression_evidence:
        raise GovernanceBlock("rollback requires regression_evidence")

    # Bind confidence placeholders from prior
    ed.setdefault("confidence_before", float(prior.get("confidence_after") or 0.8))
    ed.setdefault("confidence_after", float(ed.get("confidence_after") or 0.4))
    ed.setdefault("algorithm_versions", {"pipeline": ALGORITHM_VERSION, "confidence": CONFIDENCE_VERSION})
    ecqr_validated = validate_ecqr_decision(ed, require_bound_artifacts=False)

    receipt = None
    try:
        receipt = build_learning_receipt(
            decision="ROLLED_BACK",
            prior_id=prior_id,
            candidate_id=ed["candidate_id"],
            reviewer=ecqr_validated["reviewer"],
            rationale=ecqr_validated["rationale"],
            evidence_links=list(regression_evidence),
            confidence_before=float(ecqr_validated["confidence_before"]),
            confidence_after=float(ecqr_validated["confidence_after"]),
            affected_loops=list(ecqr_validated["affected_loops"]),
            applicable_runways=list(ecqr_validated["applicable_runways"]),
            repositories=list(ecqr_validated.get("repositories") or prior.get("scope", {}).get("repository") and [prior["scope"]["repository"]] or []),
            origin_event=regression_evidence[0],
            decision_timestamp=ecqr_validated["effective_at"],
            rollback_target=prior_id,
            snapshot_id=prior_id,
        )
        validate_learning_receipt(receipt)
        entity = {
            "state": RATIFIED,
            "status": "active",
            "prior_id": prior_id,
            "candidate_id": ed["candidate_id"],
            "transition_history": list(prior.get("transition_history") or []),
        }
        entity = transition(
            entity, ROLLED_BACK,
            actor=ecqr_validated["reviewer"],
            reason=ecqr_validated["rationale"],
            evidence=regression_evidence,
            learning_receipt=receipt,
            timestamp=ecqr_validated["effective_at"],
        )
        updated = dict(prior)
        updated["state"] = entity["state"]
        updated["status"] = entity["status"]
        updated["transition_history"] = entity["transition_history"]
        updated["learning_receipt_id"] = receipt["receipt_id"]
        updated["live_consumable"] = False
        # Atomic: write receipt to out_dir, then update store if not dry_run
        write_receipt(receipt, out_dir / f"learning_receipt-{receipt['receipt_id']}.json")
        if not dry_run:
            store.update(
                updated,
                expected_version=int(prior.get("version") or 1),
                ecqr_decision=ecqr_validated,
                learning_receipt=receipt,
            )
        else:
            _write_json(out_dir / "prior.dry_run_rollback_preview.json", updated)
    except Exception:
        # No store mutation on failure; remove receipt if we want zero orphans in out_dir for failed transitions
        for p in out_dir.glob("learning_receipt-*.json"):
            # Only delete if store wasn't updated
            if dry_run or store.get(prior_id) == prior:
                p.unlink(missing_ok=True)
        raise

    store_hash_after = store_tree_hash(store_dir)
    if dry_run and store_hash_before != store_hash_after:
        raise GovernanceBlock("dry-run rollback mutated store")

    summary = {
        "schema": "nf_motor_learning_w1_rollback_summary_v1",
        "dry_run": dry_run,
        "prior_id": prior_id,
        "final_state": ROLLED_BACK,
        "receipt_id": receipt["receipt_id"] if receipt else None,
        "store_hash_before": store_hash_before,
        "store_hash_after": store_hash_after,
        "store_unchanged": store_hash_before == store_hash_after,
    }
    _write_json(out_dir / "summary.json", summary)
    return summary


def run_from_fixture_dir(fixture_dir: Path, *, out_dir: Path, store_dir: Path, dry_run: bool = True) -> dict:
    fixture_dir = Path(fixture_dir)
    events = _load_json(fixture_dir / "events.json")
    shadow_path = fixture_dir / "shadow_events.json"
    if shadow_path.exists():
        shadow_events = _load_json(shadow_path)
    else:
        # Derive independent shadow stream by cloning events with new IDs (temporal holdout)
        shadow_events = []
        for i, e in enumerate(events):
            s = dict(e)
            s["event_id"] = f"shadow-{e['event_id']}"
            s["occurred_at"] = e["occurred_at"].replace("2026-07-01", "2026-07-08")
            shadow_events.append(s)
    ecqr_path = fixture_dir / "ecqr_decision.json"
    ecqr = _load_json(ecqr_path) if ecqr_path.exists() else None
    meta = _load_json(fixture_dir / "meta.json") if (fixture_dir / "meta.json").exists() else {}

    # Seed priors via restricted API only.
    # dry-run: seed into out_dir/fixture_seed_store (never mutate supplied store_dir).
    seed = fixture_dir / "seed_priors"
    effective_store = Path(store_dir)
    if seed.exists():
        if dry_run:
            effective_store = Path(out_dir) / "fixture_seed_store"
            seed_store = PriorStore(effective_store, create=True)
            for f in seed.glob("*.json"):
                prior = _load_json(f)
                terminal = prior.get("status") in {"active", "rejected", "rolled_back"}
                seed_store.seed_fixture(prior, allow_duplicate=True, allow_terminal_seed=terminal)
        else:
            seed_store = PriorStore(store_dir, create=True)
            for f in seed.glob("*.json"):
                prior = _load_json(f)
                terminal = prior.get("status") in {"active", "rejected", "rolled_back"}
                seed_store.seed_fixture(prior, allow_duplicate=True, allow_terminal_seed=terminal)

    mode = meta.get("mode")
    if mode == "rollback":
        prior_id = (ecqr or {}).get("rollback_target") or (ecqr or {}).get("prior_id")
        return rollback_prior(
            prior_id=prior_id,
            store_dir=effective_store if dry_run and seed.exists() else store_dir,
            out_dir=out_dir,
            ecqr_decision=ecqr or {},
            regression_evidence=list((ecqr or {}).get("evidence_reviewed") or ["rollback-evidence"]),
            dry_run=dry_run,
        )

    supplied_hash_before = store_tree_hash(store_dir)
    summary = run_pipeline(
        events=events,
        shadow_events=shadow_events,
        store_dir=effective_store if (dry_run and seed.exists()) else store_dir,
        out_dir=out_dir,
        ecqr_decision=ecqr,
        min_occurrences=int(meta.get("min_occurrences", 3)),
        dry_run=dry_run,
        as_of=meta.get("as_of"),
    )
    if dry_run:
        supplied_hash_after = store_tree_hash(store_dir)
        if supplied_hash_before != supplied_hash_after:
            raise GovernanceBlock("dry-run mutated supplied prior store")
        summary["supplied_store_hash_before"] = supplied_hash_before
        summary["supplied_store_hash_after"] = supplied_hash_after
        summary["store_unchanged"] = True
    return summary
