# CHESS_PASS_PROMPT_TEMPLATE_v2.0

Use this inside implementation prompts.

```text
CHESS PATTERN REASONING REQUIRED.

This is not a blocker. Use it to improve the move before execution.

MISSION:
[exact task]

RAW MOVE:
[what we think we want to do]

CURRENT BOARD:
- Live state:
- Repo state:
- User/business goal:
- Sensitive boundaries:
- Known drift or risk:

CHESS PASS:
1. Move 1: What immediate change will happen?
2. Move 2: What could this accidentally remove, weaken, expose, or confuse?
3. Move 3: What commercial, legal, deploy, or founder-control consequence could follow?
4. Patch: How should the instruction be improved before execution?
5. Proceed: Execute the patched move unless the action is irreversible.

PRESERVE:
- [protected feature]
- [protected route]
- [protected workflow]

REMOVE ONLY:
- [exact founder-authorized removals]
- If empty, no removals are authorized.

DO NOT:
- remove working features by interpretation
- convert “clean/minimal/polish” into capability deletion
- create founder permission loops for reversible changes
- expose private materials
- claim false legal/regulatory status

VERIFY:
- [live route check]
- [HTML/browser evidence]
- [protected features still visible/reachable]
- [tests]
- [build marker]
- [receipt path]

OUTPUT:
- chess pass summary
- final patched instruction executed
- verification result
- receipt
```
