---
name: p0pgr-receipt-verifier
description: Adversarially verify P0-PGR receipts, execution reports, and agent PASS claims in the sina-governance-SSOT repo before trusting them. Use this skill whenever the user pastes or points at a cycle receipt, execution receipt, campaign receipt, or worker report and asks anything like "verify this", "did this really pass", "audit this receipt", "can I trust this", or when a returned result must be accepted/rejected before the queue advances. Also use it proactively before reporting any P0-PGR result to the founder as done.
---

# P0-PGR Receipt Verifier

Receipts are the system's only truth. A wrong ACCEPT poisons everything downstream; a lazy REJECT freezes a living system. This skill does neither: adversarial on evidence, generous on motion.

## Inputs and references

- Loop-state schema: `p0-pgr/P0_PROMPT_LOOP_STATE_SCHEMA_v1.json`
- Packet schema: `p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json`
- Contract (states, continuity law, hard-block reasons): `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`
- The packet the receipt answers to: `receipts/p0pgr/outbox/<packet-id>.json`

## Verification sequence

1. **Schema first.** Validate against the schema with `jsonschema` (Draft 2020-12) — not by eyeballing:
```python
from jsonschema import Draft202012Validator
errs = list(Draft202012Validator(schema).iter_errors(receipt))
```
Schema failure is not automatic rejection — classify it (missing field vs malformed state) and continue the audit; the verdict comes at the end.

2. **Anti-self-report battery** (each check cites the line that fails it):
   - Self-authored PASS: did the producer verify its own work with no external evidence? PASS claims need commands + output, not prose ("should work", "config live" = prose-as-proof).
   - Timestamp math: external verify-time minus publish-time < 60s → reject the verification, not the work (L4).
   - **File provenance** (standard since the M03 audit): compare claimed `executed_at`/`recorded_at` against the receipt file's mtime (`stat`), and against the timestamps of its own inputs — an execution that predates the queue decision that selected it is a hand-authored clock. Suspiciously round times (:00) deserve a second look.
   - **Artifact existence**: every external claim (page content, HTTP status, hash) must point at a stored artifact on disk (`receipts/p0pgr/artifacts/...`). Re-narrated page content without artifacts is prose-as-proof even when accurate — spot-check by refetching 1–2 claims yourself.
   - **Execution receipts** additionally validate against `p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json` (requires `founder_authorization_ref`, `evidence_artifacts`, machine `recorded_at`). Receipts predating that schema (2026-07-08) are judged against it advisorily, not retroactively rejected.
   - Evidence refs: do cited receipt paths/row IDs actually exist? Spot-check at least two.
   - Count/ID math: do row counts sum, are ID ranges contiguous, are gaps explained?
   - Fixed-claims: any wording that an audited issue "is fixed" without a repair receipt → violation; audits report, repairs are separate packets.
   - Verifier edits: if the diff touches a verifier or pass criterion → L5 hard stop, founder immediately.
   - Cost: cycle with LLM work but $0 metered, or cost with no value_class → L11 gap. (Deterministic script runs with zero LLM calls legitimately cost $0.)

3. **Quality-state legitimacy** (continuity law cuts both ways):
   - The nine states: PASS · PARTIAL · DEGRADED · SANDBOXED · PROVISIONAL · NEEDS_RETRY · NEEDS_REVIEW · FOUNDER_ONLY · HARD_BLOCK.
   - PARTIAL/DEGRADED/PROVISIONAL require the four labels: confidence, scope, reversibility, next_improvement. Present and specific? Good — that's the system being honest, not failing.
   - An inflated PASS that should have been PARTIAL is a bigger violation than the limitation itself. Check stated limitations against what the executor could actually do (e.g., a fetch tool that follows redirects cannot claim a redirects-OFF check).
   - HARD_BLOCK must cite one of the eight allowed reasons (destructive_action, production_deploy_without_authority, money_movement, legal_financial_commitment, credential_or_security_exposure, irreversible_external_send, authority_change, merge_L5_phase_unlock). Any other reason = malformed. A HARD_BLOCK that should have been a degrade = continuity violation — flag it.
   - Was the lane frozen? A rejected packet must have produced a repair candidate, not silence.

4. **Authority audit**: did the executor stay inside the packet's authority_scope and allowed_actions? Files changed outside the declared set, forms submitted, sends, deploys → authority violation regardless of how good the result is.

## Verdict (non-binary, always with reasons)

One of: `ACCEPTED` · `ACCEPTED_PROVISIONAL` (evidence adequate, limitations honestly labeled) · `REJECTED_SELF_PASS` · `REJECTED_NO_EVIDENCE` · `REJECTED_STALE` · `REJECTED_TIMESTAMP` · `REJECTED_AUTHORITY_VIOLATION` · `REJECTED_VERIFIER_EDIT`.

Every rejection routes back as a `repair` classification with a concrete next_pointer — the queue advances or repairs, it never just stops.

## Report format

VERDICT · SCHEMA · ANTI-SELF-REPORT FINDINGS (per check: pass/fail + evidence line) · QUALITY-STATE LEGITIMACY · AUTHORITY · NEXT_POINTER · STOP
