#!/usr/bin/env python3
"""NOOS Control Desk — thin launcher for control-desk/backend/."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.server import main

if __name__ == "__main__":
    main()
