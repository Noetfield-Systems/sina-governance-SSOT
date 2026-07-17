# NF-UNIFIED-MOTOR-ARCHITECTURE-V1 — SG FINALIZATION PACKET

**decision_id:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1`  
**title:** Noetfield Unified Motor Core architecture v1  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` (foundation wave only)  
**Authority:** SG Architecture Finalization Gate  
**Tier:** P0-FOUNDATION-SPINE (execution-plane architecture)  
**Version:** v1.0.0_locked_20260717  
**Machine:** `data/nf_unified_motor_architecture_v1_LOCKED.json`  
**Waves:** `docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md`  
**Packet id:** `SG-FINALIZATION-NF-UNIFIED-MOTOR-V1`  
**effective_at:** 2026-07-17  
**proposed_by:** Founder + Brain/Architect (Advisor 2 architecture; Advisor 1 operating doctrine)  
**sg_decision:** `SG_ACCEPTED` with three corrections and T0-first foundation commission  
**sg_authority_sha:**   
**supersedes:** none as ACTIVE architecture (consolidates distributed Client-Zero Motor into a profile)

---

## founder_intent

Architecture adopts Advisor 2 implementation design under Advisor 1 operating doctrine: no Mac production dependency; cloud-resident institutional owners; shared open-model inference as default cognition; commercial APIs only through explicit escalation; existing Motor preserved as Client-Zero Motor profile on a reusable Unified Motor Core.

## problem

Distributed Motor pieces (builders, worktrees, CI, founder gates, NOOS autoruns, SourceA dispatch, SG authority, receipts) lack a single canonical runtime that separates persistent institutional ownership from durable multi-step job execution.

## scope

- Constitutional architecture for Unified Motor Core
- Resident Role runtime on Cloudflare Agents
- Durable Motor Workflow on Cloudflare Workflows
- Single `GitHub App` identity
- SandboxAdapter and OpenModelRuntime interfaces
- Model Router tiers T0–T3
- Foundation commission without GPU

## non_goals

- GPU / RunPod deployment in foundation wave
- Sole-production use of `Cloudflare Sandbox` in place of Git worktree + CI
- Unsupervised architecture self-redesign
- Duplicating full authority contracts into every venture repo
- Declaring `FULLY_COMMISSIONED` without cold proof

---

## architecture

### Operating doctrine (Advisor 1 — binding policy)

- no Mac dependency in production
- cloud-resident institutional owners
- shared open-model inference as default cognition
- commercial APIs only through explicit escalation
- RunPod/vLLM as a plausible first open-model deployment adapter

### Implementation design (Advisor 2 — adopted, with corrections)

- Cloudflare Agents SDK for Resident Role owners (not manually rebuilding everything on Durable Objects)
- one codebase with several persistent role-owner instances
- single `GitHub App`
- RunPod/vLLM as replaceable OpenModelRuntime adapter
- persistent institutional state outside the model provider

### Crucial correction — owners ≠ Motor jobs

```text
Cloudflare Agents  = persistent Resident Role owners
Cloudflare Workflows = durable Motor job execution
NOOS = portfolio control plane
Motor Registry = recipe and truth contract
Motor Runner = system that joins them
```

### Components

```text
Unified Motor Core
├── Recipe Registry
├── Job State Machine
├── Resident Role Runtime
├── Durable Workflow Runner
├── Policy Hub
├── Sandbox Adapters
├── Model Router
├── Verification
├── Promotion
├── Outcome Probes
└── Evidence Ledger
```

Profiles on the core (examples):

```text
Unified Motor Core
├── Noetfield Client-Zero Motor
├── Software Production Motor
├── Investor Workflow Motor
├── Law Firm Motor
├── Healthcare Motor
└── Sovereignty-Aware Canadian Motor
```

### Canonical flow

```text
GitHub (repos · PRs · CI)
  → GitHub App events
  → Cloudflare Event Gateway
  → Resident Role owners (SG · NOOS · SourceA · Builder · Verifier)
  → Policy Hub + Recipe Selection
  → Motor Workflow Runner
       create job → resolve authority → provision sandbox → invoke worker/model
       → verify → repair/escalate → wait for approval → promote → probe → receipt
  → SandboxAdapter · Model Router · Evidence/P99
```

### Resident Role instances (one codebase)

```text
NoetfieldResidentRoleAgent
├── noetfield:sg.registrar
├── noetfield:noos.portfolio-owner
├── noetfield:sourcea.dispatch-owner
├── noetfield:sandbox.builder-owner
└── noetfield:sandbox.verifier-owner
```

Each instance carries: `role_id`, `repo_bindings`, `authority_contract`, `event_subscriptions`, `allowed_tools`, `forbidden_tools`, `model_profile`, `memory_policy`, `receipt_obligations`, `escalation_policy`.

### Role boundaries

| Role | Does | Does not |
|------|------|----------|
| SG Registrar Owner | Resolve authority; validate contracts/permissions/receipts | Use LLM when deterministic policy suffices |
| NOOS Portfolio Owner | Observe; classify; route to recipes; true founder gates; monitor jobs | Directly edit other repositories |
| SourceA Dispatch Owner | Context; recipe; compile contracts; select workers/tiers; promotion packet | Own institutional memory outside SG/P99 |
| Builder Owner | Claim/supervise jobs; identity + queue + responsibility | Be a permanent coding process |
| Verifier Owner | Deterministic checks; evidence boundaries; proportional semantic review | Heavyweight verification theater |

### Existing piece → Unified Motor role

| Existing piece | Unified Motor role |
|----------------|--------------------|
| Fable Motor Registry | Recipe and job-contract layer |
| PR #69 SDK–Hub wiring | Worker-to-policy and worker-to-ledger interface |
| PR #72 NOOS semantics | Truthful observation and failure classification |
| NOOS autoruns | Scheduled triggers, witnesses, repair initiators |
| SourceA | Job compiler and dispatch layer |
| SG | Canonical authority and policy source |
| GitHub App | Repository event and machine identity |
| Claude/Codex | Worker adapters |
| Git worktrees/CI | Initial production-grade SandboxAdapter |
| RunPod/vLLM | First OpenModelRuntime adapter |
| P99 | Evidence and institutional memory |
| Founder | Authority for consequential promotion |

---

## Three corrections (binding)

1. **Agents for owners; Workflows for jobs** — do not implement a complete long-running software-production job inside an Agent method. Owner receives event → starts Motor Workflow.
2. **SandboxAdapter is multi-backend** — `GitWorktreeSandbox` + `GitHubActionsSandbox` first; Cloudflare Sandbox evaluate later (experimental).
3. **RunPod is first adapter, not Motor identity** — persist results immediately in Noetfield-controlled storage; provider compute must never be the job ledger.

---

## model_policy

```text
T0 — Deterministic (no model call)
T1 — Noetfield-controlled open model (default cognition)
T1S — Larger/specialist open model
T2 — Economical commercial API (requires ESCALATE_REQUIRED)
T3 — Premium commercial reasoning (founder/high-risk escalation)
```

No escalation receipt means no proprietary commercial model call.

---

## sandbox_policy

```text
SandboxAdapter
├── GitWorktreeSandbox        ← first stable
├── GitHubActionsSandbox      ← proven
├── EphemeralContainerSandbox
└── CloudflareSandbox         ← evaluate when appropriate
```

---

## p0_core_alignment

Aligned to SSOT v6 Level 0:

- Author ≠ Subject (Verifier Owner separate; independent evidence)
- Sina owns DECIDE (promotion / consequential authority remains founder-only)
- Reality > report (outcome probes; external proof)
- Banked frames reopen only on new facts
- Convergence is warning
- Removal is free

### protected_invariants

- Mac is not a production dependency
- Provider compute is never institutional memory
- Commercial model calls require `ESCALATE_REQUIRED`
- Source promotion separate from runtime promotion
- Outcome observation separate from attribution
- Exact recipe-version matching on jobs
- Proven state requires evidence; blocked/diverged/unproven require reasons

### forbidden_states

- Motor job ledger living only on RunPod / model provider
- Full authority contract duplicated into every repo
- Unsupervised architecture redesign
- Calling foundation design `FULLY_COMMISSIONED` without cold proof
- T2/T3 calls without escalation receipt

### founder_only_actions

- Consequential production promotion / merge-deploy authority
- High-risk / adversarial T3 escalation approval when required
- Architecture supersession of this decision
- Customer Motor commission ratification when material

### machine_safe_actions

- T0 deterministic diagnosis/repair under evidence-path-only authority
- Recipe selection under registered policy
- Deterministic verification
- Receipt writing to authorized sinks
- Launch `Motor Workflow` from Resident Role events
- Pause/resume waits for founder approval events

---

## p0_to_p99_impact

| Plane | Impact |
|-------|--------|
| P0 | New execution-plane architecture under Foundation Spine; Finalization Gate in P8 |
| P1–P9 | Motor commissioning, CHESS, cost doctrine remain; Client-Zero becomes profile |
| P10–P98 | Venture Motors (Investor Workflow, etc.) become profiles on shared core |
| P99 | Decision + waves + wiring receipts; job evidence routes to P99 |

---

## security / privacy / sovereignty / secrets

- Standing machine identity via a single `GitHub App` (not founder personal account)
- Secrets in repo/org secret stores; never in receipts
- Data sovereignty: prefer Noetfield-controlled storage for job state and evidence
- Open-model path default; commercial path escalated and cost-bounded
- Evidence-path-only permissions for first T0 job

---

## operational_model

Observe → Detect → Critique → Repair → Re-deploy → Observe (Living System).  
NOOS observes/classifies/routes; Motor executes; SG authorizes; P99 preserves.

### failure_modes / recovery / rollback

- Repair/escalate inside Motor Workflow; do not silent-restart without evidence
- Escalation rather than restart when repair cannot be proven
- Rollback: disable recipe; retain prior Client-Zero paths; revert pointers to previous authority SHA
- Foundation failure must not require GPU or commercial APIs to diagnose

### evidence_requirements

- Before/after checks on repair jobs
- Exact-SHA receipts on promote/deploy claims
- ≥60-second outcome probe on website/publish jobs
- Model identity in every model-backed receipt
- Immediate persistence of OpenModelRuntime results

---

## vendor_boundaries / portability / cost

- Cloudflare: Resident Role + Workflow substrate; portable behind interfaces
- GitHub App: repository identity; app_count = 1
- RunPod: first OpenModelRuntime only; `permanent_vendor_lock: false`
- Cost: T0-first proof; T1 default; T2/T3 budget_policy PASS required

---

## migration

| Item | Disposition |
|------|-------------|
| Existing Noetfield Motor | `client_zero_profile`; replacement = false; migration = incremental |
| Motor Registry | Harden v1.1 invariants (separate wave) |
| PR #69 / #72 | Finish foundations; not redefined by this packet |
| Mac | development / evaluation / benchmarking / diagnostics only |

---

## SG answers (gate questions)

1. **P0 core preserved?** Yes — DECIDE, Author≠Subject, Reality>report, no Mac production dependency.
2. **Conflict with ACTIVE decision?** No direct conflict; consolidates Client-Zero into profile; commissioning standard remains for cold proof.
3. **Superseded?** None ACTIVE replaced. Distributed “Motor = only Agents” framing rejected. GPU-first plans deferred.
4. **Authority stages?** SG authority → NOOS route → Resident Role start Workflow → Policy Hub → sandbox/model → founder for consequential promote → P99.
5. **Machine-safe?** T0 jobs, deterministic verify, receipt write, workflow orchestration under contracts.
6. **Founder-only?** Consequential promote; architecture supersession; material customer commissions; required T3.
7. **Boundaries?** Secrets out of receipts; Noetfield storage for state; SandboxAdapter bounds mutation; evidence-path-only for first job.
8. **Evidence → P99?** Workflow completion receipt + custody/doctrine receipts; provider output copied immediately.
9. **Rollback?** Recipe disable + prior profile paths + authority pointer rollback.
10. **Authority SHA?** Commit SHA that lands this packet on `doctrine/nf-unified-motor-architecture-v1` (recorded in P99 receipt after commit).

---

## implementation_waves (summary)

1. Finish PR #72 / #69 foundations (observe; fail-closed Hub)
2. Harden Motor Registry v1.1 invariants
3. Commission `NF-UNIFIED-MOTOR-V1-FOUNDATION` (T0 vertical slice; no GPU)
4. First T0 job: receipt-writer repair recipe
5. Separate commission: `NF-OPEN-MODEL-RUNTIME-ADAPTER-V1`
6. Repo embodiment via `noetfield.repo-owner-ref.v1` pointers

See `docs/NF_UNIFIED_MOTOR_IMPLEMENTATION_WAVES_v1_LOCKED.md`.

## acceptance_conditions (foundation)

- Resident Role Agent + five instances
- MotorJobWorkflow with founder approval wait/resume
- Recipe loader + seven-state job record
- Hub /check and /ledger integration
- GitWorktreeSandbox + deterministic verifier
- Receipt persistence + NOOS event adapter
- First T0 real job proves NOOS → owner → recipe → policy → Workflow → sandbox → verify → receipt

## open_questions

- Cloudflare account / Worker project home for Unified Motor Core codebase
- Pin of Motor Registry v1.1 executable schema location (sandbox vs SG projection)
- Timing of Investor Workflow Motor profile after foundation proof

## risks

- Equating `Cloudflare Agents SDK` with the whole Motor
- Cutting over to `Cloudflare Sandbox` before SandboxAdapter readiness
- Provider memory leakage if RunPod results not persisted
- Declaring operational proof before commissioning standard cold runs
