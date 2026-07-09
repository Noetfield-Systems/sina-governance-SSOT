#!/usr/bin/env python3
"""Merge engine — manual plans and safe auto-merge into SG intake staging."""
from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
REPO_MAP = ROOT / "data/governance_repo_map_v1.json"
STAGING_ROOT = ROOT / "data/governance_intake_staging_v1"

_ENGINE_DIR = Path(__file__).resolve().parent
import sys

if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))
from governance_thread_intelligence_v1 import normalize_thread_id  # noqa: E402


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_repo_map() -> dict:
    return json.loads(REPO_MAP.read_text(encoding="utf-8"))


def expand(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def repo_for_path(path: Path, repo_map: dict) -> dict | None:
    resolved = path.resolve()
    best: dict | None = None
    best_len = -1
    for repo in repo_map.get("repos", []):
        base = expand(repo.get("path", ""))
        if not base.exists():
            continue
        try:
            resolved.relative_to(base)
            match_len = len(str(base))
            if match_len > best_len:
                best = repo
                best_len = match_len
        except ValueError:
            continue
    return best


def extract_section_body(path: Path, section_title: str) -> str | None:
    text = path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    capture = False
    level = 0
    body: list[str] = []
    target = section_title.strip().lower()
    for line in lines:
        if line.startswith("#"):
            title = line.lstrip("#").strip().lower()
            if capture:
                break
            if title == target:
                capture = True
                level = len(line) - len(line.lstrip("#"))
                continue
        elif capture:
            if line.startswith("#") and (len(line) - len(line.lstrip("#"))) <= level:
                break
            body.append(line)
    joined = "\n".join(body).strip()
    return joined if joined else None


def append_section_to_file(path: Path, section_title: str, section_body: str, source_path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    marker = f"\n\n## {section_title}\n\n<!-- merged from {source_path.name} at {utc_now()} -->\n\n{section_body}\n"
    if f"## {section_title}" in text:
        return "skipped_exists"
    path.write_text(text.rstrip() + marker, encoding="utf-8")
    return "appended"


def build_merge_plan(
    thread_audit: dict,
    selection_audit: dict | None,
    repo_map: dict,
    score_document_fn: Callable[[Path], dict] | None = None,
) -> dict[str, Any]:
    auto_actions: list[dict] = []
    manual_actions: list[dict] = []
    staging = repo_map.get("repos", [{}])[0].get("staging_path", "data/governance_intake_staging_v1/")

    for thread in thread_audit.get("threads", []):
        final = thread.get("final_carrier") or {}
        final_path = final.get("path")
        if not final_path:
            continue
        src = Path(final_path)
        if not src.is_file():
            continue

        repo = repo_for_path(src, repo_map) or {}
        thread_id = thread.get("thread_id", "unknown")
        dest_name = src.name
        dest = ROOT / staging / thread_id / dest_name

        if repo.get("intake"):
            auto_actions.append(
                {
                    "action": "stage_final_carrier_to_sg_intake",
                    "thread_id": thread_id,
                    "source_path": str(src),
                    "dest_path": str(dest),
                    "reason": "Intake file is most complete carrier — stage into SG for promotion review",
                    "mode": "auto",
                }
            )
            manual_actions.append(
                {
                    "action": "registry_row_promotion",
                    "thread_id": thread_id,
                    "source_path": str(src),
                    "reason": "After founder ratification, register row in governance_artifact_registry_v1.json",
                    "mode": "manual",
                }
            )

        if thread.get("completion_state") == "PENDING_FOUNDER":
            manual_actions.append(
                {
                    "action": "founder_ratification",
                    "thread_id": thread_id,
                    "source_path": str(src),
                    "pending_items": thread.get("pending_items", []),
                    "reason": "Thread cannot close until founder approves/rejects/holds",
                    "mode": "manual",
                }
            )

        left = thread.get("left_abandoned", [])
        if left:
            auto_actions.append(
                {
                    "action": "void_stale_duplicate_pointer",
                    "thread_id": thread_id,
                    "stale_count": len(left),
                    "stale_paths": [x.get("path") for x in left[:5]],
                    "reason": f"{len(left)} stale duplicate(s) — pointer only, do not treat as live",
                    "mode": "auto",
                }
            )

    if selection_audit:
        for cluster in selection_audit.get("clusters", []):
            decision = cluster.get("decision", {})
            primary_path = (decision.get("primary_final") or {}).get("path")
            if not primary_path:
                continue
            primary_thread = normalize_thread_id(Path(primary_path))
            section_items = decision.get("section_merge_plan", [])[:12]
            for item in section_items:
                from_path = item.get("from_path", "")
                if from_path and normalize_thread_id(Path(from_path)) != primary_thread:
                    continue
                action = {
                    "action": item.get("action"),
                    "thread_id": cluster.get("cluster_id"),
                    "section": item.get("section"),
                    "from_path": from_path,
                    "over_target_path": item.get("over_target_path"),
                    "reason": item.get("reason"),
                    "conflict_review_required": item.get("conflict_review_required", False),
                }
                if item.get("conflict_review_required"):
                    action["mode"] = "manual"
                    manual_actions.append(action)
                else:
                    action["mode"] = "auto"
                    auto_actions.append(action)

    sg_repo = next((r for r in repo_map.get("repos", []) if r.get("repo_id") == "sg"), {})
    never = set(repo_map.get("merge_policy", {}).get("never_auto", []))

    safe_auto = [a for a in auto_actions if a.get("action") not in never]

    return {
        "schema": "governance-merge-plan-v1",
        "planned_at": utc_now(),
        "staging_root": str((ROOT / staging).resolve()),
        "auto_actions": safe_auto,
        "manual_actions": manual_actions,
        "summary": {
            "auto_count": len(safe_auto),
            "manual_count": len(manual_actions),
            "threads_with_staging": len({a.get("thread_id") for a in safe_auto if a.get("action") == "stage_final_carrier_to_sg_intake"}),
        },
        "sg_write_owner": sg_repo.get("write_owner"),
        "ok": bool(safe_auto or manual_actions),
    }


def apply_merge_plan(plan: dict, apply: bool = False) -> dict[str, Any]:
    results: list[dict] = []
    applied = 0
    skipped = 0
    errors: list[str] = []

    for action in plan.get("auto_actions", []):
        act = action.get("action")
        row = {"action": act, "thread_id": action.get("thread_id"), "mode": "dry_run" if not apply else "applied"}

        try:
            if act == "stage_final_carrier_to_sg_intake":
                src = Path(action["source_path"])
                dest = Path(action["dest_path"])
                row["source_path"] = str(src)
                row["dest_path"] = str(dest)
                if apply:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dest)
                    applied += 1
                    row["mode"] = "applied"
                else:
                    skipped += 1

            elif act == "adopt_section_into_primary":
                target = Path(action["over_target_path"])
                source = Path(action["from_path"])
                section = action.get("section", "")
                body = extract_section_body(source, section)
                row["section"] = section
                if not body:
                    row["result"] = "section_not_found"
                    skipped += 1
                elif apply:
                    result = append_section_to_file(target, section, body, source)
                    row["result"] = result
                    if result == "appended":
                        applied += 1
                    else:
                        skipped += 1
                else:
                    skipped += 1

            elif act == "add_section_to_primary":
                target = Path(action["over_target_path"])
                source = Path(action["from_path"])
                section = action.get("section", "")
                body = extract_section_body(source, section)
                row["section"] = section
                if not body:
                    row["result"] = "section_not_found"
                    skipped += 1
                elif apply:
                    result = append_section_to_file(target, section, body, source)
                    row["result"] = result
                    if result == "appended":
                        applied += 1
                    else:
                        skipped += 1
                else:
                    skipped += 1

            elif act == "void_stale_duplicate_pointer":
                row["stale_count"] = action.get("stale_count", 0)
                row["result"] = "pointer_only_no_delete"
                skipped += 1

            else:
                row["result"] = "unsupported_auto_action"
                skipped += 1
        except OSError as exc:
            errors.append(f"{act}: {exc}")
            row["error"] = str(exc)

        results.append(row)

    manifest_path = STAGING_ROOT / "manifest.json"
    manifest = {
        "schema": "governance-intake-staging-manifest-v1",
        "updated_at": utc_now(),
        "dry_run": not apply,
        "applied_count": applied,
        "results": results,
        "manual_actions_pending": len(plan.get("manual_actions", [])),
    }
    if apply:
        STAGING_ROOT.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    return {
        "schema": "governance-merge-apply-v1",
        "dry_run": not apply,
        "applied_count": applied,
        "skipped_count": skipped,
        "errors": errors,
        "results": results,
        "manifest_path": str(manifest_path) if apply else None,
        "ok": not errors,
    }
