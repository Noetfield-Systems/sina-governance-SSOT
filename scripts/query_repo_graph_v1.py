#!/usr/bin/env python3
"""L0 repo graph query — compact lookups against graph-out/graph_index_v1.json.

Use this instead of reading files directly when you only need to know
*where* something lives or *what references what*.

Usage:
    python3 scripts/query_repo_graph_v1.py <subsystem-name>          # subsystem file list
    python3 scripts/query_repo_graph_v1.py <keyword-or-path-fragment> # substring search + edges
    python3 scripts/query_repo_graph_v1.py --stats                    # index-wide stats only
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "graph-out" / "graph_index_v1.json"
MAX_FILES_SHOWN = 40
MAX_EDGES_SHOWN = 30


def load_index() -> dict:
    if not INDEX_PATH.exists():
        print(
            f"No graph index at {INDEX_PATH.relative_to(ROOT)}. "
            "Run: python3 scripts/build_repo_graph_v1.py",
            file=sys.stderr,
        )
        sys.exit(2)
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def print_stats(index: dict) -> None:
    print(json.dumps({"generated_at": index["generated_at"], **index["stats"]}, indent=2))


def query_subsystem(index: dict, name: str) -> bool:
    subsystems = index["subsystems"]
    if name not in subsystems:
        return False
    info = subsystems[name]
    print(f"# subsystem: {name}  (files={info['file_count']}, bytes={info['total_bytes']})")
    for f in info["files"][:MAX_FILES_SHOWN]:
        print(f"  {f['path']}  ({f['bytes']}B, mtime={f['mtime']})")
    if info["file_count"] > MAX_FILES_SHOWN:
        print(f"  ... {info['file_count'] - MAX_FILES_SHOWN} more (see graph_index_v1.json)")
    edges = [e for e in index["edges"] if e["from"].startswith(name + "/") or e["to"].startswith(name + "/")]
    if edges:
        print(f"# edges touching {name}/ ({len(edges)})")
        for e in edges[:MAX_EDGES_SHOWN]:
            print(f"  {e['from']} -> {e['to']}")
        if len(edges) > MAX_EDGES_SHOWN:
            print(f"  ... {len(edges) - MAX_EDGES_SHOWN} more")
    return True


def query_keyword(index: dict, term: str) -> None:
    term_l = term.lower()
    matches = []
    for subsystem in index["subsystems"].values():
        for f in subsystem["files"]:
            if term_l in f["path"].lower():
                matches.append(f)
    matches.sort(key=lambda f: -f["bytes"])

    print(f"# files matching '{term}' ({len(matches)})")
    for f in matches[:MAX_FILES_SHOWN]:
        print(f"  {f['path']}  ({f['bytes']}B, mtime={f['mtime']})")
    if len(matches) > MAX_FILES_SHOWN:
        print(f"  ... {len(matches) - MAX_FILES_SHOWN} more")

    edges = [
        e for e in index["edges"]
        if term_l in e["from"].lower() or term_l in e["to"].lower()
    ]
    if edges:
        print(f"# edges matching '{term}' ({len(edges)})")
        for e in edges[:MAX_EDGES_SHOWN]:
            print(f"  {e['from']} -> {e['to']}")
        if len(edges) > MAX_EDGES_SHOWN:
            print(f"  ... {len(edges) - MAX_EDGES_SHOWN} more")

    if not matches and not edges:
        print("  (no matches — try a shorter fragment, or a subsystem name from GRAPH_REPORT.md)")


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0

    index = load_index()

    if argv[0] == "--stats":
        print_stats(index)
        return 0

    term = argv[0]
    if query_subsystem(index, term):
        return 0
    query_keyword(index, term)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
