#!/usr/bin/env python3
"""Decision language machine — core models and stage receipts."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DLM_DIR = Path(__file__).resolve().parent
RECEIPTS_DIR = DLM_DIR / "receipts"
OUTPUT_DIR = DLM_DIR / "output"

CLASSIFICATIONS = frozenset(
    {"MACHINE_VALIDATABLE", "ADVISOR_REVIEW", "FOUNDER_FACT", "DEFER", "UNCLASSIFIED"}
)

STAGES = (
    "intake",
    "plain_english",
    "term_extract",
    "dictionary_check",
    "cluster",
    "classify",
    "founder_sheet",
    "apply_map",
)


class ItemSource(str, Enum):
    FORM_ROW = "form_row"
    CHAT_FORK = "chat_fork"
    AUDIT_FINDING = "audit_finding"
    AGENT_QUESTION = "agent_question"
    BACKLOG = "backlog"
    UNKNOWN = "unknown"


@dataclass
class DecisionItem:
    """One messy input normalized to a common shape."""

    id: str
    raw_text: str
    source: str = ItemSource.UNKNOWN.value
    title: str = ""
    question: str = ""
    options: list[str] = field(default_factory=list)
    blocks: str = ""
    effect: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def key_text(self) -> str:
        return " ".join(x for x in (self.title, self.question, self.raw_text) if x).strip()

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProcessedItem:
    """Item after pipeline stages."""

    item: DecisionItem
    plain_english: str = ""
    terms: list[dict[str, Any]] = field(default_factory=list)
    dictionary_flags: list[dict[str, Any]] = field(default_factory=list)
    dictionary_fix_needed: bool = False
    classification: str = "UNCLASSIFIED"
    classification_reason: str = ""
    evidence_hint: str = ""
    cluster_id: str = ""
    cluster_name: str = ""
    validated: bool = False

    def as_dict(self) -> dict[str, Any]:
        d = self.item.as_dict()
        d.update(
            {
                "plain_english": self.plain_english,
                "terms": self.terms,
                "dictionary_flags": self.dictionary_flags,
                "dictionary_fix_needed": self.dictionary_fix_needed,
                "classification": self.classification,
                "classification_reason": self.classification_reason,
                "evidence_hint": self.evidence_hint,
                "cluster_id": self.cluster_id,
                "cluster_name": self.cluster_name,
                "validated": self.validated,
            }
        )
        return d


@dataclass
class Cluster:
    cluster_id: str
    name: str
    member_ids: list[str]
    plain_english_question: str
    controls: str
    if_unanswered: str
    hint: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id() -> str:
    return uuid.uuid4().hex[:16]


def write_stage_receipt(
    *,
    run_id: str,
    stage: str,
    decision: str,
    payload: dict[str, Any],
    input_path: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = utc_now()
    sid = hashlib.sha256(f"{run_id}{stage}{ts}".encode()).hexdigest()[:16]
    receipt: dict[str, Any] = {
        "receipt_type": "decision_language_machine_stage_receipt_v1",
        "schema": "decision_language_machine_v1",
        "run_id": run_id,
        "stage": stage,
        "time": ts,
        "scan_id": sid,
        "decision": decision,
        "input_path": input_path,
        "payload": payload,
    }
    path = RECEIPTS_DIR / f"{run_id}.{stage}.{sid}.receipt.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return path, receipt


def write_run_manifest(
    *,
    run_id: str,
    input_path: str,
    stage_receipts: list[str],
    summary: dict[str, Any],
) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema": "decision_language_machine_run_v1",
        "run_id": run_id,
        "time": utc_now(),
        "input_path": input_path,
        "stage_receipts": stage_receipts,
        "summary": summary,
    }
    path = OUTPUT_DIR / f"{run_id}.manifest.json"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return path
