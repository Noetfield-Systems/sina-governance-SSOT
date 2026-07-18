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
  "docs/dispatch/wave-0-nf-unified-motor-merge-packet.md"
  "docs/dispatch/nf-unified-motor-v1-foundation-commission.md"
  "docs/dispatch/sg-to-noos-wave0-persistence-answer.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCK_2026-07-17.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_UNIFIED_MOTOR_SCALING_POSTURE_2026-07-18.md"
  "receipts/doctrine/NF_UNIFIED_MOTOR_SCALING_POSTURE_v1.lock.json"
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
ver=tuple(int(x) for x in str(d["version"]).split("."))
assert ver >= (1, 4, 0), d["version"]
need=["architecture_finalization_gate","unified_motor_architecture"]
for lane, body in d["lanes"].items():
    roles={e["role"] for e in body["must_read"]}
    for r in need:
        if r not in roles:
            raise SystemExit(f"lane {lane} missing role {r}")
print("lanes ok")
j=json.loads(Path("data/nf_unified_motor_architecture_v1_LOCKED.json").read_text())
assert j.get("version","").startswith("v1.1"), j.get("version")
assert "scaling_posture" in j, "missing scaling_posture"
assert j["scaling_posture"]["runway"]=="cloudflare_agents_plus_workflows"
assert "Temporal" in j["scaling_posture"]["reject_substrates"]
print("scaling_posture ok")
PY
grep -q "AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD" SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCKED_v1.md || { echo "HOLD floor missing from architecture MD"; fail=1; }
grep -q "NF-OPEN-MODEL-RUNTIME-ADAPTER-V1" docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md || { echo "W5 section missing"; fail=1; }
grep -qi "rolling error-rate breaker" docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md || { echo "W5 acceptance requirements missing"; fail=1; }
grep -q "nf-unified-motor-foundation-v1" docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md || { echo "liveness loop_id missing"; fail=1; }

if [[ $fail -eq 0 ]]; then
  echo "NF UNIFIED MOTOR WIRING: PASS"
else
  echo "NF UNIFIED MOTOR WIRING: FAIL"
  exit 1
fi
