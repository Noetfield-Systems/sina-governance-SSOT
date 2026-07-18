# Commission — Video Runway v1 (active first vertical)

**commission_id:** `NF-VIDEO-RUNWAY-V1-FIRST-VERTICAL`
**Status:** `IMPLEMENTATION_AUTHORIZED` · active Cursor build; continue, do not restart
**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1` v1.2
**Product baseline:** `PRODUCT_CATEGORY@b9ce619`
**Bootstrap builder:** Cursor
**Target:** Video Runway Result UI + provider-neutral shared Motor interfaces

## Objective

Continue the current video-generation build and close one complete product path:

```text
Live UI → brief/assets → Prompt Compiler → script/storyboard
→ VideoProviderAdapter → media verification → playable/downloadable Result UI
```

## Shared-foundation requirement

Video may bootstrap the interfaces needed now, but Motor core must stay artifact/provider-neutral:

`RunwayDefinition` · `MotorJob` · `PromptCompiler` · `ModelRouter` · `ProviderAdapter` · execution state machine · artifact/result interfaces · NOOS events · stack manifest · `runway doctor`.

Do not wait for new model API keys. Existing Higgsfield access stays behind `VideoProviderAdapter`.

## Acceptance proof

Real brief/assets → real provider generation → verified media → playable preview + download in Result UI → cost/runtime recorded → NOOS sees state.

## Forbidden

- Restarting or redirecting Cursor's active Video work
- Video/Higgsfield assumptions in Unified Motor core
- `GATEWAY_MODE=live` without five-check preflight
- Declaring done from generation receipt without Result UI delivery
- Deploying from this commission without separate authority

## Final status

`VIDEO_RUNWAY_VERTICAL_SLICE_BUILT` or `VIDEO_RUNWAY_BLOCKED_WITH_EXACT_CAUSE`
