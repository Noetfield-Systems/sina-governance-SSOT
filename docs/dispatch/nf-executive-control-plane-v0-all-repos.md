# Dispatch — NF-EXECUTIVE-CONTROL-PLANE-V0

**decision_id:** `NF-EXECUTIVE-CONTROL-PLANE-V0`  
**Machine:** `data/nf_executive_control_plane_v0_LOCKED.json`

## One line

Deterministic Executive Office kernel: Governor decides; Compiler emits WorkPacket; Verifier decides done. No LLM on the decision path. No Cloudflare in v0.

## Repos

| Repo | Duty |
|------|------|
| sina-governance-SSOT | Lock · schemas · verifier · doctrine receipt · SG secretariat posture |
| SourceA | Implement `packages/executive-control-plane-v0` + 15 acceptance tests |
| NOETFIELD-RUNWAY | Consume later (not wired in v0); GoalDO remains live Goal Pursuit surface |

## Proof

```bash
bash scripts/verify_nf_executive_control_plane_v0_wiring_v1.sh
# SourceA:
cd packages/executive-control-plane-v0 && npm test
```

## Learning Organ

Incidents and capacity gaps continue to feed `NF-MOTOR-LEARNING-ORGAN-V1` / `NF-DECISION-CAPACITY-V1`. This plane does not auto-promote policies.

## Status

| Repo | Status |
|------|--------|
| sina-governance-SSOT | lock live on feature branch |
| SourceA | `packages/executive-control-plane-v0` implemented; 15 acceptance tests PASS |
| NOETFIELD-RUNWAY | consume later (not wired in v0) |
