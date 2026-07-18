# NF-NOETFIELD-RUNWAY-PRODUCT-V1 — SG FINALIZATION PACKET

**decision_id:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1`  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` (Video Runway first vertical only)  
**Authority:** Architecture Finalization Gate (product surface lock — does **not** reopen Unified Motor architecture)  
**Tier:** P10-PRODUCT-LAYERS  
**Version:** v1.0.0_locked_20260718  
**Machine:** `data/nf_noetfield_runway_product_v1_LOCKED.json`  
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-HIGGSFIELD-MEDIA-ADAPTER-AND-RESULT-MOTOR-V1` · `NF-ACTIVATION-CYCLE-V1`  
**proposed_by:** Founder + NOOS product lock  
**sg_decision:** `SG_ACCEPTED` — sell finished results; Motor and governance are infrastructure, not the SKU

---

## One line

Noetfield builds **Runways** that start agents, models, and tools for a real job and deliver the **final result in the UI**.

## Product definition

| Field | Value |
|-------|-------|
| product | Noetfield Runway |
| buyer | Founder / creator / small team who wants a finished result, not a model chat |
| input | Goal + required assets (brief, repo, question, product, issue) |
| result | A finished deliverable in the UI (video, app, report, campaign pack, PR) |
| time_to_result | Minutes to a few hours depending on runway |
| providers | Models + real tools (research, video, code, deploy, search, edit) |
| human_intervention | Only at review / revise / approve checkpoints |
| pricing | Credits per completed Job, not per chat token |

## Stack roles (binding)

| Piece | Job |
|-------|-----|
| **Runway** | What the user picks and gets a result from (**the product**) |
| **Motor** | Shared engine: Prompt Compiler → routers → execution loop (**infrastructure**) |
| **Recipe** | Technical stage list for one Runway |
| **NOOS** | Queue, health, retry, continue |
| **SG** | Authority bounds / laws |
| **SinaGPT** | Cockpit to command and watch results |

## First vertical decision

**First vertical = Video Runway.**

| Runway | Real output | Verdict |
|--------|-------------|---------|
| Video Runway | Final video package | **BEST FIRST** |
| Research Runway | Decision report | Later / fast technical proof |
| App Runway | Working preview app | Too heavy as first slice |
| Campaign Runway | Ads + landing pack | Second vertical after Video |
| Software Repair | Fixed PR | Strong internal; weaker consumer ads |
| Proposal Runway | Ready proposal | Later |

### Video Runway path

```text
Live UI → brief → Prompt Compiler → research → script → video provider → Result UI
```

Flow: `INPUT → INTELLIGENCE → EXECUTION → RESULT`

### Success (product, not infra)

```text
3 completed Jobs with downloadable final video in the Result UI
```

**Not** success: receipts-only demos · selling Motor · selling a shop · generation count without a downloadable package.

## Relation to prior locks (no reopen)

| Prior lock | Relationship |
|------------|----------------|
| Unified Motor | Remains the shared engine under every Runway |
| Higgsfield adapter | A replaceable video provider behind Video Runway — not a lane, not the product |
| Circuit A | Infra proof (deterministic T0) — keeps Motor trustworthy |
| Circuit B | Media/result Motor pilot — feeds Video Runway providers; **does not redefine the SKU** |
| Activation cycle WIP=2 | Remains binding for infra proofs; Video Runway product build is the commercial vertical |

## Forbidden this cycle

- Selling governance / SG / “operating system” as the consumer SKU
- Selling Motor as the product
- First vertical = App Runway or multi-brand Campaign Runway
- Chat-token pricing as the primary commercial model
- Declaring Video Runway done without 3 downloadable Result-UI Jobs

## SG answers

1. **P0 preserved?** Yes — Author≠Subject; providers ≠ memory; founder DECIDE at review checkpoints.  
2. **Conflict?** No — product surface over existing Motor; does not redefine Gateway or Resident Roles.  
3. **Superseded?** None. Clarifies commercial surface relative to Circuit B (infra pilot ≠ product SKU).  
4. **Authority?** SG for product lock; builders implement Video Runway UI + Job path; founder for public publish/pricing.  
5. **Machine-safe?** Jobs under recipes; credits per completed Job; providers behind adapters.  
6. **Founder-only?** Pricing numbers; public launch; irreversible publish.  
7. **Evidence → P99?** Three completed Video Jobs with downloadable artifact refs.  
8. **Rollback?** Disable Video Runway UI; Motor/adapters remain.  

## non_goals

- Reopening Unified Motor architecture  
- Replacing Operating Brain Install (SourceA B2B) — separate SKU family  
- Building App/Campaign Runways before Video success criteria  
