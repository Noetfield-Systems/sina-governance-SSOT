#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_DECISION_CAPACITY_LOCKED_v1.md"
  "data/nf_decision_capacity_v1_LOCKED.json"
  "data/schemas/decision_capacity_gap_v1.json"
  "data/schemas/decision_capacity_proposal_v1.json"
  "data/schemas/decision_policy_candidate_v1.json"
  "scripts/lib/decision_capacity_v1.py"
  "docs/dispatch/nf-decision-capacity-all-repos.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_DECISION_CAPACITY_LOCK_2026-07-24.md"
  "receipts/doctrine/NF_DECISION_CAPACITY_v1_LOCKED.lock.json"
  "scripts/verify_nf_decision_capacity_wiring_v1.sh"
)
for f in "${need[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING $f"; fail=1; fi
done
grep -q "DECISION CAPACITY" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT section missing"; fail=1; }
grep -q "Decision capacity" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT row missing"; fail=1; }
grep -q "decision capacity" AGENTS.md || { echo "AGENTS skill missing"; fail=1; }

python3 - <<'PY'
import json
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from lib.decision_capacity_v1 import close_capacity_loop, detect_capacity_gap

d = json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
need = {"decision_capacity", "decision_capacity_machine", "decision_capacity_dispatch"}
for lane, body in d["lanes"].items():
    roles = {e["role"] for e in body["must_read"]}
    missing = need - roles
    if missing:
        raise SystemExit(f"lane {lane} missing roles {sorted(missing)}")
print("lanes ok")

j = json.loads(Path("data/nf_decision_capacity_v1_LOCKED.json").read_text())
assert j["decision_id"] == "NF-DECISION-CAPACITY-V1"
assert j["incident_trigger"] == "MISSING_DECISION_CAPACITY"
assert "WEBPAGE_CHANGE" in j["decision_classes"]
assert j["closed_path"][0] == "MISSING_DECISION_CAPACITY"
print("machine ok")

inc = json.loads(Path("data/schemas/incident_packet_v1.json").read_text())
assert "MISSING_DECISION_CAPACITY" in inc["properties"]["trigger"]["enum"]
assert "CREATE_OR_EXTEND_POLICY" in inc["properties"]["route"]["enum"]
print("incident schema ok")

loop = close_capacity_loop(
    decision_class="WEBPAGE_CHANGE",
    event_types=["GOAL_RESTATEMENT", "SCOPE_RESTATEMENT", "MANUAL_CORRECTION"],
    existing_policy_coverage=0.35,
    task_id="task_verify",
    human_tax_units=9,
)
assert loop is not None
assert loop["incident_type"] == "MISSING_DECISION_CAPACITY"
assert loop["gap"]["schema"] == "noetfield.decision_capacity_gap.v1"
assert loop["proposal"]["schema"] == "noetfield.decision_capacity_proposal.v1"
assert loop["policy_candidate"]["schema"] == "noetfield.decision_policy_candidate.v1"
assert loop["learning_record"]["status"] == "draft"
assert loop["learning_record"]["source_event"] == "MISSING_DECISION_CAPACITY"
assert loop["learning_record"]["layer"] == "policy"
assert loop["work_status"] == "FROZEN"
print("capacity loop ok")

assert detect_capacity_gap(
    decision_class="EMAIL_DRAFT",
    event_types=["OWNER_DECISION"],
    existing_policy_coverage=0.99,
) is None
print("no false gap ok")
PY

if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo "PASS: nf_decision_capacity wiring"
