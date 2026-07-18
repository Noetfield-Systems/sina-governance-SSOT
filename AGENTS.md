# SG (SSSOT) — Cursor agent lane

**Agent:** `sg_sssot_cursor` · **Repo:** `~/Projects/sina-governance-ssot`  
**Registry:** `data/github_automation_registry_v1.json` · **Alive docs:** `data/agent_read_surfaces_v1.json` · **Staleness gate:** `scripts/verify_agent_read_staleness_v1.sh` · **Governance:** `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`

## You edit (this repo)

- Governance registry, validators, independent-verify scripts
- Brain-loop launchd / GH Actions wiring
- SG guardrails, lock docs, automation surface inventory

## You do NOT edit (open correct venture chat)

| Venture | Workspace | Owner agent |
|---------|-----------|-------------|
| SourceA Brain / Worker | `~/Projects/SourceA` | `sourcea_brain` / `sourcea_worker` |
| TrustField loops | `~/Desktop/trustfield-loops` | `trustfield_worker` |
| NOOS doctrine | `~/Projects/noetfeld-os` | `noos_agent` |
| Noetfield website | `~/Desktop/Noetfield/.../Noetfield/` | `noetfield_website` |

## Mac founder session (INCIDENT-039)

- Max one light shell ≤90s per turn
- No validator marathons on Mac
- Proof: receipts in `receipts/` or `~/.sina/*-receipt*.json`

## Copilot / GitHub Agents

- Default lane: `assist_only` — draft PRs only
- Every PR: use `.github/pull_request_template.md` (motor_id + task_cell + lane)
- Never: autonomous promote, brain register without independent verify, cross-repo PR

## Skills (load at session start)

0c. **Architecture Finalization Gate + Unified Motor (LOCKED)** — `P8-MACHINE-LOOPS/ARCHITECTURE_FINALIZATION_GATE_LOCKED_v1.md` + `P0-FOUNDATION-SPINE/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCKED_v1.md` before redesigning Motors, resident owners, model routing, or sandbox authority

0d. **SinaGPT + Command Gateway v2 (LOCKED)** — `P1-CANON/SINAGPT_FOUNDER_BRAIN_ARCHITECT_LOCKED_v1.md` + `P0-FOUNDATION-SPINE/NF_COMMAND_GATEWAY_V2_ARCHITECTURE_LOCKED_v1.md` before cockpit/API redesign

0e. **Activation cycle + Higgsfield adapter (LOCKED)** — `docs/NF_ACTIVATION_CYCLE_V1_LOCKED.md` + `P0-FOUNDATION-SPINE/NF_HIGGSFIELD_MEDIA_ADAPTER_AND_RESULT_MOTOR_LOCKED_v1.md` before new lanes/roles/providers

0. **CHESS v2.0 (full package)** — `P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md` + templates + `SKILLS/SKILL_01`–`07` + `scripts/chess_pass_cli_v1.py`

1. `skill-foundational-agentic-systems`
2. `governed-autorun`
3. `hub-pro-mac-session`
4. `skills/pr-conflict-resolver` (in-repo, **LOCKED MANDATORY**) — use for any PR/branch merge conflict; encodes L1-L5 Scheduler and executor law and registry-JSON merge rules. Machine gate: `python3 scripts/verify_pr_conflict_skill_v1.py`. Eval app: `desktop-app/PR-Conflict-Resolver-Report.app`
5. `skills/staleness-gate-auditor` (in-repo) — run before trusting any "alive doc" as current; wraps `scripts/verify_agent_read_staleness_v1.sh`. Desktop app: `desktop-app/Staleness-Gate-Auditor.app`
6. `skills/receipt-ledger-auditor` (in-repo) — run after any multi-Scheduler and executor/multi-agent session to catch dual-claim collisions in `receipts/`; wraps `scripts/audit_receipt_ledger_v1.py`. Desktop app: `desktop-app/Receipt-Ledger-Auditor.app`
7. `skills/registry-Scheduler and executor-validator` (in-repo) — run before registering any new GH Action/worker/Copilot workflow, or after touching `data/github_automation_registry_v1.json`; wraps `scripts/validate_parallel_automation_governance_v1.py` + `scripts/audit_automation_surface_v1.py`. Desktop app: `desktop-app/Registry-Scheduler and executor-Validator.app`
