# NF-NOETFIELD-RUNWAY-PRODUCT-V1 — SG FINALIZATION PACKET

**decision_id:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1`  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` (Software Repair first; shared Unified Motor foundation)  
**Authority:** Architecture Finalization Gate (product surface lock — does **not** reopen Unified Motor architecture)  
**Tier:** P10-PRODUCT-LAYERS  
**Version:** v1.1.0_locked_20260718  
**Machine:** `data/nf_noetfield_runway_product_v1_LOCKED.json`  
**Product baseline (docs):** `Noetfield-Systems/PRODUCT_CATEGORY@b9ce619cb575f74800bb56776f3d9acb5e7ebac9`  
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-HIGGSFIELD-MEDIA-ADAPTER-AND-RESULT-MOTOR-V1` · `NF-ACTIVATION-CYCLE-V1` · `NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1`  
**proposed_by:** Founder + NOOS + PRODUCT_CATEGORY baseline + advisor upgrade  
**sg_decision:** `SG_ACCEPTED` — sell finished results; one Unified Motor; build order Software Repair → Research → Video

---

## Distinction (binding)

```text
Docs committed (PRODUCT_CATEGORY b9ce619)
≠ Architecture canonicalized (this SG packet on main)
≠ Runtime operational (Motor foundation + real Jobs)
```

## One line

Noetfield builds **Runways** that start agents, models, and tools for a real job and deliver the **final result in the UI**.

## Product definition

| Field | Value |
|-------|-------|
| product | Noetfield Runway |
| buyer | Founder / creator / small team who wants a finished result, not a model chat |
| input | Goal + required assets (brief, repo, question, product, issue) |
| result | A finished deliverable in the UI (PR, report, video, campaign pack, app) |
| flow | `User input → Prompt Compiler → Plan → Model/Tool selection → Execution loop → Verification → Final result` |
| time_to_result | Minutes to a few hours depending on runway |
| providers | Models + real tools (research, video, code, deploy, search, edit) |
| human_intervention | Only at review / revise / approve checkpoints |
| pricing | Credits per completed Job, not per chat token |

## Stack roles (binding)

| Piece | Job |
|-------|-----|
| **Runway** | User-facing result path (**the product**) |
| **Unified Motor** | Shared engine for all Runways (**infrastructure**) |
| **Recipe** | Technical stage list for one Runway |
| **SourceA** | Prompt / Job Compiler |
| **NOOS** | Runtime control plane: issues · queues · stalled jobs · retries · health |
| **SG** | Canon and final authority |
| **SinaGPT** | Founder cockpit to command and watch results |
| **Railway** | Long-running services and workers (Motor runtime, Prompt Compiler) |
| **Cloudflare** | UI · Gateway · Workflows · Queues · storage edge |
| **Cheap models** | Normal operational intelligence (default) |
| **Claude / Cursor / Codex** | Bootstrap builders + escalation / system-building workers only |

## Gateway ≠ Motor (binding)

```text
Gateway = entry / control surface
Unified Motor = actual execution runtime
```

Gateway today may dispatch checks and track simple records. That is **not** a complete Runway Job (`input → intelligence → execution → artifact`).

**`GATEWAY_MODE=live` HOLD** until five preflight checks PASS (authenticated `/v1/health`, required secrets, one read action, one idempotent dry-run write, clean worker logs). Do not merge live-mode config PRs without that preflight.

## Engine law

Repair lane **bootstraps** the foundation, but the core must stay:

- artifact-neutral  
- provider-neutral  
- **not** a Software-Repair-only engine  

Core (shared):

```text
Runway Definition · Job Intake · Prompt Compiler · Model Router · Tool/Provider Router
Execution State Machine · Retry/Repair Loop · Artifact Store · Result Delivery
Cost/Runtime Tracking · NOOS Events · Railway-inclusive stack manifest · runway doctor
```

Runway-specific pieces are **adapters/plugins** only (GitHub/worktree/PR; search/citations/report; video provider/media/delivery).

## Three initial Runways (build order)

| Order | Runway | Real result | Bootstrap builder (temporary) |
|------:|--------|-------------|-------------------------------|
| 1 | **Software Repair** | Issue/CI failure → green PR | Claude |
| 2 | **Research** | Question → cited decision-ready report | GPT |
| 3 | **Video** | Brief/assets → finished playable video | Cursor |

```text
Claude / GPT / Cursor = Bootstrap Builders (not permanent runtime owners)
Unified Motor = Permanent runtime
Cheap / cloud-hosted models = normal job intelligence
Premium / Claude / Codex / Cursor = escalation or system build only
```

### Result contracts (Done)

| Runway | Done means |
|--------|------------|
| Shared Motor foundation | UI/API Job → Motor → plan → router → execute → retry/repair → artifact → Result UI → cost/runtime → NOOS visibility |
| Software Repair | Real failing issue/test → sandbox patch → original failure fixed → relevant tests pass → real PR URL (no auto-merge) |
| Research | Real question → live research → cited report → downloadable result → citations resolve |
| Video | Real brief/assets → script/storyboard → provider generation → playable video → preview + download |

## Model providers (start)

```text
Build ModelRouter interfaces now
Enable only one live cheap provider first (DeepSeek OR Kimi)
Keep Hugging Face and others as disabled adapters until a concrete endpoint is chosen
Do not wait for API keys to build foundation (mock + deterministic adapters)
Never put keys in chat or repository — runtime secret store only
```

## Waves (authorized)

0. **SG lock** — this packet (Software-Repair-first) lands on SG `main`  
1. **Shared Motor foundation** — interfaces, state machine, stack manifest, `runway doctor`, mock flow; **no deploy**  
2. **Software Repair real job** — failing fixture → green candidate PR  
3. **Research plugin** — no new engine  
4. **Video plugin** — no new engine; providers (Higgsfield / others) are adapters only  

## Forbidden this cycle

- Fourth Runway / new lane / GPU platform  
- Three live model providers at once  
- New governance framework  
- Raw GitHub dispatch as the product experience  
- Separate engine per agent/builder  
- `GATEWAY_MODE=live` without the five-check preflight  
- API keys in chat or git  
- Selling Motor or governance as the SKU  
- Designing Motor core as Git/PR-specific  

## Relation to prior locks (no reopen)

| Prior | Relationship |
|-------|----------------|
| Unified Motor architecture | Remains the shared engine — still must be **built** as runtime |
| PRODUCT_CATEGORY `b9ce619` | Product baseline docs; this packet is the SG canonicalization |
| Higgsfield adapter | Video-provider adapter later — not the product, not Wave 1 |
| Circuit A/B | Infra proofs — keep; not the commercial Done criteria |
| Activation cycle WIP=2 | Infra proofs remain; commercial build order is Repair → Research → Video |

## First commercial / foundation success

> First success is when Sina submits a Job from UI or SinaGPT and receives a **real green PR** without hand-dispatching GitHub Actions.

## SG answers

1. **P0 preserved?** Yes.  
2. **Conflict?** No — product + build-order upgrade; Motor architecture not redesigned.  
3. **Supersedes?** Video-first order in v1.0.0 of this packet / prior PR #22 title.  
4. **Authority?** SG for canon; builders implement foundation; founder for merge/publish/pricing.  
5. **Machine-safe?** Mock-first foundation; one cheap live provider later; secrets in runtime store.  
6. **Founder-only?** Live Gateway flip; irreversible merge/publish; pricing.  
7. **Evidence → P99?** Foundation vertical slice + Software Repair green PR proof.  
8. **Rollback?** Disable Runway UI; keep Motor adapters; revert live Gateway.  

## non_goals

- Reopening Unified Motor architecture  
- Replacing Operating Brain Install (SourceA B2B)  
- Building Research/Video-specific logic into Motor core  
- Declaring runtime Done because docs/CI are green  
