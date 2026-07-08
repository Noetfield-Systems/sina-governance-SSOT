# INSTALL_PROMPT_FOR_SG_AGENT

```text
Install CHESS_PATTERN_REASONING_MACHINE_v2.0.

This is not a blocker rule.
This is a reasoning machine for agents.

Goal:
Agents forecast possible next moves, patch risky instructions, then proceed with the improved move.

Create/commit these package files:

1. P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md
2. P0-TEMPLATES/CHESS_PASS_PROMPT_TEMPLATE_v2.0.md
3. P0-TEMPLATES/AGENT_EXECUTION_CONTRACT_TEMPLATE_v2.0.md
4. P0-TEMPLATES/RECEIPT_TEMPLATE_CHESS_PASS_v2.0.md
5. P7-OVERLAYS/TRUSTFIELD_PARTNER_ACCESS_CHESS_OVERLAY_v2.0.md
6. SKILLS/SKILL_01_CHESS_PASS.md
7. SKILLS/SKILL_02_FEATURE_PARITY_LEDGER.md
8. SKILLS/SKILL_03_PROMPT_PATCHER.md
9. SKILLS/SKILL_04_LIVE_TRUTH_VERIFIER.md
10. SKILLS/SKILL_05_RESTORE_PLAYBOOK.md
11. SKILLS/SKILL_06_COMMERCIAL_CONSEQUENCE_SIMULATOR.md
12. SKILLS/SKILL_07_NON_BLOCKING_DECISION_ROUTER.md
13. SCHEMAS/chess_pass.schema.json
14. SCHEMAS/protected_feature_ledger.schema.json
15. SCHEMAS/chess_receipt.schema.json
16. PLAYBOOKS/TRUSTFIELD_PARTNER_ACCESS_RESTORE_PLAYBOOK_v2.0.md
17. PLAYBOOKS/LIVE_SITE_CHANGE_PLAYBOOK_v2.0.md
18. PLAYBOOKS/DEPLOY_DRIFT_PLAYBOOK_v2.0.md

Core rule:
Forecast → Patch → Proceed → Verify.

Allowed action labels:
- PROCEED
- PROCEED_WITH_PATCH
- ASK_IF_IRREVERSIBLE

Do not add BLOCK.

Ask founder only for irreversible actions:
- deleting working features
- exposing private material
- changing equity/control terms
- making legal/regulatory claims
- signing/sending binding commitments
- spending material money
- destructive migrations

Wire into:
- Architect prompts
- SourceA worker prompts
- TrustField worker prompts
- UX prompts
- deploy prompts
- restore prompts
- commercial launch prompts

TrustField overlay must protect:
- Request Partner Access
- Partner Access Platform
- Sign in
- Create account
- Enter Partner Access Platform
- View application status
- three tracks
- apply routes/forms
- NDA gating
- briefing-room gating
- scoring
- admin review
- status machine
- e-sign metadata
- health monitor
- boundary copy

Forbidden interpretation:
Words like clean, minimal, simplify, polish, streamline, or remove clutter do not authorize feature deletion.

Receipt:
CHESS_PATTERN_REASONING_MACHINE_v2_INSTALL_RECEIPT

Receipt must prove:
- files created
- templates installed
- TrustField overlay installed
- references wired
- no blocker/fail-closed language introduced
```
