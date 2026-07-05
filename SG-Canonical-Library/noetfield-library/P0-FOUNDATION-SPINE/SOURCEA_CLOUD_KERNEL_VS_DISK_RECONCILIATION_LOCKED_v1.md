# SourceA Cloud Kernel vs Disk — reconciliation — LOCKED v1

**Saved:** 2026-06-22T16:00:00Z  
**Version:** 1.1.0  
**Status:** LOCKED  
**Authority:** ASF — advisor Cloud Kernel target v1.3 aligned to disk  
**Index:** `docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md`  
**PDF label (authoritative):** **Target architecture v1.3 — Phase 1 partial** (supersedes v1.2; not “Production Locked / Phase 1 current”)

---

## One sentence

> The advisor PDF describes the **cloud motor target**; disk today is a **hybrid** — Mac workbench shipped, Railway FBE contract-gated, Supabase L3, JSON receipts — with explicit GREEN, AMBER, and TARGET rows below.

---

## Philosophy (GREEN — keep as-is)

| PDF principle | Disk proof |
|---------------|------------|
| Deterministic kernel; LLM plans only | `data/founder-execution-model-v1.json` · `scripts/fbe/lib/execution_contract_v1.py` |
| Execution Contract Layer | `data/fbe_execution_contract_v1.json` · FBE route map |
| Artifact / Evidence / Decision split | `~/.sina/*-receipt*.json` · Phase-1 ticket `phase1-pevc-truth-ticket-v1.json` |
| SLA / cost routing | `data/cursor-cost-intelligence-routing-v1.json` (Mac) · forge scoring SSOT (cloud) |
| Workers = muscle · graph = brain | `data/fbe_node_graph_v1.json` · `data/forge-real-blueprints-v01.json` |
| n8n glue only | `brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md` |

---

## Layer map L1–L8

| Layer | PDF name | Disk path today | Status | Notes |
|-------|----------|-----------------|--------|-------|
| **L1** | UI / Interface · Next.js + CF Pages | `agent-control-panel/worker-hub/` · `scripts/*-standalone/` · Vercel landings under portfolio repos | **AMBER** | Right idea (multi-tenant skins); Hub is static HTML + WKWebView `.app`, not Next on CF Pages |
| **L2** | Auth & Isolation · Supabase Auth + RLS | `data/supabase-portfolio-tiers-v1.json` · `infra/supabase/portfolio-spine/` · `infra/supabase/noetfield/` | **GREEN** | Production tiers locked ASF 2026-06-20 |
| **L3** | State Engine · **Neon** Postgres | **Supabase** (`portfolio-spine`, `noetfield`, `labs-sandbox`) | **AMBER** | **L3 = Supabase today.** Neon **ONLY** after ASF-approved migration |
| **L4** | Queue Engine · CF Queues | `~/.sina/phase-observed-v1.json` · `scripts/hub_cloud_forge_run_proceed_v1.py` · `scripts/cloud_auto_runtime_v1.py` | **AMBER** | **L4 = Cloud Forge Run today** → CF Queues later |
| **L5** | Runtime · 4 stateless CF Workers | `scripts/fbe_cloud_worker_http_v1.py` · Railway deploy `scripts/deploy_fbe_railway_v1.py` · `scripts/fbe_run_job_v1.py` | **AMBER** | **W1–W4 = logical roles** served by **contract-gated Railway FBE** today, not CF Workers |
| **L6** | Capability Router · tool registry | `data/forge-scoring-ssot-v01.json` · `data/fbe_node_graph_v1.json` · cloud OpenRouter on Railway | **AMBER** | Router logic partial; registry not full SQL-backed tool table |
| **L7** | Heavy Compute · Modal/RunPod | `apps/video-ad-factory/` · Fal · ElevenLabs · `scripts/video_ad_factory_orchestrate_v1.py` | **GREEN** | Same role; vendor names differ from PDF |
| **L8** | Observability · OTel + ClickHouse | `~/.sina/` receipts · `scripts/validator_machine_v1.py` · hub main terminal | **AMBER** | **L8 = JSON receipts today** → OpenTelemetry later |

---

## W1–W4 logical roles (not CF Workers today)

| PDF worker | Logical role | Disk implementation today | Status |
|------------|--------------|---------------------------|--------|
| **W1 Intake** | Validate inputs · create `runs` pending | Hub dispatch · FBE contract validation · `execution_contract_v1.py` policy gate | **AMBER** |
| **W2 Planner** | Structured plan / DAG | `forge-real-blueprints-v01.json` · FBE node graph · comprehension loop | **AMBER** |
| **W3 Executor** | Deterministic tool calls | `fbe_run_job_v1.py` · `fbe_forge_runner_v1.py` · Railway motor | **GREEN** (Python, contract-gated) |
| **W4 Memory** | Embeddings · completion signal | Receipt writes · `fbe_hub_projection_v1.py` · hub live wire | **AMBER** |

**Do not rewrite motor to Cloudflare Workers** without ASF ship window. Evolve FBE toward W1–W4 **interfaces**, not a rip-and-replace.

---

## Data hierarchy vs disk

| PDF entity | Disk analogue today | Status |
|------------|---------------------|--------|
| Tenant / Project | `supabase-portfolio-tiers-v1.json` projects · brand modules | **GREEN** |
| Factory | FBE templates (`web-product-factory-v1`, `forge-app-factory-v1`, …) | **GREEN** |
| Blueprint | `data/forge-real-blueprints-v01.json` (100 rows) · per-drain JSON schemas | **GREEN** (JSON, not SQL `blueprints` table) |
| Run | FBE job receipts · `~/.sina/fbe-*-receipt*.json` | **AMBER** |
| Task | Cloud Forge Run rows · `sa-mkt-*` · CLOUD-SEC queue | **AMBER** |
| Artifact / Evidence / Decision | Phase-1 ticket triple · gate receipts | **GREEN** (file-based) |

**TARGET:** SQL DDL in PDF §6 — migrate after Phase-1 truth tickets prove JSON shape end-to-end.

---

## Model routing (honest relabel)

| Source | Role |
|--------|------|
| **Live routing SSOT** | `data/cursor-cost-intelligence-routing-v1.json` (Mac Cursor pools) + cloud OpenRouter on Railway FBE |
| **PDF model table** (Gemini 3.1 Flash-Lite, DeepSeek V4, Claude Sonnet, Grok 4.1) | **TARGET** capability-map names — not hardcoded production endpoints |

Agents cite **cursor-cost SSOT** for Mac; cloud motor uses **OpenRouter / provider env on Railway** — not PDF slug strings until registry ships.

---

## v1.3 new constructs (supersedes v1.2 deltas)

| v1.3 construct | Disk analogue today | Status | Notes |
|----------------|----------------------|--------|-------|
| **Blueprint Registry** (versions · dependencies · tests · status) | `data/forge-real-blueprints-v01.json` · `data/forge-scoring-ssot-v01.json` | **TARGET** | JSON blueprints exist; no `blueprint_versions` / `blueprint_dependencies` / `blueprint_tests` / `blueprint_status` tables |
| **Mandatory `idempotency_key` on tasks** | `scripts/fbe/lib/execution_contract_v1.py` · some FBE job paths · PDF §9.1 `tasks` DDL | **AMBER** | Present on some FBE routes; **not enforced everywhere** |
| **Rollback / Compensation in contracts** | `data/fbe_execution_contract_v1.json` (policy gate only) | **TARGET** | **None / manual** today — v1.3 `compensation` block on plan steps not wired |
| **Circuit Breaker in Router** | `data/forge-scoring-ssot-v01.json` · OpenRouter fallback patterns in cloud dispatch | **AMBER** | Fallback exists; **formal breaker** (trip open · half-open probe) not implemented |
| **Forge Integration** (node graph → Blueprint+Contract compiler) | `data/fbe_node_graph_v1.json` · Forge UI / `scripts/forge_v01_engine_v1.py` | **TARGET** | Forge surfaces exist; **visual graph → registry compiler** not built |

**v1.3 explicit non-starts (from PDF §13):** Neon migration · CF Worker rewrite · L8 OpenTelemetry · model optimization — all premature until Execution Contract Validator + truth ticket green.

---

## Mac L0 (not in PDF — shipped ahead of kernel doc)

| Component | Path | Status |
|-----------|------|--------|
| Hardened Machine Workbench | `docs/SOURCEA_HARDENED_MACHINE_WORKBENCH_ARCHITECTURE_LOCKED_v1.md` | **GREEN** |
| Worker Hub | `:13020` · `scripts/worker_hub_v1.py` | **GREEN** |
| AG Routing Panel | `:8782` · `scripts/ag_routing_panel_core.py` | **GREEN** |
| Mac Law | `:8781` | **GREEN** |
| Belt SCAN→SHIP | `034-next-task-trigger-v1.mdc` · session gate scripts | **GREEN** |

Cloud PEVC **nests inside SHIP** — see SSOT Index.

---

## PDF roadmap vs disk phase

| PDF phase | Claim in PDF | Disk truth |
|-----------|--------------|------------|
| Phase 1 Core Kernel | “current” | **Partial** — contracts + blueprints + Supabase tiers; no unified SQL graph |
| Phase 2 Execution Engine | Queues + 4 workers | **Partial** — Railway FBE + Cloud Forge Run; not CF Queues |
| Phase 3 Router Intelligence | DB tool registry | **TARGET** |
| Phase 4 Observability | OTel + token tables | **TARGET** |

---

## Phase-1 truth ticket (authoritative — correct industrial behavior)

**Factory:** forge drain · blueprint `MAC-CTL-002` · queue `CLOUD-SEC-052`  
**Motor:** existing Railway FBE path via hub proceed dry-run  
**Receipt:** `~/.sina/phase1-pevc-truth-ticket-v1.json`  
**Shape:** top-level `artifact{}` · `evidence{}` · `decision{}` + belt step receipts  
**Gate:** PROVE = `living_system_chain_validate_v1.py --fast`; SHIP = hub cloud proceed `dry_run` only

| Field | Value |
|-------|--------|
| **Belt** | SCAN → SAY → PICK → PROVE → SHIP — **all steps ran** |
| **Verdict** | **rejected** — gates correctly **HELD** (no agent self-report green) |
| **PROVE blocker** | `railway_cloud_queue` read timeout (6/7 chains up) |
| **SHIP blocker** | Hub proceed **502** — Railway cloud worker did not respond |

**This is correct industrial behavior.** Advancement blocked until binary receipts pass.

**Re-run rule:** When Railway responds and `railway_cloud_queue` passes, re-run the **same belt** (blueprint `MAC-CTL-002`, queue `CLOUD-SEC-052`). Verdict flips to **approved** from receipts only — not from chat.

JSON now · SQL later.

---

## Explicit non-goals (LOCKED)

- No Neon until ASF migration approval  
- No CF Worker motor rewrite  
- No second IDE — Cursor stays edit surface  
- No flat merge of PDF + Workbench into one SSOT file  

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.1.0 | 2026-06-22T16:00:00Z | v1.3 target · five new construct rows · truth ticket blockers logged |
| 1.0.0 | 2026-06-22T15:30:00Z | Initial LOCK — L1–L8 map · honest relabels · Phase-1 ticket pointer |
