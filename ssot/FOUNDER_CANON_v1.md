# Founder Canon v1

**Version:** 1.0.0 · **Status:** ACTIVE  
**Activated:** 2026-07-03 (founder-directed E2E commit to SG)  
**Authority:** SG (SSSOT) — one canon, no competing mini-constitutions  
**Machine implementation:** [MACHINE_AUTONOMY_LOOPS_v1.md](MACHINE_AUTONOMY_LOOPS_v1.md)  
**Registry:** [data/founder_canon_v1.json](../data/founder_canon_v1.json)

**Doctrine pointers (authoritative — never restated here):** governed-autorun v3 (L1–L13) · deterministic-loops (D1–D8) · autorun-cycle-receipt-v2 · WORK_ORDER_GOVERNED_IDE_LANE_v1 (G1–G8)

**Applies to:** every actor — founder-side advisors, architects, IDE agents, sandbox workers, verifiers.

---

## 1. Goal

Reduce Sina's manual work toward **zero-founder operational validation**.

The system is not "agents run, then founder validates." The system validates itself: machine and agentic loops carry detection, critique, audit, repair, and validation. The founder is not the QA department, not the runtime, not the escalation inbox.

## 2. North star

Sandbox-first autonomy · walls at the boundary, freedom inside · machine/agentic validation · self-growth · self-healing · adversarial critique · outside audit/advisory loops when useful · deterministic autorun earned step by step.

## 3. Intent filter

Test every proposed rule, gate, or process:

| ID | Question |
|----|----------|
| Q1 | Does it reduce Sina's future workload — or make Sina the runtime? |
| Q2 | Does it replace founder judgment with machine/agentic validation? |
| Q3 | Is it a boundary wall (fires on escape) — or a permission loop (fires on normal work)? |
| Q4 | On leak/break/failure, does it route to repair/critique/audit/research loops — or back to Sina? |
| Q5 | Does it keep targets as targets — or freeze them into blockers? |

Founder-as-validator / permission loop / Sina-as-runtime / frozen target → **redesign or drop.**

## 4. Authority

Founder goals, roadmaps, todos, and north-star language grant **zero execution authority**. Authority flows only through: committed canon → signed work order → dispatch. Agents produce evidence; they never produce approvals, sign-offs, status promotions, or ledger entries. Missing authority → `BLOCKED_WITH_REASON` into the machine loop (§6), never improvisation.

*(Incident basis: forged L5 sign-off, 2026-07-03.)*

## 5. Operating model

**Autonomy inside sandbox. Hard walls at boundary. Receipt at exit.**

Inside a dispatched lane: read, edit allowed paths, run allowlisted commands, test, self-repair within budget, commit enumerated work, receipt, stop — zero mid-cycle permission requests.

Walls (mechanical, per G1–G8): main writes, governance/SSOT/ledger writes, approval language, token handling, hidden state, global installs, deploys, destructive git, out-of-scope files.

## 6. Failures route to machines, not to Sina

Default response:

```text
detect → contain → critique → audit → deep-research if needed → repair → validate → receipt → continue or escalate by policy
```

Implemented by [MACHINE_AUTONOMY_LOOPS_v1.md](MACHINE_AUTONOMY_LOOPS_v1.md) loops L1–L8. Orchestrator: `scripts/run_machine_autonomy_cycle_v1.py`.

Escalation targets are machine/agentic first: adversarial critic, independent verifier, outside audit. A failure reaches Sina only when policy says it must (§8) — with a receipt explaining why the machine loop could not close it.

## 7. Validation is earned autonomy

Every validation duty on the founder is a migration target. Ladder: manual dispatch → mechanical gates → sandboxed cycles → machine-validated receipts → external verifiers → adversarial loops → consecutive clean windows → limited autonomy → deterministic autorun.

Steps unlock on **receipts**, never on ambition. Once machine-safe, keeping validation on the founder is a canon violation (Q2).

## 8. Founder touchpoints — bootstrap exceptions

Exactly four until retired by receipt streak:

| ID | Class | Retire when |
|----|-------|-------------|
| FT-CAPITAL | Capital / spend beyond caps | ROI heartbeat + 30d under cap |
| FT-LEGAL | Contracts, regulated actions | 8× trap PASS + signed JSON |
| FT-L5-IRREVERSIBLE | Weakening verifier, gate, law, schema | Never auto-retire |
| FT-PHASE-UNLOCK | New autonomy tier | 5× hygiene or 8× promote streak |

Everything else — merge included once machine validation covers it — migrates off the founder.

## 9. Truth and memory

Live source beats memory, summary, or compaction. Order: current SSOT file → current repo state → current dispatch → current receipt → prior chat. All state in-repo; hidden state is a wall violation. One canon per domain, extended by versioned pointer, never restated.

**NOOS integrator:** repo-local runtime state beats home mirror (`~/.sina/noos-integrator-state-v1.json`) and cloud mirror unless promoted. See [NOOS_INTEGRATOR_RULES_v1.md](NOOS_INTEGRATOR_RULES_v1.md).

## 10. Violation law

Boundary violation → machine loop first: contain, receipt, critique, repair (§6). Escalates to founder only per §8. Repeat scope/authority violations retire the session/tool. Never hide, rewrite history, or continue silently.

---

## Dispatch line (required)

```text
LAWS: FOUNDER_CANON v1 + governed-autorun v3. Violations = BLOCKED_WITH_REASON.
```

Every receipt carries `canon_version`: `founder_canon_v1.0.0`.

---

**Final sentence:** Autonomy inside sandbox. Walls at the boundary. Failures route to machines. Receipts prove everything. The founder decides capital, irreversible L5, and phase unlocks — and the system works continuously to need even that less.
