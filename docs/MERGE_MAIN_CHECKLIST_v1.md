# Merge main checklist v1

Branch: `cursor/trustfield-signal-factory-lock-1111-plans` → `main` on `Noetfield-Systems/sina-governance-SSOT`

## Before merge

- [ ] Contains Mac Cursor fixes (`repair_sourcea_worktree_v1.sh`, `brain_mac_env_v1.sh`, launchd 30m)
- [ ] Contains CI observe-only hardening (`load_cf_tokens_v1.sh`, `brain_loop_autorun_v1.sh`)
- [ ] `validate_parallel_automation_governance_v1.py` ALL PASS
- [ ] `audit_automation_surface_v1.py` ALL PASS (0 warnings)
- [ ] `validate_copilot_pr_template_v1.py` ALL PASS
- [ ] No runtime receipt JSON staged (`git status` clean of `receipts/brain-*` dumps)

## Merge

- [ ] Open PR with lane `sg_governance` and task cell from registry
- [ ] Squash or merge per org policy — no force-push

## After merge (post-merge verification)

```bash
# 1. Record merge SHA
git fetch origin main && git log origin/main -1 --oneline

# 2. GH Actions brain-loop on main (expect green observe-only without CF secrets)
gh run list --workflow=brain-loop-autorun-v1.yml --repo Noetfield-Systems/sina-governance-SSOT --branch main --limit 3

# 3. Local Mac still healthy
bash ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/brain_loop_health_check_v1.sh
launchctl list | grep brain-loop-autorun

# 4. Drift audit
/usr/bin/python3 ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/audit_automation_drift_v1.py
```

## Pass criteria

| Check | Expected |
|-------|----------|
| `brain_loop_health_check_v1` | ALL PASS |
| `brain-loop-autorun-v1` on `main` | `success` or observe-only receipt (not fail on missing tokens) |
| launchd | `com.sina.brain-loop-autorun-v1` loaded |
| `audit_automation_drift_v1` | `PASS` after main CI green |

## Known blocker (not merge-blocking)

- Autonomous promote may stay `BLOCKED` until verifier returns PASS for current bundle SHA (see `diagnose_gate_candidate_alignment_v1.py`).
