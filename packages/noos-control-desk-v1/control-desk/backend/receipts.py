import json
import os
from datetime import datetime, timezone

from . import config as cfg


def build_receipt(
    action,
    *,
    files_changed=None,
    commands_run=None,
    policy_pass=False,
    errors=None,
    next_machine_action="",
    extra=None,
):
    receipt = {
        "action": action,
        "repo": cfg.PACKAGE_REPO,
        "files_changed": files_changed or [],
        "commands_run": commands_run or [],
        "policy_pass": bool(policy_pass),
        "errors": errors or [],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "next_machine_action": next_machine_action,
    }
    if extra:
        receipt.update(extra)
    missing = [f for f in cfg.RECEIPT_REQUIRED_FIELDS if f not in receipt]
    if missing:
        raise ValueError(f"receipt missing required fields: {missing}")
    return receipt


def write_receipt(name, receipt):
    os.makedirs(os.path.join(cfg.REPO_ROOT, cfg.RECEIPTS_REL), exist_ok=True)
    path = os.path.join(cfg.REPO_ROOT, cfg.RECEIPTS_REL, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
    return os.path.relpath(path, cfg.REPO_ROOT)
