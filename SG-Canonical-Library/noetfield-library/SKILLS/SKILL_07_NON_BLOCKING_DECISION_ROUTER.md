# SKILL_07_NON_BLOCKING_DECISION_ROUTER

## Purpose
Keep chess reasoning from becoming a blocker.

## Routing
| Condition | Action |
|---|---|
| Low risk, reversible | PROCEED |
| Risky wording, reversible | PROCEED_WITH_PATCH |
| Deletes/exposes/signs/spends/changes control | ASK_IF_IRREVERSIBLE |

## Forbidden
- BLOCK
- stop forever
- create more governance first
- ask founder for routine reversible work

## Rule
The machine improves execution. It does not freeze execution.
