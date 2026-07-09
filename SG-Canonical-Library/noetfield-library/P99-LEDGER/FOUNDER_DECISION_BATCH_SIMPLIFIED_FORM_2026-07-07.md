# Founder decision batch — simplified form (2026-07-07)

**Status:** LOCKED by founder · **Not submitted** to SourceA FORM_OFFICIAL (INCIDENT-037)  
**Source:** 80-row form collapsed to 8 advisor + 3 fact decisions  
**Locked at:** 2026-07-07T06:55:34Z

---

## C — Advisor decisions

### C1 — Daily north star
**Pick:** A — Outbound first  
**Reason:** Revenue motion is P0. Form/meta supports it, not replaces it.  
**Row IDs absorbed:** Q-FINAL-01, Q-BC-05, Q-CHAT-NEXT-P0-01, Q-SESSION-FORM-BUILD, Q-SESSION-INBOX-NEXT

### C2 — W3 PASS bar
**Pick:** C — Either deposit OR signed LOI/SOW  
**Patch — track two labels:**
- **Cash PASS** = deposit received
- **Commitment PASS** = signed LOI/SOW  
**Row IDs absorbed:** ENF-08 (+ ENF-03, ENF-17 context)

### C3 — Film vs outreach
**Pick:** B — Parallel  
**Patch:** Outreach can start small; **broad** outreach waits for proof/demo asset.  
**Row IDs absorbed:** ENF-01, ENF-02, ENF-14

### C4 — Loop auto dispatch
**Pick:** C — Auto GUARD only; REVENUE requires founder tap  
**Reason:** Guard loops can auto-run with receipts. Revenue-facing work still needs founder tap.  
**Row IDs absorbed:** Q-BC-07 (+ Q-CONF-FALSE-DONE-GUARD context)

### C5 — DNS vs drain batch 3
**Pick:** C — Parallel, but DNS has public-priority  
**Reason:** Broken sourcea.app hurts credibility; cloud drain should not fully stop.  
**Row IDs absorbed:** Q-CW-BATCH3, Q-CW-SOURCEA-APP

### C6 — npm Card 1 publish
**Pick:** B — Wait  
**Reason:** npm creates public commitment. First verify package, copy, version, and login.  
**Row IDs absorbed:** Q-MF-02, Q-MF-03, Q-CHAT-PUBLISH-01

### C7 — WitnessBC public demo
**Pick:** C — Appointment-only local  
**Reason:** Show buyers selectively; do not make public until hero/proof posture is clean.  
**Row IDs absorbed:** Q-WBC-PROOF-LAB-OK, Q-SESSION-TUNNEL-DEMO, Q-WBC-STYLE-B1

### C8 — Default reply language
**Pick:** C — Per surface, not per session  
**Patch:**
| Surface | Language |
|---------|----------|
| Internal / founder support | Persian allowed |
| Technical docs / agents / public / contracts | English |  
**Row IDs absorbed:** Q-CHAT-LANG-01, Q-CHAT-PLUSONE-01

---

## D — Founder facts (conditional)

| Row ID | Rule |
|--------|------|
| **Q-MF-10** | If Mail **not** personally sent → **B / not sent** |
| **ENF-14** | If LinkedIn **not** updated → **not done**; keep gate open |
| **Q-WBC-OCRE-L3** | If Mail **not** sent from founder account → **not confirmed** |

---

## Machine apply targets (SG / SourceA — not executed here)

| Decision | Apply when wired |
|----------|----------------|
| C1 | OUTBOUND first in daily priority registry; form/meta parallel |
| C2 | Receipt schema: `cash_pass` + `commitment_pass` labels |
| C3 | Outreach policy: small-parallel OK; broad blocked until demo asset |
| C4 | Loop registry: GUARD=auto, REVENUE=founder_tap |
| C5 | DNS track public-priority; drain continues parallel |
| C6 | npm publish gate stays closed until verify checklist |
| C7 | Proof Lab appointment-only; no public tunnel |
| C8 | Language gate surfaces: internal vs public/contract/prompt |

---

## Summary

| Layer | Count | Status |
|-------|-------|--------|
| Advisor (C1–C8) | 8 | Locked |
| Founder-fact (D) | 3 | Conditional rules locked |
| Original form rows | 80 | Collapsed — do not re-ask all 80 |

*Receipt only. No FORM_OFFICIAL submit from this agent.*
