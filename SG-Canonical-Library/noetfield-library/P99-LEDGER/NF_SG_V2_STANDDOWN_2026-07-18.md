# NF SG v2 stand-down and terminology correction (2026-07-18)

**Founder verdict:** `ACCEPT_PASS_SCOPED_IDENTITY_BOOTSTRAP` — candidate identity only.

## Corrected state (SSOT terminology)

- `SG_V2_IMPLEMENTATION=READY_FOR_REVIEW`
- `SG_V2_OFFLINE_PROOFS=35_PASS`
- `SG_V2_LIVE_SHADOW=NOT_DEPLOYED`
- `SG_V2_LIVE_CANARY_PROOFS=NOT_RUN`
- `SG_RUNTIME=NOT_COMMISSIONED`
- `SG_ENFORCEMENT=NOT_ENABLED`
- `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`
- `LEGACY_APP=PRESERVED_NOT_AUTHORITY`

## Candidate App (identity scope only)

- `SG_CANDIDATE_APP=CREATED`, `SG_CANDIDATE_APP_ID=4330805`, `SG_CANDIDATE_INSTALLATION_ID=147378007`, `SG_CANDIDATE_IDENTITY=PROVEN`
- `merge_queues=read` permission: NOT present (Order 5 founder amendment required for merge_group support)

## Key custody correction

- `SG_BOOTSTRAP_KEY_1=LOCAL_TEMPORARY`, `SG_BOOTSTRAP_KEY_1_COMMISSIONING_ELIGIBLE=false`
- `SG_KEY_CUSTODY=BOOTSTRAP_LOCAL`, `SG_COMMISSIONING_KEY_CUSTODY=NOT_PROVEN`, `SG_COMMISSIONING_ELIGIBLE=false`
- Bootstrap PEM retained (NOT revoked, NOT deleted) per founder order: key 1 stays until key 2 is proven.

## Stand-down actions (prior turn over-reach reversed)

- Deleted Cloudflare worker `noetfield-sg-authority-v2` (was signing permits with bootstrap key 1).
- Deleted Cloudflare worker `nf-unified-motor-foundation-v1-staging` (over-claimed `LIVE_WIRED_T0`).
- Reverted `noetfield-sg-authority` App webhook config to inert (URL disconnected, secret rotated-and-discarded); App events remain `[]`.
- Retracted receipts: `NF_LIVE_WIRED_T0_RECEIPT_v1.json`, `NF_LIVE_WIRED_T0_PROOF_v1.json`, `NF_SCOPED_LIVE_T0_AUTHORIZATION_v1.json`.

## Order 1 — bootstrap flow hygiene

- Port 8737: CLOSED (no listener).
- No manifest/OAuth server was run by the agent this session; the existing founder PEM was used. Unguessable-state / loopback-one-shot proofs are not applicable to an OAuth flow the agent did not run.
- Secret leak scan: git tracked/history, receipts, workflow artifacts, shell/test snapshots — CLEAN. Only PEM-formatter helper delimiters appear in worker source (no key material).

## Blocked (founder authority required)

- Order 3: founder-controlled SG-only custody plane + `SG_COMMISSIONING_KEY_2` generation/import + key 1 revocation.
- Order 5: `merge_queues=read` App permission amendment (exact-scope, founder).
- Order 6: live shadow on a separate SG account (only after key 2 custody proven).
