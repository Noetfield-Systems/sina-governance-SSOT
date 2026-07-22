# NOETFIELD_DICTIONARY_v1

**Meaning authority · foundational · broader · escalation-only**

Status: `v1.3` · **Source** from which terminology entries are minted. Not loaded on every worker output by default.

Answers: **“What does this really mean, and is it allowed to exist?”**  
Wording (daily): `NOETFIELD_TERMINOLOGY_v1.md` — one line minted **from** this file, never the reverse.  
Layer guide: `P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md`

---

## Hard gate (minting rule)

**No new job, task, specialist, role, product page, contract clause, or receipt field** enters the system without:

- an **existing entry** in this dictionary, or  
- a **new entry authored and versioned here first** (founder lock → bump dictionary version)

Only after dictionary lock may the terminology one-liner be minted.

---

## When to load this file

- Two agents or docs disagree on meaning  
- Authoring a **new** job, task cell, specialist, role, page, clause, or receipt field  
- Customer copy might overclaim — read **public rewrite** section of the entry  
- Escalation: dispatch sets `load_dictionary: true`

Every daily-use word **must** have a terminology line minted from its dictionary entry.

**Entry format:** Meaning · Why it exists · Wrong readings (IS NOT) · Edge cases · Examples · **Conflict rule** · **Public rewrite** · Related · Doctrine links

---

## Receipt

**Meaning**  
A receipt is a machine-readable proof that a specific unit of work happened. It must have defined fields: who, model, cost, tokens, success, latency, time, and sink ack when applicable. It must have enough structured proof so that a third party can verify the work without relying on chat messages. In the factory layer, it also includes cost metering, op_key, and Supabase sink acknowledgment for governed autorun paths.

**Why**  
Investors, customers, and our own census want to know if a task actually ran. Diagrams and agent claims only show plans. Receipts show the actual database row or file. This follows the funding thesis (`receipts-not-diagrams.md`) and rules R6/R7 in SSOT.

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

**Conflict rule**  
Dictionary meaning wins over filename (`*_RECEIPT_*`), chat “done,” and doctrine metaphor. If terminology and dictionary disagree, fix terminology in the same change set. Proof receipt requires fielded schema; guard snapshots are observation records.

**Public rewrite**  
- Allowed: “verifiable record,” “proof on disk,” “machine-checked result”  
- Banned: “we guarantee outcomes,” “certified,” “100% verified” without schema cite  
- Plain substitute when proof missing: “unverified — no receipt yet”

**Related:** deploy-truth · proof receipt · claim · receipt ladder · negative proof  
**Doctrine:** `receipts-not-diagrams.md` · `mechanical-not-prose.md` · GOVERNED_AUTORUN L6–L8

---

## Observation record

**Meaning**  
A structured record taken by guard or census systems showing what was seen at a specific time (such as fleet health, workflow census, or a library audit). It uses structured JSON like a receipt, but does not prove a customer payment or outcome.

**Why**  
We need honest status reporting without calling every guard check a payment receipt. Mixing these up lets agents claim a system is fully healthy when it is only partly running.

**IS NOT**  
R≥1 proof · Tier-1 audit delivery to customer · substitute for motor cycle receipt on loops

**Examples**  
- `noos-fleet-health-pass-v1` — valid observation record  
- `FIRST_REVENUE_RECEIPT` — only when payment fields are real  

**Related:** receipt · claim · GUARD · census

---

## Governed

**Meaning**  
A process is governed if the system can stop, measure, and override it without asking the agent. Clear signs include a cost cap, a kill switch, a governance override, a receipt for each tick, fail-closed gates, and a path that only the founder can change.

**Why**  
Many use the term "governed AI" as a marketing buzzword. We use it in a precise operational way: if you cannot stop the process and generate receipts, it is not governed.

**IS NOT**  
Policy PDF on shelf · “we use Claude responsibly” · loop that runs until credit card fails silently

**Examples**  
- Governed: loop with interval + sink + heartbeat drift exit 1  
- Ungoverned: researcher loop with mock data and no consumer  

**Related:** cost cap · kill criteria · fail-closed · immutable floor  
**Doctrine:** `immutable-floor.md` · GOVERNED_AUTORUN v3

---

## Loop vs ops motor vs “24/7”

**Meaning**  
- **Ops Motor / Scheduler and executor:** A cloud scheduler (such as Cloudflare cron or a Railway executor) that decides which loop runs.  
- **Loop:** One unit of work that runs on a schedule with a set interval, steps, receipt, and caps.  
- **24/7 (honest):** A status showing that the ops motor is running and receipts are newer than twice the loop interval.  

**Why**  
Agents often call simple active chats or manual tasks 24/7. This hurts trust with partners and auditors. Separating the ops motor from the loop lets our health checks report status honestly.

**IS NOT**  
- Chat session open overnight  
- GHA workflow with stale conclusion while Railway runs  
- Marketing “always-on brain” without motor name + receipt age  
- The product **AI Motor** category (vehicle for governed execution) — see next entry  

**Examples**  
- “NOOS fleet motor GREEN; 8/14 loops RUNNING; inbox STALE” — honest  
- “Full auto 24/7 revenue” with R=0 — theater  

**Conflict rule**  
Bare “Motor” in fleet/census/ops health = **Ops Motor / Scheduler and executor**. “AI Motor” in product, customer, or `/motors/` copy = **AI Motor**. Never equate them.

**Related:** deploy-truth · drift · observation record · AI Motor  
**Ledger:** `NOOS_FLEET_HEALTH_PASS_2026-07-06.md`

---

## AI Motor vs AI engine (vehicle nesting)

**Meaning**  
- **AI Motor:** The governed execution vehicle that turns human intent or business events into verified operational outcomes. It coordinates engines, agents, tools, workflows/runways, policy, knowledge, budget, and human authority; it verifies, repairs, escalates, recovers, and records receipts.  
- **AI engine:** One intelligence / reasoning / analysis power unit *inside* (or beside) a Motor — model, critic, classifier, retriever, scorer, draft generator, decision-support function. Many engines may run inside one Motor.  
- **Nesting law:** One Motor. Many engines. They are **not** synonyms. Engines answer “what should happen / what does this mean?” The Motor answers “how does work keep moving safely with proof?”

**Why**  
Calling the whole product an “AI engine” collapses Noetfield into a model wrapper. Treating Motor as slang for engine erases the operating vehicle.

**IS NOT**  
- AI Motor = AI engine  
- AI engine = the whole product, promotion authority, or continuous case progression alone  
- AI Motor = chatbot, overnight Cursor session, or unbounded autonomy  
- Engines minting final truth without verification / human gates  

**Car analogy (canonical story)**  
**AI Motor ≅ Tesla-class car:** the whole vehicle that turns human intent into action and work. Engines (big and small), computers, pipelines = power and compute *inside* the car. Transmission = workflows/runways. Wheels = tools/APIs. Driver = human decision authority. Trip log = receipts. Not a lone engine on a stand. Full story SSOT: `NOETFIELD_MOTOR_ENGINE_VOCABULARY_v1.md`.

**Architecture sentence**  
Deterministic Motor + bounded AI engines + human decision authority.

**Examples**  
- TrustField: engines draft/classify/summarize; Motor runs intake → evidence → assignment → deadlines → escalate → approve → audit-pack close.  
- Runways: shared Motor routes cheap engines + tools through plan → execute → verify → repair → receipt.  
- Public chat: “ten business ideas” = engine-only. Persistent build sequence to payment = Motor around engines.

**Conflict rule**  
Never present Motor and engine as interchangeable. Product/customer copy uses **AI Motor** for the vehicle and **AI engine(s)** for intelligence components. Ops/fleet copy uses **Scheduler and executor** (ops motor) for schedulers.

**Public rewrite**  
> An AI Motor is like a Tesla-class car: it turns human intent into action and work. AI engines are the intelligence power units inside that vehicle — many engines can serve one Motor. Engines analyze and draft; the Motor advances, verifies, escalates, and records.

**Related:** Scheduler and executor · Loop · Runway · Receipt · Governed · vendor-neutral  
**Doctrine:** `NOETFIELD_MOTOR_ENGINE_VOCABULARY_v1.md` · public `/motors/` · A-Z batch entries `AI Motor` / `AI engine`

---

## GUARD · REVENUE · META · NONE (census classes)

**Meaning**  
A way to classify what kind of receipt a loop serves under `WORKFLOW_CENSUS_v1`:  
- **REVENUE:** A path that serves an external user to generate a lead, conversation, payment, or delivery (such as `R≥1` path).  
- **GUARD:** A path that protects the system, such as verifying, checking, auditing, or running a deadman switch.  
- **META:** A path for system self-maintenance, like deploying code, clearing queues, or self-healing.  
- **NONE:** A loop with no active consumer for 14 days, which should be retired.  

**Why**  
If self-maintenance costs more than protecting the system and making money, the system is wasting resources. This causes census rules 2 and 4 to fail.

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
We do not use any AI provider by default. We route work based on clear, earned receipts. This routing can be changed or canceled. Our relationships are defined by contracts, not brand loyalty.

**Why**  
Terms like "model-agnostic" sound vague and technical. "Vendor-neutral" matches our goals: we do not ask for free access, but offer a verified setup and clear partnership terms.

**IS NOT**  
Refusal to partner · no preferred routing ever · “we hate OpenAI”

**Rewrite rule**  
Replace `model-agnostic` in all **written** library and site copy with `vendor-neutral` unless quoting an external spec literally.

**Related:** preferred routing · commercial alignment · replacement rights  
**Doctrine:** `deterministic-brain-doctrine.md` D-8 (concept); terminology owns the word

---

## Deploy-truth

**Meaning**  
The actual state of the live system checked by a direct probe, such as an HTTP 200 response, a health page, database row age, or a Cloudflare health list. It is not what is saved on disk or reported by an agent.

**Why**  
Code saved in a file is not always the same as the live running code. Relying on git pushes or stale build logs can lead to mismatches.

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
We work with only a few partners chosen based on evidence. This shows we have high standards.

**Why**  
Agents might view "selective" as snobbish. We use it to show discipline and focus, not arrogance.

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
A verifiable, receipt-backed setup that partners or auditors can inspect. It includes test results, live URLs, scheduler status, and database schema samples, rather than a list of brand logos.

**Why**  
Claiming to have many clients without proof hurts trust. We must show our actual running system instead of unverified claims.

**IS NOT**  
Customer logo wall · “500+ clients” · pipeline fantasy

**When partner has real clients**  
Name them only with permission and receipt; otherwise use governed reference environment.

**Related:** proof receipt · diagnostic · NDA  
**Terminology:** replaces `client base` when unprovable

---

## Diagnostic vs enforce

**Meaning**  
- **Diagnostic:** An audit, assessment, or check that does not change live traffic or spend.  
- **Enforce:** A live system that blocks actions or limits spend in the customer's active path, which requires proof of installation.  

**Why**  
Our first service tier is diagnostic only. Our public pages can describe our capability, but must not claim we are actively blocking live traffic unless it is actually set up.

**IS NOT**  
Selling enforcement while shipping slides only

**Public copy rule**  
SourceA/Noetfield pages may describe sprint **deliverables** and **governance OS** as product vision; mark live vs roadmap; Tier-1 = diagnostic engagement name.

**Related:** Tier-1 audit · overclaim guard · reserved commercial figure

---

## Brain vs worker vs locked-definitions

**Meaning**  
- **Brain:** A rule-based system that makes exact decisions without using probabilistic guesses.  
- **Worker:** An LLM or coding agent that drafts or runs tasks under set safety checks.  
- **Locked-definitions:** A set of approved definitions used by the brain, which is a small part of the full dictionary.  

**Why**  
If we let LLMs define terms, their meaning will change over time. The dictionary defines system words, while locked-definitions defines our public claims.

**IS NOT**  
Loading FOUNDER_JUDGMENT_PATTERNS into workers (least-knowledge violation)

**Related:** soup vs raw · least-knowledge · layered-agents  
**Files:** `P6-BRAIN-MEANING/locked-definitions-v1.md`

---

## Drift · fail-closed · schedule home

**Meaning**  
- **Schedule home:** The file `data/noos-24-7-loops-v1.json` which stores the approved schedule. The live cron job must match this exactly.  
- **Drift:** Any difference between the registry schedule and the live cron job, code hash, route, or target count.  
- **Fail-closed:** A safety check that stops work or exits with an error if drift is found.  

**Why**  
Mismatched schedules in the past caused false status reports and unnecessary health alerts.

**Examples**  
- `verify_noos_loop_schedule_registry_v1.py` before CF deploy  
- Heartbeat L12 mismatches list  

**Related:** deploy-truth · loop · motor

---

## Tombstone · RETIRE · FIX

**Meaning**  
- **Tombstone:** Mark an item, loop, or term as dead in the registry so it is ignored.  
- **RETIRE (census):** A recommendation to remove a maintenance loop that has no active consumer, rather than fixing it.  
- **FIX (census):** A task to repair a loop that serves a guard or revenue consumer and verify it within its set interval.  

**Why**  
Fixing loops that have no real users wastes our maintenance budget.

**Examples**  
- factory_autorun RETIRE — superseded motor slot  
- workflow_audit FIX — GUARD consumer  

**Ledger:** `NOOS_LOOP_CENSUS_ROOTCAUSE_2026-07-06.md`

---

## Adding a new entry (template)

```
## Term name
**Meaning** (plain English — what it is)
**Why it exists** (reasoning — why this word, not a synonym)
**Wrong readings** (IS NOT — common misreads)
**Edge cases**
**Examples** (good vs bad)
**Conflict rule** (what wins on disagreement; link to SSOT / census / doctrine)
**Public rewrite** (if customer-facing: allowed phrasing · banned phrasing · plain-English substitute)
**Related**
**Doctrine / files**
```

Founder locks dictionary entry → bump dictionary version → **mint** terminology one-liner → update SSOT_INDEX → run terminology lint on affected surfaces.

---



---

## Living System · Stale · Body · Pulse · Homeostasis · Metabolism

**Living System**  
**Meaning** — A subsystem that passes the machine-checkable liveness rubric in `LIVING_SYSTEM_DOCTRINE` §8 within its declared window: scheduled pulse, membrane or external proof, mutation or valid `IDLE_NO_WORK`, no stale DRIFT, and fresh homeostasis drills when covered.  
**Why** — One axis replaces vibe checks; governance motion and commercial motion are judged separately but with the same rubric shape.  
**IS NOT** — “has cron jobs,” “agent said healthy,” or governance-alive while metabolism ladder is empty.  
**Conflict rule** — Doctrine §8 + `living_system_chain_validate_v1.py` beat prose and agent self-report.  
**Doctrine:** `P0-CORE/LIVING_SYSTEM_DOCTRINE_v1.1_LOCKED.md`

**Stale**  
**Meaning** — Fails any §8 rubric item within the subsystem window regardless of internal motion or narrative.  
**IS NOT** — “needs improvement,” “blocked,” or “waiting on founder” unless a stale-gate receipt names the blocker.  
**Conflict rule** — STALE is a verdict from receipts, not shame language.

**Body** — 24/7 loops, workers, queues, repos, endpoints that execute work. **IS NOT** proof of market life. Failure mode: churn with no external effect.  
**Pulse** — Scheduled triggers, crons, gates, reminders that fire the body. **IS NOT** proof of mutation; ritual pulse without change is still pulse, not life.  
**Homeostasis** — Sensor → diagnoser → healer → verifier → escalator for internal repair. **IS NOT** life assertion; healers must not touch sensors/ledgers (write-isolation).  
**Metabolism** — External reality entering: strangers, buyers, verifiers, membrane-crossing signals. **IS NOT** vendor spam inbound (membrane only, rung 2).

**Related:** receipt · IDLE_NO_WORK · deploy-truth · Commercial Pulse · liveness ladder  
**Doctrine:** §1 five components · §2 two circulatory systems · §4 unforgeable vital sign

---



## Liveness Ladder · Unforgeable Vital Sign · Commercial Pulse

**Liveness Ladder** — Seven rungs on the metabolism axis; each requires a stranger to spend something scarcer (credential → signal → provocation → objection → mutation → buyer → retention).  
**Doctrine:** `LIVING_SYSTEM_DOCTRINE` §3

**Unforgeable Vital Sign** — External provocation or membrane-crossing receipt; internal health signals may be forged (precedent `239c8b5`). Health workers report health; they never declare life.  
**Doctrine:** §4 · governed-autorun L4

**Commercial Pulse** — Metabolism lane cron loop: draft priced provocation → L5 approval → send → classify reply → mutation. First target = one stranger objection in 7 days, not revenue.  
**Doctrine:** §6 · `docs/commercial_pulse_loop_v0.1.md`

**Provocation Surface** — A priced Noetfield offer a named stranger can react to (yes/no/objection). Vendor spam inbound is not provocation.  
**IS NOT:** membrane-only (rung 2).

**Dispatchable Draft** — Queued provocation passing all seven machine checks (ICP, price, entity hygiene, CASL, links, approval metadata, window).  
**Verified by:** `commercial_pulse_dispatch_check_v1.py` only — never agent self-report.

**FOUNDER_IS_THE_STALE_GATE** — Receipt when 7d pass with dispatchable draft queued and zero founder-approved sends.  
**WORKER_IS_THE_STALE_GATE** — Receipt when 7d pass with zero dispatchable drafts produced.  
**MALFORMED_DRAFT** — Receipt when dispatch check fails; lists failed fields.

*v1.2 (2026-07-08) — W1 ladder + Commercial Pulse dictionary mint.*

*v1.1 (2026-07-08) — Living System axis dictionary seed for W1 terminology mint.*

*v1 (2026-07-06) — Initial dictionary seed: receipt family, census, motor/loop, commercial tone, deploy-truth, vendor-neutral, diagnostic/enforce split.*

*v1.3 (2026-07-22) — LIVE_LOCK AI Motor vs AI engine nesting; ops motor disambiguated from product AI Motor; A-Z batch mint.*
