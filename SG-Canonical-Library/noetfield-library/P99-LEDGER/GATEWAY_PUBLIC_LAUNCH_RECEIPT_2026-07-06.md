# GATEWAY Public Launch Receipt

**Date:** 2026-07-06  
**Service:** SINA GATEWAY  

## Launch state

| Item | Status |
|------|--------|
| HTTPS URL live | ✅ `https://sina-gateway-production.up.railway.app` |
| Supabase capture | ✅ Noetfield `gateway_leads` |
| Turnstile | ✅ Supported (production env on Railway) |
| Search indexing | ⏸ **Intentionally blocked** — `noindex,nofollow` + `robots.txt` disallow |
| Custom domain | Founder-decide (optional) |

## Rationale

Per `docs/PUBLIC_LAUNCH_GATE_LOCKED_v1.md`, public **indexing** remains gated until founder removes noindex. HTTPS intake is live for invited traffic and UTM campaigns (e.g. founder-audit D2 list).

## Checklist items 17–20 (LAUNCH_CHECKLIST.md)

- Production env validated via `chain:health` PASS
- No service-role key in app
- Browser bundle contains no Supabase secrets (server-side capture only)
- Rollback: remove Railway public URL / DNS first

**Next founder action for full SEO launch:** remove noindex, update robots.txt, assign custom domain.

**Signer:** Step 9 gate — HTTPS public intake live; indexing deferred by design
