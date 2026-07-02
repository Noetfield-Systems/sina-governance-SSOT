# 1111 Upgrade Plans v2 — ROI-ranked execution

**Status:** LOCKED — supersedes scheduling in v1; v1 scope unchanged.  
**Saved:** 2026-07-02  
**Parent:** [TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md](TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md) · [1111_UPGRADE_PLANS_v1.md](1111_UPGRADE_PLANS_v1.md)  
**Brain handoff:** [SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md](SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md)

---

## Analysis summary (v1 → v2)

| Finding | v1 gap | v2 fix |
|---------|--------|--------|
| Plans were phase-sequential | Under-used parallel lanes | **Wave model** — 3 waves, max parallel within wave |
| No ROI ranking | Equal priority felt | **value_class** on every step; revenue_path first when tied |
| Brain work buried in Plan 4 | Brain idle while Worker builds | **Brain Wave 1** tasks start now (registry pointer, memory template) |
| B2 blocked Phase 2 silently | Slow path | **regulated-term JSON draft** shipped (`data/regulated-term-hardstop-v1.json`) — SG sign-off only |
| Verifier PASS over-read | False confidence | Locked: structure ≠ judgment; real inbox = Wave 2 |
| Spend invisible until Phase 3 | Late cost surprises | **cost_event** from Wave 1 day 1; THROTTLED_ROI at 30% `none` |
| Pattern export far out | Delayed T5 revenue proof | **Export dry-run** moved to Wave 2 (week 3), not week 5 |

**ROI thesis:** TrustField is a **watched pattern surface** that feeds SourceA. Signal Factory is the **reusable triage engine**. First RPAA Discovery sale (CAD 4,000) funds ~12 months of $0–25 stack. Every hour spent before first signal captured is hygiene; every hour after first client signal is revenue_path or proof_asset.

---

## Value classes (apply to every step)

| Class | Meaning | Brain throttle |
|-------|---------|----------------|
| `revenue_path` | Direct line to Discovery / Integration sale | Never throttle |
| `proof_asset` | Receipt, pattern, verifier PASS sellable later | Never throttle |
| `risk_reduction` | Prevents Brain-leak, claim, or entity harm | Never throttle |
| `hygiene` | Maintenance, mirrors, docs | Throttle if >30% 7d spend |
| `none` | No measurable ROI | Auto-deprioritize |

---

## Wave model (fast + wise)

```
WAVE 0 ✅  Signal Factory v1 + lock docs + SG/NOOS mirrors
WAVE 1 ⟳  Parallel (now): TF Phase 1 preview · SF fixture paste · B2 JSON review · Brain registry pointer
WAVE 2     TF Phase 2–3 + real inbox + pattern export dry-run #1 + weekly brief
WAVE 3     TF Phase 4–5 + Brain register TF artifact + LS1 + G6 promotions
```

**Cycle-time targets:**

| Milestone | Target | Proof |
|-----------|--------|-------|
| First TF preview receipt | Wave 1, ≤5 days | receipt_id + chain hash |
| B2 cleared | Wave 1, ≤7 days | SG-signed regulated-term JSON |
| First real inbox fixture set | Wave 2, ≤14 days | agreement report ≥90% |
| First pattern export batch | Wave 2, ≤21 days | anonymized export receipt |
| T5 first pattern in paid SA engagement | Wave 3, ≤90 days | engagement receipt |

---

# PLAN 1 — TrustField Loops (ROI: proof_asset → revenue_path)

**Unit economics target:** cost per signal < CAD 0.01 on free stack.  
**Revenue unlock:** RPAA Discovery CAD 4,000 → funds paid tier without founder subsidy.

## Wave 1 — Intake proof (TF-ARCH-W1)

| Step | value_class | ROI note |
|------|-------------|----------|
| Isolated `trustfield-loops` repo | proof_asset | Blast-radius containment |
| D1 + HMAC receipt chain | proof_asset | Anti-Brain-leak substrate |
| Intake worker preview | proof_asset | Existing `/contact` webhook — no B1 block |
| Telegram alert only | risk_reduction | Zero send surface |
| Synthetic → receipt → alert | proof_asset | T6 behavior-probe seed |

**Done when:** receipt_id within 5 min of synthetic inject. **Skip:** new intake email (B1).

## Wave 2 — Triage + monitor (requires B2)

| Step | value_class | ROI note |
|------|-------------|----------|
| Regulated-term regex BEFORE model | risk_reduction | Deterministic — model can't under-score |
| Workers AI bulk triage | hygiene | Free tier; <$0.01/signal |
| High-risk freeze → Telegram | risk_reduction | FINTRAC-class inbound contained |
| Health monitor + daily brief | proof_asset | T6 uptime evidence collection starts |
| Cost ledger 60/85% alerts | risk_reduction | Prevents surprise paid tier |

**Done when:** 100% trap pass; brief 5 consecutive days.

## Wave 3 — Draft + export + promote

| Step | value_class | ROI note |
|------|-------------|----------|
| Draft-only queues (no send API) | revenue_path | Qualifies pilots without G1 violation |
| Pattern export dry-run ×4 | revenue_path | Feeds SourceA pattern library (T5) |
| G6 promotion loops 4/5/8 | revenue_path | Only after supervised batches |

**Kill criteria:** receipt chain FAIL → freeze writes. Free tier >85% → pause telemetry/briefs, never intake.

---

# PLAN 2 — Signal Factory (ROI: hygiene → proof_asset → revenue_path)

**Baseline:** `~/.cursor/skills/signal-factory/` — ALL PASS (6/6).

## Wave 1 — Pointer + paste fixtures (parallel now)

| Step | value_class | Status |
|------|-------------|--------|
| v1 skill + verifier | proof_asset | ✅ DONE |
| Brain registry pointer row (no collision) | proof_asset | Brain task B-01 |
| 7 paste-only real inbox fixtures | proof_asset | No Gmail OAuth — fast |
| Agreement report vs Sina labels | proof_asset | ≥90% target |

## Wave 2 — Pattern extraction live

| Step | value_class | ROI note |
|------|-------------|----------|
| Wire SF receipt schema to Brain memory_line format | proof_asset | One-line compounding |
| TrustField adapter hook (TF-owned content) | revenue_path | One-way export only |
| `create_service_pattern` gate on Discovery-shaped inbound | revenue_path | Maps to CAD 4,000 SKU |

## Wave 3 — v2 (post first Discovery sale)

| Step | value_class | Trigger |
|------|-------------|---------|
| Brain register if semantic delta | proof_asset | Revenue event names budget |
| Opus adversarial on risk ≥ 4 | risk_reduction | CAD 10/week AI cap until revenue |
| cost_event per triage | hygiene | ROI dashboard |

**Brain skip v1:** meaning complete. **Brain required v2:** only if schema or doctrine delta.

---

# PLAN 3 — SG / NOOS (ROI: risk_reduction — cheap, high leverage)

## Wave 1 — Machine-readable guardrails (parallel now)

| Step | value_class | Status |
|------|-------------|--------|
| SG mirror `ssot/sg-guardrails-trustfield-v1.md` | proof_asset | ✅ DONE |
| NOOS mirror `ssot/noos-doctrine-trustfield-v1.md` | proof_asset | ✅ DONE |
| `data/regulated-term-hardstop-v1.json` | risk_reduction | ✅ DRAFT — SG sign-off clears B2 |

## Wave 2 — Weekly sync ritual

| Step | value_class | ROI note |
|------|-------------|----------|
| Brain Brief includes SG + NOOS pass | hygiene | 15 min/week |
| Correlated-agreement stress-test log | risk_reduction | Prevents consensus laundering |
| Claim ladder on generated text | risk_reduction | VERIFIED/DECLARED/PLANNED |

**Done when:** B2 signed + first weekly sync receipt with objection or "none found."

---

# PLAN 4 — SourceA Brain + Live Brain (ROI: compounding flywheel)

**Live Brain today:** `sourcea-brain-chat-v1` · bundle on `main` · autorun matrix ALL PASS baseline.

## Brain work queue (ROI order)

| ID | Task | value_class | Wave | Depends |
|----|------|-------------|------|---------|
| B-01 | Register Signal Factory as **read-only pattern reference** in knowledge bundle pointer table (not live doctrine) | proof_asset | 1 | SF verifier PASS |
| B-02 | Add `signal_factory_receipt_v1` memory_line template to bundle schema docs | proof_asset | 1 | B-01 |
| B-03 | Prepare `pattern_export` sandbox row in registry (HOLD until TF export exists) | hygiene | 1 | none |
| B-04 | Independent re-verify + register `trustfield-loops` artifact post W1 | proof_asset | 3 | TF-ARCH-W1 PASS |
| B-05 | Locked-definition collision check on TF register | risk_reduction | 3 | B-04 |
| B-06 | Classify first TF export batch reusability (one-way) | revenue_path | 2 | export dry-run #1 |
| B-07 | TF-ARCH-LS1 consume — runtime plans to registry desired-state | proof_asset | 3 | B-04 |
| B-08 | Extend E2E matrix: SF verifier + TF health probe when live | proof_asset | 2–3 | TF Phase 3 |

## Registration law (locked)

```text
Worker report = claim, not receipt.
Brain registers only after independent structural verifier PASS on artifact bytes.
Signal Factory v1: skip (meaning complete).
TrustField loops: mandatory post-build.
```

## Live Brain motors (do not duplicate)

| Motor | Cadence | Brain role |
|-------|---------|------------|
| CF auto-runtime tick | */10 | Verifier bundled |
| Loop specialist tick | */15 | Plan consumer only |
| Mac brain-loop autorun | 30m | Matrix + promote |
| GH Actions brain-loop | */30 | CI mirror |

Brain **routes and registers**; it does **not** build TF loops or write TF doctrine.

---

## Parallel execution board (founder view)

| Lane | Now | Owner | value_class |
|------|-----|-------|-------------|
| A | TF-ARCH-W1 preview | Worker | proof_asset |
| B | Paste 7 real inbox → SF fixtures | Sina + Worker | proof_asset |
| C | SG sign B2 regulated-term JSON | Sina | risk_reduction |
| D | Brain B-01/B-02 registry pointers | Brain | proof_asset |
| E | TF-ARCH-LS1 plan doc | Loop Specialist | hygiene |

Lanes A+B+C+D run **in parallel**. E after A preview PASS.

---

## ROI scorecard (review weekly in Brain Brief)

| Metric | Target | Source |
|--------|--------|--------|
| Cost per triaged signal | < CAD 0.01 | cost_event |
| Free-tier ceiling max | < 60% any meter | cost brief |
| Trap battery pass | 100% | TF triage tests |
| Real fixture agreement | ≥ 90% | SF verifier extension |
| Pattern exports to SourceA | ≥ 1 batch/week (Wave 2+) | export receipt |
| Receipt chain verifier | weekly PASS | rollup receipt |
| Revenue events | ≥ 1 Discovery path signal/quarter | CRM/tracker |

**Upgrade trigger (G5):** paid tier only when brief shows ceiling breach imminent OR revenue event names upgrade.

---

## Proof bundle v2

```bash
# Signal Factory structure
/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py

# Brain domain registry
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/validate_brain_domain_registry_v1.py

# Full matrix (when ship window)
bash ~/Projects/sina-governance-ssot/scripts/validate_brain_domain_e2e_matrix_v1.sh

# B2 draft present
test -f ~/Projects/sina-governance-ssot/data/regulated-term-hardstop-v1.json && echo B2_DRAFT_OK
```

---

*v2.0 — 2026-07-02 — ROI-ranked waves; supersedes v1 scheduling only.*
