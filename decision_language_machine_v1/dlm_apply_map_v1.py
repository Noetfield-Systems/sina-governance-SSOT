#!/usr/bin/env python3
"""Submit/apply map — only after decisions are validated."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dlm_core_v1 import ProcessedItem

SKIP_KEYS = {
    "schema", "note", "summary", "validated", "partial_batch", "form_edition",
    "clusters", "founder_facts", "advisor_clusters", "machine_queue_ids", "deferred_ids",
}


def load_validated_picks(path: Path | None) -> dict[str, str]:
    if not path or not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    picks: dict[str, str] = {}

    if isinstance(data, dict) and "picks" in data:
        raw = data["picks"]
        if isinstance(raw, list):
            for row in raw:
                if isinstance(row, dict) and "id" in row and "pick" in row:
                    picks[str(row["id"])] = str(row["pick"])
            return picks
        if isinstance(raw, dict):
            return {str(k): str(v) for k, v in raw.items()}

    if isinstance(data, dict) and "decisions" in data:
        for _cid, dec in data["decisions"].items():
            if not isinstance(dec, dict):
                continue
            pick = str(dec.get("pick") or "")
            for rid in dec.get("row_ids") or []:
                picks[str(rid)] = pick
        return picks

    if isinstance(data, dict):
        return {
            str(k): str(v) for k, v in data.items()
            if not str(k).startswith("_") and k not in SKIP_KEYS
        }
    return {}


def build_apply_map(
    processed: list[ProcessedItem],
    validated_picks: dict[str, str],
    *,
    partial_batch: bool = True,
    target_form: str = "FORM_OFFICIAL",
) -> dict[str, Any]:
    unvalidated = [
        p.item.id for p in processed
        if p.classification in {"ADVISOR_REVIEW", "FOUNDER_FACT"} and p.item.id not in validated_picks
    ]
    if unvalidated and not partial_batch:
        return {
            "schema": "decision_language_machine_apply_map_v1",
            "status": "BLOCKED_UNVALIDATED",
            "reason": "Apply map requires validated advisor/founder picks",
            "missing_ids": unvalidated,
        }

    picks_out = [{"id": pid, "pick": pick} for pid, pick in sorted(validated_picks.items())]
    machine_closed = [
        p.item.id for p in processed
        if p.classification == "MACHINE_VALIDATABLE" and p.item.id not in validated_picks
    ]

    return {
        "schema": "decision_language_machine_apply_map_v1",
        "status": "READY" if picks_out else "EMPTY",
        "target_form": target_form,
        "partial_batch": partial_batch,
        "pick_count": len(picks_out),
        "picks": picks_out,
        "machine_closed_without_founder": machine_closed,
        "deferred_ids": [p.item.id for p in processed if p.classification == "DEFER"],
        "note": "Submit map is downstream of validation — never auto-submit FORM_OFFICIAL",
    }

