# SG Guardrails — Signal Factory Iteration 2

**Status:** LOCKED — append-only; Sina approves wording changes.  
**Saved:** 2026-07-03  
**Parent lock:** [../docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md](../docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md)

SG records guardrails only. SourceA owns skill execution and build. NOOS is not primary for Signal Factory.

## Guardrails (Iteration 2)

1. **Ownership.** Signal Factory belongs to SourceA/Base Brain. SG records guardrails; does not build skill logic.

2. **Sender claims.** Inbound assertions are `sender_declared` unless independently verified. Never launder as facts.

3. **Risk routing.** `risk_score >= 4` → `decision = route` → Sina/legal/human review. Optional sections suppressed.

4. **TrustField regulated inbound.** Custody, settlement, MSB, PSP, banking, or regulated-finance signals must route — never auto-reply.

5. **PartnerMesh.** Partner/advisor/founder-track intake only — not employment or unpaid hiring. Bounded milestone before equity; written agreement before contribution.

6. **Optional sections.** `AUTOMATION RECIPE` and `COMMERCIAL IDEA` only when `decision = build_automation` or `create_service_pattern`. No score-threshold gate.

7. **Entity boundaries.** Noetfield · TrustField · SourceA · WitnessBC · SG · NOOS remain separate in receipts and memory lines.

8. **Production scope.** No Gmail, LinkedIn, website forms, UI, or live automation in v1 Iteration 2 build. `production_connected` must stay `false`.

9. **Claim ladder.** Externally-facing generated text: VERIFIED / DECLARED / PLANNED only.

10. **Market telemetry.** Inbound noise is signal to mine — not trash by default — but vendor claims are never trusted without verification.
