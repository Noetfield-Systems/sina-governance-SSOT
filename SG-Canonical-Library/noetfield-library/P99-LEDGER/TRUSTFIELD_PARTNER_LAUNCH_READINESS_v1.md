# TRUSTFIELD_PARTNER_LAUNCH_READINESS_v1

**Status:** Active priority · partner access platform + partnership plans  
**First written:** 2026-07-07  
**Venture:** TrustField (separate company — not Noetfield product)  
**Public:** https://www.trustfield.ca  
**SG language receipt:** `receipts/receipt_tf_language_cleanup_v1.json` (public web: 0 reg hits)

---

## Launch verdict

| Lane | Status | Notes |
|------|--------|-------|
| **Technical / deploy** | **GREEN** | W1–W10 green · Partner Access OS v1.1 live · CF www + Railway API |
| **Public copy / RPAA** | **GREEN** | Settlement boundary consistent · SG dry-scan PASS on `web/` |
| **Commercial partner stack** | **GREEN** | `/partners`, MSP channel, `/msb-api`, `/register`, showcase |
| **Partner Access OS** | **LIVE** | `/partner-access` → apply → verify → NDA → briefing room |
| **Entity / billing** | **LOCKED COPY** | Reserved to be incorporated · interim billing Noetfield Systems Inc. · confirm before signed production agreement |
| **Procurement contacts** | **LOCKED COPY** | Founder Compliance / Vendor Diligence: Sina Kazemnezhad · MLRO TBD until registered reporting entity |
| **Production adapters** | **PARTIAL** | Sandbox stubs until Integration SOW |
| **E-sign** | **PARTIAL** | Click-wrap stub — label honestly or wire one provider |

**Partner outbound:** Safe for **sandbox + walkthrough + RPAA Discovery** today. **MSB procurement folders** need founder locks on MLRO + billing entity before aggressive outbound.

---

## Two partner funnels (do not conflate)

| Funnel | Audience | Entry |
|--------|----------|-------|
| **Commercial / MSB channel** | Licensed MSBs, MSPs, consultancies | `/partners` · `/partners/msp` · `/msb-api` · `/register?partner=slug` |
| **Partner Access OS** | Strategic contributors, operating leads, director candidates | `/partner-access` |

---

## Launch gates (checklist)

### Green — ship now

- [x] Public web copy passes SG regulatory dry-scan (`public_high_risk_count: 0`)
- [x] RPAA positioning CI + eslint `rpaa-positioning` on web strings
- [x] Entity status page (`/entity-status`) — honest formation + billing caveat
- [x] Settlement boundary on all commercial pages
- [x] Partner Access OS apply/verify/room/admin API shipped
- [x] 24/7 CF motors + deadman + trustfield-loops production
- [x] OpenAPI + sandbox register loop

### Founder lock — before MSB procurement outbound

- [x] **Billing entity** interim copy on `/entity-status` and vendor pack (Noetfield Systems Inc. interim)
- [x] **Founder Compliance contact** on vendor pack (Sina Kazemnezhad)
- [ ] **MLRO appointment** only if/when TrustField becomes registered/licensed reporting entity or procurement requires
- [ ] **RPAA registration ID** when BoC registration confirmed (if claiming)
- [ ] TrustField Technologies Inc. incorporation filed (reserved name — do not claim incorporated until complete)

### Engineering — before production partner claims

- [ ] Production partner adapters (not stub) per Integration SOW
- [ ] E-sign: live provider OR honest interim click-wrap label in briefing room
- [ ] Partner-access external verify (human User-Agent, not 403-as-pass for bots)
- [ ] Mirror `TRUSTFIELD_DICTIONARY_OVERLAY_DRAFT_v1` to TF repo after founder sign-off

### SG governance — wiring status

- [x] tf-language-cleanup-v1 dry scan + overlay draft (`d8233e9`)
- [ ] TrustField **WIRED** (six-pack) — needs TF repo mirror + cleanup apply pass
- [ ] Update `REPO_LANGUAGE_REGISTRY_WIRING_AUDIT_v1` TrustField row → PARTIAL

---

## Credibility assets (cite in partnerships)

| Asset | URL / path |
|-------|------------|
| MSB program walkthrough | `/showcase?track=msb` |
| Partner walkthrough | `/showcase?track=partner` |
| Sandbox (no call) | `/register?partner=demo-msb-tor` |
| RPAA Discovery | `/pilot` (CAD 4,000 — published) |
| Vendor diligence pack | `/pilot/vendor-pack` |
| Entity truth | `/entity-status` |
| Partner Access | `/partner-access` |
| Runtime truth | `data/runtime_truth_sync_v1.json` |

---

## What we do NOT claim

- TrustField is **not** an MSP, PSP, money transmitter, or custody holder
- TrustField is **not** a Noetfield subsidiary (see `P10-PRODUCT-LAYERS/trustfield.md`)
- No SOC2/HA marketing on pilot surfaces without receipt
- No invented licenses, MLRO names, or billing entity

---

## Next actions (priority order)

1. **Founder:** MLRO + billing entity on vendor pack and entity-status  
2. **TF repo:** Partner funnel clarity on `/partners` (commercial vs Partner Access)  
3. **TF repo:** Briefing room honest NDA label until live e-sign  
4. **SG:** Ratify overlay draft → mirror terms to TF internal doc  
5. **SG:** TrustField safe rewrite pass (entity alias in **internal docs only** — not public web)

---
*v1.0 (2026-07-07) — TrustField first priority for partner platform launch credibility.*
