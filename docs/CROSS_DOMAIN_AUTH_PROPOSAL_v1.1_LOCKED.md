# Cross-Domain Auth Proposal v1.1 — SG SSOT (LOCKED)

**Status:** LOCKED v1.1.0 · **Lock authority:** SG auth upgrade W11 · **Authority:** SG verifies; venture repos implement
**Refs:** [Supabase Auth](https://supabase.com/docs/guides/auth) · [Next.js SSR](https://supabase.com/docs/guides/auth/server-side/nextjs)
**Machine matrix:** `data/auth_surface_matrix_v1.json` (v1.1.0)
**Probe:** `scripts/verify_auth_surfaces_e2e_v1.py` · motor `sg_auth_surface_probe_v1`

---

## Executive recommendation

**Do not login-wall every public page.** Tier access instead:

| Tier | Access | Examples |
|------|--------|----------|
| **0** | Public | Contract SKUs, GTM, `/entity-status` |
| **1** | Optional sign-up | `/register`, sandbox CTAs |
| **2** | Gated | Partner Access OS, customer portal |
| **3** | API / motors | JWT or service role — never user cookies on Workers |

**Identity plane:** `portfolio_spine` Supabase (`ldfruywifqnfpwsfgmdl`) — sole Auth issuer.
**Factory project:** `tkgpapowwplupyekpivy` — runtime tables only, linked by `user_id`.
**Cross-domain:** Per-domain sessions (A). Same `user_id` when email matches; no shared cookie across `.app`/`.ca`/`.com`.

---

## Repo ownership (one writer per task cell)

| Repo | Agent | Phase | Auth work |
|------|-------|-------|-----------|
| **TrustField-Technologies** | `trustfield_worker` | **1** | `/register`, portal, Partner Access, `api.trustfield.ca` JWT |
| **SourceA** | `sourcea_worker` | 2 | `sourcea.app` sign-in/up, sandbox |
| **Noetfield** (website) | `noetfield_website` | 3 | noetfield.com auth UI |
| **noetfeld-os** | `noos_agent` | 4 | `api.noetfield.com` JWT middleware |
| **trustfield-loops** | `trustfield_worker` | 1 | Webhooks verify JWT only |
| **sina-governance-ssot** | `sg_sssot_cursor` | **5** | Verify + registry — **no UI** |

**Forbidden:** One PR touching SourceA + TrustField + SG.

---

## Technical pattern

Shared package `@noetfield/auth-core` (create in SourceA or small repo):

- `createBrowserClient` / `createServerClient` (`@supabase/ssr`)
- Middleware: token refresh + `getClaims()` guard
- Routes: `/auth/sign-in`, `/auth/sign-up`, `/auth/callback`, `/auth/sign-out`

**Server law:** `getClaims()` on server — not `getSession()` alone.

**Redirect allow list** (Supabase dashboard + `auth_surface_matrix_v1.json`):

```
https://sourcea.app/auth/callback
https://www.noetfield.com/auth/callback
https://www.trustfield.ca/auth/callback
http://localhost:3000/auth/callback
```

### Postgres (portfolio_spine)

```sql
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  venture text not null check (venture in ('sourcea','noetfield','trustfield')),
  role text not null default 'member',
  created_at timestamptz default now()
);
alter table public.profiles enable row level security;
```

---

## SG Phase 5 (implemented here)

| Asset | Path |
|-------|------|
| Surface matrix | `data/auth_surface_matrix_v1.json` (v1.1.0) |
| E2E probe | `scripts/verify_auth_surfaces_e2e_v1.py` |
| GHA motor | `.github/workflows/sg-auth-surface-probe-v1.yml` |
| Registry | `gh_actions_sg_auth_surface_probe_v1` · 6h cron |
| Receipts | `receipts/auth-surface-probe-*.json` |
| Deadman | `sourcea-deadman-v1` |

**Closed loop:** probe → FAIL/WARN → alert → venture fix → redeploy → probe PASS

---

## Founder decisions

**Ratified 2026-07-18 (Phase 1 unblocked):**

1. **Auth project** → `portfolio_spine` only
4. **First ship** → TrustField `/register` + portal

**Still pending:**

2. **Cross-brand login** → per-domain sessions (recommended)
3. **P0 methods** → magic link + email/password
5. **Enterprise SSO** → defer P2

---

## What NOT to do

1. Login wall on contract SKU pages
2. SourceA branding on trustfield.ca auth
3. Service role in browser
4. `getSession()` alone on server
5. Clerk/Auth0 alongside Supabase
6. Auth UI in SG repo


---

**Lock receipt:** `SG-Canonical-Library/noetfield-library/P99-LEDGER/CROSS_DOMAIN_AUTH_RATIFY_2026-07-08.md`
