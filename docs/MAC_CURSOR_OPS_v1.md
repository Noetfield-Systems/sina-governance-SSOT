# Mac Cursor — operations v1

**Posture:** Full auto when `~/.sina/brain-autonomous-deploy-v1.flag` + gate CAS. Cloud GH Actions `*/30` is mirror, not duplicate writer.

## Monthly audit (15 min)

```bash
bash ~/Projects/sina-governance-ssot/scripts/repair_sourcea_worktree_v1.sh  # if sourcea_head=unknown
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/validate_parallel_automation_governance_v1.py
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/audit_automation_surface_v1.py
```

Pass lines: both `ALL PASS`. Receipt auto-written to `receipts/automation-surface-audit-<timestamp>.json`.

## Weekly ROI scorecard

From `docs/1111_UPGRADE_PLANS_v2.md`:

- Cost per signal < CAD 0.01
- Trap battery 100%
- Real fixture agreement ≥ 90%
- Pattern exports ≥ 1 batch/week (Wave 2+)

## Kill switches (founder)

```bash
# Stop Mac motor + full auto
launchctl bootout "gui/$(id -u)/com.sina.brain-loop-autorun-v1"
rm -f ~/.sina/brain-autonomous-deploy-v1.flag

# Observe-only without uninstall
rm -f ~/.sina/asf-ship-window-v1.flag

# Clear autonomous hold (retry)
rm -f ~/.sina/enforcement/brain-autonomous-hold-v1.flag
```

## New automation rule

No new cron/workflow without `motor_id` row in `data/github_automation_registry_v1.json` + `data/automation_surface_inventory_v1.json`.
