#!/usr/bin/env bash
# Brain domain E2E matrix — governance public + SourceA public proof + brain-live + contract pages.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
export SOURCEA_ROOT
export SOURCEA_CONTRACT_E2E_ALLOW_REGIONAL_REDIRECT="${SOURCEA_CONTRACT_E2E_ALLOW_REGIONAL_REDIRECT:-1}"
SANDBOX_ID="${BRAIN_MATRIX_SANDBOX_ID:-all}"

echo "=== validate_brain_domain_e2e_matrix_v1 start (sandbox=${SANDBOX_ID}) ==="
ERRORS=0

_run() {
  local label="$1"
  shift
  echo "=== ${label} ==="
  if "$@"; then
    echo "OK: ${label}"
  else
    echo "FAIL: ${label}"
    ERRORS=$((ERRORS + 1))
  fi
  echo
}

_run "brain domain registry" python3 "$ROOT/scripts/validate_brain_domain_registry_v1.py"
_run "governance public e2e" bash "$ROOT/scripts/validate-governance-public-e2e-v1.sh"

if [[ -f "$SOURCEA_ROOT/scripts/validate-sourcea-public-proof-e2e-v1.sh" ]]; then
  _run "sourcea public proof" bash "$SOURCEA_ROOT/scripts/validate-sourcea-public-proof-e2e-v1.sh"
else
  echo "FAIL: missing sourcea public proof script"
  ERRORS=$((ERRORS + 1))
fi

if [[ "$SANDBOX_ID" == "all" || "$SANDBOX_ID" == "brain_worker" || "$SANDBOX_ID" == "knowledge_bundle" || "$SANDBOX_ID" == "locked_definitions" ]]; then
  if [[ -f "$SOURCEA_ROOT/scripts/validate-sourcea-brain-live-v1.sh" ]]; then
    _run "brain live smoke" bash "$SOURCEA_ROOT/scripts/validate-sourcea-brain-live-v1.sh"
  else
    echo "FAIL: missing brain live smoke script"
    ERRORS=$((ERRORS + 1))
  fi
fi

if [[ "$SANDBOX_ID" == "all" || "$SANDBOX_ID" == "contract_pages" ]]; then
  if [[ -f "$SOURCEA_ROOT/scripts/validate-sourcea-contract-pages-e2e-v1.sh" ]]; then
    _run "contract pages e2e" bash "$SOURCEA_ROOT/scripts/validate-sourcea-contract-pages-e2e-v1.sh"
  else
    echo "FAIL: missing contract pages e2e script"
    ERRORS=$((ERRORS + 1))
  fi
fi

if [[ "$ERRORS" -gt 0 ]]; then
  echo "validate_brain_domain_e2e_matrix_v1: FAIL errors=${ERRORS} sandbox=${SANDBOX_ID}"
  exit 1
fi

echo "validate_brain_domain_e2e_matrix_v1: ALL PASS sandbox=${SANDBOX_ID}"
