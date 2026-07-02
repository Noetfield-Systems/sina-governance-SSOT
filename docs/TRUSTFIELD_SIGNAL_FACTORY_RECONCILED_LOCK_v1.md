# TrustField + Signal Factory — Reconciled Lock v1

**Status:** LOCKED — 2026-07-02  
**Authority:** High Architect + Worker receipt  
**Saved:** 2026-07-02T2040Z  
**Live surface baseline:** `www.trustfield.ca` build tag `site-v66-entity-truth-cleanup-2026-07-02`

---

## 0. One line

Two parallel tracks locked: **TrustField loops** (venture-owned watched surface, CF autorun v1) and **Signal Factory** (SourceA-owned reusable skill engine). TrustField is separate, not a child adapter. Capture/classify autoruns; external action never autoruns in v1. Brain post-build required for TrustField artifacts only; Signal Factory skips Brain (meaning complete).

---

## 1. Source documents saved (this lock reconciles)

| # | Document | Date | Status |
|---|----------|------|--------|
| A | Final TrustField E2E Autorun Architecture (§1–23) | 2026-07-02 | LOCKED |
| B | Amendment: Brain post-build mandatory + independent re-verify | 2026-07-02 | LOCKED |
| C | Signal Factory v1 final locked contract (§1–11) | 2026-07-02 | LOCKED |
| D | Worker deliverable: `~/.cursor/skills/signal-factory/` | 2026-07-02 | BUILT + VERIFIED |

---

## 2. Reconciliation table (contradictions resolved)

| Topic | Track A (TrustField) | Track B (Signal Factory) | Locked resolution |
|-------|---------------------|--------------------------|-------------------|
| TrustField identity | Separate venture; watched pattern surface | Empty hook slot `trustfield` only | Final wins: **separate + watched**. Adapter content is TrustField-owned TARGET. |
| Brain pre-build | Skipped for loop planning | Skipped (no semantic gaps) | Both: skip pre-build. |
| Brain post-build | **Required** — register artifact, provenance, collision check | **Not required** — meaning fully specified | **Track-specific.** TF loops: Brain registers after Worker. SF skill: Worker + verifier sufficient. |
| Registration trust | Worker report = claim; Brain re-runs structural verifier | Verifier IS structural proof | Same anti-laundering law: **independent PASS on bytes, not report.** |
| Eval 5 / optional gating | Loops 4,5,8 dry-run; human gate G1 | Single gating law: `build_automation` \| `create_service_pattern` | SF gating encoded in verifier T4. TF loops use human gates, not SF optional sections. |
| Blockers | B1 PII/legal, B2 regulated-term SG sign-off, B3 billing tags | None open | B1–B3 gate **TF phase promotion only**; do not block SF skill or TF preview build. |
| Entity boundaries | Six entities; cost tagged `entity: trustfield` | Six entities in every receipt | Aligned. No cross-attribution. |
| External send | Never in v1 (G1 Sina only) | Never in v1 (skill spec) | Aligned. |
| Production connections | Phase 1+ when unblocked | Explicit non-scope | SF ships spec only. TF Phase 1 can use existing `/contact` webhook. |
| Correlated agreement | GPT + Architect converged | Same | Stress-test logged, not validation. |

---

## 3. Execution sequence (locked)

```
Architect ✅
  → Worker (build)
  → Brain (register + independent re-verify)   [TrustField loops only]
  → SG/NOOS (pointer recording)                [TARGET — one-shot, non-blocking]
  → Loop Specialist (runtime plans)            [TF-ARCH-LS1 — later]
```

Signal Factory path (complete for v1 core):

```
Architect ✅  →  Worker ✅  →  Verifier ALL PASS (6/6)  →  STOP
```

---

## 4. Layer ownership (unchanged)

| Layer | Owner | Must never own |
|-------|-------|----------------|
| TrustField | TrustField venture | SourceA infra decisions, NOOS global law |
| SourceA | Noetfield | TF doctrine, TF claim language, TF risk thresholds |
| SG | Governance | Product roadmap, inbound replies, tooling |
| NOOS | Doctrine | TF product logic, TF data |
| Signal Factory core | SourceA Brain (meaning) / Worker (build) | TF doctrine, adapter content in v1 |

---

## 5. TrustField architecture summary (Track A)

**Surface:** `www.trustfield.ca` v66 verified — no-custody boundary, entity-in-formation, SKU ladder live.

**Real autorun (when built):** loops 1, 2→alert, 3, 9, 10, 11, 12.  
**Dry-run:** loops 4, 5, 8. **Manual:** loops 6, 7.

**Stack lock:** $0/month free-first (CF Workers + D1 + Workers AI + Telegram + Gmail filter + GitHub).

**Orders issued:**

| Order | Actor | Scope | Status |
|-------|-------|-------|--------|
| TF-ARCH-W1 | Worker | Phase 1 `trustfield-loops` repo | PENDING DISPATCH |
| TF-ARCH-LS1 | Loop Specialist | Runtime plans loops 1,2,3,9,11,12 | PENDING |

**Blockers (TF phase promotion only):**

- **B1** — Legal/privacy PII before new capture channels beyond `/contact`
- **B2** — SG sign-off regulated-term list before Phase 2 triage autorun
- **B3** — Entity/billing tagging before paid spend

**SG guardrails (§21):** five lines locked — no custody claims, regulated-term hard stop, sender_declared, formation disclosure, no external send v1, reliability PLANNED until T6.

**NOOS doctrine (§22):** seven lines locked — one-way export, risk≥4 routing, blocker/target law, model routing, correlated agreement stress-test, receipt required, one worker per loop.

---

## 6. Signal Factory summary (Track B)

**Location:** `~/.cursor/skills/signal-factory/`

**Pipeline:** classification → scoring → decision → receipt → memory line → pattern extraction.

**Verifier:** `scripts/verify_signal_factory_v1.py` — ALL PASS (6/6) as of 2026-07-02.

**Gating law (Eval 5 fix):**

```text
automation_recipe        IFF decision == "build_automation"
commercial_service_idea  IFF decision == "create_service_pattern"
else both null — no independent triggers
```

**Risk override:** `scores.risk ≥ 4` → `decision = route_to_human` always.

**Adapter slots (empty v1):** `trustfield`, `noetfield`, `witnessbc`, `partnermesh`, `client_mvp`.

**SG guardrails:** pointer `references/sg-guardrails-v1.md` — five items, record only.

**Test receipt IDs:** `sf-fixture-t1-vendor` through `sf-fixture-t6-entity-hygiene`.

**Adversarial note (locked):** Verifier PASS confirms structure, not triage judgment quality. Real inbox examples = TARGET.

---

## 7. Human approval gates (both tracks)

| Gate | Applies to |
|------|------------|
| G1 External send | Any outbound — Sina every time v1 |
| G2 High-risk | Risk ≥ 4, regulated terms — Sina/legal/SG |
| G3 Doctrine append | SG/NOOS lines — Sina only |
| G4 Pattern export | First 4 TF→SourceA batches — Sina |
| G5 Spend upgrade | Paid tier — Sina + cost brief |
| G6 Loop activation | dry-run → autorun — test plan receipt |

---

## 8. Proof commands (lock verification)

```bash
# Signal Factory structural verifier (independent PASS)
/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py

# TrustField live surface (manual spot-check)
curl -sI https://www.trustfield.ca/ | head -5

# TrustField loops — pending until TF-ARCH-W1 built
# (no verifier yet)
```

**Pass lines required:**

- `verify_signal_factory_v1: ALL PASS (6/6)`
- TrustField surface: 200 on `www.trustfield.ca`, build tag v66 in page source

---

## 9. STOP condition

This reconciled lock is authoritative for both tracks. Downstream execution:

1. **TF-ARCH-W1** — dispatch when ready (preview only, B1–B3 respected)
2. **Brain registration** — after TF Worker build only; independent re-verify mandatory
3. **SG/NOOS pointers** — TARGET one-shot after Brain (non-blocking)
4. **TF-ARCH-LS1** — Loop Specialist after W1 + Brain
5. **Signal Factory v2** — see `docs/1111_UPGRADE_PLANS_v1.md` Plan 2

Architect + Worker stop on locked artifacts. No improvisation past blockers.

---

*v1.0 — 2026-07-02 — reconciles Architect messages A–D + Worker deliverable D.*
