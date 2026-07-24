#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_EXECUTIVE_MESH_V1_LOCKED_v1.md"
  "data/nf_executive_mesh_v1_LOCKED.json"
  "docs/dispatch/nf-executive-mesh-v1-all-repos.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_EXECUTIVE_MESH_V1_LOCK_2026-07-24.md"
  "receipts/doctrine/NF_EXECUTIVE_MESH_V1_LOCKED.lock.json"
  "scripts/verify_nf_executive_mesh_v1_wiring_v1.sh"
)
for f in "${need[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING $f"; fail=1; fi
done
grep -q "EXECUTIVE MESH V1" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT section missing"; fail=1; }
grep -q "Executive mesh v1" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT row missing"; fail=1; }
grep -q "executive mesh v1" AGENTS.md || { echo "AGENTS skill missing"; fail=1; }
python3 - <<'PY'
import json
from pathlib import Path
d = json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
need = {"executive_mesh_v1", "executive_mesh_v1_machine", "executive_mesh_v1_dispatch"}
for lane, body in d["lanes"].items():
    roles = {e["role"] for e in body["must_read"]}
    missing = need - roles
    if missing:
        raise SystemExit(f"lane {lane} missing roles {sorted(missing)}")
m = json.loads(Path("data/nf_executive_mesh_v1_LOCKED.json").read_text())
assert m["llm_authority"] is False
assert m["second_railway_executor"] is False
print("executive_mesh_v1 wiring OK")
PY
if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo "PASS verify_nf_executive_mesh_v1_wiring_v1"
