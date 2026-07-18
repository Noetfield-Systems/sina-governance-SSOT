#!/usr/bin/env bash
# P0 containment: no Brain promotion until deterministic SG v2 is commissioned.
set -euo pipefail

echo "BLOCKED_SG_NOT_COMMISSIONED"
echo "deploy_executed: false"
echo "reason: data/runtime_reality_v1.json holds autonomous production mutations"
exit 78
