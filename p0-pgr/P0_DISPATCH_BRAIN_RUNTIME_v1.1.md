# P0 DISPATCH BRAIN RUNTIME — v1.1 (master contract)

**Status:** ACTIVE · **Era:** `PHASE_2_CLOUD_ONLY_ROI_TRACK`
**Authority:** SG (SSSOT) · Founder canon: `ssot/FOUNDER_CANON_v1.md`
**Scaffolded under:** founder authorization receipt in `receipts/p0pgr/founder/` (census finding F1, receipt `p0pgr-checklist-20260708T144545Z`)

## Purpose

The system writes and routes prompts so Sina doesn't. The runtime compiles problem
statements into prompt packets, lints them, routes them to cloud executors, and
proves every step with receipts. The operator keeps it moving — motion first,
authority controlled.

## Phases

| Phase | Name | State |
|---|---|---|
| 0 | Shadow (compile + lint + route, zero execution) | SCAFFOLDED — this document |
| 1 | Supervised execution (per-packet founder eyes) | BACKFILLED_EMPTY — never ran |
| 2 | Cloud-only ROI track | **CURRENT ERA** |
| 3 | Earned autonomy (receipt-streak unlocks) | LOCKED — founder unlock only |

## The nine execution gates

A packet may actually execute only if ALL pass. Anything failing a gate queues
for founder review; it does not execute "a little bit".

1. `cloud_only` — executes in cloud, never Mac, never HYBRID_MAC fallback
2. `read_only_or_reversible` — no irreversible mutation
3. `roi_positive` — scored ROI block present and positive
4. `no_deploy` — no production deploy/promote
5. `no_external_send` — nothing sent to humans outside the repo
6. `no_legal_financial_commitment`
7. `no_p0_leakage` — P0 CORE read-scope wall respected (`data/p0_core_decision_use_contract_v1.json`)
8. `no_authority_change` — no gate, verifier, or phase mutation
9. `founder_authorization_receipt` — an in-repo receipt exists in `receipts/p0pgr/founder/`

Chat-only founder authorization is not durable evidence (M03 lesson). Record the
verbatim directive as a founder receipt before acting on it.

## Continuity law

Prefer continuous imperfect output over blocked perfection. When quality is weak,
degrade in this order — never default to STOP:

tag confidence → reduce scope → sandbox → partial → provisional → retry-if-ROI-positive → review queue

A failed lint files a repair candidate (`receipts/p0pgr/repair_candidates/`) and
the lane keeps moving.

### HARD_BLOCK — the eight irreversible reasons (must cite one)

1. External send to a human recipient
2. Production deploy or promote
3. Capital commitment / spend above cap
4. Legal or regulatory representation
5. Authority or gate weakening (including L5 verifier changes)
6. Destructive loss of canonical records (non-reversible delete/overwrite)
7. P0 leakage beyond the read-scope wall
8. Identity or credential mutation (keys, tokens, signing)

## FOUNDER_ONLY, always

Deploy · merge · L5 verifier changes · phase unlocks · authority changes ·
scheduled automation approval · retiring a founder trigger.

## Receipt provenance rules

- Timestamps machine-generated at the moment of the event (`datetime.now(timezone.utc)`), never typed from memory.
- Every external claim stores an artifact: per-URL status + body sha256 + saved body under `receipts/p0pgr/artifacts/<receipt-id>/`.
- Route deviation goes in `executor_route_note` — silent deviation reads as authority drift.
- Session-embedded LLM cost is not a bare Determine; use `accounting_note`.
- Flag new receipts for the next founder-visible commit.

## Report format (fixed)

`OBSERVED · <operation sections> · QUALITY STATE · RECEIPT · SCORECARD · NEXT · STOP`

## Runtime map

| What | Where |
|---|---|
| Router rules | `p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md` |
| Packet schema | `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json` |
| Loop-state schema | `p0-pgr/P0_PROMPT_LOOP_STATE_SCHEMA_v1.json` |
| Execution receipt schema | `p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json` |
| MVP plan + lint reject list | `p0-pgr/P0_PROMPT_COMPILER_MVP_PLAN_v1.md` |
| Cycle runner | `scripts/p0pgr_cycle_v1.py` |
| Packet linter | `scripts/p0pgr_packet_lint_v1.py` |
| Evidence reader | `scripts/p0pgr_evidence_reader_v1.py` |
| Campaign planner | `scripts/p0pgr_campaign_planner_v1.py` |
| ROI ranker | `scripts/p0pgr_phase2_rank_v1.py` |
| Scaffold seeder | `scripts/p0pgr_scaffold_seed_v1.py` |
| Tests | `tests/test_p0pgr_phase0.py` |

## Integration law (census F3)

Consume adjacent live systems as inputs; never duplicate their queues:
P0 CORE decision contract (read-only), `receipts/roi-heartbeat-*.json`,
`data/governance_review_queue_v1.json`, `data/governance_library_promote_queue_v1.json`.
