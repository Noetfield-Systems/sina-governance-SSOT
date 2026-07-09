---
name: p0pgr-packet-compiler
description: Compile any problem statement into a lint-clean, delivery-aware P0-PGR v1.1 prompt packet for the sina-governance-SSOT dispatch brain. Use this skill whenever the user asks to "make a packet", "compile a packet", "turn this into a prompt packet", "add this to the outbox/queue", names a finding (F1, F2, census RED, doc drift, funnel issue) that needs to become dispatchable work, or describes any task that should be executed by a worker agent under P0-PGR governance rather than done ad hoc. Also use it when an advisor message defines a new mission that must become one or more packets.
---

# P0-PGR Packet Compiler

A packet is a governed executable instruction — never free text. Workers receive ONLY the packet: no P0 doctrine, no pipeline reasoning, no founder judgment. This skill turns a problem into a packet that passes lint on the first try.

## Ground truth

- Schema: `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json` (v1.1, `additionalProperties: false` — inventing fields fails lint)
- Linter: `python3 scripts/p0pgr_packet_lint_v1.py <packet.json>` — verdict PASS or REPAIR_CANDIDATE, exit 0 either way
- Working examples: `receipts/p0pgr/outbox/P0PGR-*.json` — read one before writing your first packet
- Destination: `receipts/p0pgr/outbox/P0PGR-YYYYMMDD-NNN.json` (next free NNN for that date)

## Compilation order (why this order matters)

1. **Evidence first.** A packet without real `evidence_refs` (receipt paths, registry rows, campaign findings) is blind dispatch — forbidden. If you can't cite evidence, the problem needs research, not a packet.
2. **Classify**: blocker | repair | verification | revenue | hygiene | research | deploy | architecture | founder_escalation.
3. **Choose execution_mode** — CLOUD_ONLY is the default and, in the current cloud-only era, effectively the only dispatchable mode. Needs local repo state / secrets / Mac tooling / IDE review → still author it, but mark for HOLD_CLOUD_UNSAFE handling in the queue. Deploy/merge/authority scope → FOUNDER_ONLY.
4. **Bound the task**: concrete numbered steps, one repo, exact output location (usually "write exactly one receipt to receipts/p0pgr/"), and a stop_rule. A worker should never have to decide what "done" means.
4b. **Demand artifact-grade evidence in success_receipt.** For any task with external claims (fetches, live checks), add `evidence_artifacts` to `success_receipt.required_fields` and say in the task where artifacts land (`receipts/p0pgr/artifacts/<receipt-id>/`, per-URL status + body sha256). The M03 audit downgraded an otherwise-good execution because its packet let prose stand in for artifacts.
5. **Set ROI honestly**: roi_score 0–100 with a reason a skeptic would accept; value_class revenue_path | proof_asset | risk_reduction | hygiene | none; model_tier cheap unless judgment is genuinely needed (premium requires roi_score ≥ 70); explicit cost_limit_usd.
6. **quality_handling** encodes the continuity law: `default_on_low_quality` is provisional/degrade-style, never a stop; `allowed_result_states` ≥ 2 of the nine states; `hard_block_allowed_reasons` empty for read-only packets (a read-only audit has nothing legitimate to hard-block).

## Field checklist (all required — lint enforces)

id (`P0PGR-YYYYMMDD-NNN`) · created_at · lane (SourceA|NOOS|SG|TrustField|Noetfield|Revenue|Ops) · problem_class · owner_agent · model_tier · roi_score · roi_reason · value_class · cost_limit_usd · authority_scope · execution_mode · delivery_route · target_executor · repo · worktree_required · local_secrets_required · cloud_safe · fallback_route · quality_handling · context_summary (≤1200 chars, evidence-grounded) · task (numbered steps) · constraints (≥4, must include: no P0 leakage; no speculative PASS; receipt required; stop after completion) · forbidden_actions (≥1; repo-move and authority-flip bans where relevant) · stop_rule · success_receipt (≥5 required_fields incl. evidence, changed_files, commands_run, pass_fail, next_pointer) · evidence_refs (≥1) · decision_ref · dispatch_mode (shadow until founder unlocks auto).

## Traps that cause REPAIR_CANDIDATE (each caught in production)

- Extra fields — schema is closed; notes belong in queue/campaign receipts, not packets.
- HYBRID_MAC without `canonical_path` + `mac_required_reason`.
- `cloud_safe: false` with `execution_mode: CLOUD_ONLY`.
- `authority_scope: deploy` without `execution_mode: FOUNDER_ONLY`.
- Merge/L5/authority wording in the task without the FOUNDER_ONLY gate.
- P0-CORE text pasted into context_summary/task — the linter fingerprint-sweeps against P0-CORE; paraphrase evidence, never quote doctrine.
- `mac_runner` as fallback_route in the cloud-only era — use `human_review_queue`.
- Claiming the underlying issue will be "fixed" — audit packets report; repair is a separate packet.

## Always finish with

```bash
python3 scripts/p0pgr_packet_lint_v1.py receipts/p0pgr/outbox/<packet>.json
```
PASS → report packet id, route, and where it sits in the queue. REPAIR_CANDIDATE → fix the listed reasons and re-lint (the lane never stops for a bad draft — but don't leave one in the outbox either).
