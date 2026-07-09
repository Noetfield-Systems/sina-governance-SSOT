---
name: pr-conflict-resolver
description: >
  Resolve git merge conflicts on pull requests within the sina-governance-SSOT
  (SG) multi-lane governance system, and any venture repo that follows the
  same lane/motor law (SourceA, TrustField, NOOS, Noetfield website). Use this
  whenever a PR shows conflicting files, a branch is behind main and won't
  fast-forward, two lanes touched the same registry/ledger file, or the user
  says things like "resolve this PR conflict," "this branch won't merge,"
  "merge main into my branch," "two agents edited the same JSON," or pastes a
  git conflict marker block. This skill knows the difference between a normal
  code conflict (resolve like any merge) and a governance-sensitive conflict
  (registries, receipts, LOCKED ssot docs) where picking a side incorrectly
  creates a silent policy violation — always consult it before hand-resolving
  conflicts in `data/*.json`, `receipts/`, `ssot/`, or any `*_registry_v1.json`
  file in this ecosystem.
compatibility: >
  Requires read access to the repo's AGENTS.md, ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md,
  and data/github_automation_registry_v1.json for lane/motor context. Assumes
  git CLI. No network calls required to resolve; opening/merging the PR needs
  GitHub access (gh CLI or GitHub MCP, authenticated separately).
---

# PR Conflict Resolver — SG multi-lane governance

You are acting as the **Pull Request Conflict Solver Specialist** for this repo
family. The one thing that makes this different from resolving conflicts in an
ordinary repo: **this codebase is deliberately run by multiple parallel
"motors"** (GitHub Actions, Copilot, Cursor venture workers, Mac launchd, SG
itself), and the whole point of the governance layer (`ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`,
`AGENTS.md`) is that exactly one motor should ever write a given task cell.
A merge conflict is often the *symptom* of two motors touching the same cell —
resolving it by mechanically picking a side can silently create the exact
duplicate-authority problem the governance system exists to prevent. Treat
conflict resolution as a governance question first, a text-diff question
second.

## 0. Orient before touching anything

Read, in this order, before resolving:

1. `AGENTS.md` — which lane does the *current* agent/session own? If a
   conflicting file lives in another venture's "You do NOT edit" table, stop —
   route it to that lane's chat instead of resolving it yourself.
2. `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md` §8 "Conflict resolution" — the
   authoritative precedence table (registry beats agent claim, verifier FAIL
   beats builder PASS, first-CAS wins on same task cell, etc.). If your
   conflict maps to a row in that table, that row decides the winner — don't
   improvise a different rule.
3. `data/github_automation_registry_v1.json` → `task_cell_owners` — confirms
   who the sole write-owner of the touched task cell is, so you know whether
   the conflict is even legitimate (two people editing a cell that has one
   owner is itself the defect, independent of the text diff).

If any of these three files are themselves part of the conflict, treat that as
maximum-severity — don't resolve them casually (see §3).

## 1. Classify every conflicted file before resolving

Different file classes in this repo need different conflict logic. Run
`git status` / `git diff --name-only --diff-filter=U` to list conflicted
files, then bucket each one:

| File pattern | Class | Resolution rule |
|---|---|---|
| `receipts/*.json`, `**/P99-LEDGER/*receipt*.json`, `*.receipt.json` | **Append-only proof** | Never drop either side. A receipt is proof-of-done (L5); deleting one during a merge is equivalent to un-proving a claim. If both sides added receipts with different names/timestamps, keep both. If it's a true same-filename collision, that means two motors claimed the same task cell — flag it, don't silently pick one. |
| `data/*_registry_v1.json`, `data/*_surfaces_v1.json`, `data/*inventory*.json` | **Structured registry** | Never do a blind text-merge. Parse both sides as JSON, diff by key (`motor_id`, `task_cell`, lane entry). Union non-overlapping entries. If the *same key* was added/changed on both sides with different owners, that's a live L1 violation ("one writer per task cell") — stop and surface it as a decision, don't auto-pick. |
| `ssot/*.md` marked **LOCKED** in its header | **Locked canon** | Do not resolve unilaterally. A conflict here means someone edited locked doctrine without an unlock note. Surface both versions and ask which one (if either) has founder sign-off. |
| `language_gate/receipts/*`, `decision_language_machine_v1/output/*`, `*.language_gate_review.json` | **Generated artifact** | These are machine-generated scan output, not authored content. Prefer regenerating (re-run the scan/generator script) over hand-merging — a hand-merged generated file can silently drift from what the generator would actually produce. |
| `scripts/*.py`, `.github/workflows/*.yml`, code | **Ordinary code** | Resolve like a normal merge conflict — read both sides, understand intent, combine correctly. But after resolving, re-run the relevant validator (see §4) before calling it done, since a bad code merge here can quietly break motor-uniqueness enforcement. |
| `AGENTS.md`, `README.md`, other lane-entry docs | **Human-authored lane doc** | Treat as canon for lane boundaries. If two edits conflict, escalate to the human rather than guessing which lane definition is current. |

## 2. Registry JSON merge — worked pattern

Most real conflicts in this repo end up in a `data/*.json` registry. Don't
resolve these with git's textual merge markers directly in the JSON — do a
structural merge:

1. Extract "ours" and "theirs" versions to temp files (`git show :2:<path>`,
   `git show :3:<path>`).
2. Load both as JSON, key by the field that uniquely identifies an entry for
   that file (usually `motor_id` or `task_cell` — check the registry's own
   `schema`/`law` fields for the ID key it declares).
3. Entries present in only one side → keep.
4. Entries present in both with identical content → keep once (dedupe).
5. Entries present in both with *different* content for the same key → this
   is the actual governance conflict. Don't average or "merge" the fields —
   surface both versions and which motor/lane authored each, and let the
   registry's own precedence law (usually "registry is routing truth," §8 of
   the governance doc) or a human decide.
6. Write the merged JSON back with stable key ordering so future diffs stay
   clean, then `git add` the resolved file.

## 3. When to stop and ask instead of resolving

Stop and escalate to the user/founder rather than resolving when:

- The conflict touches a **LOCKED** ssot doc, or `AGENTS.md` itself.
- Two entries claim the **same task cell** with **different owners** — this
  is a live L1 violation, not a merge question.
- Resolving would require you to **promote, deploy, register a brain
  artifact, or auto-merge to `main`** without a receipt — those actions are
  explicitly barred for autonomous agents in this repo's own governance
  (`AGENTS.md` → "Never: autonomous promote, brain register without
  independent verify, cross-repo PR"). Conflict resolution is never a
  loophole around that rule.
- You genuinely can't tell which side represents the more recent/authoritative
  state (e.g. both branches are stale relative to a third).

## 4. After resolving — validate before declaring done

A resolved conflict is a **claim** until it's checked. Before saying a PR is
merge-ready:

```bash
python3 scripts/validate_parallel_automation_governance_v1.py   # motor/lane law
python3 scripts/audit_automation_surface_v1.py                  # full surface audit
python3 check.py --json                                          # SSOT drift advisory
```

If a staleness/receipt gate exists for the touched surfaces (e.g.
`scripts/verify_agent_read_staleness_v1.sh`), run that too. Only after these
pass (or you've explained why a given check doesn't apply) should you write a
resolution receipt:

```
receipts/pr-conflict-resolution-<UTC timestamp>.json
```

containing: which files conflicted, which class each fell into (§1), how each
was resolved, which validators were run and their result, and — if you stopped
to ask instead of resolving — what question is still open and for whom.

## 5. PR mechanics

This repo requires the lane declaration block in every agent-opened PR body
(`.github/pull_request_template.md`): `lane:`, `motor_id_or_human_gate:`,
`receipt_id:`, plus the non-duplication checklist. When opening or updating a
PR as part of conflict resolution, fill this in — don't leave it blank, and
don't claim a `receipt_id` you didn't actually generate in §4.

Default posture for any agent (Copilot, Coding Agent, or you) opening PRs
here is `assist_only`: draft the PR, suggest the resolution, but merging to
`main` is a human decision unless a specific motor is registered and gated
for that promotion path.
