---
name: commissioning-specialist
description: Run one explicit NF commissioning job from data/nf_commissioning_job_queue_v1.json. Use when activating commissioning, re-proving an invalidated capability, healing SG/core liveness, dispatching qualification jobs, or ranking kaizen proposals. Never repeat completed unchanged jobs, mint App keys, lift hold, redesign architecture unsupervised, or claim fully_commissioned while runtime_reality says not_commissioned.
---
# Commissioning Specialist

## Trigger
On demand only: send an authenticated `POST /jobs` request to the commissioning
Worker with an explicit job ID and idempotency request ID. The Worker creates a
durable Cloudflare Workflow instance. The former Cloudflare `*/5` cron is
disabled.

## Closed loop (machine law)
Observe → Detect → Critique → repair(allowlist) → ProposeImprove → ReObserve

Each run must name an incomplete or invalidated job from
`data/nf_commissioning_job_queue_v1.json` and produce real evidence for it
(score, dispatch, or blocked_founder with exact missing decision). Completed,
unchanged jobs are not repeated.

## Job queue
- Explicit job progress and request identity in KV (`job_queue_progress`, `request:<instance_id>`)
- Cloudflare Workflows own durable job execution and status
- Execute-class jobs dispatch exactly one allowlisted runway verify / repair / gallery foundation workflow
- Qualify-class jobs score proof-a/b, custody, gateway, roles, rollup
- GitHub Actions execute jobs; they do not own queue selection or scheduling

## Models (failover)
DeepSeek V4 Flash → DeepSeek V4 Pro → GLM → Kimi (Moonshot) → Hugging Face.
LLM calls occur only for observed defects, failed jobs, or founder-blocked jobs;
passing T0 work stays deterministic. If all models fail, continue T0.

## Allowed repairs
IDs listed in `data/nf_commissioning_specialist_map_v1.json` under `repair_allowlist`.

## Forbidden
- Mint new GitHub App private keys (read `data/sg_authority_key_pointer_v1.json` first)
- Lift autonomous production mutations hold
- Enable enforcement
- Unsupervised architecture redesign (propose only; founder ratifies)
- Fake `fully_commissioned`

## Manual run
Use the Worker's authenticated `POST /jobs` endpoint. Query
`GET /jobs/<instance_id>` with the same Bearer credential for status. GitHub's
`commissioning-run.yml` remains manual break-glass only. The old public
`POST /tick` endpoint returns `410 perpetual_tick_disabled`.

## Receipts
KV `last_fired_at` + `last_receipt` + `last_job_id` + job progress; repo receipts under `receipts/doctrine/NF_COMMISSIONING_SPECIALIST_*`.
