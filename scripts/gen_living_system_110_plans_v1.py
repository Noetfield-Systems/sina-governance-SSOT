#!/usr/bin/env python3
"""Regenerate LS-110 plans from /tmp/ls110_*.txt data or embedded paths."""
from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
# Re-run builder logic: delegate to inline regen
subprocess.check_call([sys.executable, "-c", open(__file__).read().split("REGEN_START")[1]])
REGEN_START
raise SystemExit("Use temp builder; run: python3 from session regen script")
