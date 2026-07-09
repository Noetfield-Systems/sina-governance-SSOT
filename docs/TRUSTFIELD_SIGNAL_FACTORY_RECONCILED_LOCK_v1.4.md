# Reconciled Lock v1 — Addendum v1.4 (Signal Factory Iteration 2)

**Date:** 2026-07-03  
**Authority:** Architect handoff · SG records

## New lock

| Item | Path |
|------|------|
| Signal Factory Iteration 2 contract | `docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md` |
| SG guardrails mirror | `ssot/sg-guardrails-signal-factory-v1.md` |
| Lock receipt | `receipts/signal-factory-iteration2-lock-20260703T100500Z.json` |

## What changed from v1 core

| Topic | v1 (2026-07-02) | Iteration 2 (locked) |
|-------|-----------------|----------------------|
| Classification enum | `commercial_inquiry`, `partner_equity`, … | `vendor \| partner \| client \| investor \| risk \| bug \| idea \| spam \| unclear` |
| Decision enum | `route`, `build_automation`, … (no `reply`) | adds `ignore`, `archive`, `reply` |
| Optional sections | decision-gated | same — **no score threshold**; Eval 5 defect fixed |
| Test count | 6 (different set) | 6 with `investor` coverage |
| PartnerMesh | hook slot | explicit input class + no-employment law |
| Org cockpit | worktree chaos | Noetfield-Systems workspace + clean main clones |

## Agent routing (unchanged lane law)

- **SourceA Worker** builds `SKILL.md` + verifier  
- **SourceA Brain** registers pointer + doctrine  
- **SG** guardrails only  
- **NOOS** hold  

## Proof

```bash
cat ~/Projects/sina-governance-ssot/docs/SIGNAL_FACTORY_ITERATION2_LOCK_v1.md | head -5
```

Must show: `**Status:** LOCKED`
