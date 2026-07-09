#!/usr/bin/env python3
"""Governance intelligence engine v1 — production classify, scan, impact, audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ENGINE_DIR = Path(__file__).resolve().parent
if str(_ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(_ENGINE_DIR))
from governance_thread_intelligence_v1 import (  # noqa: E402
    collect_paths,
    detect_thread_role,
    evaluate_paths_as_threads,
    load_thread_rubric,
    normalize_thread_id,
    role_sort_key,
    should_exclude_path,
)
from governance_narrative_intelligence_v1 import build_session_story, load_repo_map  # noqa: E402
from governance_merge_engine_v1 import apply_merge_plan, build_merge_plan  # noqa: E402
from governance_intake_path_intelligence_v1 import (  # noqa: E402
    build_second_pass_story,
    load_path_rubric,
    second_pass_thread_audit,
)
from governance_thread_intelligence_v1 import build_thread_record  # noqa: E402
from governance_registry_ops_v1 import (  # noqa: E402
    build_structure_tree_view,
    load_structure_tree,
    load_thread_registry,
    op_registry_add,
    op_registry_amend,
    op_registry_list,
    op_registry_remove,
    op_registry_retire,
    op_registry_show,
    op_thread_list,
    op_thread_register,
    op_thread_retire,
    load_registry as load_registry_ops,
)

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance_artifact_registry_v1.json"
REVIEW_QUEUE = ROOT / "data/governance_review_queue_v1.json"
RUBRIC = ROOT / "data/governance_completeness_rubric_v1.json"
THREAD_RUBRIC = ROOT / "data/governance_thread_rubric_v1.json"
AUTHORITY = ROOT / "ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md"
PIPELINE = ROOT / "ssot/GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md"
RECEIPTS = ROOT / "receipts"
LIBRARY = Path.home() / "Desktop/SourceA/noetfield-library"
CANON_VERSION = "founder_canon_v1.0.0"

SCAN_SUFFIXES = {".md", ".json", ".pdf", ".html", ".txt"}
GUARD_FILES = {REGISTRY, PIPELINE, AUTHORITY, REVIEW_QUEUE, RUBRIC}

LAYER_HINTS: dict[str, list[str]] = {
    "P0": ["foundation", "ssot index", "strategy", "workbench", "reconciliation", "autorun", "governance structure", "governance intelligence"],
    "P1": ["founder canon", "north star", "founder touchpoint", "founder intent", "intent filter"],
    "P2": ["ssot plane", "operating law", "dispatch", "lane ownership", "planning authority", "worker registry"],
    "P3": ["mac runtime", "hub", "receipt", "scan", "ship", "mac law", "workbench reality", "mac cursor"],
    "P4": ["cloud kernel", "l1-l8", "kernel target", "pevc", "fbe", "reconciliation"],
    "P5": ["line engine", "forge", "pipeline", "nerve"],
    "P6": ["knowledge", "meaning", "essay", "field"],
    "P7": ["doctrine", "prompt library", "governance ops"],
    "P8": ["machine loop", "skill", "autonomy", "automation governance", "parallel automation"],
    "P9": ["pattern factory", "plan library", "prompt pack"],
    "P10": ["product boundary", "trustfield", "venture boundary", "sku"],
    "P99": ["ledger", "audit", "completeness", "handoff"],
}

DOMAIN_HINTS: dict[str, list[str]] = {
    "governance_structure": ["governance structure", "version authority", "layer placement", "authority order", "governance intelligence"],
    "founder_canon": ["founder canon", "founder touchpoint", "intent filter"],
    "automation": ["autorun", "machine loop", "github automation", "copilot", "parallel automation", "machine autonomy"],
    "ssot_plane": ["operating law", "ssot index", "planning authority", "ssot plane"],
    "cloud_kernel": ["cloud kernel", "kernel target", "l1-l8"],
    "mac_runtime": ["mac runtime", "hub", "mac law", "mac cursor", "mac founder session"],
    "product_boundary": ["trustfield", "product boundary", "venture boundary"],
    "integrator": ["integrator", "noos runtime", "session-exit", "noos integrator"],
    "venture_routing": ["multi-repo", "worker registry", "venture dispatch", "lane"],
}

STATUS_HINTS: dict[str, list[str]] = {
    "ACTIVE": ["**status:** active", "status: active", '"status": "ACTIVE"', '"status": "active"'],
    "ACTIVE_BASE": ["active_base", "older rule remains live", "remains active base", "active base where"],
    "ACTIVE_AMENDMENT": ["active_amendment", "amended by", "edit log:", "version: v0."],
    "ACTIVE_AMENDMENT_TARGET": ["active_amendment_target", "north-star", "target architecture"],
    "PROPOSED": ["**status:** proposed", "status: proposed", "awaiting founder approval"],
    "SUPERSEDED": ["**status:** superseded", "status: superseded", '"status": "SUPERSEDED"'],
}

SG_SCAN_ROOTS = ["ssot", "data", "docs", "AGENTS.md", ".github/copilot-instructions.md"]
LIBRARY_SCAN_PREFIXES = [
    "P0-FOUNDATION-SPINE",
    "P2-SSOT",
    "P4-CLOUD-KERNEL-L1-L8",
    "P10-PRODUCT-LAYERS",
    "P99-LEDGER",
    "00-INDEX.md",
    "BIG_PICTURE_RELATION_MAP.md",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def load_rubric() -> dict:
    return json.loads(RUBRIC.read_text(encoding="utf-8"))


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


def save_review_queue(payload: dict) -> None:
    REVIEW_QUEUE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    if not path.is_file():
        return ""
    if path.suffix.lower() == ".pdf":
        return path.name.lower()
    return path.read_text(encoding="utf-8", errors="ignore")


def file_fingerprint(path: Path) -> dict:
    if not path.is_file():
        return {"exists": False}
    stat = path.stat()
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:16]
    return {
        "exists": True,
        "sha256_prefix": digest,
        "mtime_iso": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "size_bytes": stat.st_size,
    }


def rel_for_registry(path: Path) -> str | None:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        pass
    if LIBRARY.exists():
        try:
            return str(path.relative_to(LIBRARY))
        except ValueError:
            pass
    return None


def extract_version(text: str, path: Path) -> str | None:
    for pattern in (
        r"\*\*Version:\*\*\s*([0-9]+(?:\.[0-9]+){0,2})",
        r'"version"\s*:\s*"([^"]+)"',
        r"_v([0-9]+(?:\.[0-9]+){0,2})",
        r"-v([0-9]+(?:\.[0-9]+){0,2})",
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    name_match = re.search(r"v([0-9]+(?:\.[0-9]+){0,2})", path.name, flags=re.IGNORECASE)
    return name_match.group(1) if name_match else None


def extract_saved_at(text: str, path: Path) -> str | None:
    for pattern in (
        r"\*\*Saved:\*\*\s*([0-9T:\-+Z]+)",
        r'"saved_at"\s*:\s*"([^"]+)"',
        r"\*\*Activated:\*\*\s*([0-9\-]+)",
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return match.group(1)
    fp = file_fingerprint(path)
    return fp.get("mtime_iso")


def score_hints(text: str, hints: dict[str, list[str]]) -> dict[str, int]:
    lowered = text.lower()
    return {key: sum(1 for word in words if word in lowered) for key, words in hints.items() if any(word in lowered for word in words)}


def best_hint(scores: dict[str, int], fallback: str) -> tuple[str, float]:
    if not scores:
        return fallback, 0.35
    key = max(scores, key=scores.get)
    total = max(scores.values())
    confidence = min(0.98, 0.45 + (total * 0.12))
    return key, round(confidence, 2)


def infer_layer_from_path(path: Path) -> str:
    parts = [p.lower() for p in path.parts]
    if "p99-ledger" in parts:
        return "P99"
    for part in parts:
        if part.startswith("p") and len(part) > 1 and part[1].isdigit():
            return part.split("-", 1)[0].upper()
    if "cloud-kernel" in path.name.lower():
        return "P4"
    if "canon" in path.name.lower():
        return "P1"
    if "ssot" in parts or "ssot" in path.name.lower():
        return "P2"
    return "P0"


def infer_domain_from_path(path: Path) -> str:
    name = path.name.lower()
    if "integrator" in name:
        return "integrator"
    if "cloud-kernel" in name or "kernel" in name:
        return "cloud_kernel"
    if "canon" in name:
        return "founder_canon"
    if "automation" in name or "autorun" in name or "machine_autonomy" in name:
        return "automation"
    if "boundary" in name or "trustfield" in name:
        return "product_boundary"
    if "dispatch" in name or "worker_registry" in name:
        return "venture_routing"
    if "mac" in name:
        return "mac_runtime"
    return "governance_structure"


def infer_authority_rank(path: Path) -> int:
    if path.is_relative_to(ROOT):
        rel = str(path.relative_to(ROOT))
        if rel.startswith("ssot/GOVERNANCE_") or "FOUNDER_CANON" in rel:
            return 1
        if rel.startswith("ssot/") or rel.startswith("data/"):
            return 2
        if rel in {"AGENTS.md", ".github/copilot-instructions.md"} or rel.startswith("docs/MAC_CURSOR"):
            return 3
        return 2
    if "noetfield-library" in str(path):
        return 4
    return 5


def infer_owner_repo(path: Path) -> str:
    if path.is_relative_to(ROOT):
        return "sina-governance-ssot"
    if "noetfield-library" in str(path):
        return "noetfield-library-read-surface"
    return "venture-copy"


def layer_neighbors(layer: str) -> set[str]:
    return {
        "P0": {"P1", "P2", "P4", "P99"},
        "P1": {"P0", "P8"},
        "P2": {"P0", "P3", "P10"},
        "P3": {"P2", "P8"},
        "P4": {"P0", "P5"},
        "P5": {"P4"},
        "P8": {"P1", "P3"},
        "P10": {"P2"},
        "P99": {"P0"},
    }.get(layer, set())


def classify_artifact(path: Path, registry: dict | None = None) -> dict:
    text = read_text(path)
    layer, layer_conf = best_hint(score_hints(text, LAYER_HINTS), infer_layer_from_path(path))
    domain, domain_conf = best_hint(score_hints(text, DOMAIN_HINTS), infer_domain_from_path(path))
    status, status_conf = best_hint(score_hints(text, STATUS_HINTS), "ACTIVE")
    version = extract_version(text, path)
    saved_at = extract_saved_at(text, path)
    authority_rank = infer_authority_rank(path)
    affects_layers = sorted({layer} | layer_neighbors(layer))
    confidence = round((layer_conf + domain_conf + status_conf) / 3, 2)

    return {
        "path": str(path),
        "registry_path": rel_for_registry(path),
        "proposed_layer": layer,
        "proposed_domain": domain,
        "proposed_status": status,
        "proposed_version": version,
        "saved_at": saved_at,
        "authority_rank": authority_rank,
        "affects_layers": affects_layers,
        "owner_repo": infer_owner_repo(path),
        "confidence": confidence,
        "fingerprint": file_fingerprint(path),
    }


def registry_index(registry: dict) -> dict[str, dict]:
    return {a["artifact_id"]: a for a in registry.get("artifacts", []) if a.get("artifact_id")}


def registry_by_path(registry: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for art in registry.get("artifacts", []):
        out[art.get("path", "")] = art
    return out


def discover_candidates() -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()

    def add(path: Path) -> None:
        key = str(path.resolve())
        if key in seen or not path.is_file():
            return
        if path.suffix.lower() not in SCAN_SUFFIXES:
            return
        seen.add(key)
        found.append(path)

    for item in SG_SCAN_ROOTS:
        target = ROOT / item
        if target.is_file():
            add(target)
        elif target.is_dir():
            for path in target.rglob("*"):
                if path.is_file():
                    add(path)

    if LIBRARY.exists():
        for prefix in LIBRARY_SCAN_PREFIXES:
            target = LIBRARY / prefix
            if target.is_file():
                add(target)
            elif target.is_dir():
                for path in target.rglob("*"):
                    if path.is_file():
                        add(path)
    return sorted(found, key=lambda p: str(p))


def scan_registry_gaps(registry: dict) -> dict:
    by_path = registry_by_path(registry)
    registered_paths = set(by_path)
    discovered = discover_candidates()
    unregistered: list[dict] = []
    registered: list[dict] = []
    drifted: list[dict] = []

    for path in discovered:
        rel = rel_for_registry(path)
        if not rel:
            continue
        cls = classify_artifact(path, registry)
        if rel in registered_paths:
            art = by_path[rel]
            registered.append({"path": rel, "artifact_id": art.get("artifact_id"), "classification": cls})
            if art.get("layer") != cls["proposed_layer"] or art.get("domain") != cls["proposed_domain"]:
                drifted.append(
                    {
                        "artifact_id": art.get("artifact_id"),
                        "path": rel,
                        "registry_layer": art.get("layer"),
                        "detected_layer": cls["proposed_layer"],
                        "registry_domain": art.get("domain"),
                        "detected_domain": cls["proposed_domain"],
                    }
                )
        else:
            if cls["authority_rank"] <= 4 and _looks_governance_relevant(path, cls):
                unregistered.append(cls)

    return {
        "discovered_count": len(discovered),
        "registered_count": len(registered),
        "unregistered_candidates": unregistered,
        "classification_drift": drifted,
    }


def _looks_governance_relevant(path: Path, cls: dict) -> bool:
    if cls["authority_rank"] <= 3:
        return True
    name = path.name.lower()
    strong = ("locked", "ssot", "governance", "canon", "registry", "authority", "boundary", "kernel", "index", "manifest", "audit", "handoff")
    return any(k in name for k in strong) and cls["confidence"] >= 0.6


def build_reference_graph(registry: dict) -> dict:
    graph: dict[str, dict] = {}
    arts = registry.get("artifacts", [])
    for art in arts:
        aid = art["artifact_id"]
        graph[aid] = {
            "path": art.get("path"),
            "depends_on": art.get("depends_on", []),
            "amends": art.get("amends", []),
            "amended_by": [],
            "must_point_here": art.get("must_point_here", []),
            "affects_layers": art.get("affects_layers", []),
        }
    for art in arts:
        for dep in art.get("amends", []):
            if dep in graph:
                graph[dep]["amended_by"].append(art["artifact_id"])
    return graph


def pointer_drift_scan(registry: dict) -> list[dict]:
    hits: list[dict] = []
    required_phrase = "GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md"
    for entry in registry.get("entry_points", []):
        path = ROOT / entry
        if not path.is_file():
            hits.append({"entry_point": entry, "issue": "missing_entry_point"})
            continue
        text = read_text(path)
        if required_phrase not in text and entry not in {"data/founder_canon_v1.json"}:
            hits.append({"entry_point": entry, "issue": "missing_structure_authority_pointer"})
        if entry == "data/founder_canon_v1.json":
            data = json.loads(text or "{}")
            if data.get("governance_structure_authority") != "ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md":
                hits.append({"entry_point": entry, "issue": "founder_canon governance_structure_authority mismatch"})
            if "governance_intelligence_pipeline" not in data:
                hits.append({"entry_point": entry, "issue": "founder_canon missing governance_intelligence_pipeline"})
    return hits


def true_conflict_scan(registry: dict) -> dict:
    arts = registry.get("artifacts", [])
    graph = build_reference_graph(registry)
    issues: list[dict] = []

    by_domain: dict[str, list[dict]] = {}
    for art in arts:
        by_domain.setdefault(art.get("domain", "unknown"), []).append(art)

    for domain, group in by_domain.items():
        active_dispatch = [a for a in group if a.get("status") == "ACTIVE" and a.get("authority_rank", 99) <= 2]
        if len(active_dispatch) > 1 and domain not in {"governance_structure", "automation", "founder_canon"}:
            issues.append(
                {
                    "type": "multiple_active_dispatch",
                    "domain": domain,
                    "artifacts": [a["artifact_id"] for a in active_dispatch],
                    "severity": "review",
                }
            )

    for art in arts:
        if art.get("status") == "ACTIVE_BASE":
            for amended in graph.get(art["artifact_id"], {}).get("amended_by", []):
                continue
            if art.get("domain") == "ssot_plane":
                pass
        if art.get("status") == "SUPERSEDED" and art.get("authority_rank", 99) <= 4:
            if art.get("retire_reason"):
                continue
            issues.append(
                {
                    "type": "superseded_live_surface",
                    "artifact_id": art["artifact_id"],
                    "path": art.get("path"),
                    "severity": "high",
                    "note": "Read-surface artifact marked SUPERSEDED — verify this is explicit SG removal, not stale labeling",
                }
            )

    for art in arts:
        if art.get("authority_rank", 99) <= 2 and art.get("owner_repo") != "sina-governance-ssot":
            issues.append(
                {
                    "type": "authority_owner_mismatch",
                    "artifact_id": art["artifact_id"],
                    "severity": "high",
                }
            )

    for art in arts:
        for dep in art.get("depends_on", []) + art.get("amends", []):
            if dep not in graph:
                issues.append(
                    {
                        "type": "missing_lineage_target",
                        "artifact_id": art["artifact_id"],
                        "missing": dep,
                        "severity": "high",
                    }
                )

    stale_hits = scan_stale_language()
    return {
        "issues": issues,
        "stale_language_hits": stale_hits,
        "ok": not stale_hits and not any(i["severity"] == "high" for i in issues),
    }


def scan_stale_language(path: Path | None = None) -> list[dict]:
    registry = load_registry()
    phrases = registry.get("stale_language_guard_patterns", [])
    hits: list[dict] = []

    targets: list[Path]
    if path is not None:
        targets = [path]
    else:
        targets = []
        for base in (ROOT, LIBRARY):
            if not base.exists():
                continue
            for candidate in base.rglob("*"):
                if candidate.is_file() and candidate.suffix.lower() in {".md", ".json", ".txt", ".html"}:
                    targets.append(candidate)

    for target in targets:
        if target.resolve() in {p.resolve() for p in GUARD_FILES}:
            continue
        text = read_text(target)
        for phrase in phrases:
            if phrase.lower() in text.lower():
                hits.append({"path": str(target), "phrase": phrase})
    return hits


def impact_analysis(path: Path, registry: dict) -> dict:
    classification = classify_artifact(path, registry)
    rel = classification.get("registry_path")
    by_path = registry_by_path(registry)
    match = by_path.get(rel or "", None)
    graph = build_reference_graph(registry)
    domain = classification["proposed_domain"]
    layer = classification["proposed_layer"]

    downstream: list[str] = []
    if match:
        aid = match["artifact_id"]
        for other_id, node in graph.items():
            if aid in node.get("depends_on", []) or aid in node.get("amends", []):
                downstream.append(other_id)
        for pointer in match.get("must_point_here", []):
            downstream.append(pointer)

    must_update = list(registry.get("entry_points", []))
    if classification["authority_rank"] <= 2:
        for art in registry.get("artifacts", []):
            if layer in art.get("affects_layers", []) or domain == art.get("domain"):
                must_update.extend(art.get("must_point_here", []))

    lineage = []
    if match:
        lineage = {
            "depends_on": match.get("depends_on", []),
            "amends": match.get("amends", []),
            "amended_by": graph.get(match["artifact_id"], {}).get("amended_by", []),
        }

    related = [
        {
            "artifact_id": art.get("artifact_id"),
            "path": art.get("path"),
            "version": art.get("version"),
            "status": art.get("status"),
            "layer": art.get("layer"),
            "relationship": _relationship(match, art),
        }
        for art in registry.get("artifacts", [])
        if art.get("domain") == domain and (not match or art.get("artifact_id") != match.get("artifact_id"))
    ]

    stale_hits = scan_stale_language(path)

    result = {
        "classification": classification,
        "registry_match": match,
        "lineage": lineage,
        "downstream_artifacts": sorted(set(downstream)),
        "must_update_pointers": sorted(set(must_update)),
        "related_domain_artifacts": related,
        "stale_language_hits": stale_hits,
        "recommended_actions": build_recommendations(classification, match, related, stale_hits),
    }
    return result


def _relationship(match: dict | None, other: dict) -> str:
    if not match:
        return "same_domain"
    if other.get("artifact_id") in match.get("amends", []):
        return "amends_target"
    if match.get("artifact_id") in other.get("amends", []):
        return "amended_by"
    if other.get("artifact_id") in match.get("depends_on", []):
        return "depends_on_target"
    return "same_domain"


def build_recommendations(classification: dict, match: dict | None, related: list[dict], stale_hits: list[dict]) -> list[str]:
    actions = [
        f"Register or update row in {REGISTRY.relative_to(ROOT)}",
        f"Confirm status={classification['proposed_status']} with confidence={classification['confidence']}",
    ]
    if not match:
        actions.append("Add artifact_id, depends_on, amends, affects_layers, and must_point_here in registry")
    if classification["authority_rank"] >= 4:
        actions.append("Treat as read surface only — SG canonical file remains owner")
    if related:
        actions.append("Review related domain artifacts for amendment-only override")
    if stale_hits:
        actions.append("Remove stale governance language before treating change as live")
    if classification["authority_rank"] <= 2:
        actions.append("Run: python3 scripts/validate_governance_intelligence_v1.py")
        actions.append("Run: python3 scripts/governance_intelligence_engine_v1.py audit --json --write-receipt")
    return actions


def build_review_queue(registry: dict) -> dict:
    gaps = scan_registry_gaps(registry)
    conflicts = true_conflict_scan(registry)
    pointer = pointer_drift_scan(registry)

    items: list[dict] = []
    for row in gaps["unregistered_candidates"]:
        items.append(
            {
                "queue_id": f"Q-UNREG-{hashlib.sha1(row['registry_path'].encode()).hexdigest()[:8]}",
                "kind": "unregistered_candidate",
                "severity": "medium",
                "path": row["registry_path"],
                "classification": row,
                "action": "Add registry row in SG data/governance_artifact_registry_v1.json",
            }
        )
    for row in gaps["classification_drift"]:
        items.append(
            {
                "queue_id": f"Q-DRIFT-{row['artifact_id']}",
                "kind": "classification_drift",
                "severity": "medium",
                "artifact_id": row["artifact_id"],
                "path": row["path"],
                "registry_layer": row["registry_layer"],
                "detected_layer": row["detected_layer"],
                "action": "Reconcile registry row with detected classification",
            }
        )
    for issue in conflicts["issues"]:
        items.append(
            {
                "queue_id": f"Q-{issue['type'].upper()}-{issue.get('artifact_id', issue.get('domain', 'X'))}",
                "kind": issue["type"],
                "severity": issue["severity"],
                "detail": issue,
                "action": "Resolve lineage, owner, or status labeling in SG registry",
            }
        )
    for hit in pointer:
        items.append(
            {
                "queue_id": f"Q-POINTER-{hit['entry_point'].replace('/', '-')}",
                "kind": "pointer_drift",
                "severity": "high",
                "detail": hit,
                "action": "Restore SG authority pointer in entry point",
            }
        )
    for hit in conflicts["stale_language_hits"]:
        items.append(
            {
                "queue_id": f"Q-STALE-{hashlib.sha1((hit['path']+hit['phrase']).encode()).hexdigest()[:8]}",
                "kind": "stale_language",
                "severity": "high",
                "detail": hit,
                "action": "Rewrite stale governance language",
            }
        )

    payload = {
        "schema": "governance_review_queue_v1",
        "version": "1.0.0",
        "saved_at": utc_now(),
        "owner": "SG (sina-governance-ssot)",
        "open_count": len(items),
        "high_severity_count": sum(1 for i in items if i["severity"] == "high"),
        "items": items,
    }
    save_review_queue(payload)
    return payload


def production_audit(registry: dict, write_queue: bool = True) -> dict:
    gaps = scan_registry_gaps(registry)
    conflicts = true_conflict_scan(registry)
    pointers = pointer_drift_scan(registry)
    graph = build_reference_graph(registry)
    queue = build_review_queue(registry) if write_queue else json.loads(REVIEW_QUEUE.read_text(encoding="utf-8")) if REVIEW_QUEUE.is_file() else {}

    ok = (
        not conflicts["stale_language_hits"]
        and not pointers
        and not any(i["severity"] == "high" for i in conflicts["issues"])
    )

    return {
        "schema": "governance-intelligence-audit-v1",
        "audited_at": utc_now(),
        "canon_version": CANON_VERSION,
        "ok": ok,
        "registry_artifacts": len(registry.get("artifacts", [])),
        "discovered_files": gaps["discovered_count"],
        "unregistered_candidates": len(gaps["unregistered_candidates"]),
        "classification_drift": gaps["classification_drift"],
        "pointer_drift": pointers,
        "conflicts": conflicts,
        "graph_nodes": len(graph),
        "review_queue": {
            "path": str(REVIEW_QUEUE.relative_to(ROOT)),
            "open_count": queue.get("open_count", 0),
            "high_severity_count": queue.get("high_severity_count", 0),
        },
    }


def parse_iso_date(value: str | None) -> float:
    if not value:
        return 0.0
    cleaned = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(cleaned).timestamp()
    except ValueError:
        pass
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).replace(tzinfo=timezone.utc).timestamp()
        except ValueError:
            continue
    return 0.0


def parse_version_tuple(version: str | None) -> tuple[int, ...]:
    if not version:
        return (0,)
    parts = re.findall(r"[0-9]+", version)
    return tuple(int(p) for p in parts) if parts else (0,)


def extract_filename_version_tuple(path: Path) -> tuple[int, ...]:
    name = path.name.lower()
    m = re.search(r"v0[_\.]?1[_\.]?(\d+)", name)
    if m:
        return (0, 1, int(m.group(1)))
    m = re.search(r"v0[_\.]?(\d+)[_\.](\d+)", name)
    if m:
        return (0, int(m.group(1)), int(m.group(2)))
    m = re.search(r"v(\d+(?:[_\.]\d+)*)", name)
    if m:
        return parse_version_tuple(m.group(1).replace("_", "."))
    return (0,)


def extract_filename_timestamp(path: Path) -> float:
    m = re.search(r"(20\d{6})-(\d{4})", path.name)
    if not m:
        return 0.0
    try:
        dt = datetime.strptime(f"{m.group(1)}{m.group(2)}", "%Y%m%d%H%M").replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except ValueError:
        return 0.0


def has_edit_log(text: str) -> bool:
    lowered = text.lower()
    return "edit log:" in lowered or bool(re.search(r"v0\.\d+\.\d+\s+—", text))


def detect_intake_status(text: str, path: Path, registry_status: str | None, rubric: dict) -> str:
    if registry_status:
        return registry_status
    intake = rubric.get("intake_rules", {})
    if re.search(r"\*\*Status:\*\*\s*PROPOSED", text, flags=re.IGNORECASE):
        return intake.get("proposed_header_means", "ACTIVE_AMENDMENT")
    if has_edit_log(text):
        return intake.get("edit_log_means", "ACTIVE_AMENDMENT")
    if extract_filename_timestamp(path) > 0 or extract_filename_version_tuple(path) > (0, 1, 0):
        return "ACTIVE_AMENDMENT"
    hinted, _ = best_hint(score_hints(text, STATUS_HINTS), "ACTIVE")
    return hinted


def score_progress(path: Path, text: str, rubric: dict) -> tuple[int, dict]:
    signals = rubric.get("progress_signals", {})
    breakdown: dict[str, int] = {}
    if extract_filename_timestamp(path) > 0:
        breakdown["filename_timestamp"] = signals.get("filename_timestamp", 0)
    if has_edit_log(text):
        breakdown["edit_log_present"] = signals.get("edit_log_present", 0)
    if extract_filename_version_tuple(path) > (0,):
        breakdown["filename_semantic_version"] = signals.get("filename_semantic_version", 0)
    if re.search(r"\*\*Status:\*\*\s*PROPOSED", text, flags=re.IGNORECASE) and has_edit_log(text):
        breakdown["proposed_status_with_edit_log"] = signals.get("proposed_status_with_edit_log", 0)
    if "implementation prompt" in path.name.lower():
        breakdown["implementation_prompt_pair"] = signals.get("implementation_prompt_pair", 0)
    if re.search(r" \d+\.md$", path.name, flags=re.IGNORECASE):
        breakdown["finder_duplicate_penalty"] = -rubric.get("intake_rules", {}).get("undated_duplicate_penalty", 15)
    return sum(breakdown.values()), breakdown


def normalize_heading(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def extract_sections(text: str) -> list[dict]:
    sections: list[dict] = []
    current = {"title": "Preamble", "level": 0, "body": ""}
    for line in text.splitlines():
        if line.startswith("#"):
            if current["body"].strip() or current["title"] != "Preamble":
                sections.append(current)
            level = len(line) - len(line.lstrip("#"))
            title = line.lstrip("#").strip()
            current = {"title": title, "level": level, "body": ""}
        else:
            current["body"] += line + "\n"
    if current["body"].strip() or current["title"] != "Preamble":
        sections.append(current)
    return sections


def score_section(section: dict, rubric: dict) -> dict:
    body = section.get("body", "")
    words = len(re.findall(r"\w+", body))
    signals = rubric.get("section_signals", {})
    breakdown: dict[str, int] = {}
    if words >= 40:
        breakdown["word_count_ge_40"] = signals.get("word_count_ge_40", 0)
    if re.search(r"^\s*[-*]", body, flags=re.MULTILINE):
        breakdown["has_bullets"] = signals.get("has_bullets", 0)
    if "|" in body and "---" in body:
        breakdown["has_table"] = signals.get("has_table", 0)
    if "`" in body or re.search(r"[~/][\w/.-]+", body):
        breakdown["has_code_or_paths"] = signals.get("has_code_or_paths", 0)
    if re.search(r"version|status|active|locked", body, flags=re.IGNORECASE):
        breakdown["has_version_or_status_words"] = signals.get("has_version_or_status_words", 0)
    if re.search(r"\bmust\b|\bforbidden\b|\bnever\b", body, flags=re.IGNORECASE):
        breakdown["has_must_or_forbidden"] = signals.get("has_must_or_forbidden", 0)
    total = sum(breakdown.values())
    return {
        "title": section.get("title"),
        "normalized_title": normalize_heading(section.get("title", "")),
        "word_count": words,
        "score": total,
        "breakdown": breakdown,
    }


def score_document(path: Path, registry: dict, rubric: dict) -> dict:
    text = read_text(path)
    classification = classify_artifact(path, registry)
    rel = classification.get("registry_path")
    match = registry_by_path(registry).get(rel or "")
    stale_hits = scan_stale_language(path)
    signals = rubric.get("document_signals", {})
    breakdown: dict[str, int] = {}

    if classification.get("proposed_version"):
        breakdown["version_declared"] = signals.get("version_declared", 0)
    if classification.get("saved_at"):
        breakdown["saved_at_declared"] = signals.get("saved_at_declared", 0)
    if score_hints(text, STATUS_HINTS):
        breakdown["status_declared"] = signals.get("status_declared", 0)
    if "locked" in path.name.lower():
        breakdown["locked_filename"] = signals.get("locked_filename", 0)
    if match:
        breakdown["registry_row"] = signals.get("registry_row", 0)
    rank = classification.get("authority_rank", 99)
    if rank == 1:
        breakdown["sg_owner_rank_1"] = signals.get("sg_owner_rank_1", 0)
    elif rank == 2:
        breakdown["sg_owner_rank_2"] = signals.get("sg_owner_rank_2", 0)
    elif rank == 3:
        breakdown["sg_owner_rank_3"] = signals.get("sg_owner_rank_3", 0)
    if re.search(r"depends_on|amends|amended by|lineage", text, flags=re.IGNORECASE):
        breakdown["lineage_declared"] = signals.get("lineage_declared", 0)
    if "GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md" in text:
        breakdown["authority_pointer"] = signals.get("authority_pointer", 0)
    if not stale_hits:
        breakdown["no_stale_language"] = signals.get("no_stale_language", 0)
    if len(extract_sections(text)) >= 3:
        breakdown["structured_sections_ge_3"] = signals.get("structured_sections_ge_3", 0)
    if len(re.findall(r"\[[^\]]+\]\([^)]+\)|`[^`]+`", text)) >= 2:
        breakdown["cross_refs_ge_2"] = signals.get("cross_refs_ge_2", 0)
    if len(re.findall(r"\w+", text)) >= 200:
        breakdown["word_count_ge_200"] = signals.get("word_count_ge_200", 0)

    total = sum(breakdown.values())
    sections = [score_section(s, rubric) for s in extract_sections(text)]
    registry_status = match.get("status") if match else None
    status = detect_intake_status(text, path, registry_status, rubric)
    status_weight = rubric.get("status_weights", {}).get(status, 50)
    progress_score, progress_breakdown = score_progress(path, text, rubric)
    filename_version = extract_filename_version_tuple(path)
    filename_ts = extract_filename_timestamp(path)
    effective_saved_at = max(parse_iso_date(classification.get("saved_at")), filename_ts)

    return {
        "path": str(path),
        "registry_path": rel,
        "artifact_id": match.get("artifact_id") if match else None,
        "classification": classification,
        "status": status,
        "status_weight": status_weight,
        "completeness_score": total,
        "completeness_breakdown": breakdown,
        "progress_score": progress_score,
        "progress_breakdown": progress_breakdown,
        "sections": sections,
        "saved_at_ts": effective_saved_at,
        "filename_version_tuple": filename_version,
        "version_tuple": parse_version_tuple(classification.get("proposed_version")),
        "has_registry": bool(match),
    }


def candidate_sort_key(candidate: dict) -> tuple:
    return (
        candidate["classification"]["authority_rank"],
        -candidate.get("progress_score", 0),
        -candidate["completeness_score"],
        -candidate["saved_at_ts"],
        candidate.get("filename_version_tuple", (0,)),
        candidate["version_tuple"],
        -candidate["status_weight"],
        -int(candidate["has_registry"]),
    )


def sections_conflict(a: dict, b: dict, rubric: dict) -> bool:
    if not rubric.get("merge_rules", {}).get("conflict_review_on_opposing_markers", True):
        return False
    text = (a.get("body", "") + " " + b.get("body", "")).lower()
    for left, right in rubric.get("opposing_markers", []):
        if left in text and right in text:
            return True
    return False


def build_section_merge_plan(primary: dict, others: list[dict], rubric: dict) -> list[dict]:
    plan: list[dict] = []
    primary_by_title = {s["normalized_title"]: s for s in primary.get("sections", []) if s["normalized_title"]}
    margin = rubric.get("merge_rules", {}).get("adopt_section_margin", 5)
    add_min = rubric.get("merge_rules", {}).get("add_section_min_score", 15)

    for doc in others:
        for section in doc.get("sections", []):
            norm = section.get("normalized_title", "")
            if not norm:
                continue
            primary_section = primary_by_title.get(norm)
            if primary_section:
                if section["score"] > primary_section["score"] + margin:
                    plan.append(
                        {
                            "action": "adopt_section_into_primary",
                            "section": section["title"],
                            "from_path": doc["path"],
                            "over_target_path": primary["path"],
                            "reason": f"section_score {section['score']} > primary {primary_section['score']} + margin {margin}",
                            "conflict_review_required": False,
                        }
                    )
            elif section["score"] >= add_min:
                plan.append(
                    {
                        "action": "add_section_to_primary",
                        "section": section["title"],
                        "from_path": doc["path"],
                        "over_target_path": primary["path"],
                        "reason": f"unique section score {section['score']} >= {add_min}",
                        "conflict_review_required": False,
                    }
                )
    return plan


def decide_cluster(candidates: list[dict], rubric: dict, cluster_by: str = "domain") -> dict:
    if not candidates:
        return {"error": "no_candidates"}

    thread_rubric = load_thread_rubric()
    ranked = sorted(candidates, key=candidate_sort_key)

    if cluster_by == "thread":
        role_ranked = sorted(
            ranked,
            key=lambda c: (
                role_sort_key(detect_thread_role(Path(c["path"]), read_text(Path(c["path"]))), thread_rubric),
                candidate_sort_key(c),
            ),
        )
        primary = next((c for c in role_ranked if c.get("status") != "SUPERSEDED"), role_ranked[0])
    else:
        primary = next((c for c in ranked if c.get("status") != "SUPERSEDED"), ranked[0])
    primary_score = primary["completeness_score"]
    primary_progress = primary.get("progress_score", 0)
    rules = rubric.get("merge_rules", {})

    amendment_finals = []
    base_retain = []
    void_or_pointer = []

    for doc in ranked:
        if doc["path"] == primary["path"]:
            continue
        status = doc.get("status", "ACTIVE")
        rank = doc["classification"]["authority_rank"]
        score = doc["completeness_score"]
        progress = doc.get("progress_score", 0)

        if status == "SUPERSEDED" or (
            rank >= rules.get("void_if_rank_ge", 5)
            and score < primary_score - rules.get("void_if_completeness_below_primary_by", 25)
            and progress < primary_progress - rules.get("void_if_progress_below_primary_by", 20)
        ):
            void_or_pointer.append(
                {
                    "path": doc["path"],
                    "reason": "superseded_or_low_value_read_surface",
                    "role": "pointer_only",
                }
            )
        elif status in {"ACTIVE_AMENDMENT", "ACTIVE_AMENDMENT_TARGET"}:
            amendment_finals.append(
                {
                    "path": doc["path"],
                    "role": "amendment_final",
                    "reason": "newer amendment carrier; wins only on direct conflict",
                }
            )
        elif status == "ACTIVE_BASE":
            retain_sections = [s["title"] for s in doc.get("sections", []) if s["score"] >= 10]
            base_retain.append(
                {
                    "path": doc["path"],
                    "role": "base_retain",
                    "retain_sections": retain_sections,
                    "reason": "older live base; retain non-conflicting sections",
                }
            )
        elif score >= primary_score - 10 and rank <= primary["classification"]["authority_rank"] + 1:
            amendment_finals.append(
                {
                    "path": doc["path"],
                    "role": "candidate_amendment",
                    "reason": "near-primary completeness; review for amendment merge",
                }
            )
        else:
            void_or_pointer.append(
                {
                    "path": doc["path"],
                    "reason": "lower rank or completeness",
                    "role": "pointer_only",
                }
            )

    others = [c for c in ranked if c["path"] != primary["path"]]
    section_merge_plan = build_section_merge_plan(primary, others, rubric)

    return {
        "deterministic_rank_order": [
            {
                "path": c["path"],
                "domain": c["classification"]["proposed_domain"],
                "layer": c["classification"]["proposed_layer"],
                "status": c["status"],
                "authority_rank": c["classification"]["authority_rank"],
                "progress_score": c.get("progress_score", 0),
                "completeness_score": c["completeness_score"],
                "saved_at": c["classification"].get("saved_at"),
            }
            for c in ranked
        ],
        "primary_final": {
            "path": primary["path"],
            "artifact_id": primary.get("artifact_id"),
            "domain": primary["classification"]["proposed_domain"],
            "layer": primary["classification"]["proposed_layer"],
            "status": primary["status"],
            "progress_score": primary.get("progress_score", 0),
            "completeness_score": primary["completeness_score"],
            "reason": "best deterministic tuple: authority_rank, progress, completeness, date, filename_version, body_version, status, registry",
        },
        "amendment_finals": amendment_finals,
        "base_retain": base_retain,
        "void_or_pointer_only": void_or_pointer,
        "section_merge_plan": section_merge_plan,
        "registry_actions": [
            "Set primary_final as ACTIVE carrier in governance_artifact_registry_v1.json",
            "Set amendment_finals as ACTIVE_AMENDMENT rows with amends=[primary artifact_id]",
            "Set base_retain as ACTIVE_BASE rows; never label superseded",
            "Apply section_merge_plan edits in SG repo only",
        ],
    }


def audit_selection(paths: list[Path], domain_filter: str | None = None, cluster_by: str = "domain") -> dict:
    registry = load_registry()
    rubric = load_rubric()
    evaluations: list[dict] = []

    for path in paths:
        if not path.is_file() or should_exclude_path(path):
            continue
        evaluation = score_document(path, registry, rubric)
        if domain_filter and evaluation["classification"]["proposed_domain"] != domain_filter:
            continue
        evaluations.append(evaluation)

    clusters: dict[str, list[dict]] = {}
    for ev in evaluations:
        domain = ev["classification"]["proposed_domain"]
        layer = ev["classification"]["proposed_layer"]
        if cluster_by == "thread":
            key = normalize_thread_id(Path(ev["path"]))
        elif cluster_by == "domain_layer":
            key = f"{domain}|{layer}"
        else:
            key = domain
        clusters.setdefault(key, []).append(ev)

    cluster_results = []
    for cluster_id, candidates in sorted(clusters.items()):
        if cluster_by == "thread":
            domain = candidates[0]["classification"]["proposed_domain"] if candidates else "unknown"
            layer = candidates[0]["classification"]["proposed_layer"] if candidates else "mixed"
        elif cluster_by == "domain_layer":
            domain, layer = cluster_id.split("|", 1)
        else:
            domain, layer = cluster_id, "mixed"
        cluster_results.append(
            {
                "cluster_id": cluster_id,
                "domain": domain,
                "layer": layer,
                "candidate_count": len(candidates),
                "candidates": [
                    {
                        "path": c["path"],
                        "artifact_id": c.get("artifact_id"),
                        "thread_role": detect_thread_role(Path(c["path"]), read_text(Path(c["path"]))),
                        "status": c["status"],
                        "progress_score": c.get("progress_score", 0),
                        "completeness_score": c["completeness_score"],
                        "authority_rank": c["classification"]["authority_rank"],
                    }
                    for c in sorted(candidates, key=candidate_sort_key)
                ],
                "decision": decide_cluster(candidates, rubric, cluster_by=cluster_by),
            }
        )

    return {
        "schema": "governance-final-version-audit-v1",
        "audited_at": utc_now(),
        "canon_version": CANON_VERSION,
        "rubric": str(RUBRIC.relative_to(ROOT)),
        "selected_count": len(evaluations),
        "cluster_count": len(cluster_results),
        "domain_filter": domain_filter,
        "cluster_by": cluster_by,
        "clusters": cluster_results,
        "ok": bool(cluster_results),
    }


def cmd_thread_audit(root_str: str, as_json: bool, write_receipt_flag: bool) -> int:
    root = Path(root_str).expanduser().resolve()
    paths = collect_paths(root)
    registry = load_registry()
    rubric = load_rubric()

    def score_fn(path: Path) -> dict:
        return score_document(path, registry, rubric)

    result = evaluate_paths_as_threads(paths, score_fn)
    if write_receipt_flag:
        result["receipt_path"] = str(write_receipt("thread-audit", result))
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def _score_fn_factory() -> tuple[dict, dict, Any]:
    registry = load_registry()
    rubric = load_rubric()

    def score_fn(path: Path) -> dict:
        return score_document(path, registry, rubric)

    return registry, rubric, score_fn


def cmd_promote_intake_drafts(root_str: str, apply: bool, as_json: bool) -> int:
    from governance_promote_intake_drafts_v1 import build_intake_manifest, promote_intake_manifest  # noqa: WPS433
    from governance_registry_ops_v1 import load_registry  # noqa: WPS433

    root = Path(root_str).expanduser().resolve()
    registry = load_registry()
    manifest = build_intake_manifest(root, registry)
    result = promote_intake_manifest(manifest, apply=apply)
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_promote_intake_artifacts(root_str: str, apply: bool, as_json: bool) -> int:
    """Deprecated alias — evidence sink promotion (not Tag name, not Downloads-only)."""
    return cmd_promote_intake_drafts(root_str, apply, as_json)


def cmd_promote_library_drafts(root_str: str, apply: bool, as_json: bool) -> int:
    from governance_promote_library_drafts_v1 import build_library_manifest, promote_library_drafts  # noqa: WPS433

    root = Path(root_str).expanduser().resolve()
    paths = list(root.rglob("*.md")) if root.is_dir() else []
    manifest = build_library_manifest(paths, root)
    result = promote_library_drafts(manifest, apply=apply)
    result["manifest"] = manifest
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_promote_tag_drafts(root_str: str, apply: bool, as_json: bool) -> int:
    """Deprecated alias — use promote-intake-drafts (evidence sink, not folder name Tag)."""
    return cmd_promote_intake_drafts(root_str, apply, as_json)


def cmd_intake_audit(root_str: str, as_json: bool, write_receipt_flag: bool, plain_only: bool) -> int:
    """Unified intake machine: first pass + evidence second pass + story + merge plan + coherence."""
    root = Path(root_str).expanduser().resolve()
    paths = collect_paths(root)
    _, _, score_fn = _score_fn_factory()
    first_pass = evaluate_paths_as_threads(paths, score_fn)
    second_pass = second_pass_thread_audit(paths, root, build_thread_record, score_fn, first_pass_audit=first_pass)
    selection_audit = audit_selection(paths, cluster_by="thread")
    merge_plan = build_merge_plan(second_pass, selection_audit, load_repo_map())
    story = build_session_story(first_pass, merge_plan=merge_plan, intake_root=str(root))
    second_story = build_second_pass_story(second_pass, load_repo_map())
    from governance_intake_path_intelligence_v1 import run_coherence_checks

    coherence_errors = run_coherence_checks(second_pass, load_path_rubric())
    payload = {
        "first_pass": first_pass,
        "second_pass": second_pass,
        "merge_plan": merge_plan,
        "coherence_errors": coherence_errors,
        "coherence_ok": not coherence_errors,
        "plain_story": story.get("plain_story", "") + "\n\n" + second_story,
    }
    if write_receipt_flag:
        payload["receipt_path"] = str(write_receipt("intake-audit", payload))
    if plain_only:
        print(payload["plain_story"])
        if coherence_errors:
            print("\n## COHERENCE FAILURES")
            for e in coherence_errors:
                print(f"- {e}")
    else:
        print(json.dumps(payload, indent=2) if as_json else payload["plain_story"])
    return 0 if not coherence_errors else 1


def cmd_second_pass_audit(root_str: str, as_json: bool, write_receipt_flag: bool, plain_only: bool) -> int:
    root = Path(root_str).expanduser().resolve()
    paths = collect_paths(root)
    _, _, score_fn = _score_fn_factory()
    first_pass = evaluate_paths_as_threads(paths, score_fn)
    second_pass = second_pass_thread_audit(
        paths,
        root,
        build_thread_record,
        score_fn,
        first_pass_audit=first_pass,
    )
    story = build_second_pass_story(second_pass, load_repo_map())
    payload = {"first_pass": first_pass, "second_pass": second_pass, "plain_story": story}
    if write_receipt_flag:
        payload["receipt_path"] = str(write_receipt("second-pass-audit", second_pass))
    if plain_only:
        print(story)
    else:
        print(json.dumps(payload, indent=2) if as_json else story)
    return 0 if second_pass.get("ok") else 1


def cmd_session_story(root_str: str, as_json: bool, write_receipt_flag: bool, plain_only: bool) -> int:
    root = Path(root_str).expanduser().resolve()
    paths = collect_paths(root)
    _, _, score_fn = _score_fn_factory()
    thread_audit = evaluate_paths_as_threads(paths, score_fn)
    selection_audit = audit_selection(paths, cluster_by="thread")
    merge_plan = build_merge_plan(thread_audit, selection_audit, load_repo_map())
    story = build_session_story(thread_audit, merge_plan=merge_plan, intake_root=str(root))
    second_pass = second_pass_thread_audit(paths, root, build_thread_record, score_fn, first_pass_audit=thread_audit)
    second_story = build_second_pass_story(second_pass, load_repo_map())
    payload = {
        "thread_audit": thread_audit,
        "selection_audit": selection_audit,
        "merge_plan": merge_plan,
        "session_story": story,
        "second_pass_audit": second_pass,
        "second_pass_story": second_story,
    }
    if write_receipt_flag:
        payload["receipt_path"] = str(write_receipt("session-story", {**story, "second_pass": second_pass}))
    if plain_only:
        print(story.get("plain_story", ""))
        print("")
        print(second_story)
    else:
        print(json.dumps(payload, indent=2) if as_json else story.get("plain_story", "") + "\n\n" + second_story)
    return 0 if story.get("ok") else 1


def cmd_merge_plan(root_str: str, as_json: bool, write_receipt_flag: bool) -> int:
    root = Path(root_str).expanduser().resolve()
    paths = collect_paths(root)
    _, _, score_fn = _score_fn_factory()
    thread_audit = evaluate_paths_as_threads(paths, score_fn)
    selection_audit = audit_selection(paths, cluster_by="thread")
    plan = build_merge_plan(thread_audit, selection_audit, load_repo_map())
    if write_receipt_flag:
        plan["receipt_path"] = str(write_receipt("merge-plan", plan))
    print(json.dumps(plan, indent=2) if as_json else json.dumps(plan, indent=2))
    return 0 if plan.get("ok") else 1


def cmd_merge_apply(root_str: str, apply: bool, as_json: bool, write_receipt_flag: bool) -> int:
    root = Path(root_str).expanduser().resolve()
    paths = collect_paths(root)
    _, _, score_fn = _score_fn_factory()
    thread_audit = evaluate_paths_as_threads(paths, score_fn)
    selection_audit = audit_selection(paths, cluster_by="thread")
    plan = build_merge_plan(thread_audit, selection_audit, load_repo_map())
    result = apply_merge_plan(plan, apply=apply)
    result["merge_plan_summary"] = plan.get("summary")
    if write_receipt_flag:
        result["receipt_path"] = str(write_receipt("merge-apply", result))
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_audit_selection(paths: list[str], domain: str | None, cluster_by: str, as_json: bool, write_receipt_flag: bool) -> int:
    resolved = [Path(p).expanduser().resolve() for p in paths]
    result = audit_selection(resolved, domain_filter=domain, cluster_by=cluster_by)
    if write_receipt_flag:
        result["receipt_path"] = str(write_receipt("audit-selection", result))
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_score(path_str: str, as_json: bool) -> int:
    path = Path(path_str).expanduser().resolve()
    result = score_document(path, load_registry(), load_rubric())
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0


def write_receipt(command: str, payload: dict) -> Path:
    RECEIPTS.mkdir(parents=True, exist_ok=True)
    rid = f"governance-intelligence-{utc_stamp()}"
    body = {
        "schema": "governance-intelligence-receipt-v1",
        "receipt_id": rid,
        "recorded_at": utc_now(),
        "canon_version": CANON_VERSION,
        "command": command,
        "ok": payload.get("ok", True),
        "result": payload,
    }
    out = RECEIPTS / f"{rid}.json"
    out.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")
    return out


def cmd_classify(path_str: str, as_json: bool) -> int:
    path = Path(path_str).expanduser().resolve()
    result = classify_artifact(path, load_registry())
    print(json.dumps(result, indent=2) if as_json else "\n".join(f"{k}: {v}" for k, v in result.items()))
    return 0


def cmd_impact(path_str: str, as_json: bool, write_receipt_flag: bool) -> int:
    path = Path(path_str).expanduser().resolve()
    result = impact_analysis(path, load_registry())
    if write_receipt_flag:
        result["receipt_path"] = str(write_receipt("impact", result))
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0


def cmd_scan(as_json: bool) -> int:
    result = scan_registry_gaps(load_registry())
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0


def cmd_audit(as_json: bool, write_receipt_flag: bool, write_queue: bool) -> int:
    result = production_audit(load_registry(), write_queue=write_queue)
    if write_receipt_flag:
        result["receipt_path"] = str(write_receipt("audit", result))
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_conflicts(as_json: bool, write_receipt_flag: bool) -> int:
    result = true_conflict_scan(load_registry())
    if write_receipt_flag:
        result["receipt_path"] = str(write_receipt("conflicts", result))
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_graph(as_json: bool) -> int:
    result = build_reference_graph(load_registry())
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0


def cmd_review_queue(as_json: bool) -> int:
    result = build_review_queue(load_registry())
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))
    return 0


def _print_ops(result: dict, as_json: bool) -> None:
    print(json.dumps(result, indent=2) if as_json else json.dumps(result, indent=2))


def cmd_structure_tree(as_json: bool) -> int:
    result = build_structure_tree_view(load_registry_ops(), load_structure_tree(), load_thread_registry())
    _print_ops(result, as_json)
    return 0


def cmd_registry_list(layer: str | None, domain: str | None, status: str | None, as_json: bool) -> int:
    result = op_registry_list(load_registry_ops(), layer, domain, status)
    _print_ops(result, as_json)
    return 0


def cmd_registry_show(artifact_id: str, as_json: bool) -> int:
    result = op_registry_show(load_registry_ops(), artifact_id)
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def cmd_registry_add(spec_json: str, apply: bool, as_json: bool, write_receipt: bool) -> int:
    spec = json.loads(spec_json)
    result = op_registry_add(load_registry_ops(), load_structure_tree(), spec, apply=apply)
    if write_receipt and result.get("ok") and apply:
        result["receipt_path"] = str(write_receipt("registry-add", result))
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def cmd_registry_amend(artifact_id: str, amends: str, status: str | None, apply: bool, as_json: bool) -> int:
    result = op_registry_amend(load_registry_ops(), artifact_id, amends, status, apply=apply)
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def cmd_registry_retire(artifact_id: str, reason: str, apply: bool, as_json: bool) -> int:
    result = op_registry_retire(load_registry_ops(), artifact_id, reason, apply=apply)
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def cmd_registry_remove(artifact_id: str, apply: bool, as_json: bool) -> int:
    result = op_registry_remove(load_registry_ops(), artifact_id, apply=apply)
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def cmd_thread_list_registry(as_json: bool) -> int:
    result = op_thread_list(load_thread_registry())
    _print_ops(result, as_json)
    return 0


def cmd_thread_register(thread_id: str, from_staging: bool, apply: bool, as_json: bool) -> int:
    result = op_thread_register(load_thread_registry(), thread_id, from_staging, None, apply=apply)
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def cmd_thread_retire(thread_id: str, reason: str, apply: bool, as_json: bool) -> int:
    result = op_thread_retire(load_thread_registry(), thread_id, reason, apply=apply)
    _print_ops(result, as_json)
    return 0 if result.get("ok") else 1


def main() -> int:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument("--json", action="store_true")
    parent.add_argument("--write-receipt", action="store_true")
    parent.add_argument("--no-write-queue", action="store_true")

    parser = argparse.ArgumentParser(description="Governance intelligence engine v1 (production)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_classify = sub.add_parser("classify", parents=[parent])
    p_classify.add_argument("--path", required=True)

    p_impact = sub.add_parser("impact", parents=[parent])
    p_impact.add_argument("--path", required=True)

    p_score = sub.add_parser("score", parents=[parent])
    p_score.add_argument("--path", required=True)

    p_select = sub.add_parser("audit-selection", parents=[parent])
    p_select.add_argument("--paths", required=True, help="Comma-separated file paths")
    p_select.add_argument("--domain", default=None, help="Optional domain filter")
    p_select.add_argument("--cluster-by", default="domain", choices=["domain", "domain_layer", "thread"])

    p_threads = sub.add_parser("thread-audit", parents=[parent])
    p_threads.add_argument("--root", required=True, help="Folder or file root to audit threads")

    p_story = sub.add_parser("session-story", parents=[parent])
    p_story.add_argument("--root", required=True, help="Intake folder for full plain-language story")
    p_story.add_argument("--plain-only", action="store_true", help="Print only the narrative markdown")

    p_second = sub.add_parser("second-pass-audit", parents=[parent])
    p_second.add_argument("--root", required=True, help="Intake folder for evidence-based second machine recheck")
    p_second.add_argument("--plain-only", action="store_true", help="Print only the second-pass narrative")

    p_intake = sub.add_parser("intake-audit", parents=[parent])
    p_intake.add_argument("--root", required=True, help="Full unified intake audit with coherence gate")
    p_intake.add_argument("--plain-only", action="store_true")

    p_sink = sub.add_parser("promote-intake-drafts", parents=[parent])
    p_sink.add_argument("--root", required=True, help="Intake root — evidence sink inferred (md + zip)")
    p_sink.add_argument("--apply", action="store_true", help="Write PROPOSED registry + thread rows")

    p_promote = sub.add_parser("promote-tag-drafts", parents=[parent])
    p_promote.add_argument("--root", required=True, help="DEPRECATED alias for promote-intake-drafts")
    p_promote.add_argument("--apply", action="store_true", help="Write PROPOSED registry + thread rows")

    p_lib = sub.add_parser("promote-library-drafts", parents=[parent])
    p_lib.add_argument("--root", required=True, help="Intake root — scan __AWAITING_UPLOAD__ + library_promote_pending")
    p_lib.add_argument("--apply", action="store_true", help="Copy to canonical noetfield-library + clear pending flags")

    p_full = sub.add_parser("promote-intake-artifacts", parents=[parent])
    p_full.add_argument("--root", required=True, help="DEPRECATED alias for promote-intake-drafts")
    p_full.add_argument("--apply", action="store_true", help="Register PROPOSED artifacts from evidence sink")

    p_mplan = sub.add_parser("merge-plan", parents=[parent])
    p_mplan.add_argument("--root", required=True, help="Folder root for manual+auto merge plan")

    p_mapply = sub.add_parser("merge-apply", parents=[parent])
    p_mapply.add_argument("--root", required=True, help="Folder root to build plan and apply")
    p_mapply.add_argument("--apply", action="store_true", help="Actually write SG intake staging (default dry-run)")

    sub.add_parser("scan", parents=[parent])
    sub.add_parser("audit", parents=[parent])
    sub.add_parser("conflicts", parents=[parent])
    sub.add_parser("graph", parents=[parent])
    sub.add_parser("review-queue", parents=[parent])
    sub.add_parser("structure-tree", parents=[parent])

    p_rlist = sub.add_parser("registry-list", parents=[parent])
    p_rlist.add_argument("--layer", default=None)
    p_rlist.add_argument("--domain", default=None)
    p_rlist.add_argument("--status", default=None)

    p_rshow = sub.add_parser("registry-show", parents=[parent])
    p_rshow.add_argument("--id", required=True)

    p_radd = sub.add_parser("registry-add", parents=[parent])
    p_radd.add_argument("--spec", required=True, help="JSON artifact spec")
    p_radd.add_argument("--apply", action="store_true")

    p_ramend = sub.add_parser("registry-amend", parents=[parent])
    p_ramend.add_argument("--id", required=True)
    p_ramend.add_argument("--amends", required=True)
    p_ramend.add_argument("--status", default=None)
    p_ramend.add_argument("--apply", action="store_true")

    p_rretire = sub.add_parser("registry-retire", parents=[parent])
    p_rretire.add_argument("--id", required=True)
    p_rretire.add_argument("--reason", required=True)
    p_rretire.add_argument("--apply", action="store_true")

    p_rremove = sub.add_parser("registry-remove", parents=[parent])
    p_rremove.add_argument("--id", required=True)
    p_rremove.add_argument("--apply", action="store_true")

    p_tlist = sub.add_parser("thread-list", parents=[parent])
    p_treg = sub.add_parser("thread-register", parents=[parent])
    p_treg.add_argument("--thread-id", required=True)
    p_treg.add_argument("--from-staging", action="store_true")
    p_treg.add_argument("--apply", action="store_true")
    p_tretire = sub.add_parser("thread-retire", parents=[parent])
    p_tretire.add_argument("--thread-id", required=True)
    p_tretire.add_argument("--reason", required=True)
    p_tretire.add_argument("--apply", action="store_true")

    args = parser.parse_args()

    if args.command == "classify":
        return cmd_classify(args.path, args.json)
    if args.command == "impact":
        return cmd_impact(args.path, args.json, args.write_receipt)
    if args.command == "score":
        return cmd_score(args.path, args.json)
    if args.command == "audit-selection":
        paths = [p.strip() for p in args.paths.split(",") if p.strip()]
        return cmd_audit_selection(paths, args.domain, args.cluster_by, args.json, args.write_receipt)
    if args.command == "thread-audit":
        return cmd_thread_audit(args.root, args.json, args.write_receipt)
    if args.command == "session-story":
        return cmd_session_story(args.root, args.json, args.write_receipt, getattr(args, "plain_only", False))
    if args.command == "second-pass-audit":
        return cmd_second_pass_audit(args.root, args.json, args.write_receipt, getattr(args, "plain_only", False))
    if args.command == "intake-audit":
        return cmd_intake_audit(args.root, args.json, args.write_receipt, getattr(args, "plain_only", False))
    if args.command == "promote-intake-drafts":
        return cmd_promote_intake_drafts(args.root, getattr(args, "apply", False), args.json)
    if args.command == "promote-tag-drafts":
        return cmd_promote_tag_drafts(args.root, getattr(args, "apply", False), args.json)
    if args.command == "promote-library-drafts":
        return cmd_promote_library_drafts(args.root, getattr(args, "apply", False), args.json)
    if args.command == "promote-intake-artifacts":
        return cmd_promote_intake_artifacts(args.root, getattr(args, "apply", False), args.json)
    if args.command == "merge-plan":
        return cmd_merge_plan(args.root, args.json, args.write_receipt)
    if args.command == "merge-apply":
        return cmd_merge_apply(args.root, getattr(args, "apply", False), args.json, args.write_receipt)
    if args.command == "scan":
        return cmd_scan(args.json)
    if args.command == "audit":
        return cmd_audit(args.json, args.write_receipt, not args.no_write_queue)
    if args.command == "conflicts":
        return cmd_conflicts(args.json, args.write_receipt)
    if args.command == "graph":
        return cmd_graph(args.json)
    if args.command == "review-queue":
        return cmd_review_queue(args.json)
    if args.command == "structure-tree":
        return cmd_structure_tree(args.json)
    if args.command == "registry-list":
        return cmd_registry_list(args.layer, args.domain, args.status, args.json)
    if args.command == "registry-show":
        return cmd_registry_show(args.id, args.json)
    if args.command == "registry-add":
        return cmd_registry_add(args.spec, args.apply, args.json, args.write_receipt)
    if args.command == "registry-amend":
        return cmd_registry_amend(args.id, args.amends, args.status, args.apply, args.json)
    if args.command == "registry-retire":
        return cmd_registry_retire(args.id, args.reason, args.apply, args.json)
    if args.command == "registry-remove":
        return cmd_registry_remove(args.id, args.apply, args.json)
    if args.command == "thread-list":
        return cmd_thread_list_registry(args.json)
    if args.command == "thread-register":
        return cmd_thread_register(args.thread_id, args.from_staging, args.apply, args.json)
    if args.command == "thread-retire":
        return cmd_thread_retire(args.thread_id, args.reason, args.apply, args.json)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
