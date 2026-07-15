BLOCKED: External attestation required for full active-runtime audit

This audit step is blocked pending org/cloud/dev access required to attest external automation surfaces. Items requiring attestation:

- GitHub org-level workflows: enabled state, schedule, last_run timestamps, secrets accessed.
- External verifier service (verifier_base_url): provider and model used, cost profile, and cost_policy_pass receipt.
- Cloudflare account: list of Workers, cron triggers, invocation logs, and usage/cost metrics.
- Vercel / Railway / Render / Supabase scheduled functions & background workers: enabled state and usage logs.
- Developer Copilot/Cursor/IDE automation registry exports: list of registered automations, triggers, last_run time, and whether they call LLMs.

Reason: Without these attestations, external services are classified as UNKNOWN_MODEL and therefore BLOCK per the enacted policy.

Next steps for org admin / devs:
1. Provide read-only GitHub org token or run the org-workflows inventory script and attach the result here.
2. Provide Cloudflare read-only API token to enumerate Workers and cron triggers.
3. Provide verifier owner attestation: a JSON receipt confirming the verifier provider and model used, signed or produced by the verifier owner.
4. Provide exports of developer Copilot/Cursor automation registry or a signed statement from each active runner.

Place attestation artifacts in audits/attestations/ and re-run the active-runtime audit to lift BLOCKED status.
