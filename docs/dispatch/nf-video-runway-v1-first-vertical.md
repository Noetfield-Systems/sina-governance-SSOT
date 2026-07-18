# Commission — Video Runway v1 (first sellable vertical)

**commission_id:** `NF-VIDEO-RUNWAY-V1-FIRST-VERTICAL`  
**Status:** `IMPLEMENTATION_AUTHORIZED`  
**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1`  
**Product:** Noetfield Runway · first vertical = Video Runway  
**Target:** builders / Result UI + Motor Job path (not noetfeld-OS redesign)

## Objective

Three completed Jobs that deliver a **downloadable final video** in the Result UI.

Path:

```text
Live UI → brief → Prompt Compiler → research → script → video provider → Result UI
```

## Build order

1. Result UI shell: Job create → status → downloadable artifact  
2. Prompt Compiler (brief → recipe-bound stages)  
3. Wire video provider via existing `MediaGenerationAdapter` / Higgsfield CLI (replaceable)  
4. Cheap-model intelligence stage (research/script) behind Motor model router  
5. Credits metering per completed Job  
6. Prove 3 end-to-end Jobs with downloadable MP4/package

## Forbidden

- Selling Motor or governance as the SKU  
- App Runway / multi-brand Campaign as first slice  
- Declaring done on receipts without downloadable Result UI video  
- Counting generation volume as success  

## Relation

- Circuit A/B = Motor infra proofs (keep)  
- This commission = **commercial product vertical**  

## Final status

`VIDEO_RUNWAY_PROVEN` when 3 Jobs have downloadable final videos in Result UI with credit receipts.
