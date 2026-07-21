# Cockpit feature freeze (LOCKED)

Status: FROZEN for feature work after SHA `469e84eefce4b0333c5be0e5172a52b9dd42d1e5`

Lane split (founder / advisor directed):

- **Cursor** = Standalone Cockpit + Kernel + HDIR release captain (`PASS_RUNWAY_LIVE_V1` promote)
- **Codex** = `app.noetfield.com` → Kernel → HDIR convergence (`PASS_APP_RUNWAY_CONVERGENCE_V1`)

Allowed on this branch after freeze:
- release/deploy fixes required to land already-committed verifier/proxy wiring
- exact SHA production promote via existing GHA / Pages path

Forbidden:
- new cockpit product features
- redesign of standalone UI
- app.noetfield.com convergence work in this tree
- dirty-worktree deploy as release proof
