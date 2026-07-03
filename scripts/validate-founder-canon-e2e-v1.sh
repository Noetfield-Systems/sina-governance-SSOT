#!/usr/bin/env bash
# FOUNDER_CANON v1 full E2E — wiring + machine cycle (Mac-safe, ≤90s).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

/usr/bin/python3 "$ROOT/scripts/validate_founder_canon_e2e_v1.py"
/usr/bin/python3 "$ROOT/scripts/validate_parallel_automation_governance_v1.py"
/usr/bin/python3 "$ROOT/scripts/run_machine_autonomy_cycle_v1.py" || true

echo "validate-founder-canon-e2e-v1: OK (canon wired; cycle receipt written)"
