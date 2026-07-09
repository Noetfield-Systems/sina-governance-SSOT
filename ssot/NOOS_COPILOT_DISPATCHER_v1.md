# NOOS Copilot Dispatcher v1

**Status:** ACTIVE  
**Layer:** P2 (SSOT / integrator plane)  
**Role:** Cross-repo sync dispatcher for root repositories  
**Owner:** SG (`sina-governance-ssot`)  
**Machine SSOT:** `data/noos_copilot_dispatcher_v1.json`  
**Sync mode (Step 5):** `data/noos-copilot-dispatcher-mode-v1.json` · `docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md`  
**Integrator role pointer:** `data/noos-integrator-role-v1.json` → `noetfeld-os/data/noos-integrator-role-v1.json`  
**Step 4 receipt:** `packages/noos-control-desk-v1/receipts/integrator_step4_verifier_v1.json` (**13/13 PASS — accepted**)  
**Step 5 SG record:** `receipts/sg-record-step5-noos-sync-mode-20260704T043000Z.json` (**COMPLETE / RECORDED**)

---

## Identity

**NOOS Copilot** is the P2 cross-repo sync dispatcher. It is **not** GitHub Copilot autorun, **not** policy writer, **not** fleet rollout engine.

Distinction:

| Actor | Layer | May do |
|-------|-------|--------|
| **NOOS Copilot** (this doc) | P2 | Integrator status/sync + receipts across root repos |
| **GitHub Copilot UI** | P8 sub-policy | Bounded manual GPT-5 mini helper only |
| **Cursor** | build lane | Main builder in `sina-governance-ssot` |

---

## Root repositories (dispatch scope)

1. `sina-governance-ssot`
2. `noetfeld-os`
3. `SourceA`
4. `Noetfield`
5. `TrustField-Technologies`

Each root repo receives **integrator status/sync only** via NOOS Copilot — not full policy stack copy.

---

## Allowed

- `GET /api/integrator/status` — repo-local, home mirror, cloud mirror **readout**
- `POST /api/integrator/sync` — **repo-local sync only**
- Write schema-validated receipts (`receipts/*.json`)
- Read home mirror when configured (`~/.sina/noos-integrator-state-v1.json` or `NOOS_HOME_MIRROR_PATH`)
- Read cloud mirror status when configured (`NOOS_CLOUD_MIRROR_STATUS_PATH`) — **read only**

---

## Sync mode (Step 5 — mode-gated)

Sync model is **mode-gated**, not binary `cloud_write_allowed`. **NOOS owns** integrator/sync behavior; SG records pointers only.

| Allowed pre-PASS modes | Blocked pre-PASS modes |
|------------------------|------------------------|
| `read_status` | `fleet_rollout` |
| `publish_receipt` | `ACTIVE` promotion |
| `publish_status` | `direct_main_write` |
| `publish_drift_report` | `policy_law_mutation` |
| `prepare_draft_branch` | `publish_audit_pending_registry_as_active_fleet_truth` |
| `prepare_pr` | |

Authority: `data/noos-copilot-dispatcher-mode-v1.json` · `docs/NOOS_COPILOT_DISPATCHER_AUTHORITY.md`

---

## Cloud write scope gate (legacy alias — Step 4)

Cloud writes are **scope-gated**. Before full PASS, NOOS Copilot may publish **receipts**, **status**, **drift reports**, and prepare **draft branches/PRs**.

**Fleet rollout**, **ACTIVE promotion**, **direct main write**, and **policy/law mutation** remain blocked.

| Allowed before full PASS | Blocked before full PASS |
|--------------------------|--------------------------|
| receipts | fleet rollout |
| status | ACTIVE promotion |
| drift reports | direct main write |
| draft branch / PR prep | policy / law mutation |
| | audit-pending registry propagation |

`cloud_write_unrestricted_allowed` = unrestricted fleet/cloud propagation — **false** before full PASS.

---

## Forbidden (always)

- Promote any artifact to **ACTIVE**
- Write or amend **policy** (`SMART_PRODUCTION_COST_LAW`, Copilot profile, `cost_policy.yaml`)
- Propagate **audit-pending registry** (`SCAFFOLD_READY_AUDIT_PENDING`, `last_audited: TODO`) to fleet or cloud
- Run **recurring Copilot automation** (GitHub Actions owns recurring; `model:none` default)

---

## Canonical API (integrator slice only)

```
GET  /api/integrator/status
POST /api/integrator/sync
GET  /api/receipts/list
```

Full Phase 1 contract: `data/noos_control_desk_api_contract_v1.json`

---

## Step 4 acceptance (2026-07-04)

Integrator verifier: **13/13 PASS**

- Integrator status visible (repo-local + home mirror + cloud readout)
- Local sync runs
- Cloud write scope gate enforced (scoped allows vs blocked list)
- Receipt written and listed

**Step 5 (2026-07-03):** NOOS Sync Mode Patch — **COMPLETE / RECORDED** (SG pointers only; NOOS owns behavior)

- Mode-gated sync model recorded
- Receipt: `receipts/sg-record-step5-noos-sync-mode-20260704T043000Z.json`

**Next:** Step 6 — Machine-Enforceable Repo Fences

**Cross-link:** [NOOS_INTEGRATOR_RULES_v1.md](NOOS_INTEGRATOR_RULES_v1.md) · [NOOS_CONTROL_DESK_PACKAGE_v1.md](NOOS_CONTROL_DESK_PACKAGE_v1.md)
