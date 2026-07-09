#!/usr/bin/env python3
"""Evidence-based intake sink promotion — md + zip → SG registry (any folder name)."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "docs/governance_drafts_intake_v1"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def thread_id_for(aid: str, role: str) -> str:
    mapping = {
        "sourcea-brain-registry-learning-gate-v0-1-4": "sourcea_brain_registry_learning_gate",
        "sourcea-brain-registry-learning-gate-impl-prompt-v0-1-4": "sourcea_brain_registry_learning_gate_impl",
        "ssot-conflict-log-runtime-rules-v0-1-2": "ssot_conflict_log_runtime_rules_domain_split",
        "ssot-proposal-artifact-versioning-v0-1-1": "ssot_proposal_artifact_versioning",
        "copilot-automation-cost-profile-v1": "copilot_automation_cost_profile_locked",
        "founder-intent-filter-v1": "founder_intent_filter",
        "smart-production-cost-law-v2": "smart_production_cost_law_v2",
        "noos-control-desk-v2": "noos_control_desk_v2",
        "noetfield-coherent-system-spec-v1": "noetfield_coherent_system_spec",
    }
    return mapping.get(aid, aid.replace("-", "_"))


def build_intake_manifest(intake_root: Path, registry: dict) -> dict[str, Any]:
    from governance_intake_sink_v1 import scan_sink_for_artifacts  # noqa: WPS433

    return scan_sink_for_artifacts(intake_root, registry)


def promote_intake_manifest(manifest: dict, apply: bool) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from governance_registry_ops_v1 import (  # noqa: WPS433
        REGISTRY,
        load_registry,
        load_structure_tree,
        load_thread_registry,
        op_registry_add,
        op_thread_register,
        save_json,
        write_receipt,
    )

    registry = load_registry()
    tree = load_structure_tree()
    thread_reg = load_thread_registry()
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    ordered = sorted(
        manifest.get("artifacts", []),
        key=lambda r: (1 if r.get("role") == "implementation_companion" else 0, r.get("artifact_id", "")),
    )

    promoted: list[dict] = []
    updated: list[dict] = []
    errors: list[str] = []

    for row in ordered:
        aid = row["artifact_id"]
        src = Path(row["source_path"])
        dest_name = row.get("dest_name") or src.name
        rel = f"docs/governance_drafts_intake_v1/{dest_name}"
        dest = ROOT / rel

        intake_source = row.get("intake_zip_path") or row.get("source_path")
        spec: dict[str, Any] = {
            "artifact_id": aid,
            "path": rel,
            "layer": row["layer"],
            "domain": row["domain"],
            "version": row.get("version", "1.0.0"),
            "status": "PROPOSED",
            "authority_rank": 2,
            "owner_repo": "sina-governance-ssot",
            "saved_at": utc_now(),
            "affects_layers": [row["layer"]],
            "depends_on": ["gov-structure-authority-v1"],
            "amends": [],
            "intake_source": intake_source,
            "intake_source_kind": row.get("source_kind"),
            "sink_relative": row.get("sink_relative") or manifest.get("sink_detection", {}).get("probable_sink_relative"),
            "awaiting_founder_ratification": True,
            "library_promote_pending": True,
        }
        if row.get("intake_zip_path"):
            spec["intake_zip_path"] = row["intake_zip_path"]
        if row.get("companion_md"):
            spec["intake_companion_md"] = row["companion_md"]
        if row.get("amends_target"):
            spec["amends"] = [row["amends_target"]]
            spec["depends_on"] = ["gov-structure-authority-v1", row["amends_target"]]
        if aid == "smart-production-cost-law-v2":
            spec["depends_on"] = ["gov-structure-authority-v1", "copilot-automation-cost-profile-v1"]

        if row.get("already_in_registry"):
            if apply:
                for art in registry.get("artifacts", []):
                    if art.get("artifact_id") == aid:
                        art["intake_zip_path"] = row.get("intake_zip_path") or art.get("intake_zip_path")
                        art["intake_source_kind"] = row.get("source_kind")
                        art["intake_source"] = intake_source
                        art["sink_relative"] = spec.get("sink_relative")
                        art["saved_at"] = utc_now()
                        if not dest.is_file():
                            shutil.copy2(src, dest)
                save_json(REGISTRY, {**registry, "saved_at": utc_now()})
            updated.append({**row, "action": "provenance_updated"})
            continue

        if apply:
            if not dest.is_file():
                shutil.copy2(src, dest)
            add_result = op_registry_add(registry, tree, spec, apply=True)
            if not add_result.get("ok"):
                errors.append(f"{aid}: {add_result.get('errors', add_result.get('error'))}")
                continue
            registry = load_registry()
            tid = thread_id_for(aid, row.get("role", "spec"))
            tr = op_thread_register(
                thread_reg,
                tid,
                from_staging=False,
                spec={
                    "artifact_id": aid,
                    "registry_path": rel,
                    "status": "REGISTERED",
                    "intake_source": intake_source,
                    "intake_source_kind": row.get("source_kind"),
                    "library_promote_pending": True,
                },
                apply=True,
            )
            if not tr.get("ok") and "already registered" not in str(tr.get("error", "")):
                errors.append(f"{aid} thread: {tr.get('error')}")
            thread_reg = load_thread_registry()
            promoted.append({**row, "registry_path": rel})

    receipt = None
    if apply and (promoted or updated):
        receipt = str(
            write_receipt(
                "promote-intake-drafts-v1",
                {"promoted": len(promoted), "updated": len(updated), "ok": not errors},
            )
        )

    return {
        "schema": "governance-promote-intake-drafts-v1",
        "manifest": manifest,
        "promoted": promoted,
        "updated": updated,
        "errors": errors,
        "ok": not errors,
        "receipt_path": receipt,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Evidence intake sink: md + zip → SG registry")
    parser.add_argument("--root", required=True, help="Intake root (sink inferred from evidence)")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    from governance_registry_ops_v1 import load_registry  # noqa: WPS433

    intake_root = Path(args.root).expanduser().resolve()
    registry = load_registry()
    manifest = build_intake_manifest(intake_root, registry)
    result = promote_intake_manifest(manifest, apply=args.apply)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
