#!/usr/bin/env python3
"""P0-PGR Phase 0 scaffold seeder — founder receipt, scorecards, seed packets. Machine timestamps only."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_packet_lint_v1 import utc_now_compact, utc_now_iso  # noqa: E402

RECEIPTS = ROOT / "receipts" / "p0pgr"

ALL_GATES_TRUE = {
    "cloud_only": True,
    "read_only_or_reversible": True,
    "roi_positive": True,
    "no_deploy": True,
    "no_external_send": True,
    "no_legal_financial_commitment": True,
    "no_p0_leakage": True,
    "no_authority_change": True,
    "founder_authorization_receipt": True,
}


def git_head() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10, check=False
        ).stdout.strip()
    except OSError:
        return "unknown"


def write_once(path: Path, payload: dict, force: bool) -> str:
    if path.exists() and not force:
        return f"SKIP (exists): {path.relative_to(ROOT)}"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n")
    return f"WROTE: {path.relative_to(ROOT)}"


def seed(directive: str, force: bool = False) -> list[str]:
    now_iso = utc_now_iso()
    ts = utc_now_compact()
    log: list[str] = []

    founder_receipt = {
        "schema": "p0pgr_founder_authorization_v1",
        "receipt_id": f"founder-authorization-{ts}",
        "recorded_at": now_iso,
        "git_head_at_recording": git_head(),
        "directive_verbatim": directive,
        "channel": "in-session founder selection (AskUserQuestion), recorded to repo per M03 lesson",
        "scope": {
            "unlocks": [
                "Phase 0 scaffold in sina-governance-ssot: contracts, schemas, scripts, scorecards, seed packets, tests",
                "shadow cycles (compile + lint + route, zero execution)",
                "campaign planning and ROI ranking (drafts only)",
            ],
            "does_not_unlock": [
                "packet execution beyond shadow cycles",
                "external send", "deploy/promote", "scheduled automation",
                "phase unlock beyond Phase 0 scaffold", "authority or gate changes",
            ],
        },
        "source_findings": ["F1", "F2"],
        "census_receipt": "p0pgr-checklist-20260708T144545Z",
        "commit_flag": "flag for next founder-visible commit",
    }
    log.append(write_once(RECEIPTS / "founder" / f"founder-authorization-{ts}.json", founder_receipt, force))

    log.append(write_once(
        RECEIPTS / "phase1_scorecard_v1.json",
        {
            "schema": "p0pgr_phase1_scorecard_v1",
            "status": "BACKFILLED_EMPTY",
            "recorded_at": now_iso,
            "note": "Phase 1 never ran under this scaffold; see census receipt p0pgr-checklist-20260708T144545Z",
            "counters": {"executions": 0, "sends": 0, "deploys": 0, "leaks": 0, "freezes": 0},
        },
        force,
    ))

    log.append(write_once(
        RECEIPTS / "phase2_scorecard_v1.json",
        {
            "schema": "p0pgr_phase2_scorecard_v1",
            "era": "PHASE_2_CLOUD_ONLY_ROI_TRACK",
            "recorded_at": now_iso,
            "updated_at": now_iso,
            "seeded_from": "p0pgr-checklist-20260708T144545Z",
            "founder_receipts": [founder_receipt["receipt_id"]],
            "counters": {"executions": 0, "sends": 0, "deploys": 0, "leaks": 0, "freezes": 0, "shadow_cycles": 0, "cost_usd": 0},
            "queue_ref": "receipts/p0pgr/phase2_queue_v1.json",
            "directives": [
                "cloud-only; Mac is cockpit, never runner",
                "no scheduled automation without explicit founder approval",
                "continuity law: never default to STOP",
            ],
            "last_cycle": None,
        },
        force,
    ))

    seed_packets = [
        {
            "schema": "p0_prompt_packet_v1.1",
            "packet_id": "PKT-0001-untracked-receipt-manifest",
            "created_at": now_iso,
            "mission": "Produce a commit manifest of every untracked receipt so the next founder-visible commit carries tamper evidence",
            "problem_statement": "Untracked receipts carry no tamper evidence; the working tree holds many unstaged governance receipts (M03 lesson).",
            "deliverable": {
                "type": "commit_manifest",
                "destination": "receipts/p0pgr/",
                "acceptance": "manifest lists every untracked receipt path with sha256 and embeds git HEAD; zero file mutations",
            },
            "route": "CLOUD_WORKER",
            "gates": dict(ALL_GATES_TRUE),
            "roi": {"revenue": 0, "trust": 5, "workload_relief": 3, "cloud_now": 5, "reversibility": 5,
                     "rationale": "trust: converts invisible receipts into auditable evidence; read-only"},
            "constraints": ["read-only sweep; the commit itself stays FOUNDER_ONLY"],
            "evidence_required": ["git status --porcelain capture", "per-file sha256 list"],
            "confidence": "HIGH",
            "status": "OUTBOX",
            "labels": ["authority_wiring"],
            "source_findings": ["census F1"],
        },
        {
            "schema": "p0_prompt_packet_v1.1",
            "packet_id": "PKT-0002-noetfield-live-truth",
            "created_at": now_iso,
            "mission": "Fetch key noetfield.com pages, hash bodies, and diff against repo static files to establish live truth",
            "problem_statement": "Live site state is asserted from memory rather than evidence; drift between repo and production is undetected.",
            "deliverable": {
                "type": "truth_diff_report",
                "destination": "receipts/p0pgr/artifacts/",
                "acceptance": "per-URL status + body sha256 + match/mismatch verdict; bodies saved as artifacts; zero writes to the site",
            },
            "route": "CLOUD_RESEARCH",
            "gates": dict(ALL_GATES_TRUE),
            "roi": {"revenue": 2, "trust": 5, "workload_relief": 2, "cloud_now": 5, "reversibility": 5,
                     "rationale": "trust: replaces memory-claims about the public site with hashed evidence"},
            "constraints": ["GET requests only", "record full redirect chains"],
            "evidence_required": ["per-URL status + body sha256", "saved bodies under receipts/p0pgr/artifacts/"],
            "confidence": "HIGH",
            "status": "OUTBOX",
            "labels": ["live_truth"],
            "source_findings": ["census F3"],
        },
    ]
    for packet in seed_packets:
        log.append(write_once(RECEIPTS / "outbox" / f"{packet['packet_id']}.json", packet, force))

    for sub in ("artifacts", "repair_candidates", "campaigns"):
        (RECEIPTS / sub).mkdir(parents=True, exist_ok=True)

    return log


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed P0-PGR Phase 0 scaffold")
    parser.add_argument("--directive", required=True, help="verbatim founder directive")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for line in seed(args.directive, args.force):
        print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
