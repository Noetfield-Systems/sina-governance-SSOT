# Commission — Video Runway v1 (parallel initial Runway)

**commission_id:** `NF-VIDEO-RUNWAY-V1`
**Status:** `IMPLEMENTATION_AUTHORIZED` · Cursor bootstrap may continue in parallel with other Runways
**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1` v1.3
**Product baseline:** `PRODUCT_CATEGORY@b9ce619`
**Bootstrap builder:** Cursor
**Concurrency:** one Job ↔ one isolated sandbox; may run beside Repair/Research Jobs

## Objective

```text
Live UI → brief/assets → Prompt Compiler → script/storyboard
→ VideoProviderAdapter → media verification → playable/downloadable Result UI
```

## Shared-foundation requirement

Video may use shared Motor interfaces. Core must stay provider-neutral and concurrency-capable. Do not claim exclusive Motor ownership.

## Acceptance proof

Real brief/assets → generation → verified media → Result UI preview/download → cost/runtime → NOOS state. Concurrent Jobs must not share this Job's sandbox.

## Final status

`VIDEO_RUNWAY_VERTICAL_SLICE_BUILT` or `VIDEO_RUNWAY_BLOCKED_WITH_EXACT_CAUSE`
