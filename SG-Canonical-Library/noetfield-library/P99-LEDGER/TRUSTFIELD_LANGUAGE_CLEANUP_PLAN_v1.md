# TRUSTFIELD_LANGUAGE_CLEANUP_PLAN_v1

**Generated:** 2026-07-07T10:32:22Z UTC
**Task:** tf-language-cleanup-v1
**SG pin:** `a51025f` on `cursor/language-layer-v1`
**Mode:** dry scan only — **no rewrites applied**

---

## Scan summary

| Metric | Value |
|--------|-------|
| Files scanned | 471 |
| Total findings | 1302 |
| Safe rewrites planned | 0 |
| Backlog (human review) | 582 |
| Public-surface backlog | 0 |
| Public high-risk (reg/entity) | 0 |

## Key finding

**trustfield.ca web copy (`web/`): 0 regulatory self-claim hits** after RPAA allowlist — backlog is mostly internal docs (entity alias history + policy quote files).

## Findings by class

- **SG_DICTIONARY_TERM:** 639
- **CONFLICT_PHRASE:** 292
- **ENTITY_ALIAS_RISK:** 280
- **TRUSTFIELD_LOCAL_TERM:** 81
- **REGULATORY_COPY_RISK:** 10

## High-risk samples (regulatory / entity)

- `docs/CURSOR_REVENUE_PROMPT.md:17` — **REGULATORY_COPY_RISK** — `we are an MSP` (MSP self-identification)
- `docs/DEMO_SHOWCASE.md:62` — **REGULATORY_COPY_RISK** — `we are an MSP` (MSP self-identification)
- `docs/FIX_NOW_API_AND_GATES.md:89` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/FIX_NOW_API_AND_GATES.md:103` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/GIT_EMAIL_GITHUB.md:12` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/INDEX.md:109` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/INSTITUTIONAL_REDESIGN_10_STEPS.md:136` — **REGULATORY_COPY_RISK** — `we process payments` (payment processing self-claim)
- `docs/MACLAW_PORTFOLIO_ACCOUNT_MAP_PROPOSAL.md:22` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/MACLAW_PORTFOLIO_SYNC_MANIFEST.md:23` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/OPS_RUNBOOK.md:8` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/SITE_CLARITY_CHECK.md:18` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/TRUSTFIELD_GOOGLE_WORKSPACE_SMTP_LOCKED_v1.md:13` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/TRUSTFIELD_PHASE1_FREE.md:62` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/TRUSTFIELD_SOURCE_OF_TRUTH.md:44` — **REGULATORY_COPY_RISK** — `we are an MSP` (MSP self-identification)
- `docs/TRUSTFIELD_SOURCE_OF_TRUTH.md:110` — **REGULATORY_COPY_RISK** — `we are an MSP` (MSP self-identification)
- `docs/TRUSTFIELD_SOURCE_OF_TRUTH.md:141` — **REGULATORY_COPY_RISK** — `we are an MSP` (MSP self-identification)
- `docs/VERCEL_BLOCKED_FIX.md:47` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/VERCEL_PERSONAL_IMPORT.md:20` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/VERCEL_TEAM_BLOCK_FIX.md:52` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/VERCEL_TEAM_BLOCK_FIX.md:81` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/VERCEL_UNBLOCK_NOW.md:27` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/VERCEL_UNBLOCK_NOW.md:52` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/gtm/BC_AI_PROCUREMENT_COVER_LETTER.md:23` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/gtm/CANADA_AI_GOVERNANCE_HALF_PAGE.md:1` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))
- `docs/gtm/CANADA_AI_GOVERNANCE_ONE_PAGER.md:1` — **ENTITY_ALIAS_RISK** — `TrustField Technologies` (retired entity alias (partial))

## Planned actions

| Action | Count | Rule |
|--------|-------|------|
| `apply_safe` | 0 | Blocked this pass |
| `backlog_human_review` | 582 | REGULATORY / PUBLIC / CONFLICT only |
| `inventory_only` | 720 | Local + SG term hits |

## SG gap routing

- `NEEDS_SG_ENTRY` hits: 0
- Route to SG pile — do not define in TrustField overlay without founder lock

## Next pass (not this task)

1. Founder/legal review of REGULATORY_COPY_RISK backlog on `web/lib/company-copy.ts`
2. Safe alias pass (TrustField entity) only after review
3. Mirror overlay to TrustField-Technologies when approved

**Forbidden:** repo edits · public rewrite · invented MSB/PSP/custody claims

*tf-language-cleanup-v1 · dry scan plan only*
