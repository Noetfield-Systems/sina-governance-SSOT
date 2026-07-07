# REPO_LANGUAGE_REGISTRY_WIRING_AUDIT_v1

**Status:** Observation-only · no repo edits  
**First written:** 2026-07-07  
**Pattern:** `P9-PATTERN-FACTORY/operational-language-governance-pattern-v1.md`  
**Proven reference:** SourceA (`sa-language-cleanup-v1`)

---

## Definition — “wired”

A repo/system is **wired** to SG Dictionary / Terminology Registry only when **all six** are present:

| # | Requirement | What counts |
|---|-------------|-------------|
| 1 | **SG Registry pointer** | Machine pin to `dictionary_index.json` + batch markdown + RC3 checkpoint (branch/commit or receipt ref) |
| 2 | **Local overlay** | Venture-specific overlay MD (not competing dictionary) |
| 3 | **Overlay index** | Machine-readable JSON classifying terms (7-bucket model) |
| 4 | **Dry scan receipt** | Repo-tree scan using SG Dictionary RC3 **and** local overlay — no live form reopen |
| 5 | **Cleanup receipt** | JSON/report with findings, safe rewrites, risky skips, SG gap queue |
| 6 | **SG gaps routed** | `NEEDS_SG_ENTRY` / `CONFLICT_PHRASE` escalated to SG pile — not silently defined locally |

**Status labels:**

- **WIRED** — all six proven with on-disk receipts or committed artifacts  
- **PARTIAL** — pointer or overlay exists; scan/receipt/gap-routing incomplete  
- **NOT_WIRED** — no proven six-pack; may have unrelated local lint only  
- **LATER** — deferred; audit not run (cheap pass only)

---

## Executive summary

| Target | SG pointer | Overlay | Index | Dry scan receipt | Cleanup receipt | SG gaps routed | **Status** |
|--------|:----------:|:-------:|:-----:|:----------------:|:---------------:|:--------------:|:----------:|
| **SourceA** | yes | yes | yes | yes | yes | yes | **WIRED** |
| **TrustField / trustfield.ca** | yes‡ | draft | yes | yes | plan only | yes | **PARTIAL** |
| **noetfield.com** | no | no | no | no | no | no | **NOT_WIRED** |
| **NOOS Integrator** | partial† | no | no | no | no | no | **NOT_WIRED** |
| **WitnessBC** | no | no | no | no | no | no | **LATER** |

‡ TrustField SG pin in `receipt_tf_language_cleanup_v1.json` + `scripts/tf_language_cleanup_v1.py` — overlay draft on SG only; not mirrored to TF repo yet (`d8233e9`).

† NOOS has **repo-registry** pointers to `sina-governance-SSOT` (copilot dispatcher, loop state) — not a **Dictionary/Terminology Registry** pin. Does not satisfy criterion 1.

**SG authority hub (this repo):** `language_gate/dictionary_index.json` (225 terms @ RC3), `LANGUAGE_LAYER_RC3_CHECKPOINT` — library scan receipt exists; this is the **registry**, not a venture target.

---

## Per-target audit

### 1. SourceA — **WIRED** (proven pattern)

**Repo path:** `~/Desktop/Noetfield-Systems/SourceA`  
**Public surfaces:** sourcea.app · sourcea.ca · sourcea.uk

| Criterion | Evidence | Verdict |
|-----------|----------|---------|
| SG Registry pointer | `scripts/sourcea_language_cleanup_v1.py` → `SG_PIN` (branch `cursor/language-layer-v1`, commit `bf40045`, `dictionary_index.json`, SG overlay index); `data/decision-language-machine-v1.json` → `sg_canon_consumers_read_only` | **yes** |
| Local overlay | `brain-os/law/SOURCEA_DICTIONARY_OVERLAY_v1.md` (+ SG mirror `P10-PRODUCT-LAYERS/SOURCEA_DICTIONARY_OVERLAY_v1.md`) | **yes** |
| Overlay index | `data/sourcea_dictionary_overlay_index_v1.json` (+ SG `language_gate/sourcea_dictionary_overlay_index_v1.json`) | **yes** |
| Dry scan receipt | `receipts/sourcea_language_cleanup_inventory_v1.json` — **757 files**, 402 findings (2026-07-07) | **yes** |
| Cleanup receipt | `receipts/sourcea_language_cleanup_plan_v1.json`, `sourcea_language_cleanup_applied_v1.json`, `docs/SOURCEA_LANGUAGE_CLEANUP_REPORT_v1.md` | **yes** |
| SG gaps routed | SG overlay: 23 `NEEDS_SG_ENTRY`, 9 `CONFLICT_PHRASE`; `P99-LEDGER/DLM_DICTIONARY_GAP_TRIAGE_RC2_2026-07-07.json`; `receipts/receipt_sourcea_dictionary_overlay_v1.json` | **yes** |

**Scan highlights (757-file pass):**

- Safe rewrites applied: **0** (by design — classify-first)  
- Risky/skipped: **10**  
- Backlog: **75**  
- Classes: COMMAND_FRAGMENT 232 · CONFLICT_PHRASE 74 · SOURCEA_LOCAL_TERM 85 · SAFE_REWRITE 10 · PUBLIC_COPY_RISK 1

**Residual (does not unwind WIRED status):**

- `sa-decision-apply-v2` evidence flags not wired — machine-validatable rows cannot auto-close  
- FORM_OFFICIAL 58 rows untouched by design  
- Cleanup receipts live in SourceA `receipts/` — **not yet mirrored** to SG `receipts/` (SG has overlay receipt only)

**Reference architecture for future repos:**

```
SG_PIN (dictionary_index + batch + commit)
  → venture overlay MD + overlay index JSON
  → dry scan script (read-only SG)
  → inventory + plan + applied receipts
  → escalate NEEDS_SG_ENTRY / CONFLICT_PHRASE only
```

---

### 2. TrustField / trustfield.ca — **NOT_WIRED**

**Repo path:** `~/Desktop/Noetfield-Systems/TrustField-Technologies`  
**Public surface:** www.trustfield.ca · api.trustfield.ca  
**Related:** `trustfield-loops` worker (intake); SG library `P10-PRODUCT-LAYERS/trustfield.md` (canon narrative only)

| Criterion | Evidence | Verdict |
|-----------|----------|---------|
| SG Registry pointer | No `dictionary_index.json` pin in TrustField-Technologies scripts/data searched | **no** |
| Local overlay | No `TRUSTFIELD_DICTIONARY_OVERLAY_v1` or equivalent | **no** |
| Overlay index | None | **no** |
| Dry scan receipt | None | **no** |
| Cleanup receipt | None | **no** |
| SG gaps routed | `receipts/trustfield-signal-factory-lock-*.json` — entity hygiene, not language registry | **no** |

**What exists instead:** CF/Railway health motors, `runtime_truth_sync_v1.json`, external-verify workflows — **ops wiring**, not language registry wiring.

**Risk note:** Legal/regulatory public copy on trustfield.ca — highest priority for first venture wiring pass.

---

### 3. noetfield.com — **NOT_WIRED**

**Repo path:** `~/Desktop/Noetfield/Noetfield-All-Documents/Noetfield`  
**Public surface:** www.noetfield.com

| Criterion | Evidence | Verdict |
|-----------|----------|---------|
| SG Registry pointer | No pin to `sina-governance-SSOT/language_gate/dictionary_index.json` | **no** |
| Local overlay | None | **no** |
| Overlay index | None | **no** |
| Dry scan receipt | None | **no** |
| Cleanup receipt | None | **no** |
| SG gaps routed | None | **no** |

**What exists instead:** `scripts/nf_agent_report_language_gate_v1.py` + `data/nf-agent-report-language-standard-v1.json` — **local anti-parrot / tone gate** using `nf-agent-report-language-standard-v1.json`, not SG Dictionary RC3. This is pre-wiring lint, not registry wiring.

---

### 4. NOOS Control Panel / Integrator — **NOT_WIRED**

**Repo path:** `~/Desktop/Noetfield-Systems/noetfeld-os`  
**Role:** Internal machine coordination · control panel · loop registry witness

| Criterion | Evidence | Verdict |
|-----------|----------|---------|
| SG Registry pointer | `noetfield-org/REPO_REGISTRY.md` points at sina-governance-SSOT as governance lane — **not** Dictionary/Terminology pin | **partial†** |
| Local overlay | None | **no** |
| Overlay index | None | **no** |
| Dry scan receipt | None | **no** |
| Cleanup receipt | `NOOS_INTEGRATOR_SYNC_RECEIPT_*` — sync/mission receipts, not language cleanup | **no** |
| SG gaps routed | None for language layer | **no** |

**What exists instead:** `docs/NOETFIELD_COHERENT_SYSTEM_SPEC_v1.md` §0 anatomy terminology — prose only, not machine overlay.

---

### 5. WitnessBC — **LATER** (not audited)

**Observation:** Referenced in DLM fixtures and form rows (`WitnessBC Proof Lab`) — no dedicated repo with six-pack wiring found in scope of this audit.

**Recommendation:** Defer until TrustField + noetfield.com + NOOS passes complete; cheap check = grep public copy against SG `TrustField` + `Proof Lab` dictionary rows only.

---

## Recommended wiring order (next repo)

Per risk and buyer exposure — **one repo per pass**, no giant overlay batch:

| Priority | Target | Why first |
|:--------:|--------|-----------|
| **1** | **TrustField / trustfield.ca** | Legal/regulatory wording risk on public site; entity-truth cleanup history; highest external liability |
| **2** | **noetfield.com** | Buyer/partner-facing enterprise narrative; GEL pages must align with SG canon |
| **3** | **NOOS Integrator** | Controls internal machine names and loop labels — drift here poisons all ventures |
| 4 | WitnessBC | After cheap dictionary-row grep if Proof Lab goes public |

**Next single action:** `tf-language-cleanup-v1` — clone SourceA `SG_PIN` pattern → `TRUSTFIELD_DICTIONARY_OVERLAY_v1` draft from trustfield.ca + TrustField-Technologies corpus → dry scan only → receipt in `TrustField-Technologies/receipts/` (SG mirror optional).

---

## SourceA wiring map (copy for next repo)

| Layer | SourceA artifact |
|-------|------------------|
| SG pin | `scripts/sourcea_language_cleanup_v1.py` :: `SG_PIN` |
| Overlay MD | `brain-os/law/SOURCEA_DICTIONARY_OVERLAY_v1.md` |
| Overlay index | `data/sourcea_dictionary_overlay_index_v1.json` |
| Dry scan | `scripts/sourcea_language_cleanup_v1.py --dry-run` |
| Validator | `scripts/validate-sourcea-language-cleanup-v1.sh` |
| Receipts | `receipts/sourcea_language_cleanup_{inventory,plan,applied}_v1.json` |
| SG mirror | `receipts/receipt_sourcea_dictionary_overlay_v1.json` (SG repo) |

---

## Evidence index

| Artifact | Repo | Role |
|----------|------|------|
| `LANGUAGE_LAYER_RC3_CHECKPOINT` @ `8c0293b` | SG | Registry baseline |
| `receipts/LANGUAGE_LAYER_RC3_FINAL_2026-07-07.json` | SG | Library 158-file scan |
| `receipts/receipt_sourcea_dictionary_overlay_v1.json` | SG | Overlay SHA256 + class stats |
| `language_gate/sourcea_dictionary_overlay_index_v1.json` | SG | Overlay index (127 entries) |
| `receipts/sourcea_language_cleanup_inventory_v1.json` | SourceA | 757-file dry scan |
| `docs/SOURCEA_LANGUAGE_CLEANUP_REPORT_v1.md` | SourceA | Human cleanup summary |
| `data/decision-language-machine-v1.json` | SourceA | DLM authority boundary |

---

## Follow-up gaps (system-wide)

1. **Mirror SourceA 757-file receipts to SG** — `receipts/receipt_sourcea_language_cleanup_v1.json` (cross-repo proof)  
2. **`sa-decision-apply-v2`** — evidence flag wiring before machine-validatable row auto-close  
3. **`build_sourcea_overlay_index_v1.py`** — automated regen (documented future)  
4. **23 `NEEDS_SG_ENTRY`** — founder pile with named locked sources  
5. **Venture wiring machines** — `tf-language-cleanup-v1`, `nf-language-cleanup-v1`, `noos-language-cleanup-v1` (not started)

---

## Scope locks (this audit)

- No repo edits performed  
- No overlays created for TrustField / noetfield.com / NOOS  
- FORM_OFFICIAL not reopened  
- SG Dictionary meanings not redefined

---
*v1.0 (2026-07-07) — Repo registry wiring audit against Operational Language Governance Pattern v1.*
