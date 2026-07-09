# SMART_PRODUCTION_COST_LAW_v2.md

**Status:** LOCKED POLICY ARTIFACT — supersedes `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md` and the unlocked `Smart Production Workflow Stack v1` proposal. Both are merged, reconciled, and upgraded here. v1 files should be kept for history but are no longer authoritative once this file is adopted.

**Scope:** every automation surface across `sina-governance-SSOT`, `SourceA`, `Noetfield`, `TrustField-Technologies`, `noetfeld-os` — GitHub Actions, Copilot automations/sessions, Cloudflare workers, NOOS Integrator, and any future orchestrator.

---

## 0. Why this rewrite exists

v1 got the *shape* right (GitHub Actions automate, Cloudflare coordinates, Copilot is a bounded worker, GPT-5 mini only, receipts are truth). But v1 has five real gaps that would have caused silent failure or a second cost leak in production. This version closes them. See §10 "What v1 missed" for the specific reasoning — read it, it's short and it's the part worth not skipping.

## 1. Prime Rule (unchanged, still correct)

Copilot does not own autorun. GitHub Actions/scripts/machine gates own recurring automation. Cloudflare coordinates cheap always-on state. Copilot is a bounded, manual-triggered helper.

**Default model:** `gpt-5-mini` · **Default effort:** `low` · **Default trigger:** `manual` · **Default recurring engine:** GitHub Actions with `model:none`.

## 2. Hard Model Lock

**Allowed by default:** `gpt-5-mini` (exact string match, case-insensitive, no wildcard).

**Forbidden by default:** any Auto/routed model, GPT-5.4 and GPT-5.4-mini, GPT-5.3-Codex, any Claude model, Codex, Gemini (unless explicitly allowed later), Kimi (unless explicit exception), MAI-Code, "Coding Agent model", any unrecognized/unlisted model string.

**Unknown-model-fails-closed** (kept from v1, this is correct): if the checker cannot classify a model string as the exact allowed string, it is a violation — never a silent pass.

**v2 addition — model-string drift guard:** GPT-5 mini's exact product name can change without notice (providers rename SKUs). The policy file (`policy/cost_policy.yaml`) holds the canonical allowed-model string in one place, versioned. If the vendor renames the model, you update **one line** in the policy file and bump `policy_version` — not every workflow file. Never let "close enough" model-name matching (`gpt-5*`) into the checker; a loose wildcard is exactly the kind of gap that becomes a silent fallback door.

## 3. Effort, Trigger, Mode Locks (unchanged from v1, correct as written)

- Effort: `low` default; `medium` only by logged exception for manual diagnosis/bounded repair. `high`/`extra high`/unknown/auto effort are hard fails.
- Trigger: `manual` default. `hourly`/`daily`/`weekly`/`background`/`keep awake`/unpinned schedule/"autopilot recurring" are hard fails for Copilot specifically — that work belongs to GitHub Actions or Cloudflare cron.
- Autopilot mode allowed only when trigger=manual AND model=gpt-5-mini AND effort=low AND task is bounded AND (read-only OR safe-fix scoped) AND no direct merge AND no background process.

## 4. Workflow Classes (from the Production Stack proposal, kept and tightened)

| Class | Purpose | Default owner | Default model |
|---|---|---|---|
| Observe | detect state/failure/drift | GitHub Actions / Cloudflare cron | `model:none` |
| Triage | root-cause from evidence | Copilot manual | `gpt-5-mini low` |
| Safe Fix | repair small deterministic defects | Copilot manual or Action script | `model:none` for mechanical fixes, `gpt-5-mini low` for text/code patch |
| Verify | prove work independently | GitHub Actions | `model:none` |
| Deploy | ship only after gates pass | GitHub Actions + host | `model:none` |
| Reconcile | sync truth across repos/mirrors | NOOS Integrator + Actions | `model:none` first, `gpt-5-mini` only if interpretation needed |

**v2 addition — Class 7, Circuit Breaker (new, see §10.3):** a class that isn't a worker but a governor. It watches the *rate* of Safe Fix output (PRs/day, branches/day) and Copilot task count/day, and halts new Safe Fix dispatch if a cap is exceeded — independent of whether each individual fix looked fine. Owner: GitHub Actions or Cloudflare Worker, `model:none`. This is the one piece v1 had no answer for: a correctly-configured GPT-5-mini-Low-Manual Copilot can still be manually triggered 200 times a day by a script or an over-eager loop. Per-call correctness doesn't bound aggregate cost or aggregate PR noise — only a rate governor does.

## 5. Workflow Registry — now with an actual schema contract, not just an example

`.noos/workflow_registry_v1.json` is the source of truth for what runs, where, under whose ownership, and with what model rights. Every entry must validate against `policy/cost_policy.yaml`'s `registry_schema` before it's trusted. Required fields (v2 adds three to v1's list):

```
workflow_id          string, unique across the whole registry (not just per-repo — see §10.1)
repo                 string
class                one of: observe | triage | safe_fix | verify | deploy | reconcile
owner                one of: github_actions | cloudflare_worker | copilot_manual | noos_integrator
trigger               schedule | manual | event
model_policy          "model:none" | "gpt-5-mini-low"        (no other string is valid)
writes                artifacts_only | branch_pr | direct    ("direct" requires class=deploy and explicit gate reference)
risk                  low | medium | high
receipt_required      boolean
safe_fix_allowed      boolean
escalation            string (what happens on failure/threshold breach)
single_owner_lock     boolean   — v2 NEW: true if this workflow_id is the only writer for its target resource
last_audited          ISO date  — v2 NEW: when a human/UI check last confirmed the live automation matches this entry
max_daily_runs        integer   — v2 NEW: circuit-breaker input for Class 7
```

**Contract rule:** any entry with `safe_fix_allowed: true` MUST also have `receipt_required: true`. A safe-fixer that can write a branch/PR but isn't required to produce a receipt is a silent-repair door — reject it at registry-validation time, not at audit time.

## 6. Cost Intelligence Lock (from v1, kept, tightened with budgets)

Fail conditions (unchanged): Auto model, GPT-5.4, Claude, Codex, Gemini (unless allowed), Kimi (unless exception), unknown model, missing cost receipt, scheduled Copilot model use unless registered.

**v2 addition — aggregate budgets, not just per-call rules.** A per-automation rule ("this one uses gpt-5-mini low") says nothing about total daily spend if the automation fires 500 times. `policy/cost_policy.yaml` defines:
- `copilot_daily_task_cap` — max Copilot-triggered tasks per day across all repos combined
- `copilot_daily_cost_cap_usd` — max estimated spend per day
- `github_actions_daily_minutes_cap` — Actions minutes aren't free at scale either; v1 never priced this
- `safe_fixer_daily_pr_cap` — circuit breaker input (§4, §10.3)

Receipt fields (unchanged from v1, correct): `provider, model, effort, tokens_in, tokens_out, estimated_cost, cost_policy_pass, cost_policy_version`.

## 7. Smart Repair Pipeline (from v1, kept, with the merge gate made explicit)

```
Observe → Classify → Safe Fix (if deterministic) → Verify → PR/receipt → merge candidate
```

Founder is not in the loop unless: capital/legal exposure, irreversible L5-class action, or explicit phase unlock — same boundary as `FOUNDER_INTENT_FILTER.md` if that canon is active in this org. **v2 note:** if both canons are adopted, `FOUNDER_INTENT_FILTER.md` rule R5 (evidence-based merge, no founder-click) and this file's "no direct merge" rule must agree — they do, by design; treat any future edit to either as requiring a matching edit to the other.

## 8. Repo-by-Repo Ownership (unchanged from v1's plan, this part was already right)

- `sina-governance-SSOT` — policy, doctrine, cost locks, the registry itself.
- `noetfeld-os` — NOOS brain, integrator, agent loops, cloud worker kernel.
- `SourceA` — product/site/workflow validation, gated deploys.
- `Noetfield` — web/app/platform verification, separate deploy vs observe.
- `TrustField-Technologies` — product/deploy/runtime health; **Copilot cloud agent must be disabled here specifically** — v1 flagged this correctly and it stays.

## 9. Phase Roadmap (unchanged sequencing from v1, correct order)

Phase 0 stop leakage → Phase 1 workflow inventory → Phase 2 convert recurring Copilot to Actions → Phase 3 safe-fixer layer → Phase 4 Cloudflare control plane → Phase 5 autonomy ladder (clean receipts lower manual triggers over time).

**v2 addition:** insert **Phase 3.5 — Circuit breaker before scaling safe-fixer scope.** Do not widen Phase 3's safe-fix file/path scope until Class 7 (rate governor) is live and tested. Scaling repair autonomy before you can rate-limit it is how a correctly-configured system still produces 40 PRs in an afternoon.

## 10. What v1 missed (the hidden gems — read this part)

**10.1 — Registry collision risk.** v1's example registry entry has `workflow_id: "daily_repo_health"` scoped by `repo` field alone. Across five repos, nothing stopped two different repos (or two different automations within one repo) from both claiming ownership of the *same underlying resource* — e.g. two workflows both syncing the NOOS integrator state, unaware of each other, racing. v2 makes `workflow_id` globally unique across the whole registry and adds `single_owner_lock` so the registry itself can be checked for collisions, not just for schema validity.

**10.2 — Safe-fixer receipt gap.** v1 said "safe fixer creates branch + PR + receipt" in prose but never made receipt-emission a *validation-time contract* on the registry entry. A safe-fixer could be registered with `safe_fix_allowed: true` and no `receipt_required` field at all, and nothing in v1 would catch that at setup time — only a human reading closely would. v2 makes this a hard registry-validation rule (§5).

**10.3 — No aggregate rate limit.** This is the biggest one. v1 locks every *individual* Copilot call to low-cost, low-effort, manual-trigger — genuinely good per-call discipline. But nothing in v1 stops a script, a loop, or an eager agent from manually triggering that same bounded, cheap, compliant-looking call 500 times in a day. Per-call correctness is necessary but not sufficient; v2 adds the Class 7 circuit breaker and aggregate budget caps (§4, §6) specifically to close this.

**10.4 — GitHub Actions isn't free either.** v1 treats GitHub Actions as the free/cheap default with no budget ceiling of its own. Actions minutes are metered past included quotas. v2 adds `github_actions_daily_minutes_cap` so "move it from Copilot to Actions" (Phase 2) doesn't just relocate the cost leak instead of closing it.

**10.5 — Self-protection gap: who edits the cost policy?** v1 never states who is allowed to change `COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md` or its future machine-readable form. A policy that any automation can edit is not a lock. v2 states explicitly: `policy/cost_policy.yaml` and this canon file may only be changed via a PR that passes the same Verify-class gates as any other governance change, and a change to the model allowlist specifically requires the exception-logging fields in §2 — no automation may edit its own leash directly, including a "helpful" Copilot safe-fixer.

**10.6 — Staleness of the audit itself.** v1's §8 audit checklist is thorough but has no cadence attached — an audit done once and never repeated is a snapshot, not a control. v2's `last_audited` registry field (§5) makes staleness visible and checkable: a registry entry whose `last_audited` is more than 30 days old should be flagged for re-verification against the live Copilot UI, since model/effort/trigger settings live in a UI that no script can read directly.

## 11. Final Operating Law (v2)

```
GitHub Actions automate.
Cloudflare coordinates.
NOOS Integrator syncs.
Copilot assists manually, gpt-5-mini-low only.
model:none is default for scheduled jobs.
Safe fixers repair; every safe fixer emits a receipt or is not registered.
Verifiers judge independently.
A circuit breaker governs aggregate rate, not just per-call cost.
No workflow_id is owned by two automations at once.
No automation edits its own cost policy.
No direct merge. No founder runtime.
```
