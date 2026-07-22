# NOETFIELD_TERMINOLOGY_v1

**Wording authority · daily · mandatory · machine-enforceable · Tier 0**

Status: `v1.3-motor-engine-nesting` · Load on **every output** before any doctrine edit, receipt field, job spec, specialist brief, or customer-facing text.

Answers: **“What word do I write, right now?”** — one line per term.  
Meaning source: `NOETFIELD_DICTIONARY_v1.md` (terminology is **minted from** dictionary — never the reverse).  
Layer guide: `P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md`  
Enforcement: lint — synonym rewrite (§6) + banned register (§7).

---

## The one rule

Use the wording here. If the term is not here, **stop** — author or locate the **dictionary** entry first, mint the terminology line, then write. Never invent a private meaning in a prompt, receipt field, or page.

**Hard gate:** no new job, task, specialist, role, product page, contract clause, or receipt field without a dictionary entry (existing or newly versioned).

---

## §1 — Core system nouns

**Receipt** — A machine-readable record that proves what happened. It must have defined fields: who, model, cost, tokens, success, latency, time, and sink ack when applicable.  
IS NOT: a log line, chat “done,” or deploy log without live verify.  
EX: “Worker said PASS but no receipt → unverified.”

**Observation record** — A status snapshot with a schema and timestamp, such as a health check or census run. It does not contain full receipt fields.  
IS NOT: a substitute for proof receipt on customer or revenue claims.  
EX: “Fleet health pass is an observation record, not R≥1 proof.”

**Claim** — Any statement of success that does not have a structured receipt.  
IS NOT: a receipt.

**SSOT** — The single authoritative file or record when different copies disagree.  
IS NOT: the latest file open in the editor.

**Doctrine** — A locked and versioned operating rule that is not debated during a session.  
IS NOT: chat opinion or draft.

**Artifact** — A saved and versioned file or deliverable in the library.  
IS NOT: chat scratch.

**Library** — The approved set of rules, doctrine, and architecture files under `noetfield-library`.  
IS NOT: random notes folder.

**Lane** — A specific path for work or a provider that has clear rules.  
IS NOT: vague category.

**Kernel** — The core running system that other modules connect to.  
IS NOT: any script that runs once.

**Scheduler and executor** — Cloud scheduler + process runner that starts loops (CF cron, Railway). Ops sense of “motor.”  
IS NOT: the loop body; the product **AI Motor**.

**AI Motor** — Governed execution vehicle: intent/event → verified outcome under policy, engines, agents, tools, workflows, and human authority.  
IS NOT: an AI engine; a chatbot; unbounded autonomy.  
EX: one AI Motor, many AI engines inside.

**AI engine** — Intelligence power unit inside or beside an AI Motor (model, critic, classifier, retrieval, scorer, draft).  
IS NOT: the AI Motor; promotion authority; the whole product.  
EX: engines draft; Motor advances and verifies.

**Loop** — A recurring task that runs on a schedule with a set interval, cost cap, kill path, and a receipt for each run.  
IS NOT: unbounded “always-on,” Cursor session, or Mac launchd without scheduler/executor receipt.

**Reconciler** — The single component that resolves conflicts and decides the final state.  
IS NOT: any component that touches state.

---

## §2 — Governance & census

**Governed** — Having clear, enforceable rules such as limits, receipts, overrides, and stops.  
IS NOT: “responsible-sounding.”

**Deploy-truth** — The actual state of the live system checked on the public page or API.  
IS NOT: commit hash alone.

**Drift** — A mismatch between the approved files and the live running setup, such as in schedule, hash, route, or configuration.  
IS NOT: “we should improve someday.”

**Fail-closed** — Stopping the process or blocking a deployment if a check fails or proof is missing.  
IS NOT: warn and continue.

**Vendor-neutral** — Using no default AI provider and routing work based on receipts, which can be canceled.  
IS NOT: “agnostic” in customer text; not anti-vendor.

**Cost cap** — A strict limit where all work stops once the spending threshold is met.  
IS NOT: soft budget.

**Kill criteria** — Predefined conditions written before a pilot that will stop it if they are not met.  
IS NOT: post-hoc judgment.

**Escalation ladder** — A fixed sequence of levels used to handle issues in order.  
IS NOT: “use the biggest model when unsure.”

**Least-knowledge** — A security rule where an agent receives only the minimum data and access needed to perform its task.  
IS NOT: load entire library.

**GUARD** (census) — A loop or receipt that protects the system by verifying, probing, or auditing.  
IS NOT: META self-grooming.

**REVENUE** (census) — A loop or receipt that directly serves an external user to generate a lead, payment, or delivery.  
IS NOT: internal factory inbox drain.

**META** (census) — A loop or receipt that handles system self-maintenance without directly earning money.  
IS NOT: excuse for unbounded cost.

**NONE** (census) — A loop with no active consumer for over 14 days, which should be retired.  
IS NOT: “keep running just in case.”

**FIX / RETIRE** (census verdict) — A decision to repair a loop only if it has a GUARD or REVENUE consumer, and to retire it otherwise.  
EX: “workflow_audit FIX; inbox RETIRE.”

**R≥1** — The first receipt of payment received from an external user.  
IS NOT: internal test or founder self-pay.

---

## §3 — Roles

**Founder** — Sina, who only approves actions that cannot be reversed.  
**Architect** — A role that designs, reviews, and removes unneeded work instead of writing features.  
**Worker** — A role that implements and deploys changes but does not make decisions.  
**Brain** — A rule-based system that routes tasks instead of using probabilistic guesses.  
**Adversarial review** — A check where other systems or people try to find flaws in a plan.

---

## §4 — Doctrine shorthand

**Soup vs raw** — A contrast between probabilistic LLM outputs and exact rule-based layers.  
**Return-on-cognition** — A principle stating that the most effective action is often to remove unneeded work.  
**Targets vs blockers** — A principle where only real damage stops a task, while minor issues are improved in the next run.  
**Split-brain** — A condition where two live instances of a system both act as the authoritative source.  
**Tombstone** — A marker used to flag retired items so they are never used.  
**Zero-founder validation** — A process where the system verifies its own state without requiring the founder.  
**Receipt ladder** — A sequence of levels unlocked only by verified receipts.

---

## §5 — Commercial (public-safe)

**Selective** — Working with only a few partners chosen based on evidence to maintain high standards.  
**Commercial alignment** — The contract and business agreement under which partners operate.  
IS NOT: “free API” ask.

**Governed reference environment** — A verifiable, receipt-backed setup that partners can inspect.  
IS NOT: unprovable “client base.”

**Structured commercial participation** — A terms-of-revenue agreement that remains confidential.  
**Design partner** — A partner in a limited early trial rather than a fully committed customer.  
**NDA** — A confidentiality agreement signed before sharing metrics, volume, or internal design.  
**Reserved commercial figure** — A confidential contract detail that is never made public.  
**Diagnostic** — An engagement focused on auditing and assessment rather than active blocking.  
IS NOT: “firewall deployed” unless customer receipt proves it.

---

## §6 — Synonym → canonical

```
agnostic / model-agnostic     → vendor-neutral
free API (as ask)             → commercial alignment
client base (unprovable)      → governed reference environment
log / it worked               → receipt (if fielded) else claim
the latest file               → SSOT
always-on / full auto 24/7    → governed loop + scheduler/executor + receipt (or say what is NOT 24/7)
alive / living (generic)        → Living System (§8 receipt) or name homeostasis vs metabolism axis
governed (decorative)           → governed (only if stoppable + measured)
24/7 (marketing)              → name the scheduler/executor + receipt or downgrade claim
AI engine (as whole product)  → AI Motor + AI engines inside
engine (when meaning the vehicle) → AI Motor
Motor (ops/fleet/census only) → Scheduler and executor
Plus One                      → Scheduler and executor
```

---

## §7 — Banned register

Never emit: `we need` · `desperate` · `revolutionary` · `game-changing` · `next-gen` · public `%` economics · unprovable customer roster · needy tone.

Customer tone: plain institutional English; state what we do; cut overclaim.

---

---

## §9 — RC2 gap fill (minted from dictionary supplement 2026-07-07)

**Inbox** — The outbound revenue queue head; RUN INBOX / sa-1200 dispatch lane.  
IS NOT: Brain reasoning backlog or form PICK list.

**Proof Lab** — WitnessBC appointment-only local demo surface for proof capture.  
IS NOT: public self-serve demo without founder arm.

**Creed** — Locked identity and operating vocabulary spine.  
IS NOT: chat shorthand or ad-hoc agent vocabulary.

**Proof Layer** — Receipt and verification stratum above execution; claims cannot skip it.  
IS NOT: diagram-only assurance.

**Unify** — Brain-side gather and routing pass that collapses forks without losing items.  
IS NOT: manual copy-paste between chats.

**Witness AI** — AI-assisted witness naming lane for proof lab assets.  
IS NOT: a public product SKU claim.

**Trust Ledger** — Structured trust and send log for outreach and commercial motion.

**Prompt OS** — Internal prompt routing and template system.  
IS NOT: customer-facing product name.

**Plus One** — Retired motor nickname; use **Scheduler and executor** in new text.

**RT LIVE** — Hub repair path proven live with structured receipt before Phase 3–10 resume.

**Worker Hub** — Legacy Worker URL hub tab; fade per E2E registry when drain complete.

**Trust Center** — Public trust narrative surface; claims require receipt ladder.

**Governance Platform** — Enterprise control-plane SKU narrative.  
IS NOT: generic “AI platform.”




## §10 — Living System axis (minted from dictionary 2026-07-07)

**Living System** — A subsystem that passes doctrine §8 within its window: scheduled pulse, external or membrane proof, mutation or valid `IDLE_NO_WORK`, no stale DRIFT, fresh drills when covered.  
IS NOT: cron exists, agent healthy, or governance-alive while metabolism rung < 3.  
EX: “Homeostasis PASS + metabolism STALE = healthy corpse.”

**Stale** — Fails any §8 rubric item in-window; verdict from receipts, not narrative.  
IS NOT: blocked, waiting, or needs polish without a receipt.

**Body** — 24/7 loops, workers, queues, repos, endpoints (the execution substrate).  
IS NOT: proof the business is alive.

**Pulse** — Crons, triggers, gates, schedulers that fire the body on schedule.  
IS NOT: proof of mutation; manual green ≠ cron green.

**Homeostasis** — Internal sensor → diagnoser → healer → verifier → escalator repair lane.  
IS NOT: life declaration; healer touching sensor/ledger is forbidden.

**Receipt** (fifth component) — see §1; disk/live proof of change or recovery. Weak if internal-only.

**Metabolism** — External market input: strangers, buyers, verifiers, membrane-crossing receipts.  
IS NOT: vendor spam inbound (membrane/rung 2 only).

```
governance-alive / internally healthy  → homeostasis axis (may be LIVING per §8)
commercially alive / market proof      → metabolism ladder rung ≥ 3
alive (generic)                        → name the axis or downgrade to claim
```
**Liveness Ladder** — Metabolism axis rungs 1–7; each rung needs a scarcer stranger cost-of-touch receipt.  
IS NOT: internal motion or governance receipts.

**Unforgeable Vital Sign** — Membrane-crossing or L4 external proof; only basis for asserting life.  
IS NOT: cron PASS, agent healthy, or internal heal receipt.

**Commercial Pulse** — Metabolism lane: draft → L5 approve → send → classify → mutate. Target = objection in 7d.  
IS NOT: revenue target on day one.

**Provocation Surface** — Priced offer a named stranger evaluates.  
IS NOT: vendor inbound spam (rung 2 only).

**Dispatchable Draft** — Queue row passing all seven dispatch predicates.  
IS NOT: agent claim of ready-to-send.

**FOUNDER_IS_THE_STALE_GATE** — Stale-gate receipt: dispatchable queued, zero sends 7d.  
**WORKER_IS_THE_STALE_GATE** — Stale-gate receipt: zero dispatchable drafts 7d.  
**MALFORMED_DRAFT** — Dispatch check failure receipt with failed fields.


## §11 — Founder reasoning motor + tier disambiguation (minted 2026-07-10)

**FOUNDER_REASONING_PACKET** — Structured escalation bundle sent to founder; includes problem, evidence, cheap-route failures, exact question, options, verification contract, and return instruction.  
IS NOT: a chat dump or bare `HANDOFF_REQUIRED`.  
EX: `packet_id=frp-20260710-001` attached to `WAITING_FOR_FOUNDER_REASONING`.

**FOUNDER_REASONING_QUEUE** — Integrator queue stage; holds packets; does **not** invoke expensive models.  
IS NOT: automatic premium API worker.

**WAITING_FOR_FOUNDER_REASONING** — Job state: dependent branch parked until `reasoning_result` ingested for `packet_id`.  
IS NOT: global motor stop.

**RESULT_INGESTION** — Motor stage validating and applying founder `reasoning_result` schema, then resuming automatic execution.  
IS NOT: manual workflow restart by founder.

**W-DET** — Deterministic work lane (no model).  
**W-INTEL-LOW** — Low-cost intel lane (COST-T1 class).  
**W-INTEL-BOUNDED** — Bounded API intel lane (COST-T2 class; capped bindings only).

**COST-T0 / COST-T1 / COST-T2** — Motor cost execution tiers (P10).  
IS NOT: `MERGE-T*` or `EXEC-T*`.

**MERGE-T0 … MERGE-T3** — Merge authority tiers (P8); govern what may machine-merge vs founder-only.  
IS NOT: motor cost or executor routing tiers.

**EXEC-T0 … EXEC-T3** — Executor routing tiers (NOOS ROUTING_MATRIX); GHA / Copilot / Cursor / Codex.  
IS NOT: merge authority or motor cost tiers.

**HANDOFF_REQUIRED** — **Deprecated as terminal state.** Valid only with `packet_id` + queue stage; otherwise use `WAITING_FOR_FOUNDER_REASONING` or `FOUNDER_REASONING_QUEUE`.  
IS NOT: permission to stop the motor without continuation contract.

**SKIPPED_LLM** — Receipt reason: LLM layer skipped; deterministic path completed.  
**LLM_PROVIDER_NOT_CONFIGURED** — Receipt reason: no approved provider binding; motor continues deterministically or queues.

**PARTIAL** — Receipt quality: deterministic layer complete; LLM layer failed or absent.  
IS NOT: loop hard-fail for deterministic-only loops.

**Premium API automation** — Standing worker that auto-invokes expensive models.  
IS NOT: founder subscription reasoning console.

**Subscription-based founder reasoning** — Founder resolves heavy reasoning in paid subscription surfaces; result ingested once.  
IS NOT: motor auto-spend on premium API.


## §12 — Advisor-package harmonization (minted 2026-07-10)

Absorbed from `FOUNDER_CONTINUATION_MOTOR_LOCKED_PACKAGE_v1` (advisor input) **into custody layers** — not as flat SSOT.  
**Canonical receipts use the right column.** Left column is deprecated alias unless noted.

### Cost execution classes

| Advisor alias | Canonical (receipts) | Lane |
|---|---|---|
| `C0` / deterministic class | `COST-T0` | `W-DET` family |
| `C1` / free or near-free callable | `COST-T1` | `W-INTEL-LOW` |
| `C2` / bounded low-cost callable | `COST-T2` | `W-INTEL-BOUNDED` |
| `C3` / founder-operated reasoning | `FOUNDER_REASONING_QUEUE` | not a cost tier — queue stage |

Bare `C0`–`C3` or bare `T0`–`T3` in motor receipts: **forbidden**.

### Worker class aliases

| Advisor worker class | Canonical lane | COST class |
|---|---|---|
| `W-DET-EXEC` | `W-DET` | `COST-T0` |
| `W-DET-PATCH` | `W-DET` | `COST-T0` |
| `W-INTEL-FREE` | `W-INTEL-LOW` | `COST-T1` |
| `W-INTEL-LOW` | `W-INTEL-LOW` | `COST-T1` (may bind COST-T2 caps) |
| `W-INTEL-BOUNDED` | `W-INTEL-BOUNDED` | `COST-T2` |
| `W-HANDOFF` | `FOUNDER_REASONING_QUEUE` | handoff mode — not callable intel |
| `W-VERIFY-RECOMPUTE` | verification plane | not motor cost tier |
| `W-VERIFY-CI` | verification plane | not motor cost tier |
| `W-VERIFY-EDGE` | verification plane | Level-3 independent (P8 commissioning) |

### Job / heading state aliases

| Advisor alias | Canonical |
|---|---|
| `REASONING_WAIT` | `WAITING_FOR_FOUNDER_REASONING` |
| `reasoning_wait` | `WAITING_FOR_FOUNDER_REASONING` |
| `reasoning_result_received` | `RESULT_INGESTION` (stage) then job `ready` |
| `handoff_required` (terminal) | **invalid** — use queue + `packet_id` |
| `THROTTLED` | budget exhaustion; reroute or `FOUNDER_REASONING_QUEUE` |

### Schema field aliases (NOOS JSON)

| Advisor / informal | Canonical schema field |
|---|---|
| `selected_action` | `chosen_action` |
| `proposed_patch` | `proposed_change` |
| `verification_steps` | `verification_requirements` |
| `founder_authorization` | `founder_authority_statement` |

Schemas: `noetfeld-OS/noetfield-org/schemas/` (see `SCHEMA_INDEX_v1.md`).

### Design vs commissioning status

| Status | Meaning |
|---|---|
| `DESIGN_LOCKED` | Custody + library + NOOS binding ratified |
| `IMPLEMENTATION_IN_PROGRESS` | Components building; schemas wired |
| `PARTIALLY_COMMISSIONED` | Some proof runs pass |
| `FULLY_COMMISSIONED` | P8 acceptance standard cold proofs A+B |
| `NOT_OPERATIONAL` | No runtime claim permitted |

`DESIGN_LOCKED` never implies `FULLY_COMMISSIONED`.



## §13 — AI Motor / AI engine nesting (minted 2026-07-22 · LIVE_LOCKED)

Minted from `NOETFIELD_DICTIONARY_v1.md` + A-Z batch. Long-form story: `NOETFIELD_MOTOR_ENGINE_VOCABULARY_v1.md`.

**Nesting law** — One AI Motor. Many AI engines. Not synonyms.  
**Architecture** — Deterministic Motor + bounded AI engines + human decision authority.  
**Public line** — Engines think and draft. Motors operate. Models generate. Agents participate.

**Runway** — Productized path that delivers a qualified outcome on a shared AI Motor.  
IS NOT: raw chat; one-off prompt.


## §8 — Versioning

Terminology rows are **minted from** dictionary entries — never authored standalone.

Add/change: dictionary entry first (founder lock) → mint or update terminology line here → bump `NOETFIELD_TERMINOLOGY_v1` version in same change set.  
This file beats prompt shorthand and model habit on **word choice**; dictionary beats this file on **meaning**.
