# NF LIVE_WIRED_T0 — 2026-07-18

**Status:** `LIVE_WIRED_T0`  
**HOLD:** `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`  
**Not claimed:** `FULLY_COMMISSIONED`

## Live surfaces
- Motor staging: https://nf-unified-motor-foundation-v1-staging.sina-kazemnezhad-ca.workers.dev
- SG authority: https://noetfield-sg-authority-v2.sina-kazemnezhad-ca.workers.dev
- Deadman: https://noos-deadman-v1.sina-kazemnezhad-ca.workers.dev

## Proven now
- Signed `/v1/events` → NOOS Portfolio Owner → workflow start
- Dual GitHub webhook HMAC paths (motor + sg) with replay rejection
- SG `/v1/permit/exact` signed permit under HOLD
- Production mutation route blocked (`deploy.production`)

## 48h watch
- Status: STARTED
- Started: 2026-07-18T13:41:27Z
- Due: 2026-07-20T13:41:27Z
- Target after pass: `COMMISSIONED_T0_PROVEN`

## Remaining founder UI
1. `noetfield-motor` App → enable webhook → URL `.../webhooks/github/motor` + staging secret + event subscriptions
2. `noetfield-sg-authority` App → enable event subscriptions `pull_request`, `merge_group`
