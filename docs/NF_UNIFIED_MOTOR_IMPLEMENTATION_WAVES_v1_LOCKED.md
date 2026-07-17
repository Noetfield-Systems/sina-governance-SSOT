# NF Unified Motor — Implementation Waves v1 LOCKED

**Authority:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1`  
**Status:** `IMPLEMENTATION_AUTHORIZED` for foundation; later waves separate commissions  
**Version:** v1.0.0_locked_20260717

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

- `OpenModelRuntime` interface
- pinned model revision
- RunPod/vLLM adapter
- health/preflight
- immediate result persistence
- time and cost controls
- model identity in every receipt
- explicit commercial escalation path

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
