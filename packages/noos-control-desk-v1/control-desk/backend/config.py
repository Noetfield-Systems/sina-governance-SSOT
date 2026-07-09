import os
import re

REPO_ROOT = None

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")

REGISTRY_REL = os.path.join(".noos", "workflow_registry_v1.json")
DRAFT_REL = os.path.join(".noos", "registry_draft.json")
REGISTRY_DRAFT_REL = os.path.join(".noos", "workflow_registry_draft.json")
RECEIPT_SCHEMA_REL = os.path.join(".noos", "receipt_schema_v1.json")
ATTESTATION_SCHEMA_REL = os.path.join(".noos", "copilot_attestation_schema_v1.json")
CHECKER_REL = os.path.join("scripts", "check_cost_policy.py")
SYNC_SCRIPT_REL = os.path.join("scripts", "noos_integrator_sync_v1.py")
RECEIPTS_REL = "receipts"

PACKAGE_REPO = "sina-governance-SSOT"
AUDIT_STALE_MAX_DAYS = 30

ALLOWED_MODEL_NAMES = {"gpt-5-mini", "gpt-5 mini", "gpt-5-mini-low"}
DETERMINISTIC_MODEL_NONE_VALUES = {"model:none", "none", "n/a", "na"}
DETERMINISTIC_OWNERS = {"github_actions", "cloudflare_worker", "noos_integrator"}
COPILOT_UI_OWNERS = {"copilot_manual"}
ALLOWED_DETERMINISTIC_CLASSES = {"observe", "triage", "safe_fix", "verify", "deploy", "reconcile"}
VALID_DETERMINISTIC_TRIGGERS = {"schedule", "event", "manual"}
DETERMINISTIC_EFFORT_OK = {"low", "none", "n/a", "na", ""}
KNOWN_FORBIDDEN_MODELS = {
    "auto", "gpt-5.4", "gpt-5.4 mini", "gpt-5.3-codex", "auto: gpt-5.4", "auto: gpt-5.3-codex",
    "claude", "claude haiku", "claude sonnet", "claude opus", "anthropic",
    "gemini", "kimi", "mai-code", "coding agent model",
}
FORBIDDEN_EFFORT = {"high", "extra high", "unknown", "auto"}
FORBIDDEN_TRIGGERS_FOR_COPILOT = {
    "hourly", "daily", "weekly", "background", "keep awake",
    "unpinned schedule", "autopilot recurring",
}

ALLOWED_DESIRED = {
    "desired_trigger": {"manual"},
    "desired_model": {"gpt-5-mini"},
    "desired_effort": {"low"},
}

WORKFLOW_ID_RE = re.compile(r"^[a-zA-Z0-9_\-]{1,80}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# NOOS Copilot P2 — cloud writes are scope-gated (see ssot/NOOS_COPILOT_DISPATCHER_v1.md)
CLOUD_WRITE_SCOPE_GATE = {
    "rule": (
        "Cloud writes are scope-gated. Before full PASS, NOOS Copilot may publish receipts, "
        "status, drift reports, and prepare draft branches/PRs. Fleet rollout, ACTIVE promotion, "
        "direct main write, and policy/law mutation remain blocked."
    ),
    "allowed_before_full_pass": [
        "receipts",
        "status",
        "drift_reports",
        "draft_branch_pr_prep",
    ],
    "blocked_before_full_pass": [
        "fleet_rollout",
        "active_promotion",
        "direct_main_write",
        "policy_law_mutation",
        "audit_pending_registry_propagation",
    ],
}
# Unrestricted fleet/cloud propagation — not allowed before full PASS
CLOUD_WRITE_UNRESTRICTED_ALLOWED = False

RECEIPT_REQUIRED_FIELDS = [
    "action", "repo", "files_changed", "commands_run",
    "policy_pass", "errors", "timestamp", "next_machine_action",
]
