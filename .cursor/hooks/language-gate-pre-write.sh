#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
python3 "$ROOT/.cursor/hooks/language_gate_pre_write_v1.py" "$ROOT"
