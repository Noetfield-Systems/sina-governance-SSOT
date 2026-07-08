#!/usr/bin/env python3
"""P0-PGR Strategic Campaign Planner v1 (Phase 1, shadow-only).

Reads the board (evidence bundle + census + registry + commercial state),
generates 10 candidate shadow packets across the 6 board axes, runs the
canonical CHESS pass (Forecast -> Patch -> Proceed -> Verify) on each move,
compiles delivery-aware v1.1 packets, lints them, makes route decisions
only, and emits one campaign receipt + updated Phase 1 scorecard.

Shadow-only: dispatch_now is false on every move. No execution, no deploy,
no merge, no authority-plane change, no scheduled automation, no Mac runner.
Weak moves become DEGRADED/PROVISIONAL/REPAIR_CANDIDATE, never STOP.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_evidence_reader_v1 import collect as collect_evidence  # noqa: E402
from p0pgr_packet_lint_v1 import lint_packet  # noqa: E402

OUTBOX = ROOT / "receipts" / "p0pgr" / "outbox"
CAMPAIGNS = ROOT / "receipts" / "p0pgr" / "campaigns"
SCORECARD = ROOT / "receipts" / "p0pgr" / "phase1_scorecard_v1.json"
CHESS_CLI = ROOT / "scripts" / "chess_pass_cli_v1.py"
CAMPAIGN_ID = "P0PGR-CAMPAIGN-20260708-001"

ROUTE_VERDICT = {
    "CLOUD_ONLY": "DISPATCH_CLOUD",
    "HYBRID_MAC": "DISPATCH_MAC",
    "HUMAN_REVIEW": "HUMAN_REVIEW_PACKET",
    "FOUNDER_ONLY": "FOUNDER_ONLY",
}

BASE_CONSTRAINTS = [
    "no P0 leakage",
    "no speculative PASS",
    "receipt required",
    "stop after completion",
    "read-only outside receipts/p0pgr/",
    "do not claim any audited issue is fixed",
]
BASE_FORBIDDEN = [
    "no repo moves",
    "no authority flip",
    "no deploy",
    "no merge",
    "no healing or repair edits",
    "no PASS based on self-report or prose-as-proof",
]
BASE_RECEIPT_FIELDS = ["evidence", "changed_files", "commands_run", "pass_fail", "next_pointer"]


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def chess_pass(move: dict) -> dict:
    """Run the canonical CHESS pass CLI (heuristic, not a blocker)."""
    payload = json.dumps({
        "raw_move": move["task"],
        "immediate_goal": move["immediate_goal"],
        "protected_assets": move["protected_assets"],
        "verification_after_execution": move["verification_after_execution"],
        "patch_before_execution": move.get("patch_before_execution"),
    })
    try:
        out = subprocess.run(
            [sys.executable, str(CHESS_CLI)], input=payload,
            capture_output=True, text=True, timeout=30,
        )
        return json.loads(out.stdout)
    except Exception as exc:  # noqa: BLE001 — continuity: degrade, don't stop
        return {"action": "DEGRADED", "error": str(exc)[:200]}


def compile_packet(move: dict, seq: int) -> dict:
    packet = {
        "id": f"P0PGR-20260708-{seq:03d}",
        "created_at": utcnow(),
        "lane": move["lane"],
        "problem_class": move["problem_class"],
        "owner_agent": move["owner_agent"],
        "model_tier": move["model_tier"],
        "roi_score": move["roi_score"],
        "roi_reason": move["roi_reason"],
        "value_class": move["value_class"],
        "cost_limit_usd": move["cost_limit_usd"],
        "authority_scope": "observe",
        "execution_mode": move["execution_mode"],
        "delivery_route": move["delivery_route"],
        "target_executor": move["target_executor"],
        "repo": move.get("repo", "sina-governance-ssot"),
        "worktree_required": False,
        "local_secrets_required": False,
        "cloud_safe": move["execution_mode"] == "CLOUD_ONLY",
        "fallback_route": move["fallback_route"],
        "quality_handling": {
            "default_on_low_quality": "provisional",
            "allowed_result_states": ["PASS", "PARTIAL", "PROVISIONAL", "NEEDS_RETRY", "NEEDS_REVIEW"],
            "hard_block_allowed_reasons": [],
            "low_quality_required_labels": ["confidence", "scope", "reversibility", "next_improvement"],
        },
        "context_summary": move["board_signal"][:1200],
        "task": move["task"],
        "allowed_actions": move["allowed_actions"],
        "constraints": BASE_CONSTRAINTS + move.get("extra_constraints", []),
        "forbidden_actions": BASE_FORBIDDEN + move.get("extra_forbidden", []),
        "stop_rule": move["stop_rule"],
        "success_receipt": {
            "required_fields": BASE_RECEIPT_FIELDS + move.get("extra_receipt_fields", []),
            "external_verification_required": True,
            "cost_fields_required": True,
        },
        "evidence_refs": move["evidence_refs"],
        "decision_ref": CAMPAIGN_ID,
        "concurrency_key": "p0pgr-dispatch",
        "dispatch_mode": "shadow",
    }
    if move["execution_mode"] == "HYBRID_MAC":
        packet["canonical_path"] = move["canonical_path"]
        packet["mac_required_reason"] = move["mac_required_reason"]
    return packet


def moves() -> list[dict]:
    """The 10 candidate moves across the 6 board axes (evidence-authored)."""
    return [
        # ---- AXIS 1: runtime health -------------------------------------
        dict(
            move_id="M01", axis="runtime_health", reuse_packet="P0PGR-20260708-002",
            board_signal="census RED: 8/38 loops rule-1 'never produced receipt'; NONE class burns ~$20/mo",
            immediate_goal="Classify all 8 receipt-less loops from evidence; no healing",
            protected_assets=["registry entries", "live loops that ARE working", "receipts ledger"],
            commercial_consequence="Indirect: restores trust in registry so revenue loops can be believed; kills ~$20/mo dead spend after follow-up packets",
            roi_score=76, reversibility="full (read-only)",
            execution_mode="CLOUD_ONLY", delivery_route="github_action",
            target_executor="claude_code_cli", fallback_route="mac_runner",
            verification_after_execution=["8-row verdict table present", "each row cites file/glob evidence", "no run was triggered"],
            founder_rewrite_likelihood="low", phase2_candidate=True,
            # packet fields unused for reuse move:
            lane="SG", problem_class="verification", owner_agent="verifier",
            model_tier="cheap", value_class="risk_reduction", cost_limit_usd=2.0,
            roi_reason="-", task="(reuses existing packet P0PGR-20260708-002)",
            allowed_actions=[], stop_rule="-", evidence_refs=["receipts/workflow-census-20260706T093358Z.json"],
        ),
        # ---- AXIS 2: authority wiring -----------------------------------
        dict(
            move_id="M02", axis="authority_wiring",
            board_signal="Wiring currency for SG/NOOS/SourceA/Library unproven: alive docs data/agent_read_surfaces_v1.json and registry claims not re-verified since census RED; example packet 001 was never promoted to a real packet.",
            immediate_goal="Promote the wiring audit to a real shadow packet: prove registry entries, alive-doc pointers, and receipt globs are current without agent self-report",
            protected_assets=["data/github_automation_registry_v1.json", "alive docs", "lane boundaries"],
            likely_misread="Auditor may 'fix' dangling pointers instead of reporting them",
            second_move_risk="If wiring is stale, every campaign packet routes on wrong assumptions",
            third_move_consequence="Phase 2 auto-dispatch built on a stale registry would misfire packets into dead lanes",
            patch_before_execution="Report-only wording enforced: verdicts CURRENT|STALE|DANGLING|NO_RECEIPT per surface; repairs are separate packets",
            commercial_consequence="Indirect: Phase 2 automation cannot ship on unproven wiring; blocks premature spend",
            roi_score=82, reversibility="full (read-only)",
            execution_mode="CLOUD_ONLY", delivery_route="github_action",
            target_executor="claude_code_cli", fallback_route="mac_runner",
            verification_after_execution=["per-surface verdict table", "census diff vs 20260706 flags", "staleness gate output captured"],
            founder_rewrite_likelihood="low", phase2_candidate=True,
            lane="SG", problem_class="verification", owner_agent="verifier",
            model_tier="cheap", value_class="risk_reduction", cost_limit_usd=3.0,
            roi_reason="All downstream dispatch inherits registry trust; mechanical evidence sweep, cheap tier, removes recurring founder verification burden.",
            task="Audit wiring currency for SG / NOOS / SourceA / Library from repo evidence only: 1) run scripts/verify_agent_read_staleness_v1.sh and capture output; 2) map each registry motor to its newest matching receipt (glob evidence, timestamps); 3) cross-check data/agent_read_surfaces_v1.json pointers against files on disk, list dangling pointers; 4) diff current state against census 20260706T093358Z audit_flags (resolved/persisting/new); 5) emit one receipt with per-surface verdict CURRENT|STALE|DANGLING|NO_RECEIPT.",
            allowed_actions=["read data/, receipts/, ssot/, scripts/, .github/workflows/", "run existing verify/audit scripts", "write one receipt to receipts/p0pgr/"],
            stop_rule="Stop after the single wiring receipt; flagged items become future repair packets.",
            evidence_refs=["data/github_automation_registry_v1.json", "data/agent_read_surfaces_v1.json", "receipts/workflow-census-20260706T093358Z.json"],
        ),
        # ---- AXIS 4: live truth ------------------------------------------
        dict(
            move_id="M03", axis="live_truth",
            board_signal="trustfield.ca is live ('launch credibility pass active' per P10 product layer doc) with published claims: sandbox at /register, CAD 4,000 RPAA Readiness Discovery, partner surfaces. No receipt proves live pages currently match repo claims; deploy stamps unverified; L12 drift undetected.",
            immediate_goal="External live-truth audit: fetch public trustfield.ca surfaces and diff against repo-documented claims and deploy receipts",
            protected_assets=["live site availability", "published pricing claims", "partner funnel routes"],
            likely_misread="Auditor may treat marketing wording differences as drift, or follow redirects and mask broken routes",
            second_move_risk="False-drift noise creates repair packets for non-problems",
            third_move_consequence="Real drift left undetected becomes a public false claim — commercial credibility damage at first partner due-diligence",
            patch_before_execution="Redirects OFF, full-body hash per URL (L4), classify diffs as CONTENT_DRIFT|ROUTE_DEAD|CLAIM_MISMATCH|COSMETIC; cosmetic is reportable not actionable",
            commercial_consequence="Direct: protects the CAD 4,000 discovery offer funnel and partner due-diligence credibility; a dead /register route is lost revenue today",
            roi_score=84, reversibility="full (read-only external fetch)",
            execution_mode="CLOUD_ONLY", delivery_route="cloudflare_worker",
            target_executor="custom_script", fallback_route="github_action",
            verification_after_execution=["per-URL status+hash table", "redirects OFF evidenced", "claims diff table vs repo docs"],
            founder_rewrite_likelihood="medium", phase2_candidate=True,
            lane="TrustField", problem_class="verification", owner_agent="verifier",
            model_tier="capable", value_class="revenue_path", cost_limit_usd=4.0,
            roi_reason="Live public claims back the CAD 4k offer; drift or dead routes directly cost partner conversions. External probe satisfies L4/L12.",
            task="Audit live truth for trustfield.ca: 1) fetch /, /register, partner program and partner-access pages from the raw public hostname, redirects OFF, record status + full-body hash per URL; 2) extract live claims (sandbox availability, CAD 4,000 discovery, partner surfaces) and diff against P10-PRODUCT-LAYERS/TRUSTFIELD_PARTNER_ACCESS_PLATFORM_v1.md and readiness ledger; 3) check deploy stamps/receipts freshness; 4) classify each diff CONTENT_DRIFT|ROUTE_DEAD|CLAIM_MISMATCH|COSMETIC; 5) emit one receipt. No claim that anything is fixed.",
            allowed_actions=["external HTTP GET on public trustfield.ca URLs (redirects OFF)", "read SG-Canonical-Library P10/P99 TrustField docs", "write one receipt to receipts/p0pgr/"],
            extra_constraints=["external fetch only from runner the builder does not control (L4)"],
            stop_rule="Stop after live-truth receipt; repairs/redeploys are separate founder-visible packets.",
            evidence_refs=["SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/TRUSTFIELD_PARTNER_ACCESS_PLATFORM_v1.md"],
        ),
        # ---- AXIS 3: commercial readiness --------------------------------
        dict(
            move_id="M04", axis="commercial_readiness",
            board_signal="TrustField Partner Access OS funnel (apply -> email verify -> NDA -> briefing room) is the gated acquisition path for strategic contributors; feature parity and no-downgrade after launch credibility pass is unproven.",
            immediate_goal="Walk the partner funnel as an outside user (sandbox scope), verify every step reachable and no capability silently downgraded",
            protected_assets=["working funnel steps", "NDA gating", "briefing room access control", "existing partner accounts"],
            likely_misread="Tester may create junk accounts in production or treat gated 403s as failures",
            second_move_risk="Test artifacts pollute partner data; false RED on intentionally-gated steps",
            third_move_consequence="Real funnel breakage found by a genuine director-track candidate instead of by us — lost strategic hire/partner",
            patch_before_execution="Use clearly-labeled test identity, sandbox tier only; gated-by-design steps are PASS-gated not FAIL; no NDA actually signed",
            commercial_consequence="Direct: this funnel is the acquisition route for partners and director-track candidates; each silent break costs conversions and credibility",
            roi_score=80, reversibility="high (test identity, no destructive ops)",
            execution_mode="CLOUD_ONLY", delivery_route="queue_cloud_worker",
            target_executor="custom_script", fallback_route="human_review_queue",
            verification_after_execution=["per-step reachability table", "no-downgrade diff vs documented features", "test identity cleanup receipt"],
            founder_rewrite_likelihood="medium", phase2_candidate=False,
            lane="TrustField", problem_class="revenue", owner_agent="verifier",
            model_tier="capable", value_class="revenue_path", cost_limit_usd=5.0,
            roi_reason="Partner funnel is the live commercial acquisition path; verifying parity protects conversions at near-zero risk (test identity, sandbox).",
            task="Audit TrustField partner funnel readiness end-to-end with a labeled test identity at sandbox tier: 1) /register self-serve flow reachable and completes; 2) partner-access apply -> email verify -> NDA gate -> briefing room sequence: each step reachable, gating intact (gated-by-design = PASS); 3) diff available features against documented parity list (no silent downgrade); 4) record evidence per step; 5) emit one receipt with per-step verdicts. Do NOT sign a real NDA; do NOT create non-labeled accounts.",
            allowed_actions=["sandbox-tier funnel walk with labeled test identity", "read TrustField readiness ledger docs", "write one receipt to receipts/p0pgr/"],
            extra_forbidden=["no real NDA signature", "no production partner data touched", "no unlabeled test accounts"],
            stop_rule="Stop after funnel receipt + test-identity cleanup note; fixes are separate packets.",
            evidence_refs=["SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/TRUSTFIELD_PARTNER_ACCESS_PLATFORM_v1.md"],
        ),
        dict(
            move_id="M05", axis="commercial_readiness",
            board_signal="commercial_pulse_queue_v1 exists (lane: metabolism) with CASL dispatchability predicates (named_icp_stranger, priced_offer_attached, casl_mailing_address, casl_unsubscribe, link_check_receipt...) but census shows REVENUE loop gateway_outbound_log_v1 with zero receipts (rule-4). Outbound commercial motion is designed but unproven.",
            immediate_goal="Audit whether the commercial pulse loop can actually produce one dispatchable, CASL-compliant outbound draft — readiness only, nothing sent",
            protected_assets=["CASL compliance gates", "founder approval gate before any send", "TrustField entity hygiene"],
            likely_misread="Auditor may draft-and-send, or mark predicates PASS from config presence rather than evidence",
            second_move_risk="A non-compliant outbound send is an irreversible external action with legal exposure (CASL)",
            third_move_consequence="Regulatory complaint or spam-flagging poisons the domain for all future TrustField outreach",
            patch_before_execution="Send remains founder_blocked by state machine; audit checks each predicate with evidence; output is a readiness verdict per predicate, not a send",
            commercial_consequence="Direct: unlocks the first compliant revenue outreach; every week the pulse loop stays unproven is a week of zero outbound pipeline",
            roi_score=78, reversibility="full (audit only; send stays founder-gated)",
            execution_mode="CLOUD_ONLY", delivery_route="queue_cloud_worker",
            target_executor="claude_code_cli", fallback_route="human_review_queue",
            verification_after_execution=["per-predicate evidence table", "confirmation nothing entered 'sent' state", "gateway_outbound_log_v1 receipt gap explained"],
            founder_rewrite_likelihood="medium", phase2_candidate=False,
            lane="Revenue", problem_class="revenue", owner_agent="revenue_agent",
            model_tier="capable", value_class="revenue_path", cost_limit_usd=4.0,
            roi_reason="First provable step toward outbound revenue; audit-only scope keeps CASL risk at zero while removing the biggest unknown in the revenue path.",
            task="Audit commercial pulse dispatch readiness: 1) evaluate every dispatchability predicate in data/commercial_pulse_queue_v1.json against current evidence (config, receipts, docs) — verdict per predicate PASS|FAIL|NO_EVIDENCE; 2) explain why REVENUE loop gateway_outbound_log_v1 has zero receipts (census rule-4); 3) confirm queue state machine keeps sends founder_blocked; 4) list the minimum missing pieces for one compliant draft; 5) emit one receipt. NOTHING is sent; no state advances to approved_pending_send or beyond.",
            allowed_actions=["read data/commercial_pulse_queue_v1.json, docs/commercial_pulse_loop_v0.1.md, receipts/", "run scripts/commercial_pulse_dispatch_check_v1.py read-only", "write one receipt to receipts/p0pgr/"],
            extra_forbidden=["no outbound send of any kind", "no queue state advancement", "no contact data collection"],
            stop_rule="Stop after readiness receipt; drafting/sending are separate founder-gated packets.",
            evidence_refs=["data/commercial_pulse_queue_v1.json", "receipts/workflow-census-20260706T093358Z.json"],
        ),
        # ---- AXIS 5: cost/ROI governance ----------------------------------
        dict(
            move_id="M06", axis="cost_roi_governance",
            board_signal="Census rule-2: META cost exceeds GUARD+REVENUE combined; NONE-class dead loops burn ~$20/mo; spend governor exists on paper (router rules) but has no enforcement receipt; no per-loop cost attribution receipts.",
            immediate_goal="Spend-shape audit: attribute monthly cost per loop/value_class from evidence, flag every dollar with value_class none, verify governor thresholds are computable from receipts",
            protected_assets=["working REVENUE and GUARD loops", "budget caps policy ($1.5k pre-revenue)"],
            likely_misread="Auditor may recommend killing loops outright — decommission is an authority action, not an audit output",
            second_move_risk="Miscounted costs lead to throttling a loop that was actually earning",
            third_move_consequence="Wrong THROTTLED_ROI policy starves a revenue loop while dead META spend continues",
            patch_before_execution="Output is attribution table + governor-computability verdict only; kill/throttle recommendations are ranked candidates, never actions",
            commercial_consequence="Direct ROI: reclaims up to ~$20/mo immediately identifiable dead spend and makes L11 governor enforceable before Phase 2 spending starts",
            roi_score=74, reversibility="full (read-only)",
            execution_mode="CLOUD_ONLY", delivery_route="github_action",
            target_executor="claude_code_cli", fallback_route="mac_runner",
            verification_after_execution=["per-loop cost table sums to census totals", "governor computability verdict with formula inputs evidenced"],
            founder_rewrite_likelihood="low", phase2_candidate=True,
            lane="Ops", problem_class="hygiene", owner_agent="verifier",
            model_tier="cheap", value_class="risk_reduction", cost_limit_usd=2.0,
            roi_reason="Phase 2 will spend real money; an unenforceable governor plus $20/mo dead spend is the cheapest fix on the board.",
            task="Cost/ROI governance audit: 1) build per-loop monthly cost attribution from census + registry + billing-relevant configs; 2) verify totals reconcile with census costs_usd_month; 3) flag every loop with value_class none and its spend; 4) verify the spend governor thresholds (monthly cap, THROTTLED_ROI trigger) are computable from existing receipts — list missing inputs; 5) rank kill/throttle CANDIDATES (no action); 6) emit one receipt.",
            allowed_actions=["read receipts/, data/, docs/", "write one receipt to receipts/p0pgr/"],
            stop_rule="Stop after attribution receipt; any throttle/kill is a separate founder-visible packet.",
            evidence_refs=["receipts/workflow-census-20260706T093358Z.json", "data/workflow_census_value_class_rules_v1.json"],
        ),
        # ---- AXIS 6: delivery readiness ------------------------------------
        dict(
            move_id="M07", axis="delivery_readiness",
            board_signal="Phase 2 needs a supply of CLOUD_ONLY-safe packet templates; currently packets are authored ad hoc. No inventory exists of which recurring problems are cloud-executable end-to-end.",
            immediate_goal="Discover and inventory every recurring problem class that is provably cloud-executable, producing Phase-2-ready packet templates",
            protected_assets=["packet schema v1.1 invariants", "least-knowledge rule (no P0 in templates)"],
            likely_misread="Template generator may bake P0 reasoning into templates or over-generalize one-off tasks into fake recurring classes",
            second_move_risk="Bad templates mass-produce bad packets in Phase 2 — error amplification",
            third_move_consequence="Phase 2 autonomy ships packets nobody needed; ROI collapses and founder trust in autonomy resets to zero",
            patch_before_execution="Every template must cite >=2 historical receipts proving the problem recurs; templates lint-checked with same rules as packets; P0-fingerprint sweep on all templates",
            commercial_consequence="Indirect but compounding: this is the packet factory — it converts founder prompt-writing into a reusable asset (proof_asset)",
            roi_score=88, reversibility="full (produces template files only)",
            execution_mode="CLOUD_ONLY", delivery_route="github_action",
            target_executor="claude_code_cli", fallback_route="mac_runner",
            verification_after_execution=["each template cites >=2 receipts", "all templates pass packet lint", "0 P0 fingerprints in templates"],
            founder_rewrite_likelihood="low", phase2_candidate=True,
            lane="SG", problem_class="architecture", owner_agent="architect",
            model_tier="capable", value_class="proof_asset", cost_limit_usd=5.0,
            roi_reason="Highest workload-reduction move on the board: converts recurring problems into lint-clean reusable templates, the direct input to Phase 2 autonomy.",
            task="Cloud-executable packet discovery: 1) sweep receipts/ and registry for recurring problem classes (staleness, census, wiring, live-truth, cost attribution); 2) for each class with >=2 historical receipts, draft a v1.1 packet TEMPLATE (CLOUD_ONLY, observe scope) with parameter slots; 3) lint every template with scripts/p0pgr_packet_lint_v1.py; 4) sweep templates for P0 fingerprints; 5) emit one receipt listing templates + lint results, templates saved under receipts/p0pgr/templates/.",
            allowed_actions=["read receipts/, data/, docs/, scripts/", "write templates to receipts/p0pgr/templates/", "write one receipt to receipts/p0pgr/"],
            extra_receipt_fields=["template_inventory", "lint_results"],
            stop_rule="Stop after template inventory receipt; enabling templates for auto-dispatch is a Phase 2 founder decision.",
            evidence_refs=["receipts/p0pgr/P0PGR-CYCLE-20260708T131523Z.json", "data/github_automation_registry_v1.json"],
        ),
        dict(
            move_id="M08", axis="delivery_readiness",
            board_signal="Router doctrine says ~20% of work is Mac-bound, but no evidence-backed inventory exists of WHICH loops/tasks genuinely require local Mac state (launchd truth, local secrets, local repos) vs merely assumed to.",
            immediate_goal="Produce the Mac-required truth list: for every registry motor and known task class, verdict CLOUD_OK|MAC_REQUIRED(reason)|UNKNOWN from repo evidence",
            protected_assets=["Mac 90s founder-session law (INCIDENT-039)", "local secrets (never enumerated in output)"],
            likely_misread="Auditor may try to probe the live Mac or enumerate secret names into a receipt",
            second_move_risk="Secrets metadata leaks into a receipt that later syncs to cloud",
            third_move_consequence="Credential exposure — one of the eight legitimate HARD_BLOCK reasons",
            patch_before_execution="Evidence source is repo/config only; secrets referenced by opaque slot-id, never name/value; Mac probing forbidden in this packet",
            commercial_consequence="Indirect: correct 80/20 split keeps Phase 2/3 costs at cloud prices and the Mac free for founder work",
            roi_score=70, reversibility="full (read-only)",
            execution_mode="CLOUD_ONLY", delivery_route="github_action",
            target_executor="claude_code_cli", fallback_route="human_review_queue",
            verification_after_execution=["per-motor verdict table", "0 secret names/values in receipt", "UNKNOWN rows carry explicit evidence gap"],
            founder_rewrite_likelihood="low", phase2_candidate=False,
            lane="Ops", problem_class="architecture", owner_agent="architect",
            model_tier="cheap", value_class="risk_reduction", cost_limit_usd=2.0,
            roi_reason="Prerequisite for the Mac runner phase: prevents building Mac execution for tasks that never needed it, and prevents cloud dispatch of genuinely Mac-bound work.",
            task="Build the Mac-required truth list from repo evidence only: 1) for each registry motor and each recurring task class, determine execution dependency: CLOUD_OK | MAC_REQUIRED(local_repo_state_not_in_cloud|local_secrets_or_env|mac_specific_tooling|human_ide_review) | UNKNOWN; 2) cite evidence per verdict (workflow files, configs, launchd references); 3) reference any secret by opaque slot-id only; 4) emit one receipt with the truth list. Do not probe the live Mac.",
            allowed_actions=["read data/, receipts/, .github/workflows/, docs/", "write one receipt to receipts/p0pgr/"],
            extra_forbidden=["no live Mac probing", "no secret names or values in any output"],
            stop_rule="Stop after truth-list receipt; Mac runner build remains founder-gated Phase 3 work.",
            evidence_refs=["data/github_automation_registry_v1.json", "p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md"],
        ),
        # ---- safety (axis 2/5 support) --------------------------------------
        dict(
            move_id="M09", axis="authority_wiring",
            board_signal="P0 leak detector exists (117 fingerprints) but has only ever scanned P0-PGR packets; legacy dispatch docs (docs/dispatch/*, docs/*DISPATCH*, handoff docs) predate the detector and were never swept.",
            immediate_goal="Sweep every existing worker-facing prompt/dispatch document in the repo for P0 leakage and least-knowledge violations",
            protected_assets=["P0-CORE confidentiality", "least-knowledge boundary", "legacy dispatch docs (report, don't edit)"],
            likely_misread="Sweeper may auto-redact legacy docs — edits to dispatch docs are repairs, not audit output",
            second_move_risk="False positives on doctrine files that are ALLOWED to cite P0 (Base Live Brain surfaces)",
            third_move_consequence="Either P0 leaks persist into agent context windows, or over-redaction breaks working dispatch docs",
            patch_before_execution="Classify surfaces first (worker-facing vs brain-facing); only worker-facing surfaces are leak violations; report-only",
            commercial_consequence="Indirect: P0 contains founder judgment/strategy — leakage into worker prompts is competitive and governance exposure",
            roi_score=72, reversibility="full (read-only)",
            execution_mode="CLOUD_ONLY", delivery_route="github_action",
            target_executor="claude_code_cli", fallback_route="mac_runner",
            verification_after_execution=["per-document leak verdict with fingerprint hit lines", "surface classification table (worker vs brain)"],
            founder_rewrite_likelihood="low", phase2_candidate=True,
            lane="SG", problem_class="verification", owner_agent="verifier",
            model_tier="cheap", value_class="risk_reduction", cost_limit_usd=2.0,
            roi_reason="One-shot mechanical sweep closes the least-knowledge gap for all legacy prompts, not just new packets — extends the Phase-0 guarantee backwards.",
            task="P0 leakage safety sweep: 1) classify every prompt/dispatch surface in docs/dispatch/, docs/*DISPATCH*, docs/*HANDOFF*, and receipts/p0pgr/outbox/ as worker-facing or brain-facing; 2) run the P0 fingerprint sweep (scripts/p0pgr_packet_lint_v1.py p0_fingerprints) against all worker-facing surfaces; 3) report per-document verdict CLEAN|LEAK(lines) — report-only, no redaction edits; 4) emit one receipt.",
            allowed_actions=["read docs/, receipts/p0pgr/outbox/, SG-Canonical-Library P0-CORE (fingerprints only)", "write one receipt to receipts/p0pgr/"],
            extra_forbidden=["no edits to any scanned document"],
            stop_rule="Stop after sweep receipt; redactions are separate founder-visible repair packets.",
            evidence_refs=["docs/dispatch/auth-phase-1-trustfield.md", "scripts/p0pgr_packet_lint_v1.py"],
        ),
        # ---- meta: phase 2 gateway ------------------------------------------
        dict(
            move_id="M10", axis="delivery_readiness",
            board_signal="Phase 2 requires ranked, evidence-backed dispatch candidates; ranking currently lives in founder judgment — exactly the workload P0-PGR exists to absorb.",
            immediate_goal="Deterministically rank campaign packets M01-M09 for Phase 2 first-dispatch by roi x reversibility x cloud-safety x rewrite-likelihood, from their packet files and receipts",
            protected_assets=["founder authority over Phase 2 unlock", "ranking determinism (same inputs, same order)"],
            likely_misread="Ranker may treat its own ranking as dispatch authorization",
            second_move_risk="A self-authorized dispatch would violate shadow mode",
            third_move_consequence="Trust reset: founder re-becomes the runtime, Phase 2 delayed",
            patch_before_execution="Output is a ranked RECOMMENDATION receipt; dispatch_now stays false; Phase 2 unlock is an explicit founder decision recorded as its own receipt",
            commercial_consequence="Indirect: shortest path to Phase 2 autonomy, which is where founder prompt-writing actually drops to ~0",
            roi_score=86, reversibility="full (produces one receipt)",
            execution_mode="CLOUD_ONLY", delivery_route="queue_cloud_worker",
            target_executor="claude_code_cli", fallback_route="github_action",
            verification_after_execution=["ranking formula shown with inputs per packet", "same-input replay yields same order", "no dispatch flag flipped"],
            founder_rewrite_likelihood="low", phase2_candidate=True,
            lane="SG", problem_class="architecture", owner_agent="architect",
            model_tier="cheap", value_class="proof_asset", cost_limit_usd=1.5,
            roi_reason="Absorbs the 'what next' decision into the runtime with a deterministic, replayable formula — the direct precondition for Phase 2.",
            task="Rank Phase 2 dispatch candidates: 1) read all campaign packet files in receipts/p0pgr/outbox/ and the campaign receipt; 2) score each: rank = roi_score x reversibility_factor x cloud_safety_factor x (1 - rewrite_likelihood_factor); 3) show the formula inputs per packet; 4) emit one ranked recommendation receipt; dispatch flags remain false. Phase 2 unlock is founder-only.",
            allowed_actions=["read receipts/p0pgr/", "write one receipt to receipts/p0pgr/"],
            extra_forbidden=["no dispatch flag changes", "no packet edits"],
            stop_rule="Stop after ranking receipt.",
            evidence_refs=["receipts/p0pgr/campaigns/P0PGR-CAMPAIGN-20260708-001.json"],
        ),
    ]


def main() -> int:
    evidence = collect_evidence()
    OUTBOX.mkdir(parents=True, exist_ok=True)
    CAMPAIGNS.mkdir(parents=True, exist_ok=True)

    entries, seq = [], 3  # 002 exists (M01 reuses it)
    counts = {"lint_pass": 0, "repair_candidates": 0, "phase2": 0,
              "commercial": 0, "p0_leaks": 0, "hard_blocks": 0}

    for move in moves():
        chess = chess_pass(move)
        entry = {
            "move_id": move["move_id"],
            "axis": move["axis"],
            "board_signal": move["board_signal"],
            "immediate_goal": move["immediate_goal"],
            "protected_assets": move["protected_assets"],
            "likely_misread": move.get("likely_misread") or chess.get("likely_misread"),
            "second_move_risk": move.get("second_move_risk") or chess.get("second_move_risk"),
            "third_move_consequence": move.get("third_move_consequence") or chess.get("third_move_consequence"),
            "patch_before_execution": move.get("patch_before_execution") or chess.get("patch_before_execution"),
            "chess_action": chess.get("action"),
            "commercial_consequence": move["commercial_consequence"],
            "roi_score": move["roi_score"],
            "reversibility": move["reversibility"],
            "execution_mode": move["execution_mode"],
            "delivery_route": move["delivery_route"],
            "target_executor": move["target_executor"],
            "dispatch_now": False,
            "verification_after_execution": move["verification_after_execution"],
            "receipt_required": True,
            "founder_rewrite_likelihood": move["founder_rewrite_likelihood"],
            "phase2_candidate": move["phase2_candidate"],
        }

        if move.get("reuse_packet"):
            entry["packet_id"] = move["reuse_packet"]
            entry["packet_file"] = f"receipts/p0pgr/outbox/{move['reuse_packet']}.json"
            existing = json.loads((OUTBOX / f"{move['reuse_packet']}.json").read_text())
            lint = lint_packet(existing)
        else:
            packet = compile_packet(move, seq)
            lint = lint_packet(packet)
            pf = OUTBOX / f"{packet['id']}.json"
            pf.write_text(json.dumps(packet, indent=2) + "\n")
            entry["packet_id"] = packet["id"]
            entry["packet_file"] = str(pf.relative_to(ROOT))
            seq += 1

        entry["lint"] = lint["verdict"]
        entry["lint_reasons"] = lint["reasons"]
        entry["quality_state"] = "PASS" if lint["verdict"] == "PASS" else "NEEDS_RETRY"
        entry["route_decision"] = (
            ROUTE_VERDICT.get(move["execution_mode"], "HOLD")
            if lint["verdict"] == "PASS" else "HOLD"
        )
        counts["lint_pass"] += lint["verdict"] == "PASS"
        counts["repair_candidates"] += lint["verdict"] != "PASS"
        counts["p0_leaks"] += any("P0 leakage" in r for r in lint["reasons"])
        counts["phase2"] += entry["phase2_candidate"]
        counts["commercial"] += move["value_class"] == "revenue_path"
        entries.append(entry)

    ranked = sorted(entries, key=lambda e: -e["roi_score"])
    top3 = [{"move_id": e["move_id"], "packet_id": e["packet_id"],
             "roi_score": e["roi_score"], "why": e["commercial_consequence"][:140]}
            for e in ranked[:3]]

    campaign = {
        "schema": "p0pgr-campaign-receipt-v1",
        "campaign_id": CAMPAIGN_ID,
        "created_at": utcnow(),
        "mode": "phase1_shadow_strategic_campaign",
        "chess_method": "Forecast -> Patch -> Proceed -> Verify (not a blocker)",
        "evidence_bundle_hash": evidence["bundle_hash"],
        "board_axes": ["runtime_health", "authority_wiring", "commercial_readiness",
                       "live_truth", "cost_roi_governance", "delivery_readiness"],
        "moves": entries,
        "top_3_next_moves": top3,
        "summary": {
            "candidates": len(entries),
            "lint_pass": counts["lint_pass"],
            "repair_candidates": counts["repair_candidates"],
            "phase2_candidates": counts["phase2"],
            "commercial_candidates": counts["commercial"],
            "p0_leakage_count": counts["p0_leaks"],
            "hard_block_count": counts["hard_blocks"],
            "unauthorized_executions": 0,
            "runtime_freezes": 0,
            "fixed_claims": 0,
            "estimated_cost_usd": 0.0,
        },
        "note": "Shadow-only. dispatch_now=false on all moves. No audited issue is claimed fixed.",
    }
    out = CAMPAIGNS / f"{CAMPAIGN_ID}.json"
    out.write_text(json.dumps(campaign, indent=2) + "\n")

    # Scorecard update
    scorecard = {
        "schema": "p0pgr-phase1-scorecard-v1",
        "updated_at": utcnow(),
        "phase": "phase1_shadow_campaign_mode",
        "total_real_shadow_packets": len(entries),
        "accepted_without_sina_rewrite_pending_founder": len(entries),
        "packets_confirmed_accepted_by_founder": 0,
        "repair_candidates_created": counts["repair_candidates"],
        "p0_leakage_count": counts["p0_leaks"],
        "hard_block_count": counts["hard_blocks"],
        "runtime_freeze_count": 0,
        "unauthorized_execution_count": 0,
        "phase2_candidates": counts["phase2"],
        "commercial_candidates": counts["commercial"],
        "estimated_cost_usd": 0.0,
        "campaign": CAMPAIGN_ID,
        "top_3_next_moves": top3,
        "exit_criteria": {
            "min_real_packets": 10,
            "min_accepted_without_rewrite": 7,
            "max_p0_leakage": 0,
            "progress": f"{len(entries)}/10 packets compiled; founder confirms accepts by diff-read",
        },
    }
    SCORECARD.write_text(json.dumps(scorecard, indent=2) + "\n")

    print(json.dumps({
        "campaign": str(out.relative_to(ROOT)),
        "moves": len(entries),
        "lint_pass": counts["lint_pass"],
        "repair_candidates": counts["repair_candidates"],
        "phase2_candidates": counts["phase2"],
        "commercial_candidates": counts["commercial"],
        "p0_leakage": counts["p0_leaks"],
        "top_3": [t["move_id"] for t in top3],
        "bundle_hash": evidence["bundle_hash"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
