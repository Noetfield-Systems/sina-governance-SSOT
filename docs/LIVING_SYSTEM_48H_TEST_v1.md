# Living System 48h Cloud Liveness Test v1

## Purpose
Laptop-closed proof that commissioned cloud loops keep firing without a founder mac session.

## Watched loop_ids
1. `nf-commissioning-specialist-tick-v1` — CF cron `*/5`
2. `nf-unified-motor-foundation-v1-staging` — event gateway + resident roles health
3. Independent deadman (`noos-deadman-v1` or SG twin) — 2x interval stale → alert + one restart

## Start criteria (all required)
- Gate 1 key2 custody `ESTABLISHED`
- Gate 2 event gateway staging health 200
- Gate 3 `sg_role` + `noos_role` commissioned on staging
- Hold preserved (`AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`)

## Protocol
1. File start receipt listing loop_ids, health URLs, expected cadences.
2. Close laptop / end founder session for >= 48h.
3. Deadman writes `last_fired_at` checks every interval; on 2x stale: alert + one POST restart + receipt.
4. After 48h, collect KV/`last_fired_at` samples and compute max gap.
5. pass if max gap <= 2x cadence for every watched loop and no fake live claims.
6. fail with exact loop_id + gap evidence otherwise.

## Receipts
- Start: `receipts/48h-test-run1-START.json`
- End: `receipts/48h-test-run1-pass.json` or `receipts/48h-test-run1-fail.json`

## Forbidden
- Claiming pass from docs alone
- Counting mac launchd as the primary motor
- Lifting hold to force heartbeats
