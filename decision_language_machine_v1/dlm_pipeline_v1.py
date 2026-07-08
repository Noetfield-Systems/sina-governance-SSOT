#!/usr/bin/env python3
"""Full decision language machine pipeline with stage receipts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from dlm_apply_map_v1 import build_apply_map, load_validated_picks
from dlm_classify_v1 import classify_item
from dlm_cluster_v1 import build_clusters
from dlm_core_v1 import OUTPUT_DIR, ProcessedItem, new_run_id, write_run_manifest, write_stage_receipt
from dlm_founder_sheet_v1 import build_founder_sheet, render_founder_sheet_md
from dlm_intake_v1 import load_items
from dlm_plain_english_v1 import rewrite_item
from dlm_terms_v1 import check_terms, extract_terms


def run_pipeline(
    input_path: Path,
    *,
    validated_picks_path: Path | None = None,
    partial_batch: bool = True,
    skip_apply_map: bool = False,
) -> dict[str, Any]:
    run_id = new_run_id()
    stage_paths: list[str] = []

    items = load_items(input_path)
    p1, _ = write_stage_receipt(
        run_id=run_id, stage="intake", decision="PASS",
        payload={"item_count": len(items), "sample_ids": [i.id for i in items[:5]]},
        input_path=str(input_path),
    )
    stage_paths.append(str(p1))

    processed = [ProcessedItem(item=i) for i in items]

    for p in processed:
        p.plain_english = rewrite_item(p.item)
    p2, _ = write_stage_receipt(
        run_id=run_id, stage="plain_english", decision="PASS",
        payload={"rewritten": len(processed)}, input_path=str(input_path),
    )
    stage_paths.append(str(p2))

    for p in processed:
        p.terms = extract_terms(p.plain_english + " " + p.item.raw_text)
    p3, _ = write_stage_receipt(
        run_id=run_id, stage="term_extract", decision="PASS",
        payload={"total_terms": sum(len(p.terms) for p in processed)}, input_path=str(input_path),
    )
    stage_paths.append(str(p3))

    dict_fix_count = 0
    for p in processed:
        p.dictionary_flags, p.dictionary_fix_needed = check_terms(p.terms)
        if p.dictionary_fix_needed:
            dict_fix_count += 1
    p4, _ = write_stage_receipt(
        run_id=run_id, stage="dictionary_check", decision="PASS",
        payload={
            "items_with_dictionary_fix_needed": dict_fix_count,
            "flagged_terms": sorted({
                f["term"] for p in processed for f in p.dictionary_flags
                if f.get("status") == "DICTIONARY_FIX_NEEDED"
            })[:30],
        },
        input_path=str(input_path),
    )
    stage_paths.append(str(p4))

    clusters = build_clusters(processed)
    p5, _ = write_stage_receipt(
        run_id=run_id, stage="cluster", decision="PASS",
        payload={
            "cluster_count": len(clusters),
            "clusters": [{"id": c.cluster_id, "members": len(c.member_ids)} for c in clusters],
        },
        input_path=str(input_path),
    )
    stage_paths.append(str(p5))

    for p in processed:
        classify_item(p)
    counts = Counter(p.classification for p in processed)
    p6, _ = write_stage_receipt(
        run_id=run_id, stage="classify", decision="PASS",
        payload=dict(counts), input_path=str(input_path),
    )
    stage_paths.append(str(p6))

    sheet = build_founder_sheet(processed, clusters)
    sheet_path = OUTPUT_DIR / f"{run_id}.founder_sheet.json"
    sheet_md_path = OUTPUT_DIR / f"{run_id}.founder_sheet.md"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sheet_path.write_text(json.dumps(sheet, indent=2) + "\n", encoding="utf-8")
    sheet_md_path.write_text(render_founder_sheet_md(sheet) + "\n", encoding="utf-8")
    p7, _ = write_stage_receipt(
        run_id=run_id, stage="founder_sheet", decision="PASS",
        payload={"path": str(sheet_path), "summary": sheet["summary"]}, input_path=str(input_path),
    )
    stage_paths.append(str(p7))

    apply_map: dict[str, Any] = {"status": "SKIPPED"}
    if not skip_apply_map:
        validated = load_validated_picks(validated_picks_path)
        apply_map = build_apply_map(processed, validated, partial_batch=partial_batch)
        apply_path = OUTPUT_DIR / f"{run_id}.apply_map.json"
        apply_path.write_text(json.dumps(apply_map, indent=2) + "\n", encoding="utf-8")
        decision = "PASS" if apply_map.get("status") in {"READY", "EMPTY"} else "BLOCKED"
        p8, _ = write_stage_receipt(
            run_id=run_id, stage="apply_map", decision=decision,
            payload={"path": str(apply_path), "status": apply_map.get("status")},
            input_path=str(validated_picks_path) if validated_picks_path else None,
        )
        stage_paths.append(str(p8))

    processed_path = OUTPUT_DIR / f"{run_id}.processed.json"
    processed_path.write_text(json.dumps([p.as_dict() for p in processed], indent=2) + "\n", encoding="utf-8")

    summary = {
        "run_id": run_id,
        "input_path": str(input_path),
        "item_count": len(processed),
        "classification": dict(counts),
        "dictionary_fix_needed_count": dict_fix_count,
        "cluster_count": len(clusters),
        "founder_sheet": str(sheet_path),
        "founder_sheet_md": str(sheet_md_path),
        "processed": str(processed_path),
        "apply_map_status": apply_map.get("status"),
    }
    manifest_path = write_run_manifest(
        run_id=run_id, input_path=str(input_path), stage_receipts=stage_paths, summary=summary,
    )
    summary["manifest"] = str(manifest_path)
    return summary

