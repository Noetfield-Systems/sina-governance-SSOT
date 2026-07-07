#!/usr/bin/env python3
"""Intake — normalize messy backlogs into DecisionItem list."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from dlm_core_v1 import DecisionItem, ItemSource


def _slug_id(raw: str, idx: int) -> str:
    base = re.sub(r"[^a-zA-Z0-9._-]+", "-", raw.strip())[:40].strip("-") or f"item-{idx}"
    return base


def from_form_open_questions(rows: list[dict[str, Any]]) -> list[DecisionItem]:
    out: list[DecisionItem] = []
    for i, row in enumerate(rows):
        qid = str(row.get("id") or row.get("number") or f"row-{i+1}")
        out.append(
            DecisionItem(
                id=qid,
                raw_text=str(row.get("question") or row.get("title") or ""),
                source=ItemSource.FORM_ROW.value,
                title=str(row.get("title") or row.get("subject") or ""),
                question=str(row.get("question") or ""),
                options=[str(o) for o in row.get("options") or []],
                blocks=str(row.get("blocks") or ""),
                effect=str(row.get("effect") or ""),
                metadata={"recommended": row.get("recommended"), "reply_template": row.get("reply_template")},
            )
        )
    return out


def from_backlog_json(data: dict[str, Any]) -> list[DecisionItem]:
    if "open_questions" in data:
        return from_form_open_questions(data["open_questions"])
    items = data.get("items") or data.get("decisions") or data.get("rows") or []
    out: list[DecisionItem] = []
    for i, row in enumerate(items):
        if not isinstance(row, dict):
            out.append(
                DecisionItem(
                    id=_slug_id(str(row), i),
                    raw_text=str(row),
                    source=ItemSource.BACKLOG.value,
                )
            )
            continue
        src = str(row.get("source") or ItemSource.BACKLOG.value)
        qid = str(row.get("id") or _slug_id(row.get("text") or row.get("question") or str(i), i))
        out.append(
            DecisionItem(
                id=qid,
                raw_text=str(row.get("text") or row.get("raw_text") or row.get("question") or ""),
                source=src,
                title=str(row.get("title") or ""),
                question=str(row.get("question") or ""),
                options=[str(o) for o in row.get("options") or []],
                blocks=str(row.get("blocks") or row.get("blocks_on") or ""),
                effect=str(row.get("effect") or row.get("impact") or ""),
                metadata={k: v for k, v in row.items() if k not in {"id", "text", "question", "title"}},
            )
        )
    return out


def from_markdown_lines(text: str) -> list[DecisionItem]:
    """One bullet or numbered line = one item."""
    out: list[DecisionItem] = []
    for i, line in enumerate(text.splitlines()):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = re.sub(r"^[-*]\s+", "", line)
        line = re.sub(r"^\d+[.)]\s+", "", line)
        if len(line) < 8:
            continue
        out.append(
            DecisionItem(
                id=_slug_id(line, i),
                raw_text=line,
                source=ItemSource.BACKLOG.value,
                question=line,
            )
        )
    return out


def from_form_markdown(text: str) -> list[DecisionItem]:
    """Parse FORM_OFFICIAL-style markdown sections."""
    out: list[DecisionItem] = []
    blocks = re.split(r"\n---+\n", text)
    for block in blocks:
        block = block.strip()
        if not block or block.startswith("# ") and "##" not in block:
            continue
        m_id = re.search(r"##\s+\d+\.\s+\[([^\]]+)\]", block)
        m_title = re.search(r"##\s+\d+\.\s+\[[^\]]+\]\s+(.+)", block)
        m_q = re.search(r"^([^\n*#].+\?)\s*$", block, re.M)
        m_effect = re.search(r"\*\*Effect:\*\*\s*(.+)", block)
        m_blocks = re.search(r"\*\*Blocks:\*\*\s*(.+)", block)
        options = re.findall(r"^-\s+([A-E].+)$", block, re.M)
        if not m_id and not m_q:
            continue
        qid = m_id.group(1) if m_id else _slug_id(block, len(out))
        out.append(
            DecisionItem(
                id=qid,
                raw_text=m_q.group(1).strip() if m_q else block[:200],
                source=ItemSource.FORM_ROW.value,
                title=m_title.group(1).strip() if m_title else "",
                question=m_q.group(1).strip() if m_q else "",
                options=options,
                blocks=m_blocks.group(1).strip() if m_blocks else "",
                effect=m_effect.group(1).strip() if m_effect else "",
            )
        )
    return out


def load_items(path: Path) -> list[DecisionItem]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            return from_backlog_json({"items": data})
        if "picks" in data and isinstance(data["picks"], list):
            return from_backlog_json({"items": data["picks"]})
        return from_backlog_json(data)
    if "## 1." in text and "**Effect:**" in text:
        items = from_form_markdown(text)
        if items:
            return items
    return from_markdown_lines(text)
