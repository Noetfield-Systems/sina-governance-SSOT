# NF-GRAPH-STUDIO-V1 — SG CONTROL LOCK

**decision_id:** `NF-GRAPH-STUDIO-V1`  
**title:** SourceA Graph Studio v1 (author / compile / observe over Executive Mesh)  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder order via Advisor architecture (Graph Studio vertical slice)  
**Tier:** P0-FOUNDATION-SPINE  
**Version:** `v1.0.0_locked_20260724`  
**Machine:** `data/nf_graph_studio_v1_LOCKED.json`  
**Depends on:** `NF-EXECUTIVE-MESH-V1`  
**Applies to:** SourceA (Graph Studio package + Worker + Studio web) · sina-governance-SSOT (lock) · Executive Mesh (runtime)

---

## One-line law

> Studio authors Blueprints; Compiler freezes plan_hash; Mesh executes pinned plans; Verifier decides reality; React Flow is UI-only.

## Hard invariants

1. **Canvas ≠ Brain** — never execute React Flow JSON.
2. **Agent ≠ Runtime** — Role Pod / Agent Team are manifests; Governor commits.
3. **Runtime ≠ Truth** — Independent Verifier + Supabase remain SSOT.
4. **Layout ≠ semantics** — positions/colors live only in Studio layout docs and never enter `plan_hash`.

## Four representations (binding)

| Layer | Role |
|-------|------|
| Node Definition Registry | Versioned Node Manifests (ports, JSON Schema, runtime binding, authority, budget, verifier) |
| Blueprint Graph | Semantic nodes/edges only (no layout) |
| Compiled Execution Plan | Validate → freeze → `plan_hash` (immutable on publish) |
| Run Graph | Live node status projected from mesh run audit |

## Composition

```text
Graph Studio =
    Node Registry + Blueprint + Compiler + Run Graph
  + Studio web (React Flow UI-only)
  + Graph Studio Worker / DO (validate / publish / run)
  → Executive Mesh Pipeline (pinned plan_hash)
  → Runway Goal Kernel + Independent Verify + Supabase SSOT
```

Do not invent a parallel SSOT, second Railway heavy executor, or generic graph interpreter that replaces Executive Mesh.

## Slice-1 vertical path (frozen blueprint)

```text
EVENT → SG Pod → Memory ContextPack → Planner Pod → Critic Pod
  → Governor → RUNWAY_GOAL_KERNEL → Independent Verify
  → Canonical Commit → Digest
```

## Ops (cloud)

| Item | Value |
|------|-------|
| Trigger host | `cloud` (Worker); publish/run API-triggered in slice-1 |
| Registry row | `loop_id=sourcea_graph_studio_pulse_v1` (reserve; wire after slice proves) |
| Deadman | `sourcea-deadman-v1` |
| Receipt | `receipts/graph-studio/` |

## Explicit non-goals (slice-1)

- Full node catalog beyond webpage-repair kinds
- Node Studio wizard / marketplace
- Redis Streams / Queues fan-out bus
- Unsupervised blueprint evolution
- Executing canvas documents
- Replacing Executive Mesh pipeline
