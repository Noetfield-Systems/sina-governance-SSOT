# Commercial Pulse Loop v0.1 — Machine Spec

**Status:** LOCKED spec (LS-051)  
**Parent:** `P0-CORE/LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md` §6  
**Lane:** metabolism (parallel to homeostasis — never blocks heal work)  
**Plans:** LS-051–LS-070 · `data/living_system_110_plans_v1_LOCKED.json`

---

## 0. First target (not revenue)

> **1 priced-offer objection from a stranger, on disk, within 7 days of lane activation.**

Objection is a cleaner first commercial receipt than payment (doctrine §3).

---

## 1. State machine

```text
IDLE
  → select_icp_stranger
  → draft_provocation
  → validate_dispatchable
      ├─ FAIL → MALFORMED_DRAFT receipt → draft_provocation
      └─ PASS → queued_for_approval
  → founder_approval_gate (L5)
      ├─ rejected → block_receipt → IDLE
      └─ approved → send (founder/manual or approved send Scheduler and executor)
  → send_receipt
  → wait_reply_window
  → classify_reply
      ├─ objection → objection_receipt (rung 4) → mutation_input
      ├─ silence → silence_receipt → IDLE
      └─ positive → buyer_track (rung 6 prep)
  → mutation_receipt (rung 5, when copy/ICP/offer changes)
  → schedule_next → IDLE
```

**Cron owns:** select, draft, validate, queue, classify, mutation input, schedule.  
**Cron never owns:** send (L5 gate + CASL compliance).

---

## 2. Receipt types

| Receipt | When | Proves |
|---------|------|--------|
| `commercial_pulse_draft` | Cron produces draft | Worker motion |
| `MALFORMED_DRAFT` | Dispatch check fails | Anti-inversion; failed fields listed |
| `commercial_pulse_queued` | Dispatchable draft in approval queue | Stale-gate precondition |
| `commercial_pulse_approval` | Founder approves or blocks | L5 gate |
| `commercial_pulse_send` | Approved send completed | Rung 3 provocation |
| `commercial_pulse_classify` | Reply/objection/silence classified | Rung 4+ signal |
| `metabolism_rung3` | First priced provocation sent | Bloodstream exists |
| `metabolism_rung4_objection` | Stranger objection on disk | Offer-contact exists |
| `metabolism_rung5_mutation` | Offer/copy/ICP changed from input | Learning exists |
| `FOUNDER_IS_THE_STALE_GATE` | 7d + dispatchable queued + zero sends | L5 approver blocker |
| `WORKER_IS_THE_STALE_GATE` | 7d + zero dispatchable drafts | Worker blocker |

Stale-gate receipts are **mandatory and non-suppressible** (governed-autorun L7 spirit).

---

## 3. Dispatchable definition (machine-checkable)

A queued draft is **dispatchable** iff **all** hold:

1. Named ICP stranger (real, identified target)
2. Priced offer attached
3. Correct company identity (entity hygiene)
4. CASL fields: mailing address + unsubscribe
5. No false claims; link-check receipt attached; links live
6. Approval metadata present
7. Queued inside declared approval window

Verified by `scripts/commercial_pulse_dispatch_check_v1.py` — **never** drafting agent self-report (L4 spirit).

---

## 4. Data artifacts (LS-052+)

| File | Role |
|------|------|
| `data/commercial_pulse_queue_v1.json` | Draft / approval / send states |
| `data/commercial_pulse_icp_v1.json` | Named stranger targets |
| `data/commercial_pulse_offers_v1.json` | Priced SKUs (e.g. ACG Tier 1 audit) |
| `data/metabolism_ladder_state_v1.json` | Current rung + receipts |

---

## 5. Motors (cloud-first)

| loop_id | Cadence | Owns |
|---------|---------|------|
| `cf_cron_commercial_pulse_draft_v1` | daily | draft + queue + validate |
| `cf_cron_commercial_pulse_stale_gate_v1` | daily | 7d stale-gate evaluator |
| `cf_cron_commercial_pulse_classify_v1` | */6h | reply classification (post-send) |
| `cf_cron_commercial_pulse_mutate_v1` | on objection | mutation receipt (rung 5) |

**Deadman:** `sourcea-deadman-v1` · **Registry:** `data/trigger-registry-v1.json` (L14 co-commit)  
**Mac:** complement only — `scripts/commercial_pulse_approve_v1.sh` for L5 approval CLI

---

## 6. Compliance

- **TrustField / CASL:** mailing address + unsubscribe on every outbound to strangers in Canada
- **Entity hygiene:** no competitor-name leakage across product files
- **No autonomous blast:** approval + send receipt pair required

---

## 7. Low-information intake rule

Unsolicited inbound (vendor spam, cold pitches) proves **membrane** (rung 2), not offer evaluation. Rung 3+ requires **provocation surface** — named stranger reacts to **priced Noetfield offer**.

---

## 8. Closed loop

```text
Observe (queue + replies) → Detect (classify / stale-gate) → Critique (dispatch check)
→ Repair (mutation / MALFORMED_DRAFT visible) → Re-deploy (next provocation) → Observe
```

---

## 9. Done when (M5 / M6)

| Milestone | Plan | Proof |
|-----------|------|-------|
| Cron live + heartbeat | LS-055 | `last_fired_at` in loop_registry |
| First dispatchable draft | LS-064 | `dispatch_check` PASS receipt |
| First send pair | LS-065 | approval + send receipts |
| First objection | LS-068 | `metabolism_rung4_objection` within 7d of LS-060 |

---

*v0.1 (2026-07-07) — LS-051 machine spec. Implementation: LS-052–LS-070.*
