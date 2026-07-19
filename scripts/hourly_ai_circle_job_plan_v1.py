#!/usr/bin/env python3
"""Hourly AI circle job plan artifact (assist-only; HOLD preserved)."""
from __future__ import annotations

import json
from typing import Any

SCHEMA = "nf.hourly-ai-circle-job-plan.v1"
ALLOWED_JOBS = {
    "commissioning_tick",
    "motor_job",
    "repair_run",
    "live_model_smoke",
}


def build_plan(
    job_id: str,
    receipt_id: str,
    why: str = "",
    hold: str = "HOLD",
) -> dict[str, Any]:
    if job_id not in ALLOWED_JOBS:
        raise ValueError(f"job_id_not_allowlisted:{job_id}")
    if hold != "HOLD":
        raise ValueError("hold_must_remain_HOLD")
    return {
        "schema": SCHEMA,
        "job_id": job_id,
        "receipt_id": receipt_id,
        "why": why,
        "mode": "ASSIST_ONLY",
        "hold": hold,
        "forbidden": ["merge", "deploy", "authority_change", "secret_change"],
        "closed_loop": [
            "Observe",
            "Detect",
            "Plan",
            "DispatchOrDraft",
            "IndependentVerify",
            "RepairByNewDraftOnly",
            "ReObserve",
        ],
    }


def main() -> None:
    plan = build_plan("commissioning_tick", "builder-20260719020917-9b1351b5", "empty_implementer_payload")
    print(json.dumps(plan, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
