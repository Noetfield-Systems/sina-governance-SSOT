#!/usr/bin/env python3
"""Discover full governance artifacts — Tag md, Downloads root, zip bundles (not research)."""
from __future__ import annotations

import json
import re
import shutil
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAFTS_DIR = ROOT / "docs/governance_drafts_intake_v1"
EXTRACT_DIR = ROOT / "data/governance_intake_extract_v1"

ZIP_PATTERNS = (
    r"noos-control-desk.*\.zip$",
    r"smart-production.*\.zip$",
    r"smart.product.*\.zip$",
)
ROOT_MD_PATTERNS = (
    r"^SMART_PRODUCTION.*\.md$",
    r"^NOETFIELD_COHERENT.*\.md$",
    r"^COPILOT_AUTOMATION.*\.md$",
    r"^CANONICAL_D4_PACKAGE.*\.md$",
)
EXCLUDE_STEMS = (
    "deep-research-report",
    "deep_research",
    "linkedin-profile",
)
BUNDLE_MD_PATHS = (
    "cost-production-law/SMART_PRODUCTION_COST_LAW_v2.md",
    "cost-production-law/COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md",
    "cost-production-law/control-desk/README.md",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_excluded_stem(stem: str) -> bool:
    lowered = stem.lower()
    if "deep-research" in lowered or "deep_research" in lowered:
        return True
    return any(x in lowered for x in EXCLUDE_STEMS)


def classify_full_doc(path: Path, text: str) -> dict[str, Any] | None:
    name = path.name.lower()
    if is_excluded_stem(path.stem):
        return None
    if "research report" in text[:300].lower() and "status:" not in text[:400].lower():
        return None

    if "smart_production_cost_law" in name:
        return {"artifact_id": "smart-production-cost-law-v2", "layer": "P8", "domain": "automation", "version": "2.0.0", "role": "spec"}
    if "noos_control_desk" in name or ("control desk" in text[:500].lower() and "noos" in text[:500].lower()):
        return {"artifact_id": "noos-control-desk-v2", "layer": "P3", "domain": "integrator", "version": "2.0.0", "role": "spec"}
    if "noetfield_coherent_system" in name:
        return {"artifact_id": "noetfield-coherent-system-spec-v1", "layer": "P10", "domain": "product_boundary", "version": "1.0.0", "role": "spec"}
    if "copilot_automation_cost" in name:
        return {"artifact_id": "copilot-automation-cost-profile-v1", "layer": "P8", "domain": "automation", "version": "1.0.0", "role": "spec"}
    return None


def registry_has(registry: dict, artifact_id: str) -> bool:
    return any(a.get("artifact_id") == artifact_id for a in registry.get("artifacts", []))


def discover_zip_artifacts(intake_root: Path) -> list[dict]:
    rows: list[dict] = []
    for zpath in intake_root.rglob("*.zip"):
        if not any(re.search(p, zpath.name, flags=re.I) for p in ZIP_PATTERNS):
            continue
        extract_to = EXTRACT_DIR / zpath.stem
        extract_to.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(zpath) as zf:
                zf.extractall(extract_to)
        except zipfile.BadZipFile:
            continue
        for rel in BUNDLE_MD_PATHS:
            candidate = extract_to / rel
            if not candidate.is_file():
                continue
            text = candidate.read_text(encoding="utf-8", errors="ignore")
            meta = classify_full_doc(candidate, text)
            if not meta:
                continue
            dest_name = {
                "smart-production-cost-law-v2": "SMART_PRODUCTION_COST_LAW_v2.md",
                "noos-control-desk-v2": "NOOS_CONTROL_DESK_v2_README.md",
                "copilot-automation-cost-profile-v1": "COPILOT_AUTOMATION_COST_PROFILE_LOCKED_v1.md",
            }.get(meta["artifact_id"], candidate.name)
            rows.append(
                {
                    "artifact_id": meta["artifact_id"],
                    "source_path": str(candidate),
                    "zip_source": str(zpath),
                    "dest_name": dest_name,
                    "intake_kind": "zip_bundle",
                    **meta,
                }
            )
    return rows


def discover_root_md_artifacts(intake_root: Path) -> list[dict]:
    from governance_thread_intelligence_v1 import should_exclude_path  # noqa: WPS433

    rows: list[dict] = []
    for path in sorted(intake_root.glob("*.md")):
        if should_exclude_path(path) or is_excluded_stem(path.stem):
            continue
        if not any(re.match(p, path.name, flags=re.I) for p in ROOT_MD_PATTERNS):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        meta = classify_full_doc(path, text)
        if not meta:
            continue
        rows.append(
            {
                "artifact_id": meta["artifact_id"],
                "source_path": str(path),
                "dest_name": path.name,
                "intake_kind": "downloads_root",
                **meta,
            }
        )
    return rows


def build_intake_manifest(intake_root: Path, registry: dict) -> list[dict]:
    seen: set[str] = set()
    manifest: list[dict] = []
    for row in discover_zip_artifacts(intake_root) + discover_root_md_artifacts(intake_root):
        aid = row["artifact_id"]
        if aid in seen:
            continue
        seen.add(aid)
        row["already_in_registry"] = registry_has(registry, aid)
        row["awaiting_registry_entry"] = not row["already_in_registry"]
        manifest.append(row)
    return manifest


def promote_intake_artifacts(manifest: list[dict], apply: bool) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from governance_registry_ops_v1 import (
        load_registry,
        load_structure_tree,
        load_thread_registry,
        op_registry_add,
        op_registry_retire,
        op_thread_register,
        write_receipt,
    )

    registry = load_registry()
    tree = load_structure_tree()
    thread_reg = load_thread_registry()
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)

    promoted: list[dict] = []
    skipped: list[dict] = []
    errors: list[str] = []

    if apply:
        if registry_has(registry, "deep-research-founder-intent-v1"):
            retire = op_registry_retire(
                registry,
                "deep-research-founder-intent-v1",
                "research report only — not a governance artifact",
                apply=True,
            )
            if retire.get("ok"):
                registry = load_registry()
                promoted.append({"artifact_id": "deep-research-founder-intent-v1", "action": "retired_superseded"})
            thread_reg = load_thread_registry()
            new_threads = [t for t in thread_reg.get("threads", []) if t.get("artifact_id") != "deep-research-founder-intent-v1"]
            if len(new_threads) != len(thread_reg.get("threads", [])):
                thread_reg["threads"] = new_threads
                from governance_registry_ops_v1 import save_thread_registry  # noqa: WPS433

                save_thread_registry(thread_reg, "thread-remove-deep-research")

    for row in manifest:
        aid = row["artifact_id"]
        if row.get("already_in_registry") and aid != "copilot-automation-cost-profile-v1":
            skipped.append({**row, "reason": "already_in_registry"})
            continue

        src = Path(row["source_path"])
        dest = DRAFTS_DIR / row["dest_name"]
        rel = f"docs/governance_drafts_intake_v1/{row['dest_name']}"

        if apply:
            shutil.copy2(src, dest)

        if aid == "copilot-automation-cost-profile-v1" and row.get("already_in_registry"):
            for art in registry.get("artifacts", []):
                if art.get("artifact_id") == aid and apply:
                    art["intake_bundle_source"] = row.get("zip_source") or row.get("source_path")
                    art["saved_at"] = utc_now()
                    from governance_registry_ops_v1 import save_json, REGISTRY  # noqa: WPS433

                    save_json(REGISTRY, {**registry, "saved_at": utc_now()})
            skipped.append({**row, "reason": "updated_intake_bundle_source"})
            continue

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
            "intake_source": row.get("source_path"),
            "intake_kind": row.get("intake_kind"),
            "intake_bundle_source": row.get("zip_source"),
            "awaiting_founder_ratification": True,
            "library_promote_pending": True,
        }
        if aid == "smart-production-cost-law-v2":
            spec["depends_on"] = ["gov-structure-authority-v1", "copilot-automation-cost-profile-v1"]

        if apply:
            add_result = op_registry_add(registry, tree, spec, apply=True)
            if not add_result.get("ok"):
                errors.append(f"{aid}: {add_result.get('errors', add_result.get('error'))}")
                continue
            registry = load_registry()
            thread_id = aid.replace("-", "_")
            tr = op_thread_register(
                thread_reg,
                thread_id,
                from_staging=False,
                spec={
                    "artifact_id": aid,
                    "registry_path": rel,
                    "status": "REGISTERED",
                    "source_path": row.get("source_path"),
                    "intake_kind": row.get("intake_kind"),
                    "library_promote_pending": True,
                },
                apply=True,
            )
            if not tr.get("ok") and "already registered" in str(tr.get("error", "")):
                pass
            else:
                thread_reg = load_thread_registry()
            promoted.append({**row, "registry_path": rel})

    receipt = None
    if apply and (promoted or errors):
        receipt = str(write_receipt("promote-intake-artifacts", {"promoted": len(promoted), "ok": not errors}))

    return {
        "schema": "governance-promote-intake-artifacts-v1",
        "manifest": manifest,
        "promoted": promoted,
        "skipped": skipped,
        "errors": errors,
        "ok": not errors,
        "receipt_path": receipt,
    }


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Promote full intake artifacts (md + zip bundles)")
    parser.add_argument("--root", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    intake_root = Path(args.root).expanduser().resolve()
    registry = json.loads((ROOT / "data/governance_artifact_registry_v1.json").read_text())
    manifest = build_intake_manifest(intake_root, registry)
    result = promote_intake_artifacts(manifest, apply=args.apply)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
