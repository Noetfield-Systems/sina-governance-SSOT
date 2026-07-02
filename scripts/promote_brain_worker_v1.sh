#!/usr/bin/env bash
# Promote brain_worker via promotion_gate — confirm-each-time or --autonomous-deploy.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCEA_ROOT="${SOURCEA_ROOT:-$HOME/Desktop/SourceA}"
RECEIPT_URL="${RECEIPT_URL:-https://sina-governance-ssot-advisory.kazemnezhadsina144.workers.dev/receipt/latest}"
SECONDARY_CF_ACCOUNT="${SECONDARY_CF_ACCOUNT:-b7282b4a5c17b84d62e3ef8866b878f8}"
ROLLBACK_RECEIPT="${ROLLBACK_RECEIPT:-$ROOT/receipts/brain-rollback-drill-latest.json}"
INDEPENDENCE_RECEIPT="${INDEPENDENCE_RECEIPT:-$ROOT/receipts/verifier-independence-proof-latest.json}"
DEPLOY_RECEIPT="${DEPLOY_RECEIPT:-$ROOT/receipts/phase3-step4-promote-receipt.json}"
LIVE_VERSION_CMD='cd cloud/workers/sourcea-brain-chat-v1 && CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN}" wrangler deployments list --name sourcea-brain-chat-v1 --json'

AUTONOMOUS=0
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --autonomous-deploy) AUTONOMOUS=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    --deploy-receipt) DEPLOY_RECEIPT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

bash "$ROOT/scripts/load_cf_tokens_v1.sh"

read -r CANDIDATE_REF CANDIDATE_PATH CANDIDATE_SHA WORKER_SHA <<<"$(python3 - <<PY
import sys
from pathlib import Path

root = Path("$ROOT")
sys.path.insert(0, str(root))
from gates.promotion_gate import load_receipt

receipt = load_receipt("$RECEIPT_URL")
print(
    receipt.get("candidate_ref", ""),
    receipt.get("candidate_path", ""),
    receipt.get("candidate_sha256", ""),
    receipt.get("worker_code_sha256", receipt.get("knowledge_bundle_sha256", "")),
)
PY
)"

GATE_ARGS=(
  python3 "$ROOT/gates/promotion_gate.py"
  --sandbox-id brain_worker
  --receipt-url "$RECEIPT_URL"
  --expected-candidate-ref "$CANDIDATE_REF"
  --expected-candidate-path "$CANDIDATE_PATH"
  --expected-candidate-sha256 "$CANDIDATE_SHA"
  --expected-cf-account-id "$SECONDARY_CF_ACCOUNT"
  --expected-worker-code-sha256 "$WORKER_SHA"
  --expected-knowledge-bundle-sha256 "$CANDIDATE_SHA"
  --rollback-receipt "$ROLLBACK_RECEIPT"
  --independence-receipt-path "$INDEPENDENCE_RECEIPT"
  --deploy-source-root "$SOURCEA_ROOT"
  --source-bundle-path cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json
  --live-version-command "$LIVE_VERSION_CMD"
  --deploy-command "bash scripts/brain_cli_v1.sh deploy-verified"
  --deploy-receipt-path "$DEPLOY_RECEIPT"
)

if [[ "$DRY_RUN" == "1" ]]; then
  "${GATE_ARGS[@]}"
  exit $?
fi

if [[ "$AUTONOMOUS" == "1" ]]; then
  "${GATE_ARGS[@]}" --autonomous-deploy
  exit $?
fi

printf 'CONFIRM DEPLOY\n' | "${GATE_ARGS[@]}" --confirm-each-time
