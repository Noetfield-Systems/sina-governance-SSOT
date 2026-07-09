#!/usr/bin/env python3
"""Alias entrypoint — delegates to verify_auth_surfaces_e2e_v1.py."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parent / "verify_auth_surfaces_e2e_v1.py"), run_name="__main__")
