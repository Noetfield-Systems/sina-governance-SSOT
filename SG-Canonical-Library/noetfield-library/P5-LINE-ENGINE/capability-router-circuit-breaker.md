# LINE ENGINE — CAPABILITY ROUTER + CIRCUIT BREAKER (dispatcher, not brain)

**Status:** Dispatch mechanism. Source: Cloud Kernel v1.3 §10.
**First written:** 2026-07-03 12:34 PDT

## Reclassified in v1.3: the Router is a DISPATCHER, not the brain
The contract already decided what is allowed. The Router only picks a **provider** for a capability+SLA, and protects the system with a circuit breaker. Models are interchangeable behind it.

## Economic routing (the ROC/cost principle applied)
- **80–85% · High Volume** → Gemini Flash-Lite / DeepSeek V4 Flash. Intake, validation, logging, structured inputs. Minimal cost. Live today via OpenRouter + Cursor pools.
- **15–20% · Advanced Logic** → Claude Sonnet / Grok 4.1 Fast. Governance, Forge code-gen, multi-layer planning, final audits.

> Principle (from IDE lane): **strong model plans; cheap agents execute; verifier proves; aggregator composes.** Expensive intelligence for understanding/decomposition/conflict/final-review — not every execution token.

## Circuit breaker (explicit requirement in v1.3)
After N consecutive failures a provider is tripped open → traffic fails over to the declared fallback → breaker half-opens on a timer to test recovery.
```js
async function resolve({ capability, sla }) {
  const config = await db.getCapabilityConfig(capability);
  const provider = selectProvider(config, sla);
  if (circuitBreaker.isOpen(provider)) return config.fallback ?? escalate(capability);
  return provider; // half-open probe restores it
}
```

## Relation
- Model-agnostic (D-8): the router IS the swap point — rented→self-hosted is a config change here.
- Layered-agents: the router is the L2-orchestration gate that assigns work to L3 workers.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Router=dispatcher not brain; economic tiers 80-85% cheap / 15-20% advanced; circuit breaker. From Kernel v1.3 §10.*
