# PATTERN — AUTO-HEAL (zero-drift hospital policy)

**Status:** Pattern (bounded self-improvement).
**First written:** 2026-07-03 12:34 PDT

## Definition
Continuous, bounded self-repair: detect → diagnose (adversarial) → fix → verify → re-probe. A fix that doesn't move a real metric **auto-reverts.**

## The loop
DETECT (measurement/behavior-probe/health-check finds degradation) → DIAGNOSE (AI station proposes cause; second station critiques; same-base-model convergence = warning) → PROPOSE (fix to content/plan/config — NEVER substrate) → VERIFY (substrate verifier + line profile) → SHIP (per ship_policy) → RE-PROBE (confirm the fix fixed it; else revert).

## Hospital policy = zero-drift discipline
- Heal only counts if it moves a real signal (no "looks fine"; auto-revert otherwise) — kills lazy-agent theater structurally.
- Self-heal may change work; may NEVER touch the floor (immutable-floor).
- Improvement is defined by measured effect, not agent declaration.

## Buyer pain
"our system degrades silently and someone has to babysit it."

## Receipts
degradation detected → fix shipped → metric moved (or auto-reverted), logged per cycle.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Auto-heal: detect→diagnose→fix→verify→re-probe; metric-or-revert; never touches floor; hospital = zero-drift discipline.*
