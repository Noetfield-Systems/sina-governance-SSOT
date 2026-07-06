# UNLOCK DOCTRINE v2.0_20260705

**Canonical path:** `P7-DOCTRINE/UNLOCK_DOCTRINE_v2.md`  
**Library analysis:** `P99-LEDGER/UNLOCK_DOCTRINE_LIBRARY_ANALYSIS_2026-07-06.md`  
**Status:** Draft for founder lock · **Supersedes:** graph model v1, PSA v1 (chat drafts)  
**Scope:** Portable (agentic-brain contexts). English-only. Receipt-native.

---

## §0 — Why v1 is retired

v1 modeled the system correctly and then optimized the wrong variable. It treated
V* (validator), D* (distribution), C* (capital) as three roles to be found, and
partner selection as a scoring problem over people. Both are unmeasurable before
revenue: Alignment, Trust, and Noise cannot be scored from conversation — v1
itself admits this ("real signal > conversation signal") and then keeps scoring
conversations anyway. v2 fixes the root: **the only instrument that measures
anything external is a transaction.**

---

## §1 — Axioms

**A1. Receipts over roles.** External actors are not roles to fill; they are
sources of receipts. A person's value to the system equals the receipts they
generate (payment, delivered work, injected traffic, signed commitment) — never
their title, promise, or conversational quality.

**A2. The market is the only validator.** No individual — however smart,
aligned, or senior — can validate the product. Only a payment can. Advice is
noise with good manners.

**A3. Trust is earned per-receipt, not assessed per-person.**
`T(x) = f(receipts exchanged with x)`. Initial T for any stranger is a small
constant — identical for everyone. No pre-scoring of humans. This deletes the
noise of judging candidates and the bias of past ecosystem damage in one move.

**A4. The founder does not sample the environment; the machine does.**
Environment noise harmed the founder because the founder was the intake surface.
The intake surface is now the signal pipeline (built, live). Humans reach the
founder only as scored verdicts.

**A5. One lock, not three.** The system has a single binding constraint:
zero payment receipts. V*, D*, C* are not three missing nodes — they are three
shadows of the one missing transaction.

---

## §2 — State model

```
S = { P, R, K, Φ }
P = product (SourceA / Brain Audit)      — status: exists, deliverable
R = payment receipts                      — status: 0   ← THE LOCK
K = capital runway                        — status: limited, function of R
Φ = external graph (validators, channels,
    partners, investors)                  — status: unmeasurable while R = 0
```

**Unlock condition:** `R ≥ 1`.
Not funding. Not a cofounder. Not ecosystem access. One payment receipt from a
stranger changes every other variable's type:

| Variable | at R = 0 | at R ≥ 1 |
|---|---|---|
| Product | claim | validated (someone paid) |
| Channel | hypothesis | proven (the one that produced R) |
| Capital | pitch for belief | pitch with evidence; or unnecessary |
| Partner search | outbound begging, unmeasurable | inbound filtering, receipt-measured |
| Founder position | asking | choosing |

**Corollary (anti-thrash).** While R = 0, the product does not get redesigned
for any audience (global vs local, enterprise vs SME). Every design oscillation
traced in the founder log came from trying to please a validator who had not
paid. The offer may be re-targeted; the product spec is frozen until the first
receipt says otherwise.

---

## §3 — The Transaction Theorem

**Claim.** The minimum external set that unlocks S is one paying stranger.

**Proof by construction.** Let stranger x pay for a Brain Audit.
- x is V*: they understood the offer well enough to exchange money — the only
  non-noisy comprehension signal that exists (A2).
- The channel that produced x is D* seed: it is now a proven, repeatable edge,
  not a hypothesis. Repetition of that channel is the distribution strategy.
- The payment is C* seed: revenue is non-dilutive capital, and one receipt
  converts every future capital conversation from belief to evidence.
- The delivery interaction with x is the first honest measurement device for
  Φ: how x behaves under a real contract generates the first true T values
  ever recorded in the system.

Therefore the "minimum spanning unlock graph" is not `{V*, D*, C*}`.
It is `{x, edge(offer→x), receipt(x)}`. ∎

---

## §4 — External Actor Algorithm (replaces PSA v1)

One algorithm for ALL external actors — leads, partners, cofounders,
investors, advisors. They are the same object: signal sources climbing a
receipt ladder.

### 4.1 The ladder

```
L0  SIGNAL      inbound/outbound contact          → triage verdict (machine)
L1  RESPONSE    they replied with substance       → T = 0.1
L2  MICRO       smallest real exchange:
                paid audit / concrete intro that
                converts / one shipped artifact   → T = 0.3, first A measurement
L3  REPEAT      second receipt, consistent        → T = 0.6, A confirmed or killed
L4  STRUCTURAL  equity / contract / capital       → founder-gated, doctrine event
```

### 4.2 The rules

**R1 — No level skipping.** No one reaches L4 (cofounder, investor, equity)
without L2 and L3 receipts. A brilliant stranger proposing partnership is an
L0 signal, nothing more. This single rule prevents every catastrophic
partner outcome the ecosystem ever produced.

**R2 — Only receipts promote.** Talk, enthusiasm, credentials, warm intros:
none of them move T or level. A calendar full of meetings is L0 traffic.

**R3 — The machine holds the queue.** Every external actor is a row in the
signals table with `{level, receipts[], T, last_receipt_at}`. Triage worker
scores L0. Founder sees verdicts. Stale rows (no new receipt in 30 days)
auto-demote one level. Nothing is remembered emotionally; everything is
remembered in the table.

**R4 — Noise is a kill condition, measured not felt.**
`N(x) = contradictions + commitments missed + words-to-receipts ratio`.
Two missed commitments at any level = retire the row (mirror of the
two-scope-failures session law). No third chances purchased with charisma.

**R5 — Alignment is measured only at L2+.** A (phase alignment) is defined as:
did working together produce the receipt faster or slower than working alone?
Faster → A high. Slower or ambiguous → A low, demote. It is a delta on
execution speed, not a feeling of good conversation.

### 4.3 What this deletes

- Candidate scoring spreadsheets (unmeasurable inputs)
- "Finding a cofounder" as a project (cofounders are L3 actors who emerge)
- Ecosystem-trust anguish as a decision input (A3 sets uniform priors;
  receipts do the rest; the past keeps its lessons but loses its veto)
- The three-roles-in-one-person unicorn search (v1's own identified trap)

---

## §5 — The Offer (the deterministic edge)

The founder's own diagnosis, verbatim: *the offer is not targeted,
deterministic, or professional.* That sentence is the entire go-to-market
problem, and it is a writing problem. Specification:

### 5.1 Offer invariants

```
NAME:      Brain Audit (fixed — no renaming per audience)
PRICE:     fixed, stated in the first message (no "book a call to discuss")
DELIVERY:  fixed scope, fixed duration (e.g. 5 business days)
PROOF:     the deliverable IS a receipt pack — machine-verifiable findings,
           the product demonstrating itself (self-proving thesis intact)
CTA:       pay/start link — never a discovery-call funnel
           (per website audit: call-funnels contradict the product thesis)
```

### 5.2 Target discipline

ONE audience per campaign. The dual-audience defect (SME + regulated
enterprise simultaneously, mechanism-jargon at buyer surface) is a locked
finding — it recurs because no verifier checks it. Rule: every outbound
artifact names its single audience in its receipt. An artifact that cannot
name its audience does not ship.

### 5.3 Channel receipts

Each channel is an experiment with a receipt:
`{channel, sent, replies, L1-conversions, L2-conversions (payments), cost}`.
Channels are promoted/killed on conversion receipts, exactly like Kaizen
queue items — highest-ROI channel gets the next batch, `value_class: none`
channels are throttled. Distribution strategy = the channel table, not a plan
document.

---

## §6 — Integration with the built machine

Nothing in this doctrine requires new infrastructure. It re-points what
shipped this week:

| Doctrine element | Existing component |
|---|---|
| L0 intake + triage | signals table + Signal Factory worker (live) |
| Receipt ledger per actor | signals/receipts schema (extend: level, T) |
| Verdicts to founder | Telegram ops bot (live) |
| Channel ROI table | improvement_queue pattern (clone for channels) |
| Daily proof of motion | 07:00 heartbeat — ADD: `offers_sent · replies ·
  L2_receipts · pipeline_by_level` |
| Anti-noise session law | two-failures-retire (R4 mirrors it) |

**Heartbeat amendment is the enforcement.** The machine reports commercial
motion every morning next to infrastructure health. A week of green checks
with `offers_sent: 0` is a RED week — the heartbeat must say so. Infrastructure
green + revenue-motion zero was the exact failure mode of the last quarter;
now it is a visible, daily, machine-reported state.

---

## §7 — Seven-day protocol (executable now)

```
D1  Write the offer per §5.1 — three sentences, price, link. Freeze it.
D2  Build the D1 target list: 25 names, ONE audience, one channel.
D3  Send 25. Log to channel table. (Machine catches replies via intake/sweep.)
D4  Triage replies; founder answers only L1+ verdicts.
D5  Second channel batch OR second 25 on channel one (whichever the
    receipt table says).
D6  Any L1 → push to L2: the paid audit, this week, calendar link, no
    free-work detour.
D7  Heartbeat review: offers, replies, L2 count. Kill/keep channels.
    Repeat.
```

**Stop conditions (fail-closed, founder-gated to change):**
- 100 offers, one audience, zero L1 → the OFFER is wrong (rewrite §5.1),
  not the product, not the ecosystem, not the founder.
- Any L2 receipt → §2 unlock condition met; partner/capital lanes reopen
  with evidence.

---

## §8 — One-line form

**Sell one Brain Audit to one stranger; let the machine filter everyone
else onto a receipt ladder; promote nobody without receipts; report
commercial motion in the same heartbeat as system health.**

Everything in v1 worth keeping survives inside this line. Everything else
in v1 was analysis standing where a transaction should be.
