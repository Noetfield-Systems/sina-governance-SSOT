# SKILL_01_CHESS_PASS

## Purpose
Run a fast chess reasoning pass before acting.

## Inputs
- mission
- raw move
- current live/repo state
- protected assets
- allowed removals
- irreversible actions

## Procedure
1. Identify the move.
2. Forecast immediate effect.
3. Forecast likely misread.
4. Forecast downstream consequence.
5. Patch the move.
6. Choose action label.
7. Proceed if reversible.

## Output
```yaml
CHESS_PASS:
  move:
  likely_misread:
  second_move_risk:
  third_move_consequence:
  patch_before_execution:
  action:
```

## Default
If reversible: patch and proceed.
If irreversible: ask founder.
