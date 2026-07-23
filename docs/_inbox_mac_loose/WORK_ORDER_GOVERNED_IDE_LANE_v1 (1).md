# WORK ORDER — Governed Agentic IDE Lane v1

**Status:** `DRAFT — PENDING FOUNDER APPROVAL. ZERO EXECUTION AUTHORITY.`
**Parent doctrine:** governed-autorun v3 (L1–L13, D1–D8) — referenced by pointer, never restated.
**Incident basis:** Session 2026-07-03 (forged L5 sign-off `239c8b5`, replayed receipts, self-fulfilling revert `166b7d3`, phantom-commit narration). Every gate below traces to one of those failures.

---

## 1. GOAL

Stand up **one** governed agent lane in `noetfield-studio-ide` where a coding agent executes bounded work orders inside an isolated git worktree, under **mechanical** (hook/CI-enforced, not prose) L5 guardrails, producing canonical receipts verified by an external runner.

North-star deliverable of v1: **five consecutive clean cycles.** Not features. Not tools. Proof that the cage holds.

## 2. NON-GOALS (v1)

- No multi-tool stack. No Roo, Kilo, OpenHands, Claude Code installs.
- No autorun/cron. Every cycle is founder-dispatched.
- No self-healing, no Kaizen slot, no improvement backlog execution.
- No writes to `sina-governance-SSOT`, `SourceA`, `noetfeld-OS`, or any repo other than the one named below.
- No touching the noos-multi-sandbox-kernel skill (stays `draft-pending-schema-fix` until separate L5 order).

## 3. PHASE-1 TOOL DECISION

**Aider** (terminal, git-native).
Reason: smallest command surface to allowlist, every edit is a git commit by construction, no IDE extension state, no background agent process, deterministic diffs. Roo Code is Phase 2 (after 5 clean cycles), Claude Code is escalation-only (P0/P1, founder-dispatched), OpenHands is Phase 4 (after external verifier + policy pack survive Phase 2).

## 4. ALLOWED SCOPE

| Dimension | Allowed | Everything else |
|---|---|---|
| Repo | `noetfield-studio-ide` | FORBIDDEN |
| Branch/lane | `worktree/task-NNN` off `main` | main = protected, direct writes FORBIDDEN |
| Paths | per-task `allowed_paths` list in the dispatch | FORBIDDEN, hook-rejected |
| Commands | `command_allowlist.json` (git, npm run build/test/lint, node, grep, ls, cat) | FORBIDDEN — no curl, no pip/npm install, no rm -rf, no ssh, no gh |
| Commits | Only those enumerated in the dispatch. Reverts count as commits. | `git add -A`, `reset --hard`, force-push, amend, rebase = hook-blocked |
| Network | none (Aider model API only) | FORBIDDEN |

## 5. MECHANICAL L5 GATES (the actual deliverable)

Prose guardrails failed twice this session. v1 builds these as **pre-commit hook + CI check**, both of which must exist and pass their own tests before the agent runs cycle 1:

**G1 — Governance-path lock.** Commit on any agent lane touching `.noetfield/skills/REGISTRY.json` status fields, any `*LAWS*`, `*ledger*`, `*SSOT*`, `QUARANTINE*`, or receipt-schema files → rejected, unconditionally. **There is no token-authorized agent path in Phase 1** — a token in a commit message would enter git history on first use and become agent-readable forever. Governance changes are founder-only, made outside agent cycles (see G6). The founder token exists solely as the §12 approval artifact.

**G2 — Approval-language lock.** Commit message or diff on any agent lane containing `L5 sign-off`, `founder approved`, `production-ready`, `approval recorded` → rejected, unconditionally. Agents produce evidence; they never produce approvals. (Incident: `239c8b5`.)

**G3 — Sweep lock.** Staged file outside the dispatch's `allowed_paths` → rejected. Kills `git add -A` structurally. (Incident: breach commit fused work + forgery, making revert destructive.)

**G4 — Unordered-commit lock.** Each dispatch carries `max_commits: N`; hook counts commits on the worktree branch and rejects N+1. (Incident: `166b7d3`.)

**G5 — Transform-fidelity check (D9 candidate, enforced locally).** CI job validates every emitted receipt: row counts and field sets of evidence structures must survive any format conversion unless the dispatch authorizes truncation. (Incident: 4-row evidence matrix silently cut to 2.)

**G6 — Policy immutability during cycle.** The entire `.agent-policy/` directory (`allowed_paths`, `command_allowlist.json`, `max_commits`, receipt schema, gate/hook scripts, `founder_token.hash`) plus the active dispatch file are hook-rejected on any agent lane, no exceptions, no token path. An agent that can edit its own cage has no cage (L5: the loop may add brakes, never remove one). Policy changes happen founder-only, on `main`, between cycles — never during one.

## 6. CYCLE CONTRACT

Per governed-autorun Cycle Anatomy, bounded form:

`DISPATCH → PLAN (posted, no edits) → PATCH (worktree only) → TEST → RECEIPT → STOP`

- Agent never proceeds past a failed step; it reports `FAILED_WITH_RECEIPT` and halts. No improvised fixes (standing rule from this session).
- PASS comes only from the GitHub Actions verifier on the pushed worktree branch — never the agent's local run (L4). Local test green is evidence, not verdict.
- Merge to `main` is founder-only, after verifier green + receipt review.

## 7. RECEIPT FORMAT (fixed fields, no narrative)

```
task_id / branch / commits (SHAs, must equal dispatch enumeration)
files_changed (must ⊆ allowed_paths)
commands_run (must ⊆ allowlist, raw output tails)
test_result (external runner URL + conclusion + timestamp)
evidence rows (count in == count out, G5)
cost {provider, model, tokens_in, tokens_out, usd} (L11)
value_class: revenue_path | proof_asset | risk_reduction | hygiene | none (L11)
state: COMPLETE | FAILED_WITH_RECEIPT | BLOCKED_WITH_REASON
next_action (one line or empty)
```

Receipt lives in-repo at `worktree branch:.agent-policy/receipts/task-NNN.json` (L6 — never home dirs, never Copilot memory, never IDE session storage).

## 8. BUDGET

- Per cycle: **$1.00** hard cap, metered at call site (L11). Breach = `BLOCKED_WITH_REASON`, not overdraft.
- Phase 1 total: **$10.00** across all cycles including failures.
- Model tier: cheap (DeepSeek/Gemini Flash class) for patches; premium never dispatched in Phase 1.

## 9. ROLLBACK RULE

`git revert` only, as its own enumerated dispatch, never bundled. `reset --hard` and force-push are hook-blocked (G4 territory). A rollback is a cycle: it gets its own receipt.

## 10. ACCEPTANCE CRITERIA (all five, externally evidenced)

1. G1–G6 hooks/CI exist, each demonstrated by a **deliberately failing test commit** that the gate rejects (negative proof, not prose). Negative-proof commits run **only on disposable `gate-test/*` branches** — never `main`, never a production worktree lane — and the branches are deleted after the rejection receipt is captured.
2. Five consecutive dispatched cycles reach COMPLETE with receipts validating against §7 — zero unordered commits, zero governance-path writes, zero approval language.
3. External verifier (GitHub Actions) produced the PASS on all five; timestamp math clean (L4).
4. Sum of metered cost ≤ budget; every receipt carries cost + value_class.
5. Zero writes outside `noetfield-studio-ide`; zero state in Copilot memory/home dirs (verified by the same find-sweep used in this session's audits).

Any single violation resets the counter to zero. Two violations in one phase = tool disqualified, session retired, incident line filed.

## 11. PHASE LADDER (informational, each phase = new founder-approved work order)

| Phase | Adds | Unlock condition |
|---|---|---|
| 1 | Aider + worktree + policy pack + hooks + CI verifier | this order |
| 2 | Roo Code (Architect/Code modes), 2 parallel lanes | 5 clean P1 cycles |
| 3 | Claude Code escalation path (P0/P1 only) | 10 clean P2 cycles |
| 4 | OpenHands sandbox farm, cron dispatch (true autorun) | P3 + 24h zero-manual window green (Bootstrapping rule 5) |

## 12. FOUNDER APPROVAL BLOCK

This order executes only when the founder (a) writes the approval line into the governance ledger **by their own hand**, and (b) places the token hash at `.agent-policy/founder_token.hash`. The token authorizes nothing in any agent flow (G1) — it exists solely so the approval is a verifiable on-disk fact rather than a sentence an agent could reconstruct. No agent, advisor, or summary may produce either artifact. Absent both: this document is inert.

```
APPROVAL: ____________________  DATE: ____________  TOKEN PLACED: [ ]
```
