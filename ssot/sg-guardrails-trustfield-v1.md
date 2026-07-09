# SG Guardrails — TrustField + Signal Factory v1

**Status:** LOCKED — append-only; Sina approves wording changes.  
**Saved:** 2026-07-02  
**Mirror of:** `~/.cursor/skills/signal-factory/references/sg-guardrails-v1.md`  
**Parent lock:** [../docs/TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md](../docs/TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md)  
**Iteration 2:** [../docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md](../docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md)

SG owns guardrail wording. SourceA owns skill execution. NOOS owns routing doctrine (separate file TARGET).

## Five guardrails (locked 2026-07-02)

1. **Regulated claims — TrustField.** TrustField must not claim or imply custody, settlement, MSB, PSP, or banking capability unless legally established. Inbound signals touching these topics route to Sina/legal regardless of score.

2. **Entity boundaries.** Six entities remain separate in all receipts, memory lines, and generated service patterns: Noetfield, TrustField, SourceA, WitnessBC, SG, NOOS. No cross-attribution.

3. **Partner/equity signals.** Partner or equity milestone signals produce a bounded exploratory next action only. No commitment language auto-generated.

4. **No-employment constraint.** Applies to all generated outreach and service patterns. No job-offer or employment implication.

5. **Claim ladder.** Externally-facing text the skill generates must respect VERIFIED / DECLARED / PLANNED classes. Do not upgrade claim class without evidence.

## Architecture §21 cross-reference (TrustField autorun)

- Regulated-term hard-stop list (§11.1) is automatic risk-5 boundary; changes require SG sign-off (**B2**).
- All sender claims are `sender_declared`; no TrustField output restates them as fact.
- During formation, commercial support flows through Noetfield Systems Inc.; cost events tagged `entity: trustfield`.
- No external message leaves any TrustField loop without human approval in v1.
- Reliability/uptime claims on trustfield.ca remain PLANNED/DECLARED until T6 evidence exists.
