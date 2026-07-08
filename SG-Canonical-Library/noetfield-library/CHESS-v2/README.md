# CHESS_PATTERN_REASONING_MACHINE_v2.0_PACKAGE

**Purpose:** Practical, non-blocking reasoning package for machine-agents.

This package turns "chess thinking" into reusable artifacts, docs, schemas, skills, checklists, and receipts.

Core operating loop:

```text
Forecast → Patch → Proceed → Verify
```

This is **not** a blocker.  
It is a move-improvement engine.

## Package contents

```text
P0-DOCTRINE/
  CHESS_PATTERN_REASONING_MACHINE_v2.0.md

P0-TEMPLATES/
  CHESS_PASS_PROMPT_TEMPLATE_v2.0.md
  AGENT_EXECUTION_CONTRACT_TEMPLATE_v2.0.md
  RECEIPT_TEMPLATE_CHESS_PASS_v2.0.md

P7-OVERLAYS/
  TRUSTFIELD_PARTNER_ACCESS_CHESS_OVERLAY_v2.0.md

SKILLS/
  SKILL_01_CHESS_PASS.md
  SKILL_02_FEATURE_PARITY_LEDGER.md
  SKILL_03_PROMPT_PATCHER.md
  SKILL_04_LIVE_TRUTH_VERIFIER.md
  SKILL_05_RESTORE_PLAYBOOK.md
  SKILL_06_COMMERCIAL_CONSEQUENCE_SIMULATOR.md
  SKILL_07_NON_BLOCKING_DECISION_ROUTER.md

SCHEMAS/
  chess_pass.schema.json
  protected_feature_ledger.schema.json
  chess_receipt.schema.json

PLAYBOOKS/
  TRUSTFIELD_PARTNER_ACCESS_RESTORE_PLAYBOOK_v2.0.md
  LIVE_SITE_CHANGE_PLAYBOOK_v2.0.md
  DEPLOY_DRIFT_PLAYBOOK_v2.0.md

EXAMPLES/
  trustfield_partner_access_minimal_header_incident.md
  sample_chess_pass.json
  raw_to_patched_prompt_examples.md

TOOLS/
  chess_pass_cli.py
  README.md

INSTALL/
  INSTALL_PROMPT_FOR_SG_AGENT.md
  WIRING_CHECKLIST.md
```

## Install philosophy

Do not install as another fail-closed gate.

Install as a **small internal reasoning pass** inside agents:

1. read the board
2. forecast next two moves
3. detect hidden downgrade/misread risks
4. patch the move
5. proceed if reversible
6. ask only if irreversible
7. verify live result
