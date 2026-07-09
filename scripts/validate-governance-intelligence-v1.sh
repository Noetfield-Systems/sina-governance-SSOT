#!/usr/bin/env bash
# Mac-founder-session-safe governance intelligence validation (<=90s)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
/usr/bin/python3 scripts/validate_governance_intelligence_v1.py
/usr/bin/python3 scripts/validate_intake_sink_v1.py
/usr/bin/python3 scripts/validate_library_promote_v1.py
/usr/bin/python3 scripts/governance_intelligence_engine_v1.py audit --write-receipt >/dev/null
/usr/bin/python3 scripts/governance_intelligence_engine_v1.py review-queue --json >/dev/null
