#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P8-MACHINE-LOOPS/ARCHITECTURE_FINALIZATION_GATE_LOCKED_v1.md"
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCKED_v1.md"
  "data/architecture_finalization_gate_v1_LOCKED.json"
  "data/nf_unified_motor_architecture_v1_LOCKED.json"
  "docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md"
  "docs/dispatch/nf-unified-motor-architecture-all-repos.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCK_2026-07-17.md"
  "receipts/doctrine/NF_UNIFIED_MOTOR_ARCHITECTURE_v1_LOCKED.lock.json"
  "scripts/verify_nf_unified_motor_wiring_v1.sh"
)
for f in "${need[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING $f"; fail=1; fi
done
grep -q "ARCHITECTURE FINALIZATION GATE" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT §2f missing"; fail=1; }
grep -q "UNIFIED MOTOR CORE" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT §2g missing"; fail=1; }
grep -q "Architecture Finalization Gate" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT gate row missing"; fail=1; }
grep -q "Unified Motor Core architecture" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT motor row missing"; fail=1; }
grep -q "Architecture Finalization Gate + Unified Motor" AGENTS.md || { echo "AGENTS 0c missing"; fail=1; }
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
assert d["version"]=="1.5.0", d["version"]
need=["architecture_finalization_gate","unified_motor_architecture"]
for lane, body in d["lanes"].items():
    roles={e["role"] for e in body["must_read"]}
    for r in need:
        if r not in roles:
            raise SystemExit(f"lane {lane} missing role {r}")
print("lanes ok")
PY
if [[ $fail -eq 0 ]]; then
  echo "NF UNIFIED MOTOR WIRING: PASS"
else
  echo "NF UNIFIED MOTOR WIRING: FAIL"
  exit 1
fi
