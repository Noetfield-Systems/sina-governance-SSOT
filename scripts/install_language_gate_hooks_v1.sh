#!/usr/bin/env bash
# Install git pre-commit hook for language gate (local, not global git config mutation).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
mkdir -p "$ROOT/.githooks"
chmod +x "$ROOT/.githooks/pre-commit"
chmod +x "$ROOT/.cursor/hooks/"*.sh
git -C "$ROOT" config core.hooksPath .githooks
echo "OK: core.hooksPath=.githooks (language gate pre-commit active for this repo)"
