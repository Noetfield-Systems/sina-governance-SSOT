# NOOS Copilot Dispatcher Authority — SG Pointer

**SG role:** Guard · authority registry · package pointer controller  
**SG status:** POINTER ONLY — SG does **not** own NOOS integrator/sync behavior  
**NOOS owns:** integrator/sync behavior, mode enforcement, runtime sync  
**Recorded:** 2026-07-03T19:58:00Z (Step 5 COMPLETE / RECORDED)

---

## Pointer map

| Artifact | Owner | SG path | Canonical |
|----------|-------|---------|-----------|
| Sync mode model | NOOS | `data/noos-copilot-dispatcher-mode-v1.json` | mode-gated dispatch |
| Integrator role | NOOS | `data/noos-integrator-role-v1.json` | pointer → `noetfeld-os/data/noos-integrator-role-v1.json` |
| Dispatcher registry | SG pointer | `data/noos_copilot_dispatcher_v1.json` | P2 cross-repo sync dispatcher |
| Dispatcher SSOT | SG pointer | `ssot/NOOS_COPILOT_DISPATCHER_v1.md` | human summary |

---

## Recorded facts (Step 5)

- **NOOS Copilot** remains **P2** cross-repo sync dispatcher (`noos-copilot-dispatcher-v1`).
- **NOOS** owns integrator/sync behavior — not SG, not GitHub Copilot UI.
- Sync model is **mode-gated** — not binary `cloud_write_allowed`.

### Allowed pre-PASS modes

- `read_status`
- `publish_receipt`
- `publish_status`
- `publish_drift_report`
- `prepare_draft_branch`
- `prepare_pr`

### Blocked pre-PASS modes

- `fleet_rollout`
- `ACTIVE` promotion
- `direct_main_write`
- `policy_law_mutation`
- `publish_audit_pending_registry_as_active_fleet_truth`

---

## SG boundaries (this step)

| SG did | SG did not |
|--------|------------|
| Record pointers + receipt | Take ownership of sync behavior |
| Register mode in package map | Promote package ACTIVE |
| Point to Step 6 next | Start CI/runtime enforcement |

**Machine mode SSOT:** `data/noos-copilot-dispatcher-mode-v1.json`  
**Step 5 receipt:** `receipts/noos-copilot-dispatcher-mode-patch-20260703T195800Z.json`  
**Step 5 report:** `receipts/noos-copilot-sync-mode-step5-report.md`

**Next canonical step:** Step 6 — Machine-Enforceable Repo Fences
