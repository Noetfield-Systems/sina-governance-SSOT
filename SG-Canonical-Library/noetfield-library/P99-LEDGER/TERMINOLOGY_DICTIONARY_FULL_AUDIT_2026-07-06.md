# Terminology & Dictionary Full Audit — Living Docs + Public Surfaces

**Date:** 2026-07-06T20:15Z  
**Scope:** 144 library markdown files · 4 live contract/landing URLs · Downloads intake `NOETFIELD_LEXICON_v1.md`  
**Foundation installed:** `LANGUAGE_LAYER_v1.md` · `NOETFIELD_TERMINOLOGY_v1.md` · `NOETFIELD_DICTIONARY_v1.md`

---

## Executive summary

| Area | Conflicts found | Severity | Action |
|------|----------------:|----------|--------|
| Receipt vs claim | 40+ ledger filenames + prose | **HIGH** | Label observation records; reserve “receipt” for proof schema |
| 24/7 / always-on / full auto | 25+ docs | **HIGH** | Motor + receipt age or explicit “not 24/7” |
| model-agnostic / agnostic | 5 docs | **MEDIUM** | → vendor-neutral (rewrites started) |
| client base (unprovable) | 2 docs | **MEDIUM** | → governed reference environment / partner’s clients |
| META loops labeled revenue | 1 registry (noetfeld-os) | **HIGH** | inbox `revenue_path` mislabel |
| Website overclaim | 2 phrases | **LOW–MED** | Plain-English downgrades below |
| Banned hype register | 0 hits | **OK** | — |

**Verdict:** Language layer was missing; drift was inevitable. Terminology + dictionary now SSOT. Remaining work is **mechanical rewrite pass** by conflict class, not re-arguing meanings.

---

## Layer placement (new)

```
P0  LANGUAGE_LAYER_v1.md          — wording vs meaning authorities + minting rule
P7  NOETFIELD_DICTIONARY_v1.md   — meaning authority (source); escalation + authoring
P7  NOETFIELD_TERMINOLOGY_v1.md  — wording authority (minted from dictionary); lint-enforced Tier 0
P6  locked-definitions-v1        — brain public claims only (unchanged scope)
```

**Minting rule:** Dictionary → Terminology → artifact. Never reverse. No new job/task/specialist/role/page/clause/receipt field without dictionary entry first.

---

## Conflict class A — Receipt / claim / observation record

### Problem
Library uses `*_RECEIPT_*` for guard ledgers, health passes, and pre-revenue motion. Agents read filename and assume **proof receipt** semantics (R6/R7, investor thesis).

### Rule (terminology)
| Has op_key + sink + schema? | Label |
|-----------------------------|--------|
| Yes | Proof receipt |
| Honest guard/census snapshot | **Observation record** (keep file, fix prose header) |
| Chat / log only | **Claim** |

### High-impact files (sample — full grep: 40+)

| File | Issue | Rewrite direction |
|------|-------|-------------------|
| `P99-LEDGER/NOOS_FLEET_HEALTH_PASS_*` | Title “receipt” implied in JSON schema name | Keep schema; first line: “Observation record — not R≥1 proof” ✓ already honest in body |
| `P99-LEDGER/OUTBOUND_MOTION_RECEIPT_*` | Commercial motion without 25 sends | Observation + FOUNDER_EXECUTE status |
| `P99-LEDGER/FIRST_REVENUE_RECEIPT_*` | Name presumes event | Keep name only when payment row exists |
| `P7-DOCTRINE/receipts-not-diagrams.md` | Correct thesis | Link to TERMINOLOGY receipt vs observation |
| `WORK_ORDER_IDE_LANE_v1.md` | Correct strict receipt | Reference terminology |

### Plain-English rewrite (template for ledgers)
```markdown
**Record type:** Observation record (SG guard) — not proof of customer payment.
**Proves:** [what fields exist]
**Does not prove:** [R≥1 / deploy / stranger payment]
```

---

## Conflict class B — 24/7 / always-on / full auto

### Problem
Doctrine and Line Engine v0.2 use “24/7” aspirationally (10 lines, self-improving fleet). Health pass proved **partial** motor green. Agents conflate **target** with **live state**.

### Canonical plain English
- **Target:** “Run governed loops pursuing targets; stop only for floor.”  
- **Live claim:** “Motor X dispatches; N/M loops have Supabase rows ≤2× interval.”  
- **Not 24/7:** Cursor, Mac launchd, founder manual, weekly census.

### Files needing tone fix (priority)

| File | Conflicting phrase | Suggested plain English |
|------|--------------------|-------------------------|
| `LINE_ENGINE_ARCHITECTURE_v0.2_HARDENED.md` | “10 revenue lines… 24/7” | “Target architecture: up to 10 lines on governed motors; live state per receipt ladder.” |
| `deterministic-brain-doctrine.md` | “24/7 brain without founder” | “North star: zero-founder validation via governed motors + receipts.” |
| `ARCHITECT_START_HERE.md` §3 | “Run 24/7 pursuing targets” | Add: “(live 24/7 = motor receipt fresh; see health pass)” |
| `immutable-floor.md` | “24/7 autonomy survivable” | OK as **conditional** — add “when motors + floor enforced” |
| `NOOS_FLEET_HEALTH_PASS_*` | Honest YELLOW | **Model doc** for class B |

---

## Conflict class C — Synonym drift (rewrites applied / queued)

| Drift term | Canonical | Files |
|------------|-----------|-------|
| model-agnostic | **vendor-neutral** | `deterministic-brain-doctrine.md` ✓ · `capability-router-circuit-breaker.md` ✓ |
| client base | **partner’s clients** / governed reference environment | `NOETFIELD_SYSTEMS_OPERATING_PLAN.md` ✓ |
| agnostic (informal) | vendor-neutral | `GOVERNED_AUTORUN_LAWS_v3` “tool-agnostic boot pack” — OK (tools ≠ vendors) |
| station-agnostic | vendor-neutral at provider layer | `BRAIN_REGISTRY_LEARNING_GATE` — note only |

---

## Conflict class D — Census vs registry value_class

| Loop (noetfeld-os) | Registry label | Census truth | Verdict |
|--------------------|------------------|--------------|---------|
| inbox | revenue_path | META | RETIRE / relabel hygiene |
| workflow_audit | risk_reduction | GUARD | FIX |
| self_heal_safe_fixes | risk_reduction | META | RETIRE |
| researcher | risk_reduction | META | RETIRE |
| factory_autorun | legacy motor | META | RETIRE |

**Dictionary entry:** GUARD/REVENUE/META/NONE — see `NOETFIELD_DICTIONARY_v1.md`.

---

## Public website word audit (live fetch 2026-07-06)

### sourcea.app (home)
| Phrase | Assessment | Plain-English note |
|--------|------------|-------------------|
| “proof built in” | **OK** | Matches receipt thesis |
| “Verify before you commit” | **OK** | Negative proof friendly |
| “Real output, not marketing claims” | **OK** | Keep |
| “Global platform · founders worldwide” | **OK** | No overclaim |
| “Jobs completed — Verified” | **VERIFY** | Needs live counter source; if static → “sample verified jobs” |
| “Demo offline” | **OK** | Honest |

**No banned hype found.** Tone: institutional, not needy.

### sourcea.app/operating-brain-install
| Phrase | Assessment | Rewrite if needed |
|--------|------------|-------------------|
| “Receipt-backed execution” | OK | Align with proof receipt schema |
| “Theater risk” | OK | Matches anti-theater doctrine |
| “Book an Operating Brain Audit” | OK | Diagnostic CTA |

### sourcea.app/ai-value-governance
| Phrase | Assessment | Rewrite if needed |
|--------|------------|-------------------|
| “Governable” | OK | Capability, not live enforce |
| “Controls before execution” | OK | Pre-execution doctrine |
| “Board-ready evidence” | OK if sprint deliverable | Not implied live in customer env |

### noetfield.com/ai-value-governance-os/
| Phrase | Assessment | Plain-English rewrite |
|--------|------------|----------------------|
| “Enterprise control layer” | OK | Product framing |
| “Policy-as-code gates material paths” | **CAUTION** | Add: “when deployed in customer environment” for Tier-3 |
| “Sandbox Evaluate before production scope” | **GOOD** | Matches diagnostic-first |
| “Start free sandbox” | OK | Self-serve eval |

### Website rewrite queue (product repos — not SG)
1. Any “jobs completed” counter → tie to live receipt endpoint or soften to “sample jobs.”  
2. Tier-1 pages: add one line: “Diagnostic sprint — live enforcement is a later implementation phase.”  
3. Run terminology §6 synonym pass on next SourceA/Noetfield copy deploy.

---

## Doctrine ↔ terminology alignment

| Doctrine file | Aligns? | Note |
|---------------|---------|------|
| receipts-not-diagrams | Yes | Add pointer to TERMINOLOGY |
| targets-vs-blockers | Yes | Matches terminology |
| deterministic-brain | Yes after D-8 rename | vendor-neutral |
| immutable-floor | Yes | Add motor conditional |
| UNLOCK_DOCTRINE_v2 | Yes | R≥1 defined in terminology |
| anti-theater | Yes | “Motion without proof” = claim |

---

## Mechanical next pass (founder-gated volume)

1. **Batch A:** Add `Record type:` header to all `P99-LEDGER/*` guard files (scriptable).  
2. **Batch B:** Grep `24/7` → add motor qualifier or “target architecture” in P5/P7/P9.  
3. **Batch C:** Product repo copy PR with terminology §6 + website table above.  
4. **Batch D:** `noetfeld-os` registry value_class align to census.  
5. **Lint (future):** `scripts/terminology_lint_v1.py` — banned register + synonym rewrite suggestions.

---

## Intake provenance

- Source: `/Users/sinakazemnezhad/Downloads/NOETFIELD_LEXICON_v1.md`  
- Promoted to: `NOETFIELD_TERMINOLOGY_v1.md` (split: terminology ≠ dictionary)  
- Extended: census, motor, observation record, FIX/RETIRE  
- Audit signer: SG language layer pass — guard only, no commercial execution
