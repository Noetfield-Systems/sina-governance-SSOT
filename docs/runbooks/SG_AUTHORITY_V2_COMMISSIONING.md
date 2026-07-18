# Runbook — SG Authority v2 commissioning

**Decision:** `NF-SG-AUTHORITY-IDENTITY-V2`  
**Current state:** `SG_V2_SHADOW=LANDED` (PR #28) · `SYSTEM_STATUS=SCOPED_LIVE_T0_AUTHORIZED` · `SG_RUNTIME=NOT_COMMISSIONED` until live deploy evidence

Shadow worker landed at `workers/sg-authority-v2-shadow/` (merge commit `898d67e5ca9eab9ae6161658cfdef3b2c48e6360`). Production worker path prepared at `workers/sg-authority-v2/` (`noetfield-sg-authority-v2`, App `4330805`, installation `147378007`). Scoped live T0 commissioning authorized; `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD` remains. Do not claim `FULLY_COMMISSIONED`.

## A. Containment

Enforce `data/runtime_reality_v1.json`, disable autonomous mutation paths, preserve legacy evidence, and deny legacy App/installation/receipt identities. Do not revoke legacy credentials yet. Allowed under containment: event intake, T0 workflows, receipt writes, signed permit evaluation — not autonomous production merge/deploy/content publication.

## B. Identity

Founder creates organization-owned App `noetfield-sg-authority` with metadata/contents/PRs/Actions read, Checks write, and no code/workflow/deployment/secret/admin write. Install only on SG and one non-production canary. SG private key, webhook secret, and receipt-signing key live under custody separate from Motor.

## C. Deterministic shadow evaluator

Pure outcomes: `PASS`, `FAIL`, `BLOCKED`, `ESCALATE_REQUIRED`. Identity attestation begins every run: authenticate App, `GET /app`, verify owner/App ID, resolve organization installation, mint token, list installation repositories, and verify target membership. Never fall back to unauthenticated public access.

Verify webhook HMAC before parsing. Reject replayed delivery IDs. For `merge_group`, evaluate the merge-group head SHA. Every signed receipt binds exact App/install/repo/SHA/action/target/artifact/policy/schema/evaluator/Worker/signing-key/nonce/time/expiry.

## D. Canary negatives

Prove correct request PASS and wrong SHA, artifact, policy, evidence, expiry, nonce replay, personal identity, public fallback, Motor spoof, invalid HMAC, replayed delivery, and wrong merge-group SHA all BLOCKED.

## E. Enforcement

Require `Noetfield SG / P0 Authority` from exact source App `noetfield-sg-authority`; no routine bypass actors. Motor requires the exact signed permit and returns `BLOCKED_MISSING_SG_PERMIT`, `BLOCKED_INVALID_SG_PERMIT`, or `BLOCKED_SG_UNAVAILABLE` fail-closed.

## F. Commission and retire

Require multiple cold starts, exact-source ruleset proof, human/Motor bypass-negative proof, replay-negative proof, key rotation, rollback, and deployment/source attestation. `SG-N` authorizes `SG-N+1`; bootstrap uses founder/threshold custody. Only after commissioning revoke legacy keys, uninstall `143449507`, archive/delete App `4179901`, and file P99 decommission evidence.
