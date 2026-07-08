# OPEN ITEMS — as of 2026-07-07

## REAL BLOCKERS (currently: none technical)
Per `P2-SSOT/OPEN_BLOCKERS.md` — no remaining technical blocker.

## STATUS SNAPSHOT (2026-07-07)
- Agent-read staleness gate: PASS — 15 alive surfaces, 0 blockers, 0 warnings (`receipts/agent-read-staleness-20260707T234651Z.json`).
- Branch `cursor/language-layer-v1`: 18 commits ahead of `main`, not yet merged. `check.py` advisory FAIL is expected (compares against `origin/main`, which predates this branch) — not a defect, but a merge is pending.
- Committed today: library-wide language_gate scan sidecars (50 files), 6 staleness receipts, `decision_language_machine_v1` output/receipts, workflow_census script/rules updates. Commit is local only — push to origin blocked (no git credentials in this environment); push manually or from an authenticated session.

## CLOSED (v0.9 upgrade pass)
- **SUPABASE_URL** — RESOLVED. Credentials live in Sina env files (not Railway): `~/.sourcea-secrets/noetfield.env` (`NOETFIELD_SUPABASE_*`) and `~/.sourcea-secrets/portfolio-spine.env` (`SUPABASE_URL`). Verifier probe PASS 2026-07-05 (`scripts/verify_supabase_live_profiles_v1.py`).
- **Supabase pause email (cybzznaieigeveiaoyoa)** — personal-org orphan, NOT production; both live refs OK. See `SUPABASE_PAUSE_TRIAGE_RECEIPT_2026-07-05.md`.
- P0 verify gaps — closed (P0_VERIFY_RECEIPT_2026-07-05.md)
- 6/6 lane preflight receipts — closed (LANE_PREFLIGHT_RECEIPTS_2026-07-05/)
- Governance hotspots (STEP10 merge, brain_deployment_state.json, SSOT v6 authority) — closed
- Revenue-start gates — closed (Brain Agent + Mac Worker receipts 2026-07-05)
- BRAIN_REGISTRY v0.1.4 on-disk — partial inventory confirmed (`sourcea-brain-registry-inventory-v1.json`); full Phase-2 activation still gated

## TARGETS (run + pursue in parallel — NOT blockers)
- Build the deterministic brain: `decision-core-v1` → `soup-wall-v1` → `learning-proposal-v1` (on the Llama mouth + substrate).
- 4 founder claim decisions gate `locked-definitions` → live_locked (`sourcea_is_live` signal; `forge_terminal_guaranteed_live_runtime`; `every_possible_run_has_public_proof` → narrow to designed-around-receipts; `broken_gears` → author 3-gear ladder).
- Prove Zero-Drift on SourceA (unlocks Tier 2 Operating Brain Install).
- **Tier 1 AI Spend Leak Audit pilot** — launch authorized 2026-07-05; recruit first customer.
- Build the IDE agentic lane (understanding→planner→router→workers→critic→aggregator) — candidate first Line Engine instance.
- Test the kill-switch before any unattended shipping.
- Migrate library artifact filenames to the ratified versioning form.
- Bulk supporting-law review (296 quarantined files) — out of scope for v0.9 pass.

## KNOWN OLDER OPEN (from gap audit — verify status)
- 90 competitor plans (producing or dead dispatch?); Founder Email Factory (broken — fix or kill?); public API HTML defect on sales surface; Canada funding doors (un-actioned); distribution line (not built).

**TRIAGE NEEDED (flagged 2026-07-07):** None of the 5 items above have an assigned owner or fix/kill decision on record in this repo. An agent cannot resolve these without live status checks in the relevant lanes (competitor-plans dispatch, Email Factory logs, sales-surface API, funding-doors tracker, distribution-line spec) — each needs a founder or lane-owner call. Recommend assigning one owner per item next session rather than leaving them open-ended.

---
*v0.3 (2026-07-07 — status snapshot + stale-item triage flag added)*
