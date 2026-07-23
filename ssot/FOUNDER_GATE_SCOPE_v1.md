# Founder Gate Scope v1 — the closed set

**Status:** ACTIVE (derived view — consolidates already-locked law; authored on founder order, 2026-07-23)
**Sources of law:** `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md` (HARD_BLOCK closed list, FOUNDER_ONLY verdict, degrade-not-block), `docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md` (points #52, #53, #86, #138, #139), `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_BATCH_A-Z_v1.md` (lines 834, 1344).
**Enforcement:** `scripts/verify_founder_gate_scope_v1.py`

## The law, in plain words

The founder is interrupted for a decision **only** when the decision is on the closed
list below. Everything else is the machine's job: pick the default, do the work,
write a receipt. An agent that raises a founder decision outside this list is not
being careful — it is violating the runtime contract. The contract already says so:
*"a HARD_BLOCK without an allowed reason is itself malformed."*

## The closed set (the ONLY legitimate founder gates)

1. Destructive repo or file operations (permanent deletion, history rewrite)
2. Production deploy without commissioned authority
3. Money movement
4. Legal or financial commitments
5. Credential or security exposure
6. Irreversible external sends (emails to strangers, public posts)
7. Authority-plane changes (keys, app identity, permissions, lifting HOLD)
8. Merge / L5 / phase-unlock decisions

Nothing may be added to this list by an agent. Adding a gate is itself an
authority-plane change — item 7 — and therefore a founder decision.

## Before raising ANY founder decision, answer five questions

If **any** answer is yes, it is not a founder decision. Decide, act, write a receipt.

1. Can the SSOT or a lock doc answer it? → follow the SSOT.
2. Can a test or command answer it? → run it.
3. Is there a sane default? → take the default.
4. Is it reversible (branch, config, retry)? → do it, receipt it.
5. Can it run as a small bounded experiment? → run the experiment.

Only when all five are **no** AND the reason is on the closed set may a founder
packet be raised. This is doctrine #139, previously unenforced — now enforced by
`scripts/verify_founder_gate_scope_v1.py`.

## What is never a founder decision (examples seen in practice)

File names, branch names, lint choices, retry strategy, which test to run, receipt
formats, doc wording, wiring order, commissioning steps already described in a plan,
fixing a red check, re-running a failed job, choosing between two equivalent
implementations. These are machine details (doctrine #52). Dumping them on the
founder is a contract violation, not caution.

Also never a founder decision: **"should I proceed?" / "should I commit?" for work
the founder already ordered.** Committing ordered, verified work into the SSOT is
recording, not merge authority — gate 8 covers PR-merge authority, L5, and
production promotion, not the machine writing down what it was told to do. Asking
permission to continue ordered work is itself an invented gate.

## When a gate IS legitimate, the interrupt must be readable

Format (doctrine #53 — founder decision compression). Plain language, no jargon,
every codename explained in ordinary words:

- **What happened:** one line.
- **Options:** A / B (max C), one line each.
- **Recommended:** one of them, named.
- **Why:** at most 3 lines.
- **If you do nothing:** one line.

A founder packet longer than this, or written in internal jargon, fails the gate
even when the reason is legitimate.

## What this does NOT change

The eight real gates stay. HOLD and containment in `data/runtime_reality_v1.json`
stay exactly as they are. This document removes invented gates; it does not weaken
real ones.
