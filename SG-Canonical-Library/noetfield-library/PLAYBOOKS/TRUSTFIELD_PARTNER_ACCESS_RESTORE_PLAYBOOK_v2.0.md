# TRUSTFIELD_PARTNER_ACCESS_RESTORE_PLAYBOOK_v2.0

## Trigger
Use when Partner Access loses platform/auth/status/application features after a UX, deploy, or cleanup pass.

## Goal
Restore full feature parity without rolling back safe v2.1+ backend improvements.

## Steps
1. Identify last good build/source where the missing features existed.
2. List missing user-facing features.
3. Restore only missing feature layer.
4. Preserve:
   - backend validation
   - scoring
   - status machine
   - admin gating
   - NDA gating
   - e-sign metadata
   - request-call endpoint
   - health monitor fixes
5. Deploy WWW. Deploy API only if required.
6. Verify live:
   - Sign in visible
   - Create account visible
   - Partner Access Platform visible
   - View application status visible when applicable
   - Request Partner Access visible
   - three tracks visible
   - apply routes work
   - protected backend tests pass
7. Write receipt.

## Receipt name
`PARTNER_ACCESS_FULL_FEATURE_RESTORE_v2`
