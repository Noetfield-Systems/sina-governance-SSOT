#!/usr/bin/env python3
"""Verify PR conflict resolver skill lock — structural gate for SG + NOOS."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "data/pr_conflict_skill_lock_v1.json"


def sha_prefix(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def expand_home(path: str) -> Path:
    return Path(os.path.expanduser(path))


def verify(*, mac_desktop: bool = False) -> dict[str, Any]:
    issues: list[str] = []
    if not LOCK.is_file():
        return {"ok": False, "issues": ["missing_lock_manifest"], "checks": {}}

    lock = json.loads(LOCK.read_text(encoding="utf-8"))
    skill = ROOT / str(lock.get("canonical_skill") or "")
    lock_doc = ROOT / str(lock.get("lock_doc") or "")
    evals = ROOT / str(lock.get("evals") or "")
    verifier = ROOT / str(lock.get("verifier") or "")

    checks: dict[str, Any] = {}

    for label, path in [
        ("lock_manifest", LOCK),
        ("canonical_skill", skill),
        ("lock_doc", lock_doc),
        ("evals", evals),
        ("verifier", verifier),
    ]:
        checks[f"{label}_exists"] = path.is_file()
        if not path.is_file():
            issues.append(f"missing:{path.relative_to(ROOT)}")

    if skill.is_file():
        got = sha_prefix(skill)
        want = str(lock.get("skill_sha256_prefix") or "")
        checks["skill_hash_ok"] = got == want
        checks["skill_sha256_prefix"] = got
        if want and got != want:
            issues.append(f"skill_hash_drift:{got}!={want}")

    if evals.is_file():
        got = sha_prefix(evals)
        want = str(lock.get("evals_sha256_prefix") or "")
        checks["evals_hash_ok"] = got == want
        checks["evals_sha256_prefix"] = got
        if want and got != want:
            issues.append(f"evals_hash_drift:{got}!={want}")

    app_rel = (lock.get("desktop_app") or {}).get("ssot_path", "")
    app_ssot = ROOT / app_rel if app_rel else None
    if app_ssot:
        launcher = app_ssot / str((lock.get("desktop_app") or {}).get("launcher") or "")
        report = app_ssot / str((lock.get("desktop_app") or {}).get("report_html") or "")
        checks["desktop_app_ssot"] = app_ssot.is_dir()
        checks["desktop_launcher"] = launcher.is_file()
        checks["desktop_report_html"] = report.is_file()
        if launcher.is_file():
            mode = launcher.stat().st_mode
            checks["desktop_launcher_executable"] = bool(mode & stat.S_IXUSR)
            if not checks["desktop_launcher_executable"]:
                issues.append("desktop_launcher_not_executable")
        for name, ok in [
            ("desktop_app_ssot", checks["desktop_app_ssot"]),
            ("desktop_launcher", checks["desktop_launcher"]),
            ("desktop_report_html", checks["desktop_report_html"]),
        ]:
            if not ok:
                issues.append(f"missing:{name}")

    if mac_desktop:
        shortcut = expand_home(str((lock.get("desktop_app") or {}).get("desktop_shortcut") or ""))
        checks["desktop_shortcut"] = shortcut.is_dir()
        if not checks["desktop_shortcut"]:
            issues.append("missing:desktop_shortcut")

    ok = not issues
    return {
        "schema": "pr-conflict-skill-verify-v1",
        "ok": ok,
        "issues": issues,
        "checks": checks,
        "lock_status": lock.get("status"),
        "report_line": "pr_conflict_skill_lock · ALL PASS" if ok else f"pr_conflict_skill_lock · FAIL ({len(issues)})",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--mac-desktop", action="store_true", help="Also require ~/Desktop shortcut app")
    args = ap.parse_args()

    row = verify(mac_desktop=args.mac_desktop)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
        for issue in row.get("issues") or []:
            print(f"  {issue}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
