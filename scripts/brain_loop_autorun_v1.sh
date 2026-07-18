#!/usr/bin/env bash
# P0 containment: observe-only receipt; never authorize production mutation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RECEIPT_DIR="${BRAIN_RECEIPT_DIR:-$ROOT/receipts}"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
AUTORUN_RECEIPT="$RECEIPT_DIR/brain-loop-autorun-${TS}.json"
mkdir -p "$RECEIPT_DIR"

python3 - <<PY_RECEIPT
import json
from pathlib import Path
reality = json.loads(Path("$ROOT/data/runtime_reality_v1.json").read_text())
payload = {
    "receipt_type": "BRAIN_LOOP_CONTAINMENT_OBSERVATION",
    "recorded_at": "$TS",
    "status": "OBSERVE_ONLY" if "${SG_OBSERVE_ONLY:-0}" == "1" else "BLOCKED_SG_NOT_COMMISSIONED",
    "autonomous": False,
    "production_mutation_authorized": False,
    "deploy_executed": False,
    "hold": reality["authority"]["autonomous_production_mutations"],
    "sg_runtime": reality["sg"]["runtime_status"],
    "incident_id": reality["incident_id"],
    "token_presence_ignored": True,
    "local_flags_cannot_authorize": True,
}
Path("$AUTORUN_RECEIPT").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
print(json.dumps(payload, indent=2, sort_keys=True))
print("autorun_receipt: $AUTORUN_RECEIPT")
PY_RECEIPT

if [[ "${SG_OBSERVE_ONLY:-0}" == "1" ]]; then
  echo "brain_loop_autorun_v1: OBSERVE_ONLY"
  exit 0
fi

echo "BLOCKED_SG_NOT_COMMISSIONED"
exit 78
