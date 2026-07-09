#!/usr/bin/env python3
"""tf-language-cleanup-v1 — TrustField dry scan using SG Dictionary RC3 + overlay draft.

Authority: SG Dictionary (read-only) · TRUSTFIELD_DICTIONARY_OVERLAY_DRAFT (SG-side draft).
Law: no TrustField repo writes · no public copy rewrite · no invented regulatory claims.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SG_REPO = Path(__file__).resolve().parents[1]
TF_REPO = Path.home() / "Desktop/Noetfield-Systems/TrustField-Technologies"

OUT_OVERLAY_MD = (
    SG_REPO
    / "SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/TRUSTFIELD_DICTIONARY_OVERLAY_DRAFT_v1.md"
)
OUT_OVERLAY_INDEX = SG_REPO / "language_gate/trustfield_dictionary_overlay_index_v1.json"
OUT_INVENTORY = (
    SG_REPO
    / "SG-Canonical-Library/noetfield-library/P99-LEDGER/TRUSTFIELD_LANGUAGE_CLEANUP_INVENTORY_v1.json"
)
OUT_PLAN_MD = (
    SG_REPO
    / "SG-Canonical-Library/noetfield-library/P99-LEDGER/TRUSTFIELD_LANGUAGE_CLEANUP_PLAN_v1.md"
)
OUT_RECEIPT = SG_REPO / "receipts/receipt_tf_language_cleanup_v1.json"

SCAN_ROOTS = [
    TF_REPO / "web",
    TF_REPO / "docs",
    TF_REPO / "data/chatbot",
    TF_REPO / "prompts",
    TF_REPO / ".cursor",
    TF_REPO / "AGENTS.md",
]

SKIP_DIR = {".git", "node_modules", "dist", ".next", "__pycache__", "package-lock.json"}
SCAN_EXT = {".md", ".mdc", ".html", ".tsx", ".ts", ".json", ".py", ".txt"}

# Files that quote forbidden phrases as CI/policy examples — not live claims
SKIP_REGULATORY_SCAN = {
    "docs/RPAA_POSITIONING_ENFORCEMENT.md",
    "eslint-plugin-rpaa-positioning/index.js",
    "scripts/verify_positioning_ci.sh",
    "scripts/verify_commit_message_rpaa.sh",
    ".github/workflows/rpaa-positioning-guard.yml",
}

BACKLOG_CLASSES = frozenset(
    {
        "REGULATORY_COPY_RISK",
        "ENTITY_ALIAS_RISK",
        "PUBLIC_COPY_RISK",
        "CONFLICT_PHRASE",
        "NEEDS_SG_ENTRY",
    }
)
PUBLIC_SURFACES = frozenset({"public_web", "web", "chatbot"})

# Seed TrustField-local terms (draft overlay — not SG canon)
SEED_LOCAL_TERMS: list[dict[str, str]] = [
    {"term": "RPAA", "meaning": "Receipt-truth positioning guard — blocks MSP/PSP self-claims in web copy"},
    {"term": "TF program ID", "meaning": "TrustField program identifier in workflow state"},
    {"term": "MSB API", "meaning": "Product surface name — API for licensed MSB partners; not TrustField MSB status"},
    {"term": "settlement party of record", "meaning": "Partner MSB/institution role — TrustField explicitly not"},
    {"term": "program operations and evidence layer", "meaning": "Canonical RPAA positioning line"},
    {"term": "trustfield.ca", "meaning": "Public web origin for TrustField venture"},
    {"term": "tf_cf_fleet_tick", "meaning": "CF cron motor — fleet tick loop"},
    {"term": "trustfield_loops", "meaning": "Intake/receipt worker on CF"},
    {"term": "payload-free handoff", "meaning": "Sandbox lane A — no functional transmission"},
    {"term": "FINTRAC", "meaning": "Canadian AML regulator — cite only with honest program posture"},
]

SEED_CONFLICT_PHRASES = [
    "we are an MSP",
    "we are a payment service provider",
    "we process payments",
    "we hold funds",
    "we move money",
    "we settle transactions",
    "licensed money transmitter",
    "TrustField Technologies Inc",
    "TrustField Technologies",
]

REGULATORY_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\bwe are an msp\b", re.I), "MSP self-identification"),
    (re.compile(r"\bwe are a payment service provider\b", re.I), "PSP self-identification"),
    (re.compile(r"\bwe are a payment processor\b", re.I), "payment processor self-identification"),
    (re.compile(r"\bwe process payments\b", re.I), "payment processing self-claim"),
    (re.compile(r"\bwe move money\b", re.I), "money movement self-claim"),
    (re.compile(r"\bwe move funds\b", re.I), "funds movement self-claim"),
    (re.compile(r"\bwe hold funds\b", re.I), "custody self-claim"),
    (re.compile(r"\bwe settle transactions\b", re.I), "settlement self-claim"),
    (re.compile(r"\blicensed money transmitter\b", re.I), "money transmitter self-claim"),
    (re.compile(r"\bregulated payment provider\b", re.I), "regulated payment provider self-claim"),
    (re.compile(r"\bTrustField Technologies Inc\.?\b", re.I), "retired entity alias"),
    (re.compile(r"\bTrustField Technologies\b", re.I), "retired entity alias (partial)"),
]

REGULATORY_ALLOWLIST = re.compile(
    r"not an msp|not a msp|not a payment|do not hold|do not |not yet|pre-psp|pre-licensed|"
    r"path to|building toward|after registration|until registration|licensed msp|licensed msb|"
    r"licensed partner|not a money transmitter|not a bank|not a psp|does not hold|does not participate|"
    r"your licensed|licensed msbs|licensed partners|settlement party of record",
    re.I,
)

PUBLIC_RISK_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\b100%\s*(guaranteed|verified|certified)\b", re.I), "unproven absolute claim"),
    (re.compile(r"\bwe guarantee outcomes\b", re.I), "banned guarantee phrase"),
    (re.compile(r"\benterprise ready\b", re.I), "overclaim status"),
    (re.compile(r"\ball green\b", re.I), "fake progress phrase"),
    (re.compile(r"\bsoc\s*2\b", re.I), "SOC2 marketing without pilot guard"),
    (re.compile(r"\bhigh availability\b", re.I), "HA marketing in pilot surfaces"),
]

ENTITY_OK_CONTEXT = re.compile(
    r"not incorporated|name reserved|separate venture|does not hold|licensed partner",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _git_head(repo: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True)
            .strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _sha256(path: Path) -> str:
    if not path.is_file():
        return ""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def sg_pin() -> dict[str, Any]:
    return {
        "branch": "cursor/language-layer-v1",
        "commit": _git_head(SG_REPO),
        "checkpoint": "LANGUAGE_LAYER_RC3_CHECKPOINT",
        "dictionary_batch": str(
            SG_REPO
            / "SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md"
        ),
        "dictionary_index": str(SG_REPO / "language_gate/dictionary_index.json"),
        "pattern_ref": "P9-PATTERN-FACTORY/operational-language-governance-pattern-v1.md",
        "sourcea_template": "scripts/sourcea_language_cleanup_v1.py (SourceA repo)",
    }


def load_sg_dictionary() -> dict[str, Any]:
    idx_path = SG_REPO / "language_gate/dictionary_index.json"
    idx = _read_json(idx_path)
    terms: dict[str, dict[str, Any]] = {}
    for row in idx.get("terms") or []:
        term = str(row.get("term") or "").strip()
        if not term:
            continue
        terms[term.lower()] = row
        for alias in row.get("aliases_retired") or []:
            al = str(alias).strip().lower()
            if al:
                terms.setdefault(al, {**row, "_alias_of": term})
    return {"index": idx, "terms": terms, "path": str(idx_path)}


def iter_scan_files() -> list[Path]:
    out: list[Path] = []
    for base in SCAN_ROOTS:
        if base.is_file():
            if base.suffix.lower() in SCAN_EXT or base.suffix == "":
                out.append(base)
            continue
        if not base.is_dir():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in SKIP_DIR for part in p.parts):
                continue
            if p.suffix.lower() in SCAN_EXT:
                out.append(p)
    return sorted(set(out))


def surface_for(path: Path) -> str:
    rel = str(path.relative_to(TF_REPO)) if path.is_relative_to(TF_REPO) else path.name
    if rel.startswith("web/app") or rel.startswith("web/components"):
        return "public_web"
    if rel.startswith("web"):
        return "web"
    if rel.startswith("data/chatbot"):
        return "chatbot"
    if rel.startswith("docs"):
        return "docs"
    if rel.startswith(".cursor"):
        return "rules"
    return "internal"


def scan_file(path: Path, sg: dict[str, Any]) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rel = str(path.relative_to(TF_REPO)) if path.is_relative_to(TF_REPO) else path.name
    surface = surface_for(path)
    findings: list[dict[str, Any]] = []
    window = 120

    def ctx(start: int, end: int) -> str:
        return text[max(0, start - window) : min(len(text), end + window)]

    if rel.replace("\\", "/") in SKIP_REGULATORY_SCAN:
        return findings

    for pat, label in REGULATORY_PATTERNS:
        for m in pat.finditer(text):
            c = ctx(m.start(), m.end())
            if REGULATORY_ALLOWLIST.search(c):
                continue
            cls = "ENTITY_ALIAS_RISK" if "entity" in label.lower() or "TrustField Technologies" in label else "REGULATORY_COPY_RISK"
            findings.append(
                {
                    "class": cls,
                    "match": m.group(0),
                    "risk": label,
                    "path": rel,
                    "surface": surface,
                    "line": text[: m.start()].count("\n") + 1,
                    "planned_action": "backlog_human_review",
                }
            )

    if surface in ("public_web", "web", "chatbot"):
        for pat, label in PUBLIC_RISK_PATTERNS:
            for m in pat.finditer(text):
                c = ctx(m.start(), m.end())
                if REGULATORY_ALLOWLIST.search(c):
                    continue
                findings.append(
                    {
                        "class": "PUBLIC_COPY_RISK",
                        "match": m.group(0),
                        "risk": label,
                        "path": rel,
                        "surface": surface,
                        "line": text[: m.start()].count("\n") + 1,
                        "planned_action": "backlog_human_review",
                    }
                )

    for phrase in SEED_CONFLICT_PHRASES:
        pat = re.compile(re.escape(phrase), re.I)
        for m in pat.finditer(text):
            c = ctx(m.start(), m.end())
            if REGULATORY_ALLOWLIST.search(c) and "TrustField Technologies" not in phrase:
                continue
            findings.append(
                {
                    "class": "CONFLICT_PHRASE",
                    "match": m.group(0),
                    "phrase": phrase,
                    "path": rel,
                    "surface": surface,
                    "line": text[: m.start()].count("\n") + 1,
                    "planned_action": "backlog_human_review",
                }
            )

    sg_terms = sg.get("terms") or {}
    for row in (_read_json(Path(sg["path"])).get("terms") or [] if sg.get("path") else []):
        term = str(row.get("term") or "")
        if term.lower() == "trustfield" and surface in ("public_web", "web", "chatbot"):
            for alias in row.get("aliases_retired") or []:
                al = str(alias).strip()
                if len(al) < 6:
                    continue
                pat = re.compile(rf"\b{re.escape(al)}\b", re.I)
                for m in pat.finditer(text):
                    findings.append(
                        {
                            "class": "NEEDS_SG_ENTRY",
                            "match": m.group(0),
                            "sg_term": term,
                            "note": "retired TrustField entity alias on surface",
                            "path": rel,
                            "surface": surface,
                            "line": text[: m.start()].count("\n") + 1,
                            "planned_action": "sg_align_or_safe_rewrite",
                        }
                    )

    tokens = re.findall(r"\b[A-Z][A-Z0-9_-]{2,}\b|\b[A-Za-z][A-Za-z0-9_-]{3,}\b", text)
    seen: set[str] = set()
    for tok in tokens[:300]:
        key = tok.lower()
        if key in seen or len(key) < 4:
            continue
        seen.add(key)
        if key in {t["term"].lower() for t in SEED_LOCAL_TERMS}:
            findings.append(
                {
                    "class": "TRUSTFIELD_LOCAL_TERM",
                    "match": tok,
                    "path": rel,
                    "surface": surface,
                    "planned_action": "inventory_only",
                }
            )
        elif key in sg_terms and not sg_terms[key].get("_alias_of"):
            findings.append(
                {
                    "class": "SG_DICTIONARY_TERM",
                    "match": tok,
                    "sg_term": sg_terms[key].get("term"),
                    "path": rel,
                    "surface": surface,
                    "planned_action": "inventory_only",
                }
            )
        elif key.isupper() and len(key) <= 12 and re.match(r"^[A-Z]{2,6}$", tok):
            findings.append(
                {
                    "class": "STATUS_LABEL",
                    "match": tok,
                    "path": rel,
                    "surface": surface,
                    "planned_action": "inventory_only",
                }
            )

    return findings


def build_overlay_index(findings: list[dict[str, Any]], sg: dict[str, Any]) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    entry_ids: set[str] = set()

    def add(term: str, cls: str, note: str) -> None:
        tid = f"TF-OVL-{len(entries)+1:03d}"
        key = term.lower()
        if key in entry_ids:
            return
        entry_ids.add(key)
        entries.append({"id": tid, "term": term, "class": cls, "note": note})

    for seed in SEED_LOCAL_TERMS:
        add(seed["term"], "TRUSTFIELD_LOCAL_TERM", seed["meaning"])

    sg_hits = Counter(f.get("sg_term") or f.get("match") for f in findings if f.get("class") == "SG_DICTIONARY_TERM")
    for term, _ in sg_hits.most_common(25):
        if term:
            add(str(term), "SG_DICTIONARY_TERM", "Cite SG meaning — align copy to dictionary_index.json")

    conflict_hits = Counter(f.get("phrase") or f.get("match") for f in findings if f.get("class") == "CONFLICT_PHRASE")
    for phrase, _ in conflict_hits.most_common(20):
        add(str(phrase), "CONFLICT_PHRASE", "Regulatory/entity confusion — human review before rewrite")

    reg_hits = Counter(f.get("risk") for f in findings if f.get("class") in ("REGULATORY_COPY_RISK", "ENTITY_ALIAS_RISK"))
    for risk, _ in reg_hits.most_common(15):
        add(str(risk), "REGULATORY_COPY_RISK", "Dry-scan risk class — not auto-fixed")

    gap_terms = Counter(f.get("match") for f in findings if f.get("class") == "NEEDS_SG_ENTRY")
    for term, _ in gap_terms.most_common(15):
        add(str(term), "NEEDS_SG_ENTRY", "Route to SG pile with named source — do not define in overlay")

    stats = Counter(e["class"] for e in entries)
    return {
        "schema": "trustfield-dictionary-overlay-index-v1",
        "status": "DRAFT",
        "generated_at": datetime.now().astimezone().isoformat(),
        "authority": {
            "meaning_authority": "SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md",
            "overlay_scope": "TrustField-local operational terms only — draft; not a competing dictionary",
            "sg_dictionary_terms_indexed": len((_read_json(Path(sg_pin()["dictionary_index"])).get("terms") or [])),
            "trustfield_repo": str(TF_REPO),
            "trustfield_commit": _git_head(TF_REPO),
        },
        "stats": dict(stats),
        "entries_total": len(entries),
        "entries": entries,
    }


def build_overlay_md(index: dict[str, Any], pin: dict[str, Any]) -> str:
    lines = [
        "# TRUSTFIELD_DICTIONARY_OVERLAY_DRAFT_v1",
        "",
        "**Status:** SG-side draft · **not** a competing dictionary · **dry-scan only**",
        f"**Generated:** {_now()} UTC",
        f"**Meaning authority:** `NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md` + `language_gate/dictionary_index.json`",
        "**Machine index:** `language_gate/trustfield_dictionary_overlay_index_v1.json`",
        f"**SG pin:** branch `{pin['branch']}` · commit `{pin['commit']}` · checkpoint `{pin['checkpoint']}`",
        "",
        "---",
        "",
        "## Purpose",
        "",
        "TrustField public copy (trustfield.ca) and program-ops vocabulary carry **legal/regulatory wording risk**.",
        "This overlay draft classifies local terms under SG canon — without editing TrustField-Technologies repo.",
        "",
        "## Authority rules",
        "",
        "1. **SG Dictionary wins on meaning.**",
        "2. **Define only `TRUSTFIELD_LOCAL_TERM` here** — RPAA, TF program ID, MSB API product surface, etc.",
        "3. **`REGULATORY_COPY_RISK` / `CONFLICT_PHRASE`** — founder/legal review only; no auto-rewrite.",
        "4. **Never invent** MSB/PSP/custody/license claims for TrustField.",
        "5. **`NEEDS_SG_ENTRY`** — queue for SG pile with named locked source.",
        "",
        "## Local terms (draft)",
        "",
        "| Term | Meaning |",
        "|------|---------|",
    ]
    for e in index.get("entries") or []:
        if e.get("class") == "TRUSTFIELD_LOCAL_TERM":
            lines.append(f"| **{e['term']}** | {e.get('note', '')} |")
    lines.extend(
        [
            "",
            "## Class reference",
            "",
            "| Class | Treatment |",
            "|-------|-----------|",
            "| `SG_DICTIONARY_TERM` | Point to SG index |",
            "| `TRUSTFIELD_LOCAL_TERM` | Define here only |",
            "| `REGULATORY_COPY_RISK` | Human/legal backlog |",
            "| `CONFLICT_PHRASE` | Fix guards or prose — not vocabulary mint |",
            "| `NEEDS_SG_ENTRY` | SG pile queue |",
            "",
            "## Scope exclusions (this pass)",
            "",
            "- No TrustField-Technologies repo edits",
            "- No public copy rewrite applied",
            "- No regulatory claims added",
            "",
            f"*v1 DRAFT ({_now()}) — tf-language-cleanup-v1 dry scan*",
        ]
    )
    return "\n".join(lines) + "\n"


def build_plan_md(summary: dict[str, Any], pin: dict[str, Any]) -> str:
    by_class = summary.get("findings_by_class") or {}
    high = summary.get("high_risk_samples") or []
    lines = [
        "# TRUSTFIELD_LANGUAGE_CLEANUP_PLAN_v1",
        "",
        f"**Generated:** {_now()} UTC",
        "**Task:** tf-language-cleanup-v1",
        f"**SG pin:** `{pin['commit']}` on `{pin['branch']}`",
        "**Mode:** dry scan only — **no rewrites applied**",
        "",
        "---",
        "",
        "## Scan summary",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Files scanned | {summary.get('files_scanned', 0)} |",
        f"| Total findings | {summary.get('total_findings', 0)} |",
        f"| Safe rewrites planned | 0 |",
        f"| Backlog (human review) | {summary.get('backlog_count', 0)} |",
        f"| Public-surface backlog | {summary.get('public_backlog_count', 0)} |",
        f"| Public high-risk (reg/entity) | {summary.get('public_high_risk_count', 0)} |",
        "",
        "## Key finding",
        "",
        (
            "**trustfield.ca web copy (`web/`): 0 regulatory self-claim hits** after RPAA allowlist — "
            "backlog is mostly internal docs (entity alias history + policy quote files)."
            if summary.get("public_high_risk_count", 0) == 0
            else "**Public surfaces have regulatory hits — review `public_high_risk_samples` first.**"
        ),
        "",
        "## Findings by class",
        "",
    ]
    for k, v in sorted(by_class.items(), key=lambda x: -x[1]):
        lines.append(f"- **{k}:** {v}")
    lines.extend(["", "## High-risk samples (regulatory / entity)", ""])
    if not high:
        lines.append("- _(none after allowlist — verify manually on public_web surfaces)_")
    else:
        for h in high[:25]:
            lines.append(
                f"- `{h.get('path')}:{h.get('line')}` — **{h.get('class')}** — `{h.get('match')}` ({h.get('risk', h.get('phrase', ''))})"
            )
    lines.extend(
        [
            "",
            "## Planned actions",
            "",
            "| Action | Count | Rule |",
            "|--------|-------|------|",
            "| `apply_safe` | 0 | Blocked this pass |",
            f"| `backlog_human_review` | {summary.get('backlog_count', 0)} | REGULATORY / PUBLIC / CONFLICT only |",
            f"| `inventory_only` | {summary.get('inventory_count', 0)} | Local + SG term hits |",
            "",
            "## SG gap routing",
            "",
            f"- `NEEDS_SG_ENTRY` hits: {by_class.get('NEEDS_SG_ENTRY', 0)}",
            "- Route to SG pile — do not define in TrustField overlay without founder lock",
            "",
            "## Next pass (not this task)",
            "",
            "1. Founder/legal review of REGULATORY_COPY_RISK backlog on `web/lib/company-copy.ts`",
            "2. Safe alias pass (TrustField entity) only after review",
            "3. Mirror overlay to TrustField-Technologies when approved",
            "",
            "**Forbidden:** repo edits · public rewrite · invented MSB/PSP/custody claims",
            "",
            f"*tf-language-cleanup-v1 · dry scan plan only*",
        ]
    )
    return "\n".join(lines) + "\n"


def run_dry_scan() -> dict[str, Any]:
    pin = sg_pin()
    sg = load_sg_dictionary()
    sg["path"] = pin["dictionary_index"]
    files = iter_scan_files()
    all_findings: list[dict[str, Any]] = []
    for f in files:
        all_findings.extend(scan_file(f, sg))

    by_class = Counter(f.get("class") for f in all_findings)
    backlog = [f for f in all_findings if f.get("class") in BACKLOG_CLASSES]
    public_backlog = [f for f in backlog if f.get("surface") in PUBLIC_SURFACES]
    high_risk = [
        f
        for f in backlog
        if f.get("class") in ("REGULATORY_COPY_RISK", "ENTITY_ALIAS_RISK", "PUBLIC_COPY_RISK")
    ]
    public_high_risk = [f for f in high_risk if f.get("surface") in PUBLIC_SURFACES]

    overlay_index = build_overlay_index(all_findings, sg)
    overlay_md = build_overlay_md(overlay_index, pin)

    summary = {
        "files_scanned": len(files),
        "total_findings": len(all_findings),
        "findings_by_class": dict(by_class),
        "backlog_count": len(backlog),
        "public_backlog_count": len(public_backlog),
        "public_high_risk_count": len(public_high_risk),
        "inventory_count": sum(
            1 for f in all_findings if f.get("planned_action") == "inventory_only"
        ),
        "high_risk_samples": sorted(high_risk, key=lambda x: (x.get("surface", ""), x.get("path", "")))[:40],
        "public_high_risk_samples": sorted(
            public_high_risk, key=lambda x: (x.get("path", ""), x.get("line", 0))
        )[:25],
    }

    inventory = {
        "schema": "trustfield-language-cleanup-inventory-v1",
        "at": _now(),
        "task": "tf-language-cleanup-v1",
        "mode": "dry_scan_only",
        "sg_pin": pin,
        "trustfield_repo": str(TF_REPO),
        "trustfield_commit": _git_head(TF_REPO),
        "summary": summary,
        "findings": all_findings,
    }

    plan_md = build_plan_md(summary, pin)

    OUT_OVERLAY_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_OVERLAY_INDEX.parent.mkdir(parents=True, exist_ok=True)
    OUT_INVENTORY.parent.mkdir(parents=True, exist_ok=True)
    OUT_PLAN_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_RECEIPT.parent.mkdir(parents=True, exist_ok=True)

    OUT_OVERLAY_MD.write_text(overlay_md, encoding="utf-8")
    OUT_OVERLAY_INDEX.write_text(json.dumps(overlay_index, indent=2) + "\n", encoding="utf-8")
    OUT_INVENTORY.write_text(json.dumps(inventory, indent=2) + "\n", encoding="utf-8")
    OUT_PLAN_MD.write_text(plan_md, encoding="utf-8")

    receipt = {
        "schema": "receipt_tf_language_cleanup_v1",
        "at": datetime.now().astimezone().isoformat(),
        "verdict": "PASS_DRY_SCAN",
        "task": "tf-language-cleanup-v1",
        "mode": "dry_scan_only",
        "rewrites_applied": 0,
        "sg_pin": pin,
        "trustfield_repo": str(TF_REPO),
        "trustfield_commit": _git_head(TF_REPO),
        "summary": {
            "files_scanned": summary["files_scanned"],
            "total_findings": summary["total_findings"],
            "findings_by_class": summary["findings_by_class"],
            "backlog_count": summary["backlog_count"],
            "public_backlog_count": summary.get("public_backlog_count", 0),
            "public_high_risk_count": summary.get("public_high_risk_count", 0),
            "overlay_entries": overlay_index.get("entries_total"),
        },
        "outputs": {
            "overlay_md": str(OUT_OVERLAY_MD.relative_to(SG_REPO)),
            "overlay_index": str(OUT_OVERLAY_INDEX.relative_to(SG_REPO)),
            "inventory": str(OUT_INVENTORY.relative_to(SG_REPO)),
            "plan_md": str(OUT_PLAN_MD.relative_to(SG_REPO)),
        },
        "sha256": {
            "overlay_md": _sha256(OUT_OVERLAY_MD),
            "overlay_index": _sha256(OUT_OVERLAY_INDEX),
            "inventory": _sha256(OUT_INVENTORY),
            "plan_md": _sha256(OUT_PLAN_MD),
        },
        "scope_excluded": [
            "TrustField-Technologies repo edits",
            "public copy rewrite",
            "regulatory claims invented",
            "MSB/PSP/custody status claims added",
        ],
        "next_repo_recommendation": "TrustField first — legal/regulatory public copy risk",
    }
    OUT_RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    return {"receipt": receipt, "summary": summary}


def main() -> int:
    ap = argparse.ArgumentParser(description="tf-language-cleanup-v1 dry scan")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not TF_REPO.is_dir():
        print(f"FAIL missing TrustField repo: {TF_REPO}", file=sys.stderr)
        return 1
    out = run_dry_scan()
    if args.json:
        print(json.dumps(out["receipt"], indent=2))
    else:
        s = out["summary"]
        print(
            f"tf-language-cleanup-v1: scanned={s['files_scanned']} findings={s['total_findings']} "
            f"backlog={s['backlog_count']} verdict=PASS_DRY_SCAN"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
