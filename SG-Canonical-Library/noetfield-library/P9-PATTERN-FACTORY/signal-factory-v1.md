# PATTERN — SIGNAL FACTORY v1

**Status:** SourceA Base Brain skill (owner: SourceA Brain Agent). Architect-locked spec, worker-build pending.
**First written:** 2026-07-03 12:34 PDT

## Purpose
Triage a raw inbound signal (vendor pitch, cold email, LinkedIn DM, website form, partner/cofounder inquiry, investor note, platform alert) into a **fixed decision report**: classification, implied need, four 0–5 scores, one bounded next action, optional automation recipe, optional commercial service idea, a machine-checkable JSON receipt, one memory line.

## Trigger sources
Any inbound message — an unlabeled pasted inbound IS the trigger.

## Output contract (fixed fields)
classification · implied_need · scores{4-dim 0–5} · next_action(one, bounded) · automation_recipe(optional) · service_idea(optional) · receipt(JSON) · memory_line(one).

## Guardrails (locked)
- **risk ≥ 4 → routes to human/legal review** (no autonomous action).
- **No laundering sender claims as facts** — sender assertions stay assertions.
- **Entity hygiene** — no competitor-name leakage across product files; strict SourceA/TrustField separation.
- **Softened partner/equity milestone guardrail** — no employment offers, no equity commitments.
- **Decision-gated optional sections only** — optional sections (automation/service) render only when gate-approved (Eval 5 fix).

## Tests (six synthetic)
SEO vendor · cofounder DM · scam · custody/MSB-risk · client web-form · (Eval 5 optional-section gating).

## Receipt requirement
Every triage emits a structural-verifier-checked JSON receipt (author≠subject: the triage agent ≠ the verifier).

## Routing (this chat)
Architect = analyze/finalize (locks spec, blocker/target classification). SourceA Brain Agent = owns/adds to Base Brain. SourceA Worker = builds SKILL.md + 6 tests + structural verifier + receipt schema (no Gmail/UI yet). SG = guardrail recording only. NOOS = HOLD.

## SG guardrail lines (recorded)
no-employment · entity-hygiene · custody/MSB-risk.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Signal Factory v1 skill: purpose, output contract, guardrails, 6 tests, receipt, routing. From this chat.*
