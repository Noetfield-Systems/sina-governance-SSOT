#!/usr/bin/env bash
# verify_l0_repo_graph_memory_v1.sh
#
# Verifies the L0 Repo Graph Memory pilot is actually wired, not just present:
#   1. graph rebuilds cleanly (also guarantees freshness for check 3)
#   2. graph outputs exist, index is valid JSON, report has the required sections
#   3. graph timestamp is current (generated within this verify run)
#   4. query command works end-to-end (subsystem lookup + keyword lookup)
#   5. AGENTS.md carries the broad-read-gate instruction + token budget rule
#
# Writes a receipt to receipts/ and exits 0 (PASS) or 1 (FAIL).
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ALL_PASS=1
CHECKS_JSON="[]"
NOW_EPOCH=$(date -u +%s)
TS=$(date -u +%Y%m%dT%H%M%SZ)

check() {
  local name="$1" rc="$2" detail="$3"
  if [ "$rc" = "0" ]; then
    echo "[PASS] $name — $detail"
  else
    echo "[FAIL] $name — $detail"
    ALL_PASS=0
  fi
  CHECKS_JSON=$(python3 -c "
import json, sys
checks = json.loads(sys.argv[1])
checks.append({'name': sys.argv[2], 'pass': sys.argv[3] == '0', 'detail': sys.argv[4]})
print(json.dumps(checks))
" "$CHECKS_JSON" "$name" "$rc" "$detail")
}

# 1. graph rebuilds cleanly
BUILD_OUT=$(python3 scripts/build_repo_graph_v1.py 2>&1)
BUILD_RC=$?
check "graph_builds" "$BUILD_RC" "build_repo_graph_v1.py exit=$BUILD_RC"

# 2a. outputs exist and index is valid JSON
if [ -f graph-out/graph_index_v1.json ] && [ -f graph-out/GRAPH_REPORT.md ]; then
  python3 -c "import json; json.load(open('graph-out/graph_index_v1.json'))" 2>/dev/null
  check "graph_outputs_exist_and_valid_json" "$?" "graph_index_v1.json + GRAPH_REPORT.md present, index parses"
else
  check "graph_outputs_exist_and_valid_json" "1" "missing graph-out/graph_index_v1.json or GRAPH_REPORT.md"
fi

# 2b. report contains the sections the pilot order requires
REQUIRED_SECTIONS=("Subsystem map" "Dependency / reference edges" "Ignored directories" "Generated (last indexed)")
for section in "${REQUIRED_SECTIONS[@]}"; do
  grep -qF "$section" graph-out/GRAPH_REPORT.md 2>/dev/null
  check "report_has_section:${section}" "$?" "GRAPH_REPORT.md contains '${section}'"
done

# 3. graph timestamp is current (generated within the last 300s of this verify run)
GEN_EPOCH=$(python3 -c "
import json
from datetime import datetime, timezone
try:
    idx = json.load(open('graph-out/graph_index_v1.json'))
    dt = datetime.strptime(idx['generated_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
    print(int(dt.timestamp()))
except Exception:
    print(-1)
" 2>/dev/null)
if [ "${GEN_EPOCH:-}" != "-1" ] && [ -n "${GEN_EPOCH:-}" ]; then
  AGE=$(( NOW_EPOCH - GEN_EPOCH ))
  if [ "$AGE" -ge -5 ] && [ "$AGE" -le 300 ]; then
    check "graph_timestamp_current" "0" "generated_at is ${AGE}s old (<=300s)"
  else
    check "graph_timestamp_current" "1" "generated_at is ${AGE}s old (expected <=300s)"
  fi
else
  check "graph_timestamp_current" "1" "could not parse generated_at from graph_index_v1.json"
fi

# 4a. query by subsystem works
Q1=$(python3 scripts/query_repo_graph_v1.py data 2>&1)
Q1_RC=$?
if [ "$Q1_RC" = "0" ] && echo "$Q1" | grep -q "^# subsystem: data"; then
  check "query_subsystem_works" "0" "query_repo_graph_v1.py data returned a subsystem listing"
else
  check "query_subsystem_works" "1" "query_repo_graph_v1.py data did not return expected output (exit=$Q1_RC)"
fi

# 4b. query by keyword works
Q2=$(python3 scripts/query_repo_graph_v1.py founder_canon 2>&1)
Q2_RC=$?
if [ "$Q2_RC" = "0" ] && echo "$Q2" | grep -q "founder_canon"; then
  check "query_keyword_works" "0" "query_repo_graph_v1.py founder_canon returned matches"
else
  check "query_keyword_works" "1" "query_repo_graph_v1.py founder_canon did not return expected output (exit=$Q2_RC)"
fi

# 5. AGENTS.md instruction + rules present (this repo's CLAUDE.md-equivalent instruction file)
grep -q "L0 repo graph memory" AGENTS.md
check "instruction_file_references_graph" "$?" "AGENTS.md references L0 repo graph memory"

grep -q "broad-read gate" AGENTS.md
check "broad_read_gate_rule_present" "$?" "AGENTS.md contains the broad-read gate rule"

grep -q "Token budget" AGENTS.md
check "token_budget_rule_present" "$?" "AGENTS.md contains the token budget rule"

RESULT="PASS"
[ "$ALL_PASS" = "1" ] || RESULT="FAIL"

RECEIPT_PATH="receipts/l0-repo-graph-verify-${TS}.json"
python3 -c "
import json, sys
payload = {
    'action': 'l0_repo_graph_memory_verify',
    'repo': 'sina-governance-ssot',
    'timestamp_utc': sys.argv[1],
    'result': sys.argv[2],
    'checks': json.loads(sys.argv[3]),
}
open(sys.argv[4], 'w').write(json.dumps(payload, indent=2) + chr(10))
" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$RESULT" "$CHECKS_JSON" "$RECEIPT_PATH"

echo
echo "L0 repo graph memory verify: $RESULT"
echo "Receipt: $RECEIPT_PATH"

[ "$RESULT" = "PASS" ]
