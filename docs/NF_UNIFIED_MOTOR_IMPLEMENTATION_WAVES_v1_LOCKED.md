# NF Unified Motor — Implementation Waves v1 LOCKED

**Authority:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1`  
**Status:** `IMPLEMENTATION_AUTHORIZED` for foundation; later waves separate commissions  
**Version:** v1.1.0_locked_20260718  
**Amendment:** scaling posture locked; W5 acceptance contract expanded; WIP = Circuit A + Circuit B

---

## Wave order (binding)

### W0 — Finish existing foundations

- PR #72: merge observability semantics; observe one live NOOS cycle
- PR #69: fail-closed Hub check; payload minimization; local receipt retention; merge SDK–Hub adapter
- No large independent-verification ceremony

### W1 — Motor Registry v1.1 invariants

Executable invariants:

- proven state requires evidence
- blocked/diverged/unproven require reasons
- exact recipe-version matching
- timestamp format and ordering
- required receipt fields
- external-proof requirements
- source promotion ≠ runtime promotion
- outcome observation ≠ attribution
- explicit mutation classes

### W2 — `NF-UNIFIED-MOTOR-V1-FOUNDATION` (commission)

Deliver only:

- Cloudflare Worker project
- Base `NoetfieldResidentRoleAgent`
- Five configured Resident Role instances
- GitHub webhook gateway
- `MotorJobWorkflow`
- Recipe Registry loader
- Seven-state job record
- Hub `/check` + `/ledger` integration
- `GitWorktreeSandbox` adapter
- Deterministic verifier adapter
- Founder approval wait/resume
- Receipt persistence
- NOOS event adapter

**Forbidden in W2:** GPU deployment.

### W3 — First T0 real job

Wire `receipt_writer_completion_evidence_repair` → `NF-MOTOR-RECEIPT-WRITER-REPAIR-001` with:

- registered owner
- machine-safe authority
- evidence-path-only permissions
- before/after verification
- escalate rather than restart when repair unproven

Proves: NOOS → Resident Role → recipe → policy → Workflow → sandbox → verification → receipt.

### W4 — Second job (authority / promotion)

Founder-gated website change:

Founder instruction → SourceA owner → WEB-PUBLISH recipe → Builder sandbox → tests → PR → Workflow waits → merge/deploy → ≥60s outcome probe → exact-SHA receipt.

### W5 — `NF-OPEN-MODEL-RUNTIME-ADAPTER-V1` (separate commission)

Deliver only after dedicated commission. Do **not** implement providers in W1/W2.

Base requirements:

- `OpenModelRuntime` interface
- pinned model revision
- RunPod/vLLM adapter
- health/preflight
- immediate result persistence
- time and cost controls
- model identity in every receipt
- explicit commercial escalation path

#### W5 acceptance requirements (provider hardening — deferred)

Encode as acceptance gates for the W5 commission. Forbidden to satisfy these by calling DeepSeek / Kimi / GLM / RunPod in W1–W4:

1. **Canonical output normalization** — provider outputs map through `OutputNormalizer` → `CanonicalAction` before Motor state mutation
2. **Error classification** — every provider failure classified as `FATAL` | `SKIP_TIER` | `RETRY` | `VALIDATION_FAIL`
3. **Rolling error-rate breaker** — open breaker only after minimum sample count; never trip on a single sample
4. **Local idempotency / result truth** — idempotency keys and result truth live in Noetfield-controlled store / trace, never only on the provider
5. **SLO budgets** — separate latency / cost / success budgets per tier; budget_policy PASS required before T2/T3
6. **Provider rate-limit dispatch** — queue-aware dispatch respects provider limits without Motor ledger on provider compute
7. **Spend kill-switch** — hard stop on budget breach; no silent continue

**Forbidden in W5 until commissioned:** DeepSeek / Kimi / GLM tier additions; production RunPod calls from foundation Workers.

### W6 — Repository embodiment

A single `GitHub App`; each repo gets generated `noetfield.repo-owner-ref.v1` pointer only — no full authority contract duplication.

---

## Trigger / loop posture

| Wave | Trigger host | Notes |
|------|--------------|-------|
| W0–W1 | founder-manual / existing PR CI | finish foundations |
| W2–W3 | cloud (Cloudflare Worker + Workflows) | first Motor vertical slice |
| W4+ | cloud | promotion waits + probes |
| Mac | complement only | never sole production motor |


---

## Cloud-first liveness contract (inactive until commissioning)

| Field | Value |
|-------|-------|
| `loop_id` | `nf-unified-motor-foundation-v1` |
| Trigger host | `cloud` (Cloudflare Worker + Workflows); Mac = development complement only |
| Cadence | reserved; not scheduled under HOLD |
| `last_fired_at` target | `noos_loop_registry` / Motor job ledger (when commissioned) |
| Deadman | independent CF deadman path (different Worker); 2× interval staleness → alert + one restart attempt + receipt |
| Receipt | `receipts/doctrine/` + P99 Motor evidence |
| Commission status | `NOT_COMMISSIONED` — registry may list the row; do not deploy or schedule under `AUTONOMOUS_PRODUCTION_MUTATIONS=HOLD` |
| 48h gate | commissioning acceptance requires laptop-closed cloud heartbeats still firing |

Foundation implementation ends at `FOUNDATION_BUILT_FOR_FOCUSED_REVIEW`, not `FULLY_COMMISSIONED`.
