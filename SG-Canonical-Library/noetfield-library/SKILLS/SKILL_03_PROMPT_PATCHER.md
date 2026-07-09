# SKILL_03_PROMPT_PATCHER

## Purpose
Transform risky human/agent wording into execution-safe instructions.

## Risk words
- clean
- minimal
- simplify
- streamline
- reduce clutter
- polish
- remove conflicting funnel
- modernize

## Patch pattern
Raw:
```text
Make the page cleaner.
```

Patched:
```text
Improve clarity without removing existing working capabilities.

REMOVE ONLY:
- [exact removals]

PRESERVE:
- [protected features]
```

## Output
- risky phrase detected
- possible misread
- patched instruction
