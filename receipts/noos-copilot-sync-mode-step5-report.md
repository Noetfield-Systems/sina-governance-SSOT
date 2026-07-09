# NOOS Copilot Sync Mode — Step 5 Report

**Owner:** NOOS  
**SG record:** pointer only (2026-07-04)  
**Status:** Step 5 COMPLETE / RECORDED

## Summary

NOOS Copilot Step 5 replaces binary `cloud_write_allowed` with a **mode-gated** sync model.

- **NOOS Copilot** remains P2 cross-repo sync dispatcher.
- **NOOS** owns integrator/sync behavior.
- **SG** records pointers only — does not own sync runtime.

## Allowed pre-PASS modes

| Mode | Purpose |
|------|---------|
| `read_status` | integrator/home/cloud readout |
| `publish_receipt` | schema-validated receipt write |
| `publish_status` | status publish |
| `publish_drift_report` | drift report publish |
| `prepare_draft_branch` | draft branch prep |
| `prepare_pr` | PR prep (no direct main) |

## Blocked pre-PASS modes

| Mode | Block reason |
|------|----------------|
| `fleet_rollout` | pre-PASS |
| `active_promotion` | pre-PASS |
| `direct_main_write` | pre-PASS |
| `policy_law_mutation` | pre-PASS |
| `publish_audit_pending_registry_as_active_fleet_truth` | audit-pending registry |

## SG pointer artifacts

- `docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md`
- `data/noos-copilot-dispatcher-mode-v1.json`
- `data/noos-integrator-role-v1.json` → canonical `noetfeld-os/data/noos-integrator-role-v1.json`

## Receipt

`receipts/noos-copilot-dispatcher-mode-patch-20260703T195800Z.json`

## Next

**Step 6 — Machine-Enforceable Repo Fences**
