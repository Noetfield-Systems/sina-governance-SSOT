Active Runtime Inventory — full repo-local audit (classifies Daily/Weekly/Manual automations)

Scope: repo-local automations, GitHub Actions, local launchd autoruns, scripts that run in background/cron/autorun, and HTTP model/verifier endpoints referenced. Not include org-level external systems (requires admin/API access). Where external/unknown provider or model is detected, policy = BLOCK by default.

Summary of automation surfaces (classification follows):
- GitHub Actions (hourly): .github/workflows/agentic-ci.yml
- GitHub Actions (6-hourly): .github/workflows/brain-loop-autorun-v1.yml
- Local Launchd / Mac autorun (6-hourly or 24x7): scripts/install_brain_loop_launchd_v1.sh + com.sina.brain-loop-autorun-v1.plist
- Manual / Confirm-each-time deploys: scripts/promote_brain_worker_v1.sh (confirm or --autonomous-deploy)
- Parallel verifier batch: scripts/run_parallel_brain_candidates_v1.sh -> scripts/trigger_verifier_run_v1.py -> external verifier (verifier_base_url)
- Self-heal tick: scripts/brain_loop_self_heal_v1.sh / scripts/brain_loop_self_heal_v1.py (may re-trigger verifier)
- Background/monitor scripts: scripts/brain_loop_health_check_v1.py, scripts/validate_brain_loop_health_v1.py

Per-automation classification (schedule | trigger | last_run | model/provider status | token-burn risk | policy decision & recommended action)

1) .github/workflows/agentic-ci.yml
- Schedule / Trigger: hourly (cron: '0 * * * *'), push, pull_request
- Last run: unknown (CI logs accessible via GitHub API)
- Model/Provider: none in workflow steps (runs tests, cost enforcer, autonomy scorer locally) — does not call external LLMs
- Token-burn risk: LOW
- Policy decision: ALLOW (keep). Enforcement: cost_policy_enforcer step already present. Ensure runners do NOT have premium provider secrets.
- Action: keep enabled; ensure cost_policy_enforcer runs before any steps that could use secrets.

2) .github/workflows/brain-loop-autorun-v1.yml
- Schedule / Trigger: cron every 6 hours + workflow_dispatch (manual)
- Last run: unknown (artifact receipts exist under receipts/brain-loop-autorun-*.json)
- Model/Provider: depends on what downstream steps do. In CI it runs observe-only brain_loop_autorun_v1.sh (CI env has no SourceA/CF tokens). When executed on a host/runner with tokens, it can: (a) call trigger_verifier_run_v1.py -> posts to verifier_base_url (external workers.dev) and (b) invoke scripts/promote_brain_worker_v1.sh which calls wrangler to deploy Cloudflare Workers (receipts show deployed Worker uses Workers AI open-source).
- Token-burn risk: CONDITIONAL — LOW when observe-only in CI; HIGH when run with tokens and promotion path executes (can trigger external verifier or worker deploys that may cause model invocations).
- Policy decision: SCHEDULED JOB with conditional unknown external verifier = BLOCK until cost_policy_pass receipt exists. For scheduled runs in org/GitHub, set to REPORT-ONLY (do not enable deploy path) unless explicit receipt present.
- Action: Convert repo-level scheduled workflow to observe-only by default (CI already observe-only). Add gating: require receipts/cost_policy_pass.json (CI/host) and require founder approval for any job that switches to autonomous-deploy mode. If external verifier is called, treat verifier as UNKNOWN_PROVIDER => BLOCK unless org attest proves allowed model.

3) Local Launchd autorun (scripts/install_brain_loop_launchd_v1.sh + plist)
- Schedule / Trigger: local launchd (6h or 24x7 as configured in docs)
- Last run: depends on local machine; receipts under receipts/ indicate runs occurred locally
- Model/Provider: same downstream risks as brain-loop-autorun (external verifier, Cloudflare Worker deploys). Deployed Worker evidence shows Workers AI open-source; verifier_base_url is external worker (unknown provider/model)
- Token-burn risk: HIGH (local machines with tokens execute full deploys and can trigger external model calls)
- Policy decision: BLOCK on unknown verifier; require cost_policy_pass receipt and strict runner token policy. Local launchd autorun should be disabled on developer machines by default; permit only on a monitored dedicated runner with tokens removed from personal devices.
- Action: Disable launchd autorun on developer machines (documented). If a monitored runner is authorized, require cost_policy_pass receipt and founder approval to enable.

4) scripts/promote_brain_worker_v1.sh (manual / confirm-each-time / --autonomous-deploy)
- Schedule / Trigger: manual by default; can be called by autorun with --autonomous-deploy
- Last run: unknown (inspect receipts/deploy receipts)
- Model/Provider: runs wrangler deploy which uploads code to Cloudflare; receipts show Cloudflare Workers AI (Open-source) in deployed runtime. However promotion also verifies candidate via external verifier endpoint (unknown model/provider).
- Token-burn risk: HIGH (deploys and possible subsequent runtime invokes; can trigger expensive API if verifier uses premium model)
- Policy decision: FAIL if executed without cost_policy_pass receipt; FAIL if any fallbacks to premium are possible; REQUIRE founder approval for enabling autonomous deploys.
- Action: Require cost_policy_pass receipt and explicit environment flag (ALLOW_REMOTE_DEPLOY=true) plus restrict runner tokens. For --autonomous-deploy, require founder-signed receipt artifact in receipts/.

5) scripts/run_parallel_brain_candidates_v1.sh -> trigger_verifier_run_v1.py
- Schedule / Trigger: manual or invoked by autorun (parallel step) or self-heal; used to post /run to verifier_base_url
- Last run: evidenced by parallel-candidate-batch receipts under receipts/
- Model/Provider: EXTERNAL verifier endpoint (data/brain_domain_sandboxes_v1.json: verifier_base_url = https://sina-governance-ssot-advisory.kazemnezhadsina144.workers.dev). The verifier is an external service; model/provider used by that service is UNKNOWN from repo context.
- Token-burn risk: HIGH (external verification may call LLMs or other expensive services). Because provider/model is UNKNOWN, policy = BLOCK by default.
- Policy decision: BLOCK. Any scheduled or automated run that posts to verifier_base_url must be DISABLED or set to REPORT-ONLY until the verifier's provider and cost receipt are documented.
- Action: Disable automated runs that call trigger_verifier_run_v1.py in scheduled contexts. Require org-admin attestation of verifier provider and a cost_policy_pass receipt before re-enabling.

6) scripts/brain_loop_self_heal_v1.sh / brain_loop_self_heal_v1.py
- Schedule / Trigger: invoked by autorun (6h) or can be run manually; may re-trigger re-verification or re-run candidate runs
- Last run: receipts exist (brain-self-heal-tick-*.json)
- Model/Provider: may call trigger_verifier_run_v1.py (external verifier) depending on conditions; model/provider therefore CONDITIONAL/UNKNOWN
- Token-burn risk: MEDIUM-HIGH when triggers re-verification; LOW when running purely local checks
- Policy decision: DISABLE re-verification calls by default in scheduled runs until verifier is attested. If run manually by trusted operator with attestation, permit.
- Action: Add a flag --dry-run or --no-verify to scheduled self-heal runs. Require cost_policy_pass to permit re-verification.

7) scripts/brain_loop_health_check_v1.py and validate_brain_loop_health_v1.py
- Schedule / Trigger: run as CI steps and pre-flight checks in autorun
- Last run: unknown
- Model/Provider: none (checks receipts and local metadata)
- Token-burn risk: LOW
- Policy decision: ALLOW
- Action: Keep as-is; run in CI and monitored hosts.

8) Deployed Cloudflare Worker: cloud/workers/sourcea-brain-chat-v1
- Schedule / Trigger: invoked by user traffic or by autorun when sync occurs
- Last run: runtime logs only (Cloudflare account)
- Model/Provider: Receipts in receipts/ indicate 'Cloudflare Workers AI' and label 'Open-source Workers AI model' — allowed per policy
- Token-burn risk: MEDIUM (runtime invocation volume matters)
- Policy decision: ALLOW with monitoring and usage receipts; cap background invocations
- Action: Add usage receipts and periodic cost/usage reports; require cost caps for background jobs.

9) IDE/Copilot/Cursor local automations and org-level workflows
- Scope: out-of-repo; not discoverable without admin/dev inputs
- Policy decision: BLOCK until enumerated. Unknown provider/model => BLOCK; scheduled unknowns must be disabled or set to report-only.
- Action: Request org-admin and developer lists; fail-closed on unknowns.

Evidence and receipts
- receipts/ show when autorun/self-heal/parallel batches ran. Use receipts as canonical proof for allowed runs. Any scheduled run that would call unknown external verifier must be disabled until external provider attestation and cost receipts are provided.

Immediate repo-local enforcement actions (done or recommended)
- cost_policy_enforcer in CI: keep enabled (already present) and fail-closed on banned patterns in code/workflows.
- Add gating: gates/promotion_gate.py and scripts/promote_brain_worker_v1.sh must require receipts/cost_policy_pass.json before any deploy execution that could invoke external verifier or perform wrangler deploys.
- Convert scheduled autorun to observe-only by default in shared runners; only enable full-run on dedicated monitored runner with tokens and cost receipts.

Blockers for complete cross-surface audit
- GitHub org API token to list org-level workflows, enabled state, last_run timestamps
- Cloudflare read-only API token to list workers, cron triggers, runtime usage logs
- Access to verifier service implementation to determine its model/provider and cost profile
- Developer-provided Copilot/Cursor automation registry

If desired next step: apply repository-local mitigations now (add gating checks in promotion_gate.py and modify promote_brain_worker_v1.sh to require cost receipt file) or request org creds to finish inventory and get last_run timestamps.
