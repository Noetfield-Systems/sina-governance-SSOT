# Deployment chain status v1

**Saved:** 2026-07-03T10:30Z  
**Authority:** SG (SSSOT) — observation only  
**Branch context:** PR #3 `cursor/trustfield-signal-factory-lock-1111-plans` → `main`  
**Inventory parent:** `data/automation_surface_inventory_v1.json`

---

## Executive summary

| Layer | Status | Headline |
|-------|--------|----------|
| Cloudflare Workers (SourceA) | **Green** | Auto-runtime, brain chat, loop specialist all `ok: true` |
| Railway (FBE upstream) | **Green** | `railway_upstream_ready: true` on auto-runtime health |
| Supabase (NOOS sink) | **Green** | Factory autorun + inbox/runtime/chain/surface loops succeeding |
| NOOS gel-ci | **Green** | Latest push success |
| SG brain-loop (`main`) | **Red** | Fails until PR #3 merges (CI observe-only path) |
| NOOS SourceA observe | **Red** | `portfolio_spine_not_configured` — secrets not wired in workflow |
| Mac launchd | **Loaded** | `com.sina.brain-loop-autorun-v1`; promote gate correctly BLOCKED |
| Public surfaces | **Green** | sourcea.app 200 · trustfield.ca 200 |

**Verdict:** Deploy chain is **live and mostly healthy**. No emergency rollback. Fix order: merge PR #3 → NOOS observe env wire → SourceA trace storage (optional).

---

## Cloudflare Workers (live probes)

| Worker | Health URL | Cadence | Last probe |
|--------|------------|---------|------------|
| `cloud-auto-runtime-tick-v1` | `https://sourcea.app/api/cloud-forge-run/health/v1` | `*/10` | `ok: true` |
| `sourcea-brain-chat-v1` | `.../health` | on request | `ok: true` (`trace_storage_ready: false`) |
| `loop-specialist-cron-v1` | `.../health` | `*/15` | `ok: true` |
| `sina-governance-ssot-advisory` | `.../health` | on `/run` | up; `pass_claimed: false` (gate) |
| `noos-factory-autorun-tick-v1` | CF cron | `*/10` | dispatches GH factory |
| `noos-loop-fleet-tick-v1` | CF cron | `*/5` | dispatches domain loops |

Auto-runtime health excerpt:

```json
{
  "ok": true,
  "cron": "*/10 * * * *",
  "railway_upstream_ready": true,
  "internal_secret_ready": true,
  "verifier_base_url": "https://sina-governance-ssot-advisory.kazemnezhadsina144.workers.dev"
}
```

---

## Railway

Railway is the **FBE / cloud-forge upstream** behind SourceA auto-runtime. No standalone Railway health URL in SG inventory — CF auto-runtime health is the probe. `railway_upstream_ready: true` confirms the chain is reachable.

---

## Supabase

| Motor | Role | Evidence |
|-------|------|----------|
| `noos-factory-autorun` | Write sink | GH success 2026-07-03T10:21Z |
| `noos-inbox-loop` | Drain / probe | GH success 10:20Z |
| `noos-runtime-loop` | Runtime hygiene | GH success 10:15Z |
| `noos-surface-loop` | Surface probe | GH success 10:20Z |
| `noos-chain-loop` | Audit chain | GH success 10:00Z |
| `noos-sourcea-observe-loop` | Read-only SourceA spine | **GH failure** — env not configured |
| pg_cron T8 | Stale-lane detector | Registered in `noetfeld-os/data/trigger-registry-v1.json` |

Active NOOS workflow secrets (factory path): `NOETFIELD_SUPABASE_URL`, `NOETFIELD_SUPABASE_SERVICE_ROLE_KEY`, `NOETFIELD_SUPABASE_DATABASE_URL`, `SUPABASE_DB_PASSWORD`, `NOETFIELD_API_KEY`.

---

## GitHub Actions crons (recent)

| Repo | Workflow | Result | Notes |
|------|----------|--------|-------|
| noetfeld-os | `noos-factory-autorun` | success | Primary factory motor |
| noetfeld-os | `noos-inbox-loop` | success | |
| noetfeld-os | `noos-runtime-loop` | success | |
| noetfeld-os | `noos-surface-loop` | success | |
| noetfeld-os | `noos-chain-loop` | success | |
| noetfeld-os | `noos-sourcea-observe-loop` | **failure** | See triage doc |
| noetfeld-os | `gel-ci` | success | |
| sina-governance-SSOT | `brain-loop-autorun-v1` (`main`) | **failure** | Fixed on PR #3 branch |

**Dual motors (by design):** NOOS factory = CF cron `*/10` + GH schedule backup. CF is primary autonomous motor per trigger registry.

---

## Mac + SG

| Motor | Status |
|-------|--------|
| `com.sina.brain-loop-autorun-v1` | Loaded (30m + RunAtLoad) |
| Autorun matrix | PASS |
| Brain promote | BLOCKED — verifier not PASS (correct gate) |
| PR #3 | Draft open — merge greens `main` brain-loop CI |

---

## TrustField

| Surface | Status |
|---------|--------|
| trustfield.ca | 200 |
| CF preview worker | Webhook-only (Phase 1) |
| GH cron | None yet |

---

## Trigger chain (reference)

```
CF SA auto-runtime */10 → Railway FBE → Supabase queue
CF NOOS factory tick */10 → GH noos-factory-autorun → Supabase sink
CF NOOS loop fleet */5 → GH inbox/runtime/chain/surface loops → Supabase
GH brain-loop */30 + Mac launchd 30m → promote gate (CAS, max 1 writer)
```

Conflict matrix: `data/automation_surface_inventory_v1.json` — NOOS factory must not deploy SourceA workers.

---

## Open items (priority)

| P | Item | Owner | Doc |
|---|------|-------|-----|
| 1 | Merge PR #3 | Founder / SG | `docs/MERGE_MAIN_CHECKLIST_v1.md` |
| 2 | Wire observe-loop Supabase env | NOOS agent | `docs/NOOS_SOURCEA_OBSERVE_LOOP_TRIAGE_v1.md` |
| 3 | Signal Factory Iteration 2 build | SourceA Worker | `docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md` |
| 4 | Brain chat trace storage | SourceA Worker | optional |
| 5 | Close PR #2 (wrong repo) | SG | assist_only comment |

---

## Re-run probes (founder-safe, ≤90s)

```bash
curl -sf https://sourcea.app/api/cloud-forge-run/health/v1 | python3 -m json.tool
curl -sf https://sourcea-brain-chat-v1.sina-kazemnezhad-ca.workers.dev/health | python3 -m json.tool
curl -sf https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health | python3 -m json.tool
gh run list --repo Noetfield-Systems/noetfeld-os --workflow=noos-factory-autorun.yml --limit 1
gh run list --repo Noetfield-Systems/sina-governance-SSOT --workflow=brain-loop-autorun-v1.yml --branch main --limit 1
launchctl list | grep brain-loop-autorun
```
