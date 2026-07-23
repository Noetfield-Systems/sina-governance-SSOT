# FOUNDER REASONING CONTINUATION DOCTRINE — LOCKED v1

**Version:** v1.0.0_locked_20260710  
**Status:** LOCKED / RATIFIED  
**Authority:** Master SSOT §0.7; D5 motor plane  
**Plane:** P8-MACHINE-LOOPS  

---

## Law

Escalation is **continuation**, not termination.

Wrong terminal pattern (forbidden):

```text
cheap route fails → HANDOFF_REQUIRED → stop
```

Correct pattern (required):

```text
99% automatic low-cost execution
→ 1% Founder Reasoning Queue
→ resolution in subscription surfaces (Custom GPT / ChatGPT / Claude / etc.)
→ structured result ingestion
→ motor resumes without manual branch/workflow restart
```

---

## Park vs stop

| State | Meaning | Highway |
|---|---|---|
| `WAITING_FOR_FOUNDER_REASONING` | Dependent job blocked on `packet_id` | Independent branches **continue** |
| `HANDOFF_REQUIRED` (bare) | **INVALID** without `packet_id` + queue stage | Treat as custody violation |
| `SKIPPED_LLM` / `PARTIAL` | LLM layer absent; deterministic layer completed | Motor **continues** |
| `BLOCKED_WITH_REASON` | Hard gate (e.g. deploy-truth HOLD) | Scoped block only |

One escalation must not park the entire motor unless all active work shares the same dependency.

---

## FOUNDER_REASONING_PACKET (minimum fields)

- `packet_id`, `job_id`
- problem statement, objective, work done, evidence/receipts
- cheap-route failure receipts
- diffs / related files
- remaining ambiguity
- exact question, options, risks/costs per option
- required response schema + verification contract
- return instruction for ingestor

---

## RESULT_INGESTION (minimum)

Ingestor validates schema + authority, then motor:

```text
result received → schema validation → authority validation
→ repair/build job → execute → verify → continue
```

Founder must not manually re-dispatch branch/workflow after submit.

---

## Subscription vs API automation

```text
Premium API automation as standing worker     ❌
Subscription-based founder reasoning console  ✅
```

Founder already pays subscription marginal cost; motor must not auto-invoke expensive API for heavy reasoning.

---

## Relation to other P8 loops

- Merge authority `MERGE-T3` (founder-only governance) is **orthogonal** to reasoning queue.
- 5-stage loop CONTROL/VERIFY stages still apply; continuation doctrine governs **what happens after cheap routes fail**.

---

*v1.0.0_locked_20260710*
