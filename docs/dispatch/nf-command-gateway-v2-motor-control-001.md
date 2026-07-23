# Commission — NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001

**Dispatch to:** `noetfield-cloud-factory-infra` builders (Command Gateway Worker lane)  
**When:** after this packet is ancestor of SG `main`  
**Canonical decisions:**
- `NF-COMMAND-GATEWAY-V2-ARCHITECTURE-V1`
- `NF-SINAGPT-FOUNDER-BRAIN-ARCHITECT-V1`
- `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` (authority `dc6080d8519b8a83dcfaaeefb65392691ce3e33e`)

**Canonical SG main SHA (post PR #18):** `b72f5a3975b0170a1b4d9e09eea06cccc9c4acf0`  
**Decision artifact SHA:** `792eb6c6fdbf9b063b29dd5672ab66d91f9da37b`

**Status:** `IMPLEMENTATION_AUTHORIZED` · draft PR only · **no deploy**  
**Laws:** FOUNDER_CANON v1 + governed-autorun v3 + Architecture Finalization Gate  
**Receipts:** SUBMITTED for independent verification (author ≠ verifier)

---

## Preconditions

1. Read SG packets for SinaGPT role + Gateway v2 + Unified Motor.
2. Confirm their `sg_authority_sha` values are ancestors of `sina-governance-SSOT@main`.
3. Preserve all `/v1` behavior for compatibility.
4. Refuse if another ACTIVE SG decision conflicts.
5. Claim the Command Gateway implementation lane before editing.

## Build (13 items)

1. Preserve all `/v1` behavior for compatibility.
2. Add `/v2/cockpit`.
3. Add SG authority/decision reads.
4. Add issue and CI incident resources.
5. Add commission resources.
6. Add read-only Motor recipe/job/truth resources.
7. Strengthen founder approvals (kinds + subject_version).
8. Add `Idempotency-Key` to all mutations.
9. Move raw GitHub dispatch behind the internal API (not GPT Action surface).
10. Split SinaGPT read authentication (API key) from founder-command authentication (OAuth).
11. Add seven-dimensional Motor truth schema.
12. Add deterministic contract tests.
13. Stop at **draft PR**; no deployment.

## Forbidden

- Production deploy / flip `GATEWAY_MODE` live as part of this commission
- Discarding `/v1`
- Letting SinaGPT declare issue classification or `SG_ACCEPTED`
- Exposing merge/deploy/secret-rotate/bypass endpoints to GPT Actions

## Final status label

`GATEWAY_V2_DRAFT_FOR_FOCUSED_REVIEW`
