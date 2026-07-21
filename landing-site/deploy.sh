#!/usr/bin/env bash
set -euo pipefail

PROJECT_NAME="${CLOUDFLARE_PAGES_PROJECT_NAME:-noetfield-runway-standalone}"
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

if ! command -v wrangler >/dev/null 2>&1; then
  echo "wrangler is not installed. Install with: npm i -g wrangler"
  exit 1
fi

cd "$SITE_DIR"

COMMAND=(wrangler pages deploy . --project-name "$PROJECT_NAME" --branch "$PROJECT_BRANCH")

VERIFIER_FILE="${SITE_DIR}/verifier.json"
VERIFIER_FILE_TEXT="${SITE_DIR}/verifier.txt"
VERIFIER_HTML="${SITE_DIR}/verifier.html"
VERIFIER_COMMIT="unknown"

if git -C "$SITE_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  VERIFIER_COMMIT="$(git -C "$SITE_DIR" rev-parse --short HEAD 2>/dev/null || echo unknown)"
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

echo "INFO: deploying ${PROJECT_NAME} (${PROJECT_BRANCH} / ${DEFAULT_ENV})"

cat > "$VERIFIER_FILE" <<EOF
{
  "project": "${PROJECT_NAME}",
  "branch": "${PROJECT_BRANCH}",
  "environment": "${DEFAULT_ENV}",
  "commit": "${VERIFIER_COMMIT}",
  "runtime": "cloudflare-pages-standalone",
  "deployed_at_utc": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "verifier_page": "https://${PROJECT_NAME}.pages.dev/verifier.json",
  "expected_mode": "${AUTH_MODE}"
}
EOF

cat > "$VERIFIER_FILE_TEXT" <<EOF
${PROJECT_NAME}|${PROJECT_BRANCH}|${DEFAULT_ENV}|${VERIFIER_COMMIT}|$(date -u +"%Y-%m-%dT%H:%M:%SZ")|${AUTH_MODE}
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
  \"project\": \"${PROJECT_NAME}\",
  \"branch\": \"${PROJECT_BRANCH}\",
  \"environment\": \"${DEFAULT_ENV}\",
  \"commit\": \"${VERIFIER_COMMIT}\",
  \"runtime\": \"cloudflare-pages-standalone\",
  \"deployed_at_utc\": \"$(date -u +"%Y-%m-%dT%H:%M:%SZ")\",
  \"verifier_page\": \"https://${PROJECT_NAME}.pages.dev/verifier.html\",
  \"expected_mode\": \"${AUTH_MODE}\"
}</pre>
  </body>
</html>
EOF

"${COMMAND[@]}"

echo "VERIFIER CHECK (json): https://${PROJECT_NAME}.pages.dev/verifier.json"
echo "VERIFIER CHECK (txt fallback): https://${PROJECT_NAME}.pages.dev/verifier.txt"
echo "VERIFIER CHECK (html fallback): https://${PROJECT_NAME}.pages.dev/verifier.html"
