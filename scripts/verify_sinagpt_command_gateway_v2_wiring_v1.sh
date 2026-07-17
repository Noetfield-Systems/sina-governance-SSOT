#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P1-CANON/SINAGPT_FOUNDER_BRAIN_ARCHITECT_LOCKED_v1.md"
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_COMMAND_GATEWAY_V2_ARCHITECTURE_LOCKED_v1.md"
  "data/sinagpt_founder_brain_architect_v1_LOCKED.json"
  "data/nf_command_gateway_v2_architecture_v1_LOCKED.json"
  "docs/dispatch/nf-command-gateway-v2-motor-control-001.md"
  "docs/dispatch/sinagpt-command-gateway-v2-all-repos.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/SINAGPT_COMMAND_GATEWAY_V2_LOCK_2026-07-17.md"
  "receipts/doctrine/SINAGPT_COMMAND_GATEWAY_V2_v1_LOCKED.lock.json"
  "scripts/verify_sinagpt_command_gateway_v2_wiring_v1.sh"
)
for f in "${need[@]}"; do
  [[ -f "$f" ]] || { echo "MISSING $f"; fail=1; }
done
grep -q "SINAGPT + COMMAND GATEWAY" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT §2h missing"; fail=1; }
grep -q "SinaGPT founder cockpit" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT row missing"; fail=1; }
grep -q "SinaGPT + Command Gateway v2" AGENTS.md || { echo "AGENTS 0d missing"; fail=1; }
python3 -c '
import json
from pathlib import Path
d=json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
assert d["version"]=="1.5.0", d["version"]
need=["sinagpt_founder_brain","command_gateway_v2_architecture"]
for lane, body in d["lanes"].items():
    roles={e["role"] for e in body["must_read"]}
    for r in need:
        if r not in roles:
            raise SystemExit(f"lane {lane} missing {r}")
print("lanes ok")
'
if [[ $fail -eq 0 ]]; then echo "SINAGPT GATEWAY V2 WIRING: PASS"; else echo "FAIL"; exit 1; fi
