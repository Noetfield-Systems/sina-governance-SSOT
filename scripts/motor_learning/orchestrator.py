"""End-to-end W1 Motor Learning pipeline. Reference artifacts only; never live-consumable."""
from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from .normalize import normalize_many
from .extract import extract_many
from .mine import mine_patterns
from .prior_store import PriorStore, store_tree_hash, W2_ACTIVATION_CONTRACT
from .similarity import rank as rank_similarity
from .confidence import compute_confidence
from .shadow import evaluate_shadow, assert_shadow_independence, require_ratifiable_shadow
from .ecqr import validate_ecqr_decision, fixture_compile_ecqr
from .lifecycle import transition, PROPOSED, SHADOW, RATIFIED, REJECTED, ROLLED_BACK
from .receipt import build_learning_receipt, validate_and_mint_receipt, write_receipt
from .event_registry import EventRegistry
from .errors import GovernanceBlock, MotorLearningError, SchemaError
from .hashutil import content_hash
from .atomic import atomic_terminal_commit, write_failed_attempt
from .validated import mint_w1_reference_store_capability, is_w1_reference_store_capability
from . import ALGORITHM_VERSION, CONFIDENCE_VERSION


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def _candidate_hash(entity: dict) -> str:
    return content_hash({
        "candidate_id": entity.get("candidate_id"),
        "fingerprint": entity.get("fingerprint"),
        "recommended_action": entity.get("recommended_action"),
        "source_event_ids": entity.get("source_event_ids"),
        "evidence_refs": entity.get("evidence_refs"),
    })


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
    store_capability=None,
    allow_store_persist: bool = False,
    inject_failure_after: str | None = None,
    event_ledger_path: Path | None = None,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    store_dir = Path(store_dir)
    store_hash_before = store_tree_hash(store_dir)

    # Event identity ledger: never write into live store_dir until atomic commit.
    # Persistence-capable callers may pass a durable shared ledger path for cross-run collisions.
    if event_ledger_path is not None:
        ledger_path = Path(event_ledger_path)
    else:
        ledger_path = out_dir / "event_identity_ledger.json"
        # If a durable store ledger already exists, load from a working copy under out_dir
        durable = store_dir / "event_identity_ledger.json"
        if durable.exists() and not dry_run:
            import shutil as _shutil
            _shutil.copy2(durable, ledger_path)

    if not dry_run:
        if not allow_store_persist or not is_w1_reference_store_capability(store_capability):
            raise GovernanceBlock(
                "run_pipeline(dry_run=False) requires allow_store_persist=True and "
                "mint_w1_reference_store_capability(); W1 never mints live_consumable authority"
            )
        # Do not create/mutate store_dir until atomic commit
        store = PriorStore(store_dir, create=False) if store_dir.exists() else PriorStore(
            out_dir / "_ephemeral_search_store", create=True
        )
    else:
        # Dry-run must never create files under store_dir
        if store_dir.exists():
            store = PriorStore(store_dir, create=False)
        else:
            store = PriorStore(out_dir / "_ephemeral_search_store", create=True)

    registry = EventRegistry(ledger_path)

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
    ecqr_original = copy.deepcopy(ecqr_decision) if ecqr_decision else None
    ecqr_original_bytes = json.dumps(ecqr_decision, sort_keys=True).encode() if ecqr_decision else None
    ok = True

    if primary and primary.get("meets_threshold") and not primary.get("contradiction"):
        entity = dict(primary)
        if entity["state"] == PROPOSED:
            entity = transition(
                entity, SHADOW,
                actor="motor_learning_w1_orchestrator",
                reason="enter_shadow_evaluation",
                evidence=entity["evidence_refs"],
            )

        if shadow_events is None:
            blocked_reason = "shadow_events_required"
            final_state = entity.get("state")
            ok = False
        else:
            sh_reg = EventRegistry(out_dir / "shadow_event_registry.json")
            sh_accepted, _ = normalize_many(shadow_events, event_registry=sh_reg)
            try:
                assert_shadow_independence(
                    candidate=entity,
                    mining_events=accepted,
                    shadow_events=sh_accepted,
                )
            except GovernanceBlock as exc:
                blocked_reason = str(exc)
                final_state = entity.get("state")
                ok = False
                _write_json(out_dir / "independence_reject.json", {"blocked_reason": blocked_reason})
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
                    shadow_evidence_ids=list(shadow_report.get("shadow_event_ids") or []),
                )
                # Also block on evidence-ref overlap via confidence
                mine_refs = set(entity.get("evidence_refs") or [])
                sh_refs = set(shadow_report.get("evidence_refs") or [])
                if mine_refs & sh_refs:
                    confidence["meets_ratify_threshold"] = False
                    confidence["shadow_contaminated_by_mining_overlap"] = True
                if not shadow_report.get("ratifiable"):
                    confidence["meets_ratify_threshold"] = False
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

                if ecqr_decision and not machine_veto and not blocked_reason:
                    try:
                        # Compile fixture placeholders into a NEW dict; never mutate original
                        compiled = fixture_compile_ecqr(
                            ecqr_decision,
                            candidate=entity,
                            shadow=shadow_report,
                            confidence=confidence,
                            mining_event_ids=list(entity.get("source_event_ids") or []),
                            shadow_event_ids=list(shadow_report.get("shadow_event_ids") or []),
                        )
                        # Prove original fixture unchanged
                        if ecqr_original_bytes is not None:
                            now_bytes = json.dumps(ecqr_decision, sort_keys=True).encode()
                            if now_bytes != ecqr_original_bytes:
                                raise GovernanceBlock("ECQR fixture mutated during pipeline (forbidden)")

                        ecqr_validated = validate_ecqr_decision(
                            compiled,
                            confidence=confidence,
                            shadow=shadow_report,
                            candidate=entity,
                        )
                        if ecqr_validated.decision == "RATIFIED":
                            require_ratifiable_shadow(shadow_report)
                    except (GovernanceBlock, SchemaError) as exc:
                        blocked_reason = str(exc)
                        ecqr_validated = None
                        ok = False
                elif machine_veto and ecqr_decision:
                    blocked_reason = "DUPLICATE_CONFLICT_REVIEW_REQUIRED"
                    ok = False
                    _write_json(out_dir / "preserved_reviewer_decision.json", ecqr_original)

                if ecqr_validated and ecqr_validated.decision in ("RATIFIED", "REJECTED"):
                    decision = ecqr_validated.decision
                    ed = ecqr_validated.as_dict()
                    ts = ed["effective_at"]
                    prior_id = ed.get("prior_id") or f"prior-{entity['candidate_id']}"
                    try:
                        cand_hash = _candidate_hash(entity)
                        receipt = build_learning_receipt(
                            decision=decision,
                            prior_id=prior_id,
                            candidate_id=entity["candidate_id"],
                            reviewer=ed["reviewer"],
                            rationale=ed["rationale"],
                            evidence_links=list(ed["evidence_reviewed"]),
                            confidence_before=confidence["confidence_before"],
                            confidence_after=confidence["confidence_after"],
                            affected_loops=list(ed["affected_loops"]),
                            applicable_runways=list(ed["applicable_runways"]),
                            repositories=list(ed.get("repositories") or []),
                            origin_event=entity["source_event_ids"][0],
                            decision_timestamp=ts,
                            expiry=ed.get("expires_at"),
                            supersedes=ed.get("supersedes"),
                            snapshot_id=prior_id,
                            shadow_evidence_path=str(out_dir / "shadow_report.json"),
                            shadow_id=shadow_report["shadow_id"],
                            shadow_hash=shadow_report["content_hash"],
                            shadow_evidence_manifest_hash=shadow_report["evidence_manifest_hash"],
                            confidence_hash=confidence["content_hash"],
                            similarity_score=(similarity_rankings[0]["total_score"] if similarity_rankings else None),
                            ecqr_decision_hash=ecqr_validated.decision_hash,
                            candidate_hash=cand_hash,
                        )
                        validated_receipt = validate_and_mint_receipt(receipt)
                        target_state = RATIFIED if decision == "RATIFIED" else REJECTED
                        entity = transition(
                            entity, target_state,
                            actor=ed["reviewer"],
                            reason=ed["rationale"],
                            evidence=ed["evidence_reviewed"],
                            learning_receipt=validated_receipt,
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
                            "expires_at": ed.get("expires_at"),
                            "supersedes": ed.get("supersedes"),
                            "version": 1,
                            "transition_history": entity.get("transition_history"),
                            "dry_run": dry_run,
                            "live_promotion": False,
                            "live_consumable": False,  # W1 never mints live authority
                            "fixture_seeded": False,
                            "store_kind": "w1_reference",
                            "w2_activation_required": True,
                            "activation_authority": False,
                            "w2_activation_contract": W2_ACTIVATION_CONTRACT,
                        }
                        # Reference bundle always under out_dir
                        _write_json(out_dir / "reference_bundle.json", {
                            "schema": "nf_motor_learning_w1_reference_bundle_v1",
                            "prior": prior,
                            "receipt": receipt,
                            "ecqr_decision_hash": ecqr_validated.decision_hash,
                            "shadow_evidence_manifest_hash": shadow_report["evidence_manifest_hash"],
                            "live_consumable": False,
                            "w2_activation_required": True,
                        })

                        if dry_run:
                            write_receipt(receipt, out_dir / f"learning_receipt-{receipt['receipt_id']}.json")
                            _write_json(out_dir / "prior.dry_run_preview.json", prior)
                            final_state = entity["state"]
                        else:
                            def _commit(staging_root: Path) -> None:
                                st = PriorStore(
                                    staging_root,
                                    create=True,
                                    store_kind="w1_reference",
                                    store_capability=store_capability,
                                    allow_persist=True,
                                )
                                st.create(
                                    prior,
                                    allow_duplicate=False,
                                    expected_version=1,
                                    ecqr_decision=ecqr_validated,
                                    learning_receipt=validated_receipt,
                                    candidate=entity,
                                    shadow=shadow_report,
                                    confidence=confidence,
                                )
                                # Promote durable event identity ledger into store only on commit
                                import shutil as _shutil
                                dest = Path(staging_root) / "event_identity_ledger.json"
                                _shutil.copy2(ledger_path, dest)

                            atomic_terminal_commit(
                                store_dir=store_dir,
                                out_dir=out_dir,
                                receipt=receipt,
                                prior=prior,
                                transition_record=(entity.get("transition_history") or [None])[-1],
                                commit_fn=_commit,
                                inject_failure_after=inject_failure_after,
                            )
                            final_state = entity["state"]
                    except Exception as exc:
                        ok = False
                        blocked_reason = f"terminal_commit_failed:{exc}"
                        write_failed_attempt(out_dir, stage="terminal", error=str(exc))
                        # Remove any authoritative receipt leftovers
                        for p in out_dir.glob("learning_receipt-*.json"):
                            p.unlink(missing_ok=True)
                        receipt = None
                        prior = None
                        final_state = entity.get("state")
                        if not dry_run:
                            raise MotorLearningError(blocked_reason) from exc
                else:
                    final_state = entity.get("state")
                    if not blocked_reason:
                        blocked_reason = "no_ecqr_decision_or_blocked"
                        ok = False
    elif primary:
        final_state = primary.get("state")
        blocked_reason = primary.get("not_ratifiable_reason") or "candidate_not_ready"
        ok = False
    else:
        blocked_reason = "no_candidates"
        ok = False

    store_hash_after = store_tree_hash(store_dir)
    if dry_run and store_hash_before != store_hash_after:
        raise GovernanceBlock("dry-run mutated prior store (forbidden)")

    # Prove ECQR original unchanged
    if ecqr_original_bytes is not None and ecqr_decision is not None:
        if json.dumps(ecqr_decision, sort_keys=True).encode() != ecqr_original_bytes:
            raise GovernanceBlock("ECQR decision mutated after pipeline (forbidden)")

    summary = {
        "schema": "nf_motor_learning_w1_run_summary_v1",
        "algorithm_version": ALGORITHM_VERSION,
        "dry_run": dry_run,
        "ok": ok and (blocked_reason is None or (receipt is not None and final_state in (RATIFIED, REJECTED))),
        "live_promotion": False,
        "live_consumable": False,
        "model_learning": False,
        "store_kind": "w1_reference",
        "w2_activation_required": True,
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
        "ecqr_decision": ecqr_validated.decision if ecqr_validated else None,
        "final_state": final_state,
        "prior_id": prior["prior_id"] if prior else None,
        "receipt_id": receipt["receipt_id"] if receipt else None,
        "blocked_reason": blocked_reason,
        "store_hash_before": store_hash_before,
        "store_hash_after": store_hash_after,
        "store_unchanged": store_hash_before == store_hash_after,
        "out_dir": str(out_dir),
    }
    # ok true only when requested terminal op succeeded OR non-terminal observe succeeded without governance failure claiming success
    if blocked_reason and receipt is None:
        summary["ok"] = False
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
    store_capability=None,
    allow_store_persist: bool = False,
    inject_failure_after: str | None = None,
) -> dict[str, Any]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    store_dir = Path(store_dir)
    store_hash_before = store_tree_hash(store_dir)

    if not dry_run:
        if not allow_store_persist or not is_w1_reference_store_capability(store_capability):
            raise GovernanceBlock("rollback dry_run=False requires w1_reference store capability")
        store = PriorStore(
            store_dir, create=True, store_kind="w1_reference",
            store_capability=store_capability, allow_persist=True,
        )
    else:
        store = PriorStore(store_dir, create=not dry_run) if store_dir.exists() else PriorStore(store_dir, create=True)

    prior = store.get(prior_id)
    if not prior:
        # dry-run seed path may have prior only after seed
        raise GovernanceBlock(f"prior not found: {prior_id}")
    if prior.get("status") != "active" and prior.get("state") != RATIFIED:
        raise GovernanceBlock(f"prior {prior_id} is not RATIFIED/active")

    # Compile without mutating original
    original_bytes = json.dumps(ecqr_decision, sort_keys=True).encode()
    ed = copy.deepcopy(ecqr_decision)
    ed["decision"] = "ROLLED_BACK"
    ed.setdefault("rollback_target", prior_id)
    ed.setdefault("prior_id", prior_id)
    ed.setdefault("candidate_id", prior.get("candidate_id") or f"cand-rollback-{prior_id}")
    ed.setdefault("shadow_result_ref", "shadow:rollback-n/a")
    ed.setdefault("evidence_reviewed", list(regression_evidence))
    if not regression_evidence:
        raise GovernanceBlock("rollback requires regression_evidence")
    ed.setdefault("confidence_before", float(prior.get("confidence_after") or 0.8))
    ed.setdefault("confidence_after", float(ed.get("confidence_after") or 0.4))
    ed.setdefault("algorithm_versions", {"pipeline": ALGORITHM_VERSION, "confidence": CONFIDENCE_VERSION})

    ecqr_validated = validate_ecqr_decision(ed, require_bound_artifacts=False)
    if json.dumps(ecqr_decision, sort_keys=True).encode() != original_bytes:
        raise GovernanceBlock("ECQR decision mutated during rollback (forbidden)")

    try:
        receipt = build_learning_receipt(
            decision="ROLLED_BACK",
            prior_id=prior_id,
            candidate_id=ed["candidate_id"],
            reviewer=ecqr_validated.as_dict()["reviewer"],
            rationale=ecqr_validated.as_dict()["rationale"],
            evidence_links=list(regression_evidence),
            confidence_before=float(ecqr_validated.as_dict()["confidence_before"]),
            confidence_after=float(ecqr_validated.as_dict()["confidence_after"]),
            affected_loops=list(ecqr_validated.as_dict()["affected_loops"]),
            applicable_runways=list(ecqr_validated.as_dict()["applicable_runways"]),
            repositories=list(
                ecqr_validated.as_dict().get("repositories")
                or ([prior["scope"]["repository"]] if prior.get("scope", {}).get("repository") else [])
            ),
            origin_event=regression_evidence[0],
            decision_timestamp=ecqr_validated.as_dict()["effective_at"],
            rollback_target=prior_id,
            snapshot_id=prior_id,
        )
        validated_receipt = validate_and_mint_receipt(receipt)
        entity = {
            "state": RATIFIED,
            "status": "active",
            "prior_id": prior_id,
            "candidate_id": ed["candidate_id"],
            "transition_history": list(prior.get("transition_history") or []),
        }
        entity = transition(
            entity, ROLLED_BACK,
            actor=ecqr_validated.as_dict()["reviewer"],
            reason=ecqr_validated.as_dict()["rationale"],
            evidence=regression_evidence,
            learning_receipt=validated_receipt,
            timestamp=ecqr_validated.as_dict()["effective_at"],
        )
        updated = dict(prior)
        updated["state"] = entity["state"]
        updated["status"] = entity["status"]
        updated["transition_history"] = entity["transition_history"]
        updated["learning_receipt_id"] = receipt["receipt_id"]
        updated["live_consumable"] = False
        updated["store_kind"] = "w1_reference"
        updated["activation_authority"] = False

        if dry_run:
            write_receipt(receipt, out_dir / f"learning_receipt-{receipt['receipt_id']}.json")
            _write_json(out_dir / "prior.dry_run_rollback_preview.json", updated)
        else:
            def _commit(staging_root: Path) -> None:
                st = PriorStore(
                    staging_root, create=True, store_kind="w1_reference",
                    store_capability=store_capability, allow_persist=True,
                )
                st.update(
                    updated,
                    expected_version=int(prior.get("version") or 1),
                    ecqr_decision=ecqr_validated,
                    learning_receipt=validated_receipt,
                )

            atomic_terminal_commit(
                store_dir=store_dir,
                out_dir=out_dir,
                receipt=receipt,
                prior=updated,
                transition_record=(entity.get("transition_history") or [None])[-1],
                commit_fn=_commit,
                inject_failure_after=inject_failure_after,
            )
    except Exception as exc:
        for p in out_dir.glob("learning_receipt-*.json"):
            p.unlink(missing_ok=True)
        write_failed_attempt(out_dir, stage="rollback", error=str(exc))
        if isinstance(exc, MotorLearningError):
            raise
        raise MotorLearningError(f"rollback failed: {exc}") from exc

    store_hash_after = store_tree_hash(store_dir)
    if dry_run and store_hash_before != store_hash_after:
        raise GovernanceBlock("dry-run rollback mutated store")

    summary = {
        "schema": "nf_motor_learning_w1_rollback_summary_v1",
        "ok": True,
        "dry_run": dry_run,
        "prior_id": prior_id,
        "final_state": ROLLED_BACK,
        "receipt_id": receipt["receipt_id"],
        "live_consumable": False,
        "store_hash_before": store_hash_before,
        "store_hash_after": store_hash_after,
        "store_unchanged": store_hash_before == store_hash_after,
    }
    _write_json(out_dir / "summary.json", summary)
    return summary


def run_from_fixture_dir(
    fixture_dir: Path,
    *,
    out_dir: Path,
    store_dir: Path,
    dry_run: bool = True,
    store_capability=None,
    allow_store_persist: bool = False,
    inject_failure_after: str | None = None,
) -> dict:
    fixture_dir = Path(fixture_dir)
    events = _load_json(fixture_dir / "events.json")
    shadow_path = fixture_dir / "shadow_events.json"
    if not shadow_path.exists():
        # No clone fallback — missing shadow blocks ratification paths
        shadow_events = None
    else:
        shadow_events = _load_json(shadow_path)
    ecqr_path = fixture_dir / "ecqr_decision.json"
    ecqr = _load_json(ecqr_path) if ecqr_path.exists() else None
    meta = _load_json(fixture_dir / "meta.json") if (fixture_dir / "meta.json").exists() else {}

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
            if not allow_store_persist or not is_w1_reference_store_capability(store_capability):
                raise GovernanceBlock("fixture seed persist requires w1_reference capability")
            seed_store = PriorStore(
                store_dir, create=True, store_kind="w1_reference",
                store_capability=store_capability, allow_persist=True,
            )
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
            store_capability=store_capability,
            allow_store_persist=allow_store_persist,
            inject_failure_after=inject_failure_after,
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
        store_capability=store_capability,
        allow_store_persist=allow_store_persist,
        inject_failure_after=inject_failure_after,
    )
    if dry_run:
        supplied_hash_after = store_tree_hash(store_dir)
        if supplied_hash_before != supplied_hash_after:
            raise GovernanceBlock("dry-run mutated supplied prior store")
        summary["supplied_store_hash_before"] = supplied_hash_before
        summary["supplied_store_hash_after"] = supplied_hash_after
        summary["store_unchanged"] = True
    return summary
