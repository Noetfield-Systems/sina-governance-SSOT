# Dispatch — NF-DECISION-CAPACITY-V1

**decision_id:** `NF-DECISION-CAPACITY-V1`  
**Machine:** `data/nf_decision_capacity_v1_LOCKED.json`

## Repos

| Repo | Duty |
|------|------|
| sina-governance-SSOT | Lock · schemas · `decision_capacity_v1.py` · verifier · Learning Organ receipt path |
| NOETFIELD-RUNWAY | GoalDO / Motor: on HT/soft breakers emit `MISSING_DECISION_CAPACITY` + proposal + learning draft |
| SourceA | Human Tax meter / cloud_auto_runtime: same capacity loop; Brain does not invent next_action |

## Proof

```bash
bash scripts/verify_nf_decision_capacity_wiring_v1.sh
python3 -m unittest tests.test_decision_capacity_v1 -v
```

## Learning Organ

Candidates land as OPEN `learning_record` drafts (`layer=policy`). Shadow/replay/promote stays under `NF-MOTOR-LEARNING-ORGAN-V1`.
