# FOUNDER EXCEPTION LEDGER
Status: DRAFT / SUBMITTED / UNVERIFIED
Authority: proposal only — not in force until founder adoption and owner assignment
Version label: v1.1 human-readable only, subordinate to git identity
Source: advisor spec (Founder Exception Budget), 2026-07-16; compiled by cloud agent. v1.1 applies the advisor review of 2026-07-16: placeholder row removed, CSV made canonical with stored factor scores, normalized guardrail rates, closure-as-new-row rule.
Governing law: D4-RECEIPT-LAW and D4-AGENT-NO-SELF-VERIFY apply to all closure claims
No PASS claimed.

Scope: every escalation to the founder, from any agent, workflow, or team.
Additions beyond the advisor's spec are marked ★.

## Core rule

Every time the founder answers, the system must learn something; otherwise the same cost is paid again.

Answering the case is NOT closing the exception. "Founder approved it" resolves today's instance. The exception is CLOSED only when a permanent artifact exists and passes the Definition of Done (section 7).

## 1. The ledger

Append one row at the moment an escalation reaches the founder. ★ A row must take under 30 seconds to write; the escalating agent writes its own row — the founder never fills this in manually.

The canonical, machine-appendable log is a single CSV — `ledger/founder-exception-ledger.csv`. This doctrine file carries no data rows, so the spec and the log can never disagree. CSV columns, exactly:

```csv
id,date,escalating_agent,lane,exception,trigger,founder_input,missing_capability,recurrence,frequency_score,founder_cost_score,preventability_score,permanent_owner,closure_condition,priority_fxcxp,status
```

- `date`, `escalating_agent`, `lane` are auto-populated by the logging mechanism, keeping a row under 30 seconds.
- `frequency_score`, `founder_cost_score`, `preventability_score` are stored per row (each 1–5).
- `priority_fxcxp` is the computed product of the three stored scores — never hand-entered, so any verifier can recompute it.
- The CSV is append-only. A closure is a NEW row with the same `id` and `status` CLOSED, citing the closure receipt in `closure_condition` — existing rows are never rewritten.

## 2. Priority formula

Priority = Frequency × Founder Cost × Preventability. Score each factor 1–5.

- Frequency: how often this exception recurs.
- Founder Cost: time + context switching + cognitive load. ★ Add +1 (cap at 5) when the stalled work is in the revenue lane — there the exception costs revenue latency, not just founder attention.
- Preventability: confidence it can be removed by a system artifact.

Scores are stored per row (section 1); the ★ revenue rule applies to `founder_cost_score` and is auditable via the `lane` column.

Work the ledger from the highest score down. Expect small frequent approvals (e.g. 5×3×5 = 75) to outrank rare big decisions (e.g. 2×5×3 = 30). Sensitive legal/capital calls (e.g. 1×5×1 = 5) stay with the founder permanently.

## 3. Conversion rule (owned by SourceA / Noetfield)

```text
IF an exception occurs more than once
AND the decision rationale can be expressed explicitly
AND the downside is bounded or reversible
THEN a permanent system artifact must be created
BEFORE the exception is considered closed.
```

Allowed artifact types: Rule, Pattern, Router, Verifier, State transition, Delegation boundary, Context package, Escalation criterion.

## 4. Good vs bad escalation test

Escalate to the founder (GOOD) only if at least one holds:

- the decision is irreversible;
- high legal, capital, or reputational risk;
- it changes the company's strategic direction;
- it requires the founder's personal preference or formal authority;
- evidence is incomplete and an automated decision would be dangerous.

Do NOT escalate (BAD — answer from the system, log the row, fix the gap) when:

- the answer has been given before;
- the decision is low-risk and reversible;
- the agent is asking from fear / has no confidence threshold;
- a rule exists but was not retrieved;
- the workflow has no defined next state;
- nobody owns converting the answer into a capability.

## 5. Guardrail metrics — always reported as a pair, never alone

1. Founder Exception Rate — preventable founder escalations per 100 completed agent tasks.
2. Unsafe Autonomy / Reversal Rate — reversed or unauthorized autonomous decisions per 100 autonomous decisions.

Weekly raw counts stay as operational context; trend comparisons use the normalized rates — raw counts mislead as task volume grows.

Target: metric 1 falls while metric 2 stays flat or falls. If metric 2 rises while metric 1 falls, agents are hiding problems or overstepping — stop and audit before continuing.

## 6. Ownership contract

- SourceA — converts exceptions into capability: Exception → pattern extraction → Machine/Router/Verifier → test → deployment.
- Noetfield — owns meaning and decision boundaries: who has authority, what evidence is sufficient, when escalation is mandatory, what the confidence thresholds are.
- TrustField — owns operational delegation: playbooks, role ownership, SLAs, QA checkpoints, execution training and review.
- Pattern Factory — prevents one-off fixes: one incident → local fix; two similar incidents → candidate pattern; three similar incidents → mandatory systemization.

## 7. Definition of Done (per exception)

An exception is CLOSED only when ALL hold:

- root cause is identified;
- a permanent artifact is built;
- a future owner is assigned;
- it has run at least once without the founder;
- the result is checkable by a Verifier or by evidence — per D4-RECEIPT-LAW, CLOSED is computed from a receipt, never declared; per D4-AGENT-NO-SELF-VERIFY, the agent that built the artifact cannot certify its own closure;
- the real escalation path is still preserved (default escalation removed, ability to escalate kept).

## 8. End-of-day log — three questions

1. Which escalation must never repeat?
2. Which artifact replaced my in-the-moment judgment?
3. What evidence shows the system actually continues without me?
