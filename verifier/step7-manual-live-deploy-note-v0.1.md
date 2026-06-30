# Step 7 Manual Live Deploy Note v0.1

Status: DONE / FOUNDER-APPROVED MANUAL DEPLOY

## Scope

Step 7 is recorded as complete by a founder-approved manual deploy, not by an
autonomous gate-triggered deploy.

## Gate Evidence

- Gate dry-run / approval receipt:
  `f73c0ce8-e3d2-4c5f-be37-fad8ffdd1684`
- Earlier candidate verifier PASS receipt:
  `9dca5cd9-4cca-42c2-8970-c64c8ffa866f`

## Live Brain Baseline

- Live target repo: `github.com/kazemnezhadsina144-dot/SourceA`
- Live target worker path: `cloud/workers/sourcea-brain-chat-v1`
- Live deploy command: `bash scripts/brain_cli_v1.sh deploy`
- Deploy run location: `~/Desktop/SourceA`
- Live Worker: `sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev`
- Deployed version ID: `628ebc37-5c66-44e5-9cad-4e05fc2f3e92`
- Post-deploy baseline: 514 chunks live, citations OK,
  `validate-sourcea-brain-knowledge-v1.sh` ALL PASS.

## Account Boundary

The live Brain remains on the MAIN Cloudflare account `0d0b967b...`.
The verifier remains on the secondary Cloudflare account
`b7282b4a5c17b84d62e3ef8866b878f8`.

These accounts must not be merged. Autonomous gate-triggered deploy is Step 10,
founder-gated, and not yet authorized.

## Next Proposed Step

Step 8: gate refusal teeth. Feed a non-PASS receipt and prove the gate blocks
deploy. Step 8 does not require the live SourceA repo.
