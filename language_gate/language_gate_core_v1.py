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
SUPPLEMENT_PATH = GATE_DIR / "dictionary_rc2_supplement.json"
RECEIPTS_DIR = GATE_DIR / "receipts"
TOOL_VERSION = "language_gate_rc2_v1"

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
    "no roo", "kilo", "gemini flash", "github actions", "llama",
}

COMMON_WORD_ALLOWLIST = {
    "draft", "todo", "note", "warning", "important", "tbd", "n/a", "id",
    "url", "api", "faq", "ceo", "cto", "cfo", "usa", "us", "ok", "asap",
    "fyi", "eta", "utc", "pdt", "pst", "pass", "fail", "json", "yaml", "md",
    "nda", "sow", "msa", "roi", "yes", "no", "defer", "approve", "never",
}

# Plain English / doc-structure tokens — not system vocabulary.
STRUCTURAL_ALLOWLIST = {
    "work order", "work", "head", "non", "goal", "goals", "phase", "tool decision",
    "allowed scope", "forbidden", "mechanical", "prose", "gates", "gate", "date",
    "dispatch", "plan", "patch", "test", "receipt", "stop", "complete", "pending",
    "required", "ratified", "signature", "authorization statement", "authorization",
    "revenue work authorization", "start ready", "product layer", "pattern", "factory",
    "canon", "status", "customer id", "spend leak audit", "nnn", "ide", "github actions",
    "gemini flash", "zero execution authority", "pending founder approval",
    "revenue", "north star", "north-star", "related", "example", "the law", "the test",
    "what this means", "relation to other doctrine", "first written", "parent doctrine",
    "incident basis", "north-star deliverable", "everything else", "dimension",
    "cycle anatomy", "no roo", "final sg", "governance hotspot fixes",
    "noetfield governance", "noetfield os", "package assembly", "remaining lane receipts",
}

# Registered product / entity / vendor names allowed without a dictionary row.
ENTITY_ALLOWLIST = {
    "sourcea", "sourcea brain", "sourcea brain agent", "noetfield systems inc",
    "noetfield systems", "cloudflare worker", "workers ai", "cloud kernel",
    "operating brain install", "managed brain", "mac worker", "trustfield technologies",
    "trustfield", "github actions", "gemini flash", "studio ide", "aider",
    "acg", "spend leak audit", "brain audit",
}

_RUNTIME_STRUCTURAL: set[str] | None = None
_RUNTIME_ENTITY: set[str] | None = None


def effective_structural_allowlist() -> set[str]:
    global _RUNTIME_STRUCTURAL
    if _RUNTIME_STRUCTURAL is None:
        merged = set(STRUCTURAL_ALLOWLIST)
        if SUPPLEMENT_PATH.is_file():
            sup = json.loads(SUPPLEMENT_PATH.read_text(encoding="utf-8"))
            merged |= {str(x).lower() for x in sup.get("structural_allowlist") or []}
        _RUNTIME_STRUCTURAL = merged
    return _RUNTIME_STRUCTURAL


def effective_entity_allowlist() -> set[str]:
    global _RUNTIME_ENTITY
    if _RUNTIME_ENTITY is None:
        merged = set(ENTITY_ALLOWLIST)
        _RUNTIME_ENTITY = merged
    return _RUNTIME_ENTITY

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
    for cut in (" Is NOT:", " Example:", " Doctrine source file:", " Public phrasing:", " ---", " Related:"):
        idx = text.find(cut)
        if idx > 0:
            text = text[:idx].strip()
    text = text.strip('"').strip("'").strip()
    return text or None


def normalize_public_phrasing(value: str | None) -> str | None:
    """First safe public phrase — strip governance footnotes and quotes."""
    text = clean_phrase(value)
    if not text:
        return None
    for cut in (" — never", " only if", " unless", " Related:"):
        idx = text.find(cut)
        if idx > 0:
            text = text[:idx].strip()
    return text.strip('"').strip("'").strip() or None


def load_dictionary(path: Path | None = None) -> Dictionary:
    path = path or DICT_PATH
    raw = json.loads(path.read_text(encoding="utf-8"))
    if SUPPLEMENT_PATH.is_file():
        sup = json.loads(SUPPLEMENT_PATH.read_text(encoding="utf-8"))
        raw_terms = list(raw.get("terms") or [])
        seen = {str(r.get("term", "")).strip().lower() for r in raw_terms}
        for row in sup.get("terms") or []:
            key = str(row.get("term") or "").strip().lower()
            if key and key not in seen:
                raw_terms.append(row)
                seen.add(key)
        raw = {**raw, "terms": raw_terms}
        for k, v in (sup.get("alias_map") or {}).items():
            raw.setdefault("alias_map", {})[k] = v
        for item in sup.get("code_alias") or []:
            raw.setdefault("code_alias", []).append(item)
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
        phrase = normalize_public_phrasing(row.get("public_phrasing"))
        if phrase:
            public_phrasing[key] = phrase
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


def line_text_at(text: str, pos: int) -> str:
    start = text.rfind("\n", 0, pos) + 1
    end = text.find("\n", pos)
    if end < 0:
        end = len(text)
    return text[start:end]


def is_markdown_header_line(line: str) -> bool:
    return bool(re.match(r"^\s{0,3}#{1,6}\s+", line))


def protected_spans(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for m in re.finditer(r"```[\s\S]*?```", text):
        spans.append((m.start(), m.end()))
    for m in re.finditer(r"`[^`\n]+`", text):
        spans.append((m.start(), m.end()))
    for m in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        spans.append((m.start(1), m.end(1)))
    for m in re.finditer(r"https?://[^\s)>\]]+", text):
        spans.append((m.start(), m.end()))
    for m in re.finditer(r"(?<![A-Za-z0-9_/])[A-Za-z0-9][A-Za-z0-9._/-]*\.(?:md|json|yaml|yml|sh|py|tsx|ts|js)(?![A-Za-z0-9_])", text):
        spans.append((m.start(), m.end()))
    spans.sort()
    return spans


def in_protected_span(spans: list[tuple[int, int]], start: int, end: int) -> bool:
    for a, b in spans:
        if start >= a and end <= b:
            return True
    return False


def is_hyphen_fragment(text: str, start: int, end: int) -> bool:
    before = text[start - 1] if start > 0 else ""
    after = text[end] if end < len(text) else ""
    return before == "-" or after == "-"


def is_compound_slug(text: str, start: int, end: int) -> bool:
    """Skip single-word keys inside hyphenated identifiers (governed-autorun)."""
    if start <= 0 or end >= len(text):
        return False
    if text[start - 1] != "-":
        return False
    return text[end] == "-" or (end < len(text) and text[end] in "-./")


def is_skippable_undefined(term: str, *, line: str, text: str, start: int, end: int, spans: list[tuple[int, int]]) -> bool:
    low = term.lower().strip()
    if not low or len(low) < 3:
        return True
    if in_protected_span(spans, start, end):
        return True
    if is_markdown_header_line(line):
        return True
    if is_hyphen_fragment(text, start, end):
        return True
    if low in KNOWN_VENDOR_ALLOWLIST or low in COMMON_WORD_ALLOWLIST:
        return True
    if low in STRUCTURAL_ALLOWLIST or low in ENTITY_ALLOWLIST:
        return True
    if low in effective_structural_allowlist() or low in effective_entity_allowlist():
        return True
    if term.isupper() and len(term) <= 4:
        return True
    if re.match(r"^\d+\.\s", line.lstrip()):
        return True
    if line.lstrip().startswith("|"):
        return True
    if re.search(r"\b(for example|e\.g\.|i\.e\.)\b", line, re.I):
        return True
    return False


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
        spans = protected_spans(text)
        seen: set[tuple[int, str]] = set()
        for m in TERM_RE.finditer(text):
            title_case_only = m.group(3) is not None and not m.group(1) and not m.group(2)
            term = (m.group(1) or m.group(2) or m.group(3) or "").strip()
            if not term or len(term) < 3:
                continue
            start, end = m.start(), m.end()
            ln = line_of(text, start)
            line = line_text_at(text, start)
            if is_skippable_undefined(term, line=line, text=text, start=start, end=end, spans=spans):
                continue
            low = term.lower()
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
            span = (start, term)
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
    hard_types = {"BANNED_REGISTER", "OVERCLAIM", "BANNED_SURFACE"}
    hard_blockers = [f for f in findings if f.type in hard_types]
    soft_blockers = [f for f in findings if f.type == "UNDEFINED_TERM"]
    autofixed = [f for f in findings if f.auto_fixed]
    if hard_blockers:
        return "FAIL", hard_blockers
    if soft_blockers:
        return "WARN", soft_blockers
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
        "tool_version": TOOL_VERSION,
    }
    if extra:
        receipt.update(extra)
    RECEIPTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RECEIPTS_DIR / f"{Path(file_path).name}.{scan_id}.receipt.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return out, receipt
