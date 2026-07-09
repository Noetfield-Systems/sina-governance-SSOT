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

## Founder decisions (pending explicit lock)

| # | Decision | Recommended |
|---|----------|-------------|
| 1 | Auth project | portfolio_spine only |
| 2 | Cross-brand login | per-domain sessions |
| 3 | P0 methods | magic_link + email_password |
| 4 | First ship | TrustField /register + portal |
| 5 | Enterprise SSO | defer P2 |

**Signer:** SG W11 auth upgrade — proposal LOCKED on disk.
