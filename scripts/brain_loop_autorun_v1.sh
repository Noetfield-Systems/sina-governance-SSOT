#!/usr/bin/env bash
# Brain loop autorun — 6h cycle; autonomous promote when founder flag set.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
export SOURCEA_ROOT
AUTONOMOUS_FLAG="${HOME}/.sina/brain-autonomous-deploy-v1.flag"
HOLD_FLAG="${HOME}/.sina/enforcement/brain-autonomous-hold-v1.flag"
SHIP_FLAG="${HOME}/.sina/asf-ship-window-v1.flag"
RECEIPT_DIR="$ROOT/receipts"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
AUTORUN_RECEIPT="$RECEIPT_DIR/brain-loop-autorun-${TS}.json"

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

AUTONOMOUS=0
SHIP_WINDOW=0
HOLD_ACTIVE=0
if [[ -f "$AUTONOMOUS_FLAG" ]]; then
  AUTONOMOUS=1
fi
if [[ -f "$HOLD_FLAG" ]]; then
  HOLD_ACTIVE=1
fi
if [[ -f "$SHIP_FLAG" || "${CI:-}" == "true" || "${GITHUB_ACTIONS:-}" == "true" ]]; then
  SHIP_WINDOW=1
fi

echo "=== brain_loop_autorun_v1 start autonomous=${AUTONOMOUS} hold=${HOLD_ACTIVE} ship_window=${SHIP_WINDOW} ==="

if [[ "$AUTONOMOUS" == "1" && "$HOLD_ACTIVE" == "1" ]]; then
  echo "brain_loop_autorun_v1: HOLD — autonomous deploy paused"
  python3 - <<PY
import json
from pathlib import Path
payload = {
    "receipt_type": "BRAIN_LOOP_AUTORUN",
    "recorded_at": "$TS",
    "autonomous": True,
    "hold_active": True,
    "gate_note": "autonomous_hold_active",
}
Path("$AUTORUN_RECEIPT").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
PY
  exit 2
fi

SELF_HEAL_RC=0
PARALLEL_RC=0
MATRIX_RC=0
GATE_RC=0
GATE_NOTE="skipped"

export BRAIN_SELF_HEAL_TRIGGER=1
set +e
bash "$ROOT/scripts/brain_loop_self_heal_v1.sh" >/dev/null
SELF_HEAL_RC=$?
bash "$ROOT/scripts/run_parallel_brain_candidates_v1.sh" --all >/dev/null
PARALLEL_RC=$?
set -e

RUN_MATRIX=0
if [[ "$AUTONOMOUS" == "1" || "$SHIP_WINDOW" == "1" ]]; then
  RUN_MATRIX=1
fi

if [[ "$RUN_MATRIX" == "1" ]]; then
  MATRIX_LOG="$(mktemp)"
  set +e
  bash "$ROOT/scripts/validate_brain_domain_e2e_matrix_v1.sh" >"$MATRIX_LOG" 2>&1
  MATRIX_RC=$?
  set -e
  cat "$MATRIX_LOG"
  LAUNCHD_TCC_BLOCK=0
  if [[ "$MATRIX_RC" -ne 0 ]] && grep -q "Operation not permitted" "$MATRIX_LOG"; then
    LAUNCHD_TCC_BLOCK=1
  fi
  rm -f "$MATRIX_LOG"
else
  LAUNCHD_TCC_BLOCK=0
  echo "SKIP: e2e matrix (observe-only; no ship window / autonomous)"
fi

MUTATION_TRIALS=$(python3 - <<PY
import sys
from pathlib import Path
sys.path.insert(0, "$ROOT")
from scripts.brain_autonomous_controls_v1 import mutation_trials_enabled
print(1 if mutation_trials_enabled(Path("$SOURCEA_ROOT")) else 0)
PY
)

if [[ "$SELF_HEAL_RC" -ne 0 || "$PARALLEL_RC" -ne 0 || "$MATRIX_RC" -ne 0 ]]; then
  if [[ "$AUTONOMOUS" == "1" && "${LAUNCHD_TCC_BLOCK:-0}" == "1" ]]; then
    GATE_NOTE="launchd_tcc_block_no_hold"
    echo "NOTE: matrix blocked by macOS TCC — not setting autonomous hold"
  elif [[ "$AUTONOMOUS" == "1" ]]; then
    python3 - <<PY
from scripts.brain_autonomous_controls_v1 import set_autonomous_hold
set_autonomous_hold(reason="autorun pre-promote fail self_heal=$SELF_HEAL_RC parallel=$PARALLEL_RC matrix=$MATRIX_RC")
PY
    GATE_NOTE="autonomous_hold_set_pre_promote"
  fi
elif [[ "$AUTONOMOUS" == "1" && "$MUTATION_TRIALS" == "0" ]]; then
  set +e
  bash "$ROOT/scripts/promote_brain_worker_v1.sh" --autonomous-deploy \
    --deploy-receipt "$RECEIPT_DIR/brain-autonomous-promote-${TS}.json"
  GATE_RC=$?
  set -e
  if [[ "$GATE_RC" -eq 0 ]]; then
    GATE_NOTE="autonomous_promote_executed"
    python3 - <<'PY'
from scripts.brain_autonomous_controls_v1 import clear_autonomous_hold
clear_autonomous_hold()
PY
  else
    GATE_NOTE="autonomous_promote_failed"
  fi
elif [[ "$SHIP_WINDOW" == "1" && "$SELF_HEAL_RC" -eq 0 && "$PARALLEL_RC" -eq 0 && "$MATRIX_RC" -eq 0 ]]; then
  GATE_NOTE="semi_auto_available_invoke_promote_brain_worker_v1"
  echo "NOTE: invoke bash scripts/promote_brain_worker_v1.sh for confirm-each-time promote"
fi

python3 - <<PY
import json
from pathlib import Path
payload = {
    "receipt_type": "BRAIN_LOOP_AUTORUN",
    "recorded_at": "$TS",
    "autonomous": bool($AUTONOMOUS),
    "ship_window": bool($SHIP_WINDOW),
    "hold_active": bool($HOLD_ACTIVE),
    "self_heal_rc": $SELF_HEAL_RC,
    "parallel_rc": $PARALLEL_RC,
    "matrix_rc": $MATRIX_RC,
    "gate_rc": $GATE_RC,
    "gate_note": "$GATE_NOTE",
    "mutation_trials": bool($MUTATION_TRIALS),
}
out = Path("$AUTORUN_RECEIPT")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"autorun_receipt: {out}")
PY

if [[ "$AUTONOMOUS" != "1" && "$SHIP_WINDOW" != "1" ]]; then
  echo "brain_loop_autorun_v1: OBSERVE_ONLY"
  exit 0
fi

if [[ "$SELF_HEAL_RC" -ne 0 || "$PARALLEL_RC" -ne 0 || "$MATRIX_RC" -ne 0 || "$GATE_RC" -ne 0 ]]; then
  echo "brain_loop_autorun_v1: FAIL"
  exit 1
fi

echo "brain_loop_autorun_v1: ALL PASS"
exit 0
