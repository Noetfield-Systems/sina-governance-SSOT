#!/usr/bin/env python3
"""Sync / upgrade the L0 repo-graph installs across all registered repos.

Single source of truth for the L0 repo-graph system:
  - canonical logic     : scripts/l0-graph-template/*.template.*
  - per-repo config      : data/l0_repo_graph_registry_v1.json
  - installed copies     : each repo's scripts/{build,query,verify}_*

Each installed copy is RENDERED from the template + that repo's registry config.
Never hand-edit an installed copy's shared logic — edit the template, bump
L0_TEMPLATE_VERSION, test in the sandbox, then run this with --apply.

Usage:
  python3 scripts/sync_l0_repo_graph_v1.py --check            # drift report, no writes
  python3 scripts/sync_l0_repo_graph_v1.py --apply            # render + rebuild + verify all repos
  python3 scripts/sync_l0_repo_graph_v1.py --apply --repo X   # just one repo
  python3 scripts/sync_l0_repo_graph_v1.py --list             # registry summary

No commits are made — review the diff and open a PR per repo (see
docs/L0_MAINTENANCE_PLAYBOOK_v1.md). stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SG_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = SG_ROOT / "data" / "l0_repo_graph_registry_v1.json"
TPL_DIR = SG_ROOT / "scripts" / "l0-graph-template"

BUILD_MARK_RE = re.compile(
    r"(# === L0-SUBSYSTEM-CONFIG[^\n]*\n).*?(# === END L0-SUBSYSTEM-CONFIG ===)",
    re.S,
)


def expand(p: str) -> Path:
    return Path(os.path.expanduser(p))


def wrap_quoted(items, per_line=4, indent=4) -> str:
    pad = " " * indent
    out, row = [], []
    for it in items:
        row.append(f'"{it}"')
        if len(row) == per_line:
            out.append(pad + ", ".join(row) + ",")
            row = []
    if row:
        out.append(pad + ", ".join(row) + ",")
    return "\n".join(out) if out else pad + "# (none)"


def render_subsystem_block(entry: dict) -> str:
    if entry["subsystem_mode"] == "auto":
        excl = entry.get("auto_exclude", [])
        return (
            "_EXCLUDED_TOP = {\n"
            + wrap_quoted(excl)
            + "\n}\n"
            "SUBSYSTEM_DIRS = sorted(\n"
            "    p.name for p in ROOT.iterdir()\n"
            "    if p.is_dir() and not p.is_symlink() and p.name not in _EXCLUDED_TOP\n"
            ")"
        )
    return "SUBSYSTEM_DIRS = [\n" + wrap_quoted(entry.get("subsystem_dirs", [])) + "\n]"


def render_files(entry: dict) -> dict:
    build_tpl = (TPL_DIR / "build_repo_graph.template.py").read_text()
    block = render_subsystem_block(entry)
    build = BUILD_MARK_RE.sub(lambda m: m.group(1) + block + "\n" + m.group(2), build_tpl)

    query = (TPL_DIR / "query_repo_graph.template.py").read_text()

    verify = (TPL_DIR / "verify_l0_repo_graph_memory.template.sh").read_text()
    verify = verify.replace("__VERIFY_SUBSYSTEM__", entry["verify_subsystem"])
    verify = verify.replace("__VERIFY_KEYWORD__", entry["verify_keyword"])

    return {
        "scripts/build_repo_graph_v1.py": build,
        "scripts/query_repo_graph_v1.py": query,
        "scripts/verify_l0_repo_graph_memory_v1.sh": verify,
    }


def norm(text: str) -> str:
    return "\n".join(line.rstrip() for line in text.splitlines())


def check_repo(entry: dict) -> dict:
    root = expand(entry["path"])
    rendered = render_files(entry)
    drifted = []
    missing = []
    for rel, content in rendered.items():
        f = root / rel
        if not f.exists():
            missing.append(rel)
        elif norm(f.read_text()) != norm(content):
            drifted.append(rel)
    return {"missing": missing, "drifted": drifted}


def apply_repo(entry: dict) -> dict:
    root = expand(entry["path"])
    rendered = render_files(entry)
    for rel, content in rendered.items():
        f = root / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(content)
        if rel.endswith(".sh") or rel.endswith(".py"):
            f.chmod(0o755)
    build = subprocess.run(
        [sys.executable, "scripts/build_repo_graph_v1.py"],
        cwd=root, capture_output=True, text=True,
    )
    verify = subprocess.run(
        ["bash", "scripts/verify_l0_repo_graph_memory_v1.sh"],
        cwd=root, capture_output=True, text=True,
    )
    vpass = "verify: PASS" in (verify.stdout + verify.stderr)
    return {"build_rc": build.returncode, "verify_pass": vpass,
            "build_tail": (build.stdout or build.stderr).strip().splitlines()[-1:] }


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--repo", help="limit to one repo by name")
    args = ap.parse_args()

    reg = load_registry()
    repos = reg["repos"]
    if args.repo:
        repos = [r for r in repos if r["name"] == args.repo]
        if not repos:
            print(f"no such repo in registry: {args.repo}")
            return 2

    tv = reg["template_version"]

    if args.list or not (args.check or args.apply):
        print(f"L0 template version: {tv}   canonical: {reg['canonical_template_dir']}")
        print(f"sandbox: {reg.get('sandbox','-')}")
        for r in repos:
            n = (len(r.get("subsystem_dirs", [])) if r["subsystem_mode"] == "list"
                 else f"auto/excl{len(r.get('auto_exclude', []))}")
            print(f"  {r['name']:26} {r['subsystem_mode']:5} idx={r['index_strategy']:9} "
                  f"verify={r['verify_subsystem']}/{r['verify_keyword']:13} dirs={n}")
        if not (args.check or args.apply):
            return 0

    rc = 0
    if args.check:
        print(f"\n=== DRIFT CHECK vs template v{tv} ===")
        for r in repos:
            res = check_repo(r)
            if res["missing"] or res["drifted"]:
                rc = 1
                bits = []
                if res["missing"]:
                    bits.append("MISSING " + ",".join(res["missing"]))
                if res["drifted"]:
                    bits.append("DRIFTED " + ",".join(x.split("/")[-1] for x in res["drifted"]))
                print(f"  [DRIFT] {r['name']:26} {' | '.join(bits)}")
            else:
                print(f"  [ok]    {r['name']:26} in sync with template v{tv}")

    if args.apply:
        print(f"\n=== APPLY template v{tv} (render + rebuild + verify) ===")
        for r in repos:
            res = apply_repo(r)
            status = "PASS" if res["verify_pass"] and res["build_rc"] == 0 else "FAIL"
            if status != "PASS":
                rc = 1
            print(f"  [{status}] {r['name']:26} build_rc={res['build_rc']} verify={res['verify_pass']}")
        print("\nApplied. Review each repo's diff and open a PR (index strategy per registry).")
    return rc


if __name__ == "__main__":
    sys.exit(main())
