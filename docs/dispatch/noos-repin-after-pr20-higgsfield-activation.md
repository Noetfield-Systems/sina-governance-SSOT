# NOOS instruction — re-pin after SG PR #20

**canonical_main_sha:** `d2c2e6ab9de8d91179aed694abac649866950b33`  
**decision_artifact_sha:** `0a4094321eb24497422f9239b935e7f395257e3c`  
**merge_strategy:** merge_commit  
**PR:** https://github.com/Noetfield-Systems/sina-governance-SSOT/pull/20

1. Re-read SG `main` at `d2c2e6ab9de8d91179aed694abac649866950b33`.
2. Re-pin custody + five read surfaces; do not reuse a pre-#20 pin.
3. Install `data/sg-authority-ref-higgsfield-activation-v1.json` from SG main.
4. Route **Circuit A** first (`docs/dispatch/nf-circuit-a-deterministic-motor-proof-001.md`).
5. Do not activate all lanes; WIP limit = 2 (A then B).
6. Circuit B only after adapter scaffold + founder campaign policy packet.
