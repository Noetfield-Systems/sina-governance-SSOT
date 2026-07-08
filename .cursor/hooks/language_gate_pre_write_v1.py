#!/usr/bin/env python3
"""Cursor preToolUse hook — deny Write/StrReplace when language gate FAILs."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile
from pathlib import Path

def main() -> int:
    root = Path(sys.argv[1])
    payload = json.load(sys.stdin)
    args = payload.get("tool_input") or payload.get("arguments") or {}
    path = args.get("path") or args.get("file_path") or args.get("target_notebook") or ""
    content = args.get("contents") or args.get("new_string") or args.get("content") or ""
    if not path or not content:
        print(json.dumps({"permission": "allow"}))
        return 0
    suffix = Path(path).suffix.lower()
    if suffix not in {".md", ".mdc", ".txt", ".json"}:
        print(json.dumps({"permission": "allow"}))
        return 0
    with tempfile.NamedTemporaryFile("w", suffix=suffix, delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        proc = subprocess.run(
            [sys.executable, str(root / "language_gate/language_gate_pipeline_v1.py"), tmp_path, "--surface", "auto"],
            cwd=str(root), capture_output=True, text=True,
        )
    finally:
        os.unlink(tmp_path)
    if proc.returncode != 0:
        msg = (proc.stdout or proc.stderr or "language gate FAIL").strip()[-800:]
        print(json.dumps({
            "permission": "deny",
            "user_message": "Language gate blocked this edit. Fix dictionary/terminology violations before saving.",
            "agent_message": f"Language gate FAIL on proposed content for {path}. Details:\n{msg}",
        }))
        return 0
    print(json.dumps({"permission": "allow"}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
