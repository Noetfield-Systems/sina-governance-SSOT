#!/usr/bin/env python3
"""Classify items: MACHINE_VALIDATABLE, ADVISOR_REVIEW, FOUNDER_FACT, DEFER."""

from __future__ import annotations

import re

from dlm_core_v1 import ProcessedItem

FOUNDER_FACT_PATTERNS = [
    r"did you send",
    r"confirm.*mail",
    r"mail sent",
    r"linkedin.*updated",
    r"personally sent",
    r"from your account",
    r"confirm_sent",
    r"you send mail",
    r"have you sent",
]

MACHINE_EVIDENCE_PATTERNS = [
    (r"script.*pass|\.sh\b|validate-", "Run named validator script; close if PASS"),
    (r"already shipped|shipped scripts/", "Check file exists on disk"),
    (r"void|never follow|copy.safety|anti-theater", "Check doctrine file; apply NEVER rule"),
    (r"13/13|pulse receipt|phase0", "Read pulse receipt JSON timestamp"),
    (r"health|probe|:13027|pages\.dev", "HTTP probe live status"),
    (r"fact(or)?y_mesh|36 node", "Count nodes in FACTORY_MESH.json"),
    (r"false.done|bay mapped|receipt proof", "Verify guard script wired"),
    (r"never_sync|cloud.*not.*law", "Check sync law JSON flag"),
    (r"hub.*retire|:13020", "Compare E2E registry faded probe"),
]

DEFER_PATTERNS = [
    r"gemini",
    r"scaffold",
    r"workspace",
    r"apple-store-api",
    r"10-step program",
    r"phase0 spot",
    r"yarn|monorepo",
    r"video-ad-factory.*typescript",
    r"broker round-trip",
    r"worker.inbox file",
    r"paradox.*form.only",
]

ADVISOR_PATTERNS = [
    r"which is p0|north star|priority",
    r"parallel|before.*film|outreach",
    r"auto.*dispatch|founder tap",
    r"publish.*npm|wait until",
    r"pass bar|deposit|loi",
    r"appointment|public demo|tunnel",
    r"language.*default|persian|english",
    r"batch 3|dns",
    r"primary offer|sku name",
    r"who executes|execution plane",
]


def classify_item(item: ProcessedItem) -> ProcessedItem:
    blob = (item.plain_english + " " + item.item.raw_text + " " + item.item.blocks).lower()

    if item.cluster_id in {"CLUSTER-DEFER-SCAFFOLD", "CLUSTER-DICT-FIX"}:
        item.classification = "DEFER" if item.cluster_id == "CLUSTER-DEFER-SCAFFOLD" else "MACHINE_VALIDATABLE"
        item.classification_reason = f"Cluster bucket: {item.cluster_name}"
        item.evidence_hint = "Dictionary batch add" if item.dictionary_fix_needed else "Low priority scaffold"
        return item

    for pat in FOUNDER_FACT_PATTERNS:
        if re.search(pat, blob, re.I):
            item.classification = "FOUNDER_FACT"
            item.classification_reason = "Requires founder-only fact"
            item.evidence_hint = "Founder confirms yes/no; agents never infer"
            return item

    for pat in DEFER_PATTERNS:
        if re.search(pat, blob, re.I):
            item.classification = "DEFER"
            item.classification_reason = "Scaffold or low-urgency fork"
            item.evidence_hint = "Revisit when lane opens; do not block revenue P0"
            return item

    for pat, hint in MACHINE_EVIDENCE_PATTERNS:
        if re.search(pat, blob, re.I):
            item.classification = "MACHINE_VALIDATABLE"
            item.classification_reason = "Evidence on disk or live probe can decide"
            item.evidence_hint = hint
            return item

    if item.dictionary_fix_needed and not re.search("|".join(ADVISOR_PATTERNS), blob, re.I):
        item.classification = "MACHINE_VALIDATABLE"
        item.classification_reason = "Close after dictionary entry added (mint gate)"
        item.evidence_hint = "Add term to dictionary batch; rebuild index"
        return item

    for pat in ADVISOR_PATTERNS:
        if re.search(pat, blob, re.I):
            item.classification = "ADVISOR_REVIEW"
            item.classification_reason = "Strategic tradeoff; needs human judgment"
            item.evidence_hint = "Reduced founder sheet only"
            return item

    if item.item.options:
        item.classification = "ADVISOR_REVIEW"
        item.classification_reason = "Multi-option fork without machine evidence path"
        item.evidence_hint = "Present on founder sheet"
        return item

    item.classification = "DEFER"
    item.classification_reason = "No advisor signal; default defer"
    item.evidence_hint = "Promote if blocks GUARD/REVENUE consumer"
    return item

