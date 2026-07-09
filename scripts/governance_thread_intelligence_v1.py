#!/usr/bin/env python3
"""Thread intelligence — recognize threads, progress, completion, change rationale, quality."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[1]
THREAD_RUBRIC = ROOT / "data/governance_thread_rubric_v1.json"

ROLE_SUFFIX_PATTERNS = [
    r"\s+implementation\s+prompt.*$",
    r"\s+discovery\s+report\s+prompt.*$",
    r"\s+discovery\s+report.*$",
    r"\s+prompt\s*$",
    r"\s+proposed\s+clarification.*$",
]

INTAKE_EXCLUDE_PARTS = ("/tests/", "/fixtures/", "/test/", "/prompts/", "/prompts ")


def should_exclude_path(path: Path) -> bool:
    lowered = str(path).lower()
    return any(part in lowered for part in INTAKE_EXCLUDE_PARTS)


def is_tag_intake_sink(path: str | Path) -> bool:
    """Deprecated — use is_unregistered_intake_draft (evidence-based, no folder name)."""
    from governance_intake_sink_v1 import is_unregistered_governance_draft  # noqa: WPS433
    from governance_registry_ops_v1 import load_registry  # noqa: WPS433

    return is_unregistered_governance_draft(Path(path), load_registry())


def is_unregistered_intake_draft(path: str | Path, registry: dict | None = None) -> bool:
    from governance_intake_sink_v1 import is_unregistered_governance_draft  # noqa: WPS433
    from governance_registry_ops_v1 import load_registry  # noqa: WPS433

    reg = registry if registry is not None else load_registry()
    return is_unregistered_governance_draft(Path(path), reg)


def registry_has_intake_source(registry: dict, path: str) -> dict | None:
    for art in registry.get("artifacts", []):
        if art.get("intake_source") == path:
            return art
    return None


def is_library_upload_placeholder(path: str | Path) -> bool:
    return "__awaiting_upload__" in Path(path).name.lower()


def is_library_sink_path(path: str | Path) -> bool:
    return "noetfield-library" in str(path).lower()


def registry_match_for_library_file(path: Path, registry: dict) -> dict | None:
    stem = path.stem.lower()
    for art in registry.get("artifacts", []):
        aid = art.get("artifact_id", "").lower()
        lib = str(art.get("library_path", "")).lower()
        reg_path = str(art.get("path", "")).lower()
        if stem in aid or stem in lib or stem in reg_path:
            return art
        if aid and aid.replace("-", "_") in stem.replace("-", "_"):
            return art
    return None


def load_thread_rubric() -> dict:
    return json.loads(THREAD_RUBRIC.read_text(encoding="utf-8"))


def normalize_thread_id(path: Path, text: str = "") -> str:
    name = path.stem
    lowered = name.lower()
    if "discovery report" in lowered:
        base = re.sub(r"\s+discovery\s+report.*$", "", name, flags=re.IGNORECASE).strip()
        slug = re.sub(r"[^a-z0-9]+", "_", f"{base} discovery report".lower()).strip("_")
        return slug or "discovery_report"
    name = re.sub(r" \d+$", "", name)
    name = re.sub(r"_v\d+.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r" v0[_\.\d ]+.*$", "", name, flags=re.IGNORECASE)
    name = re.sub(r" \d{8}-\d{4}$", "", name)
    name = re.sub(r"^SSOT CONFLICT LOG — ", "SSOT CONFLICT LOG ", name, flags=re.IGNORECASE)
    name = re.sub(r"^SSOT PROPOSAL — ", "SSOT PROPOSAL ", name, flags=re.IGNORECASE)
    for pattern in ROLE_SUFFIX_PATTERNS:
        name = re.sub(pattern, "", name, flags=re.IGNORECASE)
    name = re.sub(r" — .*$", "", name)
    slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    return slug or "unknown_thread"


def detect_thread_role(path: Path, text: str) -> str:
    name = path.name.lower()
    rel = str(path).lower()
    if re.search(r" \d+\.md$", path.name, flags=re.IGNORECASE):
        return "duplicate_copy"
    if "implementation prompt" in name:
        return "implementation_prompt"
    if "conflict log" in name or "conflict log" in text[:400].lower():
        return "conflict_log"
    if "proposal" in name or re.search(r"\*\*Status:\*\*\s*PROPOSED", text, flags=re.IGNORECASE):
        if "ssot proposal" in text[:200].lower() or "proposed rule" in text[:400].lower():
            return "proposal"
    if "discovery report" in name or "discovery report" in name:
        return "discovery_report"
    if "/prompts/" in rel or "prompts /" in rel:
        return "prompt_companion"
    return "spec"


def has_edit_log(text: str) -> bool:
    lowered = text.lower()
    return "edit log:" in lowered or bool(re.search(r"v0\.\d+\.\d+\s+—", text))


def parse_edit_log(text: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = []
    in_log = False
    for line in text.splitlines():
        if re.match(r"^edit log:\s*$", line, flags=re.IGNORECASE):
            in_log = True
            continue
        if in_log:
            match = re.match(r"\s*v([\d.]+)\s*[—\-–]\s*(.+)", line)
            if match:
                entries.append({"version": match.group(1), "rationale": match.group(2).strip()})
            elif line.strip() and not line.startswith((" ", "\t")):
                break
    return entries


def extract_pending_items(text: str) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    lowered = text.lower()
    if re.search(r"founder action required", lowered):
        items.append({"type": "founder_action", "text": "Founder action required"})
    if re.search(r"awaiting founder approval", lowered):
        items.append({"type": "founder_approval", "text": "Awaiting founder approval"})
    if re.search(r"phase 2", lowered) and re.search(r"phase 1 only|not activated|stub", lowered):
        items.append({"type": "phase_gate", "text": "Phase 2+ not opened"})
    if re.search(r"not yet ratified", lowered):
        items.append({"type": "ratification", "text": "Not yet ratified"})
    if re.search(r"wording patch", lowered):
        items.append({"type": "dependent_patch", "text": "Dependent wording patch required"})
    if re.search(r"awaiting registry|library_promote_pending", lowered):
        items.append({"type": "registry_entry", "text": "Awaiting registry and library entry"})
    return items


def score_change_entry(rationale: str, rubric: dict) -> dict[str, Any]:
    lowered = rationale.lower()
    signals = rubric.get("change_quality_signals", {})
    breakdown: dict[str, int] = {}
    verdict = "neutral"

    for label, weight in signals.get("good", {}).items():
        if label in lowered:
            breakdown[f"good:{label}"] = weight
    for label, weight in signals.get("bad", {}).items():
        if label in lowered:
            breakdown[f"bad:{label}"] = weight
    for label, weight in signals.get("neutral", {}).items():
        if label in lowered:
            breakdown[f"neutral:{label}"] = weight

    total = sum(breakdown.values())
    bands = rubric.get("quality_bands", {})
    if total >= bands.get("good_min", 15):
        verdict = "good"
    elif total <= bands.get("bad_max", -10):
        verdict = "bad"
    return {
        "rationale": rationale,
        "quality_score": total,
        "quality_verdict": verdict,
        "quality_breakdown": breakdown,
    }


def extract_thread_links(text: str, thread_id: str, rubric: dict) -> list[dict[str, str]]:
    links: list[dict[str, str]] = []
    lowered = text.lower()
    for row in rubric.get("thread_link_patterns", []):
        pattern = row.get("pattern", "")
        target = row.get("thread_id", "")
        if not pattern or not target or target == thread_id:
            continue
        if pattern in lowered:
            relation = "references"
            if "corrected" in lowered or "fixed" in lowered or "resolved" in lowered:
                relation = "resolved_by"
            if "requires a wording patch" in lowered or "blocked" in lowered:
                relation = "blocked_by"
            links.append(
                {
                    "to_thread": target,
                    "relation": relation,
                    "evidence": f"mentions '{pattern}'",
                }
            )
    return links


def role_sort_key(role: str, rubric: dict) -> int:
    roles = rubric.get("thread_roles", {})
    return roles.get(role, {}).get("rank", 50)


def thread_completion_state(
    artifacts: list[dict],
    final_carrier: dict | None,
    rubric: dict,
) -> tuple[str, list[dict], list[dict]]:
    if not artifacts:
        return "LEFT_ABANDONED", [], []

    active = [a for a in artifacts if a.get("artifact_state") != "stale_duplicate"]
    stale = [a for a in artifacts if a.get("artifact_state") == "stale_duplicate"]
    pending: list[dict] = []
    left: list[dict] = []

    if final_carrier:
        pending.extend(final_carrier.get("pending_items", []))

    for art in active:
        for item in art.get("pending_items", []):
            if item not in pending:
                pending.append(item)

    for art in stale:
        left.append(
            {
                "path": art["path"],
                "reason": "superseded by newer dated/progress carrier in same thread",
            }
        )

    if not final_carrier and stale:
        return "LEFT_ABANDONED", pending, left
    if not final_carrier:
        return "IN_PROGRESS", pending, left

    if any(p["type"] in {"founder_action", "founder_approval", "ratification"} for p in pending):
        return "PENDING_FOUNDER", pending, left
    if any(p["type"] in {"registry_entry"} for p in pending):
        return "AWAITING_REGISTRY_ENTRY", pending, left
    if any(p["type"] in {"dependent_patch", "phase_gate"} for p in pending):
        return "PENDING_THREAD", pending, left
    if any(p["type"] in {"library_upload"} for p in pending):
        return "AWAITING_LIBRARY_UPLOAD", pending, left
    if any(p["type"] in {"library_promote"} for p in pending):
        return "PENDING_LIBRARY_PROMOTE", pending, left
    if final_carrier.get("role") in {"spec", "proposal", "conflict_log"} and not pending:
        return "COMPLETED", pending, left
    return "IN_PROGRESS", pending, left


def build_thread_record(
    thread_id: str,
    artifacts: list[dict],
    rubric: dict,
    score_document_fn: Callable[[Path], dict],
) -> dict[str, Any]:
    role_ranked = sorted(
        artifacts,
        key=lambda a: (
            role_sort_key(a.get("role", "spec"), rubric),
            -a.get("progress_score", 0),
            -a.get("completeness_score", 0),
        ),
    )

    spec_candidates = [a for a in role_ranked if a.get("role") in {"spec", "proposal", "conflict_log"}]
    evidence_ranked = sorted(
        artifacts,
        key=lambda a: (
            role_sort_key(a.get("role", "spec"), rubric),
            -a.get("evidence_score", a.get("second_pass_progress", a.get("progress_score", 0))),
            -a.get("completeness_score", 0),
        ),
    )
    if any(a.get("evidence_score") for a in artifacts):
        spec_candidates = [a for a in evidence_ranked if a.get("role") in {"spec", "proposal", "conflict_log"}]
        final_carrier = spec_candidates[0] if spec_candidates else evidence_ranked[0]
    else:
        final_carrier = spec_candidates[0] if spec_candidates else (role_ranked[0] if role_ranked else None)

    change_timeline: list[dict] = []
    if final_carrier:
        text = Path(final_carrier["path"]).read_text(encoding="utf-8", errors="ignore")
        for entry in parse_edit_log(text):
            scored = score_change_entry(entry["rationale"], rubric)
            change_timeline.append({"version": entry["version"], **scored})
        if is_unregistered_intake_draft(final_carrier["path"]):
            from governance_registry_ops_v1 import load_registry  # noqa: WPS433

            reg_match = registry_has_intake_source(load_registry(), final_carrier["path"])
            if not reg_match:
                registry_pending = {
                    "type": "registry_entry",
                    "text": "Intake sink draft — new governance artifact awaiting SG registry + library entry",
                }
                pending_items = list(final_carrier.get("pending_items", []))
                if registry_pending not in pending_items:
                    pending_items.append(registry_pending)
                final_carrier = {**final_carrier, "pending_items": pending_items, "has_registry": False}
            else:
                final_carrier = {
                    **final_carrier,
                    "has_registry": True,
                    "registry_artifact_id": reg_match.get("artifact_id"),
                    "library_promote_pending": reg_match.get("library_promote_pending", False),
                }
                if reg_match.get("library_promote_pending"):
                    lib_pending = {
                        "type": "library_promote",
                        "text": "Registered in SG — library pointer promote still pending",
                    }
                    pending_items = list(final_carrier.get("pending_items", []))
                    if lib_pending not in pending_items:
                        pending_items.append(lib_pending)
                    final_carrier = {**final_carrier, "pending_items": pending_items}
        elif is_library_upload_placeholder(final_carrier["path"]):
            upload_pending = {
                "type": "library_upload",
                "text": "Library upload placeholder — canonical copy pending",
            }
            pending_items = list(final_carrier.get("pending_items", []))
            if upload_pending not in pending_items:
                pending_items.append(upload_pending)
            final_carrier = {**final_carrier, "pending_items": pending_items}
        elif is_library_sink_path(final_carrier["path"]):
            from governance_registry_ops_v1 import load_registry  # noqa: WPS433

            reg_match = registry_match_for_library_file(Path(final_carrier["path"]), load_registry())
            if reg_match and reg_match.get("library_promote_pending"):
                lib_pending = {
                    "type": "library_promote",
                    "text": "In SG registry — library pointer promote still pending",
                }
                pending_items = list(final_carrier.get("pending_items", []))
                if lib_pending not in pending_items:
                    pending_items.append(lib_pending)
                final_carrier = {
                    **final_carrier,
                    "pending_items": pending_items,
                    "registry_artifact_id": reg_match.get("artifact_id"),
                    "library_promote_pending": True,
                }
            elif reg_match and reg_match.get("library_path"):
                final_carrier = {**final_carrier, "library_path": reg_match.get("library_path")}

    completion_state, pending, left = thread_completion_state(artifacts, final_carrier, rubric)

    companions = [a for a in artifacts if a.get("path") != (final_carrier or {}).get("path")]
    thread_links: list[dict] = []
    if final_carrier:
        text = Path(final_carrier["path"]).read_text(encoding="utf-8", errors="ignore")
        thread_links = extract_thread_links(text, thread_id, rubric)

    progress_steps = len(change_timeline)
    progress_pct = min(100, 40 + (progress_steps * 10))
    if completion_state == "COMPLETED":
        progress_pct = 100
    elif completion_state == "PENDING_FOUNDER":
        progress_pct = min(progress_pct, 85)
    elif completion_state == "AWAITING_REGISTRY_ENTRY":
        progress_pct = min(progress_pct, 90)
    elif completion_state == "AWAITING_LIBRARY_UPLOAD":
        progress_pct = min(progress_pct, 75)
    elif completion_state == "PENDING_LIBRARY_PROMOTE":
        progress_pct = min(progress_pct, 95)
    elif completion_state == "LEFT_ABANDONED":
        progress_pct = 10

    display_name = thread_id.replace("_", " ").upper()
    if final_carrier:
        display_name = Path(final_carrier["path"]).stem
        display_name = re.sub(r" v0.*$", "", display_name, flags=re.IGNORECASE)
        display_name = re.sub(r" \d{8}-\d{4}$", "", display_name)

    return {
        "thread_id": thread_id,
        "display_name": display_name,
        "domain": final_carrier.get("domain") if final_carrier else artifacts[0].get("domain"),
        "completion_state": completion_state,
        "progress_pct": progress_pct,
        "final_carrier": (
            {
                "path": final_carrier["path"],
                "role": final_carrier.get("role"),
                "version": final_carrier.get("version"),
                "status": final_carrier.get("status"),
                "progress_score": final_carrier.get("progress_score"),
                "completeness_score": final_carrier.get("completeness_score"),
                "pending_items": final_carrier.get("pending_items", []),
            }
            if final_carrier
            else None
        ),
        "companions": [
            {
                "path": c["path"],
                "role": c.get("role"),
                "artifact_state": c.get("artifact_state", "companion"),
            }
            for c in companions
        ],
        "pending_items": pending,
        "left_abandoned": left,
        "change_timeline": change_timeline,
        "change_quality_summary": {
            "good_changes": sum(1 for c in change_timeline if c.get("quality_verdict") == "good"),
            "bad_changes": sum(1 for c in change_timeline if c.get("quality_verdict") == "bad"),
            "neutral_changes": sum(1 for c in change_timeline if c.get("quality_verdict") == "neutral"),
            "net_quality_score": sum(c.get("quality_score", 0) for c in change_timeline),
        },
        "thread_links": thread_links,
        "artifact_count": len(artifacts),
    }


def evaluate_paths_as_threads(
    paths: list[Path],
    score_document_fn: Callable[[Path], dict],
    rubric: dict | None = None,
) -> dict[str, Any]:
    rubric = rubric or load_thread_rubric()
    grouped: dict[str, list[dict]] = {}

    for path in paths:
        if not path.is_file() or should_exclude_path(path):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        scored = score_document_fn(path)
        thread_id = normalize_thread_id(path, text)
        role = detect_thread_role(path, text)
        pending_items = extract_pending_items(text)
        version = scored.get("classification", {}).get("proposed_version")
        artifact_state = "stale_duplicate" if role == "duplicate_copy" else "active"
        if role == "duplicate_copy" and scored.get("progress_score", 0) <= 0:
            artifact_state = "stale_duplicate"

        grouped.setdefault(thread_id, []).append(
            {
                "path": str(path),
                "thread_id": thread_id,
                "role": role,
                "domain": scored.get("classification", {}).get("proposed_domain"),
                "version": version,
                "status": scored.get("status"),
                "progress_score": scored.get("progress_score", 0),
                "completeness_score": scored.get("completeness_score", 0),
                "pending_items": pending_items,
                "artifact_state": artifact_state,
                "edit_log_entries": len(parse_edit_log(text)),
            }
        )

    threads = [build_thread_record(tid, arts, rubric, score_document_fn) for tid, arts in sorted(grouped.items())]

    completed = [t for t in threads if t["completion_state"] == "COMPLETED"]
    pending_founder = [t for t in threads if t["completion_state"] == "PENDING_FOUNDER"]
    pending_thread = [t for t in threads if t["completion_state"] == "PENDING_THREAD"]
    in_progress = [t for t in threads if t["completion_state"] == "IN_PROGRESS"]
    left = [t for t in threads if t["completion_state"] == "LEFT_ABANDONED"]

    return {
        "schema": "governance-thread-audit-v1",
        "thread_count": len(threads),
        "threads": threads,
        "summary": {
            "completed": len(completed),
            "pending_founder": len(pending_founder),
            "pending_thread": len(pending_thread),
            "in_progress": len(in_progress),
            "left_abandoned": len(left),
        },
        "completed_threads": [{"thread_id": t["thread_id"], "final": t["final_carrier"]} for t in completed],
        "open_threads": [
            {
                "thread_id": t["thread_id"],
                "state": t["completion_state"],
                "pending_items": t["pending_items"],
                "final_carrier": (t["final_carrier"] or {}).get("path"),
            }
            for t in threads
            if t["completion_state"] != "COMPLETED"
        ],
        "ok": bool(threads),
    }


def collect_paths(root: Path, suffixes: set[str] | None = None) -> list[Path]:
    suffixes = suffixes or {".md"}
    if root.is_file():
        return [root]
    return [p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in suffixes]
