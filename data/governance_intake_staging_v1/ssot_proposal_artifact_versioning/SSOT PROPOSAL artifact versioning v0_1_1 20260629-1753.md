# SSOT PROPOSAL — UNIVERSAL ARTIFACT VERSIONING & TIMESTAMP RULE

**Status:** PROPOSED — awaiting founder approval (5-option pattern applies)
**Proposed home:** New rule under D4 (Receipt & Verification) — this is a traceability/identity rule, not a Level 0 invariant about decisions or risk. Founder may override placement.

---

## Problem

Edited artifacts (specs, implementation prompts, SSOT patches) were being saved under identical filenames across multiple edit passes. No version number incremented, no timestamp recorded inside the file. This breaks traceability: an agent or a future founder review reading a saved docx/file copy cannot tell which edit pass produced it, in what order edits happened, or whether they're looking at the current version or a stale one pulled from disk/email/docx export.

This is a D4 problem by nature: a receipt or artifact without a traceable identity and timestamp is not verifiable as current.

---

## Proposed rule

**Every artifact that gets edited after creation must carry a three-part version number and a timestamp, both in the filename and inside the file header.**

### Filename pattern

```
{ARTIFACT_NAME}_v{major}.{minor}.{edit}_{YYYYMMDD-HHMM}.{ext}
```

- `major` — increments on a fundamental scope change (e.g. v0 → v1 when Phase 1 → Phase 2 opens)
- `minor` — increments on a substantive content change agreed by founder (e.g. the Phase 2 guard addition, the R1–R7 domain-split fix)
- `edit` — increments on every saved edit pass, however small, including wording fixes and typo corrections

Example: if `SOURCEA_BRAIN_REGISTRY_LEARNING_GATE` is at scope v0.1 and has had 10 edit passes since its first save, the filename becomes:

```
SOURCEA_BRAIN_REGISTRY_LEARNING_GATE_v0.1.10_20260629-1753.md
```

### In-file header (top of every artifact)

```
Version: v0.1.10
Created: 2026-06-29 (first save)
Last edited: 2026-06-29 17:53 PT
Edit log:
  v0.1.1  — initial draft
  v0.1.2  — added Phase 2 activation guard
  v0.1.3  — fixed R1–R7 domain-split conflict (R3/R4/R5 excluded from brain vocabulary)
  ...
```

The edit log doesn't need to repeat full diffs — one line per edit pass, stating what changed, is enough for an agent or founder to reconstruct the timeline without re-reading every version.

---

## Rules

1. **Every saved edit increments the `edit` number**, even a one-line wording fix. No silent re-saves under the same version number.
2. **`minor` increments only on founder-approved substantive changes** — i.e. when a revision request, conflict-log ratification, or scope change is accepted, not on every individual edit pass within that revision.
3. **`major` increments only on phase/scope transitions** explicitly opened by founder decision (e.g. Phase 1 → Phase 2).
4. **Timestamp is wall-clock at time of save**, in the founder's local timezone, format `YYYYMMDD-HHMM`.
5. This applies universally — to SSOT artifacts, implementation prompts, conflict logs, and any other artifact intended to be saved, referenced later, or read by an agent reconstructing project history.
6. Superseded versions are not deleted by default — old version files stay on disk/in docx history unless founder explicitly says to clean up. The version number is what tells anyone which is current.

---

## What this does NOT change

- Does not affect Level 0 or Level 1 SSOT content
- Does not require renaming files mid-task without founder awareness — the rule activates going forward from approval, and is being demonstrated now on the three most recent active artifacts as an example

---

**Founder action required:** Approve / Reject / Hold / Request revision / Escalate.
