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

**Receipt** — A machine-readable record that proves what happened. It must have defined fields: who, model, cost, tokens, success, latency, time, and sink ack when applicable.  
IS NOT: a log line, chat “done,” or deploy log without live verify.  
EX: “Worker said PASS but no receipt → unverified.”

**Observation record** — A status snapshot with a schema and timestamp, such as a health check or census run. It does not contain full receipt fields.  
IS NOT: a substitute for proof receipt on customer or revenue claims.  
EX: “Fleet health pass is an observation record, not R≥1 proof.”

**Claim** — Any statement of success that does not have a structured receipt.  
IS NOT: a receipt.

**SSOT** — The single authoritative file or record when different copies disagree.  
IS NOT: the latest file open in the editor.

**Doctrine** — A locked and versioned operating rule that is not debated during a session.  
IS NOT: chat opinion or draft.

**Artifact** — A saved and versioned file or deliverable in the library.  
IS NOT: chat scratch.

**Library** — The approved set of rules, doctrine, and architecture files under `noetfield-library`.  
IS NOT: random notes folder.

**Lane** — A specific path for work or a provider that has clear rules.  
IS NOT: vague category.

**Kernel** — The core running system that other modules connect to.  
IS NOT: any script that runs once.

**Motor** — A cloud scheduler that starts loops. Examples include Cloudflare cron or a Railway executor.  
IS NOT: the loop body itself.

**Loop** — A recurring task that runs on a schedule with a set interval, cost cap, kill path, and a receipt for each run.  
IS NOT: unbounded “always-on,” Cursor session, or Mac launchd without motor receipt.

**Reconciler** — The single component that resolves conflicts and decides the final state.  
IS NOT: any component that touches state.

---

## §2 — Governance & census

**Governed** — Having clear, enforceable rules such as limits, receipts, overrides, and stops.  
IS NOT: “responsible-sounding.”

**Deploy-truth** — The actual state of the live system checked on the public page or API.  
IS NOT: commit hash alone.

**Drift** — A mismatch between the approved files and the live running setup, such as in schedule, hash, route, or configuration.  
IS NOT: “we should improve someday.”

**Fail-closed** — Stopping the process or blocking a deployment if a check fails or proof is missing.  
IS NOT: warn and continue.

**Vendor-neutral** — Using no default AI provider and routing work based on receipts, which can be canceled.  
IS NOT: “agnostic” in customer text; not anti-vendor.

**Cost cap** — A strict limit where all work stops once the spending threshold is met.  
IS NOT: soft budget.

**Kill criteria** — Predefined conditions written before a pilot that will stop it if they are not met.  
IS NOT: post-hoc judgment.

**Escalation ladder** — A fixed sequence of levels used to handle issues in order.  
IS NOT: “use the biggest model when unsure.”

**Least-knowledge** — A security rule where an agent receives only the minimum data and access needed to perform its task.  
IS NOT: load entire library.

**GUARD** (census) — A loop or receipt that protects the system by verifying, probing, or auditing.  
IS NOT: META self-grooming.

**REVENUE** (census) — A loop or receipt that directly serves an external user to generate a lead, payment, or delivery.  
IS NOT: internal factory inbox drain.

**META** (census) — A loop or receipt that handles system self-maintenance without directly earning money.  
IS NOT: excuse for unbounded cost.

**NONE** (census) — A loop with no active consumer for over 14 days, which should be retired.  
IS NOT: “keep running just in case.”

**FIX / RETIRE** (census verdict) — A decision to repair a loop only if it has a GUARD or REVENUE consumer, and to retire it otherwise.  
EX: “workflow_audit FIX; inbox RETIRE.”

**R≥1** — The first receipt of payment received from an external user.  
IS NOT: internal test or founder self-pay.

---

## §3 — Roles

**Founder** — Sina, who only approves actions that cannot be reversed.  
**Architect** — A role that designs, reviews, and removes unneeded work instead of writing features.  
**Worker** — A role that implements and deploys changes but does not make decisions.  
**Brain** — A rule-based system that routes tasks instead of using probabilistic guesses.  
**Adversarial review** — A check where other systems or people try to find flaws in a plan.

---

## §4 — Doctrine shorthand

**Soup vs raw** — A contrast between probabilistic LLM outputs and exact rule-based layers.  
**Return-on-cognition** — A principle stating that the most effective action is often to remove unneeded work.  
**Targets vs blockers** — A principle where only real damage stops a task, while minor issues are improved in the next run.  
**Split-brain** — A condition where two live instances of a system both act as the authoritative source.  
**Tombstone** — A marker used to flag retired items so they are never used.  
**Zero-founder validation** — A process where the system verifies its own state without requiring the founder.  
**Receipt ladder** — A sequence of levels unlocked only by verified receipts.

---

## §5 — Commercial (public-safe)

**Selective** — Working with only a few partners chosen based on evidence to maintain high standards.  
**Commercial alignment** — The contract and business agreement under which partners operate.  
IS NOT: “free API” ask.

**Governed reference environment** — A verifiable, receipt-backed setup that partners can inspect.  
IS NOT: unprovable “client base.”

**Structured commercial participation** — A terms-of-revenue agreement that remains confidential.  
**Design partner** — A partner in a limited early trial rather than a fully committed customer.  
**NDA** — A confidentiality agreement signed before sharing metrics, volume, or internal design.  
**Reserved commercial figure** — A confidential contract detail that is never made public.  
**Diagnostic** — An engagement focused on auditing and assessment rather than active blocking.  
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
