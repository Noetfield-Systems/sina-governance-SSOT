# SG commissioning key 2 custody (2026-07-18)

**Plane:** independent verifier Cloudflare account `b7282b4a5c17b84d62e3ef8866b878f8` (not main).

**Worker:** `noetfield-sg-authority-v2-shadow`  
**URL:** https://noetfield-sg-authority-v2-shadow.kazemnezhadsina144.workers.dev  
**Health:** `mode=SHADOW`, `sg_runtime=NOT_COMMISSIONED`, `enforcement_enabled=false`

**Key 2 public fingerprint (sha256 of public DER):** `22a9513a3aaee95266538a5fc49c94a4591119d14fe9332f2964fd603817c3a8`  
Proven: GET /app, installation `147378007`, exact two repos. Imported as Worker secret `SG_APP_PRIVATE_KEY`.

**Receipt-signing key:** separate ES256 key `sg-receipt-e58df1e53eb48785` (not the GitHub App key).

**Key 1:** still active. GitHub has no API to delete App private keys. Founder must delete the OLD key in the App UI, then local bootstrap PEM is deleted and rotation proof is completed.

**HOLD / NOT_COMMISSIONED / NOT_ENABLED preserved.**
