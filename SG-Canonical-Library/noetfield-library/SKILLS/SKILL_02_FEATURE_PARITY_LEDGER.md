# SKILL_02_FEATURE_PARITY_LEDGER

## Purpose
Prevent accidental feature loss.

## Procedure
Before edit:
1. List all visible/reachable features.
2. Mark protected assets.
3. Mark explicit removals.
4. After deploy, verify protected assets remain visible/reachable.

## Output
```yaml
feature_parity:
  protected:
  removed_only:
  preserved_after:
  missing_after:
  unexpected_loss:
```

## Rule
If a feature was not explicitly approved for removal, it is protected by default.
