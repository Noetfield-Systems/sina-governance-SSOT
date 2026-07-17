# Wave 0 — NF Unified Motor Merge Packet (SG founder checklist)

**Status:** READY_FOR_FOUNDER_MERGE (single-purpose branch)  
**Purpose:** Land `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` on SG `main` so the authority SHA is an ancestor of canon and T0 foundation may build.  
**Saved at:** 2026-07-17T08:49:38Z  
**SG lane answer to NOOS:** Persist Wave 0 + T0 commission **here in SG** (`docs/dispatch/`). Do **not** treat `noetfeld-OS/docs/_NOOS_AGENT/` as authority. After merge, NOOS may add only `noetfield.sg-authority-ref.v1` + custody re-pin (founder-gated).

---

## Hygiene decision (SG)

| Option | Verdict |
|--------|---------|
| (a) Merge bundled doctrine branch as one batch | **Rejected for Wave 0** — would land LinkedIn lock, exception ledger, P0PGR outbox with Motor |
| (b) Clean single-purpose branch | **Adopted** — `doctrine/nf-unified-motor-v1-wave0` from `origin/main@ed25f459ab9d` |

Bundled branch `doctrine/nf-unified-motor-architecture-v1` remains historical. Its SG-accept commit `8b476f721b1fe21f16036c84437f16de60434618` is **prior_accept_sha** (not the Wave 0 land SHA).

After this PR merges, update machine JSON `sg_authority_sha` to the **land commit on main** (or keep land commit as authority if content-identical stamp commit follows).

---

## Verified state (pre-merge)

| Thing | Value |
|-------|-------|
| SG `main` HEAD | `ed25f459ab9d92bdd91a644559a92be9e5e922e5` |
| Clean Wave 0 branch | `doctrine/nf-unified-motor-v1-wave0` |
| Prior accept (dirty branch) | `8b476f721b1fe21f16036c84437f16de60434618` |
| Machine decision | `SG_ACCEPTED` / `IMPLEMENTATION_AUTHORIZED` / `NF-UNIFIED-MOTOR-V1-FOUNDATION` |
| In scope | Finalization Gate + Unified Motor packet + waves + dispatch + wiring + Wave 0 + T0 commission |
| Out of scope | Founder LinkedIn, exception ledger, P0PGR-20260716-001 (remain on other branches) |

---

## Steps (SG lane / founder)

1. Open PR: `doctrine/nf-unified-motor-v1-wave0` → `main`
2. Confirm no ACTIVE-decision conflict (packet: consolidates Client-Zero into profile)
3. Founder merges to `main`
4. On `main`: `bash scripts/verify_nf_unified_motor_wiring_v1.sh` → must PASS
5. Confirm authority SHA is ancestor of `origin/main`:
   ```bash
   git merge-base --is-ancestor <sg_authority_sha> origin/main && echo CANONICAL
   ```
6. Write merge receipt (shape below) into P99
7. **Then** NOOS: custody re-pin + `noetfield.sg-authority-ref.v1` pointer (not before)

---

## Merge receipt shape

```json
{
  "schema": "noetfield/sg-doctrine-merge-receipt-v1",
  "decision_id": "NF-UNIFIED-MOTOR-ARCHITECTURE-V1",
  "authority_sha": "<sg_authority_sha after land>",
  "prior_accept_sha": "8b476f721b1fe21f16036c84437f16de60434618",
  "merged_from": "doctrine/nf-unified-motor-v1-wave0@<tip>",
  "merged_into": "main",
  "sg_main_before": "ed25f459ab9d92bdd91a644559a92be9e5e922e5",
  "sg_main_after": "<merge commit SHA>",
  "wiring_verifier": "verify_nf_unified_motor_wiring_v1.sh = PASS",
  "bundled_decisions": ["NF-UNIFIED-MOTOR-ARCHITECTURE-V1"],
  "excluded_from_this_merge": [
    "founder_linkedin_upgrade_plans_v1",
    "founder-exception-ledger-v1.1",
    "P0PGR-20260716-001"
  ],
  "note": "Agentic Cost-Efficiency already on main via PR #14; not re-landed here",
  "merged_by": "founder",
  "merged_at": "<UTC>"
}
```

---

## Wave 0 = DONE when

- authority SHA is an ancestor of SG `main`
- `verify_nf_unified_motor_wiring_v1.sh` PASS
- merge receipt in P99
- NOOS custody re-pinned (founder-gated)
- authority-ref pointer added in noetfeld-OS

**Only then** is T0 foundation authorized to build (`docs/dispatch/nf-unified-motor-v1-foundation-commission.md`).
