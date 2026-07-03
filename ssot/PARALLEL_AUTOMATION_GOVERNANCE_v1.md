# Parallel Automation Governance v1

**Status:** LOCKED — 2026-07-03  
**Authority:** SG (SSSOT)  
**Parent:** [MULTI_REPO_WORKER_REGISTRY_v1.md](MULTI_REPO_WORKER_REGISTRY_v1.md)  
**Registry:** [data/github_automation_registry_v1.json](../data/github_automation_registry_v1.json)

---

## 0. One line

**Living system = many motors in parallel, one writer per task cell.** GitHub Actions, Copilot, Coding Agents, Cloudflare crons, Mac launchd, and Cursor venture workers each own a **registered lane**. Unregistered automation is a defect. Parallel is allowed; **duplicate authority is not**.

---

## 1. Why this exists

You are activating **GitHub Agents**, **GitHub Actions**, and **Copilot workflows** alongside:

- SourceA Brain · SourceA Worker · SourceA Loop Specialist  
- TrustField Worker · NOOS · Noetfield website  
- SG verifier · promotion gate · registries  

Without lane law, the failure mode is familiar: **two motors promote the same artifact**, Copilot opens a PR that conflicts with TrustField Worker, Actions deploy while Mac autorun also deploys, or an agent registers a brain artifact without independent verify.

This governance **does not slow parallel work** — it **names owners** so every side can run at once without stepping on the same cell.

---

## 2. The five laws

### L1 — One writer per task cell

Same task + same artifact + same window → **exactly one** registered motor may mutate state. Others may **read**, **observe**, or **propose** (PR/draft). Second writer → `REJECTED` receipt, not silent overwrite.

*Maps to governed-autorun D2 (single writer) and brain promotion gate CAS.*

### L2 — Lane declaration before action

Every actor states lane **before** editing:

```text
lane: <sg_governance | sourcea_brain | sourcea_build | trustfield_build | noos_doctrine | noetfield_website | assist_only>
motor_id: <registered id or human_gate>
receipt_id: <if claiming done>
```

GitHub PRs from Copilot/Coding Agents **must** include `lane:` and `motor_id_or_human_gate:` in body. Missing = do not merge without human review.

### L3 — Assist ≠ authority

| Class | May do | May never do |
|-------|--------|--------------|
| **GitHub Copilot / Coding Agent** | Draft PR, suggest patch, triage issue | Promote brain, deploy prod, register artifacts, append SG/NOOS canonical, external send |
| **GitHub Actions** | Run **registered** workflow steps, upload receipts | Build venture code outside workflow scope, bypass promotion gate |
| **Cursor venture Worker** | Build in **own repo only** | Edit other venture repos, change SG registry without SG chat |

### L4 — Registry is routing truth

`data/github_automation_registry_v1.json` + `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md` define who owns what. If Copilot adds a workflow that duplicates a registered motor → **defect** — register it or delete it.

### L5 — Receipt or unverified

No motor reports DONE without `receipt_id`. Agent summaries without receipts are **claims**, not proof (same law as Brain B-04).

---

## 3. Motor map (parallel, non-overlapping writes)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SG (SSSOT) — routing only                        │
│  registries · verifier · gates · mirrors · validate scripts              │
└────────────┬────────────────────────────────────────────────────────────┘
             │ registers / verifies
    ┌────────┴────────┬─────────────────┬──────────────────┐
    ▼                 ▼                 ▼                  ▼
 GH Actions      Mac launchd       CF Loop Spec      CF auto-runtime
 (24/7 CI)       (Mac complement)   (plans)           (forge queue)
    │                 │                 │                  │
    └────────┬────────┘                 │                  │
             ▼                           │                  │
      SourceA Brain ◄────────────────────┴──────────────────┘
      (register · route · bundle)
             │
    ┌────────┼────────┬──────────────┬─────────────┐
    ▼        ▼        ▼              ▼             ▼
 SA Worker  TF Worker  NOOS agent   NF website   Copilot/Agents
 (SA build) (TF loops) (doctrine)   (www)        (assist PRs only)
```

**Parallel OK:** TF Worker builds Phase 2 while SourceA Brain does B-01/B-02 while NOOS appends doctrine while GH Actions runs observe tick — **different task cells**.

**Conflict NOT OK:** GH Actions promote + Mac autorun promote **same sandbox same window** without gate CAS.

---

## 4. Task cell ownership (quick reference)

| Task | Sole write owner | GH Actions | Copilot/Agents |
|------|------------------|------------|----------------|
| `trustfield-loops` build/deploy | TrustField Worker | ❌ | PR suggest only |
| SourceA worker deploy | SourceA Worker | ❌ | PR suggest only |
| Brain artifact register (B-04) | SourceA Brain via SG script | ❌ | ❌ |
| Brain promote | `gh_actions_*` OR `mac_launchd_*` (gate CAS) | ✅ registered | ❌ |
| Verifier `/run` | SG secondary CF | trigger only if in workflow | ❌ |
| Loop runtime plans | Loop Specialist tick | ❌ | ❌ |
| SG guardrail append | SG + Sina | ❌ | ❌ |
| NOOS doctrine append | NOOS → `noetfeld-os` | ❌ | ❌ |
| Noetfield www deploy | Noetfield website agent | ❌ | PR suggest only |
| Signal Factory package | SourceA Worker | ❌ | PR suggest only |
| E2E matrix | `validate_*` scripts (any runner) | ✅ observe | ❌ |

Full machine list: `task_cell_owners` in registry JSON.

---

## 5. GitHub Actions rules

### Registered workflows (SG repo)

| Workflow | Motor ID | Scope |
|----------|----------|-------|
| `brain-loop-autorun-v1.yml` | `gh_actions_brain_loop_autorun_v1` | Self-heal · parallel batch · matrix · promote **only if** tokens + `BRAIN_CI_AUTONOMOUS` |

### Adding a new workflow (required checklist)

1. Pick `motor_id` — must not duplicate `owns` of existing motor  
2. Append row to `github_automation_registry_v1.json`  
3. Set `must_not_own` explicitly  
4. Run `validate_parallel_automation_governance_v1.py`  
5. SG commit + receipt  

### Forbidden in Actions (unless new motor registered + approved)

- Deploy `trustfield-loops` to prod trustfield.ca  
- Write to `noetfeld-os/docs/_NOOS_AGENT/`  
- Call `brain_register_*` without human dispatch  
- Auto-merge to `main` on SourceA / Noetfield / trustfield-loops without promotion gate  

---

## 6. GitHub Copilot & Coding Agents rules

### Default posture: **assist_only**

Copilot and GitHub Coding Agents operate in **`assist_only`** lane unless PR explicitly names a venture worker lane and human gate.

### PR template (required for agent-opened PRs)

```markdown
## Lane declaration
lane: assist_only | sourcea_build | trustfield_build | ...
motor_id_or_human_gate: gh_copilot_draft | G6_sina_approve | ...

## Scope
- Repo: 
- Task cell: (from registry task_cell_owners)

## Proof
receipt_id: (or "human merge only — no autorun claim")
```

### Copilot workflow constraints

| Rule | Reason |
|------|--------|
| No workflow cron duplicating `brain-loop-autorun` promote path | Double promote |
| No workflow that commits to multiple venture repos in one job | Mixed-scope defect |
| No scheduled TF triage until B2 signed | SG blocker |
| Suggestions may not edit `data/brain_external_artifact_registry_v1.json` without Brain lane | Registration authority |

### When Copilot **helps** (parallel, safe)

- Draft tests in `trustfield-loops` for TrustField Worker to review  
- Explain diff on SourceA PR  
- Open **draft** PR with lane header for SourceA Worker  
- Run **read-only** CI (lint, unit tests) on feature branches  

---

## 7. Coordination with live workers (no duplication)

| Live worker | Runs in | Do not duplicate with |
|-------------|---------|---------------------|
| SourceA Brain | SourceA + CF brain worker | Copilot editing bundle; second register path |
| SourceA Worker | SourceA | Copilot merging SA deploy without Worker review |
| Loop Specialist | CF `*/15` tick | GH Action spawning duplicate plan jobs |
| TrustField Worker | trustfield-loops | SourceA Worker; Copilot direct merge to TF main |
| NOOS agent | noetfeld-os | SG mirror as canonical; Noetfield website for GEL |
| Noetfield website | Noetfield repo | NOOS for Vercel/www |
| SG (this chat) | sina-governance-ssot | Any venture building product code |

---

## 8. Conflict resolution

| Situation | Winner |
|-----------|--------|
| Registry vs agent claim | Registry |
| SG guardrail vs SourceA pattern advice | SG |
| Independent verifier FAIL vs builder PASS | Verifier (FAIL) |
| Two motors same cell | First CAS wins; second REJECTED |
| Copilot PR vs locked Worker order | Worker order + human gate |
| Correlated agreement (all agents agree) | Stress-test — log objection or "none found" |

---

## 9. Monthly audit (TARGET — 15 min)

```bash
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/validate_parallel_automation_governance_v1.py
# List workflows in each org repo — compare to registry
# Kill unregistered crons (NOOS doctrine line 7)
```

Receipt: `receipts/parallel-automation-audit-<timestamp>.json`

---

## 10. Proof commands

```bash
# Governance validator
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/validate_parallel_automation_governance_v1.py

# Worker registry
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/validate_brain_domain_registry_v1.py

# Multi-repo map
cat ~/Projects/sina-governance-ssot/ssot/MULTI_REPO_WORKER_REGISTRY_v1.md
```

Pass line: `validate_parallel_automation_governance_v1: ALL PASS`

---

## 11. Activation checklist (GitHub Agents + Actions + Copilot)

- [ ] All existing workflows registered in `github_automation_registry_v1.json`  
- [ ] Copilot PR template adopted in org (or per-repo `.github/pull_request_template.md`)  
- [ ] No new workflow cron without `motor_id` row  
- [ ] Venture repos have `AGENTS.md` or rules pointing to lane declaration  
- [ ] `assist_only` default communicated to all Copilot workflows  
- [ ] First monthly audit receipt filed  

---

*v1.0 — 2026-07-03 — SG parallel living-system governance for GitHub automation layer.*
