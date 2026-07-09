# NOETFIELD_DICTIONARY_BATCH_A-Z_v1

**Meaning authority source** — plain English canonical terms. Old jargon lives under `Aliases retired`.
Terminology rows are **minted from** this file. Rebuild index: `python3 language_gate/build_dictionary_index.py`.

---

**Scheduler and executor** — CANONICAL
Meaning: The cloud scheduler and the process runner that start loops on a timer.
In our system: Cloudflare cron dispatches to the Railway loop runner.
Is NOT: The loop body itself or a one-off script.
Example: CF `*/5` cron fires; Railway runs the loop handler.
Aliases retired: Motor, motor
Public phrasing: scheduled cloud runner
Allowed surfaces: internal, receipt, prompt
Code alias: motor, noos-loop-fleet-tick-v1

---

**Need-to-know access** — CANONICAL
Meaning: Give an agent only the data and permissions required for its task.
In our system: Tier 0–2 law routing; workers never load founder judgment patterns.
Is NOT: Load the whole library so the agent can figure it out.
Example: Inbox worker sees queue rows, not contract drafts.
Aliases retired: Least-knowledge, least-knowledge, least privilege
Public phrasing: minimum access required for the task
Allowed surfaces: internal, contract, prompt

---

**Confidential commercial terms** — CANONICAL
Meaning: Revenue-share or routing percentages spoken only under NDA and in signed contracts.
In our system: Contract `[●]` variable only; never public copy.
Is NOT: A percentage on a website or first-call slide.
Example: NDA deck may discuss structure; public pages omit numbers.
Aliases retired: Reserved commercial figure, reserved commercial figure, the percentage
Public phrasing: confidential commercial terms (under NDA)
Allowed surfaces: contract
Banned surfaces: website, public, prompt

---

**model-agnostic** — ALIAS RETIRED
Meaning: Retired wording. Use canonical term: vendor-neutral.
Aliases retired: model-agnostic
Conflict rule: Auto-rewrite to vendor-neutral per terminology §6.

---

**agnostic** — ALIAS RETIRED
Meaning: Retired wording. Use canonical term: vendor-neutral.
Aliases retired: agnostic
Conflict rule: Auto-rewrite to vendor-neutral per terminology §6.

---

**client base** — ALIAS RETIRED
Meaning: Retired wording. Use canonical term: governed reference environment.
Aliases retired: client base
Conflict rule: Auto-rewrite to governed reference environment per terminology §6.

---

**Adversarial review**
Meaning: Merriam-Webster's "adversarial" — two sides set up to oppose each other on purpose, like a court's defense vs. prosecution. Applied here: one checker's job is to oppose the work, not agree with it.
Is NOT: checking your own work · a quick "looks fine" · hostility for its own sake
Example: the critique loop's checker attacks the work before it ships; checker is never the same system as the maker
Public phrasing: "checked by a separate reviewer whose job is to look for weaknesses before release"

---

**Agentic cost governance**
Meaning: IBM's "agentic AI" — software that plans and acts on its own, not just answers when asked — plus FinOps "cost governance" — real budgets and limits on spend, not just a bill you read after. Together: limits placed on AI that acts by itself, so it can't spend unchecked.
Is NOT: a spending report you read after the money's gone · "we use AI responsibly" with no budget attached · a dashboard with no power to stop anything
Example: Tier 1 "AI Spend Leak Audit" finds where autonomous AI spend has no cap, before selling any enforcement
Public phrasing: "spend controls for autonomous AI"

---

**Aggregator**
Meaning: standard software-pipeline role — collects multiple checkers' outputs and combines them into one verdict.
Is NOT: a single checker · a vote without a rule for ties
Example: IDE lane pipeline combines critic + verifier outputs before a merge decision
Public phrasing: "the step that combines the checks into one result"

---

**Anomaly detection**
Meaning: standard security/ops term — noticing when something departs from its normal pattern.
Is NOT: a person eyeballing a dashboard · a rule that only checks one fixed threshold
Example: Line Engine drops a line a gear, or to FROZEN, the moment it detects anomaly
Public phrasing: "automatic detection of unusual behavior"

---

**Anti-theater**
Meaning: built on the established term "security theater" (measures that look protective but do nothing) — the opposite discipline: never let a system perform safety without proving it.
Is NOT: skepticism for its own sake · disbelieving every receipt
Example: negative-proof doctrine — a gate isn't trusted until it's shown rejecting a bad input
Public phrasing: "we prove safety, not perform it" Related: child pattern under Pattern Factory.
Related: child pattern under Pattern Factory.

---

**Architect**
Meaning: Merriam-Webster — one who designs and reviews structure. Here: the role that designs, reviews, and cuts unneeded work, rather than writing features.
Is NOT: the person who ships code · the founder
Example: Architect locks a spec before a worker builds it
Public phrasing: "system designer"

---

**Artifact**
Meaning: standard software term ("build artifact") — a saved, versioned file a process produces.
Is NOT: chat scratch · an unsaved draft
Example: a signed release file in the library
Public phrasing: "a saved, versioned file"

---

**Audit loop**
Meaning: Merriam-Webster "audit" (an official examination) + "loop" (a repeating cycle) — a recurring, scheduled examination.
Is NOT: a one-time look · an internal opinion with no schedule
Example: `P8-MACHINE-LOOPS/audit-loop.md`, canon §5
Public phrasing: "scheduled audit"

---

**Auto-heal (zero-drift hospital policy)**
Meaning: a repair pattern that watches system health continuously and fixes known-safe breakages automatically, the way a hospital's standing protocols treat common conditions without waiting for a doctor's fresh judgment each time.
Is NOT: the same thing as Self-heal (that's the Line Engine's own bounded repair loop) · a fix for anything unknown or unsafe
Example: `P9-PATTERN-FACTORY/auto-heal-hospital.md`
Public phrasing: "automatic repair of known, safe issues" Related: child pattern under Pattern Factory, distinct from Self-heal (per founder ruling).
Related: child pattern under Pattern Factory, distinct from Self-heal (per founder ruling).

---

**Base model**
Meaning: AI-industry standard term — a pretrained model with no added "assistant" instruction-tuning or house style baked in.
Is NOT: a chat-tuned assistant model · "any small model"
Example: the brain runs on a base model specifically so it has no competing definitions of "done" or "verified"
Public phrasing: "an unmodified foundation model"

---

**Base model as first-class language**
Meaning: a base model has no pre-baked definitions of words like "done" or "verified," so our own definitions become its only meaning for those words, instead of competing with a prior meaning. In our system: this is why SSOT and the R1/R2/R6/R7 rules load before anything else — they're not policy sitting beside the model, they're the model's vocabulary.
In our system: this is why SSOT and the R1/R2/R6/R7 rules load before anything else — they're not policy sitting beside the model, they're the model's vocabulary.
Is NOT: true of assistant-tuned models (Cursor, GPT-assistant) — those already carry competing definitions, which is what causes compliance theater
Example: `P7-DOCTRINE/base-model-first-class-language.md`
Public phrasing: "we load our own definitions before the model forms any of its own"
Allowed surfaces: internal doctrine, architecture docs
Banned surfaces: customer-facing copy (too technical to be useful publicly)
Doctrine source file: `base-model-first-class-language.md` Public-safe rewrite: "we load our own definitions before the model forms any of its own"

---

**Behavior probe**
Meaning: from Kubernetes' standard "probe" pattern (liveness/readiness checks) — a check that verifies a system actually behaves correctly, not just that it deployed.
Is NOT: a deploy log · an uptime check with no behavior test
Example: Line Engine's mandatory pre-promotion behavior probe
Public phrasing: "a live behavior check before go-live"

---

**Blast-radius limit**
Meaning: standard SRE/security term — a cap on how much damage one failure can cause.
Is NOT: a general "be careful" guideline · unlimited scope with a warning label
Example: Line Engine's per-line blast-radius limits, checked every window
Public phrasing: "a limit on how much damage one failure can cause"

---

**Blueprint**
Meaning: Merriam-Webster — a detailed plan.
Is NOT: a vague idea · a finished product
Example: Line Engine blueprint registry
Public phrasing: "a detailed plan"

---

**Blueprint registry**
Meaning: Merriam-Webster "registry" (an official recorded list) applied to blueprints — a governed catalog of approved plans.
Is NOT: a folder of random files
Example: `P5-LINE-ENGINE/blueprint-registry.md`
Public phrasing: "a catalog of approved plans"

---

**Brain**
Meaning: our name for a rule-based system that routes and decides using fixed definitions, not guesses.
Is NOT: a chat assistant · a language model making its own judgment calls
Example: the brain classifies intent and picks a route from locked-definitions, never invents a new one
Public phrasing: "a rules-based decision system" — CODE_ALIAS: "Brain" is our product name for it; the plain description above is the real meaning.

---

**Brain audit**
Meaning: Merriam-Webster "audit" applied to a brain's rules — an examination of whether its decision rules are sound.
Is NOT: an audit of company finances
Example: `P9-PATTERN-FACTORY/brain-audit-v1.md`, Tier-1 sellable offer
Public phrasing: "an audit of your decision rules"

---

**Brain-as-a-service**
Meaning: built on the standard industry pattern "X-as-a-Service" (SaaS, PaaS) — the same rules-engine we run internally, offered as a delivered service.
Is NOT: a chatbot subscription
Example: `P9-PATTERN-FACTORY/brain-as-a-service.md`
Public phrasing: "operating brain, installed for you" Related: child pattern under Pattern Factory.
Related: child pattern under Pattern Factory.

---

**Circuit breaker**
Meaning: standard software-resilience term (the "circuit breaker pattern") — stop calling a failing dependency automatically instead of hammering it.
Is NOT: a manual off switch · a retry loop with no stop condition
Example: capability router's circuit breaker
Public phrasing: "automatic stop on repeated failure"

---

**Claim**
Meaning: Merriam-Webster — a statement asserting something is true.
Is NOT: a receipt
Example: "Worker said PASS" with no receipt is a claim, not proof
Public phrasing: "an unverified statement" (when no receipt backs it)

---

**Commercial alignment**
Meaning: Merriam-Webster "alignment" (agreement in position) applied to business — the contract terms partners actually operate under.
Is NOT: a free-access request
Example: terminology v1 §5
Public phrasing: "our commercial terms"

---

**Contracts run the system**
Meaning: a fixed, structured plan format (the Execution Contract) — not the language model — decides what's allowed to run, what output counts as valid, and what it costs. In our system: the model only proposes a plan; it never has authority to execute anything the contract hasn't approved.
In our system: the model only proposes a plan; it never has authority to execute anything the contract hasn't approved.
Is NOT: "the model is in charge" · "we trust the model's judgment at runtime"
Example: `P7-DOCTRINE/contracts-run-the-system.md`
Public phrasing: "a fixed set of rules decides what runs — not the AI itself"
Allowed surfaces: architecture docs, technical customer diligence
Banned surfaces: casual marketing copy (too technical to land as a soundbite)
Doctrine source file: `contracts-run-the-system.md` Public-safe rewrite: "a fixed set of rules decides what runs — not the AI itself"

---

**Cost cap**
Meaning: Merriam-Webster "cap" — a fixed upper limit. All work stops once it's hit.
Is NOT: a soft budget guideline
Example: terminology v1 §2
Public phrasing: "a hard spending limit"

---

**Critic**
Meaning: standard agentic-AI pipeline role — a component whose only job is to find problems in another component's output.
Is NOT: the producer reviewing itself
Example: `adversarial_critic_receipt_v1.py`
Public phrasing: "an independent checker"

---

**Critique loop**
Meaning: Merriam-Webster "critique" (a critical evaluation) + "loop" — a recurring, scheduled critical evaluation.
Is NOT: a one-off comment
Example: `P8-MACHINE-LOOPS/critique-loop.md`, canon §3
Public phrasing: "scheduled critical review"

---

**Deploy-truth**
Meaning: the real, live state of the system, checked directly (an HTTP response, a live page, a database row), not what a commit message or log claims.
Is NOT: "git push succeeded" · a deploy log
Example: CF health check showing 14 live targets vs. 7 in the repo = drift caught by deploy-truth
Public phrasing: "verified live status, not just a deploy log"

---

**Design partner**
Meaning: standard startup/enterprise-sales term — an early customer who tests a product in exchange for shaping it, before it's a finished sale.
Is NOT: a fully committed paying customer
Example: terminology v1 §5
Public phrasing: "design partner"

---

**Diagnostic**
Meaning: Merriam-Webster — relating to identifying a problem, not fixing or blocking it.
Is NOT: "firewall deployed" (that's enforcement) unless a customer receipt proves it
Example: Tier 1 "AI Spend Leak Audit" is diagnostic; Tier 3 "Firewall Pilot" is enforcement
Public phrasing: "diagnostic engagement"

---

**Doctrine**
Meaning: Merriam-Webster — a settled principle or rule. Here: a locked operating rule not re-argued each session.
Is NOT: a chat opinion · a draft idea
Example: `P7-DOCTRINE/`
Public phrasing: "our operating rules"

---

**Drift**
Meaning: standard DevOps term "configuration drift" — the live system no longer matching its approved definition.
Is NOT: "we should improve this someday"
Example: a cron schedule that no longer matches the approved registry file
Public phrasing: "mismatch between what's approved and what's actually running"

---

**Enforce**
Meaning: Merriam-Webster — to compel compliance, actively.
Is NOT: describing a policy without applying it
Example: pairs with Diagnostic — enforcement requires proof of live installation
Public phrasing: "actively blocking, not just checking"

---

**Escalation ladder**
Meaning: standard incident-management term — a fixed sequence of steps for handling a problem, in order.
Is NOT: "use the biggest model when unsure"
Example: terminology v1 §2
Public phrasing: "a fixed escalation sequence"

---

**Execution contract**
Meaning: standard software/legal term (a binding, structured agreement on what may run) — the fixed schema that decides what a plan is allowed to do before it runs.
Is NOT: a suggestion the model can reinterpret
Example: `P5-LINE-ENGINE/execution-contract-as-brain.md`
Public phrasing: "a fixed rulebook that decides what's allowed to run"

---

**Fail-closed**
Meaning: standard security-engineering term — when a check fails, the system stops, rather than continuing.
Is NOT: warn-and-continue
Example: terminology v1 §2
Public phrasing: "stops on failure, doesn't continue anyway"

---

**FIX / RETIRE**
Meaning: fixed labels in the workflow census: FIX = repair a loop that serves a real user; RETIRE = shut down a loop with no real user.
Is NOT: a judgment call made loosely
Example: "workflow_audit FIX; inbox RETIRE"
Public phrasing: not public-facing (internal ops label)

---

**Founder**
Meaning: Merriam-Webster — the person who starts and holds ultimate authority over an organization. Here: Sina, who approves only irreversible actions.
Is NOT: a manager · an approver of everyday changes
Example: terminology v1 §3
Public phrasing: "founder"

---

**Founder intent filter**
Meaning: our own test applied to any proposed rule or process — does it actually serve what the founder is trying to do, or just add process for its own sake.
Is NOT: a rubber-stamp · a vote
Example: `P7-DOCTRINE/founder-intent-filter.md`
Public phrasing: not public-facing (internal review step)

---

**Governed**
Meaning: Merriam-Webster "govern" (to control by rule) — a process the system can stop, measure, and override without asking the agent running it.
Is NOT: "we use AI responsibly" with no actual stop mechanism
Example: a loop with a cost cap, kill switch, and a receipt on every run
Public phrasing: "governed" only if it's actually stoppable and measured — otherwise, downgrade the claim

---

**Governed reference environment**
Meaning: a real, inspectable, receipt-backed setup a partner can check directly, instead of a claimed customer list.
Is NOT: a logo wall · an unprovable "500+ clients" claim
Example: terminology v1 §5
Public phrasing: "governed reference environment"

---

**Hub**
Meaning: Merriam-Webster — a central point that other things connect to. Here: the founder's control plane — spawns, pauses, and kills lines; approves only irreversible actions.
Is NOT: a place that executes work itself
Example: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.1.md` §2
Public phrasing: "founder control panel"

---

**Immutable floor**
Meaning: Merriam-Webster "immutable" (unchangeable) + "floor" (a lower limit) — the safety rules (verifier, kill-switch, gates) that a self-improving system is never allowed to weaken from the inside.
Is NOT: a suggestion the system can optimize away · a rule the loop can edit if it decides to
Example: any change touching a floor path auto-fails and freezes the line — founder-only, out of band
Public phrasing: "the safety rules the system can never weaken on its own"

---

**Kernel**
Meaning: standard computer-science term — the core of a system that everything else runs on top of.
Is NOT: a script that runs once
Example: terminology v1 §1
Public phrasing: "the core system"

---

**Kill criteria**
Meaning: standard product/pilot-management term — the conditions, written down before a pilot starts, that will stop it if unmet.
Is NOT: a judgment made after the fact
Example: terminology v1 §2
Public phrasing: "pre-agreed stop conditions"

---

**Kill switch**
Meaning: standard safety-engineering term — a mechanism that stops a system immediately.
Is NOT: a slow manual shutdown process
Example: the substrate's global kill-switch
Public phrasing: "an immediate stop mechanism"

---

**Lane**
Meaning: Merriam-Webster "lane" (a defined path) — a repo-scoped workstream with its own rules.
Is NOT: a vague category · the same thing as "Line" (see Line — different concept, cross-referenced)
Example: the IDE Lane work order, scoped to one repo
Public phrasing: "a scoped work path"

---

**Layered agents**
Meaning: built on the standard computer-science term "layered architecture" — each agent knows only its own layer and task, not the whole system.
Is NOT: every agent reading every rule
Example: `P7-DOCTRINE/layered-agents.md`, L0–L5 map
Public phrasing: "each part of the system only knows its own job"

---

**Library**
Meaning: Merriam-Webster + standard software term ("code library") — an approved, organized collection.
Is NOT: a random notes folder
Example: `noetfield-library`
Public phrasing: "our approved library"

---

**Line**
Meaning: built on the standard business term "production line" — one full-stack instance (plan → produce → verify → ship → measure), replicated per revenue vertical.
Is NOT: the same thing as "Lane" (a repo workstream — different concept, cross-referenced)
Example: distribution line, factory line, TrustField line
Public phrasing: "a production pipeline"

---

**Live status signal**
Meaning: plain-English combination — a signal read directly from the running system right now, not from a file.
Is NOT: a status a file claims
Example: motor/loop health check reads receipts newer than twice the loop interval
Public phrasing: "live status, checked directly"

---

**Locked-definitions**
Meaning: our own file of approved definitions the brain is allowed to use — a small subset of the full dictionary.
Is NOT: the full dictionary loaded into every worker
Example: `P6-BRAIN-MEANING/locked-definitions-v1.md`
Public phrasing: not public-facing (internal architecture term)

---

**Loop**
Meaning: Merriam-Webster + standard software term ("control loop") — a recurring task on a schedule, with a cost cap, a kill path, and a receipt per run.
Is NOT: unbounded "always-on" · a Cursor session left open
Example: terminology v1 §1
Public phrasing: "a scheduled, capped recurring task"

---

**Mechanical, not prose**
Meaning: a safety rule only counts if a machine enforces it (a hook, a CI check, code) — not if it's just written instructions an agent is asked to follow. In our system: the test is "can an agent satisfy this by producing text, without the real condition being true?" If yes, it's prose and must be rewritten as code.
In our system: the test is "can an agent satisfy this by producing text, without the real condition being true?" If yes, it's prose and must be rewritten as code.
Is NOT: "we documented the rule clearly" · a policy an agent is trusted to self-apply
Example: `P7-DOCTRINE/mechanical-not-prose.md` — the `.agent-policy/` directory is hook-rejected on every agent lane
Public phrasing: "our safety rules are enforced by code, not just written down"
Allowed surfaces: technical diligence, architecture docs
Banned surfaces: none — safe to say publicly in plain form
Doctrine source file: `mechanical-not-prose.md` Public-safe rewrite: "our safety rules are enforced by code, not just written down"

---

**Merge authority**
Meaning: standard software/git-review term — the permission level required before a change can be merged.
Is NOT: one blanket permission for all changes
Example: `P8-MACHINE-LOOPS/merge-authority-tiers-T0-T3.md` — T0 docs/tests merge by machine, T3 schema/gates require the founder
Public phrasing: "graduated approval, based on risk" `CODE_ALIAS`: the T0–T3 tier labels themselves are literal gate names in code.

---

**NDA**
Meaning: standard legal term — Non-Disclosure Agreement, a confidentiality contract signed before sharing sensitive information.
Is NOT: a verbal understanding
Example: terminology v1 §5
Public phrasing: "NDA"

---

**Negative proof**
Meaning: built on the standard QA term "negative testing" (proving a system correctly rejects bad input) — a gate is only proven by showing it reject something it should reject, not by a description claiming it works.
Is NOT: prose asserting a gate works · a gate that has only ever seen passing input
Example: `P7-DOCTRINE/negative-proof.md` — a deliberately-failing test commit the gate must reject, captured as a receipt
Public phrasing: "we prove our checks by testing what they correctly reject"

---

**Observation record**
Meaning: Merriam-Webster "observation" (a noted, factual account) + "record" — a timestamped status snapshot, not full proof of payment or outcome.
Is NOT: R≥1 proof · a substitute for a receipt on revenue claims
Example: a fleet health pass
Public phrasing: "a status snapshot"

---

**Pattern Factory**
Meaning: our own name for the parent thesis — every repeatable pattern the system runs on: healing, improvement, commercial, cost, buyer-signal, workflow-failure, or any other repeatable world/system pattern.
Is NOT: the same thing as any one of its child patterns (Self-heal, Auto-heal, Signal Factory, Anti-theater, Brain-as-a-service are children, not the whole)
Example: `P9-PATTERN-FACTORY/pattern-factory-index.md`
Public phrasing: "our pattern library"

---

**Plan contract**
Meaning: our own name for the fixed schema an LLM's output must follow before it can run — the only shape a plan is allowed to take.
Is NOT: free-form model output
Example: `P5-LINE-ENGINE/execution-contract-as-brain.md`
Public phrasing: not public-facing (internal schema term)

---

**Planner**
Meaning: standard agentic-AI pipeline role — breaks a goal into an ordered set of steps.
Is NOT: the component that executes the steps
Example: understanding → planner → router → workers pipeline
Public phrasing: "the step that breaks a goal into an ordered plan"

---

**Reconciler**
Meaning: standard distributed-systems term (the Kubernetes "reconciliation" pattern) — the one component that resolves conflicts and decides the final state.
Is NOT: any component that merely touches state
Example: terminology v1 §1
Public phrasing: "the component that resolves conflicts"

---

**Repair loop**
Meaning: Merriam-Webster "repair" + "loop" — a recurring, scheduled fix cycle.
Is NOT: a one-time manual fix
Example: `P8-MACHINE-LOOPS/repair-loop.md`, canon §4
Public phrasing: "scheduled repair cycle"

---

**Research loop**
Meaning: Merriam-Webster "research" + "loop" — a recurring, scheduled research cycle.
Is NOT: a one-off search
Example: `P8-MACHINE-LOOPS/research-loop.md`, canon §6
Public phrasing: "scheduled research cycle"

---

**Research station**
Meaning: our own name for a producer role that gathers outside information (e.g. via Perplexity or computer-use) to feed a line.
Is NOT: the AI Stations (specialist producer roles that create content, not gather it — a related but separate role)
Example: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.2_HARDENED.md` §5.1
Public phrasing: not public-facing (internal role name)

---

**Return-on-cognition**
Meaning: our own term modeled on the standard business metric "return on investment" — applied to thinking/work instead of money: is this the highest-value use of effort right now, or should it be removed.
Is NOT: "we're always busy" as a justification
Example: `P7-DOCTRINE/return-on-cognition.md`
Public phrasing: not public-facing (internal decision principle)

---

**ROI engine**
Meaning: standard business term "ROI" (return on investment) + "engine" (a processing system) — the component that ranks lines by real return.
Is NOT: a vanity metrics dashboard
Example: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.2_HARDENED.md` §7
Public phrasing: "the system that ranks by real return"

---

**Router**
Meaning: standard software term — a dispatcher that sends work to the right destination based on rules, not a decision-maker itself.
Is NOT: "the brain" · a component that makes judgment calls
Example: capability router + circuit breaker, reclassified explicitly as dispatcher not brain
Public phrasing: "the dispatcher"

---

**R≥1**
Meaning: our own shorthand — the first receipt of real payment from an external user.
Is NOT: an internal test transaction · founder self-pay
Example: terminology v1 §2
Public phrasing: "first real revenue"

---

**Schedule home**
Meaning: our own name for the one approved file that stores the schedule every live cron job must match exactly.
Is NOT: any config file that happens to have a schedule in it
Example: `data/noos-24-7-loops-v1.json`
Public phrasing: not public-facing (internal file reference)

---

**Selective**
Meaning: Merriam-Webster — choosing carefully among options, working with only a few partners chosen on evidence.
Is NOT: snobbery · an unprovable "elite" claim
Example: terminology v1 §5
Public phrasing: "selective collaboration with model providers"

---

**Self-heal**
Meaning: our own name for the Line Engine's own bounded repair loop — fixes a line automatically, within a fixed scope, requiring real signal before improving anything.
Is NOT: the same thing as Auto-heal (that's the broader Pattern Factory hospital-policy pattern) · an unbounded ability to change anything
Example: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.2_HARDENED.md` §4.1
Public phrasing: "self-repair, within fixed limits"

---

**Signal factory**
Meaning: our own name for the applied skill that triages any raw inbound message into a fixed decision report — classification, need, four scores, one next action, a receipt.
Is NOT: the same thing as Pattern Factory (Signal Factory is one applied child pattern, not the parent thesis)
Example: `P9-PATTERN-FACTORY/signal-factory-v1.md` — implemented as the installed signal-factory skill
Public phrasing: not public-facing (internal triage tool)

---

**Soup vs raw**
Meaning: our own metaphor — "soup" = probabilistic model output carrying its own invented meaning; "raw" = a base model with no competing definitions, running on our fixed rules.
Is NOT: a claim that any model is bad
Example: `P7-DOCTRINE/deterministic-brain-doctrine.md` D-1/D-2
Public phrasing: not public-facing (internal architecture metaphor)

---

**Specialist**
Meaning: Merriam-Webster — someone or something scoped to one narrow task.
Is NOT: a general-purpose worker with no scope limit
Example: AI Stations, each an adversarial specialist role
Public phrasing: "specialist"

---

**Split-brain**
Meaning: standard distributed-systems term — two live instances of a system both acting as the authoritative source at once.
Is NOT: two backups, one of which is clearly inactive
Example: terminology v1 §4
Public phrasing: "two systems disagreeing about which one is authoritative"

---

**SSOT**
Meaning: standard data-governance term "single source of truth" — the one authoritative file or record when copies disagree.
Is NOT: the file that happens to be open right now
Example: `sina-governance-SSOT`
Public phrasing: "single source of truth"

---

**Structured commercial participation**
Meaning: a confidential business arrangement broader than a simple revenue-share — covers any structured commercial term (not only revenue splits) that stays private between the parties.
Is NOT: only a revenue-sharing agreement · public pricing
Example: terminology v1 §5
Public phrasing: not public-facing, ever, in specific form `[NEEDS ARCHITECT]`: exact boundary of "broader than revenue share" not yet spelled out in any doc — flagging for a sharper definition when one is written.

---

**Substrate**
Meaning: Merriam-Webster (an underlying layer) + standard tech usage ("compute substrate") — the shared safety floor every line stands on.
Is NOT: a line itself · something a line can bypass
Example: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.1.md` §3
Public phrasing: "the shared safety layer"

---

**Tap-only principle**
Meaning: our own name for the rule that the Hub can only trigger irreversible actions manually (a tap), never run them automatically.
Is NOT: full automation of irreversible actions
Example: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.1.md` §5.2
Public phrasing: not public-facing (internal control-plane rule)

---

**Targets vs blockers**
Meaning: Merriam-Webster "target" (a goal) + standard project-management term "blocker" (something stopping work) — only real damage should stop work; smaller issues get improved next cycle, not used as an excuse to freeze.
Is NOT: an excuse to ignore real problems
Example: `P7-DOCTRINE/targets-vs-blockers.md`
Public phrasing: "we keep moving on targets, stop only for real blockers"

---

**Tier-1 / Tier-2 / Tier-3 audit**
Meaning: standard support-tiering pattern, applied to our own offers — Tier 1: AI Spend Leak Audit (diagnostic). Tier 2: Cost Policy Pack. Tier 3: Model Firewall Pilot (enforcement, receipt-gated).
Is NOT: interchangeable — Tier 3 enforcement claims require a customer receipt, per policy rule 4
Example: `P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`
Public phrasing: "Tier 1 / 2 / 3" as named above

---

**Tombstone**
Meaning: standard distributed-database term (Cassandra and similar systems mark deleted rows with a "tombstone") — a marker that flags an item as dead so it's never used again.
Is NOT: simply deleting a file with no record
Example: terminology v1 §4
Public phrasing: "marked retired"

---

**TrustField**
Meaning: Separate venture for regulated financial workflows (Canada). Name reserved with BC Registries — not incorporated, not filed. Noetfield/SourceA may serve it; never a Noetfield product or subsidiary.
Doctrine source file: `P10-PRODUCT-LAYERS/trustfield.md`

---

**Validation loop**
Meaning: Merriam-Webster "validate" + "loop" — a recurring, scheduled correctness check.
Is NOT: a one-time test run
Example: `P8-MACHINE-LOOPS/validation-loop.md`, canon §2
Public phrasing: "scheduled validation"

---

**Vendor-neutral**
Meaning: standard business/tech term — using no default AI provider, routing work by receipts, cancelable at any time.
Is NOT: "agnostic" in customer-facing text · a refusal to ever partner
Example: terminology v1 §2
Public phrasing: "vendor-neutral"

---

**Verifier**
Meaning: Merriam-Webster "verify" + standard agentic-AI pipeline role — an independent component that checks correctness, separate from the one that produced the work.
Is NOT: the producer checking itself
Example: substrate's independent verifier
Public phrasing: "independent verifier"

---

**Worker**
Meaning: Merriam-Webster — one who performs a task. Here: an LLM or coding agent that drafts or runs bounded work, without deciding strategy.
Is NOT: a decision-maker · the architect
Example: terminology v1 §3
Public phrasing: "worker"

---

**Zero-drift-of-meaning**
Meaning: our own name for keeping the language of the system stable over time — connects directly to Drift, applied specifically to what words mean instead of what code runs.
Is NOT: the same as system-health drift (Auto-heal handles that) — this is about language specifically
Example: `P9-PATTERN-FACTORY/zero-drift-target.md`
Public phrasing: "we keep our language consistent over time" Related: child pattern under Pattern Factory.
Related: child pattern under Pattern Factory.

---

**Zero-founder validation**
Meaning: our own term — the system proves its own state with receipts, without needing the founder to manually confirm it.
Is NOT: the founder being cut out of irreversible decisions — those still require the founder
Example: `P1-CANON/MACHINE_LOOPS_v1.md`
Public phrasing: not public-facing (internal operating principle)

---
**Actions UI**
Meaning: GitHub Actions run UI — invalid external-verify path; building agent cannot treat "check Actions UI" as PASS.
Doctrine source file: `P0-FOUNDATION-SPINE/GOVERNED_AUTORUN_LAWS_v3.md`

---

**Agentic Cost Policy Pack**
Meaning: Tier-1 deliverable: policy templates and spend-guard recommendations from diagnostic engagement.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**AI Spend Leak Audit**
Meaning: Tier-1 diagnostic SKU: find autonomous AI spend paths with no cap, owner, or receipt.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Apply SG**
Meaning: Execute scoped change only in sina-governance-ssot — governance registry, gate, validators.
Doctrine source file: `AGENTS.md`

---

**Authority ID**
Meaning: Stable identifier for an authority document, role, or merge tier.
Doctrine source file: `P8-MACHINE-LOOPS/SOURCEA_E2E_CHECK_REGISTRY_LOCKED_v1.md`

---

**Authority Plane**
Meaning: Layer where merge authority, lane law, and irreversible founder gates are enforced.
Doctrine source file: `P99-LEDGER/V0.9_REPO_FRAGMENTATION_LEDGER_DRAFT_2026-07-04.md`

---

**Auto GUARD**
Meaning: Shorthand for census class GUARD — loop exists to verify, probe, or audit system integrity.
Doctrine source file: `data/workflow_census_value_class_rules_v1.json`

---

**Automation Cost Governance**
Meaning: FinOps discipline for automation spend: caps, receipts, and kill paths per loop.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Automation Factory**
Meaning: NOOS/GHA factory autorun lane — META census candidate; not revenue path.
Doctrine source file: `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`

---

**BaaS HOLD**
Meaning: Brain-as-a-Service tier gated: proof ladder milestone not met; do not sell as proven.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Base Brain**
Meaning: Minimal deterministic brain install — Tier 2 path after one SourceA pattern proof.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Base Live Brain**
Meaning: Production brain worker with live health endpoints; deploy-truth required before claims.
Doctrine source file: `P0-FOUNDATION-SPINE/P0-CORE/FOUNDER_JUDGMENT_PATTERNS_v1.md`

---

**Brain Agent**
Meaning: Runtime agent attached to deterministic brain — drafts and executes under gates; does not own meaning.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/deterministic-brain-doctrine.md`

---

**Brain Architecture**
Meaning: Structure: deterministic core, walled LLM workers, gates, receipts — not a single model.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Brain Audits**
Meaning: Diagnostic engagement family: drift, theater, and coherence review before Operating Brain Install.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-audit-v1.md`

---

**Brain Coherence Report**
Meaning: Tier-1 deliverable summarizing semantic and policy coherence findings — diagnostic only.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Brain Meaning**
Meaning: Approved public claims the brain may state — P6 scope, not full dictionary.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P6-BRAIN-MEANING/locked-definitions-v1.md`

---

**Brain OS**
Meaning: Informal name for full operating-brain stack; use locked SKUs in contracts.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Brain Registry Founding Instruction**
Meaning: Founder-locked bootstrap rules for brain registry — not default worker load.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P1-CANON/BRAIN_REGISTRY_LEARNING_GATE_v0.1.4.md`

---

**Brain Worker**
Meaning: Role that ships bounded change under gates — not the decider.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md`

---

**Build Phase A**
Meaning: Named milestone in phase-loop build plan — scoped delivery slice.
Doctrine source file: `SG-Canonical-Library/noetfield-library/PHASE_LOOP_BUILD_PLAN_v0.1.md`

---

**Build TrustField MVP**
Meaning: Stand up minimum TrustField product slice in trustfield-loops — separate from SourceA brain.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/trustfield.md`

---

**Canonical GTM**
Meaning: Approved go-to-market narrative tied to proof ladder and R≥1 — not ad-hoc pitch.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/UNLOCK_DOCTRINE_v2.md`

---

**Chat Unify**
Meaning: Canonical chat migration product (v4.9.9) — copy-first migration path.
Doctrine source file: `SourceA snapshot`

---

**Cloud Loop Specialist**
Meaning: Cloudflare motor cf_loop_specialist_tick_v1 for loop_specialist_runtime_plan.
Doctrine source file: `data/github_automation_registry_v1.json`

---

**Copilot QuickScan**
Meaning: GitHub Copilot assist-only quick scan lane — draft PRs, no autonomous merge.
Doctrine source file: `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`

---

**Copilot Readiness**
Meaning: Repo posture for Copilot assist_only workflows and PR template compliance.
Doctrine source file: `ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md`

---

**Create TrustField**
Meaning: Work item to open TrustField venture lane: entity hygiene, sandbox, regulated scope.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/trustfield.md`

---

**Data Graph**
Meaning: Factory mesh graph linking nodes, edges, and receipt consumers.
Doctrine source file: `P7-DOCTRINE/contracts-run-the-system.md`

---

**Decision Gate**
Meaning: Checkpoint requiring explicit PASS before next phase or promote.
Doctrine source file: `P1-CANON/BRAIN_REGISTRY_LEARNING_GATE_v0.1.4.md`

---

**Define TrustField MVP**
Meaning: Founder/doc step locking first TrustField MVP scope before build spend.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/trustfield.md`

---

**Disk Reconciliation**
Meaning: Align committed disk state with cloud kernel truth — fail-closed on drift.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md`

---

**Domain SSOTs**
Meaning: Per-domain authority files; on conflict the SSOT row wins.
Doctrine source file: `P0-FOUNDATION-SPINE/strategy-ssot-v6-split.md`

---

**Eval Registry**
Meaning: Registry of eval passes, promotion gates, and rollback posture.
Doctrine source file: `P1-CANON/BRAIN_REGISTRY_LEARNING_GATE_v0.1.4.md`

---

**Evolve FBE**
Meaning: Iterate SourceA factory/build executor — internal lane slug.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**Execution Contract Validator**
Meaning: E2E gate validating contract pages and execution paths against SSOT.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P8-MACHINE-LOOPS/SOURCEA_E2E_CHECK_REGISTRY_LOCKED_v1.md`

---

**Forge Factory**
Meaning: SourceA cloud forge automation surface — bounded build/deploy.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**Form UI**
Meaning: Meta-label in DLM triage for form option chrome (Nov Options, PICKs Options) — not system vocabulary.
Doctrine source file: `coined-internal: DLM`

---

**Founder Email Factory**
Meaning: Outbound email motion — founder-execute until stranger payment receipt.
Doctrine source file: `P99-LEDGER/gap-audit-2026-06-30.md`

---

**Founder Mail**
Meaning: Mail sent by founder from personal channel — not autonomous bulk.
Doctrine source file: `P99-LEDGER/SOURCEA_FORM_OFFICIAL_PARTIAL_SUBMIT_RECEIPT_2026-07-07.json`

---

**Four Canadian OSs**
Meaning: Strategic frame: four Canadian venture operating systems (Noetfield family).
Doctrine source file: `P0-FOUNDATION-SPINE/strategy-ssot-v6-split.md`

---

**Gateway Railway**
Meaning: Sina Gateway service hosted on Railway — health and deadman probe targets.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/SINA_GATEWAY_BLUEPRINT_LOCKED_v1.md`

---

**Grade-its-own-homework**
Meaning: Anti-pattern: deployer validates its own output without independent verify.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/negative-proof.md`

---

**Hardened Machine Workbench**
Meaning: Secured Mac operator environment for founder sessions.
Doctrine source file: `docs/MAC_CURSOR_OPS_v1.md`

---

**HOLD/LIFT**
Meaning: Autonomy posture: HOLD blocks promote; LIFT enables brain-only 24/7 autorun.
Doctrine source file: `docs/STEP10B_AUTONOMOUS_DEPLOY_DECIDE_v0.1.md`

---

**Hub UI**
Meaning: Founder hub interface for spawn, pause, and kill controls.
Doctrine source file: `P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.1.md`

---

**Integrator Control Panel**
Meaning: NOOS integrator control surface — separate venture workspace.
Doctrine source file: `P99-LEDGER/LANE_PREFLIGHT_RECEIPTS_2026-07-05/NOETFIELD_OS.md`

---

**INTEGRITY PACK**
Meaning: Bundled integrity checks and receipts for a lane preflight.
Doctrine source file: `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`

---

**LIBRARY MIRROR**
Meaning: Synced noetfield-library copy — not ad-hoc notes.
Doctrine source file: `P99-LEDGER/SSOT_V6_AUTHORITY_RECEIPT_2026-07-05.md`

---

**LIBRARY READ SURFACE**
Meaning: Read-only library path for workers under least-knowledge.
Doctrine source file: `P0-FOUNDATION-SPINE/strategy-ssot-v6-split.md`

---

**Library-on-disk**
Meaning: Library files in repo working tree — may lag deploy-truth.
Doctrine source file: `P99-LEDGER/closed-loops.md`

---

**Line Engine ONCE**
Meaning: Build the line-engine pattern once; replicate lines via config, not ten builds.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P5-LINE-ENGINE/LINE_ENGINE_ARCHITECTURE_v0.2_HARDENED.md`

---

**Local Worker**
Meaning: Worker on Mac/local — complement to cloud motor, not schedule home.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**LOCKED SSOT**
Meaning: Versioned authority file that cannot be silently overridden.
Doctrine source file: `P7-DOCTRINE/immutable-floor.md`

---

**Mac Cursor**
Meaning: Cursor on founder Mac — complement session, not cloud motor.
Doctrine source file: `docs/MAC_CURSOR_OPS_v1.md`

---

**Mac Hardened Machine Workbench**
Meaning: Hardened Mac operator workbench — local complement to cloud motors.
Doctrine source file: `docs/MAC_CURSOR_OPS_v1.md`

---

**Mac Law**
Meaning: Mac founder session limits: light shell, no validator marathons.
Doctrine source file: `docs/MAC_CURSOR_OPS_v1.md`

---

**Mac Workbench**
Meaning: Local Mac execution bench — not 24/7 schedule host.
Doctrine source file: `docs/MAC_CURSOR_OPS_v1.md`

---

**Machine Loops**
Meaning: Catalog of governed motors and loops across ventures.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P1-CANON/MACHINE_LOOPS_v1.md`

---

**Managed AI Operations**
Meaning: Managed ops around customer AI systems — governed, receipted, not autopilot theater.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Managed AI Ops MRR**
Meaning: Internal MRR planning line for managed AI ops — not public claim.
Doctrine source file: `P1-CANON/NOETFIELD_SYSTEMS_OPERATING_PLAN.md`

---

**Managed Deterministic Brain**
Meaning: Tier 3 BaaS: receipt-backed unattended operation — gated on SourceA proof.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Manual Hub**
Meaning: Founder manual hub control — explicit tap per upgrade; not autonomous motor.
Doctrine source file: `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`

---

**Merge CREED**
Meaning: Merge CREED doctrine fragment into canonical library with version bump.
Doctrine source file: `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`

---

**Merge Hub**
Meaning: Controlled merge authority by tier T0–T3.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P8-MACHINE-LOOPS/merge-authority-tiers-T0-T3.md`

---

**Model ROI Router Advisory**
Meaning: Advisory model routing from per-line ROI receipts — config change, not rebuild.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P5-LINE-ENGINE/capability-router-circuit-breaker.md`

---

**Monthly AI**
Meaning: Internal monthly AI spend or review cadence label.
Doctrine source file: `P1-CANON/NOETFIELD_SYSTEMS_OPERATING_PLAN.md`

---

**Motor X**
Meaning: Prose placeholder for a named motor — replace with motor_id in receipts.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_DICTIONARY_v1.md`

---

**Native Pattern Thinker**
Meaning: Founder VIP role: architect bespoke deterministic brains for client stacks.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Noetfield**
Meaning: Noetfield Systems — services parent; distinct from SourceA product and TrustField venture.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/noetfield.md`

---

**Noetfield Studio IDE**
Meaning: Studio IDE venture lane — separate workspace.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**Offer GTM**
Meaning: Go-to-market offer shape under UNLOCK — honest scope per proof ladder.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/UNLOCK_DOCTRINE_v2.md`

---

**One Proof Layer**
Meaning: Architecture goal: one authoritative proof layer — receipts over diagrams.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/receipts-not-diagrams.md`

---

**One Truth Ticket**
Meaning: Single tracking item for deploy-truth reconciliation.
Doctrine source file: `P7-DOCTRINE/receipts-not-diagrams.md`

---

**Only Base Brain**
Meaning: Scope constraint: base-brain work only — no managed-tier promises.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Operations Audit**
Meaning: Operational audit engagement in Tier-1 family — findings, not live enforce.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**P1 Product Layer**
Meaning: Kernel pillar 1 (UI/Config) — business skins (Forge, Noetfield, TrustField, WitnessBC, 777); zero custom infra. Distinct from library folder P10-PRODUCT-LAYERS.
Doctrine source file: `P7-DOCTRINE/contracts-run-the-system.md`

---

**P2 Governance Layer**
Meaning: Kernel pillar 2 (Policy/SLA) — validation loops, compliance, SLA definitions.
Doctrine source file: `P7-DOCTRINE/contracts-run-the-system.md`

---

**P3 Runtime Kernel**
Meaning: Line Engine runtime kernel layer in eight-layer map.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P5-LINE-ENGINE/8-layer-kernel-and-L0-map.md`

---

**P4 Factory Data Graph**
Meaning: Kernel pillar 4 — factory mesh / data-graph layer in line-engine architecture.
Doctrine source file: `P7-DOCTRINE/contracts-run-the-system.md`

---

**Per SINA SSOT**
Meaning: Citation: governing rule lives in sina-governance-ssot repo.
Doctrine source file: `AGENTS.md`

---

**Personal Gateway**
Meaning: Founder personal gateway lane — separate from SourceA enterprise surfaces.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/SINA_GATEWAY_BLUEPRINT_LOCKED_v1.md`

---

**Phase C**
Meaning: Later phased rollout slice — not current P0.
Doctrine source file: `SG-Canonical-Library/noetfield-library/PHASE_LOOP_BUILD_PLAN_v0.1.md`

---

**Pilot CTA**
Meaning: Call-to-action for time-boxed pilot — diagnostic or design-partner scope.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Pilot SKU**
Meaning: Named pilot offer package with honest diagnostic boundaries.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Plus ONE Hub**
Meaning: Hub component in PLUS ONE cross-system integration.
Doctrine source file: `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`

---

**PLUS ONE INDEX**
Meaning: Index file for PLUS ONE linkage across systems.
Doctrine source file: `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`

---

**Premium Model Firewall**
Meaning: Policy gate on model/spend paths — diagnostic first; live enforce only when deployed.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Premium Model Firewall Pilot**
Meaning: Scoped pilot of Premium Model Firewall — not general availability.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Product Layers**
Meaning: P10 venture and product description tier in library.
Doctrine source file: `P99-LEDGER/COMPLETENESS_AUDIT.md`

---

**Production Locked**
Meaning: Production promote frozen until founder gate clears.
Doctrine source file: `P0-FOUNDATION-SPINE/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md`

---

**Queue SSOT**
Meaning: Authoritative worker cost-tier queue file.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/GOVERNED_AUTORUN_LAWS_v3.md`

---

**QuickScan SMB**
Meaning: Fast SMB diagnostic scan — Copilot-assisted, assist-only.
Doctrine source file: `P1-CANON/NOETFIELD_SYSTEMS_OPERATING_PLAN.md`

---

**Reach CAD**
Meaning: Revenue reach target in CAD — confidential unless receipt-proven.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/UNLOCK_DOCTRINE_v2.md`

---

**Rent APIs**
Meaning: Use vendor APIs on metered rent; self-host is later config flip per ROI receipts.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/deterministic-brain-doctrine.md`

---

**Retirement SSOT**
Meaning: Registry of founder duties migrating to machine proof.
Doctrine source file: `data/founder-trigger-retirement-registry-v1.json`

---

**Routing Panel**
Meaning: Control surface for capability router and circuit breaker.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P5-LINE-ENGINE/capability-router-circuit-breaker.md`

---

**Runtime Reality**
Meaning: What is actually running live — deploy-truth synonym.
Doctrine source file: `P5-LINE-ENGINE/8-layer-kernel-and-L0-map.md`

---

**Runtime Rule**
Meaning: Locked runtime behavior constraint for a loop or worker.
Doctrine source file: `P2-SSOT/SSOT_CONFLICT_LOG_R_SPLIT_v0.1.2.md`

---

**Runtime SSOT**
Meaning: Committed schedule/registry truth for runtime — contrast with live deploy-truth.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/SOURCEA_CLOUD_KERNEL_VS_DISK_RECONCILIATION_LOCKED_v1.md`

---

**Sellable NOW**
Meaning: Offer may be sold today with honest diagnostic scope — not future autonomy.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/UNLOCK_DOCTRINE_v2.md`

---

**Service SSOT**
Meaning: Registry of live services, URLs, owners, and probe targets.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P99-LEDGER/SERVICE_REGISTRY_2026-07-05.md`

---

**Setup CAD**
Meaning: Setup fee in CAD — reserved commercial figure; contract [●] only.
Doctrine source file: `P1-CANON/NOETFIELD_SYSTEMS_OPERATING_PLAN.md`

---

**Sina Governance SSOT**
Meaning: This repo: governance registry, language gate, validators, automation inventory.
Doctrine source file: `AGENTS.md`

---

**SINA SSOT**
Meaning: Abbreviation for sina-governance-ssot governance lane.
Doctrine source file: `AGENTS.md`

---

**Skill SSOT**
Meaning: Cursor agent skills loaded at session start per AGENTS.md.
Doctrine source file: `AGENTS.md`

---

**SourceA Base Brain**
Meaning: Founder's first deterministic brain — BaaS proof ladder template.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**SourceA Brain Registry**
Meaning: Governed catalog of brain artifacts, routes, and learning gates.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P1-CANON/BRAIN_REGISTRY_LEARNING_GATE_v0.1.4.md`

---

**SourceA FBE**
Meaning: SourceA factory/build executor lane slug — implementation token.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**SourceA Forge**
Meaning: SourceA cloud forge task cell — bounded build/deploy automation.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**SourceA Loop Specialist**
Meaning: CF motor dispatching loop_specialist_runtime_plan for SourceA.
Doctrine source file: `data/github_automation_registry_v1.json`

---

**SourceA Shared Authority Layer**
Meaning: Cross-repo authority routing — who may write what.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/`

---

**SourceA Worker**
Meaning: SourceA repo worker lane — ships brain/runtime; must not build TrustField loops.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**Spawn/pause/kill**
Meaning: Founder hub controls for governed lines.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md`

---

**Standard Audit**
Meaning: Baseline Tier-1 audit SKU without premium firewall pilot.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**System Architect**
Meaning: Role: design, review, delete unnecessary work — not feature coder.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/NOETFIELD_TERMINOLOGY_v1.md`

---

**Target Kernel**
Meaning: North-star runtime kernel — target architecture, not live claim.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P5-LINE-ENGINE/8-layer-kernel-and-L0-map.md`

---

**Target-as-blocker**
Meaning: Anti-pattern: treating a pursuit target as a halt condition.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P7-DOCTRINE/targets-vs-blockers.md`

---

**TF/NF**
Meaning: DLM block tag for the TrustField + Noetfield vertical pair under identity-separation law — separate ventures; Noetfield/SourceA serves TrustField; not a competitive wedge.
Doctrine source file: `P99-LEDGER/FORM_OFFICIAL_80_OPEN_PICKS_2026-07-07.md`

---

**Tier 0**
Meaning: Load tier: universal agent law plus terminology on every output.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P0-FOUNDATION-SPINE/LANGUAGE_LAYER_v1.md`

---

**Tier 1**
Meaning: Diagnostic audit engagement — findings, not live enforcement in customer env.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/agentic-cost-governance-service.md`

---

**Tier 2**
Meaning: Operating Brain Install — after one SourceA pattern proof.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**Tier 3**
Meaning: Managed deterministic brain — gated on SourceA 24/7 receipts.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P9-PATTERN-FACTORY/brain-as-a-service.md`

---

**TrustField Technologies** — ALIAS RETIRED
Meaning: Retired wording. Use canonical term: TrustField. Do not use until incorporation receipt exists.

---

Aliases retired: TrustField Technologies
Conflict rule: Auto-rewrite to TrustField per terminology §9.

---

**TrustField Technologies Inc** — ALIAS RETIRED
Meaning: Retired wording. Use canonical term: TrustField. Wrong form implies filed corporation; name is reserved only.

---

Aliases retired: TrustField Technologies Inc
Conflict rule: Auto-rewrite to TrustField per terminology §9.

---

**Update TrustField**
Meaning: Sync TrustField venture docs/worker repo to SSOT — never merge into SourceA tree.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/trustfield.md`

---

**Updated TrustField**
Meaning: Ledger note: TrustField lane docs or worker state refreshed to SSOT.
Doctrine source file: `SG-Canonical-Library/noetfield-library/P10-PRODUCT-LAYERS/trustfield.md`

---

**Video Ad Factory**
Meaning: Deferred venture lane for video-ad automation.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

**Wire PLUS ONE**
Meaning: Connect PLUS ONE index/hub integration across systems.
Doctrine source file: `P99-LEDGER/SOURCEA_FORM_OFFICIAL_SUBMIT_MAP_SIMPLIFIED_2026-07-07.md`

---

**Worker RUN INBOX**
Meaning: Worker command lane token for inbox processing — implementation, not public SKU.
Doctrine source file: `ssot/MULTI_REPO_WORKER_REGISTRY_v1.md`

---

