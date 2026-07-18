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
| 1 | Auth project | **RATIFIED 2026-07-18** | portfolio_spine only |
| 2 | Cross-brand login | PENDING | per-domain sessions (recommended) |
| 3 | P0 methods | PENDING | magic_link + email_password (recommended) |
| 4 | First ship | **RATIFIED 2026-07-18** | TrustField /register + portal |
| 5 | Enterprise SSO | PENDING | defer P2 (recommended) |

Phase 1 TrustField dispatch is authorized. This does not authorize cross-repo edits from SG, production secret changes, or bypass of venture tests.

**Signer:** Founder instruction executed through SG W11 auth upgrade.
