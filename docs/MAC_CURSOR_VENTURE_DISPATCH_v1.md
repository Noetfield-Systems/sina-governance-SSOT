# Venture lane dispatch prompts v1

Scoped one-task prompts — open the listed Cursor root; do not cross repos.

**LAWS:** FOUNDER_CANON v1 + governed-autorun v3. Violations = `BLOCKED_WITH_REASON`. Receipts carry `canon_version: founder_canon_v1.0.0`.

**Governance structure/version law:** `ssot/GOVERNANCE_STRUCTURE_AND_VERSION_AUTHORITY_v1.md` — SG owns structure; existing rules stay live; newer versions amend and win only on direct conflict.

**Integrator (NOOS lane only):** session that mutates integrator state → `python3 scripts/noos_integrator_sync_v1.py sync --agent-id <id>` before stop. Mirror: `~/.sina/noos-integrator-state-v1.json` (coordination copy). Cloud owner: see `data/noos-integrator-role-v1.json`. SG mirror: `ssot/NOOS_INTEGRATOR_RULES_v1.md`.

---

## Lane A — SourceA Brain (B-01)

**Root:** `~/Projects/SourceA`  
**Owner:** `sourcea_brain`  
**Task cell:** `sourcea_brain_register`

```
Task: Brain B-01 — register Signal Factory v1 pointer row (no collision).

Path: ~/Projects/SourceA

Target: brain registry / knowledge bundle pointer for ~/.cursor/skills/signal-factory/

Action: Add read-only pointer; independent verify not required for v1 meaning-complete skill.

Check: validate_brain_domain_registry_v1.py ALL PASS; no collision with locked-definitions.

Stop: receipt or registry row committed in SourceA only.
```

---

## Lane A — SourceA Brain (B-02)

**Root:** `~/Projects/SourceA`  
**Owner:** `sourcea_brain`

```
Task: Brain B-02 — TrustField separation pointer in Brain routing.

Path: ~/Projects/SourceA

Target: routing / registry docs that enforce TF one-way export.

Action: Pointer only — no TF doctrine writes.

Check: handoff doc SOURCEA_BRAIN_HANDOFF_SIGNAL_FACTORY_TRUSTFIELD_v1.md criteria.

Stop: pointer row live; no trustfield-loops edits.
```

---

## Lane A — SourceA Brain (B-03)

**Root:** `~/Projects/SourceA`  
**Owner:** `sourcea_brain`

```
Task: Brain B-03 — memory_line template for Signal Factory receipts.

Path: ~/Projects/SourceA

Target: brain memory / receipt schema hook.

Action: Wire SF receipt → Brain memory_line format (read-only ingest).

Check: structure validator PASS.

Stop: template documented + registry pointer; no SG edits.
```

---

## Lane B — TrustField Worker (Phase 2 prep)

**Root:** `~/Desktop/trustfield-loops`  
**Owner:** `trustfield_worker`  
**Blocked until:** SG B2 sign-off

```
Task: TF Phase 2 prep — regulated-term regex list (no send API).

Path: ~/Desktop/trustfield-loops

Target: triage regex module only.

Action: Implement deterministic regex BEFORE model; preview only.

Check: npm run test:phase1 still PASS.

Stop: receipt; no production trustfield.ca webhook.
```

---

## Lane C — SG (B2)

**Root:** `~/Projects/sina-governance-ssot`  
**Owner:** `sg_sssot_cursor`

```
Task: B2 — SG sign-off on regulated-term-hardstop-v1.json.

Path: ~/Projects/sina-governance-ssot

Target: data/regulated-term-hardstop-v1.json

Action: Founder review + sign-off metadata row; no venture repo edits.

Check: JSON schema valid; mirror in ssot/sg-guardrails-trustfield-v1.md if needed.

Stop: sign-off receipt; unlock TrustField Phase 2 lane.
```

---

## Lane D — SourceA Worker (fixtures)

**Root:** `~/Projects/SourceA`  
**Owner:** `sourcea_worker`

```
Task: Paste 7 real inbox fixtures for Signal Factory agreement report.

Path: ~/Projects/SourceA

Target: fixtures directory for signal-factory verifier extension.

Action: Paste-only — no Gmail OAuth.

Check: agreement report ≥90% vs Sina labels.

Stop: fixtures + report receipt; no brain promote.
```

---

## Lane E — NOOS doctrine

**Root:** `~/Projects/noetfeld-os`  
**Owner:** `noos_agent`

```
Task: Append canonical TrustField doctrine pointer in NOOS repo.

Path: ~/Projects/noetfeld-os

Target: docs/_NOOS_AGENT/ (canonical — not SG mirror)

Action: Pointer to SG guardrail mirror; read-only observe SourceA.

Check: gel-ci.yml PASS on push.

Stop: commit in noetfeld-os only; no SourceA writes.
```
