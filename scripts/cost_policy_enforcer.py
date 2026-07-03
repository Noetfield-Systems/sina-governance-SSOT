#!/usr/bin/env python3
"""Cost policy enforcer.
Scans the repo for banned model patterns defined in .noetfield/cost_policy.yml and exits with non-zero if any matches.
"""
from __future__ import annotations

import sys
import yaml
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / ".noetfield" / "cost_policy.yml"

if not POLICY.exists():
    print("No cost policy found; skipping enforcement")
    raise SystemExit(0)

with open(POLICY) as fh:
    cfg = yaml.safe_load(fh)

banned = cfg.get("banned_model_patterns", [])
# compile regexes
regexes = [re.compile(p, re.IGNORECASE) for p in banned]

matches = []
# Define which paths/extensions to enforce as code (fatal) vs docs (non-fatal)
CODE_PATH_PREFIXES = ["scripts/", ".github/workflows/", "cloud/", "workers/", "src/", "services/"]
CODE_EXTENSIONS = {".py", ".js", ".ts", ".yaml", ".yml", ".sh", ".json", ".dockerfile", ""}

for p in ROOT.rglob("**/*"):
    # skip policy file and hidden policy dir
    if str(p).startswith(str(POLICY.parent)):
        continue
    # skip binary files and directories
    try:
        if p.is_dir() or p.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip"}:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        continue
    for rx in regexes:
        if rx.search(text):
            rel = str(p.relative_to(ROOT))
            is_code = any(rel.startswith(prefix) for prefix in CODE_PATH_PREFIXES) or p.suffix in CODE_EXTENSIONS
            matches.append((rel, rx.pattern, is_code))

code_violations = [m for m in matches if m[2]]
doc_mentions = [m for m in matches if not m[2]]

if code_violations:
    print("COST POLICY VIOLATIONS IN CODE (FAIL):")
    for f, pat, _ in code_violations:
        print(f" - {f}: matched pattern {pat}")
    print(cfg.get("policy_enforcement", {}).get("message"))
    raise SystemExit(2)

if doc_mentions:
    print("COST POLICY MENTIONS (docs/warnings):")
    for f, pat, _ in doc_mentions:
        print(f" - {f}: matched pattern {pat}")
    print("Mentions found in docs; not blocking in CI. Consider editing docs or keeping as note.")
    raise SystemExit(0)

print("Cost policy check: no violations found")
raise SystemExit(0)
