# Commission — Software Repair Runway (parallel initial Runway)

**commission_id:** `NF-SOFTWARE-REPAIR-RUNWAY-V1`
**Status:** `IMPLEMENTATION_AUTHORIZED` · may build in parallel with Video and Research
**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1` v1.3
**Bootstrap builder:** Claude
**Concurrency:** one Job ↔ one isolated sandbox (git worktree)

## Objective

Plugin on shared Unified Motor: GitHubIssueAdapter · GitWorktreeSandbox · CodingWorkerAdapter · TestRunner · PullRequestAdapter.

## Acceptance proof

Real failing issue/test → isolated sandbox patch → relevant tests PASS → green candidate PR URL. No auto-merge. Must not mutate concurrent Video/Research sandboxes.

## Final status

`SOFTWARE_REPAIR_VERTICAL_SLICE_BUILT` or `SOFTWARE_REPAIR_BLOCKED_WITH_EXACT_CAUSE`
