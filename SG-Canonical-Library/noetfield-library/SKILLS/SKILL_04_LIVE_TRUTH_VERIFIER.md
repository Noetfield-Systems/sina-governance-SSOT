# SKILL_04_LIVE_TRUTH_VERIFIER

## Purpose
Prevent false PASS receipts and repo/live drift.

## Truth formula
```text
LIVE TRUTH = repo source + commit hash + deploy marker + live browser/HTML verification + tests
```

## Required checks
- route returns 200
- expected copy visible
- protected CTAs visible
- expected removals absent
- build marker matches deploy
- tests pass
- monitor pass

## Output
```yaml
live_truth:
  repo_commit:
  deploy_marker:
  live_routes:
  html_evidence:
  protected_features:
  tests:
  status:
```
