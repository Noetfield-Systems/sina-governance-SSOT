#!/usr/bin/env bash
# AGENT_READ_STALENESS_v1 — alive docs + stale law pointer gate for SG governance.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/agent_read_staleness_engine_v1.py --write-receipt --write-queue --fail-on blocker "$@"
echo "verify_agent_read_staleness_v1: PASS"
