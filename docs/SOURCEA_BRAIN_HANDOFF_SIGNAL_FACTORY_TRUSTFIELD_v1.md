# SourceA Brain Handoff — Signal Factory + TrustField Domain v1

**To:** SourceA Brain (live worker + knowledge bundle + registry)  
**From:** SG (SSSOT) — `sina-governance-ssot` — lock + registry + verify only  
**Date:** 2026-07-02 (v1.1 multi-repo correction)  
**Status:** ACTIONABLE — Brain Wave 1 tasks may start immediately  
**Receipt:** `trustfield-signal-factory-lock-20260702T204000Z`  
**Plans:** [1111_UPGRADE_PLANS_v2.md](1111_UPGRADE_PLANS_v2.md) · [MULTI_REPO_WORKER_REGISTRY_v1.md](../ssot/MULTI_REPO_WORKER_REGISTRY_v1.md)  
**Signal Factory Iteration 2 lock:** [SIGNAL_FACTORY_ITERATION2_LOCK_v1.md](SIGNAL_FACTORY_ITERATION2_LOCK_v1.md) · receipt `signal-factory-iteration2-lock-20260703T100500Z`

---

## 0. Executive brief (read first)

Two domain artifacts are locked. **Signal Factory v1** — SourceA-owned skill, built by **SourceA Worker** (`~/.cursor/skills/signal-factory/`, verifier 6/6). **TrustField Phase 1** — built by **TrustField Worker** in `~/Desktop/trustfield-loops` (NOT SourceA Worker); preview receipts exist.

**Your job (Brain):** Register pointers, enforce separation, consume pattern exports, never write TrustField doctrine. **Skip Brain pre-build.** **Post-build registration:** TrustField Worker artifact → Brain registers after **independent re-verify** (Worker report = claim). Signal Factory v1 skips register (meaning complete).

**Highest ROI Brain actions now:** B-01/B-02/B-03 · ~~B-04~~ ✅ registered 20260703T000733Z

---

## 1. New architecture (layer map)

```
┌─────────────────────────────────────────────────────────────┐
│  LIVE BRAIN (sourcea-brain-chat-v1)                         │
│  Registry · bundle · locked-defs · promotion gate           │
└────────────┬───────────────────────────────┬────────────────┘
             │ read-only pointers           │ pattern export IN (one-way)
             ▼                              ▼
┌────────────────────────┐      ┌─────────────────────────────┐
│  SIGNAL FACTORY v1     │      │  TRUSTFIELD (separate)      │
│  SourceA-owned skill   │      │  trustfield-loops (pending) │
│  classify→score→receipt│      │  watched surface v66 live   │
└────────────────────────┘      └─────────────────────────────┘
             │                              │
             └────────── SG / NOOS ─────────┘
                    (guardrails + doctrine by pointer)
```

| Layer | Owner | Brain relationship |
|-------|-------|-------------------|
| Signal Factory core | SourceA Brain + **SourceA Worker** (packaging) | Brain: read-only pointer B-01; Worker: skill → SA repo |
| TrustField venture | **TrustField Worker** (`trustfield-loops`) | Brain watches; export patterns in; never write TF doctrine |
| SG guardrails | **SG (SSSOT)** | Canonical mirror: `ssot/sg-guardrails-trustfield-v1.md` |
| NOOS doctrine | **NOOS** (`noetfeld-os`) | SG file is mirror; canonical append in `docs/_NOOS_AGENT/` |
| TF Worker build | **TrustField Worker** only | Brain registers after independent PASS — not SourceA Worker |
| Loop Specialist | **SourceA Loop Specialist** | Runtime plans → registry desired-state (B-07) |
| Noetfield website | **Noetfield repo** | Sync with NOOS per NF handoff — not Brain scope |

---

## 2. New rules (enforce in routing)

### 2.1 Separation rules (non-negotiable)

1. TrustField data in TrustField-dedicated store — no shared tables with SourceA Brain memory.
2. SourceA receives **exported copies** of pattern rows only — never live read of TF signal store.
3. No SourceA agent writes TF doctrine files. Export is TF → SourceA one-way.
4. TF secrets stay TF-scoped CF secrets — never in SourceA repo or bundle.
5. SourceA branding/skills never appear on trustfield.ca.
6. Cost events tagged `entity: trustfield` during formation support via Noetfield.
7. Mixed-scope prompts are defects — split before execution.

### 2.2 Anti-laundering rules

| Rule | Enforcement |
|------|-------------|
| Sender claims | Always `sender_declared`; never restate as fact in outputs |
| Worker PASS reports | Claims only — Brain re-verifies artifact bytes before register |
| Correlated agreement | Stress-test trigger, not validation — log distinct objection or "none found" |
| Verifier PASS | Structure only — not triage judgment quality |

### 2.3 Autorun law (v1)

| Autoruns | Never autoruns (v1) |
|----------|---------------------|
| Signal capture, classify, receipt, brief, health alert | External send (email, reply, API outbound) |
| TF triage, cost rollup, chain verify | Draft → send without G1 Sina click |

### 2.4 Model routing (when Brain dispatches)

| Tier | Model | Use |
|------|-------|-----|
| Doctrine | Fable 5 | Architecture, contract lock only |
| Adversarial | Opus-class | Risk ≥ 4, entity-boundary, regulated language |
| Worker | Sonnet-class | Draft-only, internal memos |
| Bulk | Workers AI Llama 3.3 70B | First-pass triage every signal |
| Memory | SourceA Brain | Registry, receipts, memory lines |

**Law:** No signal hits Opus before bulk scores. Risk ≥ 4 requires Opus confirm before safe-to-draft. Escalate over false negatives.

### 2.5 Signal Factory gating law (Eval 5 — mechanical)

```text
automation_recipe        IFF decision == "build_automation"
commercial_service_idea  IFF decision == "create_service_pattern"
else both null — no independent triggers
```

Verifier T4 enforces. Brain must not invent alternate gates.

### 2.6 Human gates (route, do not bypass)

| Gate | Brain action |
|------|--------------|
| G1 External send | Block all outbound automation |
| G2 High-risk | Route to Sina/legal/SG; freeze signal |
| G3 Doctrine append | SG/NOOS — Sina only |
| G4 Pattern export | First 4 TF batches — Sina review |
| G5 Spend upgrade | Cost brief + explicit yes |
| G6 Loop promotion | Test plan receipt required |

---

## 3. Signal Factory — what Brain must know

**Location:** `~/.cursor/skills/signal-factory/`  
**Verifier:** `/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py`  
**Pass line:** `verify_signal_factory_v1: ALL PASS (6/6)`  
**Status:** ✅ Built 2026-07-02

### Pipeline

`classification → scoring → decision → receipt → memory_line → pattern_extraction`

### Receipt schema

`~/.cursor/skills/signal-factory/references/receipt-schema.json`  
Schema id: `signal-factory-receipt-v1`

### Four scores (0–5)

`urgency` · `fit` · `risk` · `value` — risk ≥ 4 → `decision = route_to_human` always.

### Decision classes

`route_to_human` · `archive` · `draft_only` · `build_automation` · `create_service_pattern`

### Entity hygiene (every receipt)

Six entities named, `cross_attribution: false`:  
`noetfield` · `trustfield` · `sourcea` · `witnessbc` · `sg` · `noos`

### Adapter hooks (empty v1 — do not populate from Brain)

`trustfield` · `noetfield` · `witnessbc` · `partnermesh` · `client_mvp`

### Brain registration status

**v1: SKIP** — meaning fully specified; Worker + verifier sufficient.  
**v2: REGISTER** only if semantic delta after first Discovery sale.

---

## 4. TrustField domain — what Brain must know

**Live surface:** `www.trustfield.ca` · build tag `site-v66-entity-truth-cleanup-2026-07-02`  
**Verified:** no-custody boundary · entity-in-formation · SKU ladder live  
**Identity:** Separate watched venture — **not** SourceA child, **not** adapter-first-class

### TrustField Worker order (NOT SourceA Worker)

**TF-ARCH-W1** — **BUILT** in `~/Desktop/trustfield-loops` (preview only)  
Receipt example: `rcpt_97ee4a3a-64c3-4f0e-abbe-a961f4a7e68e` · verify: `cd ~/Desktop/trustfield-loops && npm run test:phase1`  
Phase 2+ — **TrustField Worker** chat only (after B2)

### Brain registration (post W1)

```text
Before registering: re-run structural verifier against actual artifact files.
Register only on independent PASS.
Worker's report is a claim, not a receipt.
```

Register: artifact provenance · locked-definition collision check · memory_line · receipt_id

### Pattern export (Wave 2+)

- Weekly batched, anonymized, PII stripped
- `sender_declared` claims → structure only
- Brain classifies reusability — **never flows back as TF instruction**
- G4: Sina reviews first 4 batches

### Blockers (TF phase promotion only — do not halt Brain Wave 1)

| ID | Blocks | Clears |
|----|--------|--------|
| B1 | New intake email publication | Existing `/contact` OK |
| B2 | Phase 2 triage autorun | SG sign-off on `data/regulated-term-hardstop-v1.json` |
| B3 | Paid spend | Entity/billing tag confirmation |

---

## 5. SG + NOOS pointers (record only — Brain cites, does not edit)

**SG:** `ssot/sg-guardrails-trustfield-v1.md` — five guardrails  
**NOOS:** `ssot/noos-doctrine-trustfield-v1.md` — seven doctrine lines  
**Regulated terms (draft):** `data/regulated-term-hardstop-v1.json` — risk 5 hard stop

Brain Brief weekly pass: one SG line + one NOOS line + correlated-agreement stress-test field.

---

## 6. Brain work queue (ROI order — start Wave 1)

| ID | Task | value_class | Proof |
|----|------|-------------|-------|
| **B-01** | Add Signal Factory to bundle **pointer table** as read-only pattern reference (`signal_factory_v1`) | proof_asset | Registry/bundle diff + no collision |
| **B-02** | Document `memory_line` format compatibility SF receipt → Brain memory | proof_asset | Schema doc in bundle or SSOT |
| **B-03** | Add `pattern_export` sandbox row to `brain_domain_sandboxes_v1.json` status HOLD | hygiene | Registry validate PASS |
| **B-04** | Register `trustfield-loops` artifact after W1 independent verifier PASS | proof_asset | **✅ DONE** `brain-register-tf-loops-20260703T000733Z` |
| **B-05** | Locked-definition collision check on B-04 | risk_reduction | **✅ DONE** (bundled in B-04) |
| **B-06** | Classify TF export batch #1 reusability | revenue_path | reusability_hint + memory_line |
| **B-07** | Ingest TF-ARCH-LS1 runtime plans as desired-state | proof_asset | LS1 receipt |
| **B-08** | E2E matrix: add SF verifier + TF health when live | proof_asset | matrix ALL PASS |

**Start now:** B-01, B-02, B-03, **B-04** (TF W1 already built — independent re-verify first)  
**Wait:** B-05+ until B-04 register PASS

---

## 7. Live Brain domain — current state + extensions

### Existing sandboxes (unchanged)

| sandbox_id | Artifact |
|------------|----------|
| `brain_worker` | Worker code + bundle |
| `knowledge_bundle` | Bundle data |
| `locked_definitions` | Locked defs lane |
| `contract_pages` | Three SKU pages |

### Proposed additions (Brain implements B-03)

```json
{
  "sandbox_id": "signal_factory_ref",
  "description": "Signal Factory v1 read-only pattern reference (skill, not live doctrine)",
  "artifact_type": "external_skill_pointer",
  "candidate_path": "~/.cursor/skills/signal-factory/SKILL.md",
  "gate_profile": { "register_mode": "pointer_only", "brain_live_smoke_default": false }
}
```

```json
{
  "sandbox_id": "pattern_export_tf",
  "description": "TrustField → SourceA one-way pattern export lane",
  "status": "HOLD",
  "gate_profile": { "human_gate": "G4", "first_batches": 4 }
}
```

### Live endpoints (health probes)

| URL | Role |
|-----|------|
| `https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/health` | Brain worker |
| `https://sourcea.app/operating-brain-install` | Contract SKU |
| `https://www.trustfield.ca/` | TF surface (monitor when loops live) |

### Autorun proof (Brain loop)

```bash
bash ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/validate_brain_domain_e2e_matrix_v1.sh
# Pass: validate_brain_domain_e2e_matrix_v1: ALL PASS sandbox=all
```

---

## 8. ROI context (why Brain should care)

| Asset | ROI path |
|-------|----------|
| Signal Factory | Reusable triage across all ventures — one brain, five adapter hooks |
| TF watched surface | Inbound signals → patterns → first paid SourceA engagement (T5) |
| Receipt chain | Sellable proof_asset — anti-theater, anti-Brain-leak |
| Pattern export | CAD 4,000 Discovery SKU maps to `create_service_pattern` gate |
| Free stack | $0 until revenue; Discovery sale funds 12mo ops |

**THROTTLED_ROI:** If >30% 7-day Brain spend is `value_class: none`, deprioritize hygiene tasks.

---

## 9. What Brain must NOT do

- Write or merge TrustField doctrine, claim language, or risk thresholds
- Populate adapter hook content (venture-owned TARGET)
- Accept Worker PASS without independent artifact re-verify (TF register)
- Restate `sender_declared` claims as verified facts
- Auto-send external messages (G1 — no send API in v1)
- Upgrade claim class without evidence (VERIFIED requires probe)
- Treat GPT+Architect agreement as validation without stress-test log

---

## 10. Orders in flight (route, don't rebuild)

| Order | Actor | Repo | Status |
|-------|-------|------|--------|
| TF-ARCH-W1 | **TrustField Worker** | `trustfield-loops` | **BUILT** — Brain B-04 next |
| TF-ARCH-LS1 | **SourceA Loop Specialist** | SourceA | PENDING |
| Signal Factory v1 | **SourceA Worker** | skill disk | **DONE** |
| Brain B-01–B-03 | **SourceA Brain** | SourceA | **READY NOW** |
| Brain B-04/B-05 | **SourceA Brain** | SourceA | **✅ DONE** |
| SG B2 sign-off | Sina + **SG** | sina-governance-ssot | DRAFT JSON ready |
| NOOS doctrine append | **NOOS agent** | noetfeld-os | TARGET — sync NF handoff |
| SF real inbox | Sina + **SourceA Worker** | SourceA | Wave 1 parallel |

---

## 11. File index (Brain load order)

| Priority | Path |
|----------|------|
| 1 | `docs/SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md` (this file) |
| 2 | `docs/TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md` |
| 3 | `docs/1111_UPGRADE_PLANS_v2.md` |
| 4 | `ssot/sg-guardrails-trustfield-v1.md` |
| 5 | `ssot/noos-doctrine-trustfield-v1.md` |
| 6 | `data/regulated-term-hardstop-v1.json` |
| 7 | `~/.cursor/skills/signal-factory/SKILL.md` |
| 8 | `data/brain_domain_sandboxes_v1.json` |

---

## 12. Proof commands (Brain session close)

```bash
# Signal Factory structure
/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py

# Brain registry
/usr/bin/python3 ~/Desktop/Noetfield-Systems/sina-governance-SSOT/scripts/validate_brain_domain_registry_v1.py

# Lock receipt
cat ~/Desktop/Noetfield-Systems/sina-governance-SSOT/receipts/trustfield-signal-factory-lock-20260702T204000Z.json

# TF surface spot-check
curl -sI https://www.trustfield.ca/ | head -3
```

**Every Brain "done" claim requires a receipt_id.** Unreceipted reports are unverified.

---

## 13. One line for Brain memory

Multi-repo law: TrustField Worker builds trustfield-loops; SourceA Worker builds SourceA; SourceA Brain registers after independent verify; NOOS↔Noetfield sync separate; SG/SSSOT verifies+mirror only; TF W1 built—Brain B-04 now; SF 6/6 PASS; export one-way TF→SourceA; send never v1.

---

*v1.0 — 2026-07-02 — handoff to SourceA Brain for Wave 1 execution.*
