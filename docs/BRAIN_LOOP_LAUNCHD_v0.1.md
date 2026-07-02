# Brain Loop launchd — 24/7 autorun v0.1

Install a 6-hour Brain loop on macOS when Phase 3 Step 10 is LIFT.

## Prerequisites

- `~/.sina/brain-autonomous-deploy-v1.flag` exists (founder DECIDE)
- No active hold: `~/.sina/enforcement/brain-autonomous-hold-v1.flag`
- CF tokens load via `scripts/load_cf_tokens_v1.sh`
- SourceA at `~/Desktop/SourceA` on clean `main`

## Plist

Save as `~/Library/LaunchAgents/com.sina.brain-loop-autorun-v1.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.sina.brain-loop-autorun-v1</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/sinakazemnezhad/Projects/sina-governance-ssot/scripts/brain_loop_autorun_v1.sh</string>
  </array>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    <key>SOURCEA_ROOT</key>
    <string>/Users/sinakazemnezhad/Desktop/SourceA</string>
  </dict>
  <key>StartInterval</key>
  <integer>21600</integer>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>/Users/sinakazemnezhad/.sina/logs/brain-loop-autorun-v1.out.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/sinakazemnezhad/.sina/logs/brain-loop-autorun-v1.err.log</string>
</dict>
</plist>
```

## Install

```bash
mkdir -p ~/.sina/logs
launchctl unload ~/Library/LaunchAgents/com.sina.brain-loop-autorun-v1.plist 2>/dev/null || true
launchctl load ~/Library/LaunchAgents/com.sina.brain-loop-autorun-v1.plist
launchctl list | grep brain-loop-autorun
```

## Clear hold (manual)

After fixing the failure:

```bash
bash ~/Projects/sina-governance-ssot/scripts/validate_brain_domain_e2e_matrix_v1.sh
rm -f ~/.sina/enforcement/brain-autonomous-hold-v1.flag
```

## Disable

```bash
launchctl unload ~/Library/LaunchAgents/com.sina.brain-loop-autorun-v1.plist
rm -f ~/.sina/brain-autonomous-deploy-v1.flag
```
