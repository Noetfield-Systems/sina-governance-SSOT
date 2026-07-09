from . import config as cfg


def _registry_entry(registry_entry):
    return registry_entry or {}


def _owner(registry_entry):
    return _registry_entry(registry_entry).get("owner", "")


def is_deterministic_eligible(registry_entry):
    """True when registry row is a non-Copilot deterministic surface with model:none policy."""
    entry = _registry_entry(registry_entry)
    owner = entry.get("owner", "")
    if owner not in cfg.DETERMINISTIC_OWNERS:
        return False
    if entry.get("model_policy") != "model:none":
        return False
    if entry.get("class") not in cfg.ALLOWED_DETERMINISTIC_CLASSES:
        return False
    return True


def _evaluate_model(observed, registry_entry):
    model_raw = observed.get("observed_model")
    if model_raw is None:
        model_raw = ""
    model_norm = model_raw.strip().lower()
    owner = _owner(registry_entry)

    if model_norm in cfg.ALLOWED_MODEL_NAMES:
        return True, []

    if model_norm in cfg.KNOWN_FORBIDDEN_MODELS:
        return False, [f"observed_model '{model_raw}' is on the known-forbidden list."]

    if model_norm in cfg.DETERMINISTIC_MODEL_NONE_VALUES:
        if is_deterministic_eligible(registry_entry):
            return True, ["Deterministic workflow: observed_model model:none matches registry model_policy."]
        return None, [
            f"observed_model '{model_raw}' (model:none) is only allowed for deterministic "
            f"non-Copilot owners with registry model_policy model:none."
        ]

    if model_norm in {"", "unknown"}:
        if owner in cfg.COPILOT_UI_OWNERS:
            return None, [
                f"observed_model '{model_raw}' is empty/unknown — Copilot UI attestation required."
            ]
        return None, ["observed_model is empty - cannot attest without an actual observed value."]

    if owner in cfg.COPILOT_UI_OWNERS:
        return None, [
            f"observed_model '{model_raw}' is not recognized — Copilot-owned workflow requires UI attestation (BLOCKED)."
        ]

    return None, [
        f"observed_model '{model_raw}' is not recognized as allowed or forbidden - unknown model."
    ]


def _evaluate_effort(observed, registry_entry, model_norm):
    effort_raw = observed.get("observed_effort")
    if effort_raw is None:
        effort_raw = ""
    effort_norm = effort_raw.strip().lower()
    owner = _owner(registry_entry)
    reasons = []

    if effort_norm in cfg.FORBIDDEN_EFFORT:
        reasons.append(f"observed_effort '{effort_raw}' is forbidden by default.")
        return False, reasons

    deterministic_none = (
        is_deterministic_eligible(registry_entry)
        and model_norm in cfg.DETERMINISTIC_MODEL_NONE_VALUES
    )

    if deterministic_none and effort_norm in cfg.DETERMINISTIC_EFFORT_OK:
        if effort_norm == "":
            reasons.append("observed_effort empty — acceptable for model:none deterministic surface.")
        return True, reasons

    if effort_norm == "low":
        return True, reasons

    if effort_norm == "medium":
        if observed.get("evidence_note"):
            reasons.append(
                "observed_effort is medium - allowed only because an exception reason was logged in evidence_note."
            )
            return True, reasons
        reasons.append(
            "observed_effort is medium with no evidence_note - medium requires a logged exception reason."
        )
        return False, reasons

    if effort_norm == "":
        if owner in cfg.COPILOT_UI_OWNERS:
            reasons.append("observed_effort is empty - Copilot UI attestation required.")
        else:
            reasons.append("observed_effort is empty - cannot attest without an actual observed value.")
        return False, reasons

    reasons.append(f"observed_effort '{effort_raw}' is not recognized for this workflow type.")
    return False, reasons


def _evaluate_trigger(observed, registry_entry):
    trigger_raw = observed.get("observed_trigger")
    if trigger_raw is None:
        trigger_raw = ""
    trigger_norm = trigger_raw.strip().lower()
    owner = _owner(registry_entry)
    reasons = []

    if trigger_norm == "":
        reasons.append("observed_trigger is empty - cannot attest without an actual observed value.")
        return False, reasons

    if owner in cfg.COPILOT_UI_OWNERS and trigger_norm in cfg.FORBIDDEN_TRIGGERS_FOR_COPILOT:
        reasons.append(f"observed_trigger '{trigger_raw}' is forbidden for a Copilot-owned automation.")
        return False, reasons

    if is_deterministic_eligible(registry_entry):
        if trigger_norm not in cfg.VALID_DETERMINISTIC_TRIGGERS:
            reasons.append(
                f"observed_trigger '{trigger_raw}' is not a valid deterministic trigger "
                f"(expected schedule|event|manual)."
            )
            return False, reasons
        return True, reasons

    if trigger_norm in cfg.VALID_DETERMINISTIC_TRIGGERS:
        return True, reasons

    reasons.append(f"observed_trigger '{trigger_raw}' is not recognized as policy-compatible.")
    return False, reasons


def compute_verdict(observed, registry_entry=None):
    """
    Server-side verdict from observed fields. observed values are compared
    normalized; stored values remain exactly as the client sent them.

    registry_entry: workflow row from workflow_registry_v1.json (owner, class,
    trigger, model_policy) used for deterministic model:none eligibility.
    """
    owner = _owner(registry_entry)
    model_raw = observed.get("observed_model") or ""
    model_norm = model_raw.strip().lower()

    model_ok, model_reasons = _evaluate_model(observed, registry_entry)
    effort_ok, effort_reasons = _evaluate_effort(observed, registry_entry, model_norm)
    trigger_ok, trigger_reasons = _evaluate_trigger(observed, registry_entry)

    reasons = model_reasons + effort_reasons + trigger_reasons

    if model_ok is None:
        return "BLOCKED", reasons
    if model_ok and trigger_ok and effort_ok:
        return "PASS", reasons if reasons else ["Observed reality matches policy. Clean."]
    return "FAIL", reasons


# Back-compat alias for callers passing owner string only.
def compute_verdict_from_owner(observed, owner):
    return compute_verdict(observed, {"owner": owner})
