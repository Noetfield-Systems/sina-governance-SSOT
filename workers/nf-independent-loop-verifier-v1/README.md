# nf-independent-loop-verifier-v1

Independent loop auditor on Cloudflare secondary account `b7282b4a`.

## KV free-tier cutback (P0)

Secondary-account Workers KV is on free tier. This worker:

- Writes **3** KV keys per tick (`last_fired_at`, `last_verdict`, `last_receipt`) — no `verify:${at}` history.
- Serves `/health` from in-isolate memory first; cold start may KV-read once.
- Cron: every 2 hours (`0 */2 * * *`, `INTERVAL_MINUTES=120`).

## GHA posture (unchanged)

Enterprise **50k** Actions minutes remain for ROI classes **A–D**. This cutback is **CF KV free tier on the secondary account**, not a directive to kill or throttle GitHub Actions.
