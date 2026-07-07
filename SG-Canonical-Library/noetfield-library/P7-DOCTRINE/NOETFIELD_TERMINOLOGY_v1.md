# NOETFIELD_TERMINOLOGY_v1

**Wording authority · daily · mandatory · machine-enforceable · Tier 0**

Status: `v1` · Load on **every output** before any doctrine edit, receipt field, job spec, specialist brief, or customer-facing text.

Answers: **“What word do I write, right now?”** — one line per term.  
Meaning source: `NOETFIELD_DICTIONARY_v1.md` (terminology is **minted from** dictionary — never the reverse).  
Layer guide: `P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md`  
Enforcement: lint — synonym rewrite (§6) + banned register (§7).

---

## The one rule

Use the wording here. If the term is not here, **stop** — author or locate the **dictionary** entry first, mint the terminology line, then write. Never invent a private meaning in a prompt, receipt field, or page.

**Hard gate:** no new job, task, specialist, role, product page, contract clause, or receipt field without a dictionary entry (existing or newly versioned).

---

## §1 — Core system nouns

**Receipt** — machine-readable record that *proves* what happened, with defined fields (who, model, cost, tokens, success, latency, time, sink ack when applicable).  
IS NOT: a log line, chat “done,” or deploy log without live verify.  
EX: “Worker said PASS but no receipt → unverified.”

**Observation record** — honest guard snapshot (health pass, census run) with schema and timestamp; may lack full proof-receipt fields.  
IS NOT: a substitute for proof receipt on customer or revenue claims.  
EX: “Fleet health pass is an observation record, not R≥1 proof.”

**Claim** — any success statement without fielded receipt.  
IS NOT: a receipt.

**SSOT** — the one authoritative file/record when copies disagree.  
IS NOT: the latest file open in the editor.

**Doctrine** — locked operating rule, versioned, not re-argued each session.  
IS NOT: chat opinion or draft.

**Artifact** — saved, versioned library deliverable.  
IS NOT: chat scratch.

**Library** — tiered `noetfield-library` SSOT/doctrine/architecture set.  
IS NOT: random notes folder.

**Lane** — scoped path for work or vendor with explicit rules.  
IS NOT: vague category.

**Kernel** — core runtime other modules attach to.  
IS NOT: any script that runs once.

**Motor** — cloud scheduler that dispatches loops (e.g. CF cron → Railway executor).  
IS NOT: the loop body itself.

**Loop** — repeating scheduled work unit with interval, cost cap, kill path, receipt per tick.  
IS NOT: unbounded “always-on,” Cursor session, or Mac launchd without motor receipt.

**Reconciler** — single owner of final state resolving conflicts.  
IS NOT: any component that touches state.

---

## §2 — Governance & census

**Governed** — explicit enforceable rules: caps, receipts, override, stop.  
IS NOT: “responsible-sounding.”

**Deploy-truth** — what is live, verified on surface/API, not disk or agent report.  
IS NOT: commit hash alone.

**Drift** — committed truth ≠ deployed/live truth (schedule, hash, route, config).  
IS NOT: “we should improve someday.”

**Fail-closed** — mismatch or missing proof → stop (exit 1, block deploy).  
IS NOT: warn and continue.

**Vendor-neutral** — no default vendor; routing earned on receipts, revocable.  
IS NOT: “agnostic” in customer text; not anti-vendor.

**Cost cap** — hard ceiling; work stops at hit.  
IS NOT: soft budget.

**Kill criteria** — written pre-pilot thresholds that end pilot if missed.  
IS NOT: post-hoc judgment.

**Escalation ladder** — fixed tier order (L1 → L1B → L2 …).  
IS NOT: “use the biggest model when unsure.”

**Least-knowledge** — agent gets minimum data/access for the task.  
IS NOT: load entire library.

**GUARD** (census) — loop/receipt protects system integrity (verify, probe, audit).  
IS NOT: META self-grooming.

**REVENUE** (census) — loop/receipt serves stranger → payment / lead / delivery path (R≥1).  
IS NOT: internal factory inbox drain.

**META** (census) — loop/receipt serves system self-maintenance without direct R path.  
IS NOT: excuse for unbounded cost.

**NONE** (census) — no named receipt consumer 14+ days → propose retire.  
IS NOT: “keep running just in case.”

**FIX / RETIRE** (census verdict) — FIX only if GUARD or REVENUE consumer; else RETIRE, do not repair.  
EX: “workflow_audit FIX; inbox RETIRE.”

**R≥1** — first payment receipt from a stranger (UNLOCK north star).  
IS NOT: internal test or founder self-pay.

---

## §3 — Roles

**Founder** — Sina; approves irreversible only.  
**Architect** — design/review/delete unnecessary work; not feature coder.  
**Worker** — ships change; not decider.  
**Brain** — deterministic router; not LLM guess.  
**Adversarial review** — try to break the plan; consensus triggers harder check.

---

## §4 — Doctrine shorthand

**Soup vs raw** — LLM probabilistic vs deterministic exact layer.  
**Return-on-cognition** — best move often deletes work.  
**Targets vs blockers** — only genuine harm stops; else improve next tick.  
**Split-brain** — two live copies both think canonical.  
**Tombstone** — mark retired; never treat as live.  
**Zero-founder validation** — system proves itself without founder in loop.  
**Receipt ladder** — L0–L4 unlocks by receipts, not diagrams.

---

## §5 — Commercial (public-safe)

**Selective** — few partners, evidence-chosen; standards not snobbery.  
**Commercial alignment** — deal structure umbrella (NDA scope).  
IS NOT: “free API” ask.

**Governed reference environment** — provable receipt-backed setup for diligence.  
IS NOT: unprovable “client base.”

**Structured commercial participation** — revenue-share phrase; NDA only.  
**Design partner** — scoped early pilot; not locked customer.  
**NDA** — before numbers, volumes, private architecture.  
**Reserved commercial figure** — contract `[●]` only; never public.

**Diagnostic** — audit/assessment engagement; findings not live enforcement.  
IS NOT: “firewall deployed” unless customer receipt proves it.

---

## §6 — Synonym → canonical

```
agnostic / model-agnostic     → vendor-neutral
free API (as ask)             → commercial alignment
client base (unprovable)      → governed reference environment
log / it worked               → receipt (if fielded) else claim
the latest file               → SSOT
always-on / full auto 24/7    → governed loop + motor + receipt (or say what is NOT 24/7)
governed (decorative)           → governed (only if stoppable + measured)
24/7 (marketing)              → name the motor + receipt or downgrade claim
```

---

## §7 — Banned register

Never emit: `we need` · `desperate` · `revolutionary` · `game-changing` · `next-gen` · public `%` economics · unprovable customer roster · needy tone.

Customer tone: plain institutional English; state what we do; cut overclaim.

---

## §8 — Versioning

Terminology rows are **minted from** dictionary entries — never authored standalone.

Add/change: dictionary entry first (founder lock) → mint or update terminology line here → bump `NOETFIELD_TERMINOLOGY_v1` version in same change set.  
This file beats prompt shorthand and model habit on **word choice**; dictionary beats this file on **meaning**.
