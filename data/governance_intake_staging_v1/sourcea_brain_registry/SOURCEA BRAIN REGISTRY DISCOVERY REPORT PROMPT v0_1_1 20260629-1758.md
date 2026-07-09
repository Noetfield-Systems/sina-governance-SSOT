# SOURCEA_BRAIN_REGISTRY_DISCOVERY_REPORT_v1

Version: v0.1.1
Created: 2026-06-29
Last edited: 2026-06-29 17:58 PT
Edit log:
  v0.1.1 — initial discovery prompt, corrected from advisor draft: added vocabulary load, R1/R2 crawl-truth instruction, aligned output taxonomy to Brain Registry Task 1–3 format

**For: Cursor / Codex**
**Mode: OBSERVE → REPORT → STOP**
**Relationship to existing work:** This is the reconnaissance pass that feeds Tasks 1–3 of `SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1.4_IMPLEMENTATION_PROMPT`. It is not a parallel or competing report — its findings should already be in the vocabulary and shape that Task 1–3 expects, so they can be dropped in directly rather than re-mapped.

---

## Founding Instruction — Vocabulary Layer First

Before inspecting anything, load `strategy-ssot-v6-split.md` (SSOT v6 — Level 0 + D1–D5) and D4-portable Runtime Rules R1/R2/R6/R7 as the language definition layer for this task. Use SourceA's definitions of `eval`, `receipt`, `verified`, `SSOT`, `gate`, `layer` — not training-prior defaults. R3/R4/R5 and `AUDIT`/`EXECUTE` are control-panel terms, not brain vocabulary — do not use them to frame this report.

**Apply R1/R2 before any crawl:** `git pull origin main`. State = git main only. Never read local cache, prior session memory, or a deployed URL as code truth. If unsure what changed: `git log --oneline -10` → read → then act.

---

## Goal

Inventory SourceA as a brain-library and identify what must be registered, connected, or built for the full SourceA Brain Registry. Do not edit files. Do not create new architecture. Do not implement. Do not commit. Do not flip `SOURCEA_PHASE2_MUTATION_TRIALS`. This is Phase 1 reconnaissance only.

---

## Inspect the repo and available docs/configs for:

### 1. Existing evals
- names, file paths, commands
- protected layer (use the `owning_layer` taxonomy: BOOT / CONSTITUTION / SSOT_RAG / ROUTER / AGENT / CRITIC / RECEIPT / TAMPER / REGRESSION / PROMOTION)
- PASS/BLOCK criteria
- receipts produced

### 2. Existing RAG / knowledge sources
- SSOT files, incident reports, locked plans, rules, validators, routes, skills, prompts, databases, manifests/indexes

### 3. Existing brain modules
- routers, critics, verifiers, memory stores, queues, pipelines, cloud dispatch, terminal/forge components, model/provider config

### 4. Missing registry layer
For each asset found in 1–3, note whether it already has:
- a registry entry (or needs one)
- `owning_layer` tag (or `layer_unknown`)
- `mutation_class` tag (LOCKED / GATED / OPEN, or flag for founder review if unclear)
- ownership / source of truth
- freshness / receipt requirement
- dependency links to other assets

### 5. Missing connection layer
- what is isolated (no eval, no RAG link, no router awareness)
- what should connect to evals
- what should connect to RAG/SSOT
- what should connect to model/router/critic
- what should connect to receipts/promotion gate

### 6. Brain-evolution readiness
- what already supports sandbox candidates (config-diff proposals, not model checkpoints)
- what already supports gated promotion
- what is missing for live brain vs. sandbox brain separation
- what is missing for prompt-forge / router / eval-threshold promotion lanes (v0.1/v0.2/v0.3 per existing lane sequencing — do not propose building these lanes now, just note what's missing)

---

## Output

One report only: `SOURCEA_BRAIN_REGISTRY_DISCOVERY_REPORT_v1_{YYYYMMDD-HHMM}.md`, versioned per the artifact versioning rule (proposal pending founder approval — apply provisionally to this output).

**Sections, in this order:**

- Existing Assets Found
- Existing Evals Found
- Existing RAG/SSOT Sources Found
- Existing Databases/Receipts Found
- Existing Pipelines/Routes Found
- Missing Registry Fields
- Missing Connections
- Required Promotion Gates (note only — do not build)
- Critical Gaps
- Recommended Minimal Next Action

For every asset listed, use the same field structure as `registry_inventory.json` in Task 1 of the implementation prompt (`asset_id`, `asset_type`, `current_location`, `status`, `owning_layer`, `mutation_class`, `last_modified`, `dependents`) so this report can feed directly into that task without reformatting.

**Stop after the report. No further action without founder review.**
