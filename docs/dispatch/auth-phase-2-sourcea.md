# Dispatch — Auth Phase 2 · SourceA

**Agent:** `sourcea_worker`  
**Repo:** `SourceA`

## Task
Header sign-in/up; contract SKUs stay Tier-0 public.

## Path
`~/Projects/SourceA`

## Action
1. `@noetfield/auth-core` pattern
2. Protect sandbox only — not contract SKU pages
3. Callback: `https://sourcea.app/auth/callback`

## Check
`scripts/validate-sourcea-contract-pages-e2e-v1.sh` — ALL PASS without session

## Commit
SourceA only.
