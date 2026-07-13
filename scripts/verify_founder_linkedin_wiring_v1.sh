#!/usr/bin/env bash
# Verify FOUNDER_LINKEDIN_PROFILE_LOCKED wiring across SG spine.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
LIB="SG-Canonical-Library/noetfield-library"
LOCKED="$LIB/P1-CANON/FOUNDER_LINKEDIN_PROFILE_LOCKED_v1.md"

fail() { echo "FOUNDER LINKEDIN WIRING: FAIL — $*" >&2; exit 1; }

[[ -f "$LOCKED" ]] || fail "missing locked profile"
[[ -f data/founder_linkedin_profile_v1_LOCKED.json ]] || fail "missing machine JSON"
[[ -f docs/dispatch/founder-linkedin-voice-all-repos.md ]] || fail "missing dispatch"

rg -q "Investor Workflow" "$LOCKED" || fail "Investor Workflow missing"
rg -q "Audit us before you invest in us" "$LOCKED" || fail "signature CTA missing"
rg -q "Custom AI Motors" "$LOCKED" || fail "headline anchor missing"

python3 - <<'PY' || fail "agent_read_surfaces"
import json
d = json.load(open("data/agent_read_surfaces_v1.json"))
paths = {e["path"] for lane in d["lanes"].values() for e in lane["must_read"]}
assert "SG-Canonical-Library/noetfield-library/P1-CANON/FOUNDER_LINKEDIN_PROFILE_LOCKED_v1.md" in paths
print("lanes ok")
PY

rg -q "2e\. FOUNDER LINKEDIN" "$LIB/ARCHITECT_START_HERE.md" || fail "ARCHITECT §2e missing"

echo "FOUNDER LINKEDIN WIRING: PASS"
