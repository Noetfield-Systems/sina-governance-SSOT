# MOTOR COMMISSIONING AND ACCEPTANCE STANDARD — LOCKED v1

**Version:** v1.0.0_locked_20260710  
**Status:** LOCKED / RATIFIED  
**Authority:** Master SSOT §0.7; P8 continuation doctrine  
**Plane:** P8-MACHINE-LOOPS (acceptance law — not kernel specification)  
**Absorbed from:** advisor `06_COMMISSIONING_AND_ACCEPTANCE_STANDARD_v1.md` (Option C placement)  
**Schemas:** `noetfeld-OS/noetfield-org/schemas/`  
**Terminology:** P7 §11–§12  

---

## Separation

| Class | Meaning |
|---|---|
| `DESIGN_LOCKED` | Custody chain + library + NOOS binding exist |
| `FULLY_COMMISSIONED` | Cold proof evidence below — motor survives commissioning session |

Documents, prompts, and wiring receipts alone **do not** prove commissioning.

---

## Proof Run A — normal autonomous closure

Must demonstrate:

- new remote heading with durable state;
- dependency graph materialized;
- ≥2 concurrent independent jobs;
- deterministic work (`COST-T0` / `W-DET`);
- low-cost intel work (`COST-T1` / `W-INTEL-LOW`);
- real repository change (branch, commit, PR);
- CI + independent recomputation;
- Level-3 edge verification where final PASS is claimed;
- automatic continuation to heading close;
- empty decision queue → auto-close;
- no post-heading founder manual dispatch;
- no dependency on commissioning engineer session.

---

## Proof Run B — failure, repair, reasoning, survival

Must demonstrate:

- deterministic failure with evidence extraction;
- low-cost diagnosis (`COST-T1`);
- bounded repair proposal and execution;
- full re-verification;
- one `WAITING_FOR_FOUNDER_REASONING` job (not bare `HANDOFF_REQUIRED`);
- `FOUNDER_REASONING_PACKET` emitted;
- unrelated jobs continue during wait;
- founder result ingested via `REASONING_RESULT_INGESTOR`;
- automatic resume without workflow restart;
- lease expiry / executor cancellation recovery from durable state.

---

## Cost proof (commissioning)

- deterministic-first routing;
- `COST-T1` where capable;
- `COST-T2` only with cheaper-failure receipt;
- hard budget caps enforced in code;
- no silent premium standing automation;
- subscription founder reasoning path for heavy work;
- cost receipts on automatic intel calls.

---

## Credential proof

- standing machine identity for ongoing service;
- bootstrap credentials removed after proof;
- bootstrap secrets never written to receipts;
- scoped, auditable, revocable standing credentials.

---

## Definition of Done — `FULLY_COMMISSIONED`

All required:

1. durable transactional state live;
2. automatic continuation live;
3. configurable parallelism proven;
4. ≥1 `W-INTEL-LOW` binding live;
5. ≥1 `W-INTEL-BOUNDED` binding live (if COST-T2 in scope);
6. cost router enforced in code;
7. `FOUNDER_REASONING_QUEUE` + packet builder live;
8. `REASONING_RESULT_INGESTOR` live;
9. repair cycle observed (not blind retry);
10. lease recovery observed;
11. real branches/commits/PRs;
12. independent edge verification for final PASS;
13. blocked branches do not stop unrelated work;
14. cold-start evidence (session ended before proof complete).

---

## Explicitly insufficient

- architecture documents alone;
- custody wiring receipt alone;
- fixed-heading replay;
- manual dispatch without durable state;
- Git-backed queue as standing operational DB;
- self-written receipts without independent verifier;
- one successful same-session run;
- premium worker as daily runtime dependency;
- decision packet for every heading.

---

## Classifications (receipt vocabulary)

- `PARTIALLY_COMMISSIONED`
- `FULLY_COMMISSIONED`
- `COMMISSIONING_FAILED`
- `DEGRADED_OPERATION`

Every classification must cite evidence artifact IDs.

---

*v1.0.0_locked_20260710 — Option C absorption; kernel spec remains in NOOS schemas + operational binding.*
