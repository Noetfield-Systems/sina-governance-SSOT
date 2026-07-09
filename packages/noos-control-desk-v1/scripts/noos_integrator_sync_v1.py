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
DEFAULT_HOME_MIRROR = os.path.expanduser("~/.sina/noos-integrator-state-v1.json")

CLOUD_WRITE_SCOPE_GATE = {
    "rule": (
        "Cloud writes are scope-gated. Before full PASS, NOOS Copilot may publish receipts, "
        "status, drift reports, and prepare draft branches/PRs. Fleet rollout, ACTIVE promotion, "
        "direct main write, and policy/law mutation remain blocked."
    ),
    "allowed_before_full_pass": [
        "receipts", "status", "drift_reports", "draft_branch_pr_prep",
    ],
    "blocked_before_full_pass": [
        "fleet_rollout", "active_promotion", "direct_main_write",
        "policy_law_mutation", "audit_pending_registry_propagation",
    ],
}
CLOUD_WRITE_UNRESTRICTED_ALLOWED = False


def cloud_write_gate_payload():
    return {
        "cloud_write_scope": "gated",
        "cloud_write_unrestricted_allowed": CLOUD_WRITE_UNRESTRICTED_ALLOWED,
        "cloud_write_scope_gate": CLOUD_WRITE_SCOPE_GATE,
        "gate_note": CLOUD_WRITE_SCOPE_GATE["rule"],
    }


def cloud_mirror_readout():
    """Read-only cloud mirror status. Never writes or propagates."""
    path = os.environ.get("NOOS_CLOUD_MIRROR_STATUS_PATH", "")
    if not path or not os.path.isfile(path):
        return {
            "status": "unconfigured",
            "path": path or None,
            "last_seen": None,
            "age_hours": None,
            "cloud_write_unrestricted_allowed": CLOUD_WRITE_UNRESTRICTED_ALLOWED,
            **{k: v for k, v in cloud_write_gate_payload().items() if k != "gate_note"},
        }
    try:
        mtime = datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc).isoformat()
        age_h = round((datetime.now(timezone.utc) - datetime.fromtimestamp(os.path.getmtime(path), tz=timezone.utc)).total_seconds() / 3600, 2)
        with open(path, "r", encoding="utf-8") as f:
            payload = json.load(f)
        return {
            "status": "available",
            "path": path,
            "last_seen": mtime,
            "age_hours": age_h,
            "cloud_write_unrestricted_allowed": CLOUD_WRITE_UNRESTRICTED_ALLOWED,
            **{k: v for k, v in cloud_write_gate_payload().items() if k != "gate_note"},
            "read_only_snapshot": {"keys": list(payload.keys())[:20]} if isinstance(payload, dict) else None,
        }
    except (OSError, json.JSONDecodeError) as e:
        return {
            "status": "error",
            "path": path,
            "last_seen": None,
            "age_hours": None,
            "cloud_write_unrestricted_allowed": CLOUD_WRITE_UNRESTRICTED_ALLOWED,
            **{k: v for k, v in cloud_write_gate_payload().items() if k != "gate_note"},
            "error": str(e),
        }


def resolve_home_mirror_path(state):
    return (
        os.environ.get("NOOS_HOME_MIRROR_PATH")
        or state.get("home_mirror_path")
        or (DEFAULT_HOME_MIRROR if os.path.isfile(DEFAULT_HOME_MIRROR) else None)
    )


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

    # Home mirror: read-only freshness check when path exists.
    home_mirror_path = resolve_home_mirror_path(state)
    if home_mirror_path and os.path.isfile(home_mirror_path):
        state["home_mirror_path"] = home_mirror_path
        state["home_mirror_last_seen"] = datetime.fromtimestamp(
            os.path.getmtime(home_mirror_path), tz=timezone.utc
        ).isoformat()
    elif home_mirror_path:
        state["home_mirror_path"] = home_mirror_path

    state["cross_ide_ready"] = state.get("repo_local_last_sync") is not None
    state["cloud_write_unrestricted_allowed"] = CLOUD_WRITE_UNRESTRICTED_ALLOWED
    save_state(state)
    print(json.dumps({
        "status": "SYNCED",
        "repo_local_last_sync": now,
        **cloud_write_gate_payload(),
    }, indent=2))
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
        "home_mirror_path": state.get("home_mirror_path"),
        "cloud_mirror": cloud_mirror_readout(),
        "cross_ide_ready": state.get("cross_ide_ready", False),
        "sync_count": state.get("sync_count", 0),
        **cloud_write_gate_payload(),
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
