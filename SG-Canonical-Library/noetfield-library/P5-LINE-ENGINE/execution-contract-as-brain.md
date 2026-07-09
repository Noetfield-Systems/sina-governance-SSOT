# LINE ENGINE — EXECUTION CONTRACT AS THE BRAIN

**Status:** Core kernel mechanism. Source: Cloud Kernel v1.3 §6.
**First written:** 2026-07-03 12:34 PDT

## The principle
**The Execution Contract — not the Router — is the brain.** A correct contract constrains: which tools are allowed, which output is valid, which cost is permitted, which rollback is required. When the contract is right, the model is fully swappable.

## Plan Contract (LLM output schema — the ONLY shape the LLM may emit)
```json
{ "steps": [ {
  "step_id": 1, "type": "tool_call",
  "tool": "llm | elevenlabs | ffmpeg | supabase",
  "action": "string", "input": {},
  "expected_output": "artifact | text | file | json",
  "sla": "draft | normal | premium",
  "idempotency_key": "uuid",        // MANDATORY v1.3
  "depends_on": [],
  "compensation": { "tool":"string","action":"string","input":{} }  // rollback, NEW v1.3
} ] }
```

## Control Layer — Hard Gate (before any execution)
Schema validation (steps is array, each tool in registry, no undefined actions) · Safety (no unauthorized external calls, no fs access outside sandbox, **no recursive self-modifying plans**) · Cost check (if est_cost > budget → reject/downgrade) · Idempotency & DAG (every step has idempotency_key; DAG acyclic, no missing refs).

## Rollback & Compensation (NEW v1.3)
Critical steps (external API calls with side effects) declare a `compensation` action. On failure of step N, the kernel walks completed steps in reverse and executes each compensation before marking FAILED. Makes multi-step runs safely reversible — no orphaned artifacts.

## Verify → Commit
- PASS → runs.status=success; artifacts/evidence/decisions saved; realtime signal to L1.
- FAIL → retry (max 3, backoff+jitter) → run compensations in reverse → runs.status=failed/escalate.

## Relation
This is "contracts-run-the-system" made concrete, and the substrate's gate at the execution layer. The Line Engine's VERIFY stage = this contract's Control+Verify.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Execution Contract = brain; Plan Contract schema; hard gate; compensation/rollback; verify/commit. From Kernel v1.3 §6.*
