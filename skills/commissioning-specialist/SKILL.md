---
name: commissioning-specialist
description: Run one explicit NF commissioning job from data/nf_commissioning_job_queue_v1.json. Use when activating commissioning, re-proving an invalidated capability, healing SG/core liveness, dispatching qualification jobs, or ranking kaizen proposals. Never repeat completed unchanged jobs, mint App keys, lift hold, redesign architecture unsupervised, or claim fully_commissioned while runtime_reality says not_commissioned.
---
# Commissioning Specialist

## Trigger
On demand only: dispatch `NOETFIELD-RUNWAY/.github/workflows/commissioning-run.yml`
with an explicit job ID. The former Cloudflare `*/5` cron is disabled.

## Closed loop (machine law)
Observe → Detect → Critique → repair(allowlist) → ProposeImprove → ReObserve

Each run must name an incomplete or invalidated job from
`data/nf_commissioning_job_queue_v1.json` and produce real evidence for it
(score, dispatch, or blocked_founder with exact missing decision). Completed,
unchanged jobs are not repeated.

## Job queue
- Cursor + progress in KV (`job_queue_cursor`, `job_queue_progress`)
- Execute-class jobs dispatch allowlisted runway verify / repair / gallery foundation workflows
- Qualify-class jobs score proof-a/b, custody, gateway, roles, rollup
- Always repository_dispatch `commissioning_tick` with `job_id` to the commissioning runway product path

## Models (failover)
DeepSeek → GLM → Kimi (Moonshot) → huggingface. If all fail, continue T0 deterministic.

## Allowed repairs
IDs listed in `data/nf_commissioning_specialist_map_v1.json` under `repair_allowlist`.

## Forbidden
- Mint new GitHub App private keys (read `data/sg_authority_key_pointer_v1.json` first)
- Lift autonomous production mutations hold
- Enable enforcement
- Unsupervised architecture redesign (propose only; founder ratifies)
- Fake `fully_commissioned`

## Manual run
Use GitHub `workflow_dispatch` for `commissioning-run.yml`. The Worker's old
public `POST /tick` endpoint returns `410 perpetual_tick_disabled`.

## Receipts
KV `last_fired_at` + `last_receipt` + `last_job_id` + job progress; repo receipts under `receipts/doctrine/NF_COMMISSIONING_SPECIALIST_*`.
