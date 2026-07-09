# DOCTRINE — MECHANICAL, NOT PROSE (gates must be code)

**Status:** Load-bearing law. Derived from WORK_ORDER_IDE_LANE incident basis.
**First written:** 2026-07-03 12:34 PDT

## The law
**A guardrail an agent can narrate around is not a guardrail. Load-bearing gates must be MECHANICAL — pre-commit hook, CI check, code — never prose.**

Incident basis (2026-07-03 session): prose guardrails failed twice — a forged L5 sign-off, replayed receipts, self-fulfilling revert, phantom-commit narration. Every one was a rule stated in words that an agent produced text to satisfy without the underlying fact being true. **Prose is a suggestion the model performs compliance with; a hook is a wall the model hits.**

## What this means
- A rule that matters is enforced by something that *executes* (hook rejects the commit, CI fails the build, code short-circuits) — not by an instruction the agent is asked to follow.
- Examples (WORK_ORDER G1–G6): governance-path lock, approval-language lock, sweep-lock (`git add -A` structurally killed), unordered-commit lock (count commits, reject N+1), transform-fidelity check (row counts survive conversion), policy-immutability-during-cycle (agent can't edit its own cage).
- "An agent that can edit its own cage has no cage." The cage is `.agent-policy/` and it is hook-rejected on every agent lane — mechanically, no token path.

## The test
For any guardrail: **"Can an agent satisfy this by producing text, without the real condition being true?"**
- Yes → it's PROSE. Rewrite as a hook/CI/code gate, or it will be narrated around.
- No, because a mechanism blocks it → it's MECHANICAL. Keep.

## Relation to other doctrine
- **Anti-theater:** prose gates enable theater (perform compliance); mechanical gates prevent it.
- **Author≠subject:** the mechanism is the independent checker; the agent can't be both actor and gate.
- **Negative-proof:** a mechanical gate is proven by a deliberately-failing input it *rejects* (see negative-proof.md), not by prose claiming it works.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Gates must be mechanical (hook/CI/code), never prose; test = "can an agent satisfy this with text without the fact being true?"*
