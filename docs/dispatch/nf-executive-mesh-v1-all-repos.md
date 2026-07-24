# Dispatch — NF-EXECUTIVE-MESH-V1

**decision_id:** `NF-EXECUTIVE-MESH-V1`  
**Machine:** `data/nf_executive_mesh_v1_LOCKED.json`

## One line

Executive Mesh on production: Role Pods recommend; Governor commits; Runway Goal Kernel executes webpage-repair; Supabase is SSOT.

## Repos

| Repo | Duty |
|------|------|
| sina-governance-SSOT | Lock · dispatch · doctrine receipt |
| SourceA | Production map · mesh package · Governor DO Worker · Supabase migration · E2E |
| NOETFIELD-RUNWAY | Execution consumer (`/v1/goals`); prefer zero code change for slice-1 |

## Proof

```bash
bash scripts/verify_nf_executive_mesh_v1_wiring_v1.sh
# SourceA:
cd packages/executive-mesh-v1 && npm test
```

## Status

| Repo | Status |
|------|--------|
| sina-governance-SSOT | lock on feature branch |
| SourceA | mesh package + governor worker (slice-1) |
| NOETFIELD-RUNWAY | consume existing Goal Kernel |
