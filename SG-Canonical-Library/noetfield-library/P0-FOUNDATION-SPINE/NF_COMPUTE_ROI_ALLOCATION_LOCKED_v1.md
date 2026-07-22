# NF-COMPUTE-ROI-ALLOCATION-V1 — SG COMPUTE LOCK

**decision_id:** `NF-COMPUTE-ROI-ALLOCATION-V1`  
**title:** Noetfield compute and ROI allocation v1  
**Status:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`  
**Authority:** Founder order constitutionalized by SG  
**Tier:** P0-FOUNDATION-SPINE (compute / platform allocation)  
**Version:** `v1.0.0_locked_20260719`  
**Machine:** `data/nf_compute_roi_allocation_v1_LOCKED.json`  
**Enterprise org:** [noetfield-systems-inc](https://github.com/enterprises/noetfield-systems-inc)  
**Depends on:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` · `NF-NOETFIELD-RUNWAY-PRODUCT-V1` · `NF-RUNWAY-EXECUTION-ASSIGNMENT-V1`  
**Does not activate:** `AUTONOMOUS_PRODUCTION_MUTATIONS=RUN` · cancel enterprise plan · unsupervised promote  
**effective_at:** 2026-07-19  
**proposed_by:** Founder  
**sg_decision:** `SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED`

---

## founder_intent

Keep the enterprise plan. Reallocate compute.

The enterprise plan pays for governance minutes. `Cloudflare Workers` + `Cloudflare Workflows` and `Railway` run scale and margin. The economical LLM matrix is Kernel policy.

one_line_law:

> Enterprise pays governance minutes; Cloudflare and Railway run scale and margin; economical LLM matrix is Kernel policy.

This does **not** cancel the enterprise plan. It forbids spending the 50,000 monthly Actions minutes as a continuous product runtime.

## problem

Actions minutes were being burned as product schedule / continuous dispatch muscle. That is not the profitable hot path. The hot path must be event-driven on Cloudflare; Actions must stay ROI-gated CI and promote gates.

## scope

- platform allocation across Cloudflare, Railway, and GitHub Actions under the enterprise plan
- 50,000 monthly Actions minutes budget classes A–D
- job wake law: authenticated HTTP `job_id` only
- Kernel economical LLM matrix (`T0` → DeepSeek → GLM repair → Kimi)
- wasm posture: typescript kernel now; wasm only after cpu-bound proof

## non_goals

- cancel the enterprise plan
- lift `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`
- declare SG runtime commissioned
- replace Cloudflare hot path with Railway
- spend Actions minutes as 24/7 product schedule

---

## platform_law

| Layer | Host | Owns | Must not |
|-------|------|------|----------|
| Hot API + Job DAG | `Cloudflare Workers` + `Cloudflare Workflows` | Auth, credits, Kernel gates, `job_id` wake, LLM fetch, receipts | Actions cron / `repository_dispatch` as continuous product muscle |
| Heavy / long | `Railway` | Video, heavy Python, long sandbox, Worker-invoked executors | Replace the Cloudflare hot path |
| Org + CI budget | GitHub Actions under enterprise plan | PR CI, main deploy gates, founder-manual proofs, merge gates | Product schedule, continuous dispatch muscle, feature-branch CI spam |
| Cognition | Kernel economical LLM matrix | T0 first, DeepSeek default, GLM repair, Kimi long-context, cost ledger | Idle LLM; LLM when deterministic suffices |

## actions_minutes_budget

Monthly total: **50,000**. Alert at **70%**.

| Class | Share | Minutes | Allowed triggers |
|-------|------:|--------:|------------------|
| A — merge gates | 55% | 27,500 | `pull_request`, push to `main` |
| B — deploy / promote | 20% | 10,000 | push to `main`, `workflow_dispatch` |
| C — founder / canary proofs | 15% | 7,500 | `workflow_dispatch` only |
| D — reserve / incident | 10% | 5,000 | `workflow_dispatch` only |

### hard_bans

- `schedule` on product runtimes
- `repository_dispatch` as continuous muscle
- CI on every feature-branch push
- high-frequency Actions whose only job is curling a Cloudflare health endpoint

## runtime_topology

```text
client / product API
  → Cloudflare Worker (auth, credit, OpenAI-compat)
  → Kernel (T0 gates + cost matrix)
  → economical LLM fetch if needed (DeepSeek → GLM repair → Kimi)
  → Cloudflare Workflows if multi-step Job
  → Railway only if Worker cannot hold the job
  → receipt on Cloudflare (R2 / D1)
  → sleep

GitHub Actions (enterprise plan)
  → PR opened → CI (class A)
  → merge to main → deploy (class B)
  → founder button → one proof (class C)
```

Job wake: authenticated HTTP `job_id` only → Workflow → receipt → sleep. Not Actions cron.

## economical_llm_matrix

1. T0 first — no model if a deterministic gate can decide
2. DeepSeek — default hot path
3. GLM — only on schema / repair fail
4. Kimi — only on long-context escalate
5. Every call writes the cost ledger (tokens × matrix rate)
6. Hard-stop if job or tenant ceiling is hit
7. Zero LLM on idle — no tick / cron health model

wasm_posture: typescript / javascript kernel in Worker now. wasm only after a live hot path proves cpu-bound. Do not block shipping on a Rust rewrite.

## holds_preserved

- `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD`
- `SG_RUNTIME=NOT_COMMISSIONED`
- `SG_ENFORCEMENT=NOT_ENABLED`

Agents may observe, draft, test, and open PRs. They may not lift HOLD or treat enterprise minutes as permission for unsupervised production mutation.

## weekly_receipt_required

File a weekly receipt with Actions minutes by class A/B/C/D, percent of 50,000, disabled schedule or dispatch runtimes, Cloudflare hot-path deploy SHA, Railway heavy-job count.

## relation_to_prior_locks

- Wake default is event-driven authenticated HTTP `job_id`; schedules are allowed under `NF-WAKE-PATH-CONFLICT-POLICY-V1` passport — do not hard-block production path solely for cron / `scheduled()`.
- Extends `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` scaling posture (Cloudflare Agents + Workflows runway). Clarifies the enterprise plan as org shell + ROI continuous-integration budget, not compute strategy.

## sg_decision

`SG_ACCEPTED` · `IMPLEMENTATION_AUTHORIZED` under founder order 2026-07-19.
