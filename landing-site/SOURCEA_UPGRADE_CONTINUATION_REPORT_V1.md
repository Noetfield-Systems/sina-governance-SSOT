# SourceA/Runway standalone landing continuation audit — v1

Date: 2026-07-22
Scope (this repo): /landing-site
Objective in this lane: make the standalone landing fully renderable, monetizable, and conversion-ready with concrete E2E checks.

## Completed audit findings
- Page rendering was failing for users due prior uncertainty and network/asset path ambiguity.
- Verified current live deploy serves the homepage and key assets with 200 on root routes.
- Found dead-prone route candidates in UI (`terms.html`/`privacy.html` redirected via clean URL layer) and missing end-to-end lead processing.

## Changes applied
1. Hardened page route/asset handling
- `landing-site/index.html`: kept paths relative for static assets/scripts.
- Added sticky CTA + urgency block and stronger conversion CTAs.
- Updated footer legal links to `/terms` and `/privacy` to avoid clean-url redirect layer.
- Added explicit lead capture endpoint binding on `#leadCaptureForm`.

2. Added real lead conversion endpoint
- New function: `landing-site/functions/lead.js`
- Route: `POST /lead`
- Behavior: validates required fields and returns JSON `{ ok:true, leadId, acceptedAt, ... }`.
- Includes `OPTIONS` preflight handling and 405 for non-POST methods.

3. Sales/verification hardening
- Kept pricing + lead qualification blocks in index for clearer purchase journey.
- Updated documentation with lead endpoint checks.
- Verification route checks remain functional (`/verifier.json`, `/verifier.txt`, `/verifier.html`).

## E2E evidence (live deployment)
- Deployment: https://9c55d1e5.noetfield-runway-standalone.pages.dev/
- Canonical domain: https://noetfield-runway-standalone.pages.dev/

### Route checks
- `GET /` -> 200
- `GET /styles.css` -> 200
- `GET /terms` -> 200
- `GET /privacy` -> 200
- `GET /verifier.json` -> 200
- `GET /verifier.txt` -> 200
- `GET /lead` -> 405 (expected)
- `OPTIONS /lead` -> 204
- `POST /lead` -> 200 with `leadId`
- `GET /v1/runway/runtime` -> 412 (standalone demo mode, expected)
- `GET /v1/runway/receipts/verify` -> 405 (expected)

## Remaining for “SourceA real usable” objective
This workspace is governed for SSOT/governance artifacts and this repo. SourceA app code changes must continue in SourceA venture lane.
Recommended SourceA handoff actions:
1) Reuse the upgraded landing pattern from this repo in SourceA landing routes.
2) Replicate `/lead` API contract in SourceA runtime entrypoint.
3) Add SourceA-specific offer tiers + SLA texts before traffic.
4) Run source-specific paid-click smoke tests (ad variant landing->lead endpoint->CRM integration).
