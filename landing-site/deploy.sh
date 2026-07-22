#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${CLOUDFLARE_PAGES_PROJECT_NAME:-noetfield-runway-standalone}"
CF_ACCOUNT_ID="${CLOUDFLARE_ACCOUNT_ID:-${CLOUDFLARE_ACCOUNT_ID_FILE:-${CLOUDFLARE_PAGES_ACCOUNT_ID:-}}}"
SITE_DIR="$(cd "$(dirname "$0")" && pwd)"
DEFAULT_ENV="${CLOUDFLARE_ENV:-production}"
PROJECT_BRANCH="${CLOUDFLARE_PAGES_BRANCH:-main}"
COMMIT_DIRTY="${CLOUDFLARE_PAGES_COMMIT_DIRTY:-}"
AUTH_MODE="${CLOUDFLARE_PAGES_AUTH_MODE:-oauth}"

function normalize_token() {
  local token="$1"

  token="${token#Bearer }"
  token="${token#bearer }"
  token="${token%%[[:space:]]*}"

  echo "$token"
}

function is_invalid_token_shape() {
  local token="$1"

  if [[ -z "$token" || "$token" == "<"*">" || "$token" == *" "* || "$token" == *$'\t'* || "$token" == *$'\n'* || "$token" == *$'\r'* ]]; then
    return 0
  fi

  return 1
}

function normalize_mode() {
  local candidate="$1"
  candidate="$(echo "${candidate:-}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')"
  if [ "$candidate" = "live" ] || [ "$candidate" = "offline" ]; then
    echo "$candidate"
  else
    echo "demo"
  fi
}

function normalize_github_repo_url() {
  local raw="$1"
  if [ -z "$raw" ]; then
    echo "unknown"
    return
  fi

  if [[ "$raw" == http*://* ]]; then
    echo "${raw%.git}"
    return
  fi

  if [[ "$raw" == git@github.com:* ]]; then
    raw="https://github.com/${raw#git@github.com:}"
    echo "${raw%.git}"
    return
  fi

  echo "$raw"
}

function repo_sha() {
  local target_dir="$1"
  if [ -z "${target_dir}" ]; then
    echo "unknown"
    return
  fi

  if git -C "$target_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$target_dir" rev-parse HEAD 2>/dev/null || echo "unknown"
  else
    echo "unknown"
  fi
}

function repo_branch() {
  local target_dir="$1"
  if [ -z "${target_dir}" ]; then
    echo "unknown"
    return
  fi

  if git -C "$target_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    git -C "$target_dir" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown"
  else
    echo "unknown"
  fi
}

function resolve_repo_directory() {
  local start_dir="$1"
  local candidate="$2"
  local fallback_dir

  if [ -z "$candidate" ]; then
    echo ""
    return
  fi

  if [ -d "$candidate" ] && git -C "$candidate" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "$candidate"
    return
  fi

  fallback_dir="${start_dir}/../${candidate}"
  if [ -d "$fallback_dir" ] && git -C "$fallback_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "$fallback_dir"
    return
  fi

  fallback_dir="${start_dir}/../../${candidate}"
  if [ -d "$fallback_dir" ] && git -C "$fallback_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "$fallback_dir"
    return
  fi

  echo ""
}

function compute_artifact_sha256() {
  local tmp_file
  tmp_file="$(mktemp)"
  local source_files=(
    "$SITE_DIR/index.html"
    "$SITE_DIR/styles.css"
    "$SITE_DIR/app.js"
    "$SITE_DIR/runway-bootstrap.js"
    "$SITE_DIR/runway-config.js"
    "$SITE_DIR/providers/demo-runway-provider.js"
    "$SITE_DIR/providers/live-runway-provider.js"
    "$SITE_DIR/functions/v1/runway/_proxy.js"
    "$SITE_DIR/functions/v1/runway/runtime.js"
    "$SITE_DIR/functions/v1/runway/receipts/verify.js"
    "$SITE_DIR/functions/v1/runway/runs/[runId]/receipt.js"
    "$SITE_DIR/_worker.js"
    "$SITE_DIR/verification.json"
    "$SITE_DIR/verifier.json"
    "$SITE_DIR/verifier.txt"
  )

  for file in "${source_files[@]}"; do
    if [ -f "$file" ]; then
      cat "$file" >> "$tmp_file"
      printf '\n' >> "$tmp_file"
    fi
  done

  if [ ! -s "$tmp_file" ]; then
    rm -f "$tmp_file"
    echo "unknown"
    return
  fi

  local checksum

  if command -v sha256sum >/dev/null 2>&1; then
    checksum="$(sha256sum "$tmp_file" | awk '{print $1}')"
  elif command -v shasum >/dev/null 2>&1; then
    checksum="$(shasum -a 256 "$tmp_file" | awk '{print $1}')"
  else
    rm -f "$tmp_file"
    echo "unknown"
    return
  fi

  if [ -z "$checksum" ]; then
    rm -f "$tmp_file"
    echo "unknown"
    return
  fi

  rm -f "$tmp_file"
  echo "$checksum"
}

function detect_backend_status() {
  local base_url="$1"
  if [ -z "$base_url" ]; then
    echo "not_configured"
    return
  fi

  if ! command -v curl >/dev/null 2>&1; then
    echo "unknown"
    return
  fi

  local probe_url
  probe_url="${base_url%/}/v1/runway/runtime"
  local probe_exit
  probe_exit="$(curl -sS -m 4 -o /tmp/noetfield-runway-standalone-curl-probe.out -w "%{http_code}" -X GET "$probe_url" \
    -H "x-tenant-id: tenant-runway-staging" \
    -H "accept: application/json" || echo "000")"

  case "$probe_exit" in
    200)
      echo "connected"
      ;;
    *)
      echo "disconnected:${probe_exit}"
      ;;
  esac
  rm -f /tmp/noetfield-runway-standalone-curl-probe.out
}

if ! command -v wrangler >/dev/null 2>&1; then
  echo "wrangler is not installed. Install with: npm i -g wrangler"
  exit 1
fi

cd "$SITE_DIR"

COMMAND=(wrangler pages deploy . --project-name "$PROJECT_NAME" --branch "$PROJECT_BRANCH")
if [ -n "${CF_ACCOUNT_ID:-}" ]; then
  echo "INFO: ignoring CF_ACCOUNT_ID for wrangler pages deploy v4.103 (account-id is not supported)."
fi

VERIFIER_FILE="${SITE_DIR}/verifier.json"
VERIFIER_FILE_TEXT="${SITE_DIR}/verifier.txt"
VERIFIER_HTML="${SITE_DIR}/verifier.html"
VERIFICATION_FILE="${SITE_DIR}/verification.json"

VERIFIER_COMMIT_FULL="unknown"
VERIFIER_COMMIT_SHORT="unknown"
if git -C "$SITE_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  VERIFIER_COMMIT_FULL="$(git -C "$SITE_DIR" rev-parse HEAD 2>/dev/null || echo unknown)"
  VERIFIER_COMMIT_SHORT="$(git -C "$SITE_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
fi

if [ "$AUTH_MODE" = "token" ]; then
  token_from_env="${CLOUDFLARE_API_TOKEN:-${CF_API_TOKEN:-}}"

  token_from_env="$(normalize_token "$token_from_env")"

  if is_invalid_token_shape "$token_from_env"; then
    echo "ERROR: token shape invalid."
    echo "Use a raw API token only (for example: CF-xxxxx) with no angle brackets, no quotes, and no leading/trailing spaces."
    echo "Example: export CLOUDFLARE_API_TOKEN=xxxxxx"
    exit 1
  fi

  export CF_API_TOKEN="$token_from_env"
  export CLOUDFLARE_API_TOKEN="$token_from_env"

  echo "INFO: using CLOUDFLARE_API_TOKEN from environment (token mode)"
elif [ "$AUTH_MODE" = "oauth" ]; then
  if [ -n "${CLOUDFLARE_API_TOKEN:-}" ] || [ -n "${CF_API_TOKEN:-}" ]; then
    unset CLOUDFLARE_API_TOKEN
    unset CF_API_TOKEN
    echo "INFO: forcing OAuth mode, API token env vars ignored"
  fi
else
  if [ -n "${CLOUDFLARE_API_TOKEN:-}" ] || [ -n "${CF_API_TOKEN:-}" ]; then
    echo "INFO: using CLOUDFLARE_API_TOKEN from environment (auth mode: $AUTH_MODE)"
  fi
fi

if [ -n "$COMMIT_DIRTY" ]; then
  COMMAND+=(--commit-dirty "$COMMIT_DIRTY")
elif [ "$(git -C "$SITE_DIR" status --porcelain 2>/dev/null | wc -l)" -gt 0 ]; then
  COMMAND+=(--commit-dirty=true)
fi

if [ -n "${CLOUDFLARE_PAGES_CUSTOM_DOMAIN:-}" ]; then
  echo "INFO: Set custom domain in Cloudflare dashboard: $CLOUDFLARE_PAGES_CUSTOM_DOMAIN"
fi

RUNWAY_MODE_RAW="${RUNWAY_MODE:-${RUNWAY_API_MODE:-${RUNWAY_STATE:-demo}}}"
RUNWAY_MODE="$(normalize_mode "$RUNWAY_MODE_RAW")"
RUNWAY_API_BASE_URL="${RUNWAY_API_BASE_URL:-${RUNWAY_API_BASE:-}}"
RUNWAY_API_BASE_URL="${RUNWAY_API_BASE_URL%/}"
RUNWAY_API_BASE_URL_DISPLAY="${RUNWAY_API_BASE_URL:-not_configured}"
RUNWAY_CONTRACT_VERSION="${RUNWAY_CONTRACT_VERSION:-runway.v1}"
LIVE_BACKEND_STATUS="$(detect_backend_status "$RUNWAY_API_BASE_URL")"
if [ "${LIVE_BACKEND_STATUS}" = "connected" ]; then
  LIVE_BACKEND_CONNECTED=true
else
  LIVE_BACKEND_CONNECTED=false
fi
DEPLOYMENT_ID="${CLOUDFLARE_PAGES_DEPLOYMENT_ID:-${CLOUDFLARE_PAGES_DEPLOYMENT_ID_FILE:-unknown}}"
if [ "$DEPLOYMENT_ID" = "${CLOUDFLARE_PAGES_DEPLOYMENT_ID_FILE:-unknown}" ]; then
  DEPLOYMENT_ID="unknown"
fi
DEPLOYMENT_URL="https://${PROJECT_NAME}.pages.dev"

FRONTEND_ARTIFACT_SHA256="$(compute_artifact_sha256)"
SOURCE_REPO="$(normalize_github_repo_url "$(git -C "$SITE_DIR" config --get remote.origin.url 2>/dev/null || true)")"
COMMIT_URL="unknown"
if [ "$VERIFIER_COMMIT_FULL" != "unknown" ] && [ "$SOURCE_REPO" != "unknown" ]; then
  COMMIT_URL="${SOURCE_REPO}/tree/${VERIFIER_COMMIT_FULL}"
fi

if [ "${RUNWAY_API_BASE_URL}" != "" ]; then
  RUNWAY_RUNTIME_ATTESTATION_URL="${RUNWAY_API_BASE_URL%/}/v1/runway/runtime"
else
  RUNWAY_RUNTIME_ATTESTATION_URL="not_configured"
fi

HDIR_RELEASE_SHA="${HDIR_RELEASE_SHA:-}"
if [ -z "$HDIR_RELEASE_SHA" ]; then
  HDIR_ROOT_CANDIDATE="$(resolve_repo_directory "$SITE_DIR" "NOETFIELD-RUNWAY")"
  if [ -n "$HDIR_ROOT_CANDIDATE" ] && git -C "${HDIR_ROOT_CANDIDATE}/noetfield-hdir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    HDIR_RELEASE_SHA="$(git -C "${HDIR_ROOT_CANDIDATE}/noetfield-hdir" rev-parse HEAD 2>/dev/null || echo unknown)"
  else
    HDIR_RELEASE_SHA="unknown"
  fi
elif [ "$HDIR_RELEASE_SHA" = "" ]; then
  HDIR_RELEASE_SHA="unknown"
fi

RUNWAY_KERNEL_REPO_DIR="${RUNWAY_KERNEL_REPO_DIR:-}"
if [ -z "$RUNWAY_KERNEL_REPO_DIR" ]; then
  RUNWAY_KERNEL_REPO_DIR="$(resolve_repo_directory "$SITE_DIR" "NOETFIELD-RUNWAY")"
fi
RUNWAY_KERNEL_RELEASE_SHA="${RUNWAY_KERNEL_RELEASE_SHA:-}"
if [ -z "${RUNWAY_KERNEL_RELEASE_SHA}" ]; then
  RUNWAY_KERNEL_RELEASE_SHA="$(repo_sha "${RUNWAY_KERNEL_REPO_DIR}")"
fi
RUNWAY_KERNEL_BRANCH="${RUNWAY_KERNEL_BRANCH:-$(repo_branch "${RUNWAY_KERNEL_REPO_DIR}")}"
RUNWAY_KERNEL_REPO="$(normalize_github_repo_url "$(git -C "${RUNWAY_KERNEL_REPO_DIR}" config --get remote.origin.url 2>/dev/null || true)")"
if [ "${RUNWAY_KERNEL_REPO}" = "unknown" ]; then
  RUNWAY_KERNEL_REPO="${RUNWAY_KERNEL_REPO:-unknown}"
fi
if [ "${RUNWAY_KERNEL_RELEASE_SHA}" = "unknown" ] || [ "${RUNWAY_KERNEL_REPO}" = "unknown" ]; then
  RUNWAY_KERNEL_COMMIT_URL="unknown"
else
  RUNWAY_KERNEL_COMMIT_URL="${RUNWAY_KERNEL_REPO}/tree/${RUNWAY_KERNEL_RELEASE_SHA}"
fi
RUNWAY_KERNEL_DEPLOYMENT_ID="${RUNWAY_KERNEL_DEPLOYMENT_ID:-unknown}"

echo "INFO: deploying ${PROJECT_NAME} (${PROJECT_BRANCH} / ${DEFAULT_ENV})"

# Emit browser bootstrap so window.__RUNWAY__ is LIVE without query-string secrets.
cat > "$SITE_DIR/runway-bootstrap.js" <<EOF
(function (root) {
  root.RUNWAY_MODE = "${RUNWAY_MODE}";
  root.RUNWAY_API_BASE_URL = "${RUNWAY_API_BASE_URL}";
  root.RUNWAY_CONTRACT_VERSION = "${RUNWAY_CONTRACT_VERSION}";
  root.RUNWAY_TENANT_ID = "${RUNWAY_TENANT_ID:-tenant-runway-staging}";
  root.__RUNWAY__ = {
    mode: root.RUNWAY_MODE,
    apiBaseUrl: root.RUNWAY_API_BASE_URL,
    contractVersion: root.RUNWAY_CONTRACT_VERSION,
    tenantId: root.RUNWAY_TENANT_ID
  };
})(window);
EOF

cat > "$VERIFIER_FILE" <<EOF
{
  "schema_version": "runway-frontend-attestation.v1",
  "attestation_scope": "frontend-deployment-only",
  "project": "${PROJECT_NAME}",
  "product": "noetfield-runway",
  "branch": "${PROJECT_BRANCH}",
  "environment": "${DEFAULT_ENV}",
  "commit": {
    "full": "${VERIFIER_COMMIT_FULL}",
    "short": "${VERIFIER_COMMIT_SHORT}"
  },
  "source_repository": "${SOURCE_REPO}",
  "commit_url": "${COMMIT_URL}",
  "runtime": "cloudflare-pages-standalone",
  "deployed_at_utc": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "deployment_id": "${DEPLOYMENT_ID}",
  "deployment_url": "${DEPLOYMENT_URL}",
  "frontend_artifact_sha256": "${FRONTEND_ARTIFACT_SHA256}",
  "configured_mode": "${RUNWAY_MODE}",
  "runway_mode": "${RUNWAY_MODE}",
  "runway_api_base_url": "${RUNWAY_API_BASE_URL_DISPLAY}",
  "runway_api_base_url_configured": "${RUNWAY_API_BASE_URL_DISPLAY}",
  "runway_contract_versions": {
    "frontend": "${RUNWAY_CONTRACT_VERSION}",
    "kernel": "runway.v1"
  },
  "runway_kernel_runtime_attestation_url": "${RUNWAY_RUNTIME_ATTESTATION_URL}",
  "runway_runtime_connection_status": "${LIVE_BACKEND_STATUS}",
  "live_backend_connected": ${LIVE_BACKEND_CONNECTED},
  "live_backend_status": "${LIVE_BACKEND_STATUS}",
  "runway_runtime_attestation_url": "${RUNWAY_RUNTIME_ATTESTATION_URL}",
  "runway_contracts": {
    "runtime": "GET /v1/runway/runtime",
    "receipt": "GET /v1/runway/runs/:runId/receipt",
    "verify": "POST /v1/runway/receipts/verify"
  },
  "runway_v1": "${RUNWAY_CONTRACT_VERSION}",
  "runway_kernel_deployment_id": "${RUNWAY_KERNEL_DEPLOYMENT_ID}",
  "hdir_release_sha": "${HDIR_RELEASE_SHA}",
  "runway_kernel_repository": "${RUNWAY_KERNEL_REPO}",
  "runway_kernel_branch": "${RUNWAY_KERNEL_BRANCH}",
  "runway_kernel_release_sha": "${RUNWAY_KERNEL_RELEASE_SHA}",
  "runway_kernel_commit_url": "${RUNWAY_KERNEL_COMMIT_URL}",
  "attestation_signature_scope": "This file identifies frontend deployment identity only; kernel truth is authoritative in Project Kernel.",
  "expected_mode": "${RUNWAY_MODE}",
  "verifier_page": "${DEPLOYMENT_URL}/verifier.json",
  "verification_contract": {
    "path": "GET /v1/runway/runtime",
    "path_receipt": "GET /v1/runway/runs/:runId/receipt",
    "path_receipts_verify": "POST /v1/runway/receipts/verify"
  },
  "signature": null,
  "public_key": null,
  "signature_algorithm": null
}
EOF

cat > "$VERIFIER_FILE_TEXT" <<EOF
attestation_scope=frontend-deployment-only
schema_version=runway-frontend-attestation.v1
project=${PROJECT_NAME}
product=noetfield-runway
branch=${PROJECT_BRANCH}
environment=${DEFAULT_ENV}
commit_full=${VERIFIER_COMMIT_FULL}
commit_short=${VERIFIER_COMMIT_SHORT}
commit_url=${COMMIT_URL}
source_repository=${SOURCE_REPO}
runtime=cloudflare-pages-standalone
deployed_at_utc="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
deployment_id=${DEPLOYMENT_ID}
deployment_url=${DEPLOYMENT_URL}
frontend_artifact_sha256=${FRONTEND_ARTIFACT_SHA256}
configured_mode=${RUNWAY_MODE}
runway_mode=${RUNWAY_MODE}
runway_api_base_url=${RUNWAY_API_BASE_URL_DISPLAY}
runway_api_base_url_configured=${RUNWAY_API_BASE_URL_DISPLAY}
runway_contracts_runtime=GET /v1/runway/runtime
runway_contracts_receipt=GET /v1/runway/runs/:runId/receipt
runway_contracts_verify=POST /v1/runway/receipts/verify
runway_contract_frontend=${RUNWAY_CONTRACT_VERSION}
runway_contract_kernel=runway.v1
runway_v1=${RUNWAY_CONTRACT_VERSION}
runway_kernel_deployment_id=${RUNWAY_KERNEL_DEPLOYMENT_ID}
runway_kernel_runtime_attestation_url=${RUNWAY_RUNTIME_ATTESTATION_URL}
live_backend_status=${LIVE_BACKEND_STATUS}
runway_runtime_connection_status=${LIVE_BACKEND_STATUS}
live_backend_connected=${LIVE_BACKEND_CONNECTED}
runway_runtime_attestation_url=${RUNWAY_RUNTIME_ATTESTATION_URL}
hdir_release_sha=${HDIR_RELEASE_SHA}
runway_kernel_repository=${RUNWAY_KERNEL_REPO}
runway_kernel_branch=${RUNWAY_KERNEL_BRANCH}
runway_kernel_release_sha=${RUNWAY_KERNEL_RELEASE_SHA}
runway_kernel_commit_url=${RUNWAY_KERNEL_COMMIT_URL}
attestation_signature_scope=frontend-deployment-only-identity-no-hdir-proof
expected_mode=${RUNWAY_MODE}
signature=null
public_key=null
signature_algorithm=null
EOF

cat > "$VERIFIER_HTML" <<EOF
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Noetfield Runway Verifier</title>
  </head>
  <body>
    <pre id="verifier-payload">{
  \"schema_version\": \"runway-frontend-attestation.v1\",
  \"attestation_scope\": \"frontend-deployment-only\",
  \"project\": \"${PROJECT_NAME}\",
  \"product\": \"noetfield-runway\",
  \"branch\": \"${PROJECT_BRANCH}\",
  \"environment\": \"${DEFAULT_ENV}\",
  \"commit\": {
    \"full\": \"${VERIFIER_COMMIT_FULL}\",
    \"short\": \"${VERIFIER_COMMIT_SHORT}\"
  },
  \"source_repository\": \"${SOURCE_REPO}\",
  \"commit_url\": \"${COMMIT_URL}\",
  \"runtime\": \"cloudflare-pages-standalone\",
  \"deployed_at_utc\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
  \"deployment_id\": \"${DEPLOYMENT_ID}\",
  \"deployment_url\": \"${DEPLOYMENT_URL}\",
  \"frontend_artifact_sha256\": \"${FRONTEND_ARTIFACT_SHA256}\",
  \"configured_mode\": \"${RUNWAY_MODE}\",
  \"runway_mode\": \"${RUNWAY_MODE}\",
  \"runway_api_base_url\": \"${RUNWAY_API_BASE_URL_DISPLAY}\",
  \"runway_api_base_url_configured\": \"${RUNWAY_API_BASE_URL_DISPLAY}\",
  \"runway_contracts\": {
    \"runtime\": \"GET /v1/runway/runtime\",
    \"receipt\": \"GET /v1/runway/runs/:runId/receipt\",
    \"verify\": \"POST /v1/runway/receipts/verify\"
  },
  \"runway_v1\": \"${RUNWAY_CONTRACT_VERSION}\",
  \"runway_kernel_deployment_id\": \"${RUNWAY_KERNEL_DEPLOYMENT_ID}\",
  \"runway_contract_versions\": {
    \"frontend\": \"${RUNWAY_CONTRACT_VERSION}\",
    \"kernel\": \"runway.v1\"
  },
  \"runway_kernel_runtime_attestation_url\": \"${RUNWAY_RUNTIME_ATTESTATION_URL}\",
  \"runway_runtime_connection_status\": \"${LIVE_BACKEND_STATUS}\",
  \"live_backend_connected\": ${LIVE_BACKEND_CONNECTED},
  \"live_backend_status\": \"${LIVE_BACKEND_STATUS}\",
  \"runway_runtime_attestation_url\": \"${RUNWAY_RUNTIME_ATTESTATION_URL}\",
  \"hdir_release_sha\": \"${HDIR_RELEASE_SHA}\",
  \"runway_kernel_repository\": \"${RUNWAY_KERNEL_REPO}\",
  \"runway_kernel_branch\": \"${RUNWAY_KERNEL_BRANCH}\",
  \"runway_kernel_release_sha\": \"${RUNWAY_KERNEL_RELEASE_SHA}\",
  \"runway_kernel_commit_url\": \"${RUNWAY_KERNEL_COMMIT_URL}\",
  \"attestation_signature_scope\": \"This file identifies frontend deployment identity only; backend HDIR truth is kernel-authoritative.\",
  \"expected_mode\": \"${RUNWAY_MODE}\",
  \"signature\": null,
  \"public_key\": null,
  \"signature_algorithm\": null
}</pre>
  </body>
</html>
EOF

cat > "$VERIFICATION_FILE" <<EOF
{
  "schema_version": "runway-frontend-verification.v1",
  "attestation_scope": "frontend-deployment-only",
  "project": "${PROJECT_NAME}",
  "branch": "${PROJECT_BRANCH}",
  "environment": "${DEFAULT_ENV}",
  "commit": {
    "full": "${VERIFIER_COMMIT_FULL}",
    "short": "${VERIFIER_COMMIT_SHORT}"
  },
  "source_repository": "${SOURCE_REPO}",
  "commit_url": "${COMMIT_URL}",
  "runtime": "cloudflare-pages-standalone",
  "deployed_at_utc": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "deployment_id": "${DEPLOYMENT_ID}",
  "deployment_url": "${DEPLOYMENT_URL}",
  "frontend_artifact_sha256": "${FRONTEND_ARTIFACT_SHA256}",
  "configured_mode": "${RUNWAY_MODE}",
  "runway_mode": "${RUNWAY_MODE}",
  "runway_api_base_url": "${RUNWAY_API_BASE_URL_DISPLAY}",
  "runway_api_base_url_configured": "${RUNWAY_API_BASE_URL_DISPLAY}",
  "runway_contract_versions": {
    "frontend": "${RUNWAY_CONTRACT_VERSION}",
    "kernel": "runway.v1"
  },
  "runway_contracts": {
    "runtime": "GET /v1/runway/runtime",
    "receipt": "GET /v1/runway/runs/:runId/receipt",
    "verify": "POST /v1/runway/receipts/verify"
  },
  "runway_v1": "${RUNWAY_CONTRACT_VERSION}",
  "runway_kernel_deployment_id": "${RUNWAY_KERNEL_DEPLOYMENT_ID}",
  "runway_kernel_runtime_attestation_url": "${RUNWAY_RUNTIME_ATTESTATION_URL}",
  "runway_runtime_connection_status": "${LIVE_BACKEND_STATUS}",
  "live_backend_connected": ${LIVE_BACKEND_CONNECTED},
  "live_backend_status": "${LIVE_BACKEND_STATUS}",
  "runway_runtime_attestation_url": "${RUNWAY_RUNTIME_ATTESTATION_URL}",
  "hdir_release_sha": "${HDIR_RELEASE_SHA}",
  "runway_kernel_repository": "${RUNWAY_KERNEL_REPO}",
  "runway_kernel_branch": "${RUNWAY_KERNEL_BRANCH}",
  "runway_kernel_release_sha": "${RUNWAY_KERNEL_RELEASE_SHA}",
  "runway_kernel_commit_url": "${RUNWAY_KERNEL_COMMIT_URL}",
  "attestation_signature_scope": "This file identifies frontend deployment identity only; backend HDIR truth is kernel-authoritative.",
  "expected_mode": "${RUNWAY_MODE}",
  "signature": null,
  "public_key": null,
  "signature_algorithm": null
}
EOF

"${COMMAND[@]}"

echo "VERIFIER CHECK (json): ${DEPLOYMENT_URL}/verifier.json"
echo "VERIFIER CHECK (txt fallback): ${DEPLOYMENT_URL}/verifier.txt"
echo "VERIFIER CHECK (html fallback): ${DEPLOYMENT_URL}/verifier.html"
echo "VERIFIER CHECK (runtime): ${DEPLOYMENT_URL}/v1/runway/runtime"
