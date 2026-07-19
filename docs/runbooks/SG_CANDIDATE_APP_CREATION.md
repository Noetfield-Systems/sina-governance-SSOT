# SG Candidate App — Creation & Identity Proof Runbook

Founder-authorized scope: **candidate GitHub App creation, selected-repository
installation, and identity proof only.**

Not authorized here: SG commissioning, production ruleset enforcement, Motor
production permits, HOLD removal, secret rotation outside candidate custody,
legacy App revocation.

## Candidate App (exact)

- Name / slug: `noetfield-sg-authority`
- Owner org: `Noetfield-Systems`
- Visibility: **private** (public: false)
- Webhook: **disabled** (`hook_attributes.active: false`, no events)
- Permissions (exact): metadata:read, contents:read, pull_requests:read,
  actions:read, checks:write, statuses:write

Manifest source of truth: `data/sg_candidate_app_manifest_v1.json`

## Install ONLY on these 2 repos

1. `Noetfield-Systems/sina-governance-SSOT`
2. `Noetfield-Systems/noetfield-sandbox-private`

Do NOT install on SANDBOX, NOETFIELD-RUNWAY, or "All repositories".
Use "Only select repositories" and pick exactly the two above.

## Step 1 — Create App (single interactive confirm)

```bash
python3 scripts/sg_candidate_app_bootstrap_v1.py
```

This serves `http://127.0.0.1:8737/` and opens it. Confirm **Create GitHub App**
on GitHub. On the callback the script:
- converts the one-time code to App credentials,
- writes the private key + webhook/client secrets ONLY to `~/.sina/secrets/`
  (mode 0600) — never to the repo,
- writes a public-metadata-only receipt to `receipts/sg-candidate-app/`.

## Step 2 — Install on exactly the 2 repos

Follow the install link shown by the callback page.

## Step 3 — Prove identity (automated)

```bash
python3 scripts/prove_sg_candidate_identity_v1.py
```

Verifies slug, org owner, exact permissions, empty events, selected-repo
installation, and exactly the 2 authorized repos. On full PASS it writes an
identity proof receipt and flips `data/sg_candidate_app_state_v1.json` to
`SG_CANDIDATE_IDENTITY=PROVEN`. HOLD / enforcement / runtime are never changed.

## Custody

- Private key: `~/.sina/secrets/noetfield-sg-authority.private-key.pem` (0600)
- Only the SHA256 fingerprint is recorded in repo receipts.
