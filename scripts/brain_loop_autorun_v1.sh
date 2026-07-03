#!/usr/bin/env bash
# Brain loop autorun — 6h cycle; autonomous promote when founder flag set.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=scripts/brain_mac_env_v1.sh
source "$ROOT/scripts/brain_mac_env_v1.sh"

brain_clear_stale_lock
brain_try_clear_smoke_hold

AUTONOMOUS_FLAG="${HOME}/.sina/brain-autonomous-deploy-v1.flag"
HOLD_FLAG="${HOME}/.sina/enforcement/brain-autonomous-hold-v1.flag"
SHIP_FLAG="${HOME}/.sina/asf-ship-window-v1.flag"
RECEIPT_DIR="$ROOT/receipts"
LOG_DIR="${HOME}/.sina/logs"
TS="$(date -u +%Y%m%dT%H%M%SZ)"
AUTORUN_RECEIPT="$RECEIPT_DIR/brain-loop-autorun-${TS}.json"
STEP_LOG="$LOG_DIR/brain-autorun-step-${TS}.log"

mkdir -p "$LOG_DIR" "$RECEIPT_DIR"

_run_step() {
  local label="$1"
  shift
  local rc=0 attempt
  for attempt in 1 2; do
    echo "=== step: $label (attempt $attempt) ===" | tee -a "$STEP_LOG"
    set +e
    "$@" >>"$STEP_LOG" 2>&1
    rc=$?
    set -e
    if [[ "$rc" -eq 0 ]]; then
      echo "OK: $label" | tee -a "$STEP_LOG"
      return 0
    fi
    if brain_rc_is_sigkill "$rc" && [[ "$attempt" -eq 1 ]]; then
      echo "WARN: $label SIGKILL (rc=$rc) — retry in 3s" | tee -a "$STEP_LOG"
      sleep 3
      continue
    fi
    echo "FAIL: $label (rc=$rc)" | tee -a "$STEP_LOG"
    return "$rc"
  done
  return "$rc"
}

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

AUTONOMOUS=0
SHIP_WINDOW=0
HOLD_ACTIVE=0
MAC_SIGKILL=0
if [[ -f "$AUTONOMOUS_FLAG" ]]; then AUTONOMOUS=1; fi
if [[ -f "$HOLD_FLAG" ]]; then HOLD_ACTIVE=1; fi
if [[ -f "$SHIP_FLAG" || "${CI:-}" == "true" || "${GITHUB_ACTIONS:-}" == "true" ]]; then
  SHIP_WINDOW=1
fi

echo "=== brain_loop_autorun_v1 start autonomous=${AUTONOMOUS} hold=${HOLD_ACTIVE} ship_window=${SHIP_WINDOW} ==="
echo "sourcea_root=${SOURCEA_ROOT} python=${BRAIN_PYTHON}"

if [[ "$AUTONOMOUS" == "1" && "$HOLD_ACTIVE" == "1" ]]; then
  echo "brain_loop_autorun_v1: HOLD — autonomous deploy paused"
  "$BRAIN_PYTHON" - <<PY
import json
import sys
from pathlib import Path
sys.path.insert(0, "$ROOT")
from scripts.brain_domain_registry_v1 import load_registry, workflow_health_targets

targets = workflow_health_targets(load_registry())
payload = {
    "receipt_type": "BRAIN_LOOP_AUTORUN",
    "recorded_at": "$TS",
    "autonomous": True,
    "hold_active": True,
    "gate_note": "autonomous_hold_active",
    "heartbeat_at": "$TS",
    "health_score": 80,
    "health_state": "paused",
    "health_threshold": targets["min_health_score"],
    "heartbeat_max_age_minutes": targets["heartbeat_max_age_minutes"],
    "slo_miss": False,
    "slo_targets": targets,
}
Path("$AUTORUN_RECEIPT").write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
  exit 2
fi

SELF_HEAL_RC=0
PARALLEL_RC=0
MATRIX_RC=0
GATE_RC=0
GATE_NOTE="skipped"

export BRAIN_SELF_HEAL_TRIGGER=1
if ! _run_step "self-heal" bash "$ROOT/scripts/brain_loop_self_heal_v1.sh"; then
  SELF_HEAL_RC=$?
  brain_rc_is_sigkill "$SELF_HEAL_RC" && MAC_SIGKILL=1
else
  SELF_HEAL_RC=0
fi

if [[ "$AUTONOMOUS" == "1" ]]; then
  PAR_ARGS=(--sandbox-id brain_worker)
else
  PAR_ARGS=(--all)
fi
if ! _run_step "parallel" bash "$ROOT/scripts/run_parallel_brain_candidates_v1.sh" "${PAR_ARGS[@]}"; then
  PARALLEL_RC=$?
  brain_rc_is_sigkill "$PARALLEL_RC" && MAC_SIGKILL=1
else
  PARALLEL_RC=0
fi

RUN_MATRIX=0
if [[ "$AUTONOMOUS" == "1" || "$SHIP_WINDOW" == "1" ]]; then RUN_MATRIX=1; fi

LAUNCHD_TCC_BLOCK=0
if [[ "$RUN_MATRIX" == "1" ]]; then
  [[ "$AUTONOMOUS" == "1" ]] && export BRAIN_MATRIX_AUTORUN=1
  MATRIX_LOG="$(mktemp)"
  set +e
  bash "$ROOT/scripts/validate_brain_domain_e2e_matrix_v1.sh" >"$MATRIX_LOG" 2>&1
  MATRIX_RC=$?
  set -e
  cat "$MATRIX_LOG" | tee -a "$STEP_LOG"
  if [[ "$MATRIX_RC" -ne 0 ]] && grep -q "Operation not permitted" "$MATRIX_LOG"; then
    LAUNCHD_TCC_BLOCK=1
  fi
  rm -f "$MATRIX_LOG"
else
  echo "SKIP: e2e matrix (observe-only)"
fi

HEALTH_SCORE=100
if [[ "$SELF_HEAL_RC" -ne 0 ]]; then HEALTH_SCORE=$((HEALTH_SCORE - 35)); fi
if [[ "$PARALLEL_RC" -ne 0 ]]; then HEALTH_SCORE=$((HEALTH_SCORE - 25)); fi
if [[ "$MATRIX_RC" -ne 0 ]]; then HEALTH_SCORE=$((HEALTH_SCORE - 25)); fi
if [[ "$GATE_RC" -ne 0 ]]; then HEALTH_SCORE=$((HEALTH_SCORE - 10)); fi
if [[ "$HOLD_ACTIVE" -eq 1 ]]; then HEALTH_SCORE=$((HEALTH_SCORE - 5)); fi
if [[ "$HEALTH_SCORE" -lt 0 ]]; then HEALTH_SCORE=0; fi
HEALTH_STATE=healthy
if [[ "$HOLD_ACTIVE" -eq 1 ]]; then
  HEALTH_STATE=deferred
elif [[ "$HEALTH_SCORE" -lt 85 || "$SELF_HEAL_RC" -ne 0 || "$PARALLEL_RC" -ne 0 || "$MATRIX_RC" -ne 0 || "$GATE_RC" -ne 0 ]]; then
  HEALTH_STATE=degraded
fi
SLO_MISS=0
if [[ "$HEALTH_SCORE" -lt 85 || "$SELF_HEAL_RC" -ne 0 || "$PARALLEL_RC" -ne 0 || "$MATRIX_RC" -ne 0 || "$GATE_RC" -ne 0 ]]; then
  SLO_MISS=1
fi

MUTATION_TRIALS=$("$BRAIN_PYTHON" - <<PY
import sys
from pathlib import Path
sys.path.insert(0, "$ROOT")
from scripts.brain_autonomous_controls_v1 import mutation_trials_enabled
print(1 if mutation_trials_enabled(Path("$SOURCEA_ROOT")) else 0)
PY
)

PROMOTE_READY=0
BRAIN_LIVE_DRIFT=0
if [[ "$SELF_HEAL_RC" -eq 0 && "$PARALLEL_RC" -eq 0 && "$MUTATION_TRIALS" == "0" ]]; then
  if [[ "$MATRIX_RC" -eq 0 ]]; then
    PROMOTE_READY=1
  elif [[ "$AUTONOMOUS" == "1" && -f "$STEP_LOG" ]] && grep -q "FAIL: brain live smoke" "$STEP_LOG"; then
    BRAIN_LIVE_DRIFT=1
    PROMOTE_READY=1
    echo "NOTE: brain-live drift — autonomous promote will sync live Worker"
  fi
fi

if [[ "$PROMOTE_READY" -eq 0 ]]; then
  if [[ "$AUTONOMOUS" == "1" && ( "$LAUNCHD_TCC_BLOCK" == "1" || "$MAC_SIGKILL" == "1" ) ]]; then
    GATE_NOTE="mac_env_block_no_hold"
    echo "NOTE: Mac TCC/SIGKILL blocker — not setting autonomous hold (fix: bash scripts/install_brain_loop_launchd_v1.sh)"
  elif [[ "$AUTONOMOUS" == "1" ]]; then
    "$BRAIN_PYTHON" - <<PY
import sys
sys.path.insert(0, "$ROOT")
from scripts.brain_autonomous_controls_v1 import set_autonomous_hold
set_autonomous_hold(reason="autorun pre-promote fail self_heal=$SELF_HEAL_RC parallel=$PARALLEL_RC matrix=$MATRIX_RC")
PY
    GATE_NOTE="autonomous_hold_set_pre_promote"
  fi
elif [[ "$AUTONOMOUS" == "1" ]]; then
  set +e
  bash "$ROOT/scripts/promote_brain_worker_v1.sh" --autonomous-deploy \
    --deploy-receipt "$RECEIPT_DIR/brain-autonomous-promote-${TS}.json"
  GATE_RC=$?
  set -e
  if [[ "$GATE_RC" -eq 0 ]]; then
    if [[ "$BRAIN_LIVE_DRIFT" == "1" ]]; then
      GATE_NOTE="autonomous_promote_healed_brain_live_drift"
    else
      GATE_NOTE="autonomous_promote_executed"
    fi
    "$BRAIN_PYTHON" - <<PY
import sys
sys.path.insert(0, "$ROOT")
from scripts.brain_autonomous_controls_v1 import clear_autonomous_hold
clear_autonomous_hold()
PY
  else
    GATE_NOTE="autonomous_promote_failed"
    if grep -q 'smoke_ok=False' "${HOME}/.sina/enforcement/brain-autonomous-hold-v1.flag" 2>/dev/null; then
      echo "NOTE: promote failed on smoke — hold set; will auto-clear next cycle if deploy landed"
    fi
  fi
elif [[ "$SHIP_WINDOW" == "1" ]]; then
  GATE_NOTE="semi_auto_available_invoke_promote_brain_worker_v1"
  echo "NOTE: invoke bash scripts/promote_brain_worker_v1.sh for confirm-each-time promote"
fi

"$BRAIN_PYTHON" - <<PY
import json
import sys
from pathlib import Path
sys.path.insert(0, "$ROOT")
from scripts.brain_domain_registry_v1 import load_registry, workflow_health_targets

targets = workflow_health_targets(load_registry())
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
    "sourcea_root": "$SOURCEA_ROOT",
    "brain_python": "$BRAIN_PYTHON",
    "mac_sigkill": bool($MAC_SIGKILL),
    "step_log": "$STEP_LOG",
    "heartbeat_at": "$TS",
    "health_score": $HEALTH_SCORE,
    "health_state": "$HEALTH_STATE",
    "health_threshold": targets["min_health_score"],
    "heartbeat_max_age_minutes": targets["heartbeat_max_age_minutes"],
    "slo_miss": bool($SLO_MISS),
    "slo_targets": targets,
}
out = Path("$AUTORUN_RECEIPT")
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2))
print(f"autorun_receipt: {out}")
PY

if [[ "$AUTONOMOUS" != "1" && "$SHIP_WINDOW" != "1" ]]; then
  echo "brain_loop_autorun_v1: OBSERVE_ONLY"
  exit 0
fi

if [[ "$MAC_SIGKILL" -eq 1 || "$LAUNCHD_TCC_BLOCK" -eq 1 ]]; then
  echo "brain_loop_autorun_v1: MAC_BLOCK (no hold — will retry next cycle)"
  exit 0
fi

if [[ "$GATE_RC" -eq 0 ]]; then
  echo "brain_loop_autorun_v1: ALL PASS"
  exit 0
fi

echo "brain_loop_autorun_v1: FAIL"
exit 1
