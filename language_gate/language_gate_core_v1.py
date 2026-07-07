#!/usr/bin/env python3
"""Shared language gate core — surfaces, dictionary load, regex scan."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GATE_DIR = Path(__file__).resolve().parent
DICT_PATH = GATE_DIR / "dictionary_index.json"
RECEIPTS_DIR = GATE_DIR / "receipts"

SURFACES = frozenset({"internal", "public", "website", "contract", "prompt", "receipt"})

SYNONYM_AUTOFIX = {
    r"\bmodel-agnostic\b": "vendor-neutral",
    r"\bagnostic\b(?=.{0,15}\bmodel\b)": "vendor-neutral",
    r"\bclient base\b": "governed reference environment",
    r"\bthe latest file\b": "SSOT",
}

BANNED_REGISTER = [
    r"\bwe need\b",
    r"\bdesperate\b",
    r"\brevolutionary\b",
    r"\bgame-changing\b",
    r"\bnext-gen\b",
]

OVERCLAIM_PATTERNS = [
    (r"\b100%\s*(guaranteed|verified|certified)\b", "unproven absolute claim"),
    (r"\bwe guarantee outcomes\b", "banned per Receipt public-rewrite rule"),
    (r"\bcertified\b", "banned unless schema-cited"),
    (r"\b\d{1,3}\+?\s*(clients|customers)\b", "unprovable customer roster"),
]

KNOWN_VENDOR_ALLOWLIST = {
    "cloudflare", "cloudflare workers", "cloudflare queues", "cloudflare cron",
    "supabase", "railway", "aider", "roo code", "openhands", "claude code",
    "github", "aws", "gcp", "perplexity", "cursor", "composer",
}

COMMON_WORD_ALLOWLIST = {
    "draft", "todo", "note", "warning", "important", "tbd", "n/a", "id",
    "url", "api", "faq", "ceo", "cto", "cfo", "usa", "us", "ok", "asap",
    "fyi", "eta", "utc", "pdt", "pst", "pass", "fail", "json", "yaml", "md",
    "nda", "sow", "msa",
}

LEADING_STOPWORDS = {
    "the", "a", "an", "our", "we", "this", "that", "these", "those", "under",
    "with", "for", "and", "or", "but", "in", "on", "at", "is", "are", "it",
    "its", "to", "of", "as", "by", "if", "so", "not",
}

TERM_RE = re.compile(
    r"\*\*([A-Za-z][A-Za-z0-9 \-/·≥]{1,50}?)\*\*"
    r"|\b([A-Z]{2,}(?:[ /][A-Z]{2,})*)\b"
    r"|\b((?:[A-Z][a-zA-Z]*[ \t]+){1,3}[A-Z][a-zA-Z]*)\b"
)

SURFACE_POLICY: dict[str, dict[str, bool]] = {
    "internal": {
        "block_banned": True,
        "block_overclaim": False,
        "block_private": False,
        "block_undefined": True,
        "autofix_alias": True,
        "plain_rewrite": True,
    },
    "public": {
        "block_banned": True,
        "block_overclaim": True,
        "block_private": True,
        "block_undefined": True,
        "autofix_alias": True,
        "plain_rewrite": True,
    },
    "website": {
        "block_banned": True,
        "block_overclaim": True,
        "block_private": True,
        "block_undefined": True,
        "autofix_alias": True,
        "plain_rewrite": True,
    },
    "contract": {
        "block_banned": True,
        "block_overclaim": True,
        "block_private": True,
        "block_undefined": True,
        "autofix_alias": True,
        "plain_rewrite": True,
    },
    "prompt": {
        "block_banned": True,
        "block_overclaim": False,
        "block_private": True,
        "block_undefined": True,
        "autofix_alias": True,
        "plain_rewrite": True,
    },
    "receipt": {
        "block_banned": True,
        "block_overclaim": False,
        "block_private": False,
        "block_undefined": True,
        "autofix_alias": True,
        "plain_rewrite": False,
    },
}


@dataclass
class Dictionary:
    schema: str
    terms: dict[str, dict[str, Any]]
    alias_map: dict[str, str]
    retired_terms: set[str]
    private_only: set[str]
    code_alias: set[str]
    public_phrasing: dict[str, str]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def clean_phrase(value: str | None) -> str | None:
    if not value:
        return None
    text = value.strip()
    for cut in (" Is NOT:", " Example:", " Doctrine source file:", " Public phrasing:", " ---"):
        idx = text.find(cut)
        if idx > 0:
            text = text[:idx].strip()
    return text or None


def load_dictionary(path: Path | None = None) -> Dictionary:
    path = path or DICT_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))
    terms: dict[str, dict[str, Any]] = {}
    for row in raw.get("terms") or []:
        key = str(row.get("term") or "").strip().lower()
        if key:
            terms[key] = row
    alias_map = {str(k).lower(): str(v) for k, v in (raw.get("alias_map") or raw.get("tombstone_map") or {}).items()}
    retired = {str(t).lower() for t in (raw.get("retired_terms") or [])}
    for alias in alias_map:
        retired.add(alias)
    private_only = {str(t).lower() for t in (raw.get("private_only") or [])}
    code_alias = {str(t).lower() for t in (raw.get("code_alias") or [])}
    public_phrasing: dict[str, str] = {}
    for key, row in terms.items():
        phrase = clean_phrase(row.get("public_phrasing"))
        if phrase:
            public_phrasing[key] = phrase.strip('"')
    return Dictionary(
        schema=str(raw.get("schema") or "noetfield-dictionary-index-v1"),
        terms=terms,
        alias_map=alias_map,
        retired_terms=retired,
        private_only=private_only,
        code_alias=code_alias,
        public_phrasing=public_phrasing,
    )


def infer_surface(path: str, explicit: str | None = None) -> str:
    if explicit and explicit != "auto":
        if explicit not in SURFACES:
            raise ValueError(f"unknown surface: {explicit}")
        return explicit
    p = path.lower().replace("\\", "/")
    if "/prompts/" in p or p.endswith("prompt.md") or "/.cursor/" in p:
        return "prompt"
    if p.endswith(".json") and ("/receipts/" in p or "receipt" in p):
        return "receipt"
    if any(x in p for x in ("/contracts/", "/legal/", "sow", "msa", "nda")):
        return "contract"
    if any(x in p for x in ("sourcea.app", "noetfield.com", "/website/", "/landing/", "public/")):
        return "website"
    if any(x in p for x in ("p99-ledger", "sg-canonical", "noetfield-library", "language_gate/test")):
        return "internal"
    return "internal"


def line_of(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


@dataclass
class Finding:
    type: str
    term: str
    line: int
    fix: str | None = None
    reason: str | None = None
    auto_fixed: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "term": self.term,
            "line": self.line,
            "fix": self.fix,
            "reason": self.reason,
            "auto_fixed": self.auto_fixed,
        }


def scan(text: str, surface: str, dictionary: Dictionary) -> tuple[list[Finding], str]:
    policy = SURFACE_POLICY[surface]
    findings: list[Finding] = []
    rewritten = text

    for alias, canonical in dictionary.alias_map.items():
        pat = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
        for m in pat.finditer(text):
            findings.append(
                Finding("ALIAS_RETIRED", m.group(0), line_of(text, m.start()), canonical, auto_fixed=True)
            )
        if policy["autofix_alias"]:
            rewritten = pat.sub(canonical, rewritten)

    for pat_str, canon in SYNONYM_AUTOFIX.items():
        pat = re.compile(pat_str, re.IGNORECASE)
        for m in pat.finditer(text):
            findings.append(Finding("SYNONYM_DRIFT", m.group(0), line_of(text, m.start()), canon, auto_fixed=True))
        if policy["autofix_alias"]:
            rewritten = pat.sub(canon, rewritten)

    if policy["block_banned"]:
        for pat_str in BANNED_REGISTER:
            pat = re.compile(pat_str, re.IGNORECASE)
            for m in pat.finditer(text):
                findings.append(Finding("BANNED_REGISTER", m.group(0), line_of(text, m.start())))

    if policy["block_overclaim"]:
        for pat_str, reason in OVERCLAIM_PATTERNS:
            pat = re.compile(pat_str, re.IGNORECASE)
            for m in pat.finditer(text):
                findings.append(Finding("OVERCLAIM", m.group(0), line_of(text, m.start()), reason=reason))

    if policy["block_private"]:
        for term in dictionary.private_only:
            pat = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            for m in pat.finditer(text):
                findings.append(
                    Finding(
                        "BANNED_SURFACE",
                        m.group(0),
                        line_of(text, m.start()),
                        reason=f"PRIVATE_ONLY on {surface} surface",
                    )
                )

    if policy["block_undefined"]:
        lines = text.split("\n")
        seen: set[tuple[int, str]] = set()
        for m in TERM_RE.finditer(text):
            title_case_only = m.group(3) is not None and not m.group(1) and not m.group(2)
            term = (m.group(1) or m.group(2) or m.group(3) or "").strip()
            if not term or len(term) < 3:
                continue
            ln = line_of(text, m.start())
            if title_case_only and 0 <= ln - 1 < len(lines) and lines[ln - 1].lstrip().startswith("#"):
                continue
            low = term.lower()
            if low in KNOWN_VENDOR_ALLOWLIST or low in COMMON_WORD_ALLOWLIST:
                continue
            if low in dictionary.terms or low in dictionary.alias_map or low in dictionary.code_alias:
                continue
            if low in dictionary.retired_terms:
                continue
            words = term.split()
            if words and words[0].lower() in LEADING_STOPWORDS:
                continue
            is_title = all(w[0].isupper() for w in words if w and w[0].isalpha())
            is_allcaps = term.isupper() and len(term) >= 3
            if not (is_title or is_allcaps):
                continue
            span = (m.start(), term)
            if span in seen:
                continue
            seen.add(span)
            findings.append(
                Finding(
                    "UNDEFINED_TERM",
                    term,
                    ln,
                    reason="no dictionary entry — add dictionary first, then mint terminology",
                )
            )

    return findings, rewritten


def decide(findings: list[Finding]) -> tuple[str, list[Finding]]:
    blocking_types = {"BANNED_REGISTER", "OVERCLAIM", "BANNED_SURFACE", "UNDEFINED_TERM"}
    blockers = [f for f in findings if f.type in blocking_types]
    autofixed = [f for f in findings if f.auto_fixed]
    if blockers:
        return "FAIL", blockers
    if autofixed:
        return "PASS_WITH_REWRITE", []
    return "PASS", []


def write_receipt(
    file_path: str,
    surface: str,
    findings: list[Finding],
    decision: str,
    blockers: list[Finding],
    *,
    rewrite_applied: bool,
    agent_rewrite_applied: bool,
    dictionary_source: str,
    extra: dict[str, Any] | None = None,
) -> tuple[Path, dict[str, Any]]:
    import hashlib

    ts = utc_now()
    scan_id = hashlib.sha256(f"{file_path}{ts}".encode()).hexdigest()[:16]
    receipt: dict[str, Any] = {
        "receipt_type": "language_gate_scan_receipt_v1",
        "scan_id": scan_id,
        "time": ts,
        "file": file_path,
        "surface": surface,
        "dictionary_source": dictionary_source,
        "decision": decision,
        "findings_count": len(findings),
        "findings": [f.as_dict() for f in findings],
        "blocking_findings_count": len(blockers),
        "regex_rewrite_applied": rewrite_applied,
        "agent_rewrite_applied": agent_rewrite_applied,
        "tool_version": "language_gate_pipeline_v1",
    }
    if extra:
        receipt.update(extra)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RECEIPTS_DIR / f"{Path(file_path).name}.{scan_id}.receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return out, receipt
