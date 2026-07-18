# NF-RUNWAY-EXECUTION-ASSIGNMENT-V1 — SG EXECUTION LOCK

**decision_id:** `NF-RUNWAY-EXECUTION-ASSIGNMENT-V1`  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder assignment constitutionalized by SG  
**Tier:** P10-PRODUCT-LAYERS  
**Version:** v1.0.0_locked_20260718  
**Machine:** `data/nf_runway_execution_assignment_v1_LOCKED.json`  
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-NOETFIELD-RUNWAY-PRODUCT-V1` v1.3  
**Does not activate:** NOOS Issue/CI autonomous routing · `GATEWAY_MODE=live` · production promotion

## Decision

The first three Runways build in parallel against one versioned Unified Motor contract. Every build and job executes in an isolated sandbox under `noetfield:sandbox.builder-owner`. Workers are temporary execution adapters, not the permanent owner or identity of a Runway.

## Corrected worker taxonomy (binding)

| Name | Exact role | Authority boundary |
|------|------------|--------------------|
| Claude Code | Local implementation worker for Unified Motor foundation and Software Repair | Builds in scoped sandbox; cannot certify closure or promote |
| Codex Local | Local GPT/Codex implementation worker for Research Runway repository code | Builds Research in an isolated local worktree/sandbox; not GPT Advisor and not Codex Cloud |
| Cursor | Local implementation worker for Video Runway | Builds in scoped sandbox; cannot certify closure or promote |
| GPT Work Verifier on GitHub | GitHub-resident independent verification worker | Clean-checkout evidence review under Verifier Owner; never Builder Owner for the artifact it verifies |
| Codex Cloud | Separate bounded cloud worker | Clean-checkout build, review, or commissioning when assigned; not the Research implementation worker here |
| GPT Advisor | Founder-facing product/architecture advisor | Advises on behavior, acceptance criteria, and commissioning intent; does not implement, certify, or promote |

Permanent institutional owners remain `noetfield:sandbox.builder-owner` and `noetfield:sandbox.verifier-owner`. Shared runtime code does not merge their authority, state, tools, or receipt obligations.

## Exact build assignment

| Workstream | Accountable owner | Product / architecture input | Implementation worker | Deliverable |
|------------|-------------------|------------------------------|-----------------------|-------------|
| Unified Motor Foundation | `noetfield:sandbox.builder-owner` | Locked Motor/Runway contracts | Claude Code | Shared job model, interfaces, execution loop, artifacts, Railway manifest, `runway doctor` |
| Software Repair Runway | `noetfield:sandbox.builder-owner` | Locked result contract | Claude Code | Issue/failed test → sandbox patch → tests → green PR |
| Research Runway | `noetfield:sandbox.builder-owner` | Founder + GPT Advisor | **Codex Local** | Search adapters, source collection, synthesis, citations, report output, Result UI |
| Video Runway | `noetfield:sandbox.builder-owner` | Locked Video result contract | Cursor | Brief compiler, storyboard, provider adapter, rendering loop, playable preview/download |
| Future Runways | `noetfield:sandbox.builder-owner` | SourceA selects approved recipe and bounded worker | Best available bounded worker | Only after each first-three Runway has completed one real job |

The Future Runway gate does not serialize the first three. Video, Software Repair, and Research execute concurrently.

## Shared contract publication

Claude Code publishes `noetfield.runway-core.v0.1` with:

```text
RunwayDefinition · MotorJob · CompiledPlan · PromptCompiler · ModelRouter
ToolAdapter · Artifact · RunwayResult · JobEvent · CostRecord · ExecutionState
```

Research and Video begin immediately with schemas, adapters, deterministic validators, mock fixtures, input forms, and result components. Until the shared implementation lands, mocks implement the same contract shapes.

They must not create another job engine, Model Router, Prompt Compiler core, receipt system, NOOS state, approval model, or permanent owner.

## Parallel sandbox law

`one Job ↔ one isolated sandbox`

Filesystem, secret scope, network allowlist, artifact root, logs, and teardown evidence are Job-scoped. Failure, retry, verification, or promotion in one sandbox must not mutate another. NOOS observes each job independently.

## Verification assignment

Level A is Builder checks: unit and contract tests, provider mocks, happy/error paths, and configured format/type checks. It is required but not independent acceptance.

Level B is deterministic CI: build, tests, types, schemas, security scans, forbidden-file checks, secret-leak checks, and contract compatibility.

Level C is first commissioning or a high-risk exception. The accountable owner is always `noetfield:sandbox.verifier-owner`.

| Runway | Builder | First commissioning worker |
|--------|---------|----------------------------|
| Software Repair | Claude Code | Codex Cloud, clean checkout and focused review |
| Research | Codex Local | **GPT Work Verifier on GitHub**, clean checkout and focused evidence/citation review |
| Video | Cursor | Codex Cloud plus deterministic media checks |

A named worker is an adapter under Verifier Owner, not a new institutional role. The Builder may not certify its own closure. After first commissioning, ordinary changes use CI and deterministic outcome probes; independent semantic review returns for exceptions or high-risk changes.

## Result contracts

**Software Repair:** reproduce original failure → apply repair → original failure is gone → relevant regression tests pass → no required check is weakened → real branch/commit/PR exists. Done: `Green PR`.

**Research:** every material claim has support; citations resolve and support their sentences; sources are not fabricated or deceptively duplicated; conflict and uncertainty are represented; the report answers the question; a downloadable artifact exists. Deterministic checks cover URL resolution, source title/domain, quotation limits, citation coverage, unsupported factual-paragraph detection, and rendering. GPT Work Verifier on GitHub checks first-commissioning evidence, counterevidence, and honest uncertainty. Done: `Decision-ready cited report`.

**Video:** provider completion alone is insufficient. Deterministic checks cover file/checksum, `ffprobe`, duration, resolution/aspect ratio, codec, corruption/black frames, relevant silence, input traceability, UI preview, HTTP download, provider cost, and runtime. Codex Cloud checks first-commissioning correspondence to brief, obvious generation defects, text legibility, brand/safety defects, and preview UX. Done: `Finished playable and downloadable video`.

## Operating matrix

| Question | Owner |
|----------|-------|
| What Runway should execute? | SourceA |
| What policy applies? | SG / Hub |
| Who owns the job? | SANDBOX Builder Owner |
| Which bounded worker builds it? | Claude Code, Codex Local, Cursor, Codex Cloud, or approved future adapter |
| Did code pass? | CI |
| Does the real result exist? | Runway-specific deterministic checker |
| Is independent semantic review required? | Verifier Owner, risk-based |
| Is the job stalled? | NOOS |
| Was authority exceeded? | SG |
| Is evidence continuous? | ReceiptGraph / P99 checks |
| Does the first result meet product expectations? | Founder, then encoded acceptance rules |

NOOS audits operational health. SG audits authority and policy, not every feature PR or artifact. P99 preserves evidence continuity; it does not independently judge product quality. Founder reviews first real results, major product direction, and consequential production authority.

## Issue and CI failures

NOOS PR #82 remains proposal-derived and is not autonomously wired by this lock:

```text
NOOS Issue Manager → classify and surface
candidate code failure → SANDBOX Builder Owner
CI workflow / runner / flaky failure → NOOS CI Reliability Owner
secret / permission / deployment authority → SG / founder gate
```

## Release ladder

```text
SPECIFIED
→ MOCK_EXECUTABLE
→ LIVE_PROVIDER_CONNECTED
→ REAL_JOB_COMPLETED
→ FIRST_COMMISSIONING_ACCEPTED
→ REPEATABLE
```

`REPEATABLE` requires three consecutive real jobs without manual GitHub or database intervention.

## Immediate parallel commissions

```text
Claude Code → Unified Motor core v0.1 + Software Repair + one real green PR
Codex Local → Research contracts/adapters/renderer/mock → one real cited report
Cursor → Video input/storyboard/provider/status/player/validator → one real playable video
NOOS → track foundation job + repair proof + research proof + video proof
```

No new architecture project, lane, or governance program. Terminal evidence is exactly: one green PR, one cited report, one playable video. Documentation alone is not completion proof.
