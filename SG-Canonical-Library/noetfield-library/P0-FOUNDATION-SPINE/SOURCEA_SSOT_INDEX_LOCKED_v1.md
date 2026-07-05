# SourceA SSOT Index — LOCKED v1

**Saved:** 2026-06-22T16:00:00Z  
**Version:** 1.2.0  
**Status:** LOCKED  
**Authority:** ASF — SSOT unification (no single flat SSOT)

---

## One sentence

> **This index is the single entry point.** SourceA has layered SSOTs — Mac control plane (shipped) and cloud factory kernel (target) — plus a reconciliation map between them. Do not treat any one file as the entire system.

---

## Three-tier model

| Tier | Role | Canonical document | Status |
|------|------|------------------|--------|
| **Index (this file)** | Single entry point · scope boundaries · read order | `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md` | **LOCKED** |
| **L0 Mac Control Plane** | Control · gating · routing · founder session · Cursor workbench | `docs/SOURCEA_HARDENED_MACHINE_WORKBENCH_ARCHITECTURE_LOCKED_v1.md` | **SHIPPED** |
| **L1–L8 Cloud Kernel** | Motor body · data graph · PEVC execution kernel | `docs/SOURCEA_CLOUD_KERNEL_TARGET_v1.3.pdf` | **TARGET — Phase 1 partial** |

**Target Kernel = v1.3; v1.2 superseded.** Status: Target / Phase-1 partial. Canonical PDF: `docs/SOURCEA_CLOUD_KERNEL_TARGET_v1.3.pdf` (symlink → `docs/Source-A-Cloud-Kernel-v1.3.pdf`).
| **Reconciliation** | PDF layers ↔ disk paths · honest GREEN/AMBER/TARGET | `docs/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md` | **LOCKED** |

**Do not merge** L0 and L1–L8 into one file. **Do not rewrite** the motor to Cloudflare Workers. **Do not add Neon** without ASF migration approval. **Cursor remains** the edit surface — the workbench is control room, not a second IDE.

---

## Boundary law

| Plane | Owns | Must NOT |
|-------|------|----------|
| **Mac (L0)** | Control · gating · telemetry read · form picks · hub proceed tap · AG Routing · receipts in `~/.sina/` | Factory motor · heavy validators during founder session · local CLI drain |
| **Cloud (L1–L8)** | Execute · verify · commit product artifacts · Railway FBE · Supabase tiers | Pretend to be Mac control plane · law SSOT · n8n brain |

**Runtime SSOT:** `data/founder-execution-model-v1.json` · `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`

---

## Nesting: Mac belt ⊃ cloud PEVC

Cloud kernel loop (**Plan → Control → Execute → Verify → Commit**) runs **only inside** the Mac belt **SHIP** step — after **PROVE** clears with binary receipts.

| Mac belt (L0) | Cloud PEVC (L1–L8) | Gate |
|---------------|-------------------|------|
| **SCAN** | — | Read disk · live surfaces · queue head |
| **SAY** | — | Plain intent · task-plan pipeline |
| **PICK** | **PLAN** (suggestion only) | Resolved task · usefulness verdict |
| **PROVE** | **CONTROL** | Validator · hub gate · execution contract |
| **SHIP** | **EXECUTE → VERIFY → COMMIT** | Hub proceed / FBE dispatch · receipt write |

Agents **cannot SHIP** on self-report. Advancement requires validator receipt and/or hub proceed receipt on disk.

**Phase-1 truth ticket:** `~/.sina/phase1-pevc-truth-ticket-v1.json` — forge drain exemplar (JSON now, SQL later).

---

## Fixed laws (all layers)

| Law | Wording |
|-----|---------|
| **n8n** | Glue only · external cron/workflows · **never SSOT** · never brain (`brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`) |
| **LLM** | Planner / suggestion engine only · **never executor** · kernel + contracts hold execution authority |
| **Workers** | Muscle only · product variation lives in data graph / blueprints |
| **Chat** | Not SSOT · receipts and hub API JSON are truth |

---

## Read order (agents · advisors · critics)

1. **This index** — scope before depth  
2. **Governance pack (June 2026)** — `brain-os/ssot/SSOT_PLANE_INDEX_LOCKED_v1.md` · operating law v3 · roadmap · GTM  
3. **L0 Workbench** — daily Mac operations  
4. **Reconciliation** — what is real vs target on disk  
5. **Cloud Kernel target PDF (v1.3)** — north-star factory architecture (target; v1.2 superseded)  
6. **Portfolio DB tiers** — `data/supabase-portfolio-tiers-v1.json`  
7. **Execution contract** — `data/fbe_execution_contract_v1.json`  
8. **Cursor cost routing** — `data/cursor-cost-intelligence-routing-v1.json`

---

## What is NOT authoritative here

| Document | Why subordinate |
|----------|-----------------|
| `agent-control-panel/command-data.json` (9MB) | Legacy projection · not daily SSOT |
| Chat history / advisor drafts | Intake only until SAVE TO disk |
| `archive/` | Museum · not live law |
| PDF alone | Missing L0 Mac layer |
| Workbench alone | Missing cloud motor target |

---

## Related internal SSOTs (domain-specific — not flat merge)

| Domain | Path |
|--------|------|
| **Governance pack (June 2026)** | `brain-os/ssot/SSOT_PLANE_INDEX_LOCKED_v1.md` · `brain-os/roadmap/ROADMAP_INDEX_LOCKED_v1.md` |
| LLM Agent Operating Law v3 | `brain-os/ssot/SOURCEA_LLM_AGENT_OPERATING_LAW_SSOT_v3.md` |
| Master Blueprint v1 | `brain-os/roadmap/SOURCEA_MASTER_BLUEPRINT_v1.md` |
| Storefront & GTM v1 (private) | `brain-os/roadmap/SOURCEA_STOREFRONT_GTM_v1.md` |
| Brain unified entry | `brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md` |
| Automation spine | `brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md` |
| Hub daily surface | `brain-os/law/HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md` |
| Supabase constitution | `.cursor/rules/040-workspace-supabase-core.mdc` |

These **reference** this index for layer scope; they do not replace it.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.2.0 | 2026-06-23T22:35:00Z | Governance pack filed — brain-os/ssot + brain-os/roadmap · read order step 2 |
| 1.1.0 | 2026-06-22T16:00:00Z | Target Kernel → v1.3 PDF · v1.2 superseded |
| 1.0.0 | 2026-06-22T15:30:00Z | Initial LOCK — 3-tier index · L0/L1–L8 split · PEVC nests in SHIP |
