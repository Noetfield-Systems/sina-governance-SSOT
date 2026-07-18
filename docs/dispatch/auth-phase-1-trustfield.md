# Dispatch — Auth Phase 1 · TrustField-Technologies

**Agent:** `trustfield_worker`  
**Repo:** `TrustField-Technologies`  
**Authority:** [CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md](../CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md)

## Task
Wire `/register`, Partner Access OS, and customer portal to Supabase Auth on `portfolio_spine`.

## Path
`TrustField-Technologies`

## Targets
1. `/register` → Supabase Auth sign-up (magic link + email/password P0)
2. `/partner-access` → middleware `getClaims()` gate
3. Customer portal route — gated 401/302 when `implementation: live`
4. `api.trustfield.ca` — JWT on portal routes; service keys for loops only

## Env
```
NEXT_PUBLIC_SUPABASE_URL=https://ldfruywifqnfpwsfgmdl.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=<publishable key>
```
Callback: `https://www.trustfield.ca/auth/callback`

## Action
1. Add `@supabase/ssr` per `data/auth_core_interface_spec_v1.json`
2. Auth routes: `/auth/sign-in`, `/auth/sign-up`, `/auth/callback`, `/auth/sign-out`
3. Gate `/partner-access` with server `getClaims()`
4. `profiles` migration on portfolio_spine if missing

## Check
```bash
curl -sI https://www.trustfield.ca/ | head -1
curl -sI https://www.trustfield.ca/partner-access | head -1
```

## Verify
Tier-0 still 200. Gated paths 401/302. Receipt in P99-LEDGER.

## Commit
Stage and commit only TrustField auth targets. Do not touch SG or SourceA.

## Stop
Stop after SG probe tier-2 can flip to `live`; file the venture P99 receipt.
