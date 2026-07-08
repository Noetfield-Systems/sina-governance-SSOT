# LIVING_SYSTEM_DOCTRINE v1.1

**Status:** LOCKED
**Filename:** `LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md`
**Tier:** P0-CORE (confirmed)
**Owner:** Founder (Sina) — L5 authority
**Supersedes:** none (new organ-level doctrine; complements SSOT v6, FOUNDER_CANON v1, AGENT_LAYERED_LAW, MACHINE_LOOPS_v1, NOOS proposal)
**Cross-binds:** governed-autorun L1–L13 (esp. L2, L4, L5, L11, L12)
**Date:** 2026-07-06
**Ratified:** 2026-07-07 (SG W0 lock pass)
**Execution matrix:** `docs/LIVING_SYSTEM_110_UPGRADE_PLANS_v1_LOCKED.md` · `data/living_system_110_plans_v1_LOCKED.json`

---

## 0. The Single Axis

Every entity — team, job, product, company, workflow — is judged on one axis:

> **LIVING SYSTEM or STALE.**

This doctrine defines what "living" means precisely enough to be machine-checked, so the axis is a rubric, not a vibe.

---

## 1. The Five Components of a Living System

```text
Living System = Body + Pulse + Homeostasis + Metabolism + Receipts
```

| Component | Definition | Instances in stack | Failure mode |
|---|---|---|---|
| **Body** | 24/7 loops, workers, queues, repos, endpoints | FBE motor, Railway workers, CF Workers, D1, repos | Can churn internally with no effect |
| **Pulse** | Crons, triggers, gates, reminders, machine prompts, machine enforcement | CF cron ticks, Railway schedulers, approval gates | Can fire without changing anything (ritual) |
| **Homeostasis** | Internal medical layer: sensors → diagnosers → healers → verifiers → escalator | NOOS (proposed, unratified) | Can heal its own thermometer (forged vitals) |
| **Metabolism** | External reality entering the system: buyers, partners, verifiers, users | D-U-N-S, Signal Factory intake, ACG page | Missing = commercially stale despite motion |
| **Receipts** | Disk/live proof the system changed or recovered | HMAC-chained receipts, ledgers, drill receipts | Weak if only internal (see §4) |

**Corrected principle:** 24/7 loops are NOT fake life by default. They are the body. The failure is not loops; the failure is **loops with no external provocation and no mutation**. Internal motion is necessary but insufficient.

---

## 2. Two Circulatory Systems (never conflate)

| Axis | Purpose | Prevents | Primary receipt |
|---|---|---|---|
| **Metabolism** | Outside input enters and mutates the system | Market/reality staleness | Stranger objection, buyer reply, payment, external verification |
| **Homeostasis** | Internal pulse-check and self-repair | Operational/workflow staleness | Sensor → diagnosis → heal → live verification receipt chain |

These are orthogonal. Perfect homeostasis with zero metabolism = a healthy corpse in a sealed room. Metabolism with no homeostasis = a fed body that bleeds out from every wound. Both organs are mandatory; they are built, governed, and drilled separately, in **parallel lanes** (governed-autorun lane isolation applies — one lane's failure never blocks the other's slot).

---

## 3. The Liveness Ladder (metabolism axis)

Each rung requires a stranger to spend something scarcer. Rung = cost-of-touch.

| Rung | Receipt | Proves |
|---|---|---|
| 1. **Credential metabolism** | D-U-N-S / domain / deployment / registration proof | Entity exists |
| 2. **Signal metabolism** | Inbound message classified, routed (Signal Factory) | Membrane exists |
| 3. **Provocation metabolism** | System pushes priced offer at named stranger | Bloodstream exists |
| 4. **Objection metabolism** | Stranger says no / too expensive / confused / irrelevant | Offer-contact exists |
| 5. **Mutation metabolism** | Copy, pricing, ICP, product, or workflow changes from objection, with receipt | Learning exists |
| 6. **Buyer metabolism** | Demo, LOI, pilot, payment | Revenue organ exists |
| 7. **Retention metabolism** | Repeat use / renewal / referral | Business organism exists |

**Current stack position (2026-07-06):** Rungs 1–2 receipted. Rung 3 not yet running on schedule. Rungs 4–7 empty.

**Doctrine:** objection is a cleaner first commercial receipt than payment. Payment can arrive via pity or network; objection only arrives via evaluation of the offer.

**Low-information intake rule:** unsolicited inbound (vendor spam, cold pitches) proves the membrane, not the offer — senders are pushing their offer, not evaluating yours. Rung 3+ requires a **provocation surface**: something a named stranger reacts to with yes/no/objection about a priced Noetfield offer.

---

## 4. The Unforgeable Vital Sign Law

Every internal signal — cron heartbeat, gate pass, health audit, agent report, machine enforcement — **can in principle be forged by the machine itself**. Precedent on disk: commit `239c8b5` (agent forged L5 founder sign-off into the governance ledger).

Therefore:

1. **Internal rejuvenation is permitted for the body.** Layers may repair each other under §5 rules.
2. **Liveness status may only be ASSERTED from receipts that crossed the membrane** — external verification, stranger contact, live public-surface probes the building agent does not control (governed-autorun L4).
3. **Health workers report health; they never declare life.**
4. External provocation is the only unforgeable vital sign in the system.

---

## 5. Homeostasis Organ (NOOS lane) — Smart Self-Healing Model

Classified self-healing, never improvised auto-repair.

| Role | Job | MUST NOT |
|---|---|---|
| **Sensor / Auditor cron** | Compare live endpoints, disk state, queues, mirrors, receipt freshness against invariants; write symptom receipt | Fix anything; declare life; read agent self-reports as evidence |
| **Diagnoser** | Map symptom → known failure class; dispatch healer | Improvise on unclassified failures |
| **Healer** | Execute bounded, pre-approved repair recipe for its class | Modify sensors, ledgers, verifiers, or other healers |
| **Verifier** | Confirm repair from the live surface | Accept healer self-report |
| **Escalator** | Page founder only on unknown failure class or repeated heal failure | Block known auto-heal classes |

**Immune write-isolation constraint:** the repair layer and the measurement layer are write-isolated from each other. A healer that can touch a sensor or ledger is a forger-in-waiting (the `239c8b5` lesson, applied internally).

**Domino chain (per incident):**
```text
sensor symptom receipt → diagnosis receipt → heal action →
live verification receipt → (unknown class? → founder page)
```
Machine-driven end-to-end; founder paged only on unknown classes.

**Ratification rule (progressive trust):** one drill receipt ratifies **one auto-heal class** and proves the chain pattern end-to-end. It does not ratify the organ. The homeostasis organ becomes progressively trusted as more failure classes pass deliberate drills (kill-on-purpose → detect → repair → verify → receipts kept). Each new healer class requires: policy entry + drill receipt before write authority (mirrors governed-autorun bootstrap §observe→control).

**Unblock path for NOOS:** write the self-heal policy file (auto-healable classes vs escalation classes) → run one deliberate drill on one class → keep the receipt chain → lane is ACTIVE for that class.

---

## 6. Commercial Pulse Loop v0.1 (metabolism lane)

**First target is NOT revenue.** First target:

> **1 priced-offer objection from a stranger, on disk, within 7 days of lane activation.**

**Compliant machine path** (human approval gate on all external sends per TrustField doctrine; CASL applies to outbound to strangers in Canada — mailing address + unsubscribe on every send):

```text
cron → select named ICP stranger → draft priced provocation
     → queue for founder approval (L5 gate)
     → approved? send + send-receipt : block-receipt
     → wait window → classify reply / objection / silence
     → mutation input → offer/copy/ICP change + receipt
     → schedule next provocation
```

The cron owns everything **except the send**. The approval receipt + send receipt pair is a stronger liveness proof than an autonomous blast, and keeps the loop legal.

**Kill condition / stale-gate receipt:** if 7 days pass with **at least one dispatchable, approval-ready priced provocation queued** and **zero approved sends**, the machine writes the receipt `FOUNDER_IS_THE_STALE_GATE` — the blocker is the L5 approver, not the system. This receipt is mandatory and non-suppressible (governed-autorun L7 spirit: founder items get louder, never vanish).

**Dispatchable (machine-checkable definition):** a queued draft is dispatchable iff ALL hold:
- named ICP stranger (real, identified target)
- priced offer attached
- correct company identity (entity hygiene across product names)
- required compliance fields present (CASL: mailing address + unsubscribe)
- no false claims, no broken links (link check receipt attached)
- approval metadata present
- queued inside the declared approval window

This precondition does not make the stale-gate suppressible; it prevents a bad worker from weaponizing garbage drafts into a false stale-founder receipt.

**Anti-inversion guard:** dispatchability is verified by machine check, never by the drafting agent's self-report (L4 spirit). A draft failing dispatchability writes its own `MALFORMED_DRAFT` receipt with the failed fields — garbage drafts are visible, never silently voided. If 7 days pass with **zero dispatchable drafts produced**, the receipt is `WORKER_IS_THE_STALE_GATE`. The stale-gate always names someone; it never goes quiet.

---

## 7. Anti-Over-Ratification Clause

Prohibited stance: "NOOS cannot move until all self-heal classes are proven."
Prohibited stance: "No outbound until homeostasis is complete."

Operating stance:

> **Start one bounded self-heal class, prove it with one drill, expand the immune library — while Commercial Pulse runs in parallel. Survival = moving, running, learning, healing in parallel.**

Homeostasis work is never a sales blocker. Metabolism work is never a health blocker. Lanes are isolated.

---

## 8. Liveness Rubric (machine-checkable)

A subsystem is **LIVING** iff, within its declared window, it has on disk:

- [ ] ≥1 pulse receipt from a scheduled (not manual) trigger — governed-autorun bootstrap rule: manual green ≠ cron green
- [ ] ≥1 externally-verified receipt (L4-grade probe) OR ≥1 membrane-crossing receipt (rung ≥2)
- [ ] ≥1 mutation receipt (something changed because of input) OR a valid IDLE_NO_WORK receipt (L2 — empty queue is healthy, silence is not)
- [ ] zero unresolved DRIFT receipts older than the freshness window (L12)
- [ ] for homeostasis-covered classes: last drill receipt within drill-refresh window

Anything failing the rubric is **STALE** by definition, regardless of internal motion, agent narrative, or report prose.

---

## 9. Amendments Log

| Ver | Date | Change | Authority |
|---|---|---|---|
| v1 | 2026-07-06 | Initial lock: five components, two axes, 7-rung ladder, unforgeable-vital-sign law, homeostasis roles + write-isolation, per-class drill ratification, Commercial Pulse v0.1 + stale-gate receipt, anti-over-ratification clause, liveness rubric | Founder (pending signature) |
| v1.1 | 2026-07-06 | §6 patch (founder-directed): stale-gate fires only with ≥1 dispatchable draft queued; machine-checkable dispatchable definition; anti-inversion guard (`MALFORMED_DRAFT` + `WORKER_IS_THE_STALE_GATE` receipts) | Founder — signature approved on this version |

---

*Doctrine is stale the moment it stops receiving receipts against it. This document is itself subject to §8.*

---

*v1.1_LOCKED (2026-07-07) — SG install + W0 cross-bind. Subject to section 8 rubric.*
