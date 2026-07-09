#!/usr/bin/env python3
"""P0-PGR strategic campaign planner — six board axes, CHESS pass (improver, not blocker)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from p0pgr_packet_lint_v1 import lint_packet, utc_now_compact, utc_now_iso  # noqa: E402

DEFAULT_RECEIPTS = ROOT / "receipts" / "p0pgr"

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

# Six board axes — deterministic candidate per axis, all cloud-safe and read-only.
AXES = [
    {
        "axis": "runtime_health",
        "packet_id": "PKT-0101-runtime-health-revalidate",
        "mission": "Independently re-validate the newest loop-state receipt against P0_PROMPT_LOOP_STATE_SCHEMA_v1",
        "problem": "Scripts' own success claims are untrusted; receipts need independent schema re-validation.",
        "deliverable": ("validation_report", "receipts/p0pgr/", "report lists every required field checked with PASS/FAIL per field"),
        "route": "CLOUD_WORKER",
        "roi": {"revenue": 0, "trust": 4, "workload_relief": 3, "cloud_now": 5, "reversibility": 5},
        "evidence": ["script_run output", "schema field checklist"],
        "chess": {
            "forecast": "validator could drift from schema file",
            "patch": "validator reads schema JSON at runtime instead of hardcoding fields",
            "verify": "re-run against a known-bad receipt fixture and confirm FAIL",
        },
    },
    {
        "axis": "authority_wiring",
        "packet_id": "PKT-0102-untracked-receipt-manifest",
        "mission": "Sweep receipts/ for untracked files and produce a commit manifest for the next founder-visible commit",
        "problem": "Untracked receipts carry no tamper evidence (M03 lesson).",
        "deliverable": ("commit_manifest", "receipts/p0pgr/", "manifest lists every untracked receipt path with sha256; zero mutations"),
        "route": "CLOUD_WORKER",
        "roi": {"revenue": 0, "trust": 5, "workload_relief": 2, "cloud_now": 5, "reversibility": 5},
        "evidence": ["git status --porcelain capture", "per-file sha256"],
        "chess": {
            "forecast": "manifest could go stale before founder commits",
            "patch": "manifest embeds git HEAD hash so staleness is detectable",
            "verify": "recompute two random sha256 values from the manifest",
        },
    },
    {
        "axis": "commercial_readiness",
        "packet_id": "PKT-0103-trustfield-offer-truth",
        "mission": "Fetch TrustField public offer surface and hash-compare against repo copies",
        "problem": "Commercial pages may drift from governed repo copies without detection.",
        "deliverable": ("truth_diff_report", "receipts/p0pgr/artifacts/", "per-URL status + sha256 + match/mismatch verdict for every checked page"),
        "route": "CLOUD_RESEARCH",
        "roi": {"revenue": 3, "trust": 4, "workload_relief": 2, "cloud_now": 4, "reversibility": 5},
        "evidence": ["per-URL status + body sha256", "saved bodies under artifacts/"],
        "chess": {
            "forecast": "page templating may cause noisy hash mismatches",
            "patch": "normalize whitespace before hashing and record both raw and normalized hashes",
            "verify": "one manually confirmed match and one confirmed mismatch fixture",
        },
    },
    {
        "axis": "live_truth",
        "packet_id": "PKT-0104-noetfield-live-truth",
        "mission": "Fetch key noetfield.com pages, hash bodies, and diff against repo static files",
        "problem": "Live site truth is asserted from memory, not evidence.",
        "deliverable": ("truth_diff_report", "receipts/p0pgr/artifacts/", "per-URL status + sha256 + diff verdict; bodies saved as artifacts"),
        "route": "CLOUD_RESEARCH",
        "roi": {"revenue": 2, "trust": 5, "workload_relief": 2, "cloud_now": 5, "reversibility": 5},
        "evidence": ["per-URL status + body sha256", "saved bodies under artifacts/"],
        "chess": {
            "forecast": "redirects (www canonical) could mask real page state",
            "patch": "record full redirect chain per URL",
            "verify": "status codes cross-checked against _redirects rules",
        },
    },
    {
        "axis": "cost_roi",
        "packet_id": "PKT-0105-roi-heartbeat-trend",
        "mission": "Aggregate receipts/roi-heartbeat-*.json into a cost/ROI trend summary",
        "problem": "Spend signals exist as scattered heartbeat receipts with no trend view.",
        "deliverable": ("trend_summary", "receipts/p0pgr/", "summary covers every heartbeat receipt present, with count, span, and per-metric trend"),
        "route": "CLOUD_WORKER",
        "roi": {"revenue": 1, "trust": 3, "workload_relief": 4, "cloud_now": 5, "reversibility": 5},
        "evidence": ["input receipt list with hashes", "aggregation script output"],
        "chess": {
            "forecast": "heartbeat schema may vary across versions",
            "patch": "summary records per-file schema version and skips-with-reason instead of crashing",
            "verify": "row count equals input file count",
        },
    },
    {
        "axis": "delivery_readiness",
        "packet_id": "PKT-0106-governance-queue-census",
        "mission": "Parse governance intake queues and emit a counts census (review + promote queues)",
        "problem": "Queue depth is unknown between sessions; delivery readiness is unmeasured.",
        "deliverable": ("queue_census", "receipts/p0pgr/", "census reports item counts and oldest item age for each queue file"),
        "route": "CLOUD_WORKER",
        "roi": {"revenue": 1, "trust": 3, "workload_relief": 4, "cloud_now": 5, "reversibility": 5},
        "evidence": ["queue file hashes", "parsed counts"],
        "chess": {
            "forecast": "queue files may be mid-write during a cycle",
            "patch": "census records file mtime and sha256 at read moment",
            "verify": "re-read after census; identical hash confirms stable read",
        },
    },
]


def build_candidates() -> list[dict]:
    now = utc_now_iso()
    candidates = []
    for axis in AXES:
        dtype, dest, acceptance = axis["deliverable"]
        packet = {
            "schema": "p0_prompt_packet_v1.1",
            "packet_id": axis["packet_id"],
            "created_at": now,
            "mission": axis["mission"],
            "problem_statement": axis["problem"],
            "deliverable": {"type": dtype, "destination": dest, "acceptance": acceptance},
            "route": axis["route"],
            "gates": dict(ALL_GATES_TRUE),
            "roi": {**axis["roi"], "rationale": f"board axis: {axis['axis']}"},
            "constraints": ["zero execution in this campaign — candidates only", "integration law: consume adjacent systems, never duplicate queues"],
            "evidence_required": axis["evidence"],
            "confidence": "MEDIUM",
            "status": "DRAFT",
            "labels": [axis["axis"]],
            "source_findings": ["census F1", "census F3"],
        }
        chess = {**axis["chess"], "proceed": True}
        candidates.append({"axis": axis["axis"], "packet": packet, "chess_pass": chess, "lint_rejects": lint_packet(packet)})
    return candidates


def run_campaign(receipts_dir: Path = DEFAULT_RECEIPTS) -> dict:
    campaigns_dir = receipts_dir / "campaigns"
    campaigns_dir.mkdir(parents=True, exist_ok=True)
    campaign_id = f"campaign-{utc_now_compact()}"
    candidates = build_candidates()
    receipt = {
        "schema": "p0pgr_campaign_receipt_v1",
        "campaign_id": campaign_id,
        "recorded_at": utc_now_iso(),
        "axes": [c["axis"] for c in candidates],
        "candidates": candidates,
        "clean_candidates": sum(1 for c in candidates if not c["lint_rejects"]),
        "counters": {"executions": 0, "sends": 0, "deploys": 0, "leaks": 0, "freezes": 0},
        "accounting_note": "deterministic planner, zero LLM calls; candidates are drafts, not executions",
        "executor_route_note": "no execution — planning only",
        "commit_flag": "flag for next founder-visible commit",
    }
    path = campaigns_dir / f"{campaign_id}.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    receipt["_receipt_path"] = str(path)
    return receipt


def main() -> int:
    receipt = run_campaign()
    print(json.dumps({k: v for k, v in receipt.items() if k != "candidates"}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
