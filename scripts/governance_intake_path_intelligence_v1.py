#!/usr/bin/env python3
"""Evidence-based intake path intelligence — no hardcoded folder names."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
PATH_RUBRIC = ROOT / "data/governance_intake_path_rubric_v1.json"


def load_path_rubric() -> dict:
    return json.loads(PATH_RUBRIC.read_text(encoding="utf-8"))


def path_parts_relative(path: Path, intake_root: Path) -> list[str]:
    try:
        rel = path.resolve().relative_to(intake_root.resolve())
    except ValueError:
        rel = path
    return list(rel.parts[:-1])


def _import_thread_helpers():
    from governance_thread_intelligence_v1 import (  # noqa: WPS433
        has_edit_log,
        parse_edit_log,
        role_sort_key,
    )

    return has_edit_log, parse_edit_log, role_sort_key


def extract_filename_timestamp(path: Path) -> float:
    m = re.search(r"(20\d{6})-(\d{4})", path.name)
    if not m:
        return 0.0
    try:
        from datetime import datetime, timezone

        dt = datetime.strptime(f"{m.group(1)}{m.group(2)}", "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return 0.0


def extract_filename_version_tuple(path: Path) -> tuple[int, ...]:
    name = path.name.lower()
    m = re.search(r"v0[_\.]?1[_\.]?(\d+)", name)
    if m:
        return (0, 1, int(m.group(1)))
    m = re.search(r"v0[_\.]?(\d+)[_\.](\d+)", name)
    if m:
        return (0, int(m.group(1)), int(m.group(2)))
    parts = re.findall(r"[0-9]+", name)
    return tuple(int(p) for p in parts) if parts else (0,)


def compute_artifact_evidence(
    path: Path,
    intake_root: Path,
    scored: dict,
    text: str,
    rubric: dict,
) -> dict[str, Any]:
    signals = rubric.get("evidence_signals", {})
    parts = path_parts_relative(path, intake_root)
    depth = len(parts)
    depth_score = min(40, depth * signals.get("path_depth", 8))
    ts = extract_filename_timestamp(path)
    dated_score = signals.get("filename_timestamp", 25) if ts > 0 else 0
    has_edit_log, _, _ = _import_thread_helpers()
    edit_score = signals.get("edit_log_present", 20) if has_edit_log(text) else 0
    version_score = signals.get("filename_semantic_version", 15) if extract_filename_version_tuple(path) > (0,) else 0
    progress = scored.get("progress_score", 0) * signals.get("progress_score_unit", 1)
    completeness = scored.get("completeness_score", 0) * signals.get("completeness_score_unit", 0.4)
    penalties = 0
    if re.search(r" \d+\.md$", path.name, flags=re.IGNORECASE):
        penalties += signals.get("finder_duplicate_penalty", 20)
    if depth == 0 and dated_score == 0:
        penalties += signals.get("undated_at_root_penalty", 15)

    total = depth_score + dated_score + edit_score + version_score + progress + completeness - penalties
    return {
        "evidence_score": round(total, 2),
        "evidence_breakdown": {
            "depth": depth_score,
            "dated": dated_score,
            "edit_log": edit_score,
            "version": version_score,
            "progress": progress,
            "completeness": round(completeness, 2),
            "penalties": penalties,
        },
        "depth": depth,
        "relative_dir": "/".join(parts) if parts else "(root)",
        "session_chain": [p.lower() for p in parts] if parts else ["root"],
        "has_timestamp": ts > 0,
        "filename_version": extract_filename_version_tuple(path),
    }


def detect_probable_final_folder(paths: list[Path], intake_root: Path, rubric: dict) -> dict[str, Any]:
    cfg = rubric.get("sink_detection", {})
    weights = cfg.get("confidence_weights", {})
    by_dir: dict[str, dict] = {}

    for path in paths:
        if not path.is_file():
            continue
        parts = path_parts_relative(path, intake_root)
        rel_dir = "/".join(parts) if parts else "(root)"
        row = by_dir.setdefault(
            rel_dir,
            {
                "relative_dir": rel_dir,
                "depth": len(parts),
                "file_count": 0,
                "dated_count": 0,
                "evidence_total": 0.0,
            },
        )
        row["file_count"] += 1
        if extract_filename_timestamp(path) > 0:
            row["dated_count"] += 1

    if not by_dir:
        return {
            "probable_final_folder": None,
            "confidence": 0.0,
            "method": "evidence_aggregate",
            "folder_ranking": [],
            "session_story_guess": "No files found under intake root.",
        }

    max_evidence = 1.0
    for rel_dir, row in by_dir.items():
        dir_paths = [
            p
            for p in paths
            if ("/".join(path_parts_relative(p, intake_root)) if path_parts_relative(p, intake_root) else "(root)") == rel_dir
            or (rel_dir == "(root)" and not path_parts_relative(p, intake_root))
        ]
        evidence_scores = []
        for p in dir_paths:
            try:
                text = p.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            pseudo_scored = {"progress_score": 0, "completeness_score": 0}
            ev = compute_artifact_evidence(p, intake_root, pseudo_scored, text, rubric)
            evidence_scores.append(ev["evidence_score"])
        avg_evidence = sum(evidence_scores) / max(len(evidence_scores), 1)
        dated_ratio = row["dated_count"] / max(row["file_count"], 1)
        row["avg_evidence"] = round(avg_evidence, 2)
        row["dated_ratio"] = round(dated_ratio, 2)
        row["evidence_total"] = round(sum(evidence_scores), 2)
        max_evidence = max(max_evidence, avg_evidence)

    for row in by_dir.values():
        row["sink_score"] = round(
            row.get("evidence_total", 0)
            + row.get("dated_count", 12)
            + row.get("file_count", 0) * 8
            + row.get("depth", 0) * 3,
            2,
        )

    ranked = sorted(
        by_dir.values(),
        key=lambda r: (
            -r.get("sink_score", 0),
            -r.get("dated_ratio", 0),
            -r.get("file_count", 0),
        ),
    )

    min_files = cfg.get("min_files_in_folder", 2)
    multi = [r for r in ranked if r.get("file_count", 0) >= min_files]
    probable = multi[0] if multi else (ranked[0] if ranked else None)

    best = probable or (ranked[0] if ranked else None)
    dated_ratio = (best or {}).get("dated_ratio", 0)
    avg_ev = (best or {}).get("avg_evidence", 0) / max_evidence
    depth_norm = min(1.0, (best or {}).get("depth", 0) / 6)
    count_norm = min(1.0, (best or {}).get("file_count", 0) / 10)
    confidence = (
        weights.get("avg_evidence", 0.45) * avg_ev
        + weights.get("dated_ratio", 0.25) * dated_ratio
        + weights.get("depth", 0.15) * depth_norm
        + weights.get("file_count", 0.15) * count_norm
    )
    confidence = round(min(0.99, confidence), 2)

    story = (
        f"Intake session looks like layered saves: early copies near the root, "
        f"later dated/versioned files deeper in the tree. "
        f"Best evidence cluster: `{probable.get('relative_dir') if probable else 'unclear'}` "
        f"(confidence {confidence}). "
        f"This is inferred from depth + timestamps + edit logs — not from any fixed folder name."
        if probable
        else "No confident final sink folder — use per-file evidence winners."
    )

    return {
        "probable_final_folder": probable,
        "confidence": confidence,
        "method": "evidence_aggregate",
        "folder_ranking": ranked[:10],
        "session_story_guess": story,
    }


def pick_thread_winner(artifacts: list[dict], thread_rubric: dict, path_rubric: dict) -> list[dict]:
    _, _, role_sort_key = _import_thread_helpers()
    rules = path_rubric.get("second_pass_rules", {})
    margin = rules.get("evidence_margin_to_demote", 12)
    role_margin = rules.get("prefer_spec_role_within_margin", 5)

    if not artifacts:
        return artifacts

    ranked = sorted(
        artifacts,
        key=lambda a: (
            role_sort_key(a.get("role", "spec"), thread_rubric),
            -a.get("evidence_score", 0),
            -a.get("progress_score", 0),
            -a.get("completeness_score", 0),
        ),
    )
    winner = ranked[0]
    winner_evidence = winner.get("evidence_score", 0)
    winner_role = role_sort_key(winner.get("role", "spec"), thread_rubric)

    for art in ranked[1:]:
        if art.get("role") in {"spec", "proposal", "conflict_log"} and winner.get("role") == "implementation_prompt":
            if art.get("evidence_score", 0) + role_margin >= winner_evidence:
                winner = art
                winner_evidence = art.get("evidence_score", 0)
                winner_role = role_sort_key(art.get("role", "spec"), thread_rubric)

    for art in artifacts:
        ev = art.get("evidence_score", 0)
        if art is winner:
            art["artifact_state"] = "primary_final"
            continue
        if winner_evidence - ev >= margin:
            art["artifact_state"] = "earlier_session_copy"
            art["role"] = rules.get("lower_evidence_role_override", "earlier_session_copy")
        elif art.get("role") == "duplicate_copy":
            art["artifact_state"] = "stale_duplicate"
        else:
            art["artifact_state"] = "companion"

    return sorted(artifacts, key=lambda a: (-a.get("evidence_score", 0), role_sort_key(a.get("role", "spec"), thread_rubric)))


def enrich_artifacts_with_evidence(
    artifacts: list[dict],
    intake_root: Path,
    score_document_fn: Callable[[Path], dict],
    rubric: dict,
) -> list[dict]:
    enriched = []
    for art in artifacts:
        path = Path(art["path"])
        text = path.read_text(encoding="utf-8", errors="ignore")
        scored = score_document_fn(path)
        ev = compute_artifact_evidence(path, intake_root, scored, text, rubric)
        enriched.append({**art, **scored, **ev, "path_meta": ev})
    return enriched


def second_pass_thread_audit(
    paths: list[Path],
    intake_root: Path,
    build_thread_record_fn: Callable[..., dict],
    score_document_fn: Callable[[Path], dict],
    first_pass_audit: dict | None = None,
    rubric: dict | None = None,
    thread_rubric: dict | None = None,
) -> dict[str, Any]:
    from governance_thread_intelligence_v1 import (  # noqa: WPS433
        detect_thread_role,
        extract_pending_items,
        load_thread_rubric,
        normalize_thread_id,
        parse_edit_log,
        should_exclude_path,
    )

    rubric = rubric or load_path_rubric()
    thread_rubric = thread_rubric or load_thread_rubric()
    folder_intel = detect_probable_final_folder(paths, intake_root, rubric)
    probable_dir = (folder_intel.get("probable_final_folder") or {}).get("relative_dir")

    grouped: dict[str, list[dict]] = {}
    for path in paths:
        if not path.is_file() or should_exclude_path(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        scored = score_document_fn(path)
        thread_id = normalize_thread_id(path, text)
        role = detect_thread_role(path, text)
        ev = compute_artifact_evidence(path, intake_root, scored, text, rubric)
        grouped.setdefault(thread_id, []).append(
            {
                "path": str(path),
                "thread_id": thread_id,
                "role": role,
                "domain": scored.get("classification", {}).get("proposed_domain"),
                "version": scored.get("classification", {}).get("proposed_version"),
                "status": scored.get("status"),
                "progress_score": scored.get("progress_score", 0),
                "completeness_score": scored.get("completeness_score", 0),
                "pending_items": extract_pending_items(text),
                "artifact_state": "active",
                "edit_log_entries": len(parse_edit_log(text)),
                **ev,
                "path_meta": ev,
            }
        )

    refined_threads = []
    corrections = []
    for thread_id, arts in sorted(grouped.items()):
        refined_arts = pick_thread_winner(arts, thread_rubric, rubric)
        record = build_thread_record_fn(thread_id, refined_arts, thread_rubric, score_document_fn)
        if first_pass_audit:
            old = next((t for t in first_pass_audit.get("threads", []) if t.get("thread_id") == thread_id), {})
            old_path = (old.get("final_carrier") or {}).get("path")
            new_path = (record.get("final_carrier") or {}).get("path")
            if old_path and new_path and old_path != new_path:
                corrections.append(
                    {
                        "thread_id": thread_id,
                        "first_pass": old_path,
                        "second_pass": new_path,
                        "reason": "evidence-based path+content composite",
                    }
                )
        final_path = (record.get("final_carrier") or {}).get("path", "")
        final_dir = "/".join(path_parts_relative(Path(final_path), intake_root)) if final_path else ""
        if not final_dir:
            final_dir = "(root)"
        record["evidence_summary"] = {
            "winner_evidence": max((a.get("evidence_score", 0) for a in refined_arts), default=0),
            "earlier_copies": sum(1 for a in refined_arts if a.get("artifact_state") == "earlier_session_copy"),
            "in_probable_sink": probable_dir == final_dir if probable_dir else None,
            "final_relative_dir": final_dir,
        }
        refined_threads.append(record)

    sink_hits = sum(1 for t in refined_threads if (t.get("evidence_summary") or {}).get("in_probable_sink"))
    return {
        "schema": "governance-second-pass-audit-v2",
        "intake_root": str(intake_root),
        "first_pass_summary": (first_pass_audit or {}).get("summary", {}),
        "second_pass_summary": {
            "completed": sum(1 for t in refined_threads if t["completion_state"] == "COMPLETED"),
            "awaiting_registry_entry": sum(
                1 for t in refined_threads if t["completion_state"] == "AWAITING_REGISTRY_ENTRY"
            ),
            "awaiting_library_upload": sum(
                1 for t in refined_threads if t["completion_state"] == "AWAITING_LIBRARY_UPLOAD"
            ),
            "pending_library_promote": sum(
                1 for t in refined_threads if t["completion_state"] == "PENDING_LIBRARY_PROMOTE"
            ),
            "pending_founder": sum(1 for t in refined_threads if t["completion_state"] == "PENDING_FOUNDER"),
            "pending_thread": sum(1 for t in refined_threads if t["completion_state"] == "PENDING_THREAD"),
            "in_progress": sum(1 for t in refined_threads if t["completion_state"] == "IN_PROGRESS"),
            "left_abandoned": sum(1 for t in refined_threads if t["completion_state"] == "LEFT_ABANDONED"),
            "final_carriers_in_probable_sink": sink_hits,
            "corrections_count": len(corrections),
        },
        "folder_intelligence": folder_intel,
        "corrections": corrections,
        "threads": refined_threads,
        "thread_count": len(refined_threads),
        "ok": bool(refined_threads),
    }


def build_second_pass_story(second_audit: dict, repo_map: dict) -> str:
    from governance_narrative_intelligence_v1 import build_save_location_index, paragraph_thread_story

    folder = second_audit.get("folder_intelligence", {})
    probable = folder.get("probable_final_folder") or {}
    lines = [
        "## Second-pass recheck (evidence-based — no hardcoded folder names)",
        "",
        folder.get("session_story_guess", ""),
        "",
        f"**Probable evidence sink:** `{probable.get('relative_dir', 'unknown')}` "
        f"(confidence {folder.get('confidence', 0)}, "
        f"{probable.get('file_count', 0)} files, dated ratio {probable.get('dated_ratio', 0)})",
        "",
    ]
    if second_audit.get("corrections"):
        lines.append("### Corrections from first pass")
        for c in second_audit["corrections"]:
            lines.append(
                f"- **{c['thread_id']}**: `{Path(c['first_pass']).name}` → `{Path(c['second_pass']).name}`"
            )
        lines.append("")

    lines.append("### Final files (evidence winners)")
    for row in build_save_location_index(second_audit.get("threads", []), repo_map):
        thread = next((t for t in second_audit.get("threads", []) if t["thread_id"] == row["thread_id"]), {})
        ev = thread.get("evidence_summary", {})
        sink = " [probable sink]" if ev.get("in_probable_sink") else ""
        lines.append(
            f"- **{row['display_name']}** → `{row['most_complete_path']}`{sink} "
            f"(evidence {ev.get('winner_evidence', '?')}, {row['completion_state']})"
        )
    lines.append("")
    lines.append("### Thread stories")
    for thread in sorted(second_audit.get("threads", []), key=lambda t: -t.get("progress_pct", 0)):
        lines.append(f"- {paragraph_thread_story(thread, repo_map)}")
    lines.append("")
    return "\n".join(lines)


def run_coherence_checks(second_audit: dict, rubric: dict) -> list[str]:
    errors: list[str] = []
    rules = rubric.get("coherence_rules", {})
    folder = second_audit.get("folder_intelligence", {})
    if folder.get("confidence", 0) < rules.get("min_sink_confidence", 0.5):
        errors.append(f"sink confidence {folder.get('confidence')} below minimum")

    thread_ids = {t.get("thread_id") for t in second_audit.get("threads", [])}
    if "sourcea_brain_registry" in thread_ids and "sourcea_brain_registry_learning_gate" in thread_ids:
        pass
    elif "sourcea_brain_registry" in thread_ids:
        dr = next((t for t in second_audit.get("threads", []) if t["thread_id"] == "sourcea_brain_registry"), {})
        fc = (dr.get("final_carrier") or {}).get("path", "").lower()
        if "discovery" in fc and "learning gate" not in fc:
            pass
        elif "learning gate" in fc:
            errors.append("discovery report thread collapsed into wrong thread_id")

    for thread in second_audit.get("threads", []):
        tid = thread.get("thread_id", "")
        final = (thread.get("final_carrier") or {}).get("path", "")
        if not final:
            continue
        if tid == "sourcea_brain_registry_learning_gate":
            if "v0_1_4" not in final and "v0.1.4" not in final:
                errors.append(f"{tid}: final missing v0.1.4")
            if "20260629" not in final:
                errors.append(f"{tid}: final missing session timestamp")
        if tid == "ssot_conflict_log_runtime_rules_domain_split":
            if "v0_1_2" not in final:
                errors.append(f"{tid}: final missing v0.1.2")
        if rules.get("implementation_prompt_never_beats_spec_same_thread"):
            role = (thread.get("final_carrier") or {}).get("role")
            if role == "implementation_prompt":
                errors.append(f"{tid}: implementation_prompt must not be final carrier")
        final_lower = final.lower()
        if "__awaiting_upload__" in final_lower and thread.get("completion_state") == "COMPLETED":
            errors.append(f"{tid}: __AWAITING_UPLOAD__ placeholder must not be COMPLETED")

    return errors
