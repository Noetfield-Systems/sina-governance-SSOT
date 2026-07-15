Cost Lock Plan — strict enforceable rules (repo-local + operational steps)

Policy summary (enforced):
- Unknown model/provider = BLOCK.
- Scheduled job that calls UNKNOWN model/provider = DISABLE or set to REPORT-ONLY until attested.
- Any path that can call a PREMIUM model = FAIL (cannot run until refactored to allowed model or explicitly approved with cost receipts).
- Any path that can FALLBACK to PREMIUM = FAIL.
- Missing cost_policy_pass receipt for scheduled/background/deploy jobs = FAIL (fail-closed).

Immediate repo-local enforcement (must be implemented now)
1) CI early-fail: .github/workflows/agentic-ci.yml must run scripts/cost_policy_enforcer.py as the first step (before any install or steps that could use secrets). Configure --fail-on-code option.
2) Promotion gate locking: gates/promotion_gate.py refusal_reasons must include cost_policy_pass verification. Deploy will be refused if receipts/cost_policy_pass.json is missing or invalid.
   - receipts/cost_policy_pass.json schema: {commit_sha, checked_by_ci:true, timestamp, allowed_models:[...], signature_optional}
3) Autorun hardening: scripts/brain_loop_autorun_v1.sh must default to OBSERVE_ONLY unless:
   - receipts/cost_policy_pass.json is present and valid, AND
   - environment variable ALLOW_REMOTE_DEPLOY=true is set on a monitored runner, AND
   - founder approval receipt exists for autonomous deploys.
   If conditions not met, autorun must only produce receipts and not call verifier or promote scripts.
4) Verifier call lockdown: scripts/trigger_verifier_run_v1.py (and any caller) must be disabled from scheduled/autorun contexts. Any automated POST to verifier_base_url must be blocked until the verifier provider/model and cost profile are attested by org admins.
5) Pre-commit & pre-push: add a developer pre-commit hook (distribution in .githooks/ or CONTRIBUTING.md) to run scripts/cost_policy_enforcer.py --local-check and fail locally on banned patterns.
6) Runner token isolation: CI runners MUST NOT expose Cloudflare or premium-provider tokens. Reserve a single monitored runner (recorded, auditable) that can hold deploy tokens; developer machines must not have persistent deploy tokens.

Medium-term (org-coordinated, requires credentials)
1) Org-wide inventory: require org-admin to enumerate:
   - All GitHub org workflows with schedule/dispatch and their 'enabled' state and last_run timestamps
   - Cloudflare Workers cron schedules and usage logs
   - Vercel/Railway/Render/Supabase scheduled functions
   - Cursor/Copilot/IDE automation registry (developer list)
   For each, produce provider/model attestation and cost receipts.
2) Automated weekly cost & autonomy report: run autonomy_scorer + cost enforcer, post report artifact, and flag any schedule changes that add blocked patterns.
3) Branch-protection rule: block merges that introduce banned provider/model references in code/workflows unless a cost_policy exception (with receipts) is attached.

Remediation actions & incident plan
- On discovery of a scheduled job calling UNKNOWN or PREMIUM provider: immediately disable scheduled trigger (set enabled: false) or convert to report-only run; issue incident receipt with commit_sha and scope.
- On detected background premium usage: revoke runner tokens, rollback recent deploys, open an incident receipt, notify founder and org-admins; require founder-signed exception to re-enable.

Developer workflow & artifacts
- receipts/cost_policy_pass.json: canonical CI-emitted artifact proving a change is allowed. CI must attach it to PR and store it in receipts/ for audit.
- receipts/cost_policy_incident.json: emit when a blocked or premium call was attempted; include evidence, logs, and responsible actor.
- Contributor checklist (CONTRIBUTING.md): include steps to run scripts/cost_policy_enforcer.py and how to request cost_policy exception.

Concrete code changes recommended (repo-local)
- Add explicit refusal in gates/promotion_gate.py: check for receipts/cost_policy_pass.json and reject if missing. (Low-risk edit.)
- Modify scripts/promote_brain_worker_v1.sh to refuse to run wrangler deploy unless cost receipt + ALLOW_REMOTE_DEPLOY=true present.
- Modify scripts/brain_loop_autorun_v1.sh to accept --no-deploy or default to observe-only and to refuse to call trigger_verifier_run_v1.py when scheduled and verifier not attested.
- Add CI step in agentic-ci.yml to produce receipts/cost_policy_pass.json when PR passes cost checks (for documented allowed changes).

Operational blockers (need from org admin/devs)
- GitHub org token (read-only or workflow-read) to list all org workflows, last_run, and enabled state
- Cloudflare read-only token to list Workers, cron triggers, and invocation logs
- Verifier service attestation: confirmation from service owners of model/provider used and a cost_profile receipt
- Developers' Copilot/Cursor automation registry export

Immediate next actions I can take now (repo-local):
- Implement the three low-risk code edits: gate refusal check, promote script harden, autorun default observe-only. Commit and run local tests. (Safe, repo-local.)
- Or pause and request org admin tokens to finish org-level inventory and produce a full cross-surface token_leakage_matrix.csv with last_run and enabled states.

Policy enforce summary (must be enforced everywhere):
- Unknown -> BLOCK
- Scheduled unknown -> DISABLE/REPORT-ONLY
- Premium or fallback to premium -> FAIL
- Missing cost receipt -> FAIL

