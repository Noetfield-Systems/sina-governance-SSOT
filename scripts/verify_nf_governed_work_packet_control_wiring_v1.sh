#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_GOVERNED_WORK_PACKET_CONTROL_LOCKED_v1.md"
  "data/nf_governed_work_packet_control_v1_LOCKED.json"
  "data/schemas/goal_contract_v1.json"
  "data/schemas/human_tax_event_v1.json"
  "data/schemas/work_packet_terminal_v1.json"
  "data/schemas/failure_signature_v1.json"
  "data/schemas/incident_packet_v1.json"
  "scripts/lib/governed_work_packet_v1.py"
  "docs/dispatch/nf-governed-work-packet-control-all-repos.md"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_GOVERNED_WORK_PACKET_CONTROL_LOCK_2026-07-24.md"
  "receipts/doctrine/NF_GOVERNED_WORK_PACKET_CONTROL_v1_LOCKED.lock.json"
  "scripts/verify_nf_governed_work_packet_control_wiring_v1.sh"
)
for f in "${need[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING $f"; fail=1; fi
done
grep -q "GOVERNED WORK PACKET CONTROL" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT section missing"; fail=1; }
grep -q "Governed work packet control" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT row missing"; fail=1; }
grep -q "governed work packet control" AGENTS.md || { echo "AGENTS skill missing"; fail=1; }
python3 - <<'PY'
import json
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from lib.governed_work_packet_v1 import (
    authority_hash,
    may_resume_after_incident,
    soft_breaker_trips,
    mechanical_done,
    reject_unnecessary_fanout,
)

d = json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
need = {
    "governed_work_packet_control",
    "governed_work_packet_control_machine",
    "governed_work_packet_control_dispatch",
}
for lane, body in d["lanes"].items():
    roles = {e["role"] for e in body["must_read"]}
    missing = need - roles
    if missing:
        raise SystemExit(f"lane {lane} missing roles {sorted(missing)}")
print("lanes ok")

j = json.loads(Path("data/nf_governed_work_packet_control_v1_LOCKED.json").read_text())
assert j.get("decision_id") == "NF-GOVERNED-WORK-PACKET-CONTROL-V1"
assert j["same_plan_hash_resume_after_incident"] is False
assert "ACCEPTED_ARTIFACT" in j["work_packet_terminals"]
assert j["learning_path"] == "NF-MOTOR-LEARNING-ORGAN-V1"
print("machine ok")

sample = {
    "goal_id": "goal_1",
    "owner": "founder",
    "goal_version": 1,
    "intent": "x",
    "acceptance_predicates": ["a"],
    "scope_allowlist": ["apps/x/**"],
    "forbidden_effects": [],
    "budgets": {
        "max_attempts": 2,
        "max_children": 1,
        "max_minutes": 30,
        "max_cost_usd": 1.5,
        "max_human_tax_units": 5,
    },
    "evidence_required": ["receipt"],
    "stop_policy": "STOP_AND_INCIDENT",
}
h = authority_hash(sample)
assert h.startswith("sha256:") and len(h) == 71
assert may_resume_after_incident(prior_plan_hash="p1", new_plan_hash="p1") is False
assert may_resume_after_incident(prior_plan_hash="p1", new_plan_hash="p2") is True
assert "UNNECESSARY_FANOUT" in soft_breaker_trips(fanout=5, fanout_budget=1)
assert reject_unnecessary_fanout(max_workers=1, requested_workers=5) == "UNNECESSARY_FANOUT"
assert mechanical_done(
    artifact_exists=True,
    all_acceptance_checks_pass=True,
    scope_is_clean=True,
    evidence_is_valid=True,
    receipt_is_written=True,
)
assert not mechanical_done(
    artifact_exists=False,
    all_acceptance_checks_pass=True,
    scope_is_clean=True,
    evidence_is_valid=True,
    receipt_is_written=True,
)
print("helpers ok")
PY
grep -q "SAME PLAN HASH CANNOT RESUME" SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_GOVERNED_WORK_PACKET_CONTROL_LOCKED_v1.md || { echo "resume law missing"; fail=1; }
grep -q "ACTIVE_FOREVER" SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_GOVERNED_WORK_PACKET_CONTROL_LOCKED_v1.md || { echo "terminal ban missing"; fail=1; }

if [[ $fail -eq 0 ]]; then
  echo "NF GOVERNED WORK PACKET CONTROL WIRING: PASS"
else
  echo "NF GOVERNED WORK PACKET CONTROL WIRING: FAIL"
  exit 1
fi
