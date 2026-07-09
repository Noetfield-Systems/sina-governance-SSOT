# P0 DISPATCH ROUTER RULES — v1

**Status:** ACTIVE · governed by `p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`

## Allowed routes

| Route | Meaning | Rails |
|---|---|---|
| `CLOUD_WORKER` | Cloud coding/execution agent (default) | nine gates, evidence artifacts required |
| `CLOUD_RESEARCH` | Cloud read-only research/fetch agent | read-only, artifact per URL claim |
| `SESSION_EMBEDDED` | Operator executes inside a founder-visible session | light shell law (INCIDENT-039), accounting_note required |
| `REVIEW_QUEUE` | Parked for founder review | no execution |

## Labels (not routes)

- `HOLD_CLOUD_UNSAFE` — work that cannot be made cloud-safe yet. A label, not a
  block: the packet stays in the outbox, visible and re-rankable.

## Forbidden routes — Mac safety

- `MAC_RUNNER` — never. The Mac is the cockpit, not a runner.
- `HYBRID_MAC` — never, including as fallback.

The linter rejects packets declaring either. The cycle runner refuses to route
them and files a repair candidate.

## Routing decision order

1. Packet malformed or lint-rejected → `REPAIR_CANDIDATE` (lane continues)
2. `cloud_only` gate false → label `HOLD_CLOUD_UNSAFE`
3. Any other gate false (incl. missing founder receipt) → `QUEUED_FOUNDER_REVIEW`
4. All nine gates pass → `ROUTED` to the packet's declared route

## Session-embedded rail (Mac founder session, INCIDENT-039)

Max one light shell ≤ 90s per turn. No validator marathons on Mac. Heavy work
routes to cloud.
