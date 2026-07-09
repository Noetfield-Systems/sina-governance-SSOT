# PR Conflict Resolver Skill — LOCKED v1

**Status:** LOCKED — 2026-07-08  
**Authority:** SG (SSSOT) + NOOS integrator  
**Unlock:** Founder gate only — do not weaken L1 stop rules or receipt requirements.

## Locked artifacts

| Artifact | Path |
|---|---|
| Canonical skill | `skills/pr-conflict-resolver/SKILL.md` |
| Eval rubric | `skills/pr-conflict-resolver/evals/evals.json` |
| Benchmark | `skills/pr-conflict-resolver/evals/benchmark.json` |
| Desktop eval app (SSOT) | `desktop-app/PR-Conflict-Resolver-Report.app` |
| Desktop shortcut | `~/Desktop/PR-Conflict-Resolver-Report.app` |
| Machine lock manifest | `data/pr_conflict_skill_lock_v1.json` |
| Verifier | `scripts/verify_pr_conflict_skill_v1.py` |

## Mandatory law

1. **Classify before resolving** — registry / receipt / LOCKED / generated / code.
2. **L1 duplicate ownership** — same key, different motor → STOP, do not commit.
3. **LOCKED canon** — never present a self-resolved final merge; founder escalation.
4. **Receipts** — append-only; rename on collision, never drop.
5. **Post-resolve** — run verifier + write resolution receipt before merge-ready claim.

## Machine enforcement

- SG: `python3 scripts/verify_pr_conflict_skill_v1.py`
- SourceA: `bash scripts/validate-pr-conflict-resolver-mandatory-v1.sh` · `pr_conflict_resolver_first_check_v1.py` in session gate + pre_write_guard
- NOOS: `python3 scripts/verify_pr_conflict_resolution_v1.py` (GEL CI)
- Cursor: `pre_write_guard` blocks governance paths with conflict markers without ack
- Agent surfaces: `data/agent_read_surfaces_v1.json` → `skills_resolve` for `noos_agent` + `sg_sssot_cursor`

## Eval benchmark (locked baseline)

With-skill pass rate **100%** on evals 1, 3, 4; without-skill **50–80%** on LOCKED/registry cases.  
Open desktop app to review before changing this skill.
