#!/usr/bin/env python3
"""
NOETFIELD LANGUAGE GATE v1
Mechanical pre-save/pre-publish scanner. Not prose - this is the hook.

Usage:
    python3 language_gate_v1.py <file> [--surface public|internal] [--write]

Exit code 0 = PASS. Exit code 1 = FAIL (blocked). Always writes a receipt.
"""
import sys, re, json, hashlib, datetime, os, argparse
from datetime import timezone

GATE_DIR = os.path.dirname(os.path.abspath(__file__))
DICT_PATH = os.path.join(GATE_DIR, "dictionary_index.json")
RECEIPTS_DIR = os.path.join(GATE_DIR, "receipts")

# --- Terminology v1 §6 synonym -> canonical (auto-fixable) ---
SYNONYM_AUTOFIX = {
    r"\bmodel-agnostic\b": "vendor-neutral",
    r"\bagnostic\b(?=.{0,15}\bmodel\b)": "vendor-neutral",
    r"\bclient base\b": "governed reference environment",
    r"\bthe latest file\b": "SSOT",
}

# --- Terminology v1 §7 banned register (never auto-fixable - blocks) ---
BANNED_REGISTER = [
    r"\bwe need\b", r"\bdesperate\b", r"\brevolutionary\b",
    r"\bgame-changing\b", r"\bnext-gen\b",
]

# --- Overclaim patterns (blocks, no safe auto-fix) ---
OVERCLAIM_PATTERNS = [
    (r"\b100%\s*(guaranteed|verified|certified)\b", "unproven absolute claim"),
    (r"\bwe guarantee outcomes\b", "banned per Receipt public-rewrite rule"),
    (r"\bcertified\b", "banned unless schema-cited"),
    (r"\b\d{1,3}\+?\s*(clients|customers)\b", "unprovable customer roster"),
]

# vendor/tool proper nouns that never need a dictionary entry
KNOWN_VENDOR_ALLOWLIST = {
    "cloudflare", "cloudflare workers", "cloudflare queues", "cloudflare cron",
    "supabase", "railway", "aider", "roo code", "openhands", "claude code",
    "github", "aws", "gcp", "perplexity",
}

# common all-caps / status words that are plain English, not system jargon
COMMON_WORD_ALLOWLIST = {
    "draft", "todo", "note", "warning", "important", "tbd", "n/a", "id",
    "url", "api", "faq", "ceo", "cto", "cfo", "usa", "us", "ok", "asap",
    "fyi", "eta", "utc", "pdt", "pst",
}

# leading words that mean a Title-Case run is just sentence structure, not a term
LEADING_STOPWORDS = {
    "the", "a", "an", "our", "we", "this", "that", "these", "those", "under",
    "with", "for", "and", "or", "but", "in", "on", "at", "is", "are", "it",
    "its", "to", "of", "as", "by", "if", "so", "not",
}

TERM_RE = re.compile(
    r'\*\*([A-Za-z][A-Za-z0-9 \-/·≥]{1,50}?)\*\*'          # **bolded term**
    r'|\b([A-Z]{2,}(?:[ /][A-Z]{2,})*)\b'                   # ALLCAPS or ALLCAPS/ALLCAPS
    r'|\b((?:[A-Z][a-zA-Z]*[ \t]+){1,3}[A-Z][a-zA-Z]*)\b'   # Title Case Multi Word Phrase (single line only)
)


def load_dictionary():
    with open(DICT_PATH) as f:
        d = json.load(f)
    known = {}
    for e in d["terms"]:
        known[e["term"].strip().lower()] = e
    tomb = {}
    for k, v in d["tombstone_map"].items():
        v_clean = re.sub(r'[`"]', "", v).strip().rstrip("`")
        tomb[k] = v_clean
    private_only = {t.lower() for t in d["private_only"]}
    return known, tomb, private_only


def line_of(text, pos):
    return text.count("\n", 0, pos) + 1


def scan(text, surface, known, tomb, private_only):
    findings = []
    rewritten = text

    # 1. tombstoned terms -> auto-rewrite
    for term, replacement in tomb.items():
        pat = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
        for m in pat.finditer(text):
            findings.append({
                "type": "TOMBSTONE",
                "term": m.group(0),
                "line": line_of(text, m.start()),
                "fix": replacement,
                "auto_fixed": True,
            })
        rewritten = pat.sub(replacement, rewritten)

    # 2. synonym drift -> auto-rewrite
    for pat_str, canon in SYNONYM_AUTOFIX.items():
        pat = re.compile(pat_str, re.IGNORECASE)
        for m in pat.finditer(text):
            findings.append({
                "type": "SYNONYM_DRIFT",
                "term": m.group(0),
                "line": line_of(text, m.start()),
                "fix": canon,
                "auto_fixed": True,
            })
        rewritten = pat.sub(canon, rewritten)

    # 3. banned register -> blocks, no auto-fix
    for pat_str in BANNED_REGISTER:
        pat = re.compile(pat_str, re.IGNORECASE)
        for m in pat.finditer(text):
            findings.append({
                "type": "BANNED_REGISTER",
                "term": m.group(0),
                "line": line_of(text, m.start()),
                "fix": None,
                "auto_fixed": False,
            })

    # 4. overclaims -> blocks, no auto-fix
    for pat_str, reason in OVERCLAIM_PATTERNS:
        pat = re.compile(pat_str, re.IGNORECASE)
        for m in pat.finditer(text):
            findings.append({
                "type": "OVERCLAIM",
                "term": m.group(0),
                "line": line_of(text, m.start()),
                "fix": None,
                "reason": reason,
                "auto_fixed": False,
            })

    # 5. private-only terms appearing on a public surface -> blocks
    if surface == "public":
        for term in private_only:
            pat = re.compile(rf'\b{re.escape(term)}\b', re.IGNORECASE)
            for m in pat.finditer(text):
                findings.append({
                    "type": "BANNED_SURFACE",
                    "term": m.group(0),
                    "line": line_of(text, m.start()),
                    "fix": None,
                    "reason": "PRIVATE_ONLY term found on a public surface",
                    "auto_fixed": False,
                })

    # 6. undefined system-looking terms -> fail-closed
    lines = text.split("\n")
    seen_spans = set()
    for m in TERM_RE.finditer(text):
        title_case_only = m.group(3) is not None and not m.group(1) and not m.group(2)
        term = (m.group(1) or m.group(2) or m.group(3) or "").strip()
        if not term or len(term) < 3:
            continue
        ln = line_of(text, m.start())
        # document titles/headers: plain Title-Case phrases here are not jargon,
        # bold/ALLCAPS in a header still counts (deliberate emphasis)
        if title_case_only and 0 <= ln - 1 < len(lines) and lines[ln - 1].lstrip().startswith("#"):
            continue
        low = term.lower()
        if low in KNOWN_VENDOR_ALLOWLIST or low in COMMON_WORD_ALLOWLIST:
            continue
        if low in known:
            continue
        if low in tomb:
            continue  # already handled as TOMBSTONE above
        words = term.split()
        if words[0].lower() in LEADING_STOPWORDS:
            continue
        is_title = all(w[0].isupper() for w in words if w and w[0].isalpha())
        is_allcaps = term.isupper() and len(term) >= 3
        if not (is_title or is_allcaps):
            continue
        span = (m.start(), term)
        if span in seen_spans:
            continue
        seen_spans.add(span)
        findings.append({
            "type": "UNDEFINED_TERM",
            "term": term,
            "line": line_of(text, m.start()),
            "fix": None,
            "reason": "no dictionary entry - fail-closed per hard gate",
            "auto_fixed": False,
        })

    return findings, rewritten


def decide(findings):
    blocking_types = {"BANNED_REGISTER", "OVERCLAIM", "BANNED_SURFACE", "UNDEFINED_TERM"}
    blockers = [f for f in findings if f["type"] in blocking_types]
    autofixed = [f for f in findings if f.get("auto_fixed")]
    if blockers:
        return "FAIL", blockers
    if autofixed:
        return "PASS_WITH_REWRITE", []
    return "PASS", []


def write_receipt(file_path, surface, findings, decision, blockers, rewritten_written):
    ts = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    scan_id = hashlib.sha256(f"{file_path}{ts}".encode()).hexdigest()[:16]
    receipt = {
        "receipt_type": "language_gate_scan_receipt_v1",
        "scan_id": scan_id,
        "time": ts,
        "file": file_path,
        "surface": surface,
        "dictionary_source": "language_gate/dictionary_index.json",
        "decision": decision,
        "findings_count": len(findings),
        "findings": findings,
        "blocking_findings_count": len(blockers),
        "rewrite_applied": rewritten_written,
        "tool_version": "language_gate_v1",
    }
    os.makedirs(RECEIPTS_DIR, exist_ok=True)
    out_path = os.path.join(RECEIPTS_DIR, f"{os.path.basename(file_path)}.{scan_id}.receipt.json")
    with open(out_path, "w") as f:
        json.dump(receipt, f, indent=2)
    return out_path, receipt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    ap.add_argument("--surface", choices=["public", "internal"], default="internal")
    ap.add_argument("--write", action="store_true", help="write auto-rewritten output back to file")
    args = ap.parse_args()

    text = open(args.file, encoding="utf-8").read()
    known, tomb, private_only = load_dictionary()
    findings, rewritten = scan(text, args.surface, known, tomb, private_only)
    decision, blockers = decide(findings)

    rewrite_written = False
    if decision == "PASS_WITH_REWRITE" and args.write:
        with open(args.file, "w", encoding="utf-8") as f:
            f.write(rewritten)
        rewrite_written = True

    receipt_path, receipt = write_receipt(args.file, args.surface, findings, decision, blockers, rewrite_written)

    print(f"FILE: {args.file}")
    print(f"SURFACE: {args.surface}")
    print(f"DECISION: {decision}")
    if findings:
        for f_ in findings:
            tag = "BLOCK" if f_["type"] in {"BANNED_REGISTER","OVERCLAIM","BANNED_SURFACE","UNDEFINED_TERM"} else "AUTO-FIX"
            print(f"  [{tag}] {f_['type']}: '{f_['term']}' (line {f_['line']})" + (f" -> '{f_['fix']}'" if f_.get('fix') else ""))
    else:
        print("  no findings")
    print(f"RECEIPT: {receipt_path}")

    sys.exit(1 if decision == "FAIL" else 0)


if __name__ == "__main__":
    main()
