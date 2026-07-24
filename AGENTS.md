# SG (SSSOT) — Cursor agent lane

**Agent:** `sg_sssot_cursor` · **Repo:** `~/Desktop/Noetfield-Systems/sina-governance-SSOT`  
**Registry:** `data/github_automation_registry_v1.json` · **Alive docs:** `data/agent_read_surfaces_v1.json` · **Staleness gate:** `scripts/verify_agent_read_staleness_v1.sh` · **Governance:** `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`

**L0 repo graph memory (read before broad reads):** `graph-out/GRAPH_REPORT.md` · query: `python3 scripts/query_repo_graph_v1.py <term>` · design: `docs/L0_REPO_GRAPH_MEMORY_v1.md`

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
| SourceA Brain / Worker | `~/Desktop/Noetfield-Systems/SourceA` | `sourcea_brain` / `sourcea_worker` |
| TrustField loops | `~/Desktop/trustfield-loops` | `trustfield_worker` |
| NOOS doctrine | `~/Desktop/Noetfield-Systems/noetfeld-OS` | `noos_agent` |
| Noetfield website | `~/Desktop/Noetfield-Systems/Noetfield/` | `noetfield_website` |

## Mac founder session (INCIDENT-039)

- Max one light shell ≤90s per turn
- No validator marathons on Mac
- Proof: receipts in `receipts/` or `~/.sina/*-receipt*.json`

## Copilot / GitHub Agents

- Default lane: `assist_only` — draft PRs only
- Every PR: use `.github/pull_request_template.md` (motor_id + task_cell + lane)
- Never: autonomous promote, brain register without independent verify, cross-repo PR

## P0 runtime containment (read before architecture claims)

`data/runtime_reality_v1.json` has precedence over architecture prose for current deployment, commissioning, ACTIVE, and authority status. Current incident: `SG-AUTHORITY-IDENTITY-P0`.

- `noetfield-motor` = proven executor identity; not SG; not commissioned Unified Motor Core.
- legacy app `4179901` / installation `143449507` and `REMOTE_CHECK_ADVISORY` are forbidden authority sources.
- Autonomous production mutation is HOLD until exact fresh signed permits from commissioned `noetfield-sg-authority` exist.
- Architecture accepted ≠ implemented ≠ deployed ≠ proven ≠ commissioned ≠ active.
- Agents may observe, test, propose, and open draft PRs; they may not lift HOLD, deploy, promote, mutate secrets/authority/verifiers, or revoke legacy identity under containment.

## Founder gates — closed set, no invented gates (LAW)

`ssot/FOUNDER_GATE_SCOPE_v1.md` · checker: `python3 scripts/verify_founder_gate_scope_v1.py`

- The founder is interrupted ONLY for the eight reasons in the closed set (destructive ops, unauthorized prod deploy, money, legal, credentials, irreversible external sends, authority-plane changes, merge/L5/phase-unlock). Runtime contract: a block without one of these reasons is **malformed**.
- Before raising ANY founder decision, run the checker. If the SSOT answers it, a test answers it, a default exists, it's reversible, or it can run as a bounded experiment → it is a MACHINE decision: act on the default and write a receipt. Do not ask.
- Fixing, wiring, and commissioning work inside an accepted plan is machine work. Never re-gate it. Committing ordered, verified work into the SSOT is recording, not merge authority — do it immediately after verification (uncommitted work gets swept by hygiene loops), receipt it, don't ask.
- Founder-facing text must be plain language: what happened, 2-3 options, one recommendation, why in ≤3 lines, consequence of no decision. No unexplained jargon, no codenames, and never hand the founder commands to run.

## Skills (load at session start)

0c. **Architecture Finalization Gate + Unified Motor (LOCKED)** — `P8-MACHINE-LOOPS/ARCHITECTURE_FINALIZATION_GATE_LOCKED_v1.md` + `P0-FOUNDATION-SPINE/NF_UNIFIED_MOTOR_ARCHITECTURE_LOCKED_v1.md` before redesigning Motors, resident owners, model routing, or sandbox authority. Scaling posture: Cloudflare Agents+Workflows only; no Temporal/Kafka+Flink/Ray/Restate substrate; W5 provider hardening deferred; HOLD preserved

0d. **SinaGPT + Command Gateway v2 (LOCKED)** — `P1-CANON/SINAGPT_FOUNDER_BRAIN_ARCHITECT_LOCKED_v1.md` + `P0-FOUNDATION-SPINE/NF_COMMAND_GATEWAY_V2_ARCHITECTURE_LOCKED_v1.md` before cockpit/API redesign

0e. **Activation cycle + Higgsfield adapter (LOCKED)** — `docs/NF_ACTIVATION_CYCLE_V1_LOCKED.md` + `P0-FOUNDATION-SPINE/NF_HIGGSFIELD_MEDIA_ADAPTER_AND_RESULT_MOTOR_LOCKED_v1.md` before new lanes/roles/providers
0f. **Noetfield Runway product (LOCKED)** — `P10-PRODUCT-LAYERS/NF_NOETFIELD_RUNWAY_PRODUCT_LOCKED_v1.md` before selling Motor/governance; parallel Video/Software Repair/Research; one Job↔one isolated sandbox; Gateway ≠ Motor
0g. **Runway execution assignment (LOCKED)** — `P10-PRODUCT-LAYERS/NF_RUNWAY_EXECUTION_ASSIGNMENT_LOCKED_v1.md` + `data/nf_runway_execution_assignment_v1_LOCKED.json`: Claude Code=foundation/Repair; Codex Local=Research impl; Cursor=Video; GPT work verifier on GitHub=Research commissioning; Codex Cloud=separate cloud worker; GPT Advisor=advice only; institutional owners remain Builder/Verifier

0h. **compute / ROI allocation (LOCKED)** — read `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_COMPUTE_ROI_ALLOCATION_LOCKED_v1.md` and `data/nf_compute_roi_allocation_v1_LOCKED.json` before changing Actions minute spend, Cloudflare hot path, Railway heavy jobs, or kernel llm matrix. enterprise plan kept; classes A-D on 50k minutes; wake = authenticated HTTP `job_id` only; HOLD preserved

0i. **Company New (LOCKED)** — read `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/NF_COMPANY_NEW_PRODUCT_LOCKED_v1.md` and `data/nf_company_new_product_v1_LOCKED.json` before changing `/new`, recipes (marketing_site / deterministic_api / crud_saas), T0–T3 dispatch for Company New, or CF Pages `nf-company-new`; Polsia UX benchmark only; HOLD preserved
0j. **governed work packet control (LOCKED)** — read `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_GOVERNED_WORK_PACKET_CONTROL_LOCKED_v1.md` and `data/nf_governed_work_packet_control_v1_LOCKED.json` before changing Goal Contracts, Human Tax meters, work-packet terminals, or circuit breakers on SourceA / Motor / Runway; SAME_PLAN_HASH cannot resume after incident; learning via Motor Learning Organ only

0. **CHESS v2.0 (full package)** — `P0-DOCTRINE/CHESS_PATTERN_REASONING_MACHINE_v2.0.md` + templates + `SKILLS/SKILL_01`–`07` + `scripts/chess_pass_cli_v1.py`

1. `skill-foundational-agentic-systems`
2. `governed-autorun`
3. `hub-pro-mac-session`
4. `skills/pr-conflict-resolver` (in-repo, **LOCKED MANDATORY**) — use for any PR/branch merge conflict; encodes L1-L5 Scheduler and executor law and registry-JSON merge rules. Machine gate: `python3 scripts/verify_pr_conflict_skill_v1.py`. Eval app: `desktop-app/PR-Conflict-Resolver-Report.app`
5. `skills/staleness-gate-auditor` (in-repo) — run before trusting any "alive doc" as current; wraps `scripts/verify_agent_read_staleness_v1.sh`. Desktop app: `desktop-app/Staleness-Gate-Auditor.app`
6. `skills/receipt-ledger-auditor` (in-repo) — run after any multi-Scheduler and executor/multi-agent session to catch dual-claim collisions in `receipts/`; wraps `scripts/audit_receipt_ledger_v1.py`. Desktop app: `desktop-app/Receipt-Ledger-Auditor.app`
7. `skills/registry-Scheduler and executor-validator` (in-repo) — run before registering any new GH Action/worker/Copilot workflow, or after touching `data/github_automation_registry_v1.json`; wraps `scripts/validate_parallel_automation_governance_v1.py` + `scripts/audit_automation_surface_v1.py`. Desktop app: `desktop-app/Registry-Scheduler and executor-Validator.app`

8. `skills/commissioning-specialist` — 5-min CF cron commissioning closed loop (heal allowlist + kaizen propose; DeepSeek/GLM/Kimi/HF)

9. **Daily cost sentinel (doctrine #133)** — `python3 scripts/daily_cost_sentinel_v1.py` once per session/day; sums real spend from the unified receipt corpus, tracks month-to-date vs the $1,500 founder cap (exit 2 = over cap), writes `receipts/cost/` + `docs/DAILY_COST_SENTINEL_LATEST.md`. Metering coverage % is the honest blindness measure; upstream token metering (#107, motor repo) is the keystone that makes it non-zero.
