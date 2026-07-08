#!/usr/bin/env bash
# AGENT_READ_GOVERNANCE_CYCLE_v1 — Observe → reason → queue → receipt (SG alive-doc law).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Agent read governance cycle ==="
python3 scripts/agent_read_staleness_engine_v1.py \
  --write-receipt \
  --write-queue \
  --fail-on blocker

echo ""
echo "Queue: data/governance_stale_pointer_queue_v1.json"
python3 - <<'PY'
import json
from pathlib import Path
q = json.loads(Path("data/governance_stale_pointer_queue_v1.json").read_text())
print(f"  open={q['open_count']} p0={q['open_p0']}")
for item in q.get("items", [])[:12]:
    print(f"  {item['queue_id']} [{item['priority']}] {item['repair_lane']}: {item['action']}")
    print(f"    {item.get('path','')[:90]}")
PY
echo "AGENT_READ_GOVERNANCE_CYCLE: pass"
