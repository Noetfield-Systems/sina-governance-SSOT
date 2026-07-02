#!/usr/bin/env python3
"""Paths and helpers for Phase 3 autonomous brain deploy controls."""
from __future__ import annotations

import json
from pathlib import Path

AUTONOMOUS_DEPLOY_FLAG = Path.home() / ".sina/brain-autonomous-deploy-v1.flag"
AUTONOMOUS_HOLD_FLAG = Path.home() / ".sina/enforcement/brain-autonomous-hold-v1.flag"
MUTATION_TRIALS_PATH = Path.home() / "Desktop/SourceA/data/sourcea-phase2-mutation-trials-v1.json"


def autonomous_deploy_enabled() -> bool:
    return AUTONOMOUS_DEPLOY_FLAG.is_file()


def autonomous_hold_active() -> bool:
    return AUTONOMOUS_HOLD_FLAG.is_file()


def set_autonomous_hold(*, reason: str) -> None:
    AUTONOMOUS_HOLD_FLAG.parent.mkdir(parents=True, exist_ok=True)
    payload = {"active": True, "reason": reason}
    AUTONOMOUS_HOLD_FLAG.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def clear_autonomous_hold() -> None:
    if AUTONOMOUS_HOLD_FLAG.is_file():
        AUTONOMOUS_HOLD_FLAG.unlink()


def mutation_trials_enabled(sourcea_root: Path | None = None) -> bool:
    path = MUTATION_TRIALS_PATH
    if sourcea_root:
        candidate = sourcea_root / "data/sourcea-phase2-mutation-trials-v1.json"
        if candidate.is_file():
            path = candidate
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    value = data.get("enabled")
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes")
