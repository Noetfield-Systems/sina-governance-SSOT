# ARCHITECTURE — LAYERED AGENTS (not every agent reads every rule)

> **STATUS: DERIVED / read-surface.** The AUTHORITATIVE locked law is `P0-FOUNDATION-SPINE/AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE_SSOT_LOCKED_v1.md` (Tier 0/1/2/3 + Need-to-know access + dispatch contract). This doc is the doctrine-layer expansion; on any conflict, the P0 locked law wins. Authority = SG registry, not file existence.


**Status:** Core architecture decision. Governs how agents are scoped and how layers connect.
**Owner:** Sina Kazemnezhad — System Architect
**First written:** 2026-07-01 00:44 PDT

---

## 0. The principle in one line

**No agent reads every rule. Each agent knows only its layer, runs a scoped mission, and the gates/transformers between layers translate and enforce — so no single agent carries the whole system.** This is the human-org model applied to agents: layered roles, not omniscient workers.

---

## 1. The problem this solves

A system where every agent must understand every layer is impossible:
- It overloads each agent (same reason the main brain must be **light** — base model, knows *the system* not the whole world, not language-soup).
- It makes every agent a single point of total failure (any agent can misapply any rule).
- It's not how any working organization operates — a warehouse worker doesn't read the board minutes; a surgeon doesn't run payroll.

**You cannot trust an agent with everything, exactly as you cannot trust a human with everything.** Trust is *scoped*: an agent is trusted *within its layer and mission*, not globally. The architecture must enforce scope, not hope for it.

---

## 2. The model: layers, missions, gates, transformers

```
LAYER N   (higher: intent / meaning / decision)
   │  ▲
 GATE ─ TRANSFORMER   ← translates Layer N's output into Layer N-1's input;
   │  │                  enforces what may cross; strips what must not.
   ▼  │
LAYER N-1 (lower: execution / production)
```

- **Layer** = a level of the system (meaning, decision, production, delivery, measurement). Each has its *own* rule-set — small, scoped, sufficient for that layer.
- **Mission** = an agent's scoped job *within one layer*. The agent reads only its layer's rules + its mission spec. Nothing else.
- **Gate** = a checkpoint between layers. Enforces what may pass up or down (author≠subject, claims-in-approved-set, identity, safety). An agent cannot cross a layer boundary except through a gate.
- **Transformer** = the translator at the boundary. Converts one layer's language into the next layer's language, so a lower agent never needs to understand the higher layer's meaning — it receives an already-translated, scoped instruction.

**Result:** each agent is light, replaceable, and safe-by-scope. Understanding lives in the *layer structure and the gates*, not in each agent.

---

## 3. The layers (initial map)

| Layer | Knows | Mission examples | Rules it reads |
|---|---|---|---|
| **L0 — Floor / Substrate** | nothing about product; only identity/safety | verify, gate, kill-switch, receipts | the immutable floor only |
| **L1 — Meaning / Decision (the brain)** | the system's locked definitions (light, not the world) | classify intent, select allowed claim, choose route | locked-definitions + objective |
| **L2 — Orchestration** | which line/mission, budgets, gears | spawn/route plans, allocate, enforce bounds | line configs + bounds |
| **L3 — Production (workers)** | only their scoped task | draft copy, run research, write code, critique | their task spec only (NOT the definitions, NOT the strategy) |
| **L4 — Delivery / Surface** | how to ship to a surface | push to site/repo/outbound, sanitize output | surface rules + forbidden-public |
| **L5 — Measurement** | what "produced" means | compute ROI, freshness, behavior-pass | metric definitions only |

**Key:** an L3 producer (e.g. Llama drafting copy) reads **only its task spec** — not the locked definitions, not the strategy, not the claims policy. It receives a *transformed* instruction ("write X in tone Y, assert only Z") from the L1 brain via a transformer, and its output passes back through a gate/sanitizer. **The soupy worker never sees or holds the meaning** — it can't drift what it never receives. (This is the soup-wall, generalized: every layer boundary is a soup-wall.)

---

## 4. Why this makes the whole system trustworthy

- **Blast radius is layered.** A compromised/drifting L3 worker can only affect its scoped task; the gate above it catches bad output; it never touches L1 meaning or L0 floor.
- **Determinism is preserved where it matters.** L1 (the brain) is deterministic and light; L3 workers can be soupy/probabilistic because their output is gated and they hold no meaning. You get determinism at the decision layer and flexibility at the production layer.
- **Agents are replaceable.** Any L3 worker (any model) can be swapped — it holds nothing persistent. Meaning lives in L1's locked definitions, not in the workers.
- **No omniscience required.** No agent needs the whole constitution. Each reads its layer's small rule-set. The system's intelligence is in the *structure* (layers + gates + transformers), not in any single agent.

---

## 5. The gate/transformer contract (what crosses a boundary)

Every layer boundary has a gate + transformer that enforces:

1. **Author ≠ subject** — the agent producing cannot be the agent verifying its crossing.
2. **Translation** — the instruction is converted to the receiving layer's language; the receiver never needs the sender's context.
3. **Scope enforcement** — only what's permitted crosses (approved claims, allowed routes, non-forbidden terms). The rest is stripped/blocked.
4. **Receipt** — every crossing leaves a record.
5. **Directionality** — downward = enforcement (meaning → execution, translated + constrained); upward = proposal (execution → meaning, as a *proposal only*, never a direct edit — see bidirectional-nervous-system doctrine).

**Downward:** L1 decides → transformer converts to L3 task spec → gate strips forbidden → L3 executes.
**Upward:** L3 hits a failure → emits a *proposal* upward → gate/council → L1/founder decides whether meaning changes. L3 never edits L1.

---

## 6. The human analogy (why this is the right model)

Trust an agent like a human in an org:
- A **worker** (L3) gets a scoped task, does it, doesn't set strategy.
- A **manager** (L2) routes work and enforces budgets, doesn't redefine the mission.
- The **executive/brain** (L1) holds the meaning and decides direction.
- **Compliance/audit** (L0) verifies independently, can stop anything unsafe, sets no strategy.
- **Translators** (transformers) sit between levels so a worker never needs the board's context.

You'd never hand every employee the full constitution and hope they each apply it correctly. You scope roles, put checkpoints between them, and translate context down. Same for agents — enforced in structure, not hoped for.

---

## 7. Application to current build

- **The main brain (L1)** = light, deterministic, reads only locked-definitions — *not* the whole world. Correct as designed.
- **Llama / API workers (L3)** = receive transformed task specs, hold no meaning, output gated by the sanitizer (soup-wall). Correct as designed.
- **The verifier (L0)** = independent, reads only identity/safety, verifies crossings, sets no strategy. Already built.
- **Line orchestration (L2)** = routes plans, enforces bounds, doesn't redefine claims. Line Engine §.
- **What to build:** make every layer boundary an explicit gate+transformer with the §5 contract — so no agent ever reads outside its layer, and every crossing is translated + gated + receipted.

---

## 8. One line
**Layers, not omniscience: each agent knows only its layer and mission; gates and transformers between layers translate and enforce so no agent carries the whole system. Meaning lives in the structure (L1 brain + gates), not in the workers — which makes soupy workers safe, the brain light and deterministic, agents replaceable, and blast radius contained. Trust agents like humans in an org: scoped roles, checkpoints between, context translated down.**

---
*v0.1 (2026-07-01 00:44 PDT) — first write. Layered-agent architecture: layers/missions/gates/transformers, the layer map, gate contract, human-org analogy, applied to current build. Generalizes the soup-wall to every layer boundary.*
