# Commission — Parallel Sandbox Manager (Motor concurrency capability)

**commission_id:** `NF-PARALLEL-SANDBOX-MANAGER-V1`
**Status:** `IMPLEMENTATION_AUTHORIZED`
**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1` v1.3
**Target:** Unified Motor / builders — required for parallel Runway execution

## Objective

Teach the system to manage **parallel isolated sandboxes**:

```text
create sandbox per Job → run → observe → retry/repair → collect artifacts → destroy
with leak detection and NOOS per-Job visibility
```

## Acceptance proof

≥2 concurrent Jobs (any Runway mix), separate sandbox IDs, no shared mutable paths, independent results, NOOS sees both, destruction leaves no cross-Job residue.

## Final status

`PARALLEL_SANDBOXES_PROVEN` or `PARALLEL_SANDBOXES_BLOCKED_WITH_EXACT_CAUSE`
