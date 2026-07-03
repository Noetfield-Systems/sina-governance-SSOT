# Signal Factory v1 — Iteration 2 Lock

**Status:** LOCKED — Architect handoff finalized  
**Saved:** 2026-07-03  
**Authority:** Architect analyze/finalize · SG records guardrails only  
**Parent:** [TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md](TRUSTFIELD_SIGNAL_FACTORY_RECONCILED_LOCK_v1.md)  
**Receipt:** `receipts/signal-factory-iteration2-lock-20260703T100500Z.json`

---

## 0. Doctrine sentence (locked)

Signal Factory v1 is a **SourceA/Base Brain Skill** that turns inbound market noise into classified signals, bounded decisions, receipts, memory lines, automation opportunities, and sellable service patterns, while preserving entity boundaries and legal/risk escalation.

**Not primary in:** NOOS · Noetfield OS org spine · SG product build  
**SG role:** guardrail lines only (mirror in `ssot/sg-guardrails-signal-factory-v1.md`)

---

## 1. Operating context (2026-07-03)

| Lane | State |
|------|-------|
| Org cockpit | `~/Desktop/Noetfield-Systems/Noetfield-Systems.code-workspace` |
| Clean `main` clones | SourceA · TrustField-Technologies · noetfeld-OS · sina-governance-SSOT · Noetfield · noetfield-studio-ide · SinaaiMonoRepo · buildmatch |
| Org sync spine (TARGET) | `noetfeld-OS` — `REPO_REGISTRY.md`, `AGENT_REGISTRY.md`, `ROUTING_MATRIX.md`, `LOOP_STATE.json`, `SYNC_RECEIPTS.md` |
| SG | Constitution / governance guardrails only |

**Tool-routing law (unchanged):**

| Tool | Role |
|------|------|
| GitHub Actions | Cheap repeatable executor |
| Copilot | GitHub-native repo worker (`assist_only`) |
| Cursor | Heavy local builder |
| Codex | Scarce special-ops / high-reasoning |
| noetfeld-OS | Org sync spine |
| SG | Constitutional guardrails |

---

## 2. Core concept (locked)

Inbound spam, vendor pitches, marketer emails, LinkedIn approaches, partner/cofounder messages, website forms, and platform patterns are **not trash by default** — they are **market telemetry**.

- Do not trust vendor claims.
- Do not buy by default.
- Mine as signal.

**Loop:**

`inbound signal → classify → extract implied need → score → decide → receipt → memory line → automation/service pattern if warranted`

**Primary owner:** SourceA / Base Brain / Signal Factory

---

## 3. PartnerMesh (locked input class)

PartnerMesh = venture-partner acquisition lane, **not** unpaid hiring.

Covers: cofounders · advisors · technical partners · sales/revenue-share operators · investor-relationship partners · product operators

**Legal/positioning:** partner/advisor/founder-track intake with written agreement before real contribution. No employment framing.

---

## 4. Deliverable type (locked fork)

| Artifact | What it is |
|----------|------------|
| `skill-creator` output | Installable Claude Skill = `SKILL.md` behavior package |
| JSON registry | **NOT** this deliverable — separate request only |

**Iteration 2 deliverable:** installable `Signal Factory v1` **`SKILL.md`** + tests + structural verifier.

---

## 5. Fixed output contract (10 sections)

Every run MUST emit in order:

1. SIGNAL SUMMARY  
2. CLASSIFICATION  
3. IMPLIED NEED  
4. SCORES  
5. DECISION  
6. NEXT ACTION  
7. AUTOMATION RECIPE *(gated)*  
8. COMMERCIAL IDEA *(gated)*  
9. RECEIPT JSON  
10. MEMORY LINE  

---

## 6. Classification enum (Iteration 2 — locked)

```text
vendor | partner | client | investor | risk | bug | idea | spam | unclear
```

---

## 7. Decision enum (Iteration 2 — locked)

```text
ignore | archive | reply | route | build_automation | create_service_pattern
```

---

## 8. Optional-section gating (Iteration 2 correction — locked)

`AUTOMATION RECIPE` and `COMMERCIAL IDEA` appear **only** when:

```text
decision = build_automation
OR
decision = create_service_pattern
```

**Forbidden gates:** score thresholds · fuzzy “sellable pattern” · `automation_value >= 3`

If `decision = reply` → both optional sections **MUST NOT** appear.

**Kim's Auto / bare-paste client web form (Eval 3):** locked decision = `create_service_pattern` (reusable SMB intake chatbot service pattern). Optional sections allowed.

---

## 9. Risk override (hard law)

```text
IF risk_score >= 4
THEN decision = route
AND next_action = Sina / legal / human review
AND optional sections MUST NOT appear
```

TrustField custody · settlement · MSB · PSP · banking · regulated-finance inbound → **route**, never auto-reply.

---

## 10. Sender-claim rule

All sender assertions = `sender_declared`. Never launder as verified facts in summary, implied need, memory line, or service patterns.

---

## 11. Score anchors (0–5 — locked)

### trust

| Score | Anchor |
|-------|--------|
| 0 | Anonymous, malicious, or obviously fake |
| 1 | Unverifiable sender, low context |
| 2 | Plausible but no corroboration |
| 3 | Identifiable person/company, ordinary confidence |
| 4 | Known or strongly corroborated source |
| 5 | Verified trusted source / existing relationship |

### risk

| Score | Anchor |
|-------|--------|
| 0 | No meaningful downside |
| 1 | Minor nuisance or reputational noise |
| 2 | Operational ambiguity, no regulated exposure |
| 3 | Moderate legal/commercial/reputation caution |
| 4 | Regulated, custody, financial, equity, legal, or public-claim risk |
| 5 | Immediate legal/security/fraud/high-liability risk |

### automation_value

| Score | Anchor |
|-------|--------|
| 0 | No repeatable workflow |
| 1 | One-off response only |
| 2 | Weak repeatability |
| 3 | Repeatable triage or routing pattern |
| 4 | Clear automatable workflow with reusable steps |
| 5 | High-leverage recurring automation pattern |

### commercial_value

| Score | Anchor |
|-------|--------|
| 0 | No commercial relevance |
| 1 | Vague market hint |
| 2 | Weak commercial angle |
| 3 | Plausible service/product pattern |
| 4 | Strong sellable pattern or ICP signal |
| 5 | Direct revenue path / high-value repeatable offer |

---

## 12. Receipt JSON minimum fields (locked)

Required:

- `signal_id`
- `timestamp`
- `source`
- `classification`
- `decision`
- `risk_score`
- `action`
- `result`
- `status`

Recommended: `entity_scope`, `sender_claims[]`, `optional_sections_emitted[]`, `production_connected: false`

---

## 13. Six-test synthetic set (locked)

| # | Fixture | Classification coverage |
|---|---------|-------------------------|
| 1 | SEO vendor pitch | `vendor` |
| 2 | Cofounder/advisor DM | `partner` |
| 3 | Client inquiry / bare paste (Kim's Auto) | `client` → `create_service_pattern` |
| 4 | Investor/funding note | `investor` |
| 5 | Spam/scam | `spam` |
| 6 | Regulatory-risk / custody request | `risk` → `route` |

Verifier MUST validate: enum · receipt schema · optional-section gating · risk ≥ 4 route.

---

## 14. Agent routing (locked)

| Agent | Role |
|-------|------|
| Architect | Analyze/finalize contract ✅ (this lock) |
| SourceA Brain | Doctrine + skill registry pointer + memory template |
| SourceA Worker | Build `SKILL.md`, 6 tests, structural verifier |
| SourceA Loop Specialist | Gmail/LinkedIn/forms runtime **later** |
| SG | Guardrail lines only |
| NOOS | Hold — not primary |
| NOOS Loop Specialist | Not now |

---

## 15. Build order (after lock — SourceA Worker)

1. Installable `SKILL.md` with Iteration 2 enums  
2. Six synthetic tests  
3. Structural verifier  
4. Receipt schema check  
5. Enum validation  
6. Optional-section gating validation  
7. Risk ≥ 4 route validation  

**NON-SCOPE:** Gmail · LinkedIn · website forms · UI · live automation · NOOS · SG code · JSON registry artifact

---

## 16. Brain add-order (SourceA Brain)

1. Doctrine sentence → Base Brain memory  
2. Register SF as read-only pointer (B-01)  
3. Inbound noise = market telemetry rule  
4. PartnerMesh input class  
5. Optional-section gate rule  
6. Risk override rule  
7. Sender-declared claim rule  
8. Entity-boundary rule  
9. Memory-line format  

---

## 17. Unresolved risks (open — not lock blockers)

- Installed skill at `~/.cursor/skills/signal-factory/` may still use v1.0 enums — Worker must align to Iteration 2 contract above.  
- Eval 5 class defect (optional sections under `reply`) must not recur — enforced by verifier.  
- `investor` enum was missing from 5-test set — fixed by 6-test set.  

---

## 18. Proof (when Worker ships Iteration 2)

```bash
/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py
# Expected: ALL PASS including T_optional_gating + T_risk_route + T_investor_enum
```

SG lock proof:

```bash
test -f ~/Projects/sina-governance-ssot/docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md
cat ~/Projects/sina-governance-ssot/receipts/signal-factory-iteration2-lock-20260703T100500Z.json
```

---

*v1.0 Iteration 2 — 2026-07-03 — LOCKED. Do not expand to 125 skills. Do not move primary ownership to NOOS.*
