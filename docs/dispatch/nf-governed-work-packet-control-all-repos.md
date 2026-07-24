# Dispatch — NF Governed Work Packet Control (all repos)

**decision_id:** `NF-GOVERNED-WORK-PACKET-CONTROL-V1`  
**Canon:** `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/NF_GOVERNED_WORK_PACKET_CONTROL_LOCKED_v1.md`  
**Machine:** `data/nf_governed_work_packet_control_v1_LOCKED.json`

## Repo duties

| Repo | Owner agent | Duty |
|------|-------------|------|
| `sina-governance-SSOT` | `sg_sssot_cursor` | LOCKED law, schemas, wiring verifier, agent_read_surfaces |
| `NOETFIELD-RUNWAY` | Motor / Goal Pursuit owners | Goal Contract immutability, HTU meter, breakers, intake hash, HDIR fingerprint |
| `SourceA` | `sourcea_brain` / worker | FBE Goal Contract envelope, cloud_auto_runtime terminals, broker HT events, brain false-done gate |

## Shared schemas

Copy or vendor from SG `data/schemas/`:

- `goal_contract_v1.json`
- `human_tax_event_v1.json`
- `work_packet_terminal_v1.json`
- `failure_signature_v1.json`
- `incident_packet_v1.json`

Reference helpers: `scripts/lib/governed_work_packet_v1.py`

## Phase order

1. SG canon (this repo)  
2. Runway GoalDO + Motor intake + HDIR  
3. SourceA contract + runtime + brain-core gate  
4. Cloud Human Tax meter loop (`loop_id=nf-human-tax-meter-v1`) only after path enforcement exists  

## Non-duties

- n8n is glue only  
- Motor Learning Organ remains the learning path (no parallel brain)  
- No Mac-only meter as sole motor  
