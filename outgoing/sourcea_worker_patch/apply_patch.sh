#!/usr/bin/env bash
set -e
if [ -z "" ]; then echo "Usage: /bin/bash /path/to/sourcea/repo"; exit 1; fi
TARGET=
mkdir -p "/skills/signal-factory-v1/tests"
cp -r /Users/sinakazemnezhad/Projects/copilot-worktrees/sina-governance-ssot/kazemnezhadsina144-dot-special-barnacle/outgoing/sourcea_worker_patch/* "/skills/signal-factory-v1/"
echo 'Files copied to' "/skills/signal-factory-v1/"
