# DOCTRINE — NEGATIVE PROOF (prove a gate by rejection)

**Status:** Load-bearing verification law. Derived from WORK_ORDER_IDE_LANE §10.
**First written:** 2026-07-03 12:34 PDT

## The law
**A gate is proven by a deliberately-failing input it REJECTS — not by prose asserting it works.** Negative proof, not positive assertion.

## Why
Anything can *claim* to work. A verifier that only ever sees passing input has never demonstrated it can catch a failure — it might be a pass-through. The only proof a gate has teeth is watching it **reject a thing that should be rejected.** (This is anti-theater applied to gates themselves: don't trust the gate's self-report, make it demonstrate rejection.)

## The mechanism
- For each gate G1..Gn, run a **deliberately failing test commit/input** that violates exactly what the gate guards.
- The gate must reject it, and the rejection is captured as a receipt (negative-proof receipt).
- Negative-proof runs on **disposable branches** (`gate-test/*`), never on `main` or a production lane; branches deleted after the rejection receipt is captured.
- A gate with no negative proof is treated as **unproven** (= FAIL), not "probably fine."

## Application
- Substrate verifier: prove it FAILs a malformed/bad artifact (already demonstrated: malformed bundle → FAIL → gate refused → live unchanged).
- IDE lane G1–G6: each demonstrated by a failing commit it rejects (WORK_ORDER acceptance criterion #1).
- Line Engine: every line's verify profile carries its negative-proof set.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Prove gates by the failing input they reject, on disposable branches, captured as receipts; unproven = FAIL.*
