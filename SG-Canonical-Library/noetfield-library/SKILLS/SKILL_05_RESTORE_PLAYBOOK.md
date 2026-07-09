# SKILL_05_RESTORE_PLAYBOOK

## Purpose
Recover from downgrade without rolling back safe backend improvements.

## Procedure
1. Stop expansion.
2. Identify last good feature set.
3. Restore missing user-facing capabilities.
4. Preserve safe backend changes.
5. Deploy surgical restore.
6. Verify live.
7. Write restore receipt.

## Rule
Do not solve a feature-loss incident with a broad rollback unless necessary.
