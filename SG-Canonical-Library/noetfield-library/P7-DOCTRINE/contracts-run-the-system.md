# DOCTRINE — CONTRACTS RUN THE SYSTEM (LLMs only propose)

**Status:** Governing principle. Source: Cloud Kernel v1.3 (governing principle, external review 9.3/10).
**First written:** 2026-07-03 12:34 PDT

## The law
**Contracts run the system. LLMs only propose plans. The kernel holds absolute execution authority.**

The LLM is a *suggestion engine* — it breaks task intent into a structured plan (JSON DAG, never free-form action). The **Execution Contract** decides what tools are allowed, what output is valid, what cost is permitted, what rollback is required. When the contract is right, the model behind it (Claude/Gemini/DeepSeek/Grok/local) is **fully swappable.**

## Why (connects to soup/raw + layered-agents)
- An LLM that *runs* the system imports its soup (drift, invented meaning, compliance theater). An LLM that only *proposes* is walled: its proposal passes through the contract gate before anything executes.
- This is the soup-wall at the execution layer: the model proposes language/plan; the contract (deterministic) decides; the executor runs the exact call. Decision authority never lives in the model.

## Specialization rule
Specialization occurs in the **configuration layer** (Data Graph / Blueprints), **not** in the infrastructure layer (Workers / Code). Workers are muscle, never brain. The brain is the Execution Contract stored in the Data Graph.

## The 4 pillars (Kernel §2)
- **P1 Product Layer** (UI/Config) — business skins (Forge, Noetfield, TrustField, WitnessBC, 777). Zero custom infra.
- **P2 Governance Layer** (Policy/SLA) — validation loops, compliance, SLA definitions. The unyielding rules.
- **P3 Runtime Kernel** (Stateless Workers) — blind execution muscle taking structured commands.
- **P4 Factory Data Graph** (Supabase/Neon) — the connected multi-tenant ecosystem, orchestrated via the Data Graph.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. Contracts hold execution authority; LLMs propose only; specialization in config not infra; the 4 pillars.*
