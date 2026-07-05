# CANONICAL D4 PACKAGE v0.1
*Mode: CANONICALIZE → SPEC → STOP. Level 2 artifacts under Level 0 + D4/D5.*
*Not implementation. No builder prompts. No Cursor/Codex authorization. No PASS.*

> Carried invariant (load-bearing, do not patch out): **there is no trusted mode flag.**
> PASS is a property *computed per-receipt* from identity + path fields. Absent or equal
> fields → SUBMITTED, fail-closed. "Local dev" and "cloud" are not modes you set — they are
> the observed cases where the fields either collapse (PASS unreachable) or separate (PASS
> computable). Independence is derived, never declared.

---
---

# F — FOUNDER_DECISION_PACKET_v0.1  *(cover — act here)*
*Governing SSOT: Level 0 + D5. This is a decision surface, not an SSOT.*

## Decisions already taken this thread (recorded)
- Versioning proposal → **REQUEST REVISION** (git-derived identity, not typed filenames; folded into the kernel).
- Canonical D4 kernel → **APPROVE TO SPEC** (single artifact, two repos import it, PASS stubbed).

## What this package contains (one line each)
- **A — D4 kernel SPEC.** The single canonical receipt schema + per-receipt derived-independence logic + verifier contract. Imported by both repos; reimplemented by neither.
- **B — SSOT canonicalization.** Move SSOT v6 from two ungoverned local copies to one git-main LOCKED path; identity derived from git.
- **C — R-rule split.** R1/R2/R6/R7 are D4-portable; R3/R4/R5 stay control-panel only. Ratifies the previously-logged conflict.
- **D — Brain Registry Phase-1 alignment patch.** Repoint its Founding Instruction to the canonical SSOT path; R1/R2/R6/R7 only; Task 5/5b stays stubbed; Task 1 is reconnaissance, not done.
- **E — NOOS import contract.** NOOS imports kernel A; authors no separate D4; its local checks become LOCAL_CHECK/SUBMITTED evidence only.

## Exact blockers (these gate everything below them)
1. **SSOT v6 is not in version control.** Found at `~/Downloads/strategy-ssot-v6-split (1).md` and `~/Desktop/SSSOT/strategy-ssot-v6-split.md` — two ungoverned copies. It fails its own R1/R2. Nothing can define LOCKED vocabulary from an uncommitted file.
2. **R6/R7 canonical source not located.** The split rule (C) stands, but it cites a source that must be found or recreated and committed.
3. **`SOURCEA_PHASE2_MUTATION_TRIALS` flag location unknown.** A guard you can't locate is not a guard.
4. **No independent verifier path exists yet.** Until builder/subject/verifier are separate identities on separate network paths, **PASS is structurally disabled** — the system can honestly emit only SUBMITTED/UNVERIFIED. This is infrastructure, not a schema field.

## Exact next allowed action (only this)
Commit SSOT v6 to one canonical git-main path as a LOCKED asset (per B). That single act unblocks authoring A–E against a real citable path. Everything else waits.

## STOP
CANONICALIZE → SPEC → STOP. No implementation, no registry seed, no NOOS shim build, no PASS claim, no agent authorization.

## Founder options (per existing 5-option pattern)
Approve · Reject · Hold · Request revision · Escalate — on the package as a whole, or per document A–E.

---
---

# A — CANONICAL_D4_ENFORCEMENT_SHIM_v0.1_SPEC
*Governing SSOT: Level 0 (0.1, 0.3) + D4. Level 2 SPEC. One canonical artifact; SourceA and NOOS import it.*

## A.0 Purpose
Define the D4 enforcement contract **once**. Two implementations of the verification layer would be drift in the one layer whose job is to catch drift. SourceA and NOOS consume this; neither re-authors it.

## A.1 The core rule (no trusted mode flag)
PASS is **derived per receipt**, never declared. The kernel computes, at verification time, whether a specific receipt qualifies. No component sets a mode that enables PASS.

```
PASS is granted to a receipt ONLY IF all hold:
  author_id            != subject_id
  process_id           != subject_process_id
  runtime_id           != subject_runtime_id
  repo_lane            != subject_repo_lane
  deploy_surface       does-not-overlap subject_deploy_surface
  network_path_id      != subject_network_path_id
  second_vantage_probe present AND agrees
  evidence             present (pasted probe output)
  false_if             present
Otherwise → SUBMITTED / UNVERIFIED.
Any field missing or unknown → SUBMITTED / UNVERIFIED (fail-closed).
```
Degenerate case (same machine / same account / same worker): the fields collapse to equal, so PASS is unreachable — automatically, with no one declaring "not independent." Separated case (distinct identities + path + second vantage): PASS becomes computable. The case is *observed from fields*, never asserted.

## A.2 Receipt schema (single canonical shape)
```
record_id
git_commit            (subject identity, git-derived)
content_hash          (subject identity, git-derived)
committed_at          (git-derived timestamp — NOT a typed string)
author_id   subject_id
process_id  subject_process_id
runtime_id  subject_runtime_id
repo_lane   subject_repo_lane
deploy_surface  subject_deploy_surface
network_path_id subject_network_path_id
truth_layer           <PUBLIC|EXTERNAL|DEPLOY|LOCAL|TELEMETRY>
evidence              <pasted HTTP status + headers + matched/no-match body lines>
second_vantage_probe  <ref + result from a different network path>
false_if              <condition that would falsify the claim>
local_status          <LOCAL_PASS|LOCAL_FAIL>  (script/command exit — NEVER a D4 decision)
receipt_decision      <SUBMITTED|UNVERIFIED|PASS|FAIL|BLOCKED>
```

## A.3 local_status vs receipt_decision (the vocabulary split)
- **local_status** is a command/script result (a test passed, a grep matched). It is evidence at the LOCAL truth layer and **can never be a D4 decision**, regardless of how confident the script is.
- **receipt_decision** is the D4 verdict. Only an independent verifier writes PASS/FAIL/BLOCKED, and only when A.1 qualifies. A builder/script printing "PASS" sets local_status=LOCAL_PASS, never receipt_decision=PASS.

## A.4 Builder vocabulary
Builder emits one closeout token: **`SUBMITTED for independent verification`** + diff + `false_if`. It has no vocabulary for done/fixed/live/verified/clean/shipped, and cannot pre-fill any independence field about a verifier.

## A.5 Verifier contract
Separate `author_id` and `network_path_id` from the subject. Dumb enough to audit by reading (~10 lines, no clever branching). Pastes the real probe output; computes only A.1; fabricates nothing. A PASS must be reproducible by a second independent vantage. One verifier alone is a smaller god to corrupt.

## A.6 No silent work
Any mutation of a subject auto-generates `SUBMITTED / UNVERIFIED`. Absence of a receipt = FAIL, not "fine."

## A.7 Artifact identity (folds the versioning proposal in)
Artifact identity = **git commit hash + content hash + commit time** — derived, external, tamper-evident. Canonical artifacts keep **one stable filename** (no version in the filename). An in-file header version/edit-log is a human-readable *label only*, explicitly subordinate to git. On any conflict between filename/header and git, **git tree + receipt win**. No standalone versioning doctrine.

## A.8 Import contract
SourceA and NOOS reference this artifact at its canonical git path (per B), call the same independence function, and never redefine the fields or thresholds. Redefinition in a consuming repo is a conformance violation.

## A.9 PASS stubbed until verifier path exists
Until an independent verifier path is named and built, no receipt can satisfy A.1, so the kernel emits only SUBMITTED/UNVERIFIED. This is correct, not a limitation — the kernel does not lie about a verifier it doesn't have.

## A.10 Conformance recursion (OPEN — the kernel's own prerequisite test)
The kernel enforces author ≠ subject, so it cannot verify *itself*. Its correctness must be proven by a **rejection test authored by a non-builder** that attempts to push a self-authored PASS (and each individual field-collision) through and confirms every one bounces to SUBMITTED. This test is a prerequisite to trusting the kernel and must not be written by the kernel's builder. Flagged open; not claimed solved.

---
---

# B — SSOT_CANONICALIZATION_PACKET_v0.1
*Governing SSOT: Level 0 + D4 (artifact identity). Level 2.*

## B.1 Problem
SSOT v6 lives as two ungoverned local copies on different paths. Every agent loads whichever copy is on its filesystem. The document that *defines* truth currently fails its own R1/R2 (git-main-only).

## B.2 Rules
- **One canonical git-main path.** Founder names the repo (SourceA, NOOS-as-control, or a dedicated governance repo). Filename stable: `strategy-ssot-v6-split.md` — no version in the name.
- **Identity is git-derived.** Currentness = HEAD on main + content hash + commit time. No local copy (`Downloads/`, `Desktop/`) is ever truth; loading one is forbidden.
- **LOCKED treatment.** Mutation requires explicit founder approval every time; no autonomous path, ever.
- **Stray copies** are quarantined or deleted, or explicitly marked non-authoritative, so no agent can resolve "current" to a download.

## B.3 Content note
The v6 content is already settled (the master canon). This packet governs *where it lives* and *how its identity derives* — not its content. First action: commit the settled v6 content to the canonical path as the initial LOCKED commit.

---
---

# C — D4_PORTABLE_RUNTIME_RULES_SPLIT_v0.1
*Governing SSOT: D4 + Conflict-Resolution rule. Level 2. Ratifies the previously-PROPOSED conflict log.*

| Rule | Domain | Portable to agentic-brain governance? |
|---|---|---|
| R1 session start / git truth | D4 | Yes |
| R2 source-of-truth order | D4 | Yes |
| R3 mode switch (AUDIT/EXECUTE) | Control panel / D5 conversational | No |
| R4 prompt-size law | Control panel | No |
| R5 dirty-file law | Control panel | No |
| R6 receipt law | D4 | Yes |
| R7 agent cannot self-verify | D4 | Yes |

- **Rule:** agentic specs import **R1/R2/R6/R7 by rule** — never wholesale R1–R7, never by judgment call.
- `AUDIT` / `EXECUTE` are excluded from brain vocabulary; they govern founder↔assistant conversation only.
- **Ratification note (0.4 / conflict resolution):** the conflict log (PROPOSED) was correctly logged as a new fact awaiting approval rather than silently adjudicated. Approving this packet *is* its ratification.
- **Prerequisite:** R6/R7 canonical source must be located or recreated and committed; the split rule stands, but it currently cites a source that must be made real.

---
---

# D — SOURCEA_BRAIN_REGISTRY_PHASE1_ALIGNMENT_PATCH_v0.1
*Governing SSOT: D4 + D5. Level 2 patch. No registry implementation.*

- **Repoint** the Brain Registry Founding Instruction to the canonical SSOT git path (B), not the `Downloads/…(1).md` copy.
- **Replace** any blanket "Runtime Rules R1–R7" with "R1/R2/R6/R7 only" per C (the task-level bindings already scoped correctly; the Founding Instruction wording is the patch target).
- **Task 5/5b stays STUBBED;** `SOURCEA_PHASE2_MUTATION_TRIALS = false`; flag needs a canonical location (blocker 3).
- **Task 1 is reconnaissance, not done.** The agent produced a prose discovery report and explicitly created no `registry_inventory.json`. Log as pre-Task-1 CHECK output; the Task 1 deliverable is not satisfied.
- **Task 6 imports kernel A.** The promotion receipt schema (author ≠ verifier) does not author its own D4 — it consumes the canonical kernel. This removes the second-D4 drift.
- **Eval-semantics caution:** rows whose PASS criteria are "inferred from validator," and the `DONE/NOT_DONE` vocabulary in `phase2_evaluations`, are flagged as assertion/collision needing normalization before any promotion gate trusts them — not carried forward as read truth.

---
---

# E — NOOS_D4_IMPORT_CONTRACT_v0.1
*Governing SSOT: Level 0 + D4. Level 2. No NOOS shim build.*

- **NOOS imports kernel A; authors no separate D4.** NEXT-001 is rescoped from "build a shim" to "implement the import + the local_status/receipt_decision split + the auto-SUBMITTED-on-mutation queue, calling the canonical kernel." Still SPEC, not built.
- **NOOS local checks** (`check_noos_repo_policy.py`, `check_noos_clean_tree.sh`, tests, repo grep) emit `local_status = LOCAL_*` / SUBMITTED evidence only. They never write `receipt_decision = PASS`.
- **NOOS live-sync gate** is reclassified as a **same-path watcher → observer/queue input**, not a PASS writer (NOOS already self-incriminated this; formalized here per D4 hierarchy item 7).
- **All prior NOOS "ecosystem green" / PASS-language receipts** are marked legacy / D4-invalid and not carried forward as truth.
- **PASS for any NOOS-observed subject** comes only from the canonical derived-independence logic (A.1), via an independent verifier path — which does not yet exist (blocker 4).

---

*Banked as a SPEC package. Reopen only on new facts. Next allowed action: commit SSOT v6 to its canonical git-main path (B). Nothing else.*
