# LINE ENGINE — RECEIPTS & NEGATIVE PROOF
Every stage emits a receipt (fixed fields, no narrative): task_id/branch/commits/files_changed/commands_run/test_result(external URL)/evidence(count in==out)/cost/value_class/state/next_action. Receipt lives in-repo (never home dirs/session storage).
**Negative proof:** each gate proven by a deliberately-failing input it rejects, on disposable `gate-test/*` branches, captured as a rejection receipt. Unproven gate = FAIL. Receipts>diagrams; PASS only from external verifier, never agent self-report.
Full doctrine: `02-DOCTRINE/negative-proof.md`, `02-DOCTRINE/receipts-not-diagrams.md`.
*v0.1 (2026-07-03 12:34 PDT) — receipts + negative-proof for the line/IDE lane.*
