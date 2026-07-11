# COST EXECUTION DOCTRINE — LOCKED v1

**Version:** v1.0.0_locked_20260710  
**Status:** LOCKED / RATIFIED  
**Authority:** Master SSOT §0.7; P8 continuation doctrine  
**Plane:** P10-PRODUCT-LAYERS (motor cost law)  
**Note:** Customer-facing FinOps vocabulary remains in `agentic-cost-governance-SSOT.md` (draft, separate scope).

---

## Automatic path (binding)

```text
cheapest capable (COST-T0)
→ next cheap capable (COST-T1)
→ bounded medium-cost API (COST-T2)
→ FOUNDER_REASONING_QUEUE
```

Selection inputs: capability, health, reliability, estimated cost, remaining budget, latency, context size — all receipt-backed where material.

---

## COST tier definitions (motor lanes)

| Tier | Name | Allowed work | LLM |
|---|---|---|---|
| **COST-T0** | Deterministic | checks, tests, scans, queues, CI, rules, schemas, search | none |
| **COST-T1** | Intel-low | classification, extraction, skeleton, draft patch, summary, initial diagnosis | free / very low-cost APIs only |
| **COST-T2** | Intel-bounded | stronger API routes | capped, approved bindings only; requires T0/T1 insufficiency receipts |
| **Queue** | Founder reasoning | ambiguity, hard architecture | subscription surfaces only — **not** auto API |

Provider names (OpenAI, Gemini, DeepSeek, Copilot, etc.) live in **private deployment bindings** only — never in canonical motor law.

---

## Limits (binding)

1. Expensive API **off** as standing automatic worker.
2. Automatic Copilot / premium surface use: receipt-gated, hard-capped, justified per job.
3. API keys: hard daily + monthly caps.
4. Failed cheap route: reroute or escalate — **no blind identical retry**.
5. Quality drop on cheap model: reroute within tier or escalate to queue.
6. LLM eval/sourcing loops without key: `PARTIAL` or `SKIPPED_LLM` — **not** hard fail of deterministic loops.

---

## Work split (motor)

| Work | Path |
|---|---|
| check, test, scan, queue, CI | COST-T0 |
| extraction, classification, skeleton | COST-T1 |
| ordinary patch + simple repair | COST-T1/COST-T2 + deterministic verify |
| real ambiguity / hard architecture | FOUNDER_REASONING_QUEUE |
| commercial decision, pricing, irreversible authority | Founder DECIDE (0.2) |
| apply result + continue | automatic motor post-ingestion |

---

## Degradation vocabulary (receipts)

| State | When |
|---|---|
| `PASS` | Deterministic + optional LLM layer succeeded |
| `PARTIAL` | Deterministic complete; LLM layer failed or absent |
| `SKIPPED_LLM` | LLM not configured; deterministic path only |
| `LLM_PROVIDER_NOT_CONFIGURED` | Explicit reason code for missing provider binding |

Deterministic loops (health, deploy-truth, asset-gate, CASL gate, receipt sink, status checks) **must not** require any LLM key.

---

*v1.0.0_locked_20260710*
