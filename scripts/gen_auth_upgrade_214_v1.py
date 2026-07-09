#!/usr/bin/env python3
"""Generate AUTH-UPG-001–214 cross-domain upgrade registry from W11 analysis."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "data" / "auth_upgrade_214_v1.json"
OUT_MD = ROOT / "docs" / "AUTH_UPGRADE_214_PLANS_v1.md"

TRACKS = [
    ("A", "Founder ratify & SG SSOT", "sg_sssot", 1, 15),
    ("B", "@noetfield/auth-core package", "noos_agent", 16, 30),
    ("C", "TrustField Phase 1 gate & portal", "trustfield_worker", 31, 60),
    ("D", "SourceA Phase 2 canonical auth", "sourcea_worker", 61, 85),
    ("E", "Noetfield www Phase 3 auth UI", "noetfield_website", 86, 110),
    ("F", "noetfeld-os API Phase 4 JWT", "noos_agent", 111, 125),
    ("G", "Supabase ops & redirect allow-list", "founder_ops", 126, 140),
    ("H", "SG probe motors & matrix", "sg_sssot", 141, 155),
    ("I", "Semantic drift L8 (Voyage anchors)", "noos_agent", 156, 170),
    ("J", "NOOS integrator & motor sustain", "noos_agent", 171, 190),
    ("K", "Institutional public_site compliance", "noos_agent", 191, 200),
    ("L", "Enterprise SSO deferred & W11 closeout", "founder_ops", 201, 214),
]

# Per-track step templates (expanded to fill id range)
TEMPLATES: dict[str, list[tuple[str, str, str]]] = {
    "A": [
        ("Ratify auth project split law in matrix", "founder_decisions_ratified populated", "P0"),
        ("Ratify per-domain sessions decision", "matrix v1.2.0 saved", "P0"),
        ("Ratify P0 magic_link + email_password", "auth_methods_p0 locked", "P0"),
        ("Ratify TrustField first-ship target", "dispatch phase 1 authorized", "P0"),
        ("Defer enterprise SSO to P2", "founder_decisions #5 ratified", "P1"),
        ("Update CROSS_DOMAIN_AUTH_RATIFY receipt", "P99 ledger row current", "P0"),
        ("Bump auth_surface_matrix to v1.2.0", "version field matches probe", "P0"),
        ("Align auth_core_interface_spec split law", "identity_plane.auth_projects", "P0"),
        ("Publish SSOT_INDEX cross-domain auth row", "P2-SSOT/SSOT_INDEX.md", "P1"),
        ("Lock venture repo ownership in matrix", "repo_ownership phase map", "P0"),
        ("Document async-only cross-venture linking", "no cross-project joins law", "P1"),
        ("Add tier 0 anti-login-wall law to probe", "must_not_redirect_to_auth checks", "P0"),
        ("Wire founder_decisions_pending empty", "all five in ratified array", "P0"),
        ("Receipt cross-domain-auth-w11-closeout", "receipts/*.json on disk", "P0"),
        ("SG W11 wave milestone M_auth_locked", "living_system W11 complete flag", "P1"),
    ],
    "B": [
        ("Ship @noetfield/auth-core package.json", "packages/auth-core", "P0"),
        ("Export createBrowserClient adapter", "clients.ts", "P0"),
        ("Export createServerClient cookie adapter", "clients.ts", "P0"),
        ("Export evaluateAuthGuard middleware helper", "middleware.ts", "P0"),
        ("Export REQUIRED_AUTH_ROUTES constant", "constants.ts", "P0"),
        ("Export Venture Role AppMetadata types", "types.ts", "P0"),
        ("Unit test gated route redirect", "middleware.test.ts 3 pass", "P0"),
        ("Document getClaims server law in README", "packages/auth-core/README.md", "P0"),
        ("Peer dep @supabase/ssr in package", "package.json peerDependencies", "P0"),
        ("npm build dist/ typescript compile", "npm run build green", "P0"),
        ("TrustField adopt auth-core evaluateAuthGuard", "optional refactor paths.ts", "P2"),
        ("SourceA adopt auth-core browser client", "landing integration", "P1"),
        ("Noetfield www adopt auth-core constants", "nf-www-auth-v1.js align", "P1"),
        ("Publish auth-core to npm private registry", "founder gate", "P2"),
        ("Version bump auth-core 1.1.0", "changelog receipt", "P2"),
    ],
    "C": [
        ("Deploy paths.ts /partner-access gate", "live 302 on /partner-access", "P0"),
        ("Keep apply funnel tier-1 public", "/partner-access/apply 200", "P0"),
        ("Keep verify confirm public", "apply funnel ungated", "P0"),
        ("Room token bypass unchanged", "?token= skips gate", "P0"),
        ("Deploy customer-portal stub", "/customer-portal gated", "P1"),
        ("Run configure_trustfield_supabase_auth_urls", "callback www.trustfield.ca", "P0"),
        ("Verify trustfield_profiles migration applied", "noetfield Supabase", "P0"),
        ("Partner Access session JWT on API", "supabase_user.py live", "P0"),
        ("Default post-auth /partner-access/platform", "destinations.ts", "P0"),
        ("Middleware getClaims not getSession", "middleware.ts law", "P0"),
        ("Cache-Control private no-store auth routes", "auth pages headers", "P1"),
        ("verify_trustfield_auth_surfaces_v1.sh PASS", "tier script green", "P0"),
        ("Flip matrix tf_partner_access to live", "after deploy 302", "P0"),
        ("Flip matrix tf_customer_portal partial→live", "after deploy", "P1"),
        ("Admin token path unchanged", "console separate from Supabase", "P1"),
        ("Header Sign in / Platform UX", "header-auth-link.tsx", "P1"),
        ("Register page tier-1 optional", "/register 200", "P1"),
        ("Partner Access platform hub signed-in", "platform/page.tsx", "P0"),
        ("Briefing room access_token flow", "room?token=", "P0"),
        ("api.trustfield.ca health 200", "tier-3 probe", "P0"),
        ("api JWT on portal routes", "partner_access router", "P1"),
        ("Ops role gates admin partner-access", "isOpsProfile", "P1"),
        ("TrustField deploy receipt", "P99 or TF receipt", "P0"),
        ("SG probe tier-2 PASS post-deploy", "tf_partner_access PASS", "P0"),
        ("Railway plan-worker partner_access lane", "integrator ICL-D09 green", "P1"),
        ("Cloudflare www.trustfield.ca deploy", "OpenNext worker", "P0"),
        ("E2E sign-up magic link smoke", "manual or Playwright", "P1"),
        ("E2E sign-in password smoke", "staging", "P1"),
        ("Document dual-auth in TF AGENTS.md", "Supabase + admin token", "P2"),
        ("Customer portal feature expansion", "founder gate P2", "P2"),
    ],
    "D": [
        ("Deploy auth/sign-in.html canonical route", "sourcea.app/auth/sign-in", "P0"),
        ("Deploy auth/sign-up.html", "sourcea.app/auth/sign-up", "P0"),
        ("Deploy auth/callback.html", "callback allow-list", "P0"),
        ("Deploy auth/sign-out.html", "sign-out route", "P0"),
        ("Wire header CTA to /auth/sign-in", "tier-1 optional", "P1"),
        ("Contract SKU pages stay tier-0", "validate-sourcea-contract-pages PASS", "P0"),
        ("operating-brain-install no auth wall", "probe sa_obi 200", "P0"),
        ("sourcea.ca avg no auth wall", "probe sa_ca_avg", "P0"),
        ("sourcea.uk eacp no auth wall", "probe sa_uk_eacp", "P0"),
        ("portfolio_spine Supabase callback", "sourcea.app/auth/callback", "P0"),
        ("Forge terminal funnel preserved", "profile→workspace", "P0"),
        ("routeAfterSignIn unchanged", "sourcea-platform-auth-v1.js", "P0"),
        ("OAuth Google GitHub P1 providers", "Supabase dashboard", "P2"),
        ("Magic link P0 enabled", "portfolio_spine auth", "P0"),
        ("Local forge_local fallback when unconfigured", "configured:false path", "P1"),
        ("Chat Unify paywall sign-in link", "unify-access-gate.js", "P1"),
        ("Platform portal /platform hub", "platform-portal.html", "P1"),
        ("sync_sourcea_platform_auth_public_v1", "anon key only public", "P0"),
        ("Flip matrix sa_sandbox_cta to partial", "implementation field", "P1"),
        ("Matrix auth_routes sourcea partial→live", "after deploy", "P0"),
        ("SourceA deploy receipt", "git + live curl", "P0"),
        ("SG probe tier-0 regression check", "11/11 PASS", "P0"),
        ("Buyer sandbox gated route define", "tier-2 surface row", "P2"),
        ("command.sourcea.app team auth backlog", "upgrade registry defer", "P2"),
        ("RLS portfolio tiers slice 1", "backlog UPG", "P2"),
    ],
    "E": [
        ("Deploy auth/sign-in/index.html", "www.noetfield.com", "P0"),
        ("Deploy auth/sign-up", "sign-up page", "P0"),
        ("Deploy auth/callback PKCE handler", "nf-www-auth-v1.js", "P0"),
        ("Deploy auth/sign-out", "sign-out page", "P0"),
        ("sync_nf_www_auth_public_v1 from vault", "configured:true", "P0"),
        ("Header Sign in CTA", "partials/header.html", "P0"),
        ("Post-auth landing /start/ sandbox", "default_next", "P0"),
        ("noetfield Supabase project tkgpapowwplupyekpivy", "env pin", "P0"),
        ("Tier-0 homepage no login wall", "probe nf_home", "P0"),
        ("Tier-0 GEL page no login wall", "probe nf_gel", "P0"),
        ("Gated sandbox route after auth", "tier-2 define", "P2"),
        ("profiles venture noetfield on signup", "metadata venture", "P1"),
        ("Magic link + password P0", "auth forms", "P0"),
        ("Flip matrix auth_routes noetfield partial→live", "after deploy", "P0"),
        ("www deploy Cloudflare Pages", "production", "P0"),
        ("NF probe sync EXPECTED_GIT_SHA GHA", "CLOUDFLARE_API_TOKEN", "P1"),
        ("Semantic drift separate from auth", "L8 track I", "P1"),
        ("Copilot demo stays public", "tier-0", "P0"),
        ("Pilot intake stays public", "tier-0 CTAs", "P0"),
        ("Auth pages noindex", "robots noindex", "P1"),
        ("Cookie consent on www if analytics", "separate from auth", "P2"),
        ("E2E sign-in smoke staging", "manual", "P1"),
        ("Noetfield deploy receipt", "live curl auth routes", "P0"),
        ("SG probe nf surfaces PASS", "tier-0", "P0"),
        ("Sandbox server-side session spec", "docs/start/SANDBOX_*", "P2"),
    ],
    "F": [
        ("Deploy supabase_jwt.py Bearer validation", "noetfeld-os", "P0"),
        ("JWT on POST /v1/decision", "require_decision_write_or_jwt", "P0"),
        ("X-API-Key path preserved", "backward compat", "P0"),
        ("/health unauthenticated", "tier-3 law", "P0"),
        ("/readiness policy gate unchanged", "health.py", "P1"),
        ("NOETFIELD_SUPABASE_URL on gel-api Railway", "env sync", "P0"),
        ("NOETFIELD_SUPABASE_ANON_KEY on gel-api", "env sync", "P0"),
        ("test_supabase_jwt.py in CI", "pytest green", "P0"),
        ("User cookies never on CF motors", "tier-3 law audit", "P0"),
        ("Service role CI-only factory tables", "no browser service key", "P0"),
        ("api.noetfield.com JWT smoke", "Bearer curl", "P0"),
        ("Document JWT auth in API README", "gel-api docs", "P1"),
        ("Portal audit routes API-key only", "portal/routes.py unchanged", "P1"),
        ("Multi-region gel-api JWT parity", "yyz + ord", "P1"),
        ("gel-api deploy receipt", "UPG-0209", "P1"),
    ],
    "G": [
        ("Run configure_portfolio_auth_redirects_v1", "SUPABASE_ACCESS_TOKEN", "P0"),
        ("portfolio_spine site_url sourcea.app", "Management API", "P0"),
        ("noetfield project site_url www.noetfield.com", "Management API", "P0"),
        ("trustfield.ca callbacks in allow-list", "uri_allow_list", "P0"),
        ("localhost:3000 dev callback", "matrix allow-list", "P1"),
        ("Enable email password provider P0", "both projects", "P0"),
        ("Enable magic link P0", "both projects", "P0"),
        ("Google OAuth P1 optional", "founder gate", "P2"),
        ("GitHub OAuth P1 optional", "founder gate", "P2"),
        ("trustfield_profiles trigger on auth.users", "migration 002", "P0"),
        ("profiles table on portfolio_spine defer", "split law", "P2"),
        ("Auth health probe WARN repair", "auth/v1/health", "P1"),
        ("Secrets never in repo audit", "split law", "P0"),
        ("~/.sourcea-secrets vault paths documented", "AGENTS.md", "P1"),
        ("Receipt auth-supabase-redirect-config", "receipts/", "P0"),
    ],
    "H": [
        ("sg_auth_surface_probe_v1 cron 6h", "GHA workflow", "P0"),
        ("verify_auth_surfaces_e2e_v1.py green tier-0", "11/11", "P0"),
        ("trustfield_profiles subprobe on noetfield", "split law probe", "P0"),
        ("redirect_allow_list_lint PASS", "4 callbacks", "P0"),
        ("tier_2 gated WARN→PASS post-deploy", "tf_partner_access", "P0"),
        ("fail_on_warn CI mode optional", "founder gate", "P2"),
        ("auth-surface-probe receipt archive", "receipts/auth-surface-probe-*", "P1"),
        ("Matrix implementation fields current", "live vs partial", "P0"),
        ("closed_loop probe→repair documented", "SG motor doc", "P1"),
        ("Deadman sourcea-deadman-v1 wired", "LS-112", "P1"),
        ("Cross-bind SSOT_INDEX auth row", "P2-SSOT", "P1"),
        ("Living system LS-111–113 COMPLETE", "110 plans json", "P1"),
        ("Auth probe unit tests 10/10", "test_verify_auth_surfaces", "P0"),
        ("Venture dispatch docs phase 1-4", "docs/dispatch/", "P0"),
        ("SG must_not_own auth UI audit", "no UI in SG repo", "P0"),
    ],
    "I": [
        ("NOETFIELD_GITHUB_TOKEN org secret", "noetfeld-os GHA", "P0"),
        ("Re-run noetfield-open-pr-v1 workflow", "semantic drift PR", "P0"),
        ("Merge Noetfield L8 semantic drift", "issue #98", "P0"),
        ("nf_semantic_drift_v1.py on main", "Voyage anchors", "P0"),
        ("make nf-semantic-drift green", "Noetfield CI", "P0"),
        ("make nf-voyage-integrity green", "L8 gates", "P0"),
        ("Hybrid chatbot retrieval when Voyage active", "semantic scoring", "P1"),
        ("semantic_anchors_v1.json SSOT pairs", "data file", "P0"),
        ("Probe drift pin separate lane", "nf-platform-deploy-pin", "P0"),
        ("CLOUDFLARE_API_TOKEN on Noetfield repo", "probe sync GHA", "P1"),
        ("Mirror branch closeout receipt", "noetfeld-os", "P1"),
        ("Telegram recovery on FAIL→PASS", "probe cron", "P1"),
        ("Platform git_sha pin law", "deploy pin json", "P0"),
        ("Semantic drift not confused with auth", "separate tracks", "P1"),
        ("L8 receipt in noetfeld-os proof", "receipts/proof/", "P1"),
    ],
    "J": [
        ("integrator-repair-autorun fresh cycles", "factory rows", "P0"),
        ("motor-sustain-verify stale_count 0", "ICL-D03", "P0"),
        ("GHA witness SLO repair", "ICL-D04", "P0"),
        ("dispatch noos-gha-health-witness", "workflow_dispatch", "P0"),
        ("dispatch noos-gha-autorun-witness", "workflow_dispatch", "P0"),
        ("TrustField partner_access lane green", "ICL-D09", "P1"),
        ("NOOS_LOOP_SECRET Railway sync", "sync_railway script", "P0"),
        ("cloud-motor-resync after secret fix", "make target", "P0"),
        ("integrator daily 11/11 green", "closure_token green", "P0"),
        ("gel-api multi-region ord canary", "UPG-0209", "P1"),
        ("Enterprise GHA billing gate triage", "ICL-D11", "P2"),
        ("NOETFIELD_GITHUB_TOKEN unblock open-pr", "cross-lane", "P0"),
        ("Integrator daily receipt commit", "founder optional", "P2"),
        ("loop-fleet-dispatch after repair", "CF ticks", "P0"),
        ("tf-cf-fleet-tick sustain", "TrustField worker", "P1"),
        ("Autorun repair receipt fresh", "noos-integrator-autorun-repair", "P1"),
        ("ICL-P2 lanes complete", "integrator status", "P1"),
        ("Machine loops audit chain ok", "ICL-D05", "P1"),
        ("Stack health receipt green", "noos-stack-health", "P1"),
        ("24/7 loop registry no stale", "motor sustain", "P0"),
    ],
    "K": [
        ("Commit public_site privacy route", "noetfeld-os", "P1"),
        ("Commit public_site cookies route", "noetfeld-os", "P1"),
        ("Cookie banner essential-only default", "cookies.js", "P1"),
        ("Cookie preferences modal", "base.html", "P1"),
        ("Skip link + mobile nav a11y", "site.js site.css", "P1"),
        ("Partner gateway form validation", "gateway.html", "P1"),
        ("test_public_site_v1.py pass", "pytest", "P1"),
        ("Decide public_site active vs legacy", "founder decision", "P2"),
        ("Institutional site separate from www.noetfield.com", "scope law", "P1"),
        ("Footer legal links privacy cookies", "base.html", "P1"),
    ],
    "L": [
        ("Enterprise SSO discovery defer P2", "founder decision #5", "P2"),
        ("SAML OIDC vendor shortlist", "founder gate", "P3"),
        ("Auth W11 full probe GREEN", "tier_0 + tier_2 PASS", "P0"),
        ("Cross-domain auth closeout v2 receipt", "all ventures deployed", "P0"),
        ("Living system W12 auth deploy wave", "next 110 plans", "P2"),
        ("Founder sign-off auth upgrade", "P99 ledger", "P0"),
        ("Buyer journey map post-auth", "verdict pipeline", "P1"),
        ("Claim-risk matrix auth surfaces", "NF-PUB track", "P1"),
        ("NW1 motion auth alignment", "business strategy doc", "P2"),
        ("Annual auth key rotation procedure", "UPG-0115 align", "P2"),
        ("npm @noetfield/auth-core v1 stable", "publish", "P2"),
        ("Document per-domain session UX", "buyer-facing", "P1"),
        ("Remove getSession-only server paths audit", "venture PRs", "P1"),
        ("CROSS_DOMAIN_AUTH_W11: green closure token", "final receipt", "P0"),
    ],
}


def expand_track(track_id: str, name: str, lane: str, start: int, end: int) -> list[dict]:
    templates = TEMPLATES[track_id]
    count = end - start + 1
    plans: list[dict] = []
    for i in range(count):
        n = start + i
        if i < len(templates):
            title, done_when, priority = templates[i]
        else:
            title = f"{name} — sustain step {i + 1}"
            done_when = "receipt or probe PASS"
            priority = "P2"
        plans.append(
            {
                "id": f"AUTH-UPG-{n:03d}",
                "track": track_id,
                "track_name": name,
                "lane": lane,
                "priority": priority,
                "title": title,
                "done_when": done_when,
                "status": "pending",
                "parent": "docs/CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md",
            }
        )
    return plans


def main() -> int:
    all_plans: list[dict] = []
    for track_id, name, lane, start, end in TRACKS:
        all_plans.extend(expand_track(track_id, name, lane, start, end))

    assert len(all_plans) == 214, f"expected 214 plans, got {len(all_plans)}"

    doc = {
        "schema": "auth_upgrade_214_v1",
        "version": "1.0.0",
        "saved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "authority": "SG (SSSOT)",
        "parent_proposal": "docs/CROSS_DOMAIN_AUTH_PROPOSAL_v1.1_LOCKED.md",
        "parent_matrix": "data/auth_surface_matrix_v1.json",
        "parent_closeout": "receipts/cross-domain-auth-w11-closeout-2026-07-08.json",
        "law": "Tier 0 public · Tier 2 gated · per-domain sessions · split-law identity · one repo per PR",
        "tracks": [{"id": t[0], "name": t[1], "lane": t[2], "range": f"AUTH-UPG-{t[3]:03d}–{t[4]:03d}"} for t in TRACKS],
        "summary": {
            "total": 214,
            "p0": sum(1 for p in all_plans if p["priority"] == "P0"),
            "p1": sum(1 for p in all_plans if p["priority"] == "P1"),
            "p2": sum(1 for p in all_plans if p["priority"] == "P2"),
            "p3": sum(1 for p in all_plans if p["priority"] == "P3"),
        },
        "plans": all_plans,
    }

    OUT_JSON.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Auth & Portfolio Upgrade — 214 Plans v1",
        "",
        f"**Generated:** {doc['saved_at']}",
        "**Authority:** SG cross-domain auth W11 + portfolio upgrade analysis",
        "**Machine registry:** `data/auth_upgrade_214_v1.json`",
        "",
        "## Summary",
        "",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total plans | 214 |",
        f"| P0 | {doc['summary']['p0']} |",
        f"| P1 | {doc['summary']['p1']} |",
        f"| P2 | {doc['summary']['p2']} |",
        f"| P3 | {doc['summary']['p3']} |",
        "",
        "## Tracks",
        "",
        "| Track | Name | IDs | Lane |",
        "|-------|------|-----|------|",
    ]
    for t in doc["tracks"]:
        lines.append(f"| {t['id']} | {t['name']} | {t['range']} | {t['lane']} |")

    lines.extend(["", "## P0 plans (execute first)", ""])
    for p in all_plans:
        if p["priority"] == "P0":
            lines.append(f"- **{p['id']}** — {p['title']} → `{p['done_when']}`")

    lines.extend(
        [
            "",
            "## Analysis basis",
            "",
            "- Cross-domain auth W11 ten-step upgrade (implemented code, pending deploy)",
            "- SG `auth_surface_matrix_v1.json` v1.2.0 tier 0–3 surfaces",
            "- TrustField Supabase SSR + Partner Access OS dual-auth",
            "- SourceA Forge funnel + portfolio_spine split law",
            "- Noetfield www static auth + noetfield Supabase project",
            "- noetfeld-os `@noetfield/auth-core` + JWT on `/v1/decision`",
            "- Semantic drift L8 handoff (issue #98, NOETFIELD_GITHUB_TOKEN)",
            "- NOOS integrator motor sustain + GHA witness repair",
            "- Institutional `public_site` privacy/cookies/a11y lane",
            "",
            "## Regenerate",
            "",
            "```bash",
            "python3 scripts/gen_auth_upgrade_214_v1.py",
            "```",
            "",
        ]
    )

    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(all_plans)} plans -> {OUT_JSON}")
    print(f"Wrote index -> {OUT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
