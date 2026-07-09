# SourceA E2E Check Registry (LOCKED v1)

**Saved:** 2026-06-24T04:00:00Z  
**Authority ID:** `SOURCEA_E2E_CHECK_REGISTRY`  
**Version:** 1.0.0

---

## Copy locations (triplicate — read any one)

| Copy | Path |
|------|------|
| **Desktop** | `~/Desktop/SOURCEA_E2E_CHECK_REGISTRY_LOCKED_v1.md` |
| **SourceA** | `~/Desktop/SourceA/brain-os/system/SOURCEA_E2E_CHECK_REGISTRY_LOCKED_v1.md` |
| **Mac Law** | `~/Desktop/MacLaw/SOURCEA_E2E_CHECK_REGISTRY_LOCKED_v1.md` |

**Machine SSOT (auto-generated — do not hand-edit):**  
`~/Desktop/SourceA/data/sourcea-e2e-check-registry-v1.json`

**Human overrides (small — bundles + probes):**  
`~/Desktop/SourceA/data/sourcea-e2e-check-registry-overrides-v1.json`

---

## One law

> **No agent runs E2E without reading the last report. No agent finishes E2E without writing the report. One bundle per cadence — not validator chains.**

**Weekly checklist law:** `brain-os/law/enforcement/SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md`  
**Mac founder session:** INCIDENT-039 — T0–T1 only on Mac body; T2+ ship window or cloud CI  
**Pressure tiers:** `data/mac-pipeline-validator-pressure-registry-v1.json`

---

## Catalog summary (live from machine registry)

| Metric | Count |
|--------|------:|
| **Total checks** | 803 |
| **E2E-named** | 42 |
| **T0_probe** | 6 |
| **T1_fast** | 649 |
| **T2_medium** | 96 |
| **T3_heavy** | 42 |
| **T4_marathon** | 10 |
| **Bundles** | 8 |

Regenerate: `python3 ~/Desktop/SourceA/scripts/sourcea_e2e_registry_generate_v1.py --json`

---

## Unified tiers

| Tier | Meaning | Mac founder session | Cadence |
|------|---------|---------------------|---------|
| **T0_probe** | HTTP health <5s | Allowed | Daily |
| **T1_fast** | Disk grep / <30s | Allowed (one shell) | Daily |
| **T2_medium** | Chain slice / <120s | Ship window only | Weekly |
| **T3_heavy** | Named E2E / 2–10 min | Ship window only | Weekly |
| **T4_marathon** | Full standard / all-e2e / Playwright | Cloud CI only | Monthly |

---

## Weekly bundles (one precise run per cadence)

| Bundle ID | Tier | Cadence | Est time | Entry |
|-----------|------|---------|----------|-------|
| `mac_daily_smoke` | T0–T1 | Daily | <2 min | `sourcea_e2e_run_v1.py --bundle mac_daily_smoke` |
| `machine_ladder_weekly` | T2 | Weekly | ~30 min | `machine_test_ladder_run_v1.py --tier weekly` |
| `hub_e2e_core` | T3 | Weekly | ~15 min | `--bundle hub_e2e_core` |
| `disk_truth_matrix` | T2 | Weekly | ~3 min | `--bundle disk_truth_matrix` |
| `h2_weekly` | T2 | Weekly | ~5 min | `--bundle h2_weekly` |
| `sourcea_standard` | T3 | Ship window | ~6–8 min | `--bundle sourcea_standard` |
| `cloud_runtime_ci` | T4 | Cloud CI | ~10 min | `--bundle cloud_runtime_ci` |
| `full_marathon` | T4 | Monthly | 60+ min | `--bundle full_marathon` |

**Full catalog:** weekly = bundles only. Monthly `--cadence monthly --all` = parallel cloud CI sweep.

---

## Agent protocol

### Before E2E

```bash
cd ~/Desktop/SourceA
python3 scripts/sourcea_e2e_run_v1.py --read-last --json
```

Read: `~/.sina/sourcea-e2e-last-report-v1.json`

### Run

```bash
python3 scripts/sourcea_e2e_run_v1.py --bundle mac_daily_smoke --write-report --json   # daily Mac-safe
python3 scripts/sourcea_e2e_run_v1.py --cadence weekly --write-report --json         # weekly
python3 scripts/sourcea_e2e_run_v1.py --bundle sourcea_standard --write-report --json # ship window
python3 scripts/sourcea_e2e_run_v1.py --cadence monthly --all --write-report --json   # cloud CI
```

### After E2E

| Artifact | Path |
|----------|------|
| Last report (agents read) | `~/.sina/sourcea-e2e-last-report-v1.json` |
| Weekly receipt | `~/.sina/sourcea-e2e-weekly-checklist-receipt-v1.json` |
| Per-check logs | `~/.sina/e2e-logs/*.log` |
| Archive | `~/Desktop/SourceA/receipts/e2e-reports/E2E-*.json` |
| Human mirror | `~/Desktop/SourceA/docs/system-audits/E2E_REPORT_YYYY-MM-DD.md` |
| Live surfaces line | `~/.sina/agent-live-surfaces-v1.json` → `e2e_last_report_line` |

### Duty card

| ID | Duty |
|----|------|
| D24 | Read last report before E2E |
| D25 | Write report after E2E |
| D26 | Sunday weekly cadence on ship window or cloud CI |

---

## Hub-probe checks (T0 — daily)

| ID | URL | Notes |
|----|-----|-------|
| `hub-probe-cloud-workers` | `http://127.0.0.1:13027/health` | **Primary cockpit** |
| `hub-probe-chat-unify` | `http://127.0.0.1:13023/health` | Form at `/form/` |
| `hub-probe-mac-health` | `http://127.0.0.1:13024/health` | |
| `hub-probe-n8n` | `http://127.0.0.1:13026/health` | |
| `hub-probe-routing-panel` | `http://127.0.0.1:8780/` | |
| `hub-probe-mac-law` | `http://127.0.0.1:8781/health` | |

**Faded (do not probe):** `hub-probe-worker-hub` · `:13020` — legacy archived (`asf_hub_legacy_trash_v1.sh` · `data/cloud-workers-control-plane-v1.json`).

---

## E2E-named checks (42 — index)

| Check ID | Tier | Cadence | Scope | Script |
|----------|------|---------|-------|--------|
| `validate-all-e2e-v1` | T4_marathon | monthly | mac_local | `scripts/validate-all-e2e-v1.sh` |
| `validate-brain-e2e-discipline-v1` | T3_heavy | weekly | mac_local | `scripts/validate-brain-e2e-discipline-v1.sh` |
| `validate-brain-intent-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-brain-intent-e2e-v1.sh` |
| `validate-brain-outbound-work-order-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-brain-outbound-work-order-e2e-v1.sh` |
| `validate-commercial-outbound-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-commercial-outbound-e2e-v1.sh` |
| `validate-e2e-fast-ladder-v1` | T3_heavy | weekly | mac_local | `scripts/validate-e2e-fast-ladder-v1.sh` |
| `validate-e2e-hardening-p0-v1` | T3_heavy | weekly | mac_local | `scripts/validate-e2e-hardening-p0-v1.sh` |
| `validate-e2e-recipe-p1-v1` | T3_heavy | weekly | mac_local | `scripts/validate-e2e-recipe-p1-v1.sh` |
| `validate-factory-e2e-protection-v1` | T3_heavy | weekly | mac_local | `scripts/validate-factory-e2e-protection-v1.sh` |
| `validate-form-official-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-form-official-e2e-v1.sh` |
| `validate-goal1-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-goal1-e2e-v1.sh` |
| `validate-hub-stabilization-e2e-light-v1` | T3_heavy | weekly | mac_local | `scripts/validate-hub-stabilization-e2e-light-v1.sh` |
| `validate-live-prompt-feed-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-live-prompt-feed-e2e-v1.sh` |
| `validate-loop-chain-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-loop-chain-e2e-v1.sh` |
| `validate-mac-health-cooldown-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-mac-health-cooldown-e2e-v1.sh` |
| `validate-mac-health-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-mac-health-e2e-v1.sh` |
| `validate-mac-law-surfaces-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-mac-law-surfaces-e2e-v1.sh` |
| `validate-mcp-chain-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-mcp-chain-e2e-v1.sh` |
| `validate-sourcea-e2e-full-v1` | T4_marathon | monthly | mac_local | `scripts/validate-sourcea-e2e-full-v1.sh` |
| `validate-sourcea-e2e-playbook-locked-v1` | T3_heavy | weekly | mac_local | `scripts/validate-sourcea-e2e-playbook-locked-v1.sh` |
| `validate-sourcea-e2e-preflight-v1` | T3_heavy | weekly | mac_local | `scripts/validate-sourcea-e2e-preflight-v1.sh` |
| `validate-sourcea-e2e-standard-v1` | T3_heavy | weekly | mac_local | `scripts/validate-sourcea-e2e-standard-v1.sh` |
| `validate-sourcea-landing-e2e-v1` | T4_marathon | monthly | mac_local | `scripts/validate-sourcea-landing-e2e-v1.sh` |
| `validate-sourcea-mvp-intake-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-sourcea-mvp-intake-e2e-v1.sh` |
| `validate-super-fast-hub-e2e-v1` | T3_heavy | weekly | mac_local | `scripts/validate-super-fast-hub-e2e-v1.sh` |
| `audit_backend_e2e` | T3_heavy | weekly | mac_local | `scripts/audit_backend_e2e.py` |
| `audit_backend_e2e_light_v1` | T3_heavy | weekly | mac_local | `scripts/audit_backend_e2e_light_v1.py` |
| `audit_agent_governance_e2e` | T3_heavy | weekly | mac_local | `scripts/audit_agent_governance_e2e.py` |
| `form_official_wire_e2e_v1` | T3_heavy | weekly | mac_local | `scripts/form_official_wire_e2e_v1.py` |
| `wbc-e2e` | T3_heavy | weekly | mac_local | `scripts/wbc-e2e.sh` |
| `validate_witnessbc_full_e2e_v1` | T4_marathon | monthly | cloud | `witnessbc-site/scripts/validate_witnessbc_full_e2e_v1.sh` |
| `validate_witnessbc_deep_e2e_v1` | T3_heavy | weekly | cloud | `witnessbc-site/scripts/validate_witnessbc_deep_e2e_v1.py` |
| `validate_toolkits_e2e_v1` | T3_heavy | weekly | cloud | `witnessbc-site/scripts/validate_toolkits_e2e_v1.sh` |

*Remaining T649 validators: see machine JSON — grep `unified_tier` per id.*

---

## Tools & validators

| Tool | Path |
|------|------|
| Registry generator | `scripts/sourcea_e2e_registry_generate_v1.py` |
| Run orchestrator | `scripts/sourcea_e2e_run_v1.py` |
| Validate registry | `scripts/validate-sourcea-e2e-registry-v1.sh` |
| Validate report discipline | `scripts/validate-sourcea-e2e-report-discipline-v1.sh` |
| E2E executor checklist | `brain-os/runtime/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md` |
| Debugger playbook | `brain-os/law/SOURCEA_E2E_DEBUGGER_PLAYBOOK_LOCKED_v1.md` |
| Cursor rule | `.cursor/rules/agent-e2e-report-discipline-v1.mdc` |

---

## Sunday rhythm

1. Read last report
2. Ship window or cloud CI dispatch
3. `python3 scripts/sourcea_e2e_run_v1.py --cadence weekly --write-report --json`
4. Glance `e2e_last_report_line` on live surfaces

Cross-ref: `founder/ASF_WEEKLY_SUNDAY.md` · `ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md`

---

## Mac Law routing

| Context | Allowed E2E |
|---------|-------------|
| Founder session (default) | `mac_daily_smoke` only |
| ASF ship window | weekly bundles + `sourcea_standard` |
| Cloud CI / Railway | all tiers including monthly full catalog |

**Mac control plane:** `~/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md`  
**Pressure law:** `~/Desktop/MacLaw/MAC_PIPELINE_VALIDATOR_PRESSURE_LAW_LOCKED_v1.md`

---

*End SOURCEA_E2E_CHECK_REGISTRY v1*
