# Dispatch — Auth Phase 2 · SourceA

**Agent:** `sourcea_worker`
**Repo:** `SourceA`
**Authority:** [CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md](../CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md)

## Task
Add SourceA sign-in/up and protect the buyer sandbox while every contract SKU remains Tier-0 public.

## Path
`~/Projects/SourceA`

## Target
Header auth controls, `/auth/*` routes, and buyer-sandbox middleware only.

## Env
```text
NEXT_PUBLIC_SUPABASE_URL=https://ldfruywifqnfpwsfgmdl.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=<publishable key>
```
Callback: `https://sourcea.app/auth/callback`

## Action
1. Implement the `data/auth_core_interface_spec_v1.json` contract with `@supabase/ssr`.
2. Add `/auth/sign-in`, `/auth/sign-up`, `/auth/callback`, `/auth/sign-out`.
3. Gate the buyer sandbox with server-side `getClaims()`.
4. Keep `/`, `/operating-brain-install`, `/ai-value-governance`, and `/enterprise-ai-control-plane` public.
5. Set `Cache-Control: private, no-store` on auth/session responses.

## Check
```bash
scripts/validate-sourcea-contract-pages-e2e-v1.sh
```
All contract pages must pass without a session; sandbox access must reject or redirect an anonymous request.

## Verify
Run the SG auth surface probe after deploy. Tier-0 SourceA rows remain PASS and auth callback matches the allow-list.

## Commit
Stage and commit SourceA auth targets only.

## Stop
Stop after deploy verification and file the venture P99 receipt. Do not edit SG, TrustField, or NOOS.
