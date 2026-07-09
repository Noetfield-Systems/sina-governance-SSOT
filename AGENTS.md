# SG (SSSOT) — Cursor agent lane

**Agent:** `sg_sssot_cursor` · **Repo:** `~/Projects/sina-governance-ssot`  
**Registry:** `data/github_automation_registry_v1.json` · **Governance:** `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`  
**Autonomy loops:** `ssot/MACHINE_AUTONOMY_LOOPS_v1.md` · `data/machine_autonomy_loops_v1.json`  
**Founder canon:** `ssot/FOUNDER_CANON_v1.md` · `data/founder_canon_v1.json` (ACTIVE)
**Structure/version authority:** `ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md` (ACTIVE)  
**SG guard model:** SG registry = authority; library = asset surface; file existence = zero authority. Dispatch: Tier 0 + role + mission + gates only (`ssot/AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE_SSOT_LOCKED_v1.md`).
**Governance intelligence pipeline:** `ssot/GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md` · `data/governance_artifact_registry_v1.json` · `data/governance_review_queue_v1.json` · `scripts/governance_intelligence_engine_v1.py`
**L0 repo graph memory (read before broad reads):** `graph-out/GRAPH_REPORT.md` · query: `python3 scripts/query_repo_graph_v1.py <term>` · design: `docs/L0_REPO_GRAPH_MEMORY_v1.md`

## Default operating mode

> **How does the process solve this without Sina?**

**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = `BLOCKED_WITH_REASON`.

Do not route validation, review, repair, audit, or uncertainty to the founder. Use the eight loops (worker exec → machine valid → adversarial → self-repair → outside audit → deep research → receipt proof → earned autonomy). Founder triggers only: capital/legal, irreversible L5, phase unlock until receipt streaks retire them.

Version law: existing rules stay live; newer versions are amendments and win only on direct conflict. `superseded` means not active for decisions and must not be used for a live base rule.

Cycle orchestrator: `python3 scripts/run_machine_autonomy_cycle_v1.py`

**Integrator (NOOS):** if you mutate integrator state in `noetfeld-os`, run `python3 scripts/noos_integrator_sync_v1.py sync` before session exit. See `ssot/NOOS_INTEGRATOR_RULES_v1.md`.

## L0 repo graph memory — broad-read gate

Do not spawn a broad "understand the repo", "map subsystem X", "architecture
review", or "audit Y" task (multi-agent or single-agent) by reading files
directly as the first step. First read `graph-out/GRAPH_REPORT.md` (compact
subsystem map, ~6KB) and, for anything it doesn't answer, run
`python3 scripts/query_repo_graph_v1.py <subsystem-or-keyword>` (bounded output,
no full file reads). Only open — or delegate reading of — the specific files the
graph names as relevant. Token budget: the orientation step (the report plus a
few targeted queries) should cost roughly 2k-6k tokens, not the ~371k a prior
blind multi-agent understand pass cost. If the graph is missing or stale for what you need,
rebuild it first with `python3 scripts/build_repo_graph_v1.py` rather than
falling back to a blind repo-wide read. Full rationale and rollout plan:
`docs/L0_REPO_GRAPH_MEMORY_v1.md`.

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
