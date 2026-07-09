> **RATIFIED 2026-07-03 12:34 PDT by founder DECIDE.** Status changed PROPOSED → RATIFIED / BINDING. This is now canonical SSOT, subordinate only to FOUNDER_CANON v1.

---

# SSOT CONFLICT LOG — PROPOSED CLARIFICATION (awaiting founder approval)

Version: v0.1.2
Created: 2026-06-29
Last edited: 2026-06-29 17:53 PT
Edit log:
  v0.1.1 — initial conflict log (R1–R7 domain split observation + proposed clarification)
  v0.1.2 — corrected false claim that no existing artifact needed modification; flagged Founding Instruction as requiring a wording patch


**Status:** PROPOSED — not yet ratified. Per SINA SSOT 0.4/Conflict Resolution: this is logged as a new fact, not silently adjudicated. Founder approval required before this becomes binding.

**Triggering observation:** Runtime Rules R1–R7 were authored as a single fused document derived from both SSOT v6 (D4 — Receipt & Verification) and `SSOT_ASSISTANT_PROMPT_OUTPUT_LOGIC` (a Level 2 control-panel artifact governing human-machine daily-assistant conversation). The fusion was correct for Cursor sessions, where both concerns co-occur. It is not correct to import wholesale into agentic-brain governance contexts (e.g. SourceA Brain Registry), where only the D4-domain rules apply.

---

## Proposed clarification

**`SSOT_ASSISTANT_PROMPT_OUTPUT_LOGIC` is scoped exclusively to human-machine daily-assistant interaction (the "control panel").** It governs prompt brevity, output format, AUDIT/EXECUTE conversational mode, and dirty-file handling *in conversation with the founder*. It is not, and was never intended to be, a brain-agentic governance document. It does not bind the base model's operational vocabulary, the Brain Registry, or any agentic mutation/promotion path.

**Runtime Rules R1–R7, as currently combined under `000-founder-rules.mdc`, split across two domains:**

| Rule | Domain | Portable to agentic-brain contexts? |
|---|---|---|
| R1 — Session start / git truth | D4 (Receipt & Verification) | Yes |
| R2 — Source of truth order | D4 | Yes |
| R3 — Mode switch (AUDIT/EXECUTE) | Control panel / D5 conversational | No — governs human-machine dialogue mode, not brain state |
| R4 — Prompt size law | Control panel | No — governs assistant output brevity to founder, not brain behavior |
| R5 — Dirty file law | Control panel | No — governs conversational handling of unrelated dirt, not brain mutation logic |
| R6 — Receipt law | D4 | Yes |
| R7 — Agent cannot self-verify | D4 | Yes |

**Proposed rule:** When a Runtime Rule is imported into an agentic-brain governance document (Brain Registry, Learning Gate, future mutation-lane specs), only D4-domain rules (R1, R2, R6, R7) are portable. Control-panel rules (R3, R4, R5) stay scoped to direct founder-assistant conversation and must not be inlined into agentic specs, even by inference.

**Consequence for prior work:** The SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1 implementation prompt's Task-level bindings (Task 1 cites R1/R2; Task 6 cites R6/R7) already scoped correctly in practice. However, the **Founding Instruction** section of that same implementation prompt currently imports "Runtime Rules R1–R7" wholesale as brain vocabulary and lists `AUDIT`/`EXECUTE` alongside D4-domain terms — this is a real conflict with the split proposed here, not a correctly-scoped reference. That section requires a wording patch (see required revision below), not just ratification.

---

## What this does NOT change

- Existing v0.1 artifacts require a wording patch in the Founding Instruction only. Task-level bindings already correctly use R1/R2/R6/R7 (Task 1 cites R1/R2, Task 6 cites R6/R7) and need no change.
- `000-founder-rules.mdc` itself does not need to be split into two files unless the founder wants that for hygiene — the rules can stay co-located; what's being ratified is the *domain tag* on each rule, not the file structure
- This is a clarifying addendum, not a Level 0 or Level 1 edit — SSOT v6 Level 0/D4/D5 content is untouched

## What this DOES change going forward

- Any future agentic spec (v0.2 router-rule lane, v0.3 validator lane, etc.) imports R1/R2/R6/R7 by rule, not by judgment call
- R3/R4/R5 stay exclusively in scope for direct founder-assistant chat behavior — never get proposed for inclusion in a brain-governance document again

---

**Founder action required:** Approve / Reject / Hold / Request revision / Escalate (per existing 5-option pattern).
