# Multi-Repo Worker Registry v1

**Status:** LOCKED — 2026-07-02  
**Authority:** SG (SSSOT) — this document lives in SG; it **routes**, it does **not** build venture workers.  
**Rule:** Every worker is **repo-specific**. One actor · one repo · one scope. Mixed-scope orders are defects.

---

## 0. Naming (this chat)

| Name | Meaning |
|------|---------|
| **SG** | Sina Governance — governance function |
| **SSSOT** | Sina Single Source of Truth — same as SG repo role |
| **This chat / this repo** | `~/Projects/sina-governance-ssot` — verifier, gate, registry, mirrors, receipts |

SG is **not** SourceA Brain, **not** TrustField Worker, **not** NOOS.

---

## 1. Actor → repo → worker map

| Actor | Repo (canonical path) | Remote (when known) | Worker / role | Builds | Must NEVER |
|-------|----------------------|---------------------|-----------------|--------|------------|
| **SG (SSSOT)** | `~/Projects/sina-governance-ssot` | `kazemnezhadsina144-dot/sina-governance-SSOT` | Independent verifier · promotion gate · brain domain registry · SG guardrail **mirrors** | Governance scripts, lock docs, receipts | Venture workers, product doctrine, SourceA bundle |
| **SourceA Brain** | `~/Projects/SourceA` | `kazemnezhadsina144-dot/SourceA` | Live brain worker `sourcea-brain-chat-v1` · bundle · locked-defs · **register** verified artifacts | Routes, memory lines, collision checks | TF/Noetfield/NOOS implementation code |
| **SourceA Worker** | `~/Projects/SourceA` | same | SA deploy scripts · skill packaging · brain CLI | SourceA workers, Signal Factory **packaging into SA** | `trustfield-loops` code · NOOS `_NOOS_AGENT` docs |
| **SourceA Loop Specialist** | `~/Projects/SourceA` + CF tick | same | `loop_specialist_tick_v1` · runtime plans · work orders | Desired-state plans, dispatch receipts | Deploy TF workers · external send |
| **TrustField Worker** | `~/Desktop/trustfield-loops` | TrustField-isolated git | CF intake · D1 · receipt chain · Telegram alert | Phase 1–5 TF autorun loops | SourceA imports · NOOS edits · production send |
| **Noetfield (website/spine)** | `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield/` | Noetfield repo | Public site · platform spine · Vercel · live nerve | www.noetfield.com routes, copy, E2E | GEL runtime implementation |
| **NOOS (GEL runtime)** | `~/Projects/noetfeld-os/` | noetfeld-os | GEL gate/log/audit · `docs/_NOOS_AGENT/` | api.noetfield.com runtime truth | Website source · default save to SourceA |

**Signal Factory v1 (interim):** built at `~/.cursor/skills/signal-factory/` — SourceA-owned meaning; **SourceA Worker** packages to SourceA repo; **SourceA Brain** B-01 pointer register.

---

## 2. Sync topology

```
                    ┌──────────────── SG (SSSOT) ────────────────┐
                    │  verifier · gate · registry · mirrors     │
                    └───────┬──────────┬──────────┬─────────────┘
                            │          │          │
              pointers only │          │          │ pointers only
                            ▼          ▼          ▼
              ┌─────────SourceA─────────┐   ┌──TrustField Worker──┐
              │ Brain · Worker · LS     │   │ trustfield-loops    │
              │ Signal Factory core     │◄──│ pattern export OUT  │
              └───────────┬─────────────┘   └─────────────────────┘
                          │ patterns only
                          ▼
              ┌──── Noetfield website ◄──sync──► NOOS (noetfeld-os) ────┐
              │  story · buyer path      GEL runtime · doctrine docs     │
              └──────────────────────────────────────────────────────────┘
```

| Edge | Direction | Law |
|------|-----------|-----|
| TF → SourceA | One-way pattern export | Anonymized; no TF doctrine back-flow |
| NOOS ↔ Noetfield | Bidirectional **sync** | Website vs GEL split per `NOETFIELD_WEBSITE_NOOS_REAL_SYNC_HANDOFF_LOCKED_v1.md` |
| SG → all | Pointers + verify | SG mirrors SG/NOOS lines; canonical NOOS docs live in `noetfeld-os` |
| SourceA → ventures | Patterns only | Never overwrite venture doctrine |

---

## 3. Order routing (who executes what)

| Order | Actor | Repo | Status (2026-07-02) |
|-------|-------|------|---------------------|
| TF-ARCH-W1 | **TrustField Worker** | `trustfield-loops` | **BUILT** — Phase 1 preview; receipt ids in `.receipt_ids/` |
| TF-ARCH-LS1 | **SourceA Loop Specialist** | SourceA | PENDING — runtime plans only |
| Signal Factory v1 build | **SourceA Worker** | SourceA (skill on disk) | **DONE** — verifier 6/6 |
| Brain B-01–B-03 | **SourceA Brain** | SourceA | READY |
| Brain B-04 register TF artifact | **SourceA Brain** | SourceA | **READY** — TF W1 built; independent re-verify required |
| B2 regulated-term sign-off | **SG** + Sina | SG mirror + `data/regulated-term-hardstop-v1.json` | DRAFT pending sign-off |
| NOOS doctrine append | **NOOS agent** | `noetfeld-os/docs/_NOOS_AGENT/` | TARGET — not SG canonical |
| SG guardrail append | **SG** + Sina | `ssot/sg-guardrails-*.md` | Mirror locked |

**Correction:** TF-ARCH-W1 is **not** a SourceA Worker order. Never dispatch TF build orders to SourceA Worker chat.

---

## 4. Repo boundary violations (defects)

| Defect | Correct owner |
|--------|---------------|
| SourceA Worker builds `trustfield-loops` | TrustField Worker repo |
| TF doctrine saved in SourceA bundle | TrustField repo only |
| NOOS canonical docs only in SG | Canonical → `noetfeld-os`; SG → mirror/pointer |
| Noetfield GEL runtime in website repo | NOOS / noetfeld-os |
| SourceA branding on trustfield.ca | TrustField surface only |
| SG chat builds product workers | Respective venture Worker chat |
| Loop Specialist deploys TF CF workers | TrustField Worker only |

---

## 5. Live evidence (disk check 2026-07-02)

| Repo | Evidence |
|------|----------|
| `trustfield-loops` | `ORDER_TF-ARCH-W1.md` delivered · `npm run test:phase1` · `.receipt_ids/webhook.json` → `rcpt_97ee4a3a-...` |
| `sina-governance-ssot` | Lock docs · registry · verifier · `data/regulated-term-hardstop-v1.json` draft |
| `~/.cursor/skills/signal-factory/` | `verify_signal_factory_v1: ALL PASS (6/6)` |
| SourceA | `brain_domain_sandboxes_v1.json` · loop specialist tick · brain worker live |
| Noetfield | `NOETFIELD_WEBSITE_NOOS_REAL_SYNC_HANDOFF_LOCKED_v1.md` |
| noetfeld-os | Canonical NOOS path per handoff; clone may be required locally |

---

## 6. SG mirror vs canonical

| Content | Canonical owner | SG role |
|---------|-----------------|---------|
| SG guardrails (5 lines) | SG | `ssot/sg-guardrails-trustfield-v1.md` — **canonical for SG** |
| NOOS doctrine (7 lines) | NOOS | `ssot/noos-doctrine-trustfield-v1.md` — **mirror**; append in `noetfeld-os` |
| Regulated-term list | SG (B2 sign-off) | `data/regulated-term-hardstop-v1.json` — **canonical for TF triage import** |
| TrustField architecture | TrustField | `TrustField Technologies/docs/internal/` per trustfield-loops README |
| Signal Factory skill | SourceA | Interim disk skill → SourceA Worker packages → Brain registers pointer |

---

## 7. Proof commands (boundary audit)

```bash
# SG registry
/usr/bin/python3 ~/Projects/sina-governance-ssot/scripts/validate_brain_domain_registry_v1.py

# Signal Factory (SourceA-owned skill, any repo context)
/usr/bin/python3 ~/.cursor/skills/signal-factory/scripts/verify_signal_factory_v1.py

# TrustField Worker (run IN trustfield-loops repo)
cd ~/Desktop/trustfield-loops && npm run test:phase1

# Noetfield live nerve (run IN Noetfield repo)
cd ~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield && make verify-live-nerve
```

---

*v1.0 — 2026-07-02 — SG authoritative worker/repo map. Amend only via SG append + receipt.*
