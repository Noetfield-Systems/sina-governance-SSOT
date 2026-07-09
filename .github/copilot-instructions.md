# Copilot instructions for `sina-governance-SSOT`

- Keep changes repo-local and aligned to governance SSOT + verifier support flows.
- Governance structure and version conflict rules are owned by `ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md`.
- Governance change impact/classification runs through `ssot/GOVERNANCE_INTELLIGENCE_PIPELINE_v1.md` and `scripts/governance_intelligence_engine_v1.py`.
- Existing rules stay live; newer versions are amendments and win only on direct conflict. Do not call a live base rule `superseded`.
- Treat `receipts/` and historical verifier notes as immutable evidence unless a task explicitly requests historical edits.
- For active config/code, use repo identity `Noetfield-Systems/sina-governance-SSOT`.
- **Forbidden active-config marker:** `kazemnezhadsina144-dot` must not appear in active config or executable code paths.
