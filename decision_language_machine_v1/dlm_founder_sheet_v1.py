#!/usr/bin/env python3
"""Generate reduced founder review sheet from classified clusters."""

from __future__ import annotations

from dlm_core_v1 import Cluster, ProcessedItem


def build_founder_sheet(processed: list[ProcessedItem], clusters: list[Cluster]) -> dict:
    advisor = [p for p in processed if p.classification == "ADVISOR_REVIEW"]
    facts = [p for p in processed if p.classification == "FOUNDER_FACT"]
    machine = [p for p in processed if p.classification == "MACHINE_VALIDATABLE"]
    defer = [p for p in processed if p.classification == "DEFER"]

    advisor_clusters = [
        c for c in clusters
        if any(p.classification == "ADVISOR_REVIEW" for p in processed if p.item.id in c.member_ids)
    ]

    sheet_clusters: list[dict] = []
    for c in advisor_clusters:
        members = [p for p in processed if p.item.id in c.member_ids and p.classification == "ADVISOR_REVIEW"]
        if not members:
            continue
        lead = members[0]
        opts = lead.item.options[:4] if lead.item.options else []
        sheet_clusters.append({
            "cluster_id": c.cluster_id,
            "name": c.name,
            "plain_english": c.plain_english_question,
            "controls": c.controls,
            "if_unanswered": c.if_unanswered,
            "member_ids": [m.item.id for m in members],
            "options": opts,
            "note": "Recommended picks are hints only — not authority",
        })

    return {
        "schema": "decision_language_machine_founder_sheet_v1",
        "summary": {
            "total_items": len(processed),
            "advisor_clusters": len(sheet_clusters),
            "advisor_items": len(advisor),
            "founder_fact_items": len(facts),
            "machine_validatable": len(machine),
            "deferred": len(defer),
        },
        "advisor_clusters": sheet_clusters,
        "founder_facts": [
            {"id": p.item.id, "plain_english": p.plain_english, "evidence_hint": p.evidence_hint}
            for p in facts
        ],
        "machine_queue_ids": [p.item.id for p in machine],
        "deferred_ids": [p.item.id for p in defer],
    }


def render_founder_sheet_md(sheet: dict) -> str:
    s = sheet["summary"]
    lines = [
        "# Founder review sheet (reduced)",
        "",
        f"**Total items:** {s['total_items']} · **Advisor clusters:** {s['advisor_clusters']} · "
        f"**Founder facts:** {s['founder_fact_items']} · **Machine-validatable:** {s['machine_validatable']} · "
        f"**Deferred:** {s['deferred']}",
        "",
        "> Recommended picks in source rows are hints only — not authority.",
        "",
    ]
    for i, c in enumerate(sheet["advisor_clusters"], 1):
        lines += [
            f"## {i}. [{c['cluster_id']}] {c['name']}",
            "",
            c["plain_english"],
            "",
            f"**Controls:** {c['controls']}",
            f"**If unanswered:** {c['if_unanswered']}",
            "",
        ]
        if c["options"]:
            lines.append("**Options:**")
            for o in c["options"]:
                lines.append(f"- {o}")
            lines.append("")
        lines += [f"**Member IDs:** {', '.join(c['member_ids'])}", "", "---", ""]

    if sheet["founder_facts"]:
        lines += ["## Founder-only facts", ""]
        for f in sheet["founder_facts"]:
            lines.append(f"- **[{f['id']}]** {f['plain_english']}")
        lines += ["", "---", ""]

    mq = sheet["machine_queue_ids"]
    preview = ", ".join(mq[:20]) + (" …" if len(mq) > 20 else "")
    lines += ["## Machine queue (do not ask founder)", "", preview, ""]
    return "\n".join(lines)

