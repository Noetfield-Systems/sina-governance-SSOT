#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0
need=(
  "SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_COMPUTE_ROI_ALLOCATION_LOCKED_v1.md"
  "data/nf_compute_roi_allocation_v1_LOCKED.json"
  "docs/dispatch/nf-compute-roi-allocation-all-repos.md"
  "docs/dispatch/noos-repin-after-pr62-compute-roi.md"
  "data/sg-authority-ref-compute-roi-v1.json"
  "SG-Canonical-Library/noetfield-library/P99-LEDGER/NF_COMPUTE_ROI_ALLOCATION_LOCK_2026-07-19.md"
  "receipts/doctrine/NF_COMPUTE_ROI_ALLOCATION_v1_LOCKED.lock.json"
  "scripts/verify_nf_compute_roi_allocation_wiring_v1.sh"
)
for f in "${need[@]}"; do
  if [[ ! -f "$f" ]]; then echo "MISSING $f"; fail=1; fi
done
grep -q "COMPUTE / ROI ALLOCATION" SG-Canonical-Library/noetfield-library/ARCHITECT_START_HERE.md || { echo "ARCHITECT section 2k missing"; fail=1; }
grep -q "Compute / ROI allocation" SG-Canonical-Library/noetfield-library/P2-SSOT/SSOT_INDEX.md || { echo "SSOT compute ROI row missing"; fail=1; }
grep -q "compute / ROI allocation" AGENTS.md || { echo "AGENTS 0h missing"; fail=1; }
python3 - <<'PY'
import json
from pathlib import Path
d=json.loads(Path("data/agent_read_surfaces_v1.json").read_text())
need={"compute_roi_allocation","compute_roi_allocation_machine","compute_roi_allocation_dispatch","compute_roi_allocation_authority_ref"}
for lane, body in d["lanes"].items():
    roles={e["role"] for e in body["must_read"]}
    missing=need-roles
    if missing:
        raise SystemExit(f"lane {lane} missing roles {sorted(missing)}")
print("lanes ok")
j=json.loads(Path("data/nf_compute_roi_allocation_v1_LOCKED.json").read_text())
assert j.get("decision_id")=="NF-COMPUTE-ROI-ALLOCATION-V1"
assert j["actions_minutes_budget"]["monthly_total"]==50000
assert j["job_wake"]=="authenticated_http_job_id_only"
assert "AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD" in j["holds_preserved"]
print("machine ok")
ref=json.loads(Path("data/sg-authority-ref-compute-roi-v1.json").read_text())
assert ref["schema"]=="noetfield.sg-authority-ref.v1"
assert ref["decision_id"]=="NF-COMPUTE-ROI-ALLOCATION-V1"
print("authority-ref ok")
PY
grep -q "AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD" SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_COMPUTE_ROI_ALLOCATION_LOCKED_v1.md || { echo "HOLD floor missing"; fail=1; }
grep -q "authenticated HTTP" SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_COMPUTE_ROI_ALLOCATION_LOCKED_v1.md || { echo "job wake law missing"; fail=1; }

if [[ $fail -eq 0 ]]; then
  echo "NF COMPUTE ROI ALLOCATION WIRING: PASS"
else
  echo "NF COMPUTE ROI ALLOCATION WIRING: FAIL"
  exit 1
fi
