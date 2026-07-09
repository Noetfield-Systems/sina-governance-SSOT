# GATEWAY Staging Deploy Receipt

**Date:** 2026-07-06  
**Service:** SINA GATEWAY  
**Deploy plane:** Railway  

| Field | Value |
|-------|-------|
| URL | `https://sina-gateway-production.up.railway.app` |
| Health | `/health` → `ok` |
| Ready | `/ready` → `captureMode=supabase`, `table=true` |
| Commit reference | `81ee590` (10-step upgrade branch baseline) |
| Supabase | Noetfield `tkgpapowwplupyekpivy` |
| Indexing | Blocked (`robots.txt` disallow all; `noindex,nofollow`) |

**Remote smoke:** `npm run private-test` → browser-capture PASS (requestId logged in runbook output).

**Signer:** Step 6 gate — staging HTTPS live with Supabase capture
