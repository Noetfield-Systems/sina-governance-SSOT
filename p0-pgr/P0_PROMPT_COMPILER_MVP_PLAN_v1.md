# P0 PROMPT COMPILER — MVP PLAN v1

**Status:** ACTIVE · governed by `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`

## MVP phases

| Step | Capability | State |
|---|---|---|
| M0 | Packet schema + linter + repair candidates | SCAFFOLDED |
| M1 | Shadow cycle runner (compile → lint → route, zero execution) | SCAFFOLDED |
| M2 | Campaign planner (six board axes + CHESS pass) | SCAFFOLDED |
| M3 | Phase 2 ROI ranker + queue | SCAFFOLDED |
| M4 | Cloud execution with artifact evidence | LOCKED until first gated packet |
| M5 | Earned-autonomy streak tracking | LOCKED — founder unlock |

## Lint reject list (canonical)

| Code | Reject reason |
|---|---|
| R1 | Missing/empty `mission` or `problem_statement` |
| R2 | `deliverable` missing `type`, `destination`, or `acceptance` |
| R3 | Route not in allowed enum, or any Mac route (`MAC_RUNNER`, `HYBRID_MAC`) |
| R4 | Any of the nine gates absent from `gates` |
| R5 | `roi` block missing or non-numeric scores |
| R6 | Vague-verb mission ("explore", "consider", "look into", "think about") without measurable acceptance |
| R7 | Routes validation/review/uncertainty to the founder (violates autonomy loops) |
| R8 | `evidence_required` empty |
| R9 | Wrong/missing `schema` version or `packet_id` format |

A lint failure files a repair candidate and the lane continues (continuity law).
Never STOP on lint.

## CHESS pass (campaign planner)

Forecast → Patch → Proceed → Verify. An improver, not a blocker: every candidate
gets a forecast risk, a patch applied to the packet, `proceed: true`, and a
verify pointer. CHESS never kills a candidate; it repairs it.

## Six board axes

`runtime_health` · `authority_wiring` · `commercial_readiness` · `live_truth` · `cost_roi` · `delivery_readiness`
