# SourceA FORM_OFFICIAL — simplified batch submit map (dry-run only)

**Not submitted.** Machine-closable and deferred rows excluded.

| # | SourceA row ID | submit pick | reason | SG decision | founder fact? |
|---|----------------|-------------|--------|-------------|---------------|
| 1 | `Q-FINAL-01` | `A` | Outbound P0 spine; catalog parallel not paused | C1 | no |
| 2 | `Q-BC-05` | `A` | Outbound is spine; Goal 1 does not block drain | C1 | no |
| 3 | `Q-CHAT-NEXT-P0-01` | `B` | Outbound first: RUN INBOX sa-1200, not form-block-first | C1 | no |
| 4 | `Q-SESSION-FORM-BUILD` | `A` | Form fill parallel with Worker BUILD — meta supports revenue | C1 | no |
| 5 | `Q-SESSION-INBOX-NEXT` | `A` | RUN INBOX P0-13 next — outbound queue head | C1 | no |
| 6 | `ENF-08` | `YES` | Either counts: Cash PASS=deposit OR Commitment PASS=signed LOI/SOW (patch labels) | C2 | no |
| 7 | `ENF-01` | `A` | Film on schedule; parallel track — not waiting for Hub button | C3 | no |
| 8 | `ENF-02` | `APPROVE` | Small outreach parallel; broad outreach waits for demo asset | C3 | no |
| 9 | `ENF-14` | `C` | LinkedIn gate open by default (DEFER); flip to APPROVE only if founder confirms updated | C3+D | YES |
| 10 | `Q-BC-07` | `C` | Auto for mapped/GUARD bays; manual or sign-only for unmapped/REVENUE | C4 | no |
| 11 | `Q-CW-SOURCEA-APP` | `A` | DNS fix public-priority (parallel track) | C5 | no |
| 12 | `Q-CW-BATCH3` | `A` | Drain continues — batch 3 arms while DNS track runs | C5 | no |
| 13 | `Q-MF-02` | `C` | Wait: verify package, copy, version, login before npm publish | C6 | no |
| 14 | `Q-MF-03` | `A` | One Proof Layer card only when publish gate opens | C6 | no |
| 15 | `Q-CHAT-PUBLISH-01` | `B` | Wait until simplified batch + language surface lock applied | C6 | no |
| 16 | `Q-WBC-PROOF-LAB-OK` | `C` | Internal/appointment-only — no external buyer URL yet | C7 | no |
| 17 | `Q-SESSION-TUNNEL-DEMO` | `B` | Local only until founder authorizes tunnel | C7 | no |
| 18 | `Q-WBC-STYLE-B1` | `B` | Defer hero film; Proof Lab interactive sufficient for selective demos | C7 | no |
| 19 | `Q-CHAT-LANG-01` | `B` | Per surface: Persian for meaning/internal; English for paths/proof/public | C8 | no |
| 20 | `Q-CHAT-PLUSONE-01` | `A` | Wire PLUS ONE + Prompt OS before voice; supports surface split | C8 | no |
| 21 | `Q-MF-10` | `B` | Default not sent — use A only if founder confirms Mail sent | D | YES |
| 22 | `Q-WBC-OCRE-L3` | `B` | Default not confirmed — use A only if founder confirms Mail from their account | D | YES |

## Dry-run command (SourceA repo — founder actor, no live submit)

```bash
cd ~/Desktop/Noetfield-Systems/SourceA

python3 scripts/hub_form_submit_v1.py --dry-state --actor founder \
  --picks-json "$(cat /Users/sinakazemnezhad/Desktop/Noetfield-Systems/sina-governance-SSOT/SG-Canonical-Library/noetfield-library/P99-LEDGER/SOURCEA_FORM_OFFICIAL_SUBMIT_MAP_SIMPLIFIED_2026-07-07.json)" \
  --json | jq '{ok, complete: .complete, picked_count: .count, open_count: .open_count, missing_ids: .missing_ids}'
```

Before live submit: resolve founder-fact rows (ENF-14, Q-MF-10, Q-WBC-OCRE-L3) if facts changed from default.

Overrides-only path: `/Users/sinakazemnezhad/Desktop/Noetfield-Systems/sina-governance-SSOT/SG-Canonical-Library/noetfield-library/P99-LEDGER/SOURCEA_FORM_OFFICIAL_SUBMIT_MAP_SIMPLIFIED_2026-07-07.json`
