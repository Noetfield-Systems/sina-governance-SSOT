#!/usr/bin/env bash
# E2E verify CHESS_PATTERN_REASONING_MACHINE_v2.0 full package install.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LIB="$ROOT/SG-Canonical-Library/noetfield-library"
cd "$ROOT"

fail() { echo "CHESS INSTALL VERIFY: FAIL — $*" >&2; exit 1; }
ok() { echo "CHESS INSTALL VERIFY: $*"; }

MANIFEST="$ROOT/data/chess_pattern_reasoning_machine_v2_manifest.json"
[[ -f "$MANIFEST" ]] || fail "missing manifest"

python3 - <<'PY' || fail "manifest file paths missing on disk"
import json
from pathlib import Path
root = Path(".")
lib = root / "SG-Canonical-Library/noetfield-library"
manifest = json.loads((root / "data/chess_pattern_reasoning_machine_v2_manifest.json").read_text())
for rel in manifest["files"]:
    if rel.startswith("INSTALL/") or rel == "README.md":
        candidates = [lib / "CHESS-v2" / rel, lib / rel]
    elif rel.startswith("TOOLS/"):
        candidates = [root / "scripts/chess_pass_cli_v1.py"]
    else:
        candidates = [lib / rel]
    if not any(c.is_file() for c in candidates):
        raise SystemExit(f"missing: {rel}")
print("manifest files: ok")
PY

[[ -x "$ROOT/scripts/chess_pass_cli_v1.py" ]] || fail "chess_pass_cli not executable"

# Wiring grep proofs (WIRING_CHECKLIST)
for pat in \
  "CHESS_PATTERN_REASONING_MACHINE_v2.0" \
  "Forecast → Patch → Proceed → Verify" \
  "PROCEED_WITH_PATCH" \
  "ASK_IF_IRREVERSIBLE" \
  "Forbidden action label" \
; do
  rg -q "$pat" "$LIB/P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md" \
    || fail "doctrine missing pattern: $pat"
done

rg -q "Improve clarity without removing working capability" \
  "$LIB/P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md" \
  || fail "anti-downgrade translation missing"

rg -q "fail-closed" "$LIB/P0-DOCTRINE" "$LIB/SKILLS" "$LIB/PLAYBOOKS" 2>/dev/null && \
  fail "fail-closed language found in CHESS package" || true

# CLI smoke on risky prompt
OUT="$(echo '{"raw_move":"Make the partner page clean and minimal","protected_assets":["Sign in","Partner Access Platform"]}' | python3 scripts/chess_pass_cli_v1.py)"
echo "$OUT" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['action'] in ('PROCEED','PROCEED_WITH_PATCH','ASK_IF_IRREVERSIBLE'); assert d['action']=='PROCEED_WITH_PATCH'" \
  || fail "cli did not return PROCEED_WITH_PATCH for risky prompt"

# Sample example validates required keys
python3 - <<'PY' || fail "sample_chess_pass.json schema keys"
import json
from pathlib import Path
schema = json.loads(Path("SG-Canonical-Library/noetfield-library/SCHEMAS/chess_pass.schema.json").read_text())
sample = json.loads(Path("SG-Canonical-Library/noetfield-library/EXAMPLES/sample_chess_pass.json").read_text())
for key in schema["required"]:
    assert key in sample, key
assert sample["action"] in schema["properties"]["action"]["enum"]
print("sample schema keys: ok")
PY

# Registry wiring
python3 - <<'PY' || fail "agent_read_surfaces missing CHESS skills"
import json
from pathlib import Path
d = json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
paths = {e["path"] for lane in d["lanes"].values() for e in lane["must_read"]}
need = "SG-Canonical-Library/noetfield-library/P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md"
assert need in paths
assert any("SKILL_01" in p for p in paths), paths
print("agent_read_surfaces: ok")
PY

python3 -m unittest tests.test_chess_pass_cli_v1 -q 2>/dev/null || fail "unit tests"

ok "PASS — full CHESS v2.0 package e2e"
