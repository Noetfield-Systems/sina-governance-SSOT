#!/usr/bin/env python3
"""Detect and promote library drafts — __AWAITING_UPLOAD__ + registry library_promote_pending."""
from __future__ import annotations

import json
import re
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TARGET_MAP = ROOT / "data/governance_library_target_map_v1.json"
QUEUE_PATH = ROOT / "data/governance_library_promote_queue_v1.json"
REGISTRY_PATH = ROOT / "data/governance_artifact_registry_v1.json"
PLACEHOLDER_MARKERS = ("__awaiting_upload__", "awaiting upload", "not yet installed")


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def expand(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def load_target_map() -> dict:
    return json.loads(TARGET_MAP.read_text(encoding="utf-8"))


def load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def save_registry(registry: dict) -> None:
    registry["saved_at"] = utc_now()
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")


def is_upload_placeholder(path: Path) -> bool:
    name = path.name.lower()
    if "__awaiting_upload__" in name:
        return True
    return False


def placeholder_stem(path: Path) -> str:
    stem = path.stem
    stem = re.sub(r"\.__AWAITING_UPLOAD__$", "", stem, flags=re.I)
    stem = re.sub(r"__AWAITING_UPLOAD__$", "", stem, flags=re.I)
    return stem


def is_real_draft(path: Path) -> bool:
    if not path.is_file() or path.suffix.lower() != ".md":
        return False
    from governance_thread_intelligence_v1 import should_exclude_path  # noqa: WPS433

    if should_exclude_path(path) or is_upload_placeholder(path):
        return False
    if re.search(r" \d+\.md$", path.name, flags=re.I):
        return False
    if ".venv/" in str(path) or "/site-packages/" in str(path):
        return False
    return len(path.read_text(encoding="utf-8", errors="ignore").split()) >= 50


def is_library_intake_path(path: Path, patterns: list[str]) -> bool:
    lowered = str(path).lower()
    return any(p.lower() in lowered for p in patterns)


def score_candidate(path: Path) -> tuple:
    name = path.name.lower()
    penalties = 0
    if "superseded" in name:
        penalties += 30
    if re.search(r" v0[_\.]", name):
        bonuses = 10
    else:
        bonuses = 0
    depth = len(path.parts)
    words = len(path.read_text(encoding="utf-8", errors="ignore").split())
    return (penalties, -depth, -words, -bonuses, name)


def find_source_for_stem(stem: str, intake_root: Path, registry: dict, canonical: Path) -> Path | None:
    hints = {stem.lower(), stem.lower().replace("_", "-"), stem.lower().replace("-", "_")}
    registry_sources: list[Path] = []
    for art in registry.get("artifacts", []):
        aid = art.get("artifact_id", "").lower()
        rel = art.get("path", "")
        if any(h in aid or h in rel.lower() for h in hints):
            candidate = ROOT / rel
            if candidate.is_file() and is_real_draft(candidate):
                registry_sources.append(candidate)

    intake_hits: list[Path] = []
    if intake_root.is_dir():
        for path in intake_root.rglob("*.md"):
            if not is_real_draft(path):
                continue
            stem_l = path.stem.lower()
            if any(h in stem_l for h in hints) or stem_l.replace(" ", "_") == stem.lower():
                intake_hits.append(path)

    ranked = sorted(set(registry_sources + intake_hits), key=score_candidate)
    if ranked:
        return ranked[0]

    for target in load_target_map().get("placeholder_targets", {}).values():
        if stem.lower().replace("_", "-") in target.lower():
            candidate = canonical / target
            if candidate.is_file() and is_real_draft(candidate):
                return candidate
    return None


def registry_pending_rows(registry: dict) -> list[dict]:
    rows = []
    target_map = load_target_map().get("artifact_targets", {})
    for art in registry.get("artifacts", []):
        if not art.get("library_promote_pending"):
            continue
        aid = art["artifact_id"]
        rows.append(
            {
                "kind": "registry_pending",
                "artifact_id": aid,
                "source_registry_path": art.get("path"),
                "library_target": target_map.get(aid),
                "intake_source": art.get("intake_source"),
            }
        )
    return rows


def placeholder_rows(paths: list[Path], intake_root: Path, registry: dict, canonical: Path) -> list[dict]:
    target_map = load_target_map()
    placeholder_targets = target_map.get("placeholder_targets", {})
    rows: list[dict] = []
    seen: set[str] = set()

    for path in paths:
        if not is_upload_placeholder(path):
            continue
        stem = placeholder_stem(path)
        if stem in seen:
            continue
        seen.add(stem)
        library_target = placeholder_targets.get(stem) or placeholder_targets.get(stem.upper())
        source = find_source_for_stem(stem, intake_root, registry, canonical)
        canonical_dest = canonical / library_target if library_target else None
        already = bool(canonical_dest and canonical_dest.is_file() and is_real_draft(canonical_dest))
        rows.append(
            {
                "kind": "upload_placeholder",
                "placeholder_path": str(path),
                "stem": stem,
                "library_target": library_target,
                "resolved_source": str(source) if source else None,
                "already_in_library": already,
                "awaiting_library_upload": not already and not source,
            }
        )
    return rows


def intake_library_draft_rows(paths: list[Path], registry: dict, target_map: dict) -> list[dict]:
    patterns = target_map.get("intake_library_folder_patterns", ["noetfield-library"])
    artifact_targets = target_map.get("artifact_targets", {})
    rows: list[dict] = []
    registry_by_hint: dict[str, str] = {}
    for aid, rel in artifact_targets.items():
        key = Path(rel).stem.lower()
        registry_by_hint[key] = aid

    for path in paths:
        if not is_real_draft(path) or not is_library_intake_path(path, patterns):
            continue
        stem_key = path.stem.lower()
        artifact_id = None
        for hint, aid in registry_by_hint.items():
            if hint in stem_key or stem_key in hint:
                artifact_id = aid
                break
        if not artifact_id:
            continue
        art = next((a for a in registry.get("artifacts", []) if a.get("artifact_id") == artifact_id), None)
        if not art or not art.get("library_promote_pending"):
            continue
        rows.append(
            {
                "kind": "intake_library_copy",
                "artifact_id": artifact_id,
                "source_path": str(path),
                "library_target": artifact_targets.get(artifact_id),
                "already_in_registry": True,
            }
        )
    return rows


def build_library_manifest(paths: list[Path], intake_root: Path) -> dict[str, Any]:
    registry = load_registry()
    target_map = load_target_map()
    canonical = expand(target_map.get("canonical_library_root", "~/Desktop/SourceA/noetfield-library"))

    registry_rows = registry_pending_rows(registry)
    for row in registry_rows:
        src = ROOT / (row.get("source_registry_path") or "")
        if not src.is_file():
            alt = row.get("intake_source")
            if alt and Path(alt).is_file():
                src = Path(alt)
            else:
                stem = Path(row.get("library_target") or "").stem
                resolved = find_source_for_stem(stem, intake_root, registry, canonical)
                src = resolved
        row["resolved_source"] = str(src) if src and src.is_file() else None
        dest = canonical / row["library_target"] if row.get("library_target") else None
        row["already_in_library"] = bool(dest and dest.is_file() and is_real_draft(dest))
        row["awaiting_library_promote"] = bool(row.get("library_target")) and not row["already_in_library"]

    placeholders = placeholder_rows(paths, intake_root, registry, canonical)
    intake_copies = intake_library_draft_rows(paths, registry, target_map)

    return {
        "schema": "governance-library-draft-manifest-v1",
        "intake_root": str(intake_root),
        "canonical_library": str(canonical),
        "registry_pending": registry_rows,
        "upload_placeholders": placeholders,
        "intake_library_copies": intake_copies,
        "counts": {
            "registry_pending": len(registry_rows),
            "upload_placeholders": len(placeholders),
            "intake_library_copies": len(intake_copies),
            "awaiting_promote": sum(1 for r in registry_rows if r.get("awaiting_library_promote")),
            "placeholder_gaps": sum(1 for r in placeholders if r.get("awaiting_library_upload")),
        },
    }


def promote_library_drafts(manifest: dict, apply: bool) -> dict[str, Any]:
    target_map = load_target_map()
    canonical = expand(target_map.get("canonical_library_root", "~/Desktop/SourceA/noetfield-library"))
    registry = load_registry()
    promoted: list[dict] = []
    skipped: list[dict] = []
    errors: list[str] = []

    actions: list[dict] = []
    for row in manifest.get("registry_pending", []):
        if not row.get("awaiting_library_promote"):
            skipped.append({**row, "reason": "already_in_library"})
            continue
        src = row.get("resolved_source")
        if not src:
            skipped.append({**row, "reason": "no_resolved_source"})
            continue
        actions.append(
            {
                "artifact_id": row["artifact_id"],
                "source": src,
                "dest": str(canonical / row["library_target"]),
                "library_target": row["library_target"],
            }
        )

    for row in manifest.get("upload_placeholders", []):
        if row.get("already_in_library"):
            skipped.append({**row, "reason": "placeholder_target_already_live"})
            continue
        src = row.get("resolved_source")
        if not src or not row.get("library_target"):
            skipped.append({**row, "reason": "placeholder_no_source"})
            continue
        actions.append(
            {
                "artifact_id": row.get("stem"),
                "source": src,
                "dest": str(canonical / row["library_target"]),
                "library_target": row["library_target"],
                "from_placeholder": row.get("placeholder_path"),
            }
        )

    if apply:
        for row in manifest.get("registry_pending", []):
            if row.get("already_in_library") and row.get("artifact_id"):
                for art in registry.get("artifacts", []):
                    if art.get("artifact_id") == row["artifact_id"]:
                        art["library_promote_pending"] = False
                        art["library_path"] = row.get("library_target")
                        art["library_promoted_at"] = utc_now()
                        promoted.append({"artifact_id": row["artifact_id"], "action": "cleared_pending_already_in_library"})
        for act in actions:
            src_path = Path(act["source"])
            dest_path = Path(act["dest"])
            if not src_path.is_file():
                errors.append(f"{act.get('artifact_id')}: missing source {src_path}")
                continue
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dest_path)
            promoted.append(act)
            aid = act.get("artifact_id")
            if aid and aid in {a.get("artifact_id") for a in registry.get("artifacts", [])}:
                for art in registry.get("artifacts", []):
                    if art.get("artifact_id") == aid:
                        art["library_promote_pending"] = False
                        art["library_path"] = act["library_target"]
                        art["library_promoted_at"] = utc_now()
        if promoted:
            save_registry(registry)

    queue = {
        "schema": "governance_library_promote_queue_v1",
        "saved_at": utc_now(),
        "manifest": manifest,
        "actions": actions,
        "promoted": promoted,
        "skipped": skipped,
        "errors": errors,
        "dry_run": not apply,
    }
    if apply:
        QUEUE_PATH.write_text(json.dumps(queue, indent=2) + "\n", encoding="utf-8")

    return {
        "schema": "governance-promote-library-drafts-v1",
        "ok": not errors,
        "promoted": promoted,
        "skipped": skipped,
        "errors": errors,
        "counts": manifest.get("counts", {}),
        "queue_path": str(QUEUE_PATH) if apply else None,
        "dry_run": not apply,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Promote SG drafts to canonical noetfield-library")
    parser.add_argument("--root", required=True, help="Intake scan root (e.g. ~/Downloads)")
    parser.add_argument("--apply", action="store_true", help="Copy files to canonical library + update registry")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    intake_root = expand(args.root)
    paths = list(intake_root.rglob("*.md")) if intake_root.is_dir() else []
    manifest = build_library_manifest(paths, intake_root)
    result = promote_library_drafts(manifest, apply=args.apply)
    result["manifest"] = manifest
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
