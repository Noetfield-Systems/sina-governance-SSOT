# CROSS DOMAIN AUTH — Ratification Receipt

**Date:** 2026-07-08
**Authority:** SG auth SSOT upgrade (W11)
**Artifact:** `docs/CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md`
**Matrix:** `data/auth_surface_matrix_v1.json` v1.1.0
**Interface spec:** `data/auth_core_interface_spec_v1.json`

## Ratified

1. **Cross-domain auth proposal v1.1** — tiered access law; portfolio_spine sole identity plane (recommended).
2. **Auth surface matrix** — machine-readable tier 0–3 surfaces + redirect allow-list.
3. **SG verify-only lane** — `sg_auth_surface_probe_v1` motor; no auth UI in SG.
4. **Venture dispatch** — Phase 1 TrustField, Phase 2 SourceA, Phase 4 NOOS (separate PRs).

## Founder decisions

| # | Decision | State | Value |
|---|----------|-------|-------|
| 1 | Auth projects | **RATIFIED 2026-07-18 · CORRECTED AFTER TRUSTFIELD PREFLIGHT** | SourceA → portfolio_spine; Noetfield/TrustField → noetfield |
| 2 | Cross-brand login | PENDING | per-domain sessions (recommended) |
| 3 | P0 methods | PENDING | magic_link + email_password (recommended) |
| 4 | First ship | **RATIFIED 2026-07-18** | TrustField /register + portal; public recruitment landing preserved, private workspace gated |
| 5 | Enterprise SSO | PENDING | defer P2 (recommended) |

Phase 1 TrustField dispatch is authorized. TrustField uses the `noetfield` Supabase project and gates `/partner-access/workspace` plus `/customer-portal`; `/partner-access` remains public. This does not authorize cross-repo edits from SG, production secret changes, or bypass of venture tests.

## Phase 1 closure

`LIVE_VERIFIED` on 2026-07-18. TrustField PR #60 deployed main `2e862346668dfeea2806055de62f8c6c5cc24155`, adding the completed-intake handoff to `/auth/sign-up?next=/customer-portal`. SG cloud run `29642379016` proved public landing PASS, workspace and customer portal auth redirects PASS, noetfield Auth health PASS, and `trustfield_profiles` PASS. TrustField deploy run `29642763388` passed and the portal-account CTA was verified live. Next venture action advances to SourceA Phase 2.

**Signer:** Founder instruction executed through SG W11 auth upgrade.
