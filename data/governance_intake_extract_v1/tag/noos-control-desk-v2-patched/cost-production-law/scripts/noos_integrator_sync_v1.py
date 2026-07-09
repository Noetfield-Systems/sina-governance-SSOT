#!/usr/bin/env python3
"""
noos_integrator_sync_v1.py

Real, minimal implementation of the integrator sync commands referenced by
SMART_PRODUCTION_COST_LAW_v2.md and COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md:

    python3 scripts/noos_integrator_sync_v1.py sync
    python3 scripts/noos_integrator_sync_v1.py summary --json

State lives in .noos/integrator_state.json (repo-local). This is intentionally
stdlib-only, no network, no external mirror wiring yet - it tracks *this*
repo's local sync timestamp and reports staleness. Home-mirror and cloud-mirror
fields are present in the schema but stay "unconfigured" until you point them
at a real path/endpoint - this script does not fabricate a synced mirror it
never actually checked.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STATE_PATH = os.path.join(REPO_ROOT, ".noos", "integrator_state.json")


def load_state():
    if not os.path.isfile(STATE_PATH):
        return {
            "repo_local_last_sync": None,
            "home_mirror_path": None,
            "home_mirror_last_seen": None,
            "cross_ide_ready": False,
            "sync_count": 0
        }
    with open(STATE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def cmd_sync(args):
    state = load_state()
    now = datetime.now(timezone.utc).isoformat()
    state["repo_local_last_sync"] = now
    state["sync_count"] = state.get("sync_count", 0) + 1

    # Home mirror: only report "seen" if a real configured path actually exists.
    home_mirror_path = os.environ.get("NOOS_HOME_MIRROR_PATH") or state.get("home_mirror_path")
    if home_mirror_path and os.path.isdir(home_mirror_path):
        state["home_mirror_path"] = home_mirror_path
        state["home_mirror_last_seen"] = now
    elif home_mirror_path:
        # configured but not found - stay honest, don't mark it fresh
        state["home_mirror_path"] = home_mirror_path
        # leave home_mirror_last_seen as whatever it last was; do not update to "now"

    state["cross_ide_ready"] = state.get("repo_local_last_sync") is not None
    save_state(state)
    print(json.dumps({"status": "SYNCED", "repo_local_last_sync": now}, indent=2))
    return 0


def cmd_summary(args):
    state = load_state()
    now = datetime.now(timezone.utc)

    def age_str(iso_ts):
        if not iso_ts:
            return None
        try:
            dt = datetime.fromisoformat(iso_ts)
            return round((now - dt).total_seconds() / 3600, 2)
        except ValueError:
            return None

    repo_age_h = age_str(state.get("repo_local_last_sync"))
    mirror_age_h = age_str(state.get("home_mirror_last_seen"))

    summary = {
        "repo_local": "fresh" if (repo_age_h is not None and repo_age_h < 1) else
                      ("stale" if repo_age_h is not None else "never_synced"),
        "repo_local_age_hours": repo_age_h,
        "home_mirror": "synced" if (mirror_age_h is not None and mirror_age_h < 24) else
                        ("stale" if mirror_age_h is not None else "unconfigured"),
        "home_mirror_age_hours": mirror_age_h,
        "cross_ide_ready": state.get("cross_ide_ready", False),
        "sync_count": state.get("sync_count", 0)
    }

    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        for k, v in summary.items():
            print(f"{k}: {v}")
    return 0


def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("sync")

    summary_parser = sub.add_parser("summary")
    summary_parser.add_argument("--json", action="store_true")

    args = parser.parse_args()

    if args.command == "sync":
        sys.exit(cmd_sync(args))
    elif args.command == "summary":
        sys.exit(cmd_summary(args))


if __name__ == "__main__":
    main()
