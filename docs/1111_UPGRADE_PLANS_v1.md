# 1111 Upgrade Plans v1

**Status:** LOCKED — execute top-down per plan; cross-plan deps noted.  
**Saved:** 2026-07-02  
**Parent lock:** [TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md](TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md)

Four parallel upgrade tracks (**1-1-1-1**): TrustField Loops · Signal Factory · SG/NOOS Sync · SourceA Brain Integration.

---

## Dependency graph

```
Plan 1 (TF Loops) ──► Plan 4 (Brain register TF artifact)
Plan 2 (SF v2)    ──► Plan 4 (pattern export from TF telemetry)
Plan 3 (SG/NOOS)  ──► Plan 1 Phase 2 (B2 regulated-term sign-off)
Plan 4            ──► consumes Plans 1–3 outputs
```

---

# PLAN 1 — TrustField Loops (physical autorun)

**Owner:** TrustField / SourceA Worker  
**Budget:** $0/month until revenue or ceiling breach  
**Blockers:** B1 (Phase 1 publish), B2 (Phase 2), B3 (paid spend)

## Phase 1 — Week 1: Intake + receipts

**Order:** TF-ARCH-W1

- [ ] Create isolated repo `trustfield-loops`
- [ ] D1 schemas: `signal`, `decision`, `receipt`, `memory_line`, `cost_event`, `route_event`
- [ ] Signal Intake Worker: webhook + shared-secret header + intake-email parser
- [ ] HMAC hash-chained receipt writer (append-only, no update/delete)
- [ ] Telegram alert function (alert only, no send)
- [ ] Preview deploy only — no production endpoints
- [ ] §15 test battery: synthetic signal → receipt → alert
- [ ] Receipt IDs for every test

**Done when:** Synthetic signal through preview endpoint → chained receipt → Telegram alert within 5 min.

**Gate:** B1 does not block preview; blocks publication of new intake email address.

## Phase 2 — Week 2: Triage + high-risk lane

- [ ] Triage Worker: deterministic regulated-term regex **before** model
- [ ] Workers AI Llama 3.3 70B classification + risk 0–5
- [ ] High-risk freeze lane → `route_events` → Telegram
- [ ] Full trap battery: ≥5 regulated-term traps → risk 5, zero reach standard lane

**Done when:** 100% trap pass, ≥90% overall classification vs manual labels.

**Gate:** **B2 required** — SG sign-off on regulated-term hard-stop list.

## Phase 3 — Week 3: Monitor + brief + cost

- [ ] Health/surface monitor cron 30 min (`/status-system`, `/register`, `/contact`, build tag v66)
- [ ] Daily brief cron 08:00 PT → Telegram
- [ ] Cost ledger + weekly threshold flags (60%/85% free-tier)

**Done when:** Kill-a-page test fires alert; brief arrives 5 consecutive days.

## Phase 4 — Week 4: Draft queues + rollup

- [ ] Draft-only queues (loops 4, 5) — no send API wired
- [ ] Weekly receipt rollup + hash-chain verifier
- [ ] Chain verifier in weekly brief (PASS/FAIL)

**Done when:** 1 weekly rollup receipt mirrored to GitHub; chain verifies.

## Phase 5 — Weeks 5–8: Supervised export + G6

- [ ] Pattern export dry-runs (4 supervised batches, loop 8)
- [ ] SG/NOOS weekly sync ritual established
- [ ] G6 reviews to promote loops 4, 5, 8 to autorun

**Done when:** T1–T4 targets from architecture §18 met or explicitly deferred with receipt.

## Phase 5+ targets (architecture §18)

| Target | Criterion |
|--------|-----------|
| T1 | Loops 4/5/8 promoted after G6 |
| T2 | Telegram approve→send v2 only after ≥50 manual sends |
| T3 | Cost per signal < CAD 0.01 for 4 weeks |
| T4 | Receipt chain verifier 8 consecutive weekly PASSes |
| T5 | First TF pattern reused in paid SourceA engagement |
| T6 | Uptime/behavior-probe for VERIFIED reliability claim |
| T7 | Immutability audit — no runtime regulated-term/receipt mutation |

---

# PLAN 2 — Signal Factory (skill → production triage)

**Owner:** SourceA Worker + Brain (registration optional v2)  
**Baseline:** `~/.cursor/skills/signal-factory/` — verifier ALL PASS (6/6)  
**Budget:** $0 — skill-only until adapter or inbox connection

## Step 1 — v1 lock maintenance (DONE)

- [x] SKILL.md core spec
- [x] Receipt schema JSON
- [x] SG guardrails pointer
- [x] Six-test structural verifier
- [x] Synthetic fixtures

**Proof:** `verify_signal_factory_v1: ALL PASS (6/6)`

## Step 2 — Real inbox fixtures (TARGET)

- [ ] Replace synthetic fixtures with 7+ anonymized real inbound examples
- [ ] Manual Sina labels as gold standard for classification agreement
- [ ] Extend verifier: fixture agreement ≥90% (human-labeled set)
- [ ] Do not connect Gmail/LinkedIn/APIs yet — paste-only capture

**Done when:** Real fixture directory + verifier PASS on structure + agreement report receipt.

## Step 3 — TrustField adapter (TrustField-owned)

- [ ] TrustField builds adapter content in `trustfield-loops` doctrine
- [ ] Populate `trustfield` hook slot from TrustField repo (not SourceA overwrite)
- [ ] High-risk routing rules TF-owned; export patterns one-way to SourceA
- [ ] Regulated-term list synced from SG guardrail #1

**Done when:** Adapter slot non-null in TF repo; SourceA skill hook remains pointer-only.

## Step 4 — Remaining adapters (TARGET, revenue-gated)

- [ ] `noetfield` — Copilot audit / Trust Brief lane
- [ ] `witnessbc` — when venture active
- [ ] `partnermesh` — partner API white-label
- [ ] `client_mvp` — scoped client pilot

**Done when:** Each adapter has owner venture + empty-by-default until venture dispatches.

## Step 5 — Signal Factory v2 (post first Discovery sale)

- [ ] Brain registration of skill artifact (if semantic delta from v1)
- [ ] Independent re-verify before register (Brain order amendment)
- [ ] Opus-class adversarial review on risk ≥ 4 (when AI budget exists)
- [ ] Cost per triaged signal metering in `cost_event` schema

**Done when:** Brain registry row + collision check receipt; cost < CAD 0.01/signal sustained 4 weeks.

---

# PLAN 3 — SG / NOOS sync ritual

**Owner:** Sina (approver) · SG/NOOS record-only  
**Status:** TARGET — non-blocking; one-shot order after Brain registration  
**Budget:** $0

## Step 1 — SG guardrail pointer file (partial DONE)

- [x] Five guardrails in `signal-factory/references/sg-guardrails-v1.md`
- [ ] Mirror append-only SG file in governance SSOT: `ssot/sg-guardrails-trustfield-v1.md`
- [ ] Regulated-term hard-stop list (§11.1) as machine-readable JSON for TF triage
- [ ] Sina sign-off on list → clears **B2**

**Done when:** B2 cleared with signed receipt; list in TF repo + SG mirror match.

## Step 2 — NOOS doctrine pointers

- [ ] Append-only NOOS file: `ssot/noos-doctrine-trustfield-v1.md` (seven lines from architecture §22)
- [ ] Pointer references in Signal Factory SKILL.md (already partial)
- [ ] Weekly Brain Brief includes one SG + one NOOS review pass

**Done when:** First weekly sync receipt with ≥1 distinct objection or explicit "none found."

## Step 3 — Correlated-agreement discipline

- [ ] Every weekly sync logs stress-test when SourceA/SG/NOOS agree
- [ ] No validation-by-consensus — distinct objection required or logged absent

**Done when:** 4 consecutive weekly sync receipts with discipline field populated.

## Step 4 — Claim ladder enforcement

- [ ] VERIFIED / DECLARED / PLANNED tags on any skill-generated external text
- [ ] T6 evidence gate before TrustField reliability claims upgrade to VERIFIED

**Done when:** Claim-class field in receipt schema v2 proposal (TARGET, not blocker).

---

# PLAN 4 — SourceA Brain + Loop Specialist integration

**Owner:** SourceA Brain (register) · Loop Specialist (plan)  
**Depends on:** Plan 1 Phase 1 complete · Plan 3 Step 1 for B2

## Step 1 — TF-ARCH-LS1 runtime plans

**Order:** Loop Specialist post-lock

- [ ] Runtime plans for loops 1, 2, 3, 9, 11, 12 only
- [ ] Per loop: cron/webhook config, registry entry, degradation order, synthetic probe, G6 checklist
- [ ] Do not plan loops 4, 5, 8 (dry-run)
- [ ] Flag any >$0 tier as cost brief line, not decision

**Done when:** Plan document + receipts; no deployed code from LS1.

## Step 2 — Brain registration (TrustField Worker artifact)

**Trigger:** After TF-ARCH-W1 Worker PASS

```text
Before registering: re-run the structural verifier against the
actual artifact files. Register only on independent PASS.
Worker's report is a claim, not a receipt.
```

- [ ] Register verified artifact + provenance in Brain registry
- [ ] Locked-definition collision check
- [ ] Independent structural verifier PASS (not Worker self-report)
- [ ] Memory line + receipt id emitted

**Done when:** Brain registry row exists; collision check PASS receipt.

**Note:** Signal Factory v1 skips this step (meaning complete per SF contract §9).

## Step 3 — Pattern export pipeline (TF → SourceA)

- [ ] Weekly batched export (loop 8 dry-run first 4 weeks)
- [ ] Anonymized; PII stripped; sender_declared claims → structure only
- [ ] SourceA classifies reusability; no back-flow as TF instruction
- [ ] G4: Sina reviews first 4 batches before autorun

**Done when:** T5 — first TF pattern reused in paid SourceA engagement.

## Step 4 — Loop registry consolidation

- [ ] One worker per loop rule enforced
- [ ] Monthly audit: unregistered crons killed
- [ ] Degradation order under free-tier pressure (intake never pauses)

**Done when:** Registry lists all TF deployed crons; monthly audit receipt.

## Step 5 — E2E matrix extension (optional TARGET)

- [ ] Add TrustField health probes to governance E2E matrix when loops live
- [ ] Synthetic behavior probe: inject signal → assert classification (Brain-leak class fix)

**Done when:** Matrix pass line includes TF probe or explicit HOLD with reason.

---

## 1111 execution priority (founder default)

| Priority | Plan | Next action |
|----------|------|-------------|
| **Now** | Plan 2 Step 1 | DONE — maintain verifier |
| **Next** | Plan 1 Phase 1 | Dispatch TF-ARCH-W1 |
| **Parallel** | Plan 3 Step 1 | Draft regulated-term JSON for B2 review |
| **After W1** | Plan 4 Step 2 | Brain register with independent re-verify |
| **Later** | Plan 4 Step 1 | TF-ARCH-LS1 Loop Specialist |

---

## Proof bundle (all four plans)

```bash
# Plan 2 baseline
/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py

# Plan 1 (when built)
# trustfield-loops/scripts/verify_phase1_v1.py  → ALL PASS

# Plan 3
# diff sg-guardrails mirror vs signal-factory reference

# Plan 4
# Brain registry query + collision check receipt
```

---

*v1.0 — 2026-07-02 — four parallel upgrade tracks derived from reconciled lock.*
