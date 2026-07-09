# DEPLOY_DRIFT_PLAYBOOK_v2.0

## Symptoms
- live build marker differs from expected
- repo says feature exists but browser does not show it
- monitor false-negative
- old copy appears after deploy
- route served from different worker/branch/cache

## Response
1. Compare repo commit, pushed remote, deploy target, live build marker.
2. Fetch live HTML and search full page, not truncated sample.
3. Check Cloudflare/Railway deploy target.
4. Purge cache if needed.
5. Redeploy correct target.
6. Verify live protected features.
7. Write drift receipt.
