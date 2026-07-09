# Auth & Portfolio Upgrade — 214 Plans v1

**Generated:** 2026-07-08T08:02:52Z
**Authority:** SG cross-domain auth W11 + portfolio upgrade analysis
**Machine registry:** `data/auth_upgrade_214_v1.json`

## Summary

| Metric | Count |
|--------|-------|
| Total plans | 214 |
| P0 | 123 |
| P1 | 66 |
| P2 | 24 |
| P3 | 1 |

## Tracks

| Track | Name | IDs | Lane |
|-------|------|-----|------|
| A | Founder ratify & SG SSOT | AUTH-UPG-001–015 | sg_sssot |
| B | @noetfield/auth-core package | AUTH-UPG-016–030 | noos_agent |
| C | TrustField Phase 1 gate & portal | AUTH-UPG-031–060 | trustfield_worker |
| D | SourceA Phase 2 canonical auth | AUTH-UPG-061–085 | sourcea_worker |
| E | Noetfield www Phase 3 auth UI | AUTH-UPG-086–110 | noetfield_website |
| F | noetfeld-os API Phase 4 JWT | AUTH-UPG-111–125 | noos_agent |
| G | Supabase ops & redirect allow-list | AUTH-UPG-126–140 | founder_ops |
| H | SG probe motors & matrix | AUTH-UPG-141–155 | sg_sssot |
| I | Semantic drift L8 (Voyage anchors) | AUTH-UPG-156–170 | noos_agent |
| J | NOOS integrator & motor sustain | AUTH-UPG-171–190 | noos_agent |
| K | Institutional public_site compliance | AUTH-UPG-191–200 | noos_agent |
| L | Enterprise SSO deferred & W11 closeout | AUTH-UPG-201–214 | founder_ops |

## P0 plans (execute first)

- **AUTH-UPG-001** — Ratify auth project split law in matrix → `founder_decisions_ratified populated`
- **AUTH-UPG-002** — Ratify per-domain sessions decision → `matrix v1.2.0 saved`
- **AUTH-UPG-003** — Ratify P0 magic_link + email_password → `auth_methods_p0 locked`
- **AUTH-UPG-004** — Ratify TrustField first-ship target → `dispatch phase 1 authorized`
- **AUTH-UPG-006** — Update CROSS_DOMAIN_AUTH_RATIFY receipt → `P99 ledger row current`
- **AUTH-UPG-007** — Bump auth_surface_matrix to v1.2.0 → `version field matches probe`
- **AUTH-UPG-008** — Align auth_core_interface_spec split law → `identity_plane.auth_projects`
- **AUTH-UPG-010** — Lock venture repo ownership in matrix → `repo_ownership phase map`
- **AUTH-UPG-012** — Add tier 0 anti-login-wall law to probe → `must_not_redirect_to_auth checks`
- **AUTH-UPG-013** — Wire founder_decisions_pending empty → `all five in ratified array`
- **AUTH-UPG-014** — Receipt cross-domain-auth-w11-closeout → `receipts/*.json on disk`
- **AUTH-UPG-016** — Ship @noetfield/auth-core package.json → `packages/auth-core`
- **AUTH-UPG-017** — Export createBrowserClient adapter → `clients.ts`
- **AUTH-UPG-018** — Export createServerClient cookie adapter → `clients.ts`
- **AUTH-UPG-019** — Export evaluateAuthGuard middleware helper → `middleware.ts`
- **AUTH-UPG-020** — Export REQUIRED_AUTH_ROUTES constant → `constants.ts`
- **AUTH-UPG-021** — Export Venture Role AppMetadata types → `types.ts`
- **AUTH-UPG-022** — Unit test gated route redirect → `middleware.test.ts 3 pass`
- **AUTH-UPG-023** — Document getClaims server law in README → `packages/auth-core/README.md`
- **AUTH-UPG-024** — Peer dep @supabase/ssr in package → `package.json peerDependencies`
- **AUTH-UPG-025** — npm build dist/ typescript compile → `npm run build green`
- **AUTH-UPG-031** — Deploy paths.ts /partner-access gate → `live 302 on /partner-access`
- **AUTH-UPG-032** — Keep apply funnel tier-1 public → `/partner-access/apply 200`
- **AUTH-UPG-033** — Keep verify confirm public → `apply funnel ungated`
- **AUTH-UPG-034** — Room token bypass unchanged → `?token= skips gate`
- **AUTH-UPG-036** — Run configure_trustfield_supabase_auth_urls → `callback www.trustfield.ca`
- **AUTH-UPG-037** — Verify trustfield_profiles migration applied → `noetfield Supabase`
- **AUTH-UPG-038** — Partner Access session JWT on API → `supabase_user.py live`
- **AUTH-UPG-039** — Default post-auth /partner-access/platform → `destinations.ts`
- **AUTH-UPG-040** — Middleware getClaims not getSession → `middleware.ts law`
- **AUTH-UPG-042** — verify_trustfield_auth_surfaces_v1.sh PASS → `tier script green`
- **AUTH-UPG-043** — Flip matrix tf_partner_access to live → `after deploy 302`
- **AUTH-UPG-048** — Partner Access platform hub signed-in → `platform/page.tsx`
- **AUTH-UPG-049** — Briefing room access_token flow → `room?token=`
- **AUTH-UPG-050** — api.trustfield.ca health 200 → `tier-3 probe`
- **AUTH-UPG-053** — TrustField deploy receipt → `P99 or TF receipt`
- **AUTH-UPG-054** — SG probe tier-2 PASS post-deploy → `tf_partner_access PASS`
- **AUTH-UPG-056** — Cloudflare www.trustfield.ca deploy → `OpenNext worker`
- **AUTH-UPG-061** — Deploy auth/sign-in.html canonical route → `sourcea.app/auth/sign-in`
- **AUTH-UPG-062** — Deploy auth/sign-up.html → `sourcea.app/auth/sign-up`
- **AUTH-UPG-063** — Deploy auth/callback.html → `callback allow-list`
- **AUTH-UPG-064** — Deploy auth/sign-out.html → `sign-out route`
- **AUTH-UPG-066** — Contract SKU pages stay tier-0 → `validate-sourcea-contract-pages PASS`
- **AUTH-UPG-067** — operating-brain-install no auth wall → `probe sa_obi 200`
- **AUTH-UPG-068** — sourcea.ca avg no auth wall → `probe sa_ca_avg`
- **AUTH-UPG-069** — sourcea.uk eacp no auth wall → `probe sa_uk_eacp`
- **AUTH-UPG-070** — portfolio_spine Supabase callback → `sourcea.app/auth/callback`
- **AUTH-UPG-071** — Forge terminal funnel preserved → `profile→workspace`
- **AUTH-UPG-072** — routeAfterSignIn unchanged → `sourcea-platform-auth-v1.js`
- **AUTH-UPG-074** — Magic link P0 enabled → `portfolio_spine auth`
- **AUTH-UPG-078** — sync_sourcea_platform_auth_public_v1 → `anon key only public`
- **AUTH-UPG-080** — Matrix auth_routes sourcea partial→live → `after deploy`
- **AUTH-UPG-081** — SourceA deploy receipt → `git + live curl`
- **AUTH-UPG-082** — SG probe tier-0 regression check → `11/11 PASS`
- **AUTH-UPG-086** — Deploy auth/sign-in/index.html → `www.noetfield.com`
- **AUTH-UPG-087** — Deploy auth/sign-up → `sign-up page`
- **AUTH-UPG-088** — Deploy auth/callback PKCE handler → `nf-www-auth-v1.js`
- **AUTH-UPG-089** — Deploy auth/sign-out → `sign-out page`
- **AUTH-UPG-090** — sync_nf_www_auth_public_v1 from vault → `configured:true`
- **AUTH-UPG-091** — Header Sign in CTA → `partials/header.html`
- **AUTH-UPG-092** — Post-auth landing /start/ sandbox → `default_next`
- **AUTH-UPG-093** — noetfield Supabase project tkgpapowwplupyekpivy → `env pin`
- **AUTH-UPG-094** — Tier-0 homepage no login wall → `probe nf_home`
- **AUTH-UPG-095** — Tier-0 GEL page no login wall → `probe nf_gel`
- **AUTH-UPG-098** — Magic link + password P0 → `auth forms`
- **AUTH-UPG-099** — Flip matrix auth_routes noetfield partial→live → `after deploy`
- **AUTH-UPG-100** — www deploy Cloudflare Pages → `production`
- **AUTH-UPG-103** — Copilot demo stays public → `tier-0`
- **AUTH-UPG-104** — Pilot intake stays public → `tier-0 CTAs`
- **AUTH-UPG-108** — Noetfield deploy receipt → `live curl auth routes`
- **AUTH-UPG-109** — SG probe nf surfaces PASS → `tier-0`
- **AUTH-UPG-111** — Deploy supabase_jwt.py Bearer validation → `noetfeld-os`
- **AUTH-UPG-112** — JWT on POST /v1/decision → `require_decision_write_or_jwt`
- **AUTH-UPG-113** — X-API-Key path preserved → `backward compat`
- **AUTH-UPG-114** — /health unauthenticated → `tier-3 law`
- **AUTH-UPG-116** — NOETFIELD_SUPABASE_URL on gel-api Railway → `env sync`
- **AUTH-UPG-117** — NOETFIELD_SUPABASE_ANON_KEY on gel-api → `env sync`
- **AUTH-UPG-118** — test_supabase_jwt.py in CI → `pytest green`
- **AUTH-UPG-119** — User cookies never on CF motors → `tier-3 law audit`
- **AUTH-UPG-120** — Service role CI-only factory tables → `no browser service key`
- **AUTH-UPG-121** — api.noetfield.com JWT smoke → `Bearer curl`
- **AUTH-UPG-126** — Run configure_portfolio_auth_redirects_v1 → `SUPABASE_ACCESS_TOKEN`
- **AUTH-UPG-127** — portfolio_spine site_url sourcea.app → `Management API`
- **AUTH-UPG-128** — noetfield project site_url www.noetfield.com → `Management API`
- **AUTH-UPG-129** — trustfield.ca callbacks in allow-list → `uri_allow_list`
- **AUTH-UPG-131** — Enable email password provider P0 → `both projects`
- **AUTH-UPG-132** — Enable magic link P0 → `both projects`
- **AUTH-UPG-135** — trustfield_profiles trigger on auth.users → `migration 002`
- **AUTH-UPG-138** — Secrets never in repo audit → `split law`
- **AUTH-UPG-140** — Receipt auth-supabase-redirect-config → `receipts/`
- **AUTH-UPG-141** — sg_auth_surface_probe_v1 cron 6h → `GHA workflow`
- **AUTH-UPG-142** — verify_auth_surfaces_e2e_v1.py green tier-0 → `11/11`
- **AUTH-UPG-143** — trustfield_profiles subprobe on noetfield → `split law probe`
- **AUTH-UPG-144** — redirect_allow_list_lint PASS → `4 callbacks`
- **AUTH-UPG-145** — tier_2 gated WARN→PASS post-deploy → `tf_partner_access`
- **AUTH-UPG-148** — Matrix implementation fields current → `live vs partial`
- **AUTH-UPG-153** — Auth probe unit tests 10/10 → `test_verify_auth_surfaces`
- **AUTH-UPG-154** — Venture dispatch docs phase 1-4 → `docs/dispatch/`
- **AUTH-UPG-155** — SG must_not_own auth UI audit → `no UI in SG repo`
- **AUTH-UPG-156** — NOETFIELD_GITHUB_TOKEN org secret → `noetfeld-os GHA`
- **AUTH-UPG-157** — Re-run noetfield-open-pr-v1 workflow → `semantic drift PR`
- **AUTH-UPG-158** — Merge Noetfield L8 semantic drift → `issue #98`
- **AUTH-UPG-159** — nf_semantic_drift_v1.py on main → `Voyage anchors`
- **AUTH-UPG-160** — make nf-semantic-drift green → `Noetfield CI`
- **AUTH-UPG-161** — make nf-voyage-integrity green → `L8 gates`
- **AUTH-UPG-163** — semantic_anchors_v1.json SSOT pairs → `data file`
- **AUTH-UPG-164** — Probe drift pin separate lane → `nf-platform-deploy-pin`
- **AUTH-UPG-168** — Platform git_sha pin law → `deploy pin json`
- **AUTH-UPG-171** — integrator-repair-autorun fresh cycles → `factory rows`
- **AUTH-UPG-172** — motor-sustain-verify stale_count 0 → `ICL-D03`
- **AUTH-UPG-173** — GHA witness SLO repair → `ICL-D04`
- **AUTH-UPG-174** — dispatch noos-gha-health-witness → `workflow_dispatch`
- **AUTH-UPG-175** — dispatch noos-gha-autorun-witness → `workflow_dispatch`
- **AUTH-UPG-177** — NOOS_LOOP_SECRET Railway sync → `sync_railway script`
- **AUTH-UPG-178** — cloud-motor-resync after secret fix → `make target`
- **AUTH-UPG-179** — integrator daily 11/11 green → `closure_token green`
- **AUTH-UPG-182** — NOETFIELD_GITHUB_TOKEN unblock open-pr → `cross-lane`
- **AUTH-UPG-184** — loop-fleet-dispatch after repair → `CF ticks`
- **AUTH-UPG-190** — 24/7 loop registry no stale → `motor sustain`
- **AUTH-UPG-203** — Auth W11 full probe GREEN → `tier_0 + tier_2 PASS`
- **AUTH-UPG-204** — Cross-domain auth closeout v2 receipt → `all ventures deployed`
- **AUTH-UPG-206** — Founder sign-off auth upgrade → `P99 ledger`
- **AUTH-UPG-214** — CROSS_DOMAIN_AUTH_W11: green closure token → `final receipt`

## Analysis basis

- Cross-domain auth W11 ten-step upgrade (implemented code, pending deploy)
- SG `auth_surface_matrix_v1.json` v1.2.0 tier 0–3 surfaces
- TrustField Supabase SSR + Partner Access OS dual-auth
- SourceA Forge funnel + portfolio_spine split law
- Noetfield www static auth + noetfield Supabase project
- noetfeld-os `@noetfield/auth-core` + JWT on `/v1/decision`
- Semantic drift L8 handoff (issue #98, NOETFIELD_GITHUB_TOKEN)
- NOOS integrator motor sustain + GHA witness repair
- Institutional `public_site` privacy/cookies/a11y lane

## Regenerate

```bash
python3 scripts/gen_auth_upgrade_214_v1.py
```

