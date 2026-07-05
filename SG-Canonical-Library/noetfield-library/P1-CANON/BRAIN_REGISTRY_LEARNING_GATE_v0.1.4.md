# SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1

Version: v0.1.4
Created: 2026-06-29
Last edited: 2026-06-29 17:53 PT
Edit log:
  v0.1.1 — initial spec (registry, layer map, mutation classes, learning_record schema)
  v0.1.2 — added Phase 1/2/3 sequencing, base-model vocabulary founding principle, living-system framing
  v0.1.3 — corrected "no competing definitions" → "subordinate to statistical priors" (technical accuracy fix)
  v0.1.4 — fixed R1–R7 domain conflict: scoped vocabulary layer to D4-portable R1/R2/R6/R7 only, excluded R3/R4/R5 and AUDIT/EXECUTE from brain vocabulary


**Status:** Discovery + Spec (bounded) — PHASE 1: CONFIGURATION ONLY
**Owner lane:** Forge Factory foundation
**Explicitly out of scope:** base-model training, candidate model checkpoints, canary/shadow model infra, broad rebuild, active mutation proposals (Phase 2), live brain promotion (Phase 3)

---

## 0. Founding Principle — Base Model as Blank Vocabulary Slate

SourceA's base model (open-source pretrained) has no SourceA-authoritative operational definitions. It may contain statistical language priors from pretraining, but inside SourceA those priors are subordinate to SSOT v6 + D4-portable Runtime Rules R1/R2/R6/R7. SourceA vocabulary wins. This is the architectural advantage. Cursor and assistant-tuned models arrive with pre-baked operational vocabulary — their definition of "done," "verified," "approved," "complete" — and that vocabulary fights founder instructions. The result is compliance theater: the model performs following an order while defaulting to its own prior meaning.

A base model has no SourceA-competing authoritative definitions. That means:

**SSOT v6 (strategy-ssot-v6-split.md) and the D4-portable Runtime Rules (R1, R2, R6, R7) are not governance documents sitting beside the model. They are the model's first-class language definitions.**

Every term in those documents — `SUBMITTED`, `PASS`, `FAIL`, `BLOCKED`, `GATED`, `LOCKED`, `DECIDE`, `VERIFY`, `RECEIPT`, `SPEC`, `CHECK`, `CRITIQUE` — becomes operational vocabulary with no competing prior. The CONSTITUTION (Level 0) is not a policy the model obeys reluctantly. It is the model's definition of what those words mean.

**R3/R4/R5 are excluded from this vocabulary layer.** Those rules (mode switch, prompt size law, dirty file law) govern founder-assistant daily conversation — the control panel — not agentic brain state. `AUDIT` and `EXECUTE` (R3's terms) are control-panel conversational modes, not brain vocabulary, and must not be loaded into the base model's operational language. They may be referenced only in artifacts governing direct founder-assistant prompt behavior.

**Consequence for the Brain Registry:** The LOCKED mutation class does not just mean "high risk, needs human approval." It means **"this is a word definition — changing it changes what the model means by everything downstream."** SSOT v6 Level 0 and R1/R2/R6/R7 are LOCKED not because they are sensitive, but because they are the semantic foundation everything else runs on.

**Consequence for implementation:** SSOT v6 and the D4-portable Runtime Rules must be loaded as the model's context layer before any other asset. They are not configuration — they are language.

---

## 0.1 Phase Sequencing — Three Phases, v0.1 Is Phase 1 Only

```
PHASE 1 — CONFIGURATION (this document / v0.1)
  Register what exists. Tag layers. Bind evals to assets.
  Load SSOT v6 + D4-portable Runtime Rules (R1/R2/R6/R7) as vocabulary layer.
  Define mutation classes. Define learning_record schema.
  Stub mutation proposal path — defined but NOT activated.
  No active mutations. No sandbox proposals touching live brain.
  No promotion. No improvement trials.

PHASE 2 — IMPROVEMENT TRIALS (parallel sandbox, future)
  Learning records active and populated.
  Prompt-forge mutation proposals run in sandbox only.
  Gate reviews operate. No live brain contact.
  Phase 2 opens only after Phase 1 registry is complete and verified.

PHASE 3 — SAFE IMPLEMENTATION (gated promotion, future)
  Promotion path activates.
  Receipt-backed. Rollback-pointed. Human-approved via canvas form.
  Live brain updates only after Phase 2 proves the loop in sandbox.
```

**v0.1 delivers Phase 1 only.** The mutation proposal mechanism (Task 5/5b) is defined and built but remains in STUB state — no proposals are submitted, no gate reviews triggered, no promotions occur — until Phase 2 is explicitly opened by founder decision.

---

## 0.2 SourceA Is Already a Living System

The Ecosystem Agentic Living System diagram confirms: Brain OS/Registry, Plan registry, Traceability machine, Receipts + telemetry, Evidence manifest, Knowledge/memory already exist in the SourceA Shared Authority Layer. This registry does not build infrastructure. It **observes, registers, and governs what already exists.** The crawl in Task 1 is not discovery of a blank slate — it is inventory of a live system.

---



SourceA already has a large surface of brain assets — evals, SSOTs, incidents, validators, routes, skills, prompts, receipts, pipelines — built before SourceA existed as a product. These assets are currently **unregistered**: they exist, but nothing maps which layer they belong to, what they protect, what's allowed to mutate them, or how a correction becomes a structured learning record.

This phase does not build new intelligence. It makes existing intelligence **legible and governable**, so that 24/7 automation has something safe to mutate against.

---

## 1. OBSERVE — Asset Inventory

Goal: produce a flat inventory of every existing brain asset, regardless of where it currently lives (Cursor rules, Supabase tables, repo files, incident docs, eval scripts).

For each asset, capture:

| Field | Description |
|---|---|
| `asset_id` | Stable unique ID |
| `asset_type` | eval / ssot / validator / route / skill / prompt / receipt_schema / pipeline / incident_record |
| `current_location` | file path / table / repo |
| `owning_layer` | see Section 2 |
| `status` | active / stale / duplicate / orphaned / unknown |
| `last_modified` | date |
| `dependents` | what else references this asset (if known) |

**Discovery method:** crawl `.cursor/rules/`, the forge-factory-stations repo, Supabase schema, incident docs, and the eval scripts behind `sourcea-boot`. Output is a single inventory table — no judgment calls about merging or deleting yet. This step is allowed to surface "unknown" status liberally; the registry doesn't need full classification on pass one.

---

## 2. LAYER MAP — Where Each Asset Belongs

Adopt the gate stack already implicit in SourceA's existing eval culture:

```
BOOT          → session readiness (policy_version, provider, receipt_fresh, queue_truth)
CONSTITUTION  → locked meanings (SSOT, founder rules) — high mutation barrier
SSOT/RAG      → truth consistency, source-of-record docs
ROUTER        → task routing rules (which station handles what)
AGENT         → execution behavior per station
CRITIC        → catches weak/fake/dangerous output
RECEIPT       → proof-of-run schema
TAMPER        → corruption/integrity detection
REGRESSION    → "old wins preserved" checks
PROMOTION     → gate for anything entering live (future lane, stub only in v0.1)
```

Every inventoried asset gets tagged with exactly one primary layer (secondary tags allowed but one primary owner). Assets that don't fit cleanly are flagged `layer_unknown` rather than forced into a bucket — this is itself useful signal.

---

## 3. MUTATION CLASS — What Can Change and How

Three classes, not a spectrum:

- **LOCKED** — Constitution, founder rules, core SSOT. Mutation requires explicit human approval every time, regardless of who/what proposes it. No autonomous path, ever.
- **GATED** — Router rules, prompts, validators, eval thresholds, RAG links. Sandbox agents may *propose* mutations. Nothing lands without Decision Gate approval + receipt.
- **OPEN** — Logs, incident records, draft learning records. Can be written/appended automatically without gate review (the gate reviews what's *derived* from them, not the raw log itself).

  OPEN assets may be written automatically only if the write passes schema validation, required-field validation, timestamp/source attribution, and append-only enforcement. No raw OPEN write may overwrite history.

Each asset's `mutation_class` is added to the registry alongside its layer tag.

---

## 4. EVAL ↔ ASSET BINDING

For every eval already in existence (the `sourcea-boot` four checks and any others found in discovery), record:

- which asset(s) it protects
- what failure mode it's catching
- whether it currently runs at boot, per-task, or ad hoc

This produces the **Eval Registry** — not new evals, just a map of existing ones to what they actually guard. Gaps (a GATED asset with no eval protecting it) get logged as `eval_gap`, not fixed in this phase.

---

## 5. LEARNING RECORD SCHEMA

Defines how an incident/failure/correction becomes structured data, without yet doing anything automated with it.

```
learning_record {
  record_id
  source_event        // incident id, failed task id, manual flag
  layer                // which gate-stack layer this touches
  asset_affected        // asset_id from registry, if known
  failure_description
  proposed_correction   // free text or structured patch, station-agnostic
  ssot_consistency_check // bool — does correction conflict with locked SSOT?
  critic_reviewed        // bool
  status                 // draft / proposed / approved / rejected / promoted
  receipt_id              // linked once anything moves
}
```

This schema is the **only** new thing being built in v0.1 beyond the registry itself. It doesn't move learning records anywhere automatically yet — it just gives every future incident a consistent shape.

---

## 6. MUTATION PROPOSAL PATH (sandbox agents)

**Lane sequencing (not all in v0.1):**

```
v0.1 — prompt forge config proposals       (this phase — lowest blast radius)
v0.2 — router rule proposals
v0.3 — validator / eval threshold proposals
future — adapter / base-model candidate lanes
```

v0.1 implements the mechanism below for **prompt forge configs only**. Router rules, eval thresholds, and SSOT/RAG links remain GATED but have no active proposal path yet — they get layer-tagged and registered in this phase, not opened to mutation.

Sandbox agents (Cursor/Codex) may, for prompt forge config assets only in v0.1:

1. Read a `learning_record` with `status: draft`
2. Generate a proposed patch to the affected prompt forge config only.
3. Write the patch as `status: proposed` — never apply directly
4. Decision Gate reviews: SSOT-consistent? Critic-approved? Regression-safe (does it break an existing passing eval)?
5. On approval → receipt written → asset updated → `status: promoted`
6. On rejection → `status: rejected`, reason logged, learning record stays for future reference

No step here touches a model checkpoint. "Candidate" = a config diff, full stop.

---

## 7. RECEIPT REQUIREMENT

Every promoted mutation gets a receipt matching SourceA's existing receipt pattern (consistent with the kernel's Decision Gate + receipt writer already in place): what changed, which layer, which eval/critic approved it, timestamp, rollback pointer to the prior asset state.

---

## 8. EXPLICIT STOP CONDITIONS for v0.1

This phase is done — and should be called done — when:

- [ ] Asset inventory exists and covers known locations (Cursor rules, repo, Supabase, incident docs)
- [ ] Every asset has a layer tag (or `layer_unknown`) and mutation class
- [ ] Eval Registry maps existing evals to assets they protect, with gaps logged
- [ ] `learning_record` schema is implemented and incidents can be logged into it
- [ ] Mutation proposal path is defined and gated for at least one asset type (recommend starting with prompt forge configs — lowest blast radius)
- [ ] Receipt schema for mutations is specified

**Do not proceed past this list into:** training data pipelines, model checkpoints, canary/shadow deployments, automated promotion without human review on LOCKED-adjacent assets. Those are a named future lane, not part of v0.1.

---

## 9. Sequencing Note

This sits inside Forge Factory foundation, in parallel with — not competing against — Video Ad Factory. Recommended split: Codex sandbox time on registry discovery/crawl (mechanical, scriptable), your review time on layer-tagging the LOCKED/CONSTITUTION-tier assets only (judgment calls Codex shouldn't make alone).
