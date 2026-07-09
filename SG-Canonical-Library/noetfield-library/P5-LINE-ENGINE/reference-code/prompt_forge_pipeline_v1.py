#!/usr/bin/env python3
"""
Prompt Forge — Pipeline Machine (v1)  ·  Chat Unify pipeline #3
================================================================
Turns FOUNDER LANGUAGE → the best Cursor-agent mission prompt, by running the
SOURCE-A LLM Agent Operating Law (SSOT v2) as code.

Design mirrors your own architecture:
    The LLM PROPOSES the rewrite.  The POLICY CODE enforces it.
So the output is always SSOT-shaped, whether or not an LLM is available.

Two layers:
  1. Deterministic policy (always on, zero deps): lint, mode detect, fact
     extraction, template assembly, mandatory guardrail injection.
  2. Optional LLM pass (OpenRouter, stdlib urllib): rewrites prose into the
     template fields under an SSOT system prompt. The deterministic layer then
     RE-ASSERTS the constraints so the LLM can never strip them.

Run:
    echo "fix the dns for sourcea.app" | python3 prompt_forge_pipeline_v1.py
    python3 prompt_forge_pipeline_v1.py --text "wire old vercel page as subpage" --json
    python3 prompt_forge_pipeline_v1.py --demo
    OPENROUTER_API_KEY=sk-... python3 prompt_forge_pipeline_v1.py --text "..." --llm
"""

from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import json
import os
import re
import sys
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

VERSION = "1.0.0"
PIPELINE_ID = "prompt_forge"

# ── known systems the founder works across (for "name the systems" law) ──────
KNOWN_SYSTEMS = [
    "Vercel", "Cloudflare", "Cloudflare Pages", "Cloudflare Workers", "Supabase",
    "Railway", "GitHub", "n8n", "Neon", "OpenRouter", "Modal", "RunPod", "R2",
    "Fal", "ElevenLabs", "FBE", "Worker Hub", "Mac Law",
]

# ── standing guardrails injected into EVERY prompt (SSOT §C/§F) ───────────────
STANDING_CONSTRAINTS = [
    "NO rebuild, NO redeploy, NO starting over if it already exists — wire/fix, don't recreate.",
    "One job only — do not bundle unrelated work into this mission.",
    "Don't break anything already working (or its TLS / live state).",
    "Verdicts from receipts only — no build theater, no 'it's green' without proof.",
]
IF_BLOCKED = (
    "IF BLOCKED or ambiguous: STOP and tell me what's missing or which decision is mine "
    "(naming, paths, which project/provider). Do not guess my intent. Do not deploy a placeholder."
)

# ── the SSOT v2 policy, condensed, used as the LLM system prompt ──────────────
SSOT_SYSTEM_PROMPT = """\
You are Prompt Forge. You convert a founder's raw, informal request into ONE
bounded Cursor-agent mission prompt that obeys the SOURCE-A LLM Agent Operating
Law (SSOT v2). You are under the SAME law you enforce:

CORE: Direction, not force. Carry the founder's GOAL and guardrails. Do NOT add
scope, steps, or "while we're at it" extras the founder did not ask for. Translate
the need — never inflate it.

RULES you must bake into the output:
- One job per mission. If the input bundles unrelated jobs, surface that and keep
  the prompt to the primary job only.
- State the true current state. If the founder says something already exists / is
  deployed / is live, put it under ALREADY DONE and forbid rebuilding it.
- Name the systems involved (hosts/platforms) but leave the METHOD to the agent.
- Founder decisions (naming, paths, which project/provider, what a page shows) are
  the founder's — the agent must ask, never guess.
- Truth from receipts: every mission ends with a concrete VERIFY (curl / test log /
  live URL loads), never self-report.
- Binary, end-to-end DONE condition.
- Prefer Direction mode (let the agent diagnose) unless the founder clearly specified
  exact steps.

OUTPUT EXACTLY this template, filled, nothing before or after:

GOAL: <one plain sentence>

CONTEXT (true now — do not re-derive):
- ALREADY DONE / DEPLOYED (do NOT redo): <...>
- Systems involved: <...>
- Accounts/access if relevant: <...>

WHAT I WANT: <the outcome, not the steps>

DONE = <one binary, provable, end-to-end condition>

VERIFY: <exact proof — curl output / test log / live URL>

CONSTRAINTS:
- <constraints>

IF BLOCKED or ambiguous: STOP and tell me what's missing or which decision is mine.
Do not guess. Do not deploy a placeholder. Verdicts from receipts only.
"""

URL_RE = re.compile(r"https?://[^\s)>\]]+")
CMD_RE = re.compile(r"^\s*(git|curl|npm|npx|python3?|rm|mv|cp|ln|sudo|docker|wrangler|gh|kubectl)\b",
                    re.I | re.M)
DESTRUCTIVE_RE = re.compile(r"\b(rm\s+-rf|git\s+reset\s+--hard|stash\s+pop|drop\s+table|checkout|--force)\b", re.I)


# ─────────────────────────────────────────────────────────────────────────────
@dataclass
class Finding:
    level: str          # "warn" | "note"
    code: str
    message: str


@dataclass
class ForgeResult:
    pipeline: str
    version: str
    mode: str                       # "direction" | "spec"
    prompt: str                     # the compiled Cursor prompt
    findings: list[Finding]
    facts: dict
    used_llm: bool
    created_at: str

    def to_dict(self) -> dict:
        d = dataclasses.asdict(self)
        return d


# ── 1. LINT: catch anti-patterns in the founder input (SSOT §H) ──────────────
def lint(text: str) -> list[Finding]:
    f: list[Finding] = []
    low = text.lower()

    # bundled jobs — multiple distinct system-domains or explicit conjunction of tasks
    domains_hit = {s.lower() for s in ["dns", "queue", "database", "schema", "deploy",
                                       "test", "router", "auth", "billing"] if s in low}
    if len(domains_hit) >= 2 or re.search(r"\b(and also|then also|while you'?re at it|plus also)\b", low):
        f.append(Finding("warn", "bundled_jobs",
                         "Looks like more than one job. Keep this mission to the PRIMARY job; "
                         "split the rest into a separate mission."))

    # prescribing commands → nudge toward direction
    if CMD_RE.search(text):
        f.append(Finding("note", "prescribes_commands",
                         "You included commands. Consider Direction mode — let the agent choose "
                         "the steps unless you're certain."))

    # destructive op
    if DESTRUCTIVE_RE.search(text):
        f.append(Finding("warn", "destructive_op",
                         "Destructive action detected. The prompt will require LOOK-FIRST "
                         "(inspect before any delete/checkout/stash-pop)."))

    # rebuild risk: says it exists AND says build/deploy
    exists = re.search(r"\b(already|deployed|live|exists|working|200)\b", low)
    rebuild = re.search(r"\b(build|deploy|create|rebuild|redeploy|from scratch|from begin)\b", low)
    if exists and rebuild:
        f.append(Finding("warn", "rebuild_risk",
                         "You mention something already exists AND a build/deploy. The prompt will "
                         "pin ALREADY DONE and forbid rebuilding it."))

    # no verification intent
    if not re.search(r"\b(verify|check|confirm|show|test|curl|prove|loads?)\b", low):
        f.append(Finding("note", "adds_verification",
                         "No verification asked — the machine will add a receipt-based VERIFY step."))
    return f


# ── 2. MODE detection (Direction vs Spec) ────────────────────────────────────
def detect_mode(text: str) -> str:
    spec_signals = bool(re.search(r"(^|\n)\s*(\d+[\.\)]|step\s*\d)", text, re.I)) or len(CMD_RE.findall(text)) >= 2
    return "spec" if spec_signals else "direction"


# ── 3. FACT extraction ───────────────────────────────────────────────────────
def extract_facts(text: str) -> dict:
    systems = sorted({s for s in KNOWN_SYSTEMS if re.search(rf"\b{re.escape(s)}\b", text, re.I)},
                     key=str.lower)
    urls = URL_RE.findall(text)
    # sentences that imply current state already exists
    already = []
    for sent in re.split(r"(?<=[.!?\n])\s+", text):
        if re.search(r"\b(already|deployed|live|exists|working|200|on (vercel|github|railway|cloudflare))\b",
                     sent, re.I):
            s = sent.strip()
            if s:
                already.append(s)
    emails = re.findall(r"[\w.\-]+@[\w.\-]+\.\w+", text)
    return {"systems": systems, "urls": urls, "already_done": already, "accounts": emails}


# ── 4. DETERMINISTIC compile (always works, no network) ──────────────────────
def compile_deterministic(text: str, mode: str, facts: dict) -> str:
    goal = text.strip().split("\n")[0][:240] or "(state the goal in one sentence)"

    already = facts["already_done"]
    already_line = " ".join(already) if already else \
        "(none stated — confirm what already exists before any build)"

    systems = ", ".join(facts["systems"]) if facts["systems"] else "(name the hosts/platforms involved)"
    accounts = ", ".join(facts["accounts"]) if facts["accounts"] else "(add account/access if the agent needs it)"
    urls = ("\n  - URLs: " + ", ".join(facts["urls"])) if facts["urls"] else ""

    want = (text.strip() if len(text.strip()) > len(goal)
            else "(the outcome you want — not the steps)")

    constraints = "\n".join(f"- {c}" for c in STANDING_CONSTRAINTS)
    if mode == "spec":
        constraints += "\n- Follow my stated steps, but still prove DONE with receipts."

    return f"""\
GOAL: {goal}

CONTEXT (true now — do not re-derive):
  - ALREADY DONE / DEPLOYED (do NOT redo): {already_line}
  - Systems involved: {systems}{urls}
  - Accounts/access if relevant: {accounts}

WHAT I WANT: {want}

DONE = the outcome above is true and verified end-to-end on the real surface.

VERIFY: show me how you confirmed it actually works — curl output / test log / the live
URL loading the correct content with valid TLS. Receipts, not "it's done".

CONSTRAINTS:
{constraints}

{IF_BLOCKED}
"""


# ── 5. OPTIONAL LLM pass (OpenRouter via stdlib) ─────────────────────────────
def openrouter_call(system: str, user: str, model: str, api_key: str, timeout: int = 60) -> str:
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps({
            "model": model,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
            "temperature": 0.2,
        }).encode(),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read().decode())
    return data["choices"][0]["message"]["content"].strip()


def compile_with_llm(text: str, facts: dict, llm_fn: Callable[[str, str], str]) -> str:
    user = (f"FOUNDER REQUEST:\n{text}\n\n"
            f"EXTRACTED FACTS (use, do not invent more):\n{json.dumps(facts, indent=2)}\n\n"
            f"Produce the mission prompt now.")
    return llm_fn(SSOT_SYSTEM_PROMPT, user).strip()


def _enforce_constraints(prompt: str) -> str:
    """Belt-and-suspenders: the LLM may not strip the standing guardrails."""
    if "CONSTRAINTS" not in prompt:
        prompt += "\n\nCONSTRAINTS:\n" + "\n".join(f"- {c}" for c in STANDING_CONSTRAINTS)
    if "IF BLOCKED" not in prompt:
        prompt += "\n\n" + IF_BLOCKED
    return prompt


# ── 6. The pipeline machine ──────────────────────────────────────────────────
class PromptForge:
    """Chat Unify pipeline #3. Stateless. `.run()` is the entry point."""

    def __init__(self, model: str = "google/gemini-flash-1.5", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")

    def run(self, founder_text: str, use_llm: Optional[bool] = None) -> ForgeResult:
        text = (founder_text or "").strip()
        if not text:
            raise ValueError("empty founder input")

        findings = lint(text)
        mode = detect_mode(text)
        facts = extract_facts(text)

        want_llm = (use_llm is True) or (use_llm is None and bool(self.api_key))
        used_llm = False
        prompt = ""

        if want_llm and self.api_key:
            try:
                prompt = compile_with_llm(
                    text, facts,
                    lambda s, u: openrouter_call(s, u, self.model, self.api_key),
                )
                prompt = _enforce_constraints(prompt)   # policy code wins
                used_llm = True
            except Exception as e:                       # graceful fallback — always reliable
                findings.append(Finding("note", "llm_fallback",
                                        f"LLM pass failed ({e.__class__.__name__}); used deterministic policy."))

        if not prompt:
            prompt = compile_deterministic(text, mode, facts)

        return ForgeResult(
            pipeline=PIPELINE_ID, version=VERSION, mode=mode, prompt=prompt,
            findings=findings, facts=facts, used_llm=used_llm,
            created_at=_dt.datetime.now(_dt.timezone.utc).isoformat(),
        )


# ── Chat Unify registration descriptor (adapt to your registry shape) ────────
PIPELINE = {
    "id": PIPELINE_ID,
    "name": "Prompt Forge",
    "version": VERSION,
    "summary": "Founder language → SSOT-v2 Cursor mission prompt.",
    "entry": "PromptForge",          # class to instantiate
    "method": "run",                 # run(founder_text:str, use_llm:bool|None) -> ForgeResult
    "input": "founder_text: str",
    "output": "ForgeResult (.prompt is the Cursor-ready text; .to_dict() for JSON)",
}


def _write_receipt(result: ForgeResult) -> Optional[str]:
    try:
        d = Path.home() / ".sina" / "prompt-forge-receipts"
        d.mkdir(parents=True, exist_ok=True)
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        p = d / f"prompt-forge-{stamp}-v1.json"
        p.write_text(json.dumps(result.to_dict(), indent=2))
        return str(p)
    except Exception:
        return None


# ── CLI ──────────────────────────────────────────────────────────────────────
def main() -> int:
    ap = argparse.ArgumentParser(description="Prompt Forge — founder language → Cursor mission prompt")
    ap.add_argument("--text", help="founder request (else reads stdin)")
    ap.add_argument("--json", action="store_true", help="emit full JSON receipt")
    ap.add_argument("--llm", dest="llm", action="store_true", help="force LLM pass")
    ap.add_argument("--no-llm", dest="llm", action="store_false", help="force deterministic only")
    ap.add_argument("--model", default="google/gemini-flash-1.5")
    ap.add_argument("--receipt", action="store_true", help="write a ~/.sina receipt")
    ap.add_argument("--demo", action="store_true", help="run a built-in example")
    ap.set_defaults(llm=None)
    a = ap.parse_args()

    if a.demo:
        a.text = ("sourcea.app/ is already live. the old kernel page is already deployed on "
                  "source-a.vercel.app/sourcea/ — wire it as a subpage under sourcea.app. "
                  "dont redeploy everything from scratch! just fix it e2e.")

    text = a.text or (sys.stdin.read() if not sys.stdin.isatty() else "")
    if not text.strip():
        ap.error("no input (use --text, pipe stdin, or --demo)")

    result = PromptForge(model=a.model).run(text, use_llm=a.llm)
    receipt_path = _write_receipt(result) if a.receipt else None

    if a.json:
        out = result.to_dict()
        if receipt_path:
            out["receipt_path"] = receipt_path
        print(json.dumps(out, indent=2))
    else:
        if result.findings:
            print("─ findings ───────────────────────────────")
            for f in result.findings:
                print(f"  [{f.level}] {f.code}: {f.message}")
            print("─ compiled prompt ────────────────────────")
        print(result.prompt)
        meta = f"mode={result.mode} · llm={'on' if result.used_llm else 'off'}"
        if receipt_path:
            meta += f" · receipt={receipt_path}"
        print(f"\n# {meta}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
