# NOOS Control Desk (MVP)

Zero-dependency local cockpit for `.noos/workflow_registry_v1.json`, the cost-policy
checker, and NOOS integrator sync. Per the Phase 1 decision: localhost web app first,
Electron/Tauri wrapper deferred until this MVP is actually useful day-to-day.

## Run it

```bash
python3 control-desk/app.py --port 17877 --repo-root .
```

Then open **http://localhost:17877**. No pip install needed — backend is Python stdlib
(`http.server`) on purpose, so there's nothing to break between your machine and the
checker script it wraps.

## What it actually does (tested end-to-end before delivery, not just written)

- **Dashboard** — registry entry count, TODO-audit count, live git status (honest: if the
  folder isn't a git repo yet, it says so instead of pretending).
- **Workflow Registry** — reads the real registry, shows every entry, TODO vs audited badge.
- **Attest** — click a row, fill model_policy/trigger/last_audited from dropdowns (not free
  text, so you can't accidentally type `gpt-5.4`), save. Writes the real registry file +
  a receipt with before/after diff.
- **Cost Policy** — one button runs the real `scripts/check_cost_policy.py` and shows the
  full aggregated report (every violation, not just the first).
- **NOOS Sync** — one button runs the real `scripts/noos_integrator_sync_v1.py sync` +
  `summary --json`.
- **Receipts** — lists what's actually in `receipts/`.
- **Submit Queue** — shows real git status. Does not fabricate a PR-ready state if the
  directory isn't a real git repo with a remote.

## Security model (the whole thing, no more no less)

- Binds to `127.0.0.1` only — not reachable from network.
- The backend runs exactly two subprocess commands, both built from fixed constants:
  `check_cost_policy.py` and `noos_integrator_sync_v1.py`. No request field is ever
  concatenated into a shell command. Tested with an injection-attempt workflow_id
  (`"; rm -rf /"`) — rejected by regex before it ever reaches a subprocess call.
- Attestation fields are validated against fixed allowlists (dropdown-backed on the
  frontend, re-validated server-side regardless of what the frontend sends).
- Never merges to main. Never runs a model. Never starts a background monitor.

## What's explicitly NOT built yet (be honest about this)

- **Open PR** is not wired to actually create a branch/commit/PR yet — the Submit Queue
  tab reports real git status but stops there. Wire this once the repo is actually
  `sina-governance-SSOT` with a real remote; faking a PR button before that exists would
  be exactly the kind of overclaim this whole system is designed to refuse.
- **Home mirror / cloud mirror** fields in `noos_integrator_sync_v1.py` report
  `unconfigured` honestly rather than a fake "synced" — point `NOOS_HOME_MIRROR_PATH`
  at a real path when one exists.
- **Copilot UI auto-scrape** (the "hidden gem" from the earlier discussion — a
  Selenium/API bridge that reads Copilot Automations settings automatically) is Phase 4,
  not built here. Attestation is manual-entry by design until that bridge exists.
- No Electron/Tauri wrapper — deferred per the Phase 1/Phase 2 decision above.

## Verified test run (this session)

```
GET  /                          -> 200
GET  /api/registry               -> 200, 23 entries
GET  /api/dashboard               -> 200, correct TODO/audited counts
POST /api/registry/attest (valid)   -> SAVED, receipt written, registry file updated
POST /api/registry/attest (bad model)  -> REJECTED with clear error, file untouched
POST /api/registry/attest (injection attempt in workflow_id) -> REJECTED, never reached subprocess
POST /api/validate               -> real checker ran, returned full aggregated report
POST /api/sync                   -> real sync script ran, returned honest summary
GET  /api/receipts                -> listed real files
```

Test attestation was reverted back to `TODO` before packaging — this delivery ships with
the honest, unaudited 23-entry registry, not a pre-faked one.
