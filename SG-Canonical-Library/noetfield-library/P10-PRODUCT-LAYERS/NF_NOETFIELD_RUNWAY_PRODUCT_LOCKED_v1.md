# NF-NOETFIELD-RUNWAY-PRODUCT-V1 — SG FINALIZATION PACKET

**decision_id:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1`
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` (parallel initial Runways)
**Authority:** Architecture Finalization Gate (product surface lock — does **not** reopen Unified Motor architecture)
**Tier:** P10-PRODUCT-LAYERS
**Version:** v1.3.0_locked_20260718
**Machine:** `data/nf_noetfield_runway_product_v1_LOCKED.json`
**Product baseline (docs):** `Noetfield-Systems/PRODUCT_CATEGORY@b9ce619cb575f74800bb56776f3d9acb5e7ebac9`
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-HIGGSFIELD-MEDIA-ADAPTER-AND-RESULT-MOTOR-V1` · `NF-ACTIVATION-CYCLE-V1` · `NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1`
**proposed_by:** Founder + NOOS + PRODUCT_CATEGORY baseline
**founder_override:** Execution is parallel — no serial first/second monopoly; Motor must manage concurrent isolated sandboxes
**sg_decision:** `SG_ACCEPTED` — sell finished results; one Unified Motor; Video / Software Repair / Research run in parallel under isolated sandboxes

---

## Distinction (binding)

```text
Docs committed (PRODUCT_CATEGORY b9ce619)
≠ Architecture canonicalized (this SG packet on main)
≠ Runtime operational (real end-to-end Runway Jobs)
```

## One line

Noetfield builds **Runways** that start agents, models, and tools for a real job and deliver the **final result in the UI**.

## Product definition

| Field | Value |
|-------|-------|
| product | Noetfield Runway |
| buyer | Founder / creator / small team who wants a finished result, not a model chat |
| input | Goal + required assets (brief, repo, question, product, issue) |
| result | A finished deliverable in the UI (video, PR, report, campaign pack, app) |
| flow | `User input → Prompt Compiler → Plan → Model/Tool selection → Execution loop → Verification → Final result` |
| time_to_result | Minutes to a few hours depending on runway |
| providers | Models + real tools (research, video, code, deploy, search, edit) |
| human_intervention | Only at review / revise / consequential-action checkpoints |
| pricing | Credits per completed Job, not per chat token |
| concurrency | Parallel Jobs across Runways and within a Runway, each in an isolated sandbox |

## Stack roles (binding)

| Piece | Job |
|-------|-----|
| **Runway** | User-facing result path (**the product**) |
| **Unified Motor** | Shared engine for all Runways (**infrastructure**) |
| **Recipe** | Technical stage list for one Runway |
| **SourceA** | Prompt / Job Compiler |
| **NOOS** | Runtime control plane: issues · queues · stalled jobs · retries · health · concurrency visibility |
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

**`GATEWAY_MODE=live` HOLD** until five preflight checks PASS: authenticated `/v1/health`; required secrets; one read action; one idempotent dry-run write; clean worker logs.

## Engine law

One Unified Motor. Core stays:

- artifact-neutral
- provider-neutral
- **concurrency-capable**
- not Video-only, not Repair-only, not Research-only
- not hardcoded to Higgsfield / GitHub / any single provider

Core (shared):

```text
Runway Definition · Job Intake · Prompt Compiler · Model Router · Tool/Provider Router
Execution State Machine · Retry/Repair Loop · Artifact Store · Result Delivery
Cost/Runtime Tracking · NOOS Events · Railway-inclusive stack manifest · runway doctor
Parallel Sandbox Manager (isolated sandboxes per Job)
```

Runway-specific pieces are adapters/plugins only: media input/storyboard/provider/validator/delivery; GitHub/worktree/PR; search/citations/report.

## Parallel isolated sandboxes (binding)

Serial "first then second then third" is **not** the operating model.

```text
Job A (Video)     → sandbox_id_A  (isolated)
Job B (Repair)    → sandbox_id_B  (isolated)
Job C (Research)  → sandbox_id_C  (isolated)
Job D (Video #2)  → sandbox_id_D  (isolated)
```

Laws:

1. **One Job ↔ one sandbox** — no shared mutable workspace between concurrent Jobs.
2. **Isolation** — filesystem, credentials scope, network allowlist, and artifact root are Job-scoped.
3. **No cross-Job contamination** — failure/retry/promote of one Job must not rewrite another Job's sandbox.
4. **NOOS visibility** — concurrent Jobs are independently observable (status, stall, retry, cost).
5. **Preserve unrelated work** — dirty trees / other builders / other sandboxes are protected by default (Change-Preservation Law).
6. **Capability to learn** — Motor/NOOS must accumulate receipts proving parallel sandbox management (create, run, destroy, leak detection).

Bootstrap builders may work in parallel too:

| Runway | Real result | Bootstrap builder (temporary) |
|--------|-------------|-------------------------------|
| **Video** | Brief/assets → finished playable + downloadable video | Cursor |
| **Software Repair** | Issue/CI failure → green PR | Claude |
| **Research** | Question → cited decision-ready report | GPT |

```text
Claude / GPT / Cursor = Bootstrap Builders (not permanent runtime owners)
Unified Motor = Permanent runtime
Cheap / cloud-hosted models = normal job intelligence
Premium / Claude / Codex / Cursor = escalation or system build only
```

**Execution preservation:** Do not stop Cursor Video, Claude Repair, or GPT Research to force a serial queue. Coordinate via isolated sandboxes + shared Motor contracts.

### Result contracts (Done)

| Surface | Done means |
|---------|------------|
| Shared Motor + parallel sandboxes | ≥2 concurrent Jobs in separate sandboxes; each reaches Result UI / artifact without cross-contamination; NOOS sees both |
| Video | Real brief/assets → script/storyboard → provider generation → playable video → preview + download |
| Software Repair | Real failing issue/test → sandbox patch → original failure fixed → relevant tests PASS → real PR URL (no auto-merge) |
| Research | Real question → live research → cited report → downloadable result → citations resolve |

## Model providers (start)

```text
Build ModelRouter interfaces now
Enable only one live cheap provider first (DeepSeek OR Kimi) when needed
Keep Hugging Face and others disabled until a concrete endpoint is selected
Do not wait for API keys to build shared foundation (mock + deterministic adapters)
Never put keys in chat or repository — runtime secret store only
```

Existing Higgsfield access may continue behind `VideoProviderAdapter`; provider ≠ product and provider ≠ Motor.

## Waves (authorized — parallel, not serial monopoly)

0. **SG lock** — this parallel-sandbox packet lands on SG `main`
1. **Shared Motor foundation + Parallel Sandbox Manager** — concurrent Job isolation; mock/deterministic OK; no deploy
2. **Three initial Runways in parallel** — Video · Software Repair · Research plugins against the shared engine
3. **Prove concurrency** — at least two simultaneous sandboxed Jobs with independent results and NOOS visibility

## Forbidden this cycle

- Blocking one Runway until another finishes ("must be first")
- Sharing one mutable sandbox across concurrent Jobs
- Fourth Runway / new lane / GPU platform
- Three live model providers at once
- New governance framework
- Raw GitHub dispatch as the product experience
- Separate engine per agent/builder
- `GATEWAY_MODE=live` without the five-check preflight
- API keys in chat or git
- Selling Motor or governance as the SKU
- Designing Motor core as video/Git/provider-specific

## Relation to prior locks (no reopen)

| Prior | Relationship |
|-------|--------------|
| Unified Motor architecture | Remains the shared engine — must gain parallel sandbox management as a runtime capability |
| PRODUCT_CATEGORY `b9ce619` | Product baseline docs; parallel build owners already intended |
| Higgsfield adapter | Replaceable Video provider — not the product, not Motor identity |
| Circuit A/B | Infra/media proofs — keep |
| Serial Video-first / Software-first order debates | **Superseded** — concurrency is the law; bootstrap builders may run together |

## First system success (concurrency)

> Motor creates two isolated sandboxes for two Jobs (any Runway mix), runs them without cross-contamination, and returns independent results visible to NOOS/UI.

Product success remains: finished deliverables in Result UI (video, green PR, report) — earned in parallel, not queued behind each other.

## SG answers

1. **P0 preserved?** Yes.
2. **Conflict?** No — product/runtime concurrency clarification; Motor architecture not redesigned.
3. **Supersedes?** Serial "active order Video → Repair → Research" as a blocking queue in v1.2.
4. **Authority?** Founder sets parallel execution intent; SG canonicalizes; Motor/NOOS operationalize isolation.
5. **Machine-safe?** Isolated sandboxes; scoped secrets; no shared mutable state across Jobs.
6. **Evidence → P99?** Parallel sandbox concurrency receipts + per-Runway result artifacts.
7. **Rollback?** Disable concurrent scheduling; keep single-Job path; preserve sandboxes already proven.

## non_goals

- Reopening Unified Motor architecture
- Replacing Operating Brain Install (SourceA B2B)
- Building Runway-specific logic into Motor core
- Declaring concurrency Done because docs say "parallel"
