#!/usr/bin/env bash
# Bounded Brain loop autorun — self-heal tick; optional semi-auto gate when ship-window flag set.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
export SOURCEA_ROOT
SHIP_FLAG="${HOME}/.sina/asf-ship-window-v1.flag"
RECEIPT_DIR="$ROOT/receipts"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
AUTORUN_RECEIPT="$RECEIPT_DIR/brain-loop-autorun-${TS}.json"

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

SHIP_WINDOW=0
if [[ -f "$SHIP_FLAG" || "${CI:-}" == "true" || "${GITHUB_ACTIONS:-}" == "true" ]]; then
  SHIP_WINDOW=1
fi

echo "=== brain_loop_autorun_v1 start ship_window=${SHIP_WINDOW} ==="

SELF_HEAL_JSON="$(mktemp)"
export BRAIN_SELF_HEAL_TRIGGER=1
set +e
bash "$ROOT/scripts/brain_loop_self_heal_v1.sh" > "$SELF_HEAL_JSON"
SELF_HEAL_RC=$?
set -e

PARALLEL_JSON="$(mktemp)"
set +e
bash "$ROOT/scripts/run_parallel_brain_candidates_v1.sh" --all > "$PARALLEL_JSON"
PARALLEL_RC=$?
set -e

MATRIX_RC=0
if [[ "$SHIP_WINDOW" == "1" ]]; then
  set +e
  bash "$ROOT/scripts/validate_brain_domain_e2e_matrix_v1.sh"
  MATRIX_RC=$?
  set -e
else
  echo "SKIP: e2e matrix (no ship window / CI context)"
fi

GATE_RC=0
GATE_NOTE="skipped_no_ship_window"
if [[ "$SHIP_WINDOW" == "1" && "$SELF_HEAL_RC" -eq 0 && "$PARALLEL_RC" -eq 0 ]]; then
  if [[ "${BRAIN_SANDBOX_SEMI_AUTO:-}" == "brain_worker" ]]; then
    GATE_NOTE="semi_auto_available_not_auto_invoked"
    echo "NOTE: semi-auto gate available; invoke promotion_gate.py manually or via ship window script"
  else
    GATE_NOTE="heal_only_no_semi_auto_env"
  fi
fi

python3 - <<PY
import json
from pathlib import Path
out = Path("$AUTORUN_RECEIPT")
payload = {
    "receipt_type": "BRAIN_LOOP_AUTORUN",
    "recorded_at": "$TS",
    "ship_window": bool($SHIP_WINDOW),
    "self_heal_rc": $SELF_HEAL_RC,
    "parallel_rc": $PARALLEL_RC,
    "matrix_rc": $MATRIX_RC,
    "gate_note": "$GATE_NOTE",
    "mutation_trials": False,
}
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"autorun_receipt: {out}")
PY

if [[ "$SHIP_WINDOW" != "1" ]]; then
  echo "brain_loop_autorun_v1: OBSERVE_ONLY (no ship window)"
  exit 0
fi

if [[ "$SELF_HEAL_RC" -ne 0 || "$PARALLEL_RC" -ne 0 || "$MATRIX_RC" -ne 0 ]]; then
  echo "brain_loop_autorun_v1: FAIL"
  exit 1
fi

echo "brain_loop_autorun_v1: ALL PASS"
exit 0
