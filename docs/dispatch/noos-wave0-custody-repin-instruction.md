# NOOS instruction — Wave 0 custody re-pin (founder-gated)

SG Wave 0 land is complete. Authority SHA on main: `dc6080d8519b8a83dcfaaeefb65392691ce3e33e`.

## Apply in noetfeld-OS only

1. Update `noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json` `sg_repo`:
   - `commit` → `dc6080d8519b8a83dcfaaeefb65392691ce3e33e`
   - `previous_commit` → current live pin value (do not assume)
2. Add `data/sg-authority-ref-unified-motor-v1.json` from SG:
   - source: `Noetfield-Systems/sina-governance-SSOT@main:data/sg-authority-ref-unified-motor-v1.json`

Machine instruction: `docs/dispatch` companion JSON fields below.

```json
{
  "schema": "noetfield/noos-custody-repin-instruction-v1",
  "apply_in": "noetfeld-OS",
  "file": "noetfield-org/CUSTODY_AUTHORITY_PINS_v1.json",
  "sg_repo": {
    "name": "sina-governance-SSOT",
    "commit": "dc6080d8519b8a83dcfaaeefb65392691ce3e33e",
    "previous_commit_was": "0e2c1ea2849823a9c642ae4fe4f9ec8e52d5482e",
    "note": "NOOS must read current pin before write; bump previous_commit to whatever was live."
  },
  "also_add": "data/sg-authority-ref-unified-motor-v1.json (copy from SG data/sg-authority-ref-unified-motor-v1.json)",
  "founder_gated": true,
  "do_not_apply_from_sg_lane": true
}
```

SG lane does not edit noetfeld-OS.
