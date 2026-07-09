#!/usr/bin/env python3
"""L0 repo graph indexer — builds a compact static map of this repo for agent memory.

CANONICAL TEMPLATE — do not hand-edit installed copies. Installed copies in each
repo are RENDERED from this template by scripts/sync_l0_repo_graph_v1.py using the
per-repo config in data/l0_repo_graph_registry_v1.json. To upgrade the logic,
edit THIS file, bump L0_TEMPLATE_VERSION, test in sg-sandbox, then run the sync.

Walks the repo once, writes a full JSON index plus a compact Markdown report.
No network calls, no external DB, no LLM calls — stdlib only.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

L0_TEMPLATE_VERSION = "1.1.0"  # bumped by sync when the shared logic changes

ROOT = Path(__file__).resolve().parents[1]
REPO_NAME = ROOT.name  # self-naming — no longer hardcoded per repo
OUT_DIR = ROOT / "graph-out"
INDEX_PATH = OUT_DIR / "graph_index_v1.json"
REPORT_PATH = OUT_DIR / "GRAPH_REPORT.md"

# Directories never walked, anywhere in the tree.
IGNORED_DIR_NAMES = {
    ".git", "node_modules", "__pycache__", ".pytest_cache", ".wrangler",
    "dist", "build", ".cache", "venv", ".venv", ".noos_cache", "graph-out",
}

# === L0-SUBSYSTEM-CONFIG (rendered by sync_l0_repo_graph_v1.py from the registry — do not hand-edit) ===
SUBSYSTEM_DIRS = [
    "data", "docs", "scripts", "receipts", "tests", ".github",
]
# === END L0-SUBSYSTEM-CONFIG ===

# Extensions scanned for repo-relative path references (edges).
EDGE_SCAN_EXTS = {".py", ".sh", ".md", ".json", ".yaml", ".yml", ".jsonc"}
EDGE_SCAN_MAX_BYTES = 2_000_000  # skip pathologically large files when scanning for edges
TOP_FILES_PER_SUBSYSTEM_IN_REPORT = 6

_subsystem_pattern = "|".join(re.escape(s) for s in SUBSYSTEM_DIRS) or "__none__"
PATH_REF_RE = re.compile(
    r"""(?:^|[\s"'`(\[])((?:%s)/[A-Za-z0-9_\-./]+\.(?:md|json|py|sh|yaml|yml|jsonc|txt))"""
    % _subsystem_pattern
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_ignored_dir(name: str) -> bool:
    return name in IGNORED_DIR_NAMES or name.endswith(".egg-info")


def iter_files(base: Path):
    # Symlink-hardened: skip symlinks (often broken .bin shims / can point outside
    # the repo / create cycles) and survive unreadable paths without crashing.
    try:
        entries = sorted(base.rglob("*"))
    except OSError:
        return
    for path in entries:
        if path.is_symlink():
            continue
        try:
            if path.is_dir():
                continue
        except OSError:
            continue
        if any(is_ignored_dir(part) for part in path.relative_to(ROOT).parts[:-1]):
            continue
        if path.name == ".DS_Store":
            continue
        yield path


def file_record(path: Path):
    try:
        stat = path.stat()
    except OSError:
        return None  # unreadable / vanished / broken link — skip rather than crash
    return {
        "path": str(path.relative_to(ROOT)),
        "bytes": stat.st_size,
        "mtime": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def subsystem_root_dirs() -> list:
    present = []
    for name in SUBSYSTEM_DIRS:
        if (ROOT / name).is_dir():
            present.append(name)
    return present


def build_subsystems() -> dict:
    subsystems = {}
    claimed_top_names = set(subsystem_root_dirs())

    for name in claimed_top_names:
        base = ROOT / name
        files = [r for r in (file_record(p) for p in iter_files(base)) if r]
        subsystems[name] = {
            "path": name,
            "file_count": len(files),
            "total_bytes": sum(f["bytes"] for f in files),
            "files": sorted(files, key=lambda f: -f["bytes"]),
        }

    root_files = []
    for path in sorted(ROOT.glob("*")):
        if path.is_symlink() or path.name == ".DS_Store":
            continue
        if path.is_file():
            rec = file_record(path)
            if rec:
                root_files.append(rec)
    subsystems["_root"] = {
        "path": ".",
        "file_count": len(root_files),
        "total_bytes": sum(f["bytes"] for f in root_files),
        "files": sorted(root_files, key=lambda f: -f["bytes"]),
    }

    return subsystems


def build_edges(subsystems: dict) -> list:
    edges = []
    seen = set()
    for subsystem in subsystems.values():
        for finfo in subsystem["files"]:
            rel = finfo["path"]
            ext = Path(rel).suffix
            if ext not in EDGE_SCAN_EXTS:
                continue
            if finfo["bytes"] > EDGE_SCAN_MAX_BYTES:
                continue
            full = ROOT / rel
            try:
                text = full.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for match in PATH_REF_RE.finditer(text):
                target = match.group(1)
                if target == rel:
                    continue
                key = (rel, target)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"from": rel, "to": target})
    return edges


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    subsystems = build_subsystems()
    edges = build_edges(subsystems)

    total_files = sum(s["file_count"] for s in subsystems.values())
    total_bytes = sum(s["total_bytes"] for s in subsystems.values())

    index = {
        "schema": "l0_repo_graph_index_v1",
        "template_version": L0_TEMPLATE_VERSION,
        "repo": REPO_NAME,
        "generated_at": utc_now(),
        "root": ".",
        "ignored_dirs": sorted(IGNORED_DIR_NAMES),
        "scanned_extensions_for_edges": sorted(EDGE_SCAN_EXTS),
        "subsystems": subsystems,
        "edges": edges,
        "stats": {
            "total_files": total_files,
            "total_bytes": total_bytes,
            "total_edges": len(edges),
            "subsystem_count": len(subsystems) - 1,  # excludes _root
        },
    }

    INDEX_PATH.write_text(json.dumps(index, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.write_text(render_report(index), encoding="utf-8")

    print(f"L0 repo graph built @ {index['generated_at']}  (template v{L0_TEMPLATE_VERSION})")
    print(f"  subsystems: {index['stats']['subsystem_count']}  files: {total_files}  edges: {len(edges)}")
    print(f"  index:  {INDEX_PATH.relative_to(ROOT)}")
    print(f"  report: {REPORT_PATH.relative_to(ROOT)}")
    return 0


def human_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.0f}{unit}" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}TB"


def render_report(index: dict) -> str:
    lines = []
    lines.append(f"# L0 Repo Graph Report — {index['repo']}")
    lines.append("")
    lines.append(f"Generated (last indexed): `{index['generated_at']}` · template `v{index.get('template_version','?')}`")
    lines.append(f"Total files: {index['stats']['total_files']} · "
                 f"Total size: {human_bytes(index['stats']['total_bytes'])} · "
                 f"Edges detected: {index['stats']['total_edges']}")
    lines.append("")
    lines.append(
        "**Read this file first.** Do not spawn broad repo-reading agents "
        "(\"understand the repo\", \"map subsystem X\", \"audit Y\") until you have "
        "read this report and, if you need more detail, queried the index with "
        "`python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>`. "
        "This report + a query response should answer routing questions "
        "(\"which files touch X\", \"how big is subsystem Y\") without opening "
        "every file in the subsystem."
    )
    lines.append("")
    lines.append("## Subsystem map (sorted by size, descending)")
    lines.append("")
    lines.append("| subsystem | files | size | largest files |")
    lines.append("|---|---:|---:|---|")

    subsystems = {k: v for k, v in index["subsystems"].items() if k != "_root"}
    ordered = sorted(subsystems.items(), key=lambda kv: -kv[1]["total_bytes"])
    for name, info in ordered:
        top = info["files"][:TOP_FILES_PER_SUBSYSTEM_IN_REPORT]
        top_str = ", ".join(f"`{f['path']}`" for f in top) if top else "—"
        lines.append(
            f"| {name}/ | {info['file_count']} | {human_bytes(info['total_bytes'])} | {top_str} |"
        )

    root = index["subsystems"].get("_root")
    if root and root["file_count"]:
        top = ", ".join(f"`{f['path']}`" for f in root["files"][:TOP_FILES_PER_SUBSYSTEM_IN_REPORT])
        lines.append(f"| (root files) | {root['file_count']} | {human_bytes(root['total_bytes'])} | {top} |")

    lines.append("")
    lines.append("## Dependency / reference edges")
    lines.append("")
    lines.append(
        f"{index['stats']['total_edges']} static repo-relative path references were "
        "detected across .py/.sh/.md/.json/.yaml/.yml/.jsonc files (best-effort regex "
        "scan, not a real import graph). Full edge list is in `graph_index_v1.json`; "
        "query by file or subsystem with the query script rather than reading it directly."
    )
    lines.append("")

    lines.append("## Ignored directories")
    lines.append("")
    lines.append(", ".join(f"`{d}`" for d in index["ignored_dirs"]))
    lines.append("")

    lines.append("## Query command")
    lines.append("")
    lines.append("```")
    lines.append("python3 scripts/query_repo_graph_v1.py <subsystem-name|keyword|path-fragment>")
    lines.append("```")
    lines.append("")
    lines.append("## Rebuild command")
    lines.append("")
    lines.append("```")
    lines.append("python3 scripts/build_repo_graph_v1.py")
    lines.append("```")
    lines.append("")
    lines.append(
        "Rebuild whenever the file layout changes materially (new subsystem, large "
        "doc/data additions). See `docs/L0_REPO_GRAPH_MEMORY_v1.md` for the token "
        "budget rule and the broad-read prevention rule."
    )
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
