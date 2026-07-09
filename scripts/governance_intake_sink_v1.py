#!/usr/bin/env python3
"""Evidence-based intake sink intelligence — NO hardcoded folder names."""
from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINK_RULES = ROOT / "data/governance_intake_sink_rules_v1.json"
PATH_RUBRIC = ROOT / "data/governance_intake_path_rubric_v1.json"
EXTRACT_DIR = ROOT / "data/governance_intake_extract_v1"


def load_sink_rules() -> dict:
    return json.loads(SINK_RULES.read_text(encoding="utf-8"))


def load_path_rubric() -> dict:
    return json.loads(PATH_RUBRIC.read_text(encoding="utf-8"))


def is_excluded_intake_path(path: Path, rules: dict | None = None) -> bool:
    rules = rules or load_sink_rules()
    lowered = str(path).lower()
    for part in rules.get("exclude_path_parts", []):
        if part.lower() in lowered:
            return True
    for pat in rules.get("exclude_name_patterns", []):
        if pat.lower() in lowered:
            return True
    rx = rules.get("exclude_filename_regex", "")
    if rx and re.search(rx, path.name, flags=re.I):
        return True
    return False


def classify_intake_artifact(path: Path, text: str, rules: dict | None = None) -> dict[str, Any] | None:
    rules = rules or load_sink_rules()
    name = path.name.lower()
    body = text[:800].lower()

    if is_excluded_intake_path(path, rules):
        return None
    if "research report" in body and "status:" not in text[:500].lower():
        return None

    for aid, sig in rules.get("artifact_signatures", {}).items():
        name_hints = sig.get("name_hints", [])
        exclude = sig.get("exclude_name_hints", [])
        text_hints = sig.get("text_hints", [])
        if exclude and any(h in name for h in exclude):
            continue
        name_match = any(h.replace(" ", "_") in name.replace(" ", "_") or h in name for h in name_hints)
        text_match = any(h in body for h in text_hints) if text_hints else False
        if not name_match and not text_match:
            continue
        row: dict[str, Any] = {
            "artifact_id": aid,
            "role": "implementation_companion" if "impl" in aid or "implementation" in name else "spec",
            "layer": sig["layer"],
            "domain": sig["domain"],
            "version": sig.get("version", "1.0.0"),
        }
        if sig.get("amends"):
            row["amends_target"] = sig["amends"]
            row["role"] = "implementation_companion"
        if sig.get("depends_on"):
            row["depends_on_extra"] = sig["depends_on"]
        if "conflict log" in name:
            row["role"] = "conflict_log"
        if "proposal" in name or "versioning" in name:
            row["role"] = "proposal"
        return row
    return None


def collect_intake_files(intake_root: Path) -> list[Path]:
    rules = load_sink_rules()
    exts = {e.lower() for e in rules.get("scan_scope", {}).get("file_types", [".md", ".zip"])}
    out: list[Path] = []
    for p in intake_root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            out.append(p)
    return out


def resolve_evidence_sink_dirs(intake_root: Path, rules: dict | None = None) -> dict[str, Any]:
    from governance_intake_path_intelligence_v1 import detect_probable_final_folder  # noqa: WPS433

    rules = rules or load_sink_rules()
    rubric = load_path_rubric()
    cfg = rules.get("sink_detection", {})
    files = collect_intake_files(intake_root)
    md_files = [p for p in files if p.suffix.lower() == ".md"]

    intel = detect_probable_final_folder(md_files, intake_root, rubric)
    ranking = intel.get("folder_ranking", [])
    probable = intel.get("probable_final_folder") or {}
    top_score = (ranking[0].get("sink_score", 0) if ranking else 0) or probable.get("sink_score", 0)
    margin = cfg.get("include_ranked_within_margin", 0.7)

    rel_dirs: list[str] = []
    for row in ranking[: cfg.get("max_sink_dirs", 3)]:
        score = row.get("sink_score", 0)
        if top_score and score < top_score * margin:
            continue
        rel = row.get("relative_dir", "")
        if rel and rel not in rel_dirs:
            rel_dirs.append(rel)

    if not rel_dirs and probable.get("relative_dir"):
        rel_dirs.append(probable["relative_dir"])

    sink_paths: list[Path] = []
    for rel in rel_dirs:
        if rel == "(root)":
            sink_paths.append(intake_root)
        else:
            sink_paths.append(intake_root / rel)

    if not sink_paths:
        sink_paths = [intake_root]

    confidence = intel.get("confidence", 0)
    return {
        "method": cfg.get("method", "evidence_aggregate"),
        "intake_root": str(intake_root),
        "confidence": confidence,
        "meets_min_confidence": confidence >= cfg.get("min_confidence", 0.5),
        "probable_sink_relative": probable.get("relative_dir"),
        "sink_relative_dirs": rel_dirs,
        "sink_paths": [str(p) for p in sink_paths],
        "folder_intelligence": intel,
    }


def path_in_sink(path: Path, sink_paths: list[Path], intake_root: Path) -> bool:
    try:
        path.resolve().relative_to(intake_root.resolve())
    except ValueError:
        return False
    for sink in sink_paths:
        try:
            path.resolve().relative_to(sink.resolve())
            return True
        except ValueError:
            if sink == intake_root:
                continue
    return False


def zip_priority(zip_name: str, rules: dict) -> int:
    tokens = rules.get("zip_bundle_rules", {}).get("zip_priority_tokens", {})
    n = zip_name.lower()
    score = 10
    for token, weight in tokens.items():
        if token in n:
            score = max(score, weight)
    return score


def extract_zip_artifacts(zip_path: Path, rules: dict) -> list[tuple[str, Path]]:
    inner_map = rules.get("zip_bundle_rules", {}).get("inner_paths_by_artifact", {})
    extract_to = EXTRACT_DIR / re.sub(r"[^a-zA-Z0-9._-]+", "_", zip_path.stem)
    extract_to.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(extract_to)
    except zipfile.BadZipFile:
        return []

    found: list[tuple[str, Path]] = []
    for aid, rels in inner_map.items():
        for rel in rels:
            candidate = extract_to / rel
            if candidate.is_file():
                found.append((aid, candidate))
                break
    return found


def is_unregistered_governance_draft(path: Path, registry: dict, rules: dict | None = None) -> bool:
    """File-level rule: governance artifact signature + not yet in registry."""
    rules = rules or load_sink_rules()
    if is_excluded_intake_path(path, rules):
        return False
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    meta = classify_intake_artifact(path, text, rules)
    if not meta:
        return False
    aid = meta["artifact_id"]
    for art in registry.get("artifacts", []):
        if art.get("artifact_id") == aid and art.get("status") != "SUPERSEDED":
            return False
        if art.get("intake_source") == str(path):
            return False
    return True


DEST_NAMES: dict[str, str] = {
    "smart-production-cost-law-v2": "SMART_PRODUCTION_COST_LAW_v2.md",
    "noos-control-desk-v2": "NOOS_CONTROL_DESK_v2_README.md",
    "copilot-automation-cost-profile-v1": "COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md",
    "founder-intent-filter-v1": "FOUNDER_INTENT_FILTER.md",
}


def dest_name_for(aid: str) -> str:
    return DEST_NAMES.get(aid, f"{aid}.md")


def scan_sink_for_artifacts(
    intake_root: Path,
    registry: dict,
    rules: dict | None = None,
) -> dict[str, Any]:
    rules = rules or load_sink_rules()
    sink_info = resolve_evidence_sink_dirs(intake_root, rules)
    sink_paths = [Path(p) for p in sink_info["sink_paths"]]

    rows: list[dict] = []
    by_id: dict[str, dict] = {}

    def upsert(row: dict) -> None:
        aid = row["artifact_id"]
        if aid not in by_id:
            by_id[aid] = row
            return
        cur = by_id[aid]
        if row.get("source_kind") == "zip_bundle" and cur.get("source_kind") != "zip_bundle":
            by_id[aid] = {**cur, **row, "companion_md": cur.get("source_path")}
        elif row.get("zip_priority", 0) > cur.get("zip_priority", 0):
            by_id[aid] = row

    # Sink-scoped md
    for sink in sink_paths:
        for path in sorted(sink.rglob("*.md") if sink.is_dir() else []):
            if not path.is_file() or is_excluded_intake_path(path, rules):
                continue
            if not path_in_sink(path, sink_paths, intake_root):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            meta = classify_intake_artifact(path, text, rules)
            if not meta:
                continue
            aid = meta["artifact_id"]
            existing = next((a for a in registry.get("artifacts", []) if a.get("artifact_id") == aid), None)
            upsert(
                {
                    "artifact_id": aid,
                    "source_path": str(path),
                    "source_kind": "sink_md",
                    "sink_relative": sink_info.get("probable_sink_relative"),
                    "dest_name": DEST_NAMES.get(aid, path.name),
                    "already_in_registry": existing is not None and existing.get("status") != "SUPERSEDED",
                    **meta,
                }
            )

    # Sink-scoped + root zips matching hints
    zip_hints = rules.get("zip_bundle_rules", {}).get("zip_name_hints", [])
    for path in collect_intake_files(intake_root):
        if path.suffix.lower() != ".zip" or is_excluded_intake_path(path, rules):
            continue
        if not any(h in path.name.lower() for h in zip_hints) and not path_in_sink(path, sink_paths, intake_root):
            continue
        priority = zip_priority(path.name, rules)
        for aid, inner in extract_zip_artifacts(path, rules):
            text = inner.read_text(encoding="utf-8", errors="ignore")
            meta = classify_intake_artifact(inner, text, rules) or {
                "artifact_id": aid,
                "role": "spec",
                "layer": "P8",
                "domain": "automation",
                "version": "1.0.0",
            }
            existing = next((a for a in registry.get("artifacts", []) if a.get("artifact_id") == aid), None)
            upsert(
                {
                    "artifact_id": aid,
                    "source_path": str(inner),
                    "intake_zip_path": str(path),
                    "source_kind": "zip_bundle",
                    "zip_priority": priority,
                    "sink_relative": sink_info.get("probable_sink_relative"),
                    "dest_name": dest_name_for(aid),
                    "already_in_registry": existing is not None and existing.get("status") != "SUPERSEDED",
                    **{k: meta[k] for k in ("role", "layer", "domain", "version", "amends_target") if k in meta},
                }
            )

    # High-signal intake root md (any folder name)
    scope = rules.get("scan_scope", {})
    for pattern in scope.get("root_md_patterns", []):
        for path in intake_root.glob("*.md"):
            if not re.match(pattern, path.name, flags=re.I) or is_excluded_intake_path(path, rules):
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            meta = classify_intake_artifact(path, text, rules)
            if not meta:
                continue
            aid = meta["artifact_id"]
            existing = next((a for a in registry.get("artifacts", []) if a.get("artifact_id") == aid), None)
            upsert(
                {
                    "artifact_id": aid,
                    "source_path": str(path),
                    "source_kind": "intake_root_md",
                    "dest_name": path.name,
                    "already_in_registry": existing is not None and existing.get("status") != "SUPERSEDED",
                    **meta,
                }
            )

    rows = sorted(by_id.values(), key=lambda r: r["artifact_id"])
    return {
        "schema": "governance-intake-sink-manifest-v1",
        "sink_detection": sink_info,
        "artifacts": rows,
        "counts": {
            "total": len(rows),
            "from_sink_md": sum(1 for r in rows if r.get("source_kind") == "sink_md"),
            "from_zip": sum(1 for r in rows if r.get("source_kind") == "zip_bundle"),
            "from_root_md": sum(1 for r in rows if r.get("source_kind") == "intake_root_md"),
            "awaiting_entry": sum(1 for r in rows if not r.get("already_in_registry")),
        },
    }
