---
name: commissioning-specialist
description: Run the NF commissioning specialist closed loop and advance one real job from data/nf_commissioning_job_queue_v1.json per tick. Use when activating commissioning, healing SG/core liveness, dispatching qualification jobs, or ranking kaizen proposals. Never mint App keys, lift hold, redesign architecture unsupervised, or claim fully_commissioned while runtime_reality says not_commissioned.
---
# Commissioning Specialist

## Trigger
Cloudflare cron `*/5` → worker `nf-commissioning-specialist-tick-v1`.

## Closed loop (machine law)
Observe → Detect → Critique → repair(allowlist) → ProposeImprove → ReObserve

Each tick must select the next incomplete job from `data/nf_commissioning_job_queue_v1.json` and produce real evidence for that job (score, dispatch, or blocked_founder with exact missing decision).

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

## Manual tick
`POST https://nf-commissioning-specialist-tick-v1.<subdomain>.workers.dev/tick`

## Receipts
KV `last_fired_at` + `last_receipt` + `last_job_id` + job progress; repo receipts under `receipts/doctrine/NF_COMMISSIONING_SPECIALIST_*`.
