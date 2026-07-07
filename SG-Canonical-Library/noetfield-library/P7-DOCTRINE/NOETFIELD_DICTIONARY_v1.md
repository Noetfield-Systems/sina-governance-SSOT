# NOETFIELD_DICTIONARY_v1

**Long-form vocabulary SSOT · escalation & authoring layer**

Status: `v1` · **Not** loaded by every worker by default.  
Short daily form: `NOETFIELD_TERMINOLOGY_v1.md` · Layer guide: `P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md`

---

## How to use this file

Read a **dictionary entry** when:
- Two agents or docs disagree on a word
- You are writing a **new job, task cell, specialist role, or contract SKU**
- Customer copy might overclaim
- You need **reasoning**, not just the one-line terminology rule

Every dictionary entry must eventually have a terminology line if the word is daily-use.

**Entry format:** Meaning · Why we chose this · IS NOT · Edge cases · Examples · Related · Doctrine links

---

## Receipt

**Meaning**  
A receipt is a **fielded, machine-readable proof** that a specific unit of work happened. Minimum expectation: identifiable actor/system, timestamp, success/failure, and enough structured evidence that a **third party** could verify without trusting chat. In the factory layer, receipts also carry cost metering, op_key, and Supabase sink acknowledgment when the path is governed autorun.

**Why**  
Investors, customers, and our own census ask one question: *did it actually run?* Diagrams and agent self-reports answer “we think so.” Receipts answer “here is the row.” This is the funding thesis (`receipts-not-diagrams.md`) and R6/R7 in SSOT.

**IS NOT**  
- A stdout log  
- A markdown ledger note titled `*_RECEIPT_*` without schema (call that an **observation record** until fielded)  
- “Deployed successfully” from CI without deploy-truth check  

**Edge cases**  
- **Observation record:** SG health pass, census run — honest snapshots; label them; do not use for revenue proof.  
- **Degraded receipt:** step failed but sink acked (`FAILED_WITH_RECEIPT`) — still a receipt for guard loops; critique content lives inside.  
- **Brain public claims:** must match locked-definitions; receipt proves runtime, not marketing copy.

**Examples**  
- PASS: `autorun-cycle-receipt-v2` with op_key + `supabase_sink.ok=true`  
- FAIL: Agent says “I fixed the loop” with no cycle row  

**Related:** deploy-truth · proof receipt · claim · receipt ladder · negative proof  
**Doctrine:** `receipts-not-diagrams.md` · `mechanical-not-prose.md` · GOVERNED_AUTORUN L6–L8

---

## Observation record

**Meaning**  
A structured snapshot taken by guard or census machinery documenting **what was observed at time T** (fleet health, workflow census, library audit). It uses receipt-like JSON discipline but may not prove a customer outcome or payment.

**Why**  
We need honest yellow/red reporting without calling every guard pass a “payment receipt.” Conflating the two is how agents claim “full auto healthy” from partial motor green.

**IS NOT**  
R≥1 proof · Tier-1 audit delivery to customer · substitute for motor cycle receipt on loops

**Examples**  
- `noos-fleet-health-pass-v1` — valid observation record  
- `FIRST_REVENUE_RECEIPT` — only when payment fields are real  

**Related:** receipt · claim · GUARD · census

---

## Governed

**Meaning**  
A process is governed when the system can **stop it, measure it, and override it** without negotiating with the agent. Concrete signals: cost cap, kill switch, governance override, receipt each tick, fail-closed gates, founder-only irreversible path.

**Why**  
“Governed AI” is market noise. Our use is **legally and operationally precise**: if you cannot halt and produce receipts, do not call it governed in contracts or doctrine.

**IS NOT**  
Policy PDF on shelf · “we use Claude responsibly” · loop that runs until credit card fails silently

**Examples**  
- Governed: loop with interval + sink + heartbeat drift exit 1  
- Ungoverned: researcher loop with mock data and no consumer  

**Related:** cost cap · kill criteria · fail-closed · immutable floor  
**Doctrine:** `immutable-floor.md` · GOVERNED_AUTORUN v3

---

## Loop vs motor vs “24/7”

**Meaning**  
- **Motor:** scheduler (CF `*/5`, Railway executor) that decides *which* loop fires.  
- **Loop:** one unit of domain work on a schedule with interval, steps, receipt, caps.  
- **24/7 (honest):** motor green + receipts fresh within 2× interval for claimed targets.  

**Why**  
Agents label Cursor sessions, Mac launchd, and “founder sent 25 emails” as 24/7. That destroys trust internally and with diligence. Splitting motor/loop lets health passes report YELLOW honestly.

**IS NOT**  
- Chat session open overnight  
- GHA workflow with stale conclusion while Railway runs  
- Marketing “always-on brain” without motor name + receipt age  

**Examples**  
- “NOOS fleet motor GREEN; 8/14 loops RUNNING; inbox STALE” — honest  
- “Full auto 24/7 revenue” with R=0 — theater  

**Related:** deploy-truth · drift · observation record  
**Ledger:** `NOOS_FLEET_HEALTH_PASS_2026-07-06.md`

---

## GUARD · REVENUE · META · NONE (census classes)

**Meaning**  
WORKFLOW_CENSUS_v1 asks: **which receipt does this loop serve?**  
- **REVENUE:** stranger → lead / conversation / payment / delivery (`R≥1` path)  
- **GUARD:** integrity of live system (verify, probe, audit, deadman)  
- **META:** system grooms itself (promote CI, inbox drain, self-heal theater chain)  
- **NONE:** no named consumer 14d → retire proposal  

**Why**  
When META cost > GUARD + REVENUE, the system is grooming itself instead of earning or protecting. Rule 2 and Rule 4 in census turn RED.

**IS NOT**  
- `value_class: revenue_path` in NOOS registry without census check (inbox mislabel)  
- “Everything is important” — forces FIX spend on RETIRE loops  

**Examples**  
- workflow_audit → GUARD → FIX  
- inbox internal queue → META → RETIRE  
- gateway_outbound → REVENUE only when founder sends + channel receipt  

**Related:** FIX/RETIRE · R≥1 · observation record  
**Files:** `workflow_census_value_class_rules_v1.json` · `NOOS_LOOP_CENSUS_ROOTCAUSE_2026-07-06.md`

---

## Vendor-neutral

**Meaning**  
No AI vendor gets default routing. Priority is **scoped, named, receipt-earned, revocable** (preferred routing). Commercial openness is contract-shaped, not brand loyalty.

**Why**  
“Model-agnostic” reads technical and vague in enterprise copy. “Vendor-neutral” matches partnership doctrine: we are not begging for free API; we offer governed reference environment + commercial alignment.

**IS NOT**  
Refusal to partner · no preferred routing ever · “we hate OpenAI”

**Rewrite rule**  
Replace `model-agnostic` in all **written** library and site copy with `vendor-neutral` unless quoting an external spec literally.

**Related:** preferred routing · commercial alignment · replacement rights  
**Doctrine:** `deterministic-brain-doctrine.md` D-8 (concept); terminology owns the word

---

## Deploy-truth

**Meaning**  
The state of production as verified by **live probe** (HTTP 200, health URL, Supabase row age, CF `/health` target list), not repo disk or agent narrative.

**Why**  
Third disk-vs-live incident class. Committed file ≠ live worker. GHA conclusion stale while Railway runs is a deploy-truth split.

**IS NOT**  
`git push` succeeded · wrangler deploy log · “I deployed” in chat

**Examples**  
- CF health shows 14 Railway targets; repo worker JS shows 7 → drift  
- Contract page validator PASS on live URL → deploy-truth PASS  

**Related:** drift · fail-closed · split-brain  
**Doctrine:** SSOT v6 invariant 0.3 Reality > report

---

## Selective (commercial tone)

**Meaning**  
We work with **few** partners chosen on evidence. Signals high bar and standards.

**Why**  
Coding agents hear “selective” as exclusivity/arrogance. Institutional tone: selective = disciplined, not “we’re too good for you.”

**IS NOT**  
Snobbery · exclusion club · unprovable “elite” positioning

**Public example**  
“Selective collaboration with model providers” — OK  
“We only work with the best founders” — arrogant; cut  

**Related:** design partner · NDA · governed reference environment  
**Terminology:** §5 · §7 banned needy register

---

## Governed reference environment

**Meaning**  
Our **demonstrable**, receipt-backed operating setup that a vendor or diligence team can inspect: eval PASS, live proof URLs, motor health, schema samples — not a list of logos.

**Why**  
“We have a client base” without provable customers is an overclaim that kills enterprise trust and violates negative-proof doctrine.

**IS NOT**  
Customer logo wall · “500+ clients” · pipeline fantasy

**When partner has real clients**  
Name them only with permission and receipt; otherwise use governed reference environment.

**Related:** proof receipt · diagnostic · NDA  
**Terminology:** replaces `client base` when unprovable

---

## Diagnostic vs enforce

**Meaning**  
- **Diagnostic:** audit, assessment, leak find, readiness — **no live control plane installed**  
- **Enforce / firewall / control plane:** blocks/spend caps live in customer path — requires implementation receipt  

**Why**  
Tier-1 offer is diagnostic-only (`agentic-cost-governance-service.md`). Sites correctly say “governable” and “controls before execution” as **capability**; must not imply live firewall unless deployed.

**IS NOT**  
Selling enforcement while shipping slides only

**Public copy rule**  
SourceA/Noetfield pages may describe sprint **deliverables** and **governance OS** as product vision; mark live vs roadmap; Tier-1 = diagnostic engagement name.

**Related:** Tier-1 audit · overclaim guard · reserved commercial figure

---

## Brain vs worker vs locked-definitions

**Meaning**  
- **Brain:** deterministic decider; holds no soupy meaning  
- **Worker:** LLM or coding agent that drafts/executes under gates  
- **Locked-definitions:** approved public meaning the brain reads (P6); not the whole dictionary  

**Why**  
If public models own meaning, drift is guaranteed. Dictionary defines **system words**; locked-definitions defines **SourceA public claims**.

**IS NOT**  
Loading FOUNDER_JUDGMENT_PATTERNS into workers (least-knowledge violation)

**Related:** soup vs raw · least-knowledge · layered-agents  
**Files:** `P6-BRAIN-MEANING/locked-definitions-v1.md`

---

## Drift · fail-closed · schedule home

**Meaning**  
- **Schedule home:** `data/noos-24-7-loops-v1.json` interval is committed truth; workflow cron must match or be absent when motor dispatches.  
- **Drift:** registry vs deployed cron, config hash, route, worker target count.  
- **Fail-closed:** deploy/heartbeat exits 1 on drift (same class as hash gates).  

**Why**  
self_heal `every_10m` vs hourly GHA cron caused false green and heartbeat noise.

**Examples**  
- `verify_noos_loop_schedule_registry_v1.py` before CF deploy  
- Heartbeat L12 mismatches list  

**Related:** deploy-truth · loop · motor

---

## Tombstone · RETIRE · FIX

**Meaning**  
- **Tombstone:** mark artifact/loop/meaning dead in registry; do not read as live  
- **RETIRE (census):** META/no-consumer loop — propose removal, do not repair  
- **FIX (census):** GUARD/REVENUE consumer — root cause, fix, one receipt ≤ interval  

**Why**  
Repair theater on META loops burns META budget (census Rule 2).

**Examples**  
- factory_autorun RETIRE — superseded motor slot  
- workflow_audit FIX — GUARD consumer  

**Ledger:** `NOOS_LOOP_CENSUS_ROOTCAUSE_2026-07-06.md`

---

## Adding a new entry (template)

```
## Term name
**Meaning** (plain English, 2–4 sentences)
**Why** (reasoning — why this word, why not synonym)
**IS NOT** (common misread)
**Edge cases**
**Examples** (good vs bad)
**Related**
**Doctrine / files**
```

Founder locks → compress to TERMINOLOGY § → update SSOT_INDEX → run terminology audit on affected docs.

---

*v1 (2026-07-06) — Initial dictionary seed: receipt family, census, motor/loop, commercial tone, deploy-truth, vendor-neutral, diagnostic/enforce split.*
