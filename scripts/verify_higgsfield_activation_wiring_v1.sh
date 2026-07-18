#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_HIGGSFIELD_MEDIA_ADAPTER_AND_RESULT_MOTOR_LOCKED_v1.md"
  "docs/NF_ACTIVATION_CYCLE_V1_LOCKED.md"
  "data/nf_higgsfield_media_adapter_result_motor_v1_LOCKED.json"
  "data/nf_activation_cycle_v1_LOCKED.json"
  "docs/dispatch/higgsfield-activation-cycle-all-repos.md"
  "docs/dispatch/nf-circuit-a-deterministic-motor-proof-001.md"
  "docs/dispatch/nf-circuit-b-higgsfield-campaign-proof-001.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/HIGGSFIELD_ACTIVATION_LOCK_2026-07-18.md"
  "receipts/doctrine/NF_HIGGSFIELD_ACTIVATION_v1_LOCKED.lock.json"
  "scripts/verify_higgsfield_activation_wiring_v1.sh"
)
for f in "${need[@]}"; do
  [[ -f "$f" ]] || { echo "MISSING $f"; fail=1; }
done
grep -q "ACTIVATION CYCLE + HIGGSFIELD" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT §2i missing"; fail=1; }
grep -q "Higgsfield media adapter" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT missing"; fail=1; }
grep -q "Activation cycle + Higgsfield" AGENTS.md || { echo "AGENTS 0e missing"; fail=1; }
python3 -c '
import json
from pathlib import Path
d=json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
assert d["version"]=="1.6.0", d["version"]
need=["activation_cycle","higgsfield_media_adapter"]
for lane, body in d["lanes"].items():
    roles={e["role"] for e in body["must_read"]}
    for r in need:
        if r not in roles:
            raise SystemExit(f"lane {lane} missing {r}")
print("lanes ok")
'
if [[ $fail -eq 0 ]]; then echo "HIGGSFIELD ACTIVATION WIRING: PASS"; else echo FAIL; exit 1; fi
