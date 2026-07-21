# Brain Loop launchd — 24/7 autorun v0.1

Mac must **help** deploy, not block. All Mac-specific fixes live in `scripts/brain_mac_env_v1.sh`.

## One-command install (recommended)

```bash
bash ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/repair_sourcea_worktree_v1.sh   # if git broken
bash ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/install_brain_loop_launchd_v1.sh
```

## Fast health check (<1s)

```bash
bash ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/brain_loop_health_check_v1.sh
```

## One-command install details

This script:
1. Creates `~/Projects/SourceA` git worktree (TCC-safe — not Desktop)
2. Installs launchd plist with `/usr/bin/python3` (avoids Framework Python SIGKILL)
3. Sets overlap lock (no concurrent cycles killing each other)
4. Configures **30m** interval (`StartInterval: 1800`) + 5min throttle

## What was blocking Mac (fixed)

| Blocker | Fix |
|---------|-----|
| Desktop TCC (`Operation not permitted`) | `~/Projects/SourceA` worktree |
| Framework Python SIGKILL under launchd | `BRAIN_PYTHON=/usr/bin/python3` |
| Overlapping launchd + manual runs | mkdir lock at `~/.sina/locks/` |
| Stale Desktop path in verifier/heal | `resolve_sandbox_repo()` uses `SOURCEA_ROOT` |
| Wrong hold on Mac env failures | `mac_env_block_no_hold` — retry next cycle |

## Manual cycle

```bash
bash ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/brain_loop_launchd_entry_v1.sh
```

## Logs

- `~/.sina/logs/brain-loop-autorun-v1.out.log`
- `~/.sina/logs/brain-loop-autorun-v1.err.log`
- `~/.sina/logs/brain-autorun-step-*.log` (per-cycle step detail)

## Schedule

| Setting | Value |
|---------|-------|
| `StartInterval` | **1800s (30m)** |
| `RunAtLoad` | true |
| `ThrottleInterval` | 300s |

Cloud mirror: GitHub Actions `brain-loop-autorun-v1` at `*/30`.

**Mac ops:** [MAC_CURSOR_OPS_v1.md](MAC_CURSOR_OPS_v1.md) · **Venture lanes:** [MAC_CURSOR_VENTURE_LANES_v1.md](MAC_CURSOR_VENTURE_LANES_v1.md)

## Prerequisites

- `~/.sina/brain-autonomous-deploy-v1.flag` (founder DECIDE)
- CF tokens via `scripts/load_cf_tokens_v1.sh`
- SourceA git at `~/Projects/SourceA` worktree (or archive fallback via `brain_mac_env_v1.sh`)

## Clear hold

```bash
rm -f ~/.sina/enforcement/brain-autonomous-hold-v1.flag
```

## Disable

```bash
launchctl bootout "gui/$(id -u)/com.sina.brain-loop-autorun-v1"
rm -f ~/.sina/brain-autonomous-deploy-v1.flag
```

## Fallback (Desktop only)

If you must use `~/Desktop/SourceA` under launchd: System Settings → Privacy & Security → Full Disk Access → add `/bin/bash`. **Not recommended** — use the worktree install instead.
