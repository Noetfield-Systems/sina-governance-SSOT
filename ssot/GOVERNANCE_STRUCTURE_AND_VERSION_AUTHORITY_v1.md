# Governance Structure and Version Authority v1

**Status:** ACTIVE  
**Owner:** SG (`sina-governance-ssot`)  
**Purpose:** Single authority for governance structure, layer ownership, and version conflict rules.

## Owner Law

SG owns the governance structure. SourceA, Noetfield OS, Cloud, Mac, Copilot, and packaged libraries may reference this file, but they do not define governance structure.

No fragmentation. No duplicate constitutions. If another repo or library copy disagrees with this file, this file wins for governance structure and version handling.

## Layer Placement

| Layer | Belongs here when the artifact is about |
|-------|-----------------------------------------|
| P0 | Foundation, SSOT index, strategy, workbench, reconciliation, autorun law |
| P1 | Founder canon, north-star intent, founder touchpoints |
| P2 | SSOT plane, lane ownership, operating law, dispatch authority |
| P3 | Mac runtime reality, Hub, receipts, SCAN to SHIP belt |
| P4 | Cloud kernel target, L1-L8 factory motor architecture |
| P5 | Production line, Forge, pipelines |
| P6 | Knowledge, meaning, essays |
| P7 | Doctrine and governance operations |
| P8 | Machine loops, skills, process registries |
| P9 | Pattern libraries and reusable prompt/plan packs |
| P10 | Product and venture boundaries |
| P99 | Ledger, completeness audit, custody receipts |

## Version Law

Newer versions are amendments unless an authority file explicitly says a prior rule is removed.

- Existing rules stay live.
- Newer rules patch or extend older rules.
- If two live versions conflict, the newer version wins only on the conflicting point.
- If the newer version is silent, the older version still binds.
- Do not call a live base rule `superseded`.
- Do not redefine `superseded`; it means not active for decisions.
- Do not delete or ignore older rules only because a newer version exists.

## Current Kernel / SSOT Read

| Artifact | Status | Layer | Conflict rule |
|----------|--------|-------|---------------|
| `Source-A-SSOT-v1.2.pdf` | ACTIVE_BASE | P2 | Later operating-law amendments win only on direct conflict |
| `Source-A-Cloud-Kernel-v1.3.pdf` | ACTIVE_AMENDMENT_TARGET | P4 | v1.3 wins only where it conflicts with earlier kernel/base rules |

## SG and library authority model

| Plane | Role | Owns |
|-------|------|------|
| **SG** (`sina-governance-ssot`) | Guard · authority registry · intake controller | Live authority status, promotion, conflict resolution, version authority, dispatch allowance |
| **Library** (`noetfield-library`) | Asset / law surface repository | Canonical files stored by layer |

**Library file existence gives zero live authority.** SG registry status determines authority:

| Status | Meaning |
|--------|---------|
| `ACTIVE` | May enter dispatch and govern decisions |
| `PROPOSED` | Staged; not dispatch authority until ratified |
| `READ_SURFACE` | Canonical file on disk; indexed/readable; zero live authority |
| `SUPERSEDED` | Removed from decision authority |
| `QUARANTINED` | Blocked from promotion and dispatch pending review |

The library may store canonical files by layer, but **SG alone** controls promotion, conflict resolution, version authority, and whether a law is allowed into dispatch.

**Forbidden:**
- Bulk-promote library files into registry or agent prompts
- Inject library law into agent prompts

**Dispatch law routing (least-knowledge):** Tier 0 + role law + mission brief + mechanical gates only.  
Authority: `ssot/AGENT_LAYERED_LAW_AND_LEAST_KNOWLEDGE_SSOT_LOCKED_v1.md` · registry `agent-layered-law-least-knowledge-v1`.

---

## Authority Order

1. SG canonical governance files in this repo
2. SG registry status for the artifact (`data/governance_artifact_registry_v1.json`)
3. Current repo state and dispatch
4. Current receipts
5. Referenced product/library copies (READ_SURFACE until SG promotes)
6. Prior chat or memory

Library copies must point back to SG for structure law, version law, and authority status.

**Machine pipeline:** [GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md](GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md) · registry `data/governance_artifact_registry_v1.json`
