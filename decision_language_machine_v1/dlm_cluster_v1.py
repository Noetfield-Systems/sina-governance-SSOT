#!/usr/bin/env python3
"""Cluster duplicate or overlapping decisions."""

from __future__ import annotations

import re
from collections import defaultdict

from dlm_core_v1 import Cluster, ProcessedItem

# Theme keywords → cluster bucket
THEME_RULES: list[tuple[str, str, list[str]]] = [
    ("CLUSTER-REVENUE", "Revenue and daily priority", ["outbound", "revenue", "w3", "inbox", "north star", "p0", "commercial"]),
    ("CLUSTER-DEMO-FILM", "Demo film and outreach timing", ["film", "demo", "outreach", "linkedin", "tamper", "dry run"]),
    ("CLUSTER-CLOUD-EXEC", "Where code runs (cloud vs Mac)", ["cloud", "mac", "execution", "worker url", "headless", "railway", "cloudflare"]),
    ("CLUSTER-CLAIMS", "Public claims safety", ["investor", "headline", "100m", "never", "overclaim", "bypass", "score"]),
    ("CLUSTER-NPM-MARKET", "Marketplace and npm", ["npm", "marketplace", "card1", "publish", "cursor"]),
    ("CLUSTER-WITNESSBC", "WitnessBC and proof lab", ["witness", "proof lab", "tunnel", "style-b1", "hero film"]),
    ("CLUSTER-FORM-META", "Form process and gather", ["form", "gather", "unify", "canvas", "chat fork"]),
    ("CLUSTER-VOCAB", "Vocabulary and identity", ["creed", "kernel", "factory mesh", "36 node", "terminology", "dictionary"]),
    ("CLUSTER-LOOP-AUTO", "Loop auto and false-done", ["loop auto", "false done", "dispatch", "hub tap", "bay mapped"]),
    ("CLUSTER-DNS-DRAIN", "Domain and cloud drain", ["dns", "sourcea.app", "batch 3", "cloud-sec", "drain"]),
    ("CLUSTER-LANGUAGE", "Reply language and voice", ["language", "persian", "farsi", "voice", "plus one", "locale"]),
    ("CLUSTER-DEFER-SCAFFOLD", "Scaffold and defer", ["gemini", "scaffold", "workspace", "apple-store", "10-step", "phase0 spot"]),
]

def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{4,}", text.lower()))


def assign_cluster(item: ProcessedItem) -> tuple[str, str]:
    blob = (item.plain_english + " " + item.item.blocks + " " + item.item.effect).lower()
    best_id, best_name, best_score = "CLUSTER-OTHER", "Other decisions", 0
    for cid, cname, keywords in THEME_RULES:
        score = sum(1 for k in keywords if k in blob)
        if score > best_score:
            best_id, best_name, best_score = cid, cname, score
    if best_score == 0:
        # token overlap with cluster members handled in build_clusters
        toks = _tokens(blob)
        if "mail" in blob and ("sent" in blob or "confirm" in blob):
            return "CLUSTER-FOUNDER-FACT", "Founder-only facts"
        if item.dictionary_fix_needed and len(toks) < 3:
            return "CLUSTER-DICT-FIX", "Dictionary fixes needed"
    return best_id, best_name


def build_clusters(processed: list[ProcessedItem]) -> list[Cluster]:
    buckets: dict[str, list[ProcessedItem]] = defaultdict(list)
    names: dict[str, str] = {}
    for p in processed:
        cid, cname = assign_cluster(p)
        p.cluster_id = cid
        p.cluster_name = cname
        buckets[cid].append(p)
        names[cid] = cname

    clusters: list[Cluster] = []
    for cid, members in buckets.items():
        lead = members[0]
        controls = "; ".join(sorted({m.item.effect[:80] for m in members if m.item.effect})[:3])
        clusters.append(
            Cluster(
                cluster_id=cid,
                name=names[cid],
                member_ids=[m.item.id for m in members],
                plain_english_question=_merge_questions(members),
                controls=controls or "See member rows",
                if_unanswered="Decision stays open; agents may guess priority",
                hint="",
            )
        )
    return sorted(clusters, key=lambda c: -len(c.member_ids))


def _merge_questions(members: list[ProcessedItem]) -> str:
    if len(members) == 1:
        return members[0].plain_english
    lead = members[0].plain_english[:200]
    return f"{lead} (+ {len(members)-1} related items)"

