#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_EXECUTIVE_CONTROL_PLANE_V0_LOCKED_v1.md"
  "data/nf_executive_control_plane_v0_LOCKED.json"
  "data/schemas/executive_founder_charter_v0.json"
  "data/schemas/executive_decision_record_v0.json"
  "data/schemas/executive_commitment_v0.json"
  "data/schemas/executive_work_packet_v0.json"
  "data/schemas/executive_canonical_state_v0.json"
  "data/schemas/executive_decision_result_v0.json"
  "data/schemas/executive_founder_decision_packet_v0.json"
  "data/schemas/executive_drift_finding_v0.json"
  "docs/dispatch/nf-executive-control-plane-v0-all-repos.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_EXECUTIVE_CONTROL_PLANE_V0_LOCK_2026-07-24.md"
  "receipts/doctrine/NF_EXECUTIVE_CONTROL_PLANE_V0_LOCKED.lock.json"
  "scripts/verify_nf_executive_control_plane_v0_wiring_v1.sh"
)
for f in "${need[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING $f"; fail=1; fi
done
grep -q "EXECUTIVE CONTROL PLANE V0" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT section missing"; fail=1; }
grep -q "Executive control plane v0" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT row missing"; fail=1; }
grep -q "executive control plane v0" AGENTS.md || { echo "AGENTS skill missing"; fail=1; }

python3 - <<'PY'
import json
from pathlib import Path
d = json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
need = {"executive_control_plane_v0", "executive_control_plane_v0_machine", "executive_control_plane_v0_dispatch"}
for lane, body in d["lanes"].items():
    roles = {e["role"] for e in body["must_read"]}
    missing = need - roles
    if missing:
        raise SystemExit(f"lane {lane} missing roles {sorted(missing)}")
m = json.loads(Path("data/nf_executive_control_plane_v0_LOCKED.json").read_text())
assert m["llm_on_decision_path"] is False
assert m["cloudflare_in_v0"] is False
assert m["background_loops_in_v0"] is False
print("executive_control_plane_v0 wiring OK")
PY

if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo "PASS verify_nf_executive_control_plane_v0_wiring_v1"
