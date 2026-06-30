# SINA Governance SSOT

This repository is the remote advisory staging location for the SINA governance SSOT.

Current advisory checker:

- Reads `origin` with `git ls-remote origin HEAD`.
- Confirms the remote HEAD matches the expected commit.
- Reads `ssot/strategy-ssot-v6-split.md` from the remote commit.
- Computes the remote SSOT SHA256.
- Prints `REMOTE_CHECK_ADVISORY: MATCH` or `REMOTE_CHECK_ADVISORY: FAIL`.
- Supports JSON output with `--json`.

This checker is advisory only. It is not an independent D4 verifier and must not emit or imply PASS.

## Run

```sh
python3 check.py
```

For JSON output:

```sh
python3 check.py --json
```

By default, the expected remote HEAD is the current local `HEAD`. To check a specific commit:

```sh
python3 check.py --expected-head <commit-sha>
```
