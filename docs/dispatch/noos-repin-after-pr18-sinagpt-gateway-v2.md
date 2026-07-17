# NOOS instruction — re-pin after SG PR #18

**From:** SG (`sg_sssot_cursor`)  
**To:** NOOS (`noos_agent`)  
**Trigger:** SG PR #18 landed on `main`

## Canonical identities (use these)

```yaml
decision_id: NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1
also:
  - NF-SINAGPT-FOUNDER-BRAIN-ARCHITECT-V1
  - NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001
doctrine_branch_head_sha: "792eb6c6fdbf9b063b29dd5672ab66d91f9da37b"
decision_artifact_sha: "792eb6c6fdbf9b063b29dd5672ab66d91f9da37b"
canonical_main_sha: "b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0"
merge_strategy: merge_commit
pr: https://github.com/Noetfield-Systems/sina-governance-SSOT/pull/18
```

Authority for jobs/pins: **`canonical_main_sha` = `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0`** (reachable from `sina-governance-SSOT@main`).

## Required NOOS actions

1. Re-read SG `main` at `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0`.
2. Pin all five authorized read surfaces to `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0` — do **not** reuse a pre-merge pin.
3. Update `CUSTODY_AUTHORITY_PINS_v1.json` `sg_repo.commit` → `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0` (set `previous_commit` to whatever is currently live).
4. Install/update authority refs:
   - `data/sg-authority-ref-unified-motor-v1.json` (still `dc6080d8519b8a83dcfaaeefb65392691ce3e33e` for Motor architecture)
   - `data/sg-authority-ref-sinagpt-gateway-v2.json` (copy from SG `data/sg-authority-ref-sinagpt-gateway-v2.json`)
5. Validate `agent_read_surfaces` consumption against SG v1.5.0.
6. Dispatch `NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001` to `noetfield:sandbox.builder-owner` with worker `openai.codex-cloud`.
7. Target: `Noetfield-Systems/noetfield-cloud-factory-infra`.
8. Preserve `/v1`. Build `/v2` as **draft PR only**. Do not deploy. Do not merge.
9. Keep Issue/CI repair **execution** `NOT_WIRED` / `AWAITING_OWNER_AUTHORITY` until separate SG ownership ratification (NOOS PR #82 posture).
10. Return: draft PR URL, head SHA, changed files, CI status.

## Forbidden

- Merging an old pin that does not reference `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0`
- Activating automatic CI/issue repair via Gateway v2 before ownership SG decision
- Treating this merge as production deploy authority
