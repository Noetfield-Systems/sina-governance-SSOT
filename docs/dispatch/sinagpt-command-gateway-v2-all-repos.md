# Dispatch — SinaGPT + Command Gateway v2 (all repos)

**Authority (role):** `P1-CANON/SINAGPT_FOUNDER_BRAIN_ARCHITECT_LOCKED_v1.md`  
**Authority (API):** `P0-FOUNDATION-SPINE/NF_COMMAND_GATEWAY_V2_ARCHITECTURE_LOCKED_v1.md`  
**Commission:** `docs/dispatch/nf-command-gateway-v2-motor-control-001.md`  
**Unified Motor:** `NF-UNIFIED-MOTOR-ARCHITECTURE-V1` @ `dc6080d8519b8a83dcfaaeefb65392691ce3e33e`

## One-liner

```text
SinaGPT = founder.brain-architect cockpit (not Issue Manager / CI daemon / Motor). Command Gateway v1 stays. v2 adds Motor+Issues+CI+SG reads, commissions, seven-truth, OAuth founder split, idempotency; raw workflow-dispatch is internal. Implement NF-COMMAND-GATEWAY-V2-MOTOR-CONTROL-001 as draft PR only.
```

## Per-repo

| Repo | Action |
|------|--------|
| sina-governance-SSOT | Canon + authority SHA |
| noetfield-cloud-factory-infra | Implement Gateway v2 commission |
| noetfeld-OS | Issue Manager / CI reliability owners; consume Gateway; do not redefine cockpit |
| SourceA | Compile commissions → recipes |
| sandbox / builders | Ephemeral workers under Builder Owner |

## Forbidden

- Declaring Gateway v2 canonical from infra repo alone
- Treating Custom GPT as 24/7 issue watcher
- GPT Action for merge or production-deploy endpoints
