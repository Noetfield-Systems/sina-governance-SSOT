# Commission — Software Repair Runway + Unified Motor foundation

**commission_id:** `NF-SOFTWARE-REPAIR-RUNWAY-V1-FOUNDATION`  
**Status:** `IMPLEMENTATION_AUTHORIZED`  
**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1` (v1.1)  
**Product baseline:** `PRODUCT_CATEGORY@b9ce619`  
**Build agent (bootstrap):** Claude  
**Target:** builders / sandbox — **not** a Git-specific Motor core

## Objective

Build **Unified Motor foundation** in the Software Repair lane (provider-neutral), then prove one real Software Repair Job.

## Wave 1 — foundation (no API keys required)

```text
RunwayDefinition · MotorJob · PromptCompiler interface · ModelRouter interface
ProviderAdapter interface · Execution state machine · Artifact interface · Result interface
NOOS event interface · Railway-inclusive stack manifest · runway doctor
mock/deterministic adapter · minimal submit/status/result flow
```

Do **not** deploy. Do **not** flip `GATEWAY_MODE=live`. Do **not** put Research/Video logic in core.

## Wave 2 — Software Repair acceptance

```text
Real failing fixture
→ Motor job
→ sandbox patch
→ deterministic test
→ green candidate PR
```

Cheap/default worker first; `ESCALATE_REQUIRED` only after failure.

## Final status

`FOUNDATION_VERTICAL_SLICE_BUILT` or `FOUNDATION_BLOCKED_WITH_EXACT_CAUSE`
