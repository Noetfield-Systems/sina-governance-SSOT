#!/usr/bin/env python3
"""AGENT_READ_STALENESS_v1 — alive docs, stale pointers, reasoning + repair queue."""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SURFACES = ROOT / "data" / "agent_read_surfaces_v1.json"
PATTERNS = ROOT / "data" / "stale_law_guard_patterns_v1.json"
QUEUE = ROOT / "data" / "governance_stale_pointer_queue_v1.json"
LIBRARY_REG = ROOT / "SG-Canonical-Library" / "LIBRARY_REGISTRY.json"
RECEIPTS = ROOT / "receipts"

ORG_REPO_ROOTS = [
    Path.home() / "Desktop" / "Noetfield-Systems",
    Path.home() / "Projects",
]

WORKFLOW_SKIP_PARTS = {
    ".worktrees",
    "copilot-worktrees",
    "node_modules",
    ".git",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def expand_path(raw: str) -> Path:
    return Path(raw.replace("~/", f"{Path.home()}/")).expanduser()


def resolve_read_path(entry: dict) -> Path | None:
    candidates = [expand_path(entry["path"])]
    for alt in entry.get("alt_paths") or []:
        candidates.append(expand_path(alt))
    if entry.get("repo") == "sina-governance-ssot" and not entry["path"].startswith("~"):
        p = ROOT / entry["path"]
        if p.is_file():
            return p
    for c in candidates:
        if c.is_file():
            return c
    return None


def excluded(rel: str, globs: list[str]) -> bool:
    return any(fnmatch.fnmatch(rel, g) for g in globs)


def skip_workflow_path(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & WORKFLOW_SKIP_PARTS)


def collect_authority_files(surfaces: dict) -> list[tuple[Path, str]]:
    out: list[tuple[Path, str]] = []
    for rel in surfaces.get("scan_roots_authority", []):
        p = ROOT / rel
        if p.is_file():
            out.append((p, "ACTIVE"))
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in {".md", ".json", ".mdc", ".yml"}:
                    rel_s = str(f.relative_to(ROOT))
                    if not excluded(rel_s, surfaces.get("exclude_globs", [])):
                        out.append((f, "ACTIVE"))
    return out


def scan_stale_patterns(text: str, pattern: dict, status: str) -> list[dict]:
    if status not in pattern.get("applies_to_status", ["ACTIVE"]):
        return []
    rx = re.compile(pattern["regex"], re.IGNORECASE)
    skip_rx = re.compile(
        r"retired_deploy_surfaces|must_not_own|replaced_by|retire candidate|RETIRED for|legacy_preview",
        re.IGNORECASE,
    )
    hits = []
    for line_no, line in enumerate(text.splitlines(), 1):
        if skip_rx.search(line):
            continue
        for m in rx.finditer(line):
            hits.append({"match": m.group(0)[:120], "line": line_no})
    return hits


def scan_workflow_globs(pattern: dict) -> list[dict]:
    findings: list[dict] = []
    globs = pattern.get("scan_workflow_globs") or []
    if not globs:
        return findings
    seen: set[str] = set()
    for base in ORG_REPO_ROOTS:
        if not base.is_dir():
            continue
        for wf in base.glob("**/.github/workflows/*"):
            if not wf.is_file() or skip_workflow_path(wf):
                continue
            rel = str(wf)
            if not any(fnmatch.fnmatch(rel, g) for g in globs):
                continue
            key = f"{wf.parent.parent.parent.name}/{wf.name}"
            if key in seen:
                continue
            body = wf.read_text(encoding="utf-8", errors="replace")
            if re.search(pattern["regex"], body, re.IGNORECASE):
                seen.add(key)
                findings.append({
                    "path": str(wf),
                    "workflow": wf.name,
                    "repo": wf.parent.parent.parent.name,
                })
    return findings


def infer_repo_from_path(path: str) -> str:
    for base in ORG_REPO_ROOTS:
        try:
            p = Path(path)
            if p.is_relative_to(base):
                rel = p.relative_to(base)
                if rel.parts:
                    return rel.parts[0]
        except ValueError:
            continue
    if path.startswith(str(ROOT)):
        return "sina-governance-SSOT"
    return "unknown"


def reason_about(finding: dict) -> dict:
    kind = finding.get("kind", "")
    path = finding.get("path", "")
    repo = finding.get("repo") or infer_repo_from_path(path)
    severity = finding.get("severity", "WARN")

    if kind == "missing_read_surface":
        return {
            "repair_lane": "sg_governance" if "sina-governance" in path or repo == "sina-governance-SSOT" else repo,
            "action": "restore_or_update_registry_path",
            "priority": "P0",
            "reason": "Agent lane references a doc that does not exist on disk — agent will act blind.",
        }
    if kind == "missing_skill":
        return {
            "repair_lane": "sg_governance",
            "action": "fix_skill_path_in_agent_read_surfaces",
            "priority": "P1",
            "reason": "AGENTS.md skill pointer does not resolve — session start load fails.",
        }
    if kind == "stale_law_pattern":
        return {
            "repair_lane": "sg_governance",
            "action": "edit_active_surface_replace_pointer",
            "priority": "P0" if severity == "BLOCKER" else "P1",
            "reason": "ACTIVE law still carries retired terminology — can misroute deploy/spend decisions.",
        }
    if kind == "retired_workflow_motor":
        return {
            "repair_lane": repo if repo != "unknown" else "venture_handoff",
            "action": "disable_schedule_and_mark_retired",
            "priority": "P1",
            "reason": "Workflow motor on disk but deploy truth moved — do not repair retired platform; retire motor.",
        }
    if kind == "library_registry_drift":
        return {
            "repair_lane": "sg_governance",
            "action": "sync_library_registry_or_restore_file",
            "priority": "P1",
            "reason": "LIBRARY_REGISTRY points at missing file — index authority broken.",
        }
    if kind == "superseded_still_active":
        return {
            "repair_lane": "sg_governance",
            "action": "demote_to_READ_SURFACE_or_SUPERSEDED",
            "priority": "P1",
            "reason": "Doc marked superseded but still in ACTIVE scan root.",
        }
    return {
        "repair_lane": "sg_governance",
        "action": "review_manually",
        "priority": "P2",
        "reason": "Unclassified staleness finding.",
    }


def scan_library_registry() -> list[dict]:
    if not LIBRARY_REG.is_file():
        return [{
            "severity": "BLOCKER",
            "kind": "missing_read_surface",
            "path": str(LIBRARY_REG.relative_to(ROOT)),
            "message": "LIBRARY_REGISTRY.json missing",
        }]
    reg = json.loads(LIBRARY_REG.read_text(encoding="utf-8"))
    findings = []
    for layer in reg.get("layers", []):
        for f in layer.get("files", []):
            rel = f.get("path") or f.get("file")
            if not rel:
                continue
            p = ROOT / "SG-Canonical-Library" / rel if not str(rel).startswith("SG-") else ROOT / rel
            if not p.is_file():
                findings.append({
                    "severity": "WARN",
                    "kind": "library_registry_drift",
                    "path": str(rel),
                    "message": "registry entry missing on disk",
                })
    return findings


def build_queue(findings: list[dict]) -> dict:
    items = []
    for i, f in enumerate(findings, 1):
        r = reason_about(f)
        items.append({
            "queue_id": f"GSP-{i:04d}",
            "status": "open",
            "severity": f.get("severity", "WARN"),
            "kind": f.get("kind"),
            "path": f.get("path"),
            "repo": f.get("repo") or infer_repo_from_path(f.get("path", "")),
            "pattern_id": f.get("pattern_id"),
            "message": f.get("message"),
            "replacement": f.get("replacement"),
            "repair_lane": r["repair_lane"],
            "action": r["action"],
            "priority": r["priority"],
            "reason": r["reason"],
            "opened_at": utc_now(),
        })
    open_p0 = sum(1 for x in items if x["priority"] == "P0" and x["status"] == "open")
    return {
        "schema": "governance_stale_pointer_queue_v1",
        "version": "1.0.0",
        "updated_at": utc_now(),
        "open_count": len(items),
        "open_p0": open_p0,
        "items": items,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-receipt", action="store_true")
    parser.add_argument("--write-queue", action="store_true")
    parser.add_argument("--fail-on", choices=["blocker", "warn", "never"], default="blocker")
    args = parser.parse_args()

    surfaces = json.loads(SURFACES.read_text(encoding="utf-8"))
    patterns_doc = json.loads(PATTERNS.read_text(encoding="utf-8"))
    patterns = patterns_doc.get("patterns", [])
    exclude = surfaces.get("exclude_globs", [])

    findings: list[dict] = []
    alive: list[dict] = []
    missing: list[dict] = []

    for lane_id, lane in surfaces.get("lanes", {}).items():
        for entry in lane.get("must_read", []):
            p = resolve_read_path(entry)
            if p is None:
                if entry.get("optional"):
                    continue
                missing.append({
                    "severity": "BLOCKER",
                    "kind": "missing_read_surface",
                    "lane": lane_id,
                    "path": entry["path"],
                    "role": entry.get("role"),
                })
            else:
                mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d")
                alive.append({
                    "lane": lane_id,
                    "path": str(p),
                    "status": entry.get("status", "ACTIVE"),
                    "role": entry.get("role"),
                    "last_modified": mtime,
                })
        for skill in lane.get("skills_resolve", []):
            if not expand_path(skill).is_file():
                missing.append({
                    "severity": "WARN",
                    "kind": "missing_skill",
                    "lane": lane_id,
                    "path": skill,
                })

    for path, status in collect_authority_files(surfaces):
        rel = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)
        if excluded(rel, exclude):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if re.search(r"\bSUPERSEDED\b", text[:500], re.IGNORECASE) and status == "ACTIVE":
            if "READ_SURFACE" not in text[:800]:
                findings.append({
                    "severity": "WARN",
                    "kind": "superseded_still_active",
                    "path": rel,
                    "message": "header suggests SUPERSEDED but file is in ACTIVE authority scan",
                })
        for pat in patterns:
            hits = scan_stale_patterns(text, pat, status)
            if hits:
                findings.append({
                    "severity": pat.get("severity", "WARN"),
                    "kind": "stale_law_pattern",
                    "pattern_id": pat["id"],
                    "path": rel,
                    "hits": len(hits),
                    "replacement": pat.get("replacement"),
                    "message": pat.get("message"),
                })

    for pat in patterns:
        for wf in scan_workflow_globs(pat):
            findings.append({
                "severity": pat.get("severity", "WARN"),
                "kind": "retired_workflow_motor",
                "pattern_id": pat["id"],
                "path": wf["path"],
                "repo": wf.get("repo"),
                "message": pat.get("message"),
                "replacement": pat.get("replacement"),
            })

    findings.extend(scan_library_registry())

    all_findings = findings + missing
    blockers = [f for f in all_findings if f.get("severity") == "BLOCKER"]
    warns = [f for f in all_findings if f.get("severity") == "WARN"]

    reasoning = {
        "alive_doc_count": len(alive),
        "authority_scan_roots": surfaces.get("scan_roots_authority", []),
        "retired_deploy_surfaces": [r.get("id") for r in surfaces.get("retired_deploy_surfaces", [])],
        "verdict": "AUTHORITY_CLEAN" if not blockers else "AUTHORITY_BLOCKED",
        "next_actions": [reason_about(f) | {"path": f.get("path")} for f in blockers[:5] + warns[:5]],
        "handoff_by_lane": {},
    }
    queue_doc = build_queue(all_findings)
    for item in queue_doc["items"]:
        lane = item["repair_lane"]
        reasoning["handoff_by_lane"].setdefault(lane, []).append(item["queue_id"])

    result = {
        "schema": "agent_read_staleness_receipt_v1",
        "at": utc_now(),
        "ok": len(blockers) == 0,
        "alive_surfaces": len(alive),
        "blocker_count": len(blockers),
        "warn_count": len(warns),
        "alive": alive,
        "findings": all_findings,
        "blockers": blockers,
        "warns": warns,
        "reasoning": reasoning,
        "queue_summary": {
            "open": queue_doc["open_count"],
            "open_p0": queue_doc["open_p0"],
            "path": "data/governance_stale_pointer_queue_v1.json",
        },
        "closure_token": "AGENT_READ_STALENESS: pass" if not blockers else "AGENT_READ_STALENESS: fail",
    }

    if args.write_queue or args.write_receipt:
        QUEUE.write_text(json.dumps(queue_doc, indent=2) + "\n", encoding="utf-8")

    if args.write_receipt:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = RECEIPTS / f"agent-read-staleness-{stamp}.json"
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        result["receipt_path"] = str(out.relative_to(ROOT))

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("=== Agent read staleness (v1) ===")
        print(f"  alive={len(alive)} blockers={len(blockers)} warns={len(warns)} queue={queue_doc['open_count']}")
        print(f"  reasoning: {reasoning['verdict']}")
        for b in blockers[:15]:
            r = reason_about(b)
            print(f"  BLOCKER [{r['priority']}] {b.get('path')} -> {r['action']} ({r['repair_lane']})")
        for w in warns[:8]:
            r = reason_about(w)
            print(f"  WARN    [{r['priority']}] {w.get('path')} -> {r['action']} ({r['repair_lane']})")
        print(result["closure_token"])

    if args.fail_on == "blocker" and blockers:
        return 1
    if args.fail_on == "warn" and (blockers or warns):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
