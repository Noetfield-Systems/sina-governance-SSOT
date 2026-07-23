#!/usr/bin/env python3
"""Cursor preToolUse hook — deny Write/StrReplace only when language gate DECISION is FAIL.

WARN (undefined terms) must not block auto-execution. FAIL (banned register / overclaim) still denies.
"""
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
            [
                sys.executable,
                str(root / "language_gate/language_gate_pipeline_v1.py"),
                tmp_path,
                "--surface",
                "auto",
                "--soft-undefined",
            ],
            cwd=str(root),
            capture_output=True,
            text=True,
        )
    finally:
        os.unlink(tmp_path)
    out = (proc.stdout or "") + "\n" + (proc.stderr or "")
    decision = "PASS"
    for line in out.splitlines():
        if line.startswith("DECISION:"):
            decision = line.split(":", 1)[1].strip()
            break
    # Deny only hard FAIL. WARN/PASS allow writes so agents are not stalled on undefined terms.
    if decision == "FAIL" or (proc.returncode != 0 and decision not in {"PASS", "WARN"}):
        msg = out.strip()[-800:] or "language gate FAIL"
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
