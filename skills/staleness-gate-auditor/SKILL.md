---
name: staleness-gate-auditor
description: >
  Check whether the "alive docs" this governance system depends on (lane-entry
  files like AGENTS.md, registries like data/agent_read_surfaces_v1.json,
  doctrine docs, worker-routing files) are still current, or have quietly
  gone stale/retired while other docs kept pointing at them as authority.
  Use this whenever the user asks to "check staleness," "run the staleness
  gate," "is anything stale," "audit alive docs," before making a cross-lane
  decision that depends on a doc being current, after a doc gets marked
  RETIRED/LOCKED/superseded, or before trusting any file this system calls an
  "alive doc" or "authority file." Wraps
  scripts/verify_agent_read_staleness_v1.sh (and the underlying
  scripts/agent_read_staleness_engine_v1.py) so staleness receipts get read
  and interpreted correctly instead of skimmed for a bare PASS/FAIL.
compatibility: >
  Requires scripts/agent_read_staleness_engine_v1.py, data/agent_read_surfaces_v1.json,
  and data/stale_law_guard_patterns_v1.json to exist in the repo root. Python 3.
---

# Staleness Gate Auditor

This repo tracks a specific failure mode: a doc gets superseded, retired, or
locked to a new version, but other docs/agents keep citing the old one as
live authority because nobody told them it changed. `agent_read_staleness_engine_v1.py`
exists to catch that — it scans every "alive doc" registered in
`data/agent_read_surfaces_v1.json`, checks each one against stale-law patterns
in `data/stale_law_guard_patterns_v1.json`, and reports blockers (a doc that's
actively misleading) versus warnings (worth a look, not urgent).

## Running the gate

```bash
scripts/verify_agent_read_staleness_v1.sh
```

This is a thin wrapper around:

```bash
python3 scripts/agent_read_staleness_engine_v1.py --write-receipt --write-queue --fail-on blocker
```

- `--write-receipt` drops a timestamped receipt in `receipts/agent-read-staleness-<UTC>.json`
- `--write-queue` updates `data/governance_stale_pointer_queue_v1.json` with anything needing repair
- `--fail-on blocker` (the default) means the script exits non-zero only on
  blockers, not warnings — don't loosen this to `never` just to get a clean
  exit code; a warning is information, a suppressed exit code is not.
- Add `--json` for machine-readable output.

The wrapper only prints `verify_agent_read_staleness_v1: PASS` after the
underlying engine has already succeeded — so "PASS" here means zero blockers,
not zero issues at all. Check the receipt's `warn_count` too.

## Reading the receipt

Every run's receipt looks like:

```json
{
  "schema": "agent_read_staleness_receipt_v1",
  "at": "<UTC timestamp>",
  "ok": true,
  "alive_surfaces": <count>,
  "blocker_count": <int>,
  "warn_count": <int>,
  "alive": [ {"lane": "...", "path": "...", "status": "ACTIVE|READ_SURFACE", "role": "...", "last_modified": "..."} ]
}
```

Don't just report `ok` — walk through what it means:

1. **`blocker_count` > 0** is the case that matters most: some doc's content
   actively contradicts current law (a stale-law pattern matched an ACTIVE
   surface). This is not "eventually fix it" — a blocker means an agent could
   read that doc right now and make a decision based on wrong information.
   Name the specific file(s) and quote the matched pattern.
2. **`warn_count` > 0**: something's worth a look but isn't actively
   misleading yet (e.g. a doc hasn't been touched in a long time, or a
   READ_SURFACE doc — not authority, just referenced — shows a stale pattern).
   Report these as a punch list, not an emergency.
3. **`alive_surfaces` dropping between runs** is itself a signal — it usually
   means a doc that used to resolve (via `path` or `alt_paths` in
   `agent_read_surfaces_v1.json`) no longer does, which is its own kind of
   staleness (a registry pointing at a file that moved or got deleted).

## A blocker that isn't real: `missing_read_surface` outside this repo

Some alive docs live in sibling venture repos (SourceA, TrustField-Technologies,
noetfeld-OS) rather than this one. If the engine reports `blocker_count > 0`
with `kind: missing_read_surface` for a path under another venture's
workspace, check first whether *this session even has that repo on disk* —
a sandboxed/limited session that only has `sina-governance-ssot` checked out
will report every sibling-repo doc as a missing blocker, which is an artifact
of the environment, not real staleness. Only trust a `missing_read_surface`
blocker as real if you've confirmed the run had access to that venture's
actual repo path.

## Cross-lane awareness

`agent_read_surfaces_v1.json` registers alive docs across every lane (SG,
SourceA, TrustField, NOOS, Noetfield website), not just this repo. A path
under another venture's workspace failing to resolve doesn't mean you should
fix it yourself — per `AGENTS.md`'s "You do NOT edit" table, route that
finding to the owning lane's chat rather than reaching into their repo.

## Before trusting an "alive doc" mid-task

If you're about to make a decision that leans on a specific doc being
current (a lane boundary, a locked policy, a registry's routing truth), and
the last staleness receipt is more than a session or two old, re-run the gate
first rather than trusting a stale receipt about staleness — that's the one
place where an old check is actively counterproductive.

## After running

Don't declare "staleness checked, all good" from a bare exit code. State the
actual numbers (`alive_surfaces`, `blocker_count`, `warn_count`), name any
blockers explicitly, and point at the receipt path so the claim is checkable
later — same "claim vs. proof" standard the rest of this repo's governance
holds every motor to (L5, no motor reports DONE without a receipt_id).
