"""Authoritative artifact validators — derive from inputs; reject synthetic self-hashes."""
from __future__ import annotations

import math
from typing import Any

from .errors import GovernanceBlock, SchemaError
from .hashutil import content_hash, canonical_json
from .shadow import evaluate_shadow, MIN_EVALUATED, MIN_COVERAGE, MIN_SUCCESS_RATE, MAX_FAILURES
from .confidence import compute_confidence, WEIGHTS, RATIFY_THRESHOLD
from .validated import (
    ValidatedShadow,
    ValidatedConfidence,
    ValidatedCandidate,
    _mint_shadow,
    _mint_confidence,
    _mint_candidate,
)
from . import CONFIDENCE_VERSION


def _finite_unit(x: Any, name: str) -> float:
    try:
        v = float(x)
    except (TypeError, ValueError) as exc:
        raise SchemaError(f"{name} must be float") from exc
    if not math.isfinite(v) or v < 0.0 or v > 1.0:
        raise SchemaError(f"{name} must be finite in [0,1]")
    return v


def candidate_content_hash(candidate: dict[str, Any]) -> str:
    body = {
        "candidate_id": candidate.get("candidate_id"),
        "fingerprint": candidate.get("fingerprint"),
        "recommended_action": candidate.get("recommended_action"),
        "source_event_ids": candidate.get("source_event_ids"),
        "evidence_refs": candidate.get("evidence_refs"),
        "occurrence_count": candidate.get("occurrence_count"),
        "scope": candidate.get("scope"),
    }
    return content_hash(body)


def validate_candidate_artifact(candidate: dict[str, Any] | ValidatedCandidate) -> ValidatedCandidate:
    if isinstance(candidate, ValidatedCandidate):
        candidate = candidate.as_dict()
    if not isinstance(candidate, dict):
        raise SchemaError("candidate must be object")
    for req in ("candidate_id", "fingerprint", "recommended_action", "source_event_ids", "evidence_refs"):
        if req not in candidate:
            raise GovernanceBlock(f"candidate missing {req}")
    if not candidate["candidate_id"] or not candidate["source_event_ids"]:
        raise GovernanceBlock("candidate_id and source_event_ids required")
    expected = candidate_content_hash(candidate)
    claimed = candidate.get("content_hash")
    out = dict(candidate)
    out["content_hash"] = expected
    if claimed is not None and claimed != expected:
        raise GovernanceBlock(
            f"candidate content_hash mismatch: claimed={claimed!r} recomputed={expected!r}"
        )
    return _mint_candidate(out)


def _canonical_equal(a: Any, b: Any) -> bool:
    return canonical_json(a) == canonical_json(b)


def validate_shadow_evidence_manifest(manifest: dict[str, Any], *, report: dict[str, Any]) -> str:
    if not isinstance(manifest, dict):
        raise GovernanceBlock("shadow evidence_manifest must be object")
    required = (
        "shadow_event_ids", "evidence_refs", "normalized_event_hashes",
        "successes", "failures", "abstentions", "evaluated", "coverage", "success_rate",
    )
    missing = [k for k in required if k not in manifest]
    if missing:
        raise GovernanceBlock(f"shadow evidence_manifest missing: {missing}")
    expected = content_hash(manifest)
    claimed = report.get("evidence_manifest_hash")
    if claimed is not None and claimed != expected:
        raise GovernanceBlock(
            f"shadow evidence_manifest_hash mismatch: claimed={claimed!r} recomputed={expected!r}"
        )
    return expected


def validate_shadow_report(
    shadow: dict[str, Any] | ValidatedShadow,
    *,
    candidate: dict[str, Any] | None = None,
    shadow_events: list[dict] | None = None,
    require_derivation: bool = True,
) -> ValidatedShadow:
    """
    Prefer derivation proof: require concrete normalized shadow_events + candidate,
    rerun evaluate_shadow, and require complete canonical equality with submitted artifact.
    """
    if isinstance(shadow, ValidatedShadow):
        shadow = shadow.as_dict()
    if not isinstance(shadow, dict):
        raise SchemaError("shadow must be object")

    if require_derivation:
        if candidate is None:
            raise GovernanceBlock("shadow validation requires candidate for derivation proof")
        if shadow_events is None:
            raise GovernanceBlock(
                "shadow validation requires concrete normalized shadow_events; "
                "self-hash alone is never proof"
            )
        if not isinstance(shadow_events, list) or not shadow_events:
            raise GovernanceBlock("shadow_events must be a nonempty list of normalized events")

        derived = evaluate_shadow(candidate, shadow_events)
        # Every derived key must match; no extra material keys allowed to disagree
        for key in sorted(derived.keys()):
            if key not in shadow:
                raise GovernanceBlock(f"submitted shadow missing derived field: {key}")
            if not _canonical_equal(shadow[key], derived[key]):
                raise GovernanceBlock(
                    f"shadow derivation mismatch on {key}: "
                    f"submitted≠evaluate_shadow(candidate, shadow_events)"
                )
        extra = set(shadow.keys()) - set(derived.keys())
        if extra:
            raise GovernanceBlock(f"submitted shadow has undeclared extra fields: {sorted(extra)}")
        if not _canonical_equal(shadow, derived):
            raise GovernanceBlock(
                "shadow artifact is not canonically equal to evaluate_shadow(candidate, shadow_events)"
            )
        return _mint_shadow(dict(derived))

    # Non-derivation path forbidden for ratification paths
    raise GovernanceBlock("shadow validation requires derivation proof")


def validate_confidence_artifact(
    confidence: dict[str, Any] | ValidatedConfidence,
    *,
    shadow: dict | ValidatedShadow | None = None,
    confidence_inputs: dict[str, Any] | None = None,
    require_derivation: bool = True,
) -> ValidatedConfidence:
    """
    Prefer derivation proof: require canonical confidence_inputs, rerun compute_confidence,
    and require exact component names/weights/contributions and complete artifact equality.
    """
    if isinstance(confidence, ValidatedConfidence):
        confidence = confidence.as_dict()
    if not isinstance(confidence, dict):
        raise SchemaError("confidence must be object")

    if require_derivation:
        if confidence_inputs is None:
            raise GovernanceBlock(
                "confidence validation requires canonical confidence_inputs; "
                "caller-supplied component sums alone are never proof"
            )
        required_in = (
            "occurrence_count", "outcomes_seen", "evidence_refs",
            "confidence_before", "scope", "mining_evidence_ids", "shadow_evidence_ids",
        )
        missing = [k for k in required_in if k not in confidence_inputs]
        if missing:
            raise GovernanceBlock(f"confidence_inputs missing: {missing}")

        sh_dict = shadow.as_dict() if isinstance(shadow, ValidatedShadow) else shadow
        derived = compute_confidence(
            occurrence_count=int(confidence_inputs["occurrence_count"]),
            outcomes_seen=list(confidence_inputs["outcomes_seen"]),
            evidence_refs=list(confidence_inputs["evidence_refs"]),
            shadow_report=sh_dict,
            expired_evidence=bool(confidence_inputs.get("expired_evidence", False)),
            confidence_before=float(confidence_inputs["confidence_before"]),
            scope=dict(confidence_inputs.get("scope") or {}),
            mining_evidence_ids=list(confidence_inputs["mining_evidence_ids"]),
            shadow_evidence_ids=list(confidence_inputs["shadow_evidence_ids"]),
        )

        # Exact component names
        want_names = set(WEIGHTS.keys())
        got_names = set((confidence.get("component_contributions") or {}).keys())
        der_names = set((derived.get("component_contributions") or {}).keys())
        if got_names != want_names:
            raise GovernanceBlock(
                f"confidence components must be exactly {sorted(want_names)}; got {sorted(got_names)}"
            )
        if der_names != want_names:
            raise GovernanceBlock("derived confidence components incomplete")

        for name in want_names:
            sc = (confidence.get("component_contributions") or {})[name]
            dc = derived["component_contributions"][name]
            if not _canonical_equal(sc, dc):
                raise GovernanceBlock(
                    f"confidence component {name} mismatch vs compute_confidence() "
                    f"(invented/omitted/reweighted components forbidden)"
                )
            if abs(float(sc.get("weight")) - float(WEIGHTS[name])) > 1e-12:
                raise GovernanceBlock(f"confidence component {name} weight reweighted")

        for key in (
            "schema", "algorithm_version", "confidence_before", "confidence_after",
            "component_contributions", "threshold_references", "meets_ratify_threshold",
            "evidence_ids", "mining_evidence_ids", "shadow_evidence_ids",
            "shadow_contaminated_by_mining_overlap", "overlap_event_ids",
            "promotion_authority", "advisory_only", "content_hash", "explanation",
        ):
            if key not in derived:
                continue
            if key not in confidence:
                raise GovernanceBlock(f"submitted confidence missing derived field: {key}")
            if not _canonical_equal(confidence[key], derived[key]):
                raise GovernanceBlock(
                    f"confidence derivation mismatch on {key}: "
                    f"submitted≠compute_confidence(...)"
                )

        if confidence.get("algorithm_version") != CONFIDENCE_VERSION:
            raise GovernanceBlock("confidence algorithm_version mismatch")
        if not _canonical_equal(
            {k: confidence[k] for k in sorted(confidence)},
            {k: derived[k] for k in sorted(derived)},
        ):
            raise GovernanceBlock(
                "confidence artifact is not canonically equal to compute_confidence()"
            )
        return _mint_confidence(dict(derived))

    raise GovernanceBlock("confidence validation requires derivation proof")


def unwrap_shadow(
    obj: Any,
    *,
    candidate: dict | None = None,
    shadow_events: list[dict] | None = None,
    require_derivation: bool = True,
) -> dict:
    if isinstance(obj, ValidatedShadow):
        return validate_shadow_report(
            obj.as_dict(), candidate=candidate, shadow_events=shadow_events,
            require_derivation=require_derivation,
        ).as_dict()
    if isinstance(obj, dict):
        return validate_shadow_report(
            obj, candidate=candidate, shadow_events=shadow_events,
            require_derivation=require_derivation,
        ).as_dict()
    raise GovernanceBlock("shadow artifact required")


def unwrap_confidence(
    obj: Any,
    *,
    shadow=None,
    confidence_inputs: dict | None = None,
    require_derivation: bool = True,
) -> dict:
    if isinstance(obj, ValidatedConfidence):
        return validate_confidence_artifact(
            obj.as_dict(), shadow=shadow, confidence_inputs=confidence_inputs,
            require_derivation=require_derivation,
        ).as_dict()
    if isinstance(obj, dict):
        return validate_confidence_artifact(
            obj, shadow=shadow, confidence_inputs=confidence_inputs,
            require_derivation=require_derivation,
        ).as_dict()
    raise GovernanceBlock("confidence artifact required")


def unwrap_candidate(obj: Any) -> dict:
    if isinstance(obj, ValidatedCandidate):
        return validate_candidate_artifact(obj.as_dict()).as_dict()
    if isinstance(obj, dict):
        return validate_candidate_artifact(obj).as_dict()
    raise GovernanceBlock("candidate artifact required")


def mining_evidence_manifest(candidate: dict[str, Any], mining_events: list[dict]) -> tuple[dict, str]:
    """Canonical mining evidence manifest + hash for ECQR/receipt binding."""
    if not isinstance(mining_events, list) or not mining_events:
        raise GovernanceBlock("mining_events required for mining evidence manifest")
    hashes = []
    for ev in mining_events:
        h = ev.get("content_hash") or ev.get("provenance_fingerprint")
        if not h:
            raise GovernanceBlock("mining event missing content_hash/provenance_fingerprint")
        hashes.append(h)
    manifest = {
        "source_event_ids": list(candidate.get("source_event_ids") or []),
        "evidence_refs": list(candidate.get("evidence_refs") or []),
        "normalized_event_hashes": sorted(hashes),
        "occurrence_count": int(candidate.get("occurrence_count") or 0),
        "outcomes_seen": list(candidate.get("outcomes_seen") or []),
    }
    return manifest, content_hash(manifest)


def assert_confidence_inputs_canonical(
    confidence_inputs: dict[str, Any],
    *,
    candidate: dict[str, Any],
    shadow: dict[str, Any],
) -> dict[str, Any]:
    """
    Do not accept unconstrained confidence_inputs.
    Enforce exact equality with canonical candidate/shadow fields.
    """
    if not isinstance(confidence_inputs, dict):
        raise GovernanceBlock("confidence_inputs must be object")
    canonical = {
        "occurrence_count": int(candidate["occurrence_count"]),
        "outcomes_seen": list(candidate.get("outcomes_seen") or []),
        "evidence_refs": list(candidate.get("evidence_refs") or []),
        "confidence_before": float(confidence_inputs.get("confidence_before", 0.0)),
        "scope": dict(candidate.get("scope") or {}),
        "mining_evidence_ids": list(candidate.get("source_event_ids") or []),
        "shadow_evidence_ids": list(shadow.get("shadow_event_ids") or []),
        "expired_evidence": bool(confidence_inputs.get("expired_evidence", False)),
    }
    checks = (
        ("occurrence_count", canonical["occurrence_count"], confidence_inputs.get("occurrence_count")),
        ("evidence_refs", canonical["evidence_refs"], list(confidence_inputs.get("evidence_refs") or [])),
        ("scope", canonical["scope"], dict(confidence_inputs.get("scope") or {})),
        ("mining_evidence_ids", canonical["mining_evidence_ids"], list(confidence_inputs.get("mining_evidence_ids") or [])),
        ("shadow_evidence_ids", canonical["shadow_evidence_ids"], list(confidence_inputs.get("shadow_evidence_ids") or [])),
        ("outcomes_seen", canonical["outcomes_seen"], list(confidence_inputs.get("outcomes_seen") or [])),
    )
    for name, want, got in checks:
        if name in ("evidence_refs", "mining_evidence_ids", "shadow_evidence_ids", "outcomes_seen"):
            if list(want) != list(got):
                raise GovernanceBlock(
                    f"confidence_inputs.{name} not canonical: got={got!r} want={want!r}"
                )
        elif name == "scope":
            if not _canonical_equal(want, got):
                raise GovernanceBlock(f"confidence_inputs.scope not canonical vs candidate.scope")
        else:
            if int(got) != int(want):
                raise GovernanceBlock(
                    f"confidence_inputs.{name} not canonical: got={got!r} want={want!r}"
                )
    # Return canonical form with caller confidence_before / expired preserved after equality on others
    return {
        **canonical,
        "confidence_before": float(confidence_inputs.get("confidence_before", 0.0)),
        "expired_evidence": bool(confidence_inputs.get("expired_evidence", False)),
    }


def recompute_normalized_event_hashes(ev: dict[str, Any]) -> tuple[str, str]:
    """Recompute content_hash and provenance_fingerprint from substantive normalized fields."""
    body = {
        "event_id": str(ev.get("event_id")),
        "event_type": ev.get("event_type"),
        "source": str(ev.get("source")),
        "occurred_at": ev.get("occurred_at"),
        "observed_at": ev.get("observed_at"),
        "actor": ev.get("actor"),
        "stage": ev.get("stage"),
        "provider": ev.get("provider"),
        "action_attempted": str(ev.get("action_attempted")),
        "outcome": ev.get("outcome"),
        "error_class": ev.get("error_class"),
        "recovery_path": ev.get("recovery_path"),
        "repository": ev.get("repository"),
        "runway": ev.get("runway"),
        "loop_id": ev.get("loop_id"),
        "evidence_refs": list(ev.get("evidence_refs") or []),
        "raw_evidence_ref": ev.get("raw_evidence_ref") or f"raw://{ev.get('event_id')}",
    }
    # evidence_refs must be canonical-sorted for stable hash
    body["evidence_refs"] = sorted(str(x) for x in body["evidence_refs"] if x is not None and str(x).strip())
    h = content_hash(body)
    return h, h


def assert_normalized_event_provenance(ev: dict[str, Any], *, label: str = "event") -> dict[str, Any]:
    """Reject stale content_hash / provenance_fingerprint after substantive field changes."""
    if not isinstance(ev, dict):
        raise GovernanceBlock(f"{label} must be object")
    for req in (
        "event_id", "content_hash", "provenance_fingerprint",
        "evidence_refs", "schema", "action_attempted", "outcome",
        "event_type", "source", "occurred_at",
    ):
        if req not in ev or ev.get(req) in (None, ""):
            raise GovernanceBlock(f"{label} missing {req}")
    if not isinstance(ev.get("evidence_refs"), list):
        raise GovernanceBlock(f"{label} evidence_refs must be list")
    if not ev.get("raw_evidence_ref"):
        raise GovernanceBlock(f"{label} missing raw_evidence_ref")
    want_ch, want_pf = recompute_normalized_event_hashes(ev)
    if ev.get("content_hash") != want_ch:
        raise GovernanceBlock(
            f"{label} content_hash stale after substantive field change "
            f"(stored={ev.get('content_hash')!r} recomputed={want_ch!r})"
        )
    if ev.get("provenance_fingerprint") != want_pf:
        raise GovernanceBlock(
            f"{label} provenance_fingerprint stale after substantive field change "
            f"(stored={ev.get('provenance_fingerprint')!r} recomputed={want_pf!r})"
        )
    return ev


def assert_normalized_events_provenance(events: list[dict], *, label: str) -> list[dict]:
    if not isinstance(events, list) or not events:
        raise GovernanceBlock(f"{label} must be a nonempty list")
    return [assert_normalized_event_provenance(ev, label=f"{label}[{i}]") for i, ev in enumerate(events)]


def assert_mining_events_canonical(mining_events: list[dict]) -> list[dict]:
    """Validate every normalized mining event carries identity/provenance fields and fresh hashes."""
    return assert_normalized_events_provenance(mining_events, label="mining_events")


def assert_candidate_derived_from_mining(
    candidate: dict[str, Any],
    mining_events: list[dict],
) -> dict[str, Any]:
    """
    Re-run extract_many → mine_patterns from concrete mining events and require
    the submitted candidate to be canonically identical to the derived candidate,
    including candidate_id. No fallback to a different derived candidate.
    """
    from .extract import extract_many
    from .mine import mine_patterns

    events = assert_mining_events_canonical(mining_events)
    event_ids = sorted({e["event_id"] for e in events})
    signals = extract_many(events)
    min_occ = int(candidate.get("min_occurrences_required") or 3)
    derived_list = mine_patterns(signals, min_occurrences=min_occ)
    if not derived_list:
        raise GovernanceBlock("mining events produced no derived candidates")

    want_id = candidate.get("candidate_id")
    derived = None
    for d in derived_list:
        if d.get("candidate_id") == want_id:
            derived = d
            break
    if derived is None:
        raise GovernanceBlock(
            f"candidate_id {want_id!r} not among derived mining candidates; "
            f"renamed/alternate candidate IDs are rejected "
            f"(derived={[d.get('candidate_id') for d in derived_list]!r})"
        )

    # Exact equality on identity-bearing fields including candidate_id
    if candidate.get("candidate_id") != derived.get("candidate_id"):
        raise GovernanceBlock("candidate.candidate_id mismatch derived candidate_id")
    sub_ids = list(candidate.get("source_event_ids") or [])
    der_ids = list(derived.get("source_event_ids") or [])
    if sorted(sub_ids) != sorted(event_ids):
        raise GovernanceBlock(
            f"candidate.source_event_ids must equal mining event IDs used for derivation; "
            f"candidate={sorted(sub_ids)!r} mining={event_ids!r}"
        )
    if sorted(sub_ids) != sorted(der_ids):
        raise GovernanceBlock(
            "candidate.source_event_ids mismatch derived mining pattern source_event_ids"
        )
    if int(candidate.get("occurrence_count") or 0) != len(event_ids):
        raise GovernanceBlock(
            "candidate.occurrence_count must equal unique mining-event count"
        )
    if int(candidate.get("occurrence_count") or 0) != int(derived.get("occurrence_count") or 0):
        raise GovernanceBlock("candidate.occurrence_count mismatch derived occurrence_count")
    if list(candidate.get("evidence_refs") or []) != list(derived.get("evidence_refs") or []):
        raise GovernanceBlock("candidate.evidence_refs mismatch derived mining evidence refs")
    if list(candidate.get("outcomes_seen") or []) != list(derived.get("outcomes_seen") or []):
        raise GovernanceBlock("candidate.outcomes_seen mismatch derived outcomes")
    if not _canonical_equal(candidate.get("fingerprint"), derived.get("fingerprint")):
        raise GovernanceBlock("candidate.fingerprint mismatch derived fingerprint")
    if not _canonical_equal(candidate.get("scope") or {}, derived.get("scope") or {}):
        raise GovernanceBlock("candidate.scope mismatch derived scope")
    if candidate.get("recommended_action") != derived.get("recommended_action"):
        raise GovernanceBlock("candidate.recommended_action mismatch derived recommended_action")
    fp = candidate.get("fingerprint") or {}
    dfp = derived.get("fingerprint") or {}
    for k in ("action_attempted", "recovery_path", "error_class"):
        if fp.get(k) != dfp.get(k):
            raise GovernanceBlock(f"candidate.fingerprint.{k} mismatch derived mining pattern")
    if candidate.get("fingerprint_hash") not in (None, derived.get("fingerprint_hash")):
        if candidate.get("fingerprint_hash") != derived.get("fingerprint_hash"):
            raise GovernanceBlock("candidate.fingerprint_hash mismatch derived fingerprint_hash")
    return validate_candidate_artifact(candidate).as_dict()


def prior_payload_material(
    *,
    candidate: dict[str, Any],
    prior_id: str,
    status: str,
    state: str,
) -> dict[str, Any]:
    cand = unwrap_candidate(candidate)
    fp = cand.get("fingerprint") or {}
    return {
        "prior_id": prior_id,
        "status": status,
        "state": state,
        "candidate_id": cand.get("candidate_id"),
        "action_attempted": fp.get("action_attempted"),
        "recommended_action": cand.get("recommended_action"),
        "recovery_path": fp.get("recovery_path"),
        "error_class": fp.get("error_class"),
        "fingerprint": fp,
        "scope": cand.get("scope") or {},
        "evidence_refs": list(cand.get("evidence_refs") or []),
        "source_event_ids": list(cand.get("source_event_ids") or []),
        "expected_outcome": cand.get("expected_outcome"),
    }


def compute_prior_payload_hash(
    *,
    candidate: dict[str, Any],
    prior_id: str,
    status: str,
    state: str,
) -> str:
    return content_hash(prior_payload_material(
        candidate=candidate, prior_id=prior_id, status=status, state=state,
    ))


def build_canonical_prior(
    *,
    candidate: dict[str, Any],
    prior_id: str,
    status: str,
    state: str,
    learning_receipt_id: str,
    transition_history: list,
    prior_payload_hash: str,
    existing: dict | None = None,
    extra: dict | None = None,
) -> dict[str, Any]:
    """Build reference prior internally from validated candidate — ignore caller semantics."""
    cand = unwrap_candidate(candidate)
    fp = cand.get("fingerprint") or {}
    body: dict[str, Any] = {
        "schema": "nf_motor_learning_prior_v1",
        "prior_id": prior_id,
        "status": status,
        "state": state,
        "action_attempted": fp.get("action_attempted"),
        "recommended_action": cand.get("recommended_action"),
        "expected_outcome": cand.get("expected_outcome") or "success",
        "error_class": fp.get("error_class"),
        "recovery_path": fp.get("recovery_path"),
        "fingerprint": fp,
        "scope": cand.get("scope") or {},
        "evidence_refs": list(cand.get("evidence_refs") or []),
        "source_event_ids": list(cand.get("source_event_ids") or []),
        "learning_receipt_id": learning_receipt_id,
        "candidate_id": cand.get("candidate_id"),
        "transition_history": list(transition_history or []),
        "prior_payload_hash": prior_payload_hash,
        "live_consumable": False,
        "store_kind": "w1_reference",
        "w2_activation_required": True,
        "activation_authority": False,
        "fixture_seeded": False,
        "supersedes": None,
        "superseded_by": None,
        "expires_at": None,
    }
    if extra:
        # Only allow governed metadata keys, never semantic overrides
        for k in (
            "confidence_after", "expires_at", "supersedes", "dry_run",
            "live_promotion", "w2_activation_contract",
            "rollback_target", "rollback_target_prior_content_hash",
            "rollback_target_version", "prior_ratification_receipt_id",
        ):
            if k in extra and extra[k] is not None:
                body[k] = extra[k]
    want = compute_prior_payload_hash(
        candidate=cand, prior_id=prior_id, status=status, state=state,
    )
    if prior_payload_hash != want:
        raise GovernanceBlock("prior_payload_hash mismatches canonical prior payload")
    return body


def merge_event_identity_ledger(
    durable: dict | None,
    update: dict | None,
) -> dict[str, Any]:
    """
    Monotonic merge: never replace/remove historic identities.
    Reject changed historic records and updates that omit durable history.
    """
    empty = {"schema": "nf_motor_learning_event_identity_ledger_v1", "events": {}}
    base = dict(durable or empty)
    base.setdefault("schema", empty["schema"])
    base_events = dict(base.get("events") or {})
    if update is None:
        return {"schema": base.get("schema", empty["schema"]), "events": base_events}
    if not isinstance(update, dict):
        raise GovernanceBlock("event_ledger_update must be object")
    upd_events = update.get("events")
    if upd_events is None:
        return {"schema": base.get("schema", empty["schema"]), "events": base_events}
    if not isinstance(upd_events, dict):
        raise GovernanceBlock("event_ledger_update.events must be object")
    # Full-ledger snapshots must preserve every historic identity
    durable_ids = set(base_events)
    update_ids = set(upd_events)
    missing = durable_ids - update_ids
    if missing:
        raise GovernanceBlock(
            f"ledger update removes historic event identities: {sorted(missing)!r}"
        )
    out = dict(base_events)
    for eid, rec in upd_events.items():
        if eid in out:
            prev = out[eid]
            # Normalize string legacy form
            if isinstance(prev, str):
                prev = {"content_hash": prev, "provenance_fingerprint": prev}
            if isinstance(rec, str):
                rec = {"content_hash": rec, "provenance_fingerprint": rec}
            if prev.get("content_hash") != rec.get("content_hash") or \
               prev.get("provenance_fingerprint") != rec.get("provenance_fingerprint"):
                raise GovernanceBlock(
                    f"ledger update changes historic identity for event_id={eid!r}"
                )
            out[eid] = prev
        else:
            if isinstance(rec, str):
                rec = {"content_hash": rec, "provenance_fingerprint": rec}
            out[eid] = rec
    return {"schema": update.get("schema") or base.get("schema") or empty["schema"], "events": out}

