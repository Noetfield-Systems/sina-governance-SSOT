# MACHINE LOOPS — THE 5-STAGE CONTROLLED RUNTIME LOOP

**Status:** Core runtime pipeline. Source: Cloud Kernel v1.3 §5.
**First written:** 2026-07-03 12:34 PDT

## The loop
Every computational step runs a strict pipeline. Without it: probabilistic execution. With it: a controlled runtime machine.
```
PLAN → CONTROL → EXECUTE → VERIFY → COMMIT
(LLM)  (gate)    (determ.)  (validator) (state engine)
```

## Nesting inside the Mac belt (L0)
In production this loop **nests inside the Mac belt's SHIP step** — it fires only after the founder gate (PROVE) clears:
```
Mac belt: SCAN → SAY → PICK → PROVE → SHIP
                                        └─ SHIP triggers ↓ (cloud only, after PROVE gate clears)
Cloud kernel:            PLAN → CONTROL → EXECUTE → VERIFY → COMMIT
```

## The 5 stages
1. **PLAN (Suggestion Engine)** — LLM breaks intent into a structured DAG. Structured JSON only, never free-form.
2. **CONTROL (Gate/Policy)** — input validated against contract schema; permissions, tool allowlist, SLA cost-guards enforced. On failure: reject or rewrite.
3. **EXECUTE (Deterministic Muscle)** — exact programmatic call. Zero creativity/prompt-alteration/guessing: only tool(input)→output.
4. **VERIFY (Validation Loop)** — output checked vs validation contracts (size/schema/token limits). On failure: backoff retry or escalate.
5. **COMMIT (State Engine)** — verified state finalized: assets as Artifacts, reasoning as Evidence, outcomes as Decisions, realtime signal to L1.

## Relation
This is the Line Engine's plan→produce→verify→ship→measure, mapped to the kernel's naming, gated by L0's PROVE (founder). Same 5-stage skeleton everywhere.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. PLAN→CONTROL→EXECUTE→VERIFY→COMMIT nested inside Mac belt SCAN→SAY→PICK→PROVE→SHIP. From Kernel v1.3 §5.*
