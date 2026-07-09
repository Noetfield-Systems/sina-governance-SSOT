# Missing or unverified (P0) — VERIFIED 2026-07-05

**Status:** P0 verify pass complete (Step 1 / v0.9 upgrade)

| Item | Prior status | Verify result | Evidence |
|------|--------------|---------------|----------|
| `000-founder-rules.mdc` | INSTALLED — verify active | **RETIRED** | File self-labels `SUPERSEDED`; `alwaysApply: false`. Use `.cursor/rules/agent-founder-intent-first.mdc` + `027-agent-report-plan-story-v1.mdc`. R-split (v0.1.2) still cites R1–R7 domain tags from this file location; file kept for link resolution only — not active law. |
| Cloud Kernel v1.2 full schema | NOT FOUND | **RESOLVED** | `P4/SOURCEA_SSOT_v1.2_MASTER_ARCH_LOCKED.pdf` present |
| GOVERNED_AUTORUN_LAWS_v3 | placeholder | **VERIFIED** | Installed from active SourceA docs (189 lines) |
| machine-process-loops-v1.json | archive-origin verify | **VERIFIED** | Schema `machine-process-loops-v1` v1.2.0; `loops_doc` → MACHINE_LOOPS_v1; loop IDs (LP-WORKER-EXEC, LP-MACHINE-VALID, LP-ADVERSARIAL, LP-CRITIC, etc.) match implementation map in P1-CANON/MACHINE_LOOPS_v1.md |
| founder-trigger-retirement-registry-v1.json | archive-origin verify | **VERIFIED** | Referenced by MACHINE_LOOPS_v1 retirement SSOT section; schema consistent |
| supporting-law (296 files) | placeholder | **QUARANTINED** | See `supporting-law/SUPPORTING_LAW_QUARANTINE_MANIFEST.md` |

**Verify receipt:** `P99-LEDGER/P0_VERIFY_RECEIPT_2026-07-05.md`

**Remaining founder-gated (non-blocking):**
- supporting-law batch ratify (296 files)
- 4 founder claim decisions (P6 locked-definitions → live_lock)

---

*v0.2 (2026-07-05) — Step 1 complete. 000-founder-rules RETIRED; machine-loops JSON verified against MACHINE_LOOPS v1.*
