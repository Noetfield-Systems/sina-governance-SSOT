---
name: receipt-ledger-auditor
description: >
  Scan receipts/ for the anomalies that look like a duplicate-motor or
  dual-ownership claim rather than a normal proof trail: malformed JSON,
  receipts with no discoverable timestamp, and receipts of different types
  landing within seconds of each other (a sign two motors may have raced on
  the same task cell). Use this whenever the user asks to "audit receipts,"
  "check the ledger," "did two motors claim the same thing," before trusting
  a receipt as proof a task actually completed, or after any session where
  multiple agents/motors were working in this repo at once. This is a
  post-hoc, single-tree audit -- it complements pr-conflict-resolver, which
  catches the same class of collision but only during an actual git merge.
compatibility: >
  Requires scripts/audit_receipt_ledger_v1.py and a receipts/ directory.
  Python 3, no external dependencies.
---

# Receipt Ledger Auditor

This repo's governance law (L5) says no motor reports DONE without a
`receipt_id` — a receipt is supposed to be proof, not a claim. But a receipt
file existing doesn't automatically mean it's trustworthy: it could be
malformed, missing the timestamp that would let you sequence it against other
events, or — the case that matters most — one of two receipts that landed at
nearly the same instant because two different motors both thought they owned
the same task cell.

## Running the audit

```bash
python3 scripts/audit_receipt_ledger_v1.py --json
```

Add `--write-receipt` to save the audit's own findings as a receipt (yes,
auditing the ledger produces a ledger entry — that's intentional, it's proof
the audit itself happened). This script always exits 0; it's an audit, not a
gate, so don't read a clean exit code as "nothing to report" — read the
`ok` field and the counts.

## What each finding means

- **`malformed_count`** — a receipt file that fails to parse as JSON. This is
  not proof of anything; whatever task it claims to document should be
  treated as unverified until re-checked by another means.
- **`missing_timestamp_count`** — a receipt with no `at`/`timestamp`/similar
  field and no date anywhere in its filename. Not automatically wrong (some
  receipts are intentionally "latest" snapshots), but it means you can't
  sequence this receipt against anything else, which matters if you're ever
  trying to reconstruct what happened in what order.
- **`cluster_count`** — the important one. Two or more *differently-named*
  receipt types landing within a few seconds of each other. This is exactly
  the shape of the collision the pr-conflict-resolver skill's eval suite
  tests for during a merge — here it's the same signal spotted after the
  fact, in a single already-merged tree. A cluster is not automatically a
  problem (could be one motor legitimately kicking off several sub-tasks at
  once), but it's always worth a quick look at what each file actually
  claims, especially if any of them touch the same task cell in
  `data/github_automation_registry_v1.json`.
- **`receipt_family_count`** (informational, not a finding) — how many receipt
  *types* have more than one instance over time (e.g. `agent-read-staleness-*`
  showing up six times). This is completely normal for a recurring motor and
  should not be reported as an anomaly on its own — only the specific
  cross-type clusters matter.

## When a cluster shows up

Don't silently pick a "winner" between clustered receipts the way a naive
merge might. Look at what each file claims (which task, which motor, what
status), check `data/github_automation_registry_v1.json`'s `task_cell_owners`
for who's actually supposed to own that cell, and report the finding — this
is the same "surface it, don't auto-resolve it" posture pr-conflict-resolver
takes for the same underlying failure mode.

## Reporting results

State the actual counts, not just "audit passed/failed" — `ok: false` from a
handful of missing timestamps on old "latest"-style receipts is a very
different situation from `ok: false` because two motors clustered on the same
task cell. Name the specific files for anything you'd want a human to look
at, the same way you'd name specific files in a PR conflict rather than
saying "there was a conflict."
