# PRODUCT LAYER — Alive Doc Governance Audit

**Pattern:** `P9-PATTERN-FACTORY/alive-doc-staleness-governance-pattern-v1.md`  
**Machine:** `P8-MACHINE-LOOPS/agent-read-staleness-machine-v1.md`  
**SKU:** SG internal + client ops maturity audits

## Deliverable

Weekly (or on-demand) audit answering:

1. Which docs are **alive** for each agent lane?
2. Which ACTIVE laws carry **stale pointers**?
3. What is the prioritized **repair queue** with reasoning?

## Outputs

| Artifact | Consumer |
|----------|----------|
| `receipts/agent-read-staleness-*.json` | Founder, integrator |
| `data/governance_stale_pointer_queue_v1.json` | Agent repair lanes |
| GHA artifact upload | Cloud witness |

## Run

```bash
./scripts/run_agent_read_governance_cycle_v1.sh
```

Exit 0 = ACTIVE authority clean. Warnings = venture handoffs. Blockers = stop until SG law fixed.
