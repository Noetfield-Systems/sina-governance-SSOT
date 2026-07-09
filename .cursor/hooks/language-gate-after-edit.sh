#!/usr/bin/env bash
# Cursor afterFileEdit — mandatory language gate (regex + agent plain-English pass).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
input="$(cat)"
file="$(python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('file_path') or d.get('path') or '')" <<<"$input")"

case "$file" in
  *.md|*.mdc|*.txt|*.json)
    ;;
  *)
    exit 0
    ;;
esac

case "$file" in
  *node_modules/*|*.min.js|language_gate/receipts/*)
    exit 0
    ;;
esac

cd "$ROOT"
python3 language_gate/language_gate_pipeline_v1.py "$file" --surface auto --write
exit $?
