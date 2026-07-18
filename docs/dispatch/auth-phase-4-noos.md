# Dispatch — Auth Phase 4 · noetfeld-os

**Agent:** `noos_agent`
**Repo:** `noetfeld-os`
**Authority:** [CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md](../CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md)

## Task
Add JWT middleware to `api.noetfield.com`; browser cookies must never authorize Worker motors.

## Path
`~/Projects/noetfeld-os`

## Target
API authentication middleware and protected Motor routes only.

## Action
1. Validate Bearer JWTs issued by `portfolio_spine`.
2. Use service-role credentials only in server/CI custody; never expose them to browsers.
3. Return 401 for missing, expired, wrong-issuer, or malformed tokens.
4. Preserve the public health endpoint and existing NOOS observe/classify/route behavior.

## Check
```bash
curl -sI https://api.noetfield.com/health
curl -sI https://api.noetfield.com/<protected-route>
```
Health stays available; an anonymous protected request returns 401.

## Verify
Run middleware negative tests and the SG auth surface probe after deploy. Record exact deployment SHA and endpoint evidence.

## Commit
Stage and commit noetfeld-os auth middleware targets only.

## Stop
Stop after live verification and file the venture P99 receipt. Do not edit SG or product UI repositories.
