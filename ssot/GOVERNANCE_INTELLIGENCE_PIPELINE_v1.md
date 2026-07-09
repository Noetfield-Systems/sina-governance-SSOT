# Governance Intelligence Pipeline v1.1 — Production

**Status:** ACTIVE  
**Owner:** SG (`sina-governance-ssot`)  
**Authority:** [GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md](GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md)  
**Registry:** [data/governance_artifact_registry_v1.json](../data/governance_artifact_registry_v1.json)  
**Review queue:** [data/governance_review_queue_v1.json](../data/governance_review_queue_v1.json)  
**Completeness rubric:** [data/governance_completeness_rubric_v1.json](../data/governance_completeness_rubric_v1.json)  
**Engine:** `scripts/governance_intelligence_engine_v1.py`  
**Validator:** `scripts/validate_governance_intelligence_v1.py`  
**E2E validator:** `scripts/validate_governance_intelligence_e2e_v1.py` (Raw AI fixture cases)  
**Shell:** `scripts/validate-governance-intelligence-v1.sh`

---

## One sentence

> **When governance changes, the production machine classifies layer, domain, version, lineage, conflicts, pointer drift, and downstream updates — then writes a review queue and receipt before any agent treats the change as live law.**

---

## Production stack

| Stage | Command | Output |
|-------|---------|--------|
| 1. Register | `data/governance_artifact_registry_v1.json` | artifact graph with layer, domain, version, status, rank, dates |
| 2. Discover | `engine scan --json` | unregistered candidates + classification drift |
| 3. Classify | `engine classify --path <file> --json` | layer/domain/status + confidence |
| 4. Impact | `engine impact --path <file> --json` | lineage, downstream artifacts, must-update pointers |
| 5. Graph | `engine graph --json` | depends_on / amends / amended_by map |
| 6. Conflicts | `engine conflicts --json` | true conflicts + stale-language hits |
| 7. Review queue | `engine review-queue --json` | machine-owned human review items |
| 8. Audit | `engine audit --json --write-receipt` | full production audit + receipt |
| 9. Score | `engine score --path <file> --json` | deterministic completeness breakdown |
| 10. Final selection | `engine audit-selection --paths a,b,c --cluster-by thread --json` | which doc + which parts become final per thread |
| 11. Thread audit | `engine thread-audit --root <folder> --json --write-receipt` | threads, completion, pending, change quality |
| 12. Session story | `engine session-story --root <folder> --plain-only` | plain-language whole story + founder intent guess |
| 13. Merge plan | `engine merge-plan --root <folder> --json` | manual + auto-safe merge actions |
| 14. Merge apply | `engine merge-apply --root <folder> [--apply]` | dry-run or stage to SG intake |
| 15. Second pass | `engine second-pass-audit --root <folder> --plain-only` | evidence-based path recheck (no hardcoded names) |
| 16. Validate | `validate_governance_intelligence_v1.py` | registry + audit + e2e + threads + structure tree |

Wired into `run_machine_autonomy_cycle_v1.py` as L2 machine validation.

---

## Daily registry + thread ops (strict)

| Action | Command | Rule |
|--------|---------|------|
| Structure tree | `engine structure-tree --json` | layers, domains, machines, artifacts_by_layer |
| List rules | `engine registry-list [--layer P0] [--domain automation]` | read registry |
| Show rule | `engine registry-show --id <artifact_id>` | lineage + amended_by |
| Add rule | `engine registry-add --spec '<json>'` | dry-run; add `--apply` to write |
| Amend rule | `engine registry-amend --id X --amends Y --apply` | sets ACTIVE_AMENDMENT + amends link |
| Retire rule | `engine registry-retire --id X --reason '...' --apply` | SUPERSEDED only — never delete live base |
| Remove rule | `engine registry-remove --id X --apply` | only SUPERSEDED rank>2, no dependents |
| List threads | `engine thread-list --json` | daily thread registry |
| Register thread | `engine thread-register --thread-id X --from-staging --apply` | promote intake staging |
| Retire thread | `engine thread-retire --thread-id X --reason '...' --apply` | mark RETIRED |
| Strict validate | `validate_registry_structure_v1.py` | tree ↔ registry ↔ machines |

**Strict laws:** rank ≤2 rows never deleted · retire before remove · dependents block retire · version law unchanged.

---

## What the machine detects

### Classification
- P-layer placement
- domain
- version from filename/frontmatter
- saved date
- authority rank
- confidence score

### Impact
- self layer
- affected layers
- lineage (`depends_on`, `amends`, `amended_by`)
- downstream artifacts that reference the changed rule
- entry points that must update
- stale-language risk

### True conflicts
- authority owner mismatch
- missing lineage targets
- pointer drift in entry points
- stale governance wording in live surfaces
- classification drift between registry and detected file

### Review queue
Machine writes actionable queue rows:
- unregistered candidates
- classification drift
- pointer drift
- stale language
- lineage/conflict issues

### Thread intelligence (advisory sessions)
- normalizes filenames into stable `thread_id` (strips version, timestamp, role suffix)
- assigns roles: `spec`, `proposal`, `conflict_log`, `implementation_prompt`, `discovery_report`, `duplicate_copy`
- reads edit logs → **change timeline** with rationale per version bump
- scores each change **good / bad / neutral** from deterministic signals (corrected, false claim, scoped, etc.)
- sets **completion_state**: `COMPLETED`, `PENDING_FOUNDER`, `PENDING_THREAD`, `IN_PROGRESS`, `LEFT_ABANDONED`
- surfaces **pending_items** (founder approval, phase gate, dependent patch) and **left_abandoned** stale copies
- links threads (`resolved_by`, `blocked_by`, `references`) when one doc mentions another

### Intake sink promotion (evidence-based — NOT folder names)
- **Rules SSOT:** `data/governance_intake_sink_rules_v1.json` + `data/governance_intake_path_rubric_v1.json`
- **Sink detection:** deepest cluster with dated/versioned files, edit logs, zip bundles (`detect_probable_final_folder`)
- **Scan scope:** all `.md` + `.zip` inside evidence sink; high-signal root `.md` patterns; exclude `Prompts/`, `/tests/`, `/fixtures/`, Finder duplicates, `deep-research`
- **Zip bundles:** inner path map by artifact signature; prefer `patched` > `batch` > `mvp` zip names
- **Artifact recognition:** filename/body signatures in sink rules — not folder name (Raw AI `Tag/` was test fixture only)
- **Promote:** `promote-intake-drafts --root <any>` → `docs/governance_drafts_intake_v1/` → registry `PROPOSED` → thread register → SG-controlled library copy (never bulk-promote; never inject into agent prompts)
- **Completion:** unregistered governance draft → `AWAITING_REGISTRY_ENTRY`; registered + pending library → `PENDING_LIBRARY_PROMOTE`
- **Deprecated aliases:** `promote-tag-drafts`, `promote-intake-artifacts` (same engine path)

### Session story + merge layers
- **Repo map** (`data/governance_repo_map_v1.json`) — SG guard/registry/intake; library asset/law surface; ventures; Raw AI intake
- **Dispatch routing:** Tier 0 + role law + mission brief + mechanical gates only (`agent-layered-law-least-knowledge-v1`)
- **Second-pass machine** (`second-pass-audit`) — re-ranks by evidence (depth, dates, edit logs, versions) — **not** hardcoded folder names
- **Founder arc inference** — guesses what the founder was doing across threads (brain vocabulary split, traceability, etc.)
- **Save location index** — where the most complete file for each thread lives today + where it should promote
- **Plain story** — readable narrative: progress, why, what's done vs pending, next steps
- **Merge plan** — auto-safe (stage to `data/governance_intake_staging_v1/`, section adopt) vs manual (ratification, registry, cross-repo)
- **Merge apply** — dry-run by default; `--apply` copies intake finals into SG staging only

### Final selection (long sessions)
- groups selected docs by domain + layer
- scores completeness + **progress** deterministically (filename timestamp, edit log, semantic version in filename)
- ranks candidates by authority, **progress**, completeness, date, filename/body version, status, registry
- intake docs with `PROPOSED` header or edit log classify as `ACTIVE_AMENDMENT` (not plain `ACTIVE`)
- Finder duplicate suffixes (` 2.md`, ` 3.md`) penalized
- chooses primary final carrier
- chooses amendment finals and base retain docs
- emits section-level merge plan (`adopt_section_into_primary`, `add_section_to_primary`)
- voids low-value duplicates as pointer-only

---

## Operator commands

```bash
cd ~/Projects/sina-governance-ssot

# Founder-session-safe full validation
bash scripts/validate-governance-intelligence-v1.sh

# Full production audit + receipt
python3 scripts/governance_intelligence_engine_v1.py audit --json --write-receipt

# New/changed rule impact
python3 scripts/governance_intelligence_engine_v1.py impact --path ssot/NEW_RULE_v1.md --json --write-receipt

# Review what still needs human closure
python3 scripts/governance_intelligence_engine_v1.py review-queue --json

# Long advisory session — thread-aware final-version decision
python3 scripts/governance_intelligence_engine_v1.py audit-selection \
  --paths ~/Desktop/Raw\ AI/... \
  --cluster-by thread --json --write-receipt

# Full thread map: completed vs pending vs left, with change quality
python3 scripts/governance_intelligence_engine_v1.py thread-audit \
  --root ~/Desktop/Raw\ AI --json --write-receipt

# Plain-language whole story (founder intent, repo map, save locations, next steps)
python3 scripts/governance_intelligence_engine_v1.py session-story \
  --root ~/Desktop/Raw\ AI --plain-only --write-receipt

# Evidence-based second machine (works on any intake tree — Raw AI was test fixture only)
python3 scripts/governance_intelligence_engine_v1.py second-pass-audit \
  --root ~/Desktop/Raw\ AI --plain-only --write-receipt

# Coherence gate — fails if winners contradict evidence
python3 scripts/validate_intake_coherence_v1.py

# Evidence intake sink → PROPOSED registry (folder name does NOT matter; Tag was test fixture only)
python3 scripts/governance_intelligence_engine_v1.py promote-intake-drafts \
  --root ~/Desktop/Raw\ AI --json
python3 scripts/governance_intelligence_engine_v1.py promote-intake-drafts \
  --root ~/Downloads --json

python3 scripts/validate_intake_sink_v1.py
python3 scripts/governance_intelligence_engine_v1.py merge-plan --root ~/Desktop/Raw\ AI --json
python3 scripts/governance_intelligence_engine_v1.py merge-apply --root ~/Desktop/Raw\ AI
python3 scripts/governance_intelligence_engine_v1.py merge-apply --root ~/Desktop/Raw\ AI --apply

# Score one doc completeness
python3 scripts/governance_intelligence_engine_v1.py score --path ssot/FOUNDER_CANON_v1.md --json
```

---

## Change workflow

1. Governance change lands in SG repo only.  
2. `classify` → proposed layer/domain/status.  
3. `impact` → downstream files, lineage, pointers.  
4. Update registry row.  
5. Update library/product copies as pointers only.  
6. `audit --write-receipt`.  
7. `validate_governance_intelligence_v1.py`.  
8. Machine autonomy cycle receipt proves closure.

Founder is not the classifier. The machine is.

---

## Forbidden

- Defining governance structure outside SG repo  
- Labeling live base rules `superseded`  
- Treating library copies as owners of structure/version law  
- Shipping governance changes without audit receipt  
- Ignoring open high-severity review queue items
