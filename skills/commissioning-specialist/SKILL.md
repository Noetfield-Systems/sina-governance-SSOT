---
name: commissioning-specialist
description: Run the NF commissioning specialist closed loop (observe/detect/critique/repair/propose). Use when activating commissioning, healing SG/Motor liveness, or ranking kaizen proposals. Machine-enforceable map at data/nf_commissioning_specialist_map_v1.json. Never mint App keys, lift HOLD, or redesign architecture unsupervised.
---
# Commissioning Specialist

## Trigger
Cloudflare cron `*/5` → worker `nf-commissioning-specialist-tick-v1`.

## Closed loop (machine law)
`Observe → Detect → Critique → Repair(allowlist) → ProposeImprove → ReObserve`

## Models (failover)
DeepSeek → GLM → Kimi (Moonshot) → Hugging Face. If all fail, continue T0 deterministic.

## Allowed repairs
Only IDs in `data/nf_commissioning_specialist_map_v1.json` → `repair_allowlist`.

## Forbidden
- Mint new GitHub App private keys (read `data/sg_authority_key_pointer_v1.json` first)
- Lift `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`
- Enable enforcement
- Unsupervised architecture redesign (propose only; founder ratifies)

## Manual tick
`POST https://nf-commissioning-specialist-tick-v1.<subdomain>.workers.dev/tick`

## Receipts
KV `last_fired_at` + `last_receipt`; repo receipts under `receipts/doctrine/NF_COMMISSIONING_SPECIALIST_*`.
