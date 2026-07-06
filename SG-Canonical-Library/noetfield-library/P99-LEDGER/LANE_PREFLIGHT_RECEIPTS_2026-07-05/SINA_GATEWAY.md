# LANE PREFLIGHT — SINA GATEWAY

**Lane:** SINA GATEWAY (Lead intake / revenue-organ mouth)  
**Date:** 2026-07-06  
**Status:** SG_PREFLIGHT_VERIFIED  

| Field | Value |
|-------|-------|
| Canonical folder | `/Users/sinakazemnezhad/Desktop/SINA GATEWAY` |
| Git remote | `https://github.com/kazemnezhadsina144-dot/sina-gateway.git` (legacy org slug — migrate to `Noetfield-Systems/sina-gateway` when org repo exists) |
| Branch | `cursor/update-private-test-readiness-receipt...origin/cursor/update-private-test-readiness-receipt` |
| HEAD | `81ee590` Update 10-step plan snapshot after production verification passes |
| Production URL | `https://sina-gateway-production.up.railway.app` |
| Supabase project | `tkgpapowwplupyekpivy` (noetfield) — anon insert-only |
| Credential source | `~/.sourcea-secrets/sina-gateway.env` |
| SG blueprint mirror | `P10-PRODUCT-LAYERS/SINA_GATEWAY_BLUEPRINT_LOCKED_v1.md` (repo is authority) |

**Preflight checks (2026-07-06):**

- Remote exists and fetchable
- Single canonical Desktop path documented (`data/supabase-binding-v1.json`, `DEPLOY.md`)
- `npm run verify:supabase` → INSERT OK + READ DENIED BY RLS
- No `SUPABASE_SERVICE_ROLE_KEY` in app env contract

**Signer:** SG-v0.9-preflight / Cursor 10-step upgrade pass
