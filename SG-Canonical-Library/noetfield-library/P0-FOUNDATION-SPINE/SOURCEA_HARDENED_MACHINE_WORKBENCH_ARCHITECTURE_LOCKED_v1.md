# SourceA Hardened Machine Workbench — architecture — LOCKED v1

**Saved:** 2026-06-22T14:15:00Z  
**Version:** 1.0.0  
**Status:** LOCKED  
**Authority:** Founder + advisor structural correction (reject “Agentic IDE” theater)  
**Runtime SSOT:** `data/founder-execution-model-v1.json` · `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`  
**Supersedes for naming:** informal “Agentic IDE” · “agent magic” UI vocabulary

---

## One sentence

> **Mac is a Hardened Machine Workbench — a deterministic industrial control room where agents are production-line workers, every action has an API/CLI twin, UI mirrors receipts on disk, and cloud runs the motor body.**

---

## Terminology (mandatory)

| Forbidden (marketing theater) | Canonical (disk truth) |
|-----------------------------|------------------------|
| Agentic IDE | **Hardened Machine Workbench** |
| Agents as engine | **Architecture is the engine** — agents turn tools |
| Chat as SSOT | **`~/.sina/*-receipt*.json`** + hub API JSON |
| GUI-first control | **API & CLI first** — UI is live reflection |
| Heavy WebGL daily routing | **AG Routing :8782** (fast) · legacy architect :8780 optional |

---

## Two-plane law (unchanged)

| Plane | Where | Role |
|-------|-------|------|
| **Control** | Mac | Hub · routing · Mac Law · form gate · telemetry read · Cursor steering |
| **Execution** | Cloud + APIs | Railway FORGE · Supabase edge · n8n cron glue · OpenRouter on cloud |

**Law:** `data/founder-execution-model-v1.json` → `mac_role.forbidden_as_factory` · `cloud_role.execution_plane_headless`

Agents **must not** run factory motors on Mac body. Mac validators during founder session = light reads only (INCIDENT-039).

---

## Agent interface decision (LOCKED)

### Primary: local HTTP API + thin CLI `--json`

**Chosen:** Local API server pattern (Worker Hub model). **Not** native RPC/IPC as the agent control plane.

| Reason | Detail |
|--------|--------|
| Already shipped | Fixed ports · JSON endpoints · receipt writes |
| Agent-native | Cursor agents use `curl`, `fetch`, `python3 scripts/*_v1.py --json` |
| One contract | Browser · WKWebView `.app` · terminal · n8n · cloud cron share same API |
| Auditable | Pass/Fail provable from disk paths — industrial telemetry |
| Commercial wrap | Notarized DMG/Tauri embeds same localhost contract — no rewrite |

### Secondary: minimal native IPC (UI chrome only)

| Mechanism | Scope | Agents |
|-----------|-------|--------|
| `SinaAppRouter` · `sinaAppOpen` | Tab bar opens native `.app` | **Do not depend** |
| Swift `applicationWillTerminate` | Kill child Python servers on ⌘Q | N/A |
| Future Unix socket (optional) | High-frequency log stream to xterm | Optimization only |

**Rule:** No agent workflow may require IPC. If IPC fails, API + CLI must still advance the belt.

---

## Factory infrastructure (three pillars)

### 1. Deterministic CLI & API first

Every UI control **must** have a machine twin:

| UI control | API / CLI twin (examples) |
|------------|---------------------------|
| Cloud proceed | `POST http://127.0.0.1:13020/api/cloud-forge-run/proceed/v1` |
| Routing refresh | `POST http://127.0.0.1:8782/api/ag-routing-panel` `{"action":"refresh_panel"}` |
| Task/plan validation | `python3 scripts/next_task_trigger_v1.py --refresh --json` |
| Session gate | `python3 scripts/agent_session_gate_run_v1.py --role worker --json` |
| Hub worker slice | `GET http://127.0.0.1:13020/api/worker-hub/v1` |
| n8n chain (fast) | `python3 scripts/living_system_chain_validate_v1.py --fast --json` |

**Law:** UI tiles are **glance hints**. Terminal lines and receipt JSON are **truth**.

### 2. Five-step conveyor belt (physical lifecycle)

Fixed lifecycle — agents **cannot skip a stage** without binary proof (validator receipt · hub proceed receipt · gate JSON).

| Step | Name | Proof artifact |
|------|------|----------------|
| 1 | **SCAN** | Disk read · `agent-live-surfaces-v1.json` · queue head |
| 2 | **SAY** | Plain-English intent · task-plan pipeline sections |
| 3 | **PICK** | Resolved task id · usefulness verdict · priority P0–P4 |
| 4 | **PROVE** | Validator/gate receipt · no chat-only green |
| 5 | **SHIP** | Cloud motor receipt · product file on disk |

**SSOT:** `docs/SOURCEA_FIVE_STEP_AUTONOMOUS_PROGRESS_BLUEPRINT_LOCKED_v1.md` (when present) · `data/sourcea-next-task-trigger-v1.json` · `034-next-task-trigger-v1.mdc`

**Agent entry station:** AG Routing Panel `:8782` — “Agent start here” glance before WORK orders.

### 3. Workspace sandbox (directory isolation)

| Zone | Paths | Policy |
|------|-------|--------|
| **Active WORK** | `apps/<factory>/` · bounded `sa-*` scope · `scripts/` gates | Agents execute here only when `WORK:` / INBOX bound |
| **Law / governance** | `brain-os/` · `.cursor/rules/` | Cross-lane edit forbidden without `EDIT ALLOWED:` |
| **Archive / museum** | `archive/` · `/legacy/` hub | **Museum purity** — no live writes · no law SSOT |
| **Receipts** | `~/.sina/` | Telemetry — read-first, not chat memory |
| **Heavy / ignored** | `receipts/` · `.cursorignore` paths | No agent mega-paste · bounded reads |

**Law:** `000-cross-lane-edit-forbidden.mdc` · `043-workspace-governance-core.mdc`

---

## Control panel UI layout (industrial dashboard)

Not a VS Code clone — an **operations control room**:

| Panel | Production role | SourceA surface today |
|-------|-----------------|----------------------|
| **Top — Official links bar** | Jump between factory stations | `agent-control-panel/shared/official-links-bar.js` — all hub `.app`s |
| **Top — Conveyor belt** | 5-step phase · gate blocked/active | **Target:** shared belt component (Hub + AG Routing) |
| **Left — Registry tree** | `sa-mkt-*` · Ready / Pipeline / Locked | Worker Hub queue · `phase-observed-v1.json` — **not** 9MB monolith |
| **Center top — Gate status** | Founder proceed · auto-tick · override | Hub cloud proceed · form lane · INCIDENT-037 founder-only submit |
| **Center — Editor** | Plans JSON/MD with syntax feedback | **Cursor IDE** — workbench does not duplicate Monaco |
| **Bottom — Structured terminal** | Pass/Fail blocks · cloud stream | `sina-main-terminal.js` · API station terminal · validator terminal |

**AG Routing Panel (:8782):** Agent-first routing · cost intelligence · brand routes · quick jump to correct `.app`.

**Legacy routing architect (:8780):** Heavy WebGL — optional deep view, not daily agent path.

---

## Mac workbench port map (agent-facing)

| Port | Service | Agent use |
|------|---------|-----------|
| **13020** | Worker Hub (H1) | Queue · proceed · form · API Station |
| **8782** | AG Routing Panel | **Start here** · route · cost ROI |
| **8781** | Mac Law | Control-plane rules · surfaces |
| **13027** | Cloud Workers | CLOUD-SEC drain · Railway motor |
| **13026** | N8N Integration | Automation spine · fast chain validate |
| **13023** | Chat Unify | Chat merge · webhook wire |
| **13024** | Mac Health Guard | Mac body telemetry · heal |
| **8780** | Legacy routing architect | Optional · not daily |
| **5678** | n8n UI | External glue only — never law SSOT |

**Catalog:** `PORT_CATALOG.json` · `brain-os/law/AGENT_APPLICATION_USE_BLUEPRINT_LOCKED_v1.md` §13

---

## Standalone desktop apps (commercial shell pattern)

Each station ships as a **signed `.app`** on Desktop + Applications:

| App | Bundle pattern |
|-----|----------------|
| Worker Hub · Cloud Workers · N8N · Chat Unify · AG Routing · Portfolio Mail · Mac Health | `*Shell.swift` + bundled Python server + WKWebView |
| Cross-app navigation | `SinaAppRouter` · official links bar · native open |

**⌘Q law:** `SinaStandaloneShell.installStandardMenu` — child servers terminate on quit.

**Live repo preference:** When `~/Desktop/SourceA/scripts/*-standalone/` exists, server serves live UI (not stale bundle only).

---

## Agent rules on the workbench

1. **Read receipts first** — `~/.sina/agent-live-surfaces-v1.json` · quote `factory_now_line`.
2. **Route before build** — AG Routing light mode · task-plan pipeline before sa WORK.
3. **One bounded WORK** — Worker lane · `apps/<name>/` scope · no whole-repo search.
4. **Cloud for motor** — `POST` hub proceed · never `fbe_motor_delegate` on Mac.
5. **No validator marathon on Mac** — INCIDENT-039 · one light check ≤90s · proof = JSON read.
6. **No green theater** — RED stays RED until founder fixes disk.
7. **Brain routes · Worker builds** — role separation locked.

**Cost pools:** `data/cursor-cost-intelligence-routing-v1.json` — Auto/Composer daily · API ship-window only.

---

## Commercial-grade packaging (future ship window)

For a **luxury Mac installable** outside App Store:

| Requirement | Path |
|-------------|------|
| Developer ID code sign | `codesign` on `.app` inner binary + deep sign (existing build scripts) |
| Notarization | `notarytool` submit + staple — **ASF ship window only** |
| DMG delivery | Standard drag-to-Applications — embeds same localhost API |
| Tauri (optional) | Wrap existing Python servers — **do not** change agent API contract |

**Law:** Subprocess spawn · local ports · filesystem access → direct distribution required (not Mac App Store sandbox).

---

## What agents are NOT

- Not the factory motor  
- Not law authors (unless `EDIT ALLOWED:` + path)  
- Not GUI operators (they call API/CLI)  
- Not allowed to skip conveyor stage without receipt  

**Founder** sits at the top of the line: form picks · proceed gates · telemetry override.

---

## Related law (read order)

1. `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`  
2. `data/founder-execution-model-v1.json`  
3. `brain-os/law/HUB_WORKER_ONLY_ARCHIVED_MONOLITH_LOCKED_v1.md`  
4. `data/cursor-cost-intelligence-routing-v1.json`  
5. `brain-os/law/SINA_AUTOMATION_SPINE_AND_N8N_LOCKED_v1.md`  
6. `.cursor/rules/034-next-task-trigger-v1.mdc`  
7. `.cursor/rules/035-hub-cloud-proceed-v1.mdc`  
8. `.cursor/skills/hub-pro-master/SKILL.md`

---

## Proof commands (light — founder session safe)

```bash
curl -sf http://127.0.0.1:13020/health
curl -sf http://127.0.0.1:8782/health
curl -sf http://127.0.0.1:8782/api/ag-routing-panel | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('headline'), d.get('agent_glance',{}).get('primary_action',{}).get('label'))"
python3 scripts/next_task_trigger_v1.py --refresh --json | head -c 600
test -f ~/.sina/mac-control-plane-v1.flag && echo "mac control plane flag OK"
```

Heavy E2E validators: **cloud CI / ASF ship window only** — not Mac founder Cursor session.

---

## Version history

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-06-22T14:15:00Z | Initial LOCK — API-first workbench · reject Agentic IDE · map advisor factory model to disk |
