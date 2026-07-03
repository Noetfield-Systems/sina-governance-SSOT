# SG (SSSOT) — Cursor agent lane

**Agent:** `sg_sssot_cursor` · **Repo:** `~/Projects/sina-governance-ssot`  
**Registry:** `data/github_automation_registry_v1.json` · **Governance:** `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`  
**Autonomy loops:** `ssot/MACHINE_AUTONOMY_LOOPS_v1.md` · `data/machine_autonomy_loops_v1.json`

## Default operating mode

> **How does the process solve this without Sina?**

Do not route validation, review, repair, audit, or uncertainty to the founder. Use the eight loops (worker exec → machine valid → adversarial → self-repair → outside audit → deep research → receipt proof → earned autonomy). Founder triggers only: capital/legal, irreversible L5, phase unlock until receipt streaks retire them.

Cycle orchestrator: `python3 scripts/run_machine_autonomy_cycle_v1.py`

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

1. `skill-foundational-agentic-systems`
2. `governed-autorun`
3. `hub-pro-mac-session`
