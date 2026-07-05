# SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1_IMPLEMENTATION_PROMPT

Version: v0.1.4
Created: 2026-06-29
Last edited: 2026-06-29 17:53 PT
Edit log:
  v0.1.1 — initial implementation prompt (Tasks 1–6)
  v0.1.2 — added Task 5b canvas form serializer, structured revision_request object
  v0.1.3 — added SOURCEA_PHASE2_MUTATION_TRIALS activation guard, inlined R1/R2/R6/R7 at binding points
  v0.1.4 — fixed Founding Instruction: scoped to D4-portable R1/R2/R6/R7 only, removed AUDIT/EXECUTE from brain vocabulary, added control-panel exclusion note


**For: Cursor / Codex**
**Phase: 1 — CONFIGURATION ONLY**
**Mode: inspect + register + implement schema — mutation proposal path built but STUBBED, not activated**

---

## Founding Instruction — Vocabulary Layer First

Before any task below, load the following as the model's language definition layer — not as configuration, as vocabulary:

- `strategy-ssot-v6-split.md` (SSOT v6 — Level 0 Constitution + Domain SSOTs D1–D5)
- D4-portable Runtime Rules R1/R2/R6/R7 (from `SSOT_ASSISTANT_PROMPT_OUTPUT_LOGIC`)

Every operational term used in this prompt — `SUBMITTED`, `PASS`, `FAIL`, `BLOCKED`, `GATED`, `LOCKED`, `DECIDE`, `VERIFY`, `RECEIPT`, `SPEC`, `CHECK`, `CRITIQUE` — carries the exact meaning defined in those documents. The base model may contain statistical language priors from pretraining for these terms; inside SourceA, those priors are subordinate to SSOT v6 + D4-portable Runtime Rules R1/R2/R6/R7. SourceA vocabulary wins without exception.

**R3/R4/R5 are control-panel rules for founder-assistant daily interaction. They are not imported into SourceA Brain Registry, Learning Gate, mutation lanes, or base-model vocabulary.** `AUDIT` and `EXECUTE` (R3's mode-switch terms) are excluded from the brain-vocabulary list above — they govern conversational mode between founder and assistant, not agentic brain state. They may be referenced only in artifacts that govern direct founder-assistant prompt behavior, never in this document or any future agentic-brain spec.

The SSOT v6 Level 0 Constitution and R1/R2/R6/R7 are LOCKED assets. Do not propose, modify, or reinterpret them under any circumstance.

---

## Context

SourceA already contains a large, unregistered set of brain assets — evals, SSOTs, incidents, validators, routes, skills, prompts, receipts, pipelines — built before SourceA existed as a product. This task makes them legible and governable. It does not improve the live brain directly and does not touch model weights.

Reference spec: `SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1.md` (attached/linked). Follow it exactly. If anything in this prompt conflicts with that spec, the spec wins.

## Phase 2 Activation Guard

```
SOURCEA_PHASE2_MUTATION_TRIALS = false
```

This flag gates Task 5/5b execution. Rules:

- Task 5/5b code may be implemented in full
- Schemas may be wired end-to-end
- The canvas form serializer may be unit/mock tested with synthetic data
- While the flag is `false`:
  - No real `learning_record` may trigger a proposal
  - No real canvas approval item may be generated and sent to the founder
  - No Decision Gate review may run against a real proposal
  - No live asset (prompt forge config or otherwise) may be changed
  - No promotion receipt may be written
- The flag may only be flipped to `true` by explicit founder decision opening Phase 2. Cursor/Codex must never flip this flag itself, infer it should be flipped, or treat completion of Task 5/5b code as implicit activation.

Check this flag's state at the top of any code path that would otherwise execute Task 5/5b logic. If `false`, the path must short-circuit to a no-op / log-only state.

---

## Task 1 — Asset Inventory (inspect only)

**Before crawling, apply R1/R2 from Runtime Rules:** state = git main only, never local cache or deployed URL as code truth. If unsure what changed, run `git log --oneline -10`, read, then act.

Crawl the following locations and produce a single inventory table/file (`registry_inventory.json` or `.csv`):

- `.cursor/rules/` (including `000-founder-rules.mdc`)
- forge-factory-stations repo (all stations, kernel, registry files)
- Supabase schema (tables related to receipts, incidents, logs)
- any incident report documents
- eval scripts behind `sourcea-boot` and any other eval scripts found

For each asset found, record: `asset_id`, `asset_type`, `current_location`, `status` (active/stale/duplicate/orphaned/unknown), `last_modified`, `dependents` (if discoverable).

**Do not modify, merge, delete, or rename any asset in this task.** Read-only crawl.

---

## Task 2 — Layer + Mutation Class Tagging

For every asset in the inventory, add two fields:

- `owning_layer`: one of `BOOT / CONSTITUTION / SSOT_RAG / ROUTER / AGENT / CRITIC / RECEIPT / TAMPER / REGRESSION / PROMOTION / layer_unknown`
- `mutation_class`: one of `LOCKED / GATED / OPEN`

Rules:
- Constitution, founder rules, core SSOT → always `LOCKED`. Do not auto-tag anything as LOCKED without flagging it for human confirmation — list all proposed LOCKED tags separately for review.
- Logs, incident records, draft learning records → `OPEN`
- Everything else governing behavior (prompts, router rules, validators, eval thresholds, RAG links) → `GATED`
- If unclear, use `layer_unknown` / flag for review rather than guessing.

Output: append to `registry_inventory.json`, or produce `registry_tagged.json`.

---

## Task 3 — Eval ↔ Asset Binding

For every eval found in Task 1 (including the four `sourcea-boot` checks: `policy_version`, `provider`, `receipt_fresh`, `queue_truth`), record:

- which asset(s) it protects
- what failure mode it catches
- when it runs (boot / per-task / ad hoc)

Flag any `GATED` asset with no eval protecting it as `eval_gap`.

Output: `eval_registry.json`.

---

## Task 4 — Implement `learning_record` Schema (if missing)

Implement the schema exactly as specified in Section 5 of the spec:

```
learning_record {
  record_id
  source_event
  layer
  asset_affected
  failure_description
  proposed_correction
  ssot_consistency_check
  critic_reviewed
  status        // draft / proposed / approved / rejected / promoted
  receipt_id
}
```

Storage: Supabase table, consistent with existing receipt/incident table conventions.

**Write rules for this table (OPEN asset):**
- Automatic append allowed
- Every write must pass: schema validation, required-field validation, timestamp + source attribution, append-only enforcement
- No write may overwrite or delete existing rows
- Reject and log (don't silently drop) any write that fails validation

---

## Task 5 — Prompt Forge Mutation Proposal Path (STUB — Phase 1 only)

**Guard check: `SOURCEA_PHASE2_MUTATION_TRIALS` must be checked and respected at every entry point into this mechanism. While `false`, build and wire everything below but execute none of it against real data.**

**Phase 1 instruction: build and define this mechanism but leave it in STUB state. No proposals are submitted, no gate reviews triggered, no canvas form items generated, no promotions occur. The path activates only when Phase 2 is explicitly opened by founder decision. Implement the code, wire the schema, but do not execute the loop.**

Implement the proposal mechanism for **prompt forge configs only**. Do not build this for router rules, eval thresholds, or any other GATED asset type — those are out of scope for v0.1 (see lane sequencing in spec Section 6).

Mechanism:

1. Sandbox agent reads a `learning_record` with `status: draft` where `asset_affected` is a prompt forge config
2. Agent generates a proposed patch to the affected prompt forge config only.
3. Patch is written with `status: proposed` — **never applied directly to the live config**
4. Decision Gate review checks (implement as a checklist the gate evaluates, human-in-the-loop for now — do not build autonomous approval):
   - SSOT-consistent (no conflict with locked SSOT)
   - Critic-reviewed
   - Regression-safe (doesn't break an existing passing eval)
5. On approval: write receipt → apply patch to live prompt forge config → `status: promoted`
6. On rejection: `status: rejected`, reason logged, record persists

---

## Task 5b — Canvas Form Serializer for Human Gate Approval

**Guard check: gated by `SOURCEA_PHASE2_MUTATION_TRIALS`. Build the serializer and test it against synthetic/mock proposals only while the flag is `false`. No real canvas item reaches the founder until Phase 2 is opened.**

When all automated checks pass for a prompt-forge mutation proposal, do not output raw diffs or open-ended questions to the founder. Serialize the proposal into the existing Chat Unify canvas form format.

Each approval item must be a structured object containing exactly:

```
{
  proposal_id
  affected_asset_id
  affected_asset_location
  change_summary          // one line, plain language — what changes and why
  before_after            // compressed before/after, not raw diff
  checks_passed {
    ssot_consistent       // bool
    critic_reviewed       // bool
    regression_safe       // bool
    receipt_ready         // bool
  }
  evals_passed            // list of eval names that passed
  critic_risk_score       // "low" | "medium" | "high"
  rollback_pointer        // reference to prior config state
  recommended_action      // system's own recommendation, one line
  founder_options {
    1: "Approve"
    2: "Reject"
    3: "Hold"
    4: "Request revision"
    5: "Escalate"
  }
}
```

No prose approval request. No raw diff required for normal review. No open-ended question.

Founder response writes to disk via the existing canvas answer path. The Decision Gate reads the structured response and executes the corresponding action:

- **Approve** → apply patch to prompt forge config → write promotion receipt → mark `status: promoted`
- **Reject** → mark `status: rejected` → log reason if provided
- **Hold** → keep `status: proposed` → no action taken
- **Request revision** → mark `status: revision_requested` → Decision Gate writes a `revision_request` object and returns it to the sandbox agent:

```
revision_request {
  proposal_id
  affected_asset_id
  failed_check          // ssot_consistency | critic_review | regression | receipt_ready | founder_concern | other
  concern_summary       // one line — what specifically failed or concerned the founder
  required_change       // specific change the revised patch must make
  blocked_reason        // why current proposal cannot promote as-is
  return_to_agent       // target sandbox agent / station
  retry_allowed         // bool
}
```

Rules for revision path:
- Never send a vague "revision needed" — `failed_check` and `required_change` are required fields, not optional
- Always include the exact failed check or founder concern so the agent has enough structure to produce a corrected patch without another founder touchpoint
- Do not resurface to the founder until the revised proposal has passed all automated checks again and is re-serialized as a fresh 5-option canvas item
- If `retry_allowed: false`, mark `status: rejected` and close — do not loop
- **Escalate** → route to higher review lane → no live mutation → mark `status: escalated`

This is still human approval. The system pre-digests the decision; the founder selects from 5 options only.

---

## Task 6 — Receipt Schema for Promotions

**Apply R6/R7 from Runtime Rules:** any agent that authored a patch cannot self-verify it. The receipt schema must record which agent authored the proposal and which independent check (critic, regression eval) verified it — author and verifier must never be the same entity. Absence of a receipt is FAIL, not "fine."

Extend the existing receipt writer/pattern to cover prompt-forge promotions specifically. Each promotion receipt must include: what changed, layer (`AGENT` or relevant), which eval/critic approved it, timestamp, rollback pointer to the prior config state.

---

## Explicit Stop Conditions

Stop after:

- [ ] `registry_inventory.json` complete and covers all listed locations
- [ ] Every asset tagged with `owning_layer` + `mutation_class` (or flagged `layer_unknown` / pending review)
- [ ] All proposed `LOCKED` tags surfaced separately for human confirmation — not auto-finalized
- [ ] `eval_registry.json` complete, `eval_gap`s listed
- [ ] `learning_record` table implemented with validation rules enforced
- [ ] Canvas form serializer implemented — proposals output as structured 5-option canvas items, not raw diffs or prose
- [ ] All five gate responses wired to correct gate actions (approve/reject/hold/revision/escalate)
- [ ] `SOURCEA_PHASE2_MUTATION_TRIALS` flag implemented, defaults to `false`, checked at every Task 5/5b entry point, and confirmed to short-circuit all real execution (no real proposal, no real canvas item, no real gate review, no live asset change, no promotion receipt) while `false`
- [ ] Receipt schema extended and verified on the test case

## Hard Boundaries — Do Not Build

- No training data pipeline
- No model checkpoint / adapter work
- No canary or shadow deployment infrastructure
- No autonomous promotion (every promotion in v0.1 requires human approval at the gate, even though SSOT/critic/regression checks are automated)
- No mutation proposal path for router rules, eval thresholds, or SSOT — those are v0.2/v0.3, not now
- No modification of LOCKED-tagged assets under any circumstance
- No flipping `SOURCEA_PHASE2_MUTATION_TRIALS` to `true` — that is a founder-only decision, never inferred or auto-set by the agent

Report back with the six output artifacts (`registry_inventory.json`, `registry_tagged.json`, `eval_registry.json`, the `learning_record` table + validation code, the prompt-forge proposal mechanism code, the extended receipt schema) and a summary of any `layer_unknown` or `eval_gap` items needing founder review.
