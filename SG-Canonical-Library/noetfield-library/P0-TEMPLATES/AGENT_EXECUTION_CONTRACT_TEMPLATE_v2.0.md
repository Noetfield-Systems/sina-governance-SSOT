# AGENT_EXECUTION_CONTRACT_TEMPLATE_v2.0

Use this for any worker that edits live systems.

```text
MISSION:
[task]

SCOPE:
[exact paths/routes/systems allowed]

OUT OF SCOPE:
[systems/features not to touch]

CHESS PASS:
- Current board:
- Move 1:
- Move 2 risk:
- Move 3 consequence:
- Patch before execution:
- Action label:

PRESERVE:
[features/routes/flows]

REMOVE ONLY:
[exact removals]

IMPLEMENT:
[steps]

VERIFY:
[checks]

ROLLBACK:
[restore trigger + path]

RECEIPT:
[required fields]

STOP CONDITION:
Stop after receipt. Do not expand scope.
```
