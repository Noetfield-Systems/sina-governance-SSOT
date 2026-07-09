# Daily Governance Machine Runbook v1

**Status:** ACTIVE  
**Owner:** SG (`sina-governance-ssot`)  
**Purpose:** Turn existing governance machines into a daily executable workflow — not theory.  
**Machines (use only these):**

| Machine | Entry point | Library |
|---------|-------------|---------|
| Impact | `scripts/governance_intelligence_engine_v1.py impact` | engine |
| Thread audit | `scripts/governance_intelligence_engine_v1.py thread-audit` | `scripts/governance_thread_intelligence_v1.py` |
| Final selection | `scripts/governance_intelligence_engine_v1.py audit-selection` | engine |
| Registry ops | `scripts/governance_intelligence_engine_v1.py registry-*` | `scripts/governance_registry_ops_v1.py` |

**Related:** [GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md](GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md) · `data/governance_artifact_registry_v1.json` · `data/daily_governance_calibration_matrix_v1.json`

---

## One sentence

> **Every day: classify messy intake, check thread progress, score proposed law changes, and touch the registry only through ops + receipt — machine output is advisory until registry proves ACTIVE.**

---

## State ladder (hard rule)

| State | Meaning | Machine may claim? | Live authority? |
|-------|---------|-------------------|-----------------|
| `checked` | Machine ran scan/audit on paths | Yes | **No** |
| `selected` | `audit-selection` chose `primary_final` | Yes | **No** |
| `staged` | File in intake staging / `PROPOSED` header / merge-apply dry-run | Yes | **No** |
| `registered` | Row in `governance_artifact_registry_v1.json` (any status) | Only with registry receipt | **No** unless `ACTIVE` |
| `ratified` | Human/SG closure recorded; ready for promote | SG receipt only | **No** until `ACTIVE` |
| `ACTIVE` | Registry `status: ACTIVE` + activation receipt | Only with registry receipt | **Yes** |

**Hard rule:** Machine “done” can only mean `checked` / `selected` / `staged` unless a registry receipt proves `registered` / `ratified` / `ACTIVE`.  
File existence on disk or library = **zero authority**.

---

## Daily command loop

```bash
cd ~/Projects/sina-governance-ssot
```

### Step A — Messy folder / Downloads / Raw AI → `audit-selection`

**When:** New duplicates, version sprawl, unclear “final” doc.

```bash
python3 scripts/governance_intelligence_engine_v1.py audit-selection \
  --paths "<comma-separated absolute paths>" \
  --cluster-by thread \
  --json --write-receipt
```

**Read output:**

| Label | JSON path |
|-------|-----------|
| Machine recommendation | `clusters[].decision.primary_final.path` + `status` |
| Required human/SG action | If `status` ≠ `ACTIVE` → stage + registry; never treat selection as live law |
| Registry status | `clusters[].decision.primary_final.artifact_id` + `status` (null = unregistered) |
| Receipt path | `receipt_path` |
| Live authority? | **Only** if registry row `status == ACTIVE` with receipt — else **not live** |

**Ladder after run:** `selected` (not `ACTIVE`).

---

### Step B — Active thread / progress check → `thread-audit`

**When:** Morning thread hygiene; what is done vs pending vs abandoned.

```bash
python3 scripts/governance_intelligence_engine_v1.py thread-audit \
  --root ~/Desktop/Raw\ AI \
  --json --write-receipt
```

Uses `governance_thread_intelligence_v1.py` internally (`evaluate_paths_as_threads`).

**Read output:**

| Label | JSON path |
|-------|-----------|
| Machine recommendation | `open_threads[]` + `completion_state` per `thread_id` |
| Required human/SG action | `pending_items[]` — founder approval, phase gate, registry entry |
| Registry status | `final_carrier` may show `ACTIVE_AMENDMENT` — still not live until SG registry |
| Receipt path | `receipt_path` |
| Live authority? | Thread final carrier ≠ registry ACTIVE — **not live** unless registry confirms |

**Ladder after run:** `checked` (threads mapped; not registered).

---

### Step C — Proposed law / rule change → `impact`

**When:** Any SG `ssot/` or intake doc may change governance.

```bash
python3 scripts/governance_intelligence_engine_v1.py impact \
  --path ssot/<RULE>_v1.md \
  --json --write-receipt
```

**Read output:**

| Label | JSON path |
|-------|-----------|
| Machine recommendation | `downstream_must_update[]`, `lineage`, `affected_layers` |
| Required human/SG action | Update pointers, run `registry-amend` or `registry-add`, then validate |
| Registry status | `registry_match.status` + `artifact_id` |
| Receipt path | `receipt_path` |
| Live authority? | `registry_match.status == ACTIVE` → live; else **not live** |

**Ladder after run:** `checked` (impact known; change not applied).

---

### Step D — Promote / retire / amend → registry ops

**When:** Closing a thread, ratifying intake, retiring superseded law.

Registry ops module: `scripts/governance_registry_ops_v1.py`  
Daily CLI (wraps ops): `scripts/governance_intelligence_engine_v1.py`

```bash
# Read (no side effects)
python3 scripts/governance_intelligence_engine_v1.py registry-show --id <artifact_id> --json
python3 scripts/governance_intelligence_engine_v1.py registry-list --status ACTIVE --json

# Mutations — dry-run first (default), then --apply
python3 scripts/governance_intelligence_engine_v1.py registry-add --spec '<json>' --json
python3 scripts/governance_intelligence_engine_v1.py registry-add --spec '<json>' --apply --json

python3 scripts/governance_intelligence_engine_v1.py registry-amend \
  --id <amendment_id> --amends <base_id> --apply --json

python3 scripts/governance_intelligence_engine_v1.py registry-retire \
  --id <artifact_id> --reason 'superseded by X' --apply --json

python3 scripts/governance_intelligence_engine_v1.py registry-remove \
  --id <artifact_id> --apply --json   # SUPERSEDED rank>2 only
```

**Strict laws (machine-enforced):**

- Rank ≤2 never deleted — retire only  
- Retire before remove  
- Dependents block retire  
- No `--apply` without reviewing dry-run `ok` + `errors`

**Read output:**

| Label | JSON path |
|-------|-----------|
| Machine recommendation | `ok`, `dry_run`, `status`, `errors` |
| Required human/SG action | If `dry_run: true` → review then re-run with `--apply` |
| Registry status | `status` field on artifact row |
| Receipt path | `receipt_path` (only when `--apply` succeeds) |
| Live authority? | `status == ACTIVE` + receipt → **live**; `PROPOSED` / `RECORDED_*` → **not live** |

**Ladder after dry-run:** `staged` intent only.  
**Ladder after `--apply` + receipt:** `registered` or `ACTIVE` per status.

---

## Daily sequence (operator)

```
1. audit-selection   → pick finals from messy intake        → selected
2. thread-audit      → map progress + pending               → checked
3. impact            → on any doc you plan to change today  → checked
4. registry-*        → dry-run then --apply if closing      → registered/ACTIVE
5. Write daily run receipt (template below)
```

**Do not skip:** Receipt on any step that moves toward `registered` or `ACTIVE`.

---

## Output label cheat sheet

Every command JSON should be read for these five fields (derive if not explicit):

```json
{
  "machine_recommendation": "<what the machine advises>",
  "required_sg_action": "<what SG/human must do next>",
  "registry_status": "<ACTIVE|PROPOSED|…|null>",
  "receipt_path": "<path or null>",
  "live_authority": "<true only if registry ACTIVE + receipt; else false>"
}
```

Derive from machine output using tables in Steps A–D. Never treat `ACTIVE_AMENDMENT` on an intake file as live authority.

---

## Trust calibration

Known-answer matrix: `data/daily_governance_calibration_matrix_v1.json`  
Run calibration (founder-session-safe):

```bash
python3 scripts/validate_governance_intelligence_e2e_v1.py
```

Re-run after rubric or engine changes. Five core cases + registry ACTIVE check documented in matrix.

---

## Negative-proof gates (expect BLOCK)

Run dry-run only — never `--apply` on these:

| Test | Command | Expected block |
|------|---------|----------------|
| Rank ≤2 delete | `registry-remove --id gov-structure-authority-v1` | `only SUPERSEDED artifacts may be removed` |
| Duplicate ACTIVE id | `registry-add` with existing `founder-judgment-patterns-v1` | `duplicate artifact_id` |
| Wrong duplicate final | `audit-selection` on `…v1.md` + `…v1 2.md` | Primary excludes ` 2.md`; status `ACTIVE_AMENDMENT` not live |
| Staged ≠ ACTIVE | `registry-show --id noos-copilot-dispatcher-mode-v1` | `RECORDED_STEP_5` — not live authority |

Receipt: `receipts/daily-governance-negative-proof-20260704T043400Z.json`

---

## Sample daily run receipt

Template run: `receipts/daily-governance-machine-run-20260704T043400Z.json`

---

## What this runbook does NOT do

- Does not rebuild the intelligence engine  
- Does not bulk-promote intake to ACTIVE  
- Does not inject governance into worker prompts  
- Does not treat library file existence as authority  
- Does not modify P0 CORE

---

## Founder-session guard

- One light validation pass: `validate_governance_intelligence_e2e_v1.py`  
- No validator marathons on Mac  
- Heavy full audit → cloud CI / machine hub
