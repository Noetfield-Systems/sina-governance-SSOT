# P0 CORE Decision Use Contract v1

**Status:** ACTIVE  
**Registry:** `p0-core-decision-use-contract-v1`  
**Registry receipt:** `receipts/p0-core-decision-use-contract-v1-registry-20260704T044240Z.json`  
**Owner:** SG (`sina-governance-ssot`)  
**Governs:** `founder-judgment-patterns-v1` (ACTIVE P0 CORE)  
**Machine schema:** `data/p0_core_decision_use_contract_v1.json`  
**Read-scope gate:** `data/founder_judgment_patterns_read_scope_v1.json`  
**Invocation-scope:** `data/p0_core_invocation_scope_v1.json` (PROPOSED)

---

## One sentence

> **Base Live Brain and high decision agents may read P0 CORE as a read-only judgment source for novel decisions — output is a proposal with a receipt, never worker prompt content, never direct mutation.**

---

## Scope

| Field | Value |
|-------|-------|
| Artifact | `founder-judgment-patterns-v1` |
| Library path | `P0-FOUNDATION-SPINE/P0-CORE/FOUNDER_JUDGMENT_PATTERNS_v1.md` |
| Registry status required | `ACTIVE` |
| Allowed readers | `base_live_brain`, `high_decision_agent` |
| Forbidden readers | all workers, Tier 1, Tier 2 prompt bundles |
| Mode | read-only judgment source |
| Authority | registry ACTIVE + read-scope marker + decision receipt |

**Out of scope:** edits to P0 CORE content, worker prompt changes, registry promotion without `governance_registry_ops_v1.py` + receipt.

---

## 1. When P0 CORE may be invoked

Invoke only when **at least one** trigger applies:

| Trigger | Description |
|---------|-------------|
| `novel_case` | No Tier-1 rule fits the situation |
| `lower_law_conflict` | Two or more lower-tier laws conflict |
| `money_build_sell_sequencing` | Choice between selling, building, or capital spend |
| `authority_registry_dispute` | File claim vs registry status; receipt order vs filesystem truth |
| `target_vs_blocker_dispute` | Aspiration treated as halt gate |
| `no_tier1_rule_fits` | Explicit exhaustion of Tier-0 + role law + mission + gates |

**Do not invoke** for routine worker execution, bulk law loading, or cases fully covered by mechanical gates.

---

## 2. Required input schema

Every invocation must supply:

```json
{
  "case_id": "stable slug for this decision episode",
  "invoking_actor": "base_live_brain | high_decision_agent",
  "decision_question": "single plain-language question",
  "lower_tier_facts": ["fact rows from Tier 0/1/2 execution only"],
  "conflicting_rules": ["artifact_id or rule ref — empty array if none"],
  "available_receipts": ["receipt paths already on disk"],
  "proposed_options": [
    {"option_id": "A", "description": "...", "risks": ["..."]}
  ],
  "invocation_triggers": ["one or more from §1"]
}
```

**Validation:** reject invocation if `invoking_actor` not in read-scope `allowed_readers`, if registry status ≠ `ACTIVE`, or if triggers array is empty.

---

## 3. Required output schema

Every invocation must produce:

```json
{
  "decision": "chosen option or explicit halt",
  "matched_patterns": ["PATTERN N — short name"],
  "reasoning_summary": "principle-based, not rule-recall",
  "chosen_next_action": "single next move for invoking actor or SG",
  "stop_continue_verdict": "STOP | CONTINUE | ESCALATE_TO_SG",
  "required_gate_or_receipt": "gate script, registry op, or receipt path required before execution",
  "harvest_proposed": false,
  "harvest_note": "only true when genuinely novel; requires real case + SG/Founder ratification"
}
```

**Semantics:**

- `decision` is a **proposal** unless invoking actor has execution authority for that domain.
- `matched_patterns` reference existing P0 patterns by id + name — do not invent Pattern 11+ in dry-run or without ratification.
- `stop_continue_verdict` = `STOP` when next step is unsafe; `ESCALATE_TO_SG` for registry/legal/capital gates.

---

## 6. Output soup-wall

P0 CORE reasoning **must not** propagate into worker prompts.

When a high actor (`base_live_brain`, `high_decision_agent`) acts on a P0 decision, only these fields may cross to workers:

| Allowed in worker task-spec | Stays above the gate |
|----------------------------|----------------------|
| `goal` | `matched_patterns` |
| `files` | `reasoning_summary` |
| `constraints` | founder-judgment language |
| `done_criteria` | internal decision analysis |
| `verify_method` | P0 CORE text / pattern names |
| `receipts_required` | `harvest_proposed` rationale |
| `decision_verdict` (short verdict only) | full P0 invocation input/output |

**Gate:** `scripts/verify_p0_core_output_soup_wall_gate_v1.py` — BLOCK if worker bundle contains forbidden keys or P0 leakage markers.

Workers receive **scoped execution instructions only** — never judgment reasoning.

---

## 7. No-match handling

If **no P0 pattern shape matches** the case:

```json
{
  "decision": "ESCALATE_TO_FOUNDER",
  "matched_patterns": [],
  "reasoning_summary": "No existing pattern fit; weak similarity rejected",
  "stop_continue_verdict": "ESCALATE_TO_SG",
  "harvest_proposed": true,
  "harvest_note": "Genuinely novel case — founder DECIDE + future harvest candidate"
}
```

**Hard rules:**

- Do **not** fabricate a pattern match.
- Do **not** force a decision from weak similarity.
- Do **not** create Pattern 11+ without real case + SG/Founder ratification.
- Empty `matched_patterns` + `harvest_proposed: true` is valid and expected for novel cases.

---

## 8. Dry-run validation

Calibration case: `founder-judgment-chronology-reconciliation-historical` (already decided).

| Check | Expected |
|-------|----------|
| Pattern match | PATTERN 4 + PATTERN 9 |
| Pattern 11 created | **No** |
| Worker prompt receives P0 reasoning | **No** (soup-wall BLOCK) |
| Receipt written | `receipts/p0-core-decision-dryrun-chronology-reconciliation-20260704T043502Z.json` |

Soup-wall negative-proof: `receipts/p0-core-output-soup-wall-negative-proof-20260704T043807Z.json`

---

## 4. Hard limits

| Limit | Rule |
|-------|------|
| No worker leakage | P0 CORE text must never be copied into worker prompts or Tier 1/2 bundles |
| No direct mutation | P0 CORE output cannot directly mutate registry, code, gates, or prompts |
| Proposal default | Output is decision proposal unless actor authority + gate allows execution |
| Harvest gate | New patterns require real case + SG/Founder ratification; no speculative philosophy |
| Read-only source | P0 CORE is read for judgment; file is not edited during invocation |
| Mechanical protection | `verify_p0_core_read_scope_gate_v1.py` remains authoritative for worker BLOCK |

---

## 5. Receipt requirement

Every P0 CORE invocation writes a decision receipt to `receipts/p0-core-decision-<case_id>-<timestamp>.json`.

**Required receipt fields:**

| Field | Required |
|-------|----------|
| `schema` | `p0-core-decision-receipt-v1` |
| `artifact_id` | `founder-judgment-patterns-v1` |
| `contract_id` | `p0-core-decision-use-contract-v1` |
| `case_id` | from input |
| `invoking_actor` | from input |
| `timestamp` | UTC ISO |
| `input` | full input schema |
| `output` | full output schema |
| `matched_patterns` | from output |
| `harvest_proposed` | boolean |
| `dry_run` | boolean — `true` for calibration/historical replay |
| `live_authority` | `false` for proposals; `true` only if downstream registry receipt confirms execution |

**Dry-run receipts** are valid for calibration and audit replay; they do not create new patterns or registry rows.

---

## Invocation flow

```
1. Gate check — read-scope + invocation-scope + registry ACTIVE
2. Validate input schema + triggers
3. Read P0 CORE (allowed actor only)
4. Match pattern shape(s) — if none, §7 no-match handling
5. Emit output schema (above soup-wall)
6. Transform to worker task-spec only if dispatching — soup-wall gate
7. Write decision receipt
8. If harvest_proposed → queue SG ratification (never auto-append to P0 CORE)
```

---

## Related artifacts

- `founder-judgment-patterns-v1` — judgment source (ACTIVE, do not edit)
- `agent-layered-law-least-knowledge-v1` — least-knowledge routing
- `data/founder_judgment_patterns_read_scope_v1.json` — mechanical read gate
- `data/p0_core_invocation_scope_v1.json` — invocation when/how (PROPOSED)
- `scripts/verify_p0_core_read_scope_gate_v1.py` — negative-proof worker block
- `scripts/verify_p0_core_output_soup_wall_gate_v1.py` — negative-proof soup-wall block
- `ssot/DAILY_GOVERNANCE_MACHINE_RUNBOOK_v1.md` — registry/receipt discipline

---

## Registry + scope proposals

See `data/p0_core_decision_use_contract_v1.json` → `registry_proposal`.  
Invocation-scope proposal: `data/p0_core_invocation_scope_v1.json`.  
**Do not register ACTIVE** until SG review + receipt confirms.
