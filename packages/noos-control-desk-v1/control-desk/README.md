# NOOS Control Desk (MVP v2 - Observed Reality patch)

Zero-dependency local cockpit for `.noos/workflow_registry_v1.json`, the cost-policy
checker, and NOOS integrator sync. Localhost web app first (Python stdlib
`http.server`, no pip install) — Electron/Tauri and a Selenium/scraper bridge are
both explicitly deferred, per the Phase 1 decision and the Advisor's 4th patch below.

## What changed in this patch (do not skip this if you read the v1 README)

The v1 README claimed the form "doesn't let you type gpt-5.4." **That was wrong and
has been removed.** The correct behavior, now implemented and tested:

The form records **observed reality**, including bad values, and never hides a leak:

- `observed_model`, `observed_effort`, `observed_trigger`, `observed_mode` are free-text
  fields. You type exactly what the live Copilot/GitHub UI actually shows — `gpt-5.4`,
  `Auto`, `Claude`, `High`, `Hourly` — whatever it really is.
- `desired_model`, `desired_effort`, `desired_trigger` are dropdown-constrained to the
  allowed policy values (`gpt-5-mini` / `low` / `manual`/`schedule`/`event`) — this is
  "what it should be," separate from "what it is."
- The server — never the client — computes `policy_verdict` (`PASS`/`FAIL`/`BLOCKED`)
  from the observed fields against the known-forbidden lists and effort/trigger rules.
  A client cannot self-report PASS.

## Two-state model (Draft vs Lock Candidate)

- **Save Draft Attestation** — writes to `.noos/registry_draft.json`, never touches the
  real registry. Savable at any time, any mix of PASS/FAIL/BLOCKED/incomplete. This is
  how you record 3 leaks and 20 TODOs without anything breaking.
- **Submit Lock Candidate** — only enabled when *all* workflows in the draft are `PASS`.
  On submit: applies the attested `last_audited` dates to the real registry, re-runs the
  real checker, and — **only if that also returns PASS** — creates a bounded local git
  branch (`audit/update-registry-YYYY-MM-DD`) and a local commit. **It never pushes,
  never opens a PR, and never touches `main`.** If the checker fails after applying, the
  registry is left in the failed state with a clear error rather than silently rolled
  back or silently reported clean — inspect `receipts/control_desk_last_validate.json`.

## Builder roles (Architect retired)

**Architect:** FINISHED — no new architecture in build phase.  
**Primary builder:** Cursor in `sina-governance-ssot`  
**Role map:** `data/noos_control_desk_builder_roles_v1.json`

| Step | Role | Tool | Status |
|------|------|------|--------|
| 1 | Policy Checker | Cursor | ACTIVE |
| 2 | Backend Builder | Cursor | ACTIVE |
| 3 | Frontend Builder | Cursor | NEXT |
| 4 | Integrator Agent | Cursor | noetfeld-os canonical |
| 5 | Negative Test | Cursor + GH Actions | pending |
| 6 | Critic / Auditor | this chat | pending |
| 7 | Packager | Cursor | pending |

## Run it

```bash
python3 control-desk/app.py --port 17877 --repo-root .
```
Open **http://localhost:17877**.

## Verified end-to-end this session (real subprocess calls, not descriptions)

```
POST /api/draft/save  observed_model=gpt-5.4, observed_effort=high, observed_trigger=hourly
   -> SAVED, policy_verdict=FAIL, reasons: [forbidden model, forbidden effort, forbidden trigger]
   (the leak was RECORDED, not rejected - this was the whole point of the patch)

POST /api/draft/save  observed_model=gpt-5-mini, observed_effort=low, observed_trigger=event
   -> SAVED, policy_verdict=PASS

POST /api/draft/save  observed_model=SomeBrandNewModelXYZ
   -> SAVED, policy_verdict=BLOCKED (unrecognized model, neither allowed nor known-forbidden)

POST /api/lock-candidate/submit  (with 1 FAIL, 1 BLOCKED, 20 TODO in draft)
   -> 409 BLOCKED, lists exactly which workflow_ids are blocking

[all 23 workflows attested PASS via script]

POST /api/lock-candidate/submit  (all 23 PASS)
   -> LOCK_CANDIDATE_READY, checker_status=PASS,
      git_result: real local branch "audit/update-registry-2026-07-04" + real commit
      (verified via `git log` and `git branch` afterward - not just claimed)
```

Test data (the attested-PASS registry, the draft file, the test git repo/branch/commit)
was reset before packaging. This delivery ships with the honest, fully-unaudited
23-entry registry — same principle as before: don't ship a fake audit.

## Security model (unchanged from v1, still the whole thing)

- Binds to `127.0.0.1` only.
- Exactly three subprocess commands, all built from fixed constants: the checker, the
  sync script, and `git` (checkout/add/commit only — no push, no remote operations).
- Every attestation field is validated server-side (workflow_id regex, date regex)
  regardless of what the frontend sends. `policy_verdict` is server-computed, never
  accepted from the client.

## Still explicitly NOT built (unchanged from v1, still true)

- Actually opening a PR (branch + commit are real; push + PR are not wired — would need
  a real remote + auth this environment doesn't have).
- Copilot UI auto-scrape/Selenium bridge — Advisor's 4th patch explicitly defers this;
  manual observed-reality entry is the whole point of the MVP, not a placeholder for it.
- Home/cloud mirror sync — still reports `unconfigured` honestly.
- Electron/Tauri wrapper.
