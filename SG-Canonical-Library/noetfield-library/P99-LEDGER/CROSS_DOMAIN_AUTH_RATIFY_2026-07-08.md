# CROSS DOMAIN AUTH — Ratification Receipt

**Date:** 2026-07-08
**Authority:** SG auth SSOT upgrade (W11)
**Artifact:** `docs/CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md`
**Matrix:** `data/auth_surface_matrix_v1.json` v1.2.0
**Interface spec:** `data/auth_core_interface_spec_v1.json`

## Ratified

1. **Cross-domain auth proposal v1.1** — tiered access law; identity plane split per `supabase-portfolio-tiers-v1.json`.
2. **Auth surface matrix v1.2.0** — machine-readable tier 0–3 surfaces + redirect allow-list + founder decisions locked.
3. **SG verify-only lane** — `sg_auth_surface_probe_v1` motor; no auth UI in SG.
4. **Venture dispatch** — Phase 1 TrustField, Phase 2 SourceA, Phase 3 Noetfield, Phase 4 NOOS (separate PRs).

## Founder decisions (ratified 2026-07-08)

| # | Decision | Ratified |
|---|----------|----------|
| 1 | Auth project | Split law: SourceA/Forge → portfolio_spine; Noetfield+TrustField → noetfield |
| 2 | Cross-brand login | per-domain sessions |
| 3 | P0 methods | magic_link + email_password |
| 4 | First ship | TrustField /register + Partner Access platform |
| 5 | Enterprise SSO | defer P2 |

**Signer:** Founder via SG W11 upgrade execution — matrix `founder_decisions_ratified` populated.
