# Supabase Pause Email — Verifier Triage Receipt

**Status:** TRIAGED  
**Date:** 2026-07-05  
**Trigger:** Supabase email — project `cybzznaieigeveiaoyoa` paused (personal org)  

---

## Email summary

| Field | Value |
|-------|-------|
| Paused project ID | `cybzznaieigeveiaoyoa` |
| Org | `sina.kazemnezhad.ca@gmail.com's Org` |
| Reason | Free-tier 7-day inactivity auto-pause |
| Restore window | 90 days from dashboard |

---

## Verifier finding (SG probe 2026-07-05)

**The paused project is NOT production.**

| Ref | Role | Probe | In Sina env? |
|-----|------|-------|--------------|
| `ldfruywifqnfpwsfgmdl` | portfolio-spine (SourceA, Forge, gov) | ✅ OK | `~/.sourcea-secrets/portfolio-spine.env` |
| `tkgpapowwplupyekpivy` | noetfield (Noetfield, TrustField, NOOS factory) | ✅ OK | `~/.sourcea-secrets/noetfield.env` |
| `cybzznaieigeveiaoyoa` | **Unknown personal-org orphan** | ❌ Unreachable (paused) | **Not in SSOT or env files** |

SSOT authority: `SourceA/data/supabase-cloud-project-map-v1.json` + `supabase-never-resume-refs-v1.json`

---

## Founder action

1. **Do NOT unpause `cybzznaieigeveiaoyoa`** unless you identify what it was — it is not wired to any live lane.
2. **No production action required** — both live projects respond today.
3. **Prevent future pause on live projects:** run SourceA daily pulse:
   ```bash
   bash ~/Desktop/Noetfield-Systems/SourceA/scripts/run-portfolio-supabase-daily-v1.sh
   ```
4. Optional: delete or export-then-ignore the orphan project in personal org dashboard to stop noise emails.

---

## SG verifier script

```bash
python3 scripts/verify_supabase_live_profiles_v1.py --json --write-receipt
```

**Latest probe:** PASS (2026-07-05T12:56:59Z) — both live refs responding. Receipt: `receipts/supabase-live-profiles-verify-20260705T125659Z.json`

**Signer:** SG-verifier + Sina env probe
