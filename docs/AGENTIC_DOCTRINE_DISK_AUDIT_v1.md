<!-- GENERATED from receipts/doctrine/AGENTIC_DOCTRINE_DISK_AUDIT_v1.json — do not hand-edit (doctrine #128) -->
# Agentic Doctrine v1 — Disk Implementation Audit (2026-07-12)

**Doctrine:** docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md (sha256 cda3c2f6…)  
**Method:** 9 evidence-based audit agents over motor (noetfield-sandbox-private), sina-governance-SSOT, noetfeld-OS, SourceA; every status cites real files. SourceB is not cloned locally → NOT_LOCAL.

## Verdict

**49 DONE · 64 PARTIAL · 24 MISSING · 1 NOT_LOCAL** (of 138 assessed sub-points).

> The execution kernel is doctrine-grade (deterministic-first, receipts, SSOT, permissions, contracts largely DONE), but the system is nearly blind to its own cost and has almost no revenue organ or learning loop — the single keystone gap is real cost metering (#107 -> #133), which unblocks the entire cost-governance cluster (109/132/134/142/143).

## By cluster

| Cluster | Done | Partial | Missing | Summary |
|---|---|---|---|---|
| A. Agent-as-role, registry, invocation discipline, permissions | 7 | 3 | 0 | Strongest structural area: closed callable-worker set (#1/#2), capability guards (#58), per-agent secrets (#57), cost-classed registry (#116); only registry-population and lint items (#117/#123/#135) remain PARTIAL. |
| B. Model tiers, cost routing, escalation, local/cloud, vendor failover | 6 | 5 | 2 | Escalation ladder (#3), vendor-neutral routing (#110) and degraded mode (#112) are DONE, but there is only one provider binding so failover (#111) is thin, and scoring/history feedback (#97/#98) plus distillation/shadow-eval (#101/#103) are absent. |
| C. Context slicing, budgets, retrieval, caching, versioning, compression | 4 | 7 | 1 | Slicing (#5), micro-batching (#78) and output compression (#89) work, but there is no token/context budget at all (#6 MISSING) and retrieval/caching/versioning (#7/#39/#40) are only half-wired. |
| D. Deterministic-first, verification pyramid, receipts, heartbeat, structured output | 8 | 5 | 1 | Deep strength: deterministic-first (#8), code-authored + schema-bearing receipts (#28/#29), structured output (#79); gaps are an unordered pyramid (#27), no real cost receipt (#107), and missing semantic diff (#84). |
| E. Job contracts, budgets, bounded change, branch-per-job, single writer, states, gates | 7 | 3 | 0 | Contract discipline is solid: immutable contract (#16), branch-per-job (#15), dependency decomposition (#49), irreversible gate (#60); remaining gaps are max_files/lines caps (#48), typed BLOCKED_EXECUTOR_ENDPOINT (#56) and dry-run-default inversion (#59). |
| F. Retry ladder, failure caching, negative KB, success patterns, distillation, audit | 1 | 8 | 2 | Weak learning organ: signatures/patterns exist in SourceA but are unwired from the motor; failure-typed retry ladder (#19), failure-signature suppression (#20) and capability promotion (#137) are all PARTIAL, kill-criteria (#122) and random audit (#105) MISSING. |
| G. Event-driven, adaptive polling, ROI preflight, stop conditions, liveness, cost sentinel | 1 | 6 | 5 | The cost/ROI blind spot: only event-driven dispatch (#31) is DONE; daily cost sentinel (#133), spike breaker (#132), waste report (#134) and cost-per-outcome (#143) are all MISSING because spend is never aggregated. |
| H. SSOT enforcement, authority, no-2nd-control-plane, compiler, canary, integrator, parallel, Ruflo | 11 | 11 | 1 | Largest cluster and second-strongest: SSOT/authority/no-2nd-plane (#41/#42/#43), prompt + deterministic-workflow compilers (#23/#118), canary (#45/#46) all DONE; PARTIALs are integrator automation, interface contracts, Ruflo stubs and workflow-template breadth; change propagation (#130) MISSING. |
| I. Commercial surface / SourceB fulfillment / config / pricing / claims / founder gates / outcome metrics | 4 | 16 | 12 | Biggest and least-built cluster: founder-gate plumbing exists but there is no pricing SSOT (#83), claims registry (#82), customer-config layer (#67-72), fulfillment state machine (#74), revenue receipt (#144) or unlock-score queue (#65); the SourceB fast path (#148) is not even local. |

## Top gaps (ranked by dependency-unlock leverage, doctrine #65)

**1. #133 Daily cost sentinel** — MISSING → `sina-governance-SSOT`
   - Why: unlock 5 and the explicit currency the entire cost-governance cluster (109/132/134/142/143) depends on; without a summed daily spend number none of revenue-linked scaling, spike breaker, waste report or cost-per-outcome can fire. Cost receipts exist but are mostly 0.0 and never aggregated.
   - Next step: Write a deterministic daily sentinel that scans all cost receipts for the day and emits cost-by-project / by-model / retry / failed-job totals + top-5 workflows.

**2. #107 Cost receipt (real token metering)** — PARTIAL → `noetfield-sandbox-private (motor)`
   - Why: unlock 4; the measurement primitive UNDER #133. Cost fields exist in schema but are hardcoded (0.002/0.01) not measured, so every downstream cost gate (108/133/134/143) is computing on fiction. Instrumenting this is the true keystone that makes the whole G cluster real.
   - Next step: Instrument intel_low._call_raw to capture real token counts + call count and have executor.build_receipt compute cost from those plus wall-clock runtime and retry count.

**3. #83 Pricing SSOT** — MISSING → `sina-governance-SSOT`
   - Why: unlock 4; foundational commercial primitive that #130 change-propagation, #82 claims registry and every checkout/landing/FAQ surface must derive from. Price is currently a free-form draft field with no canonical source, so commercial correctness is unguaranteed.
   - Next step: Create data/pricing_ssot_v1.json (canonical price IDs + display) and make commercial_pulse price_display and any checkout read from it.

**4. #65 Dependency unlock score** — MISSING → `noetfield-sandbox-private (motor)`
   - Why: unlock 4; this is the doctrine's own prioritization mechanism (the very metric this report ranks by). Without an unlock_score term in the scorer, the queue cannot rank foundational unblockers (standing identity, canonical queue, cost metering) ahead of cosmetic work — it self-limits every other improvement.
   - Next step: Add an unlock_score field (0-5) to census metadata and a UNLOCK_WEIGHT term in score_record so foundational unblockers rank first.

**5. #148 SourceB commercial fast path** — NOT_LOCAL → `SourceB (not cloned) + motor registry`
   - Why: unlock 5; the actual revenue pipeline (setup->demo->gate->provision->activate->receipt). It is the highest-unlock point in the audit but currently only a bounded write target — the money path does not exist in any local repo. Everything commercial (67-76, 144) is downstream of standing this up.
   - Next step: Author the fast path as workflow definition sourceb_voice_provision_v1 in the motor workflow registry, targeting the SourceB repo once it is available locally.

**6. #144 Revenue receipt** — MISSING → `sina-governance-SSOT`
   - Why: unlock 4; the denominator for cost-per-verified-outcome (#143) and the only proof the commercial organ works. The outbound revenue log exists but has zero real receipts, so revenue is uncounted and unmeasurable.
   - Next step: Define revenue_receipt_v1 schema (lead_id/payment_id/provisioning_id/trial/captured-call/appointment) and emit one on the first real lead/payment event.

**7. #74 Fulfillment state machine** — PARTIAL → `sina-governance-SSOT`
   - Why: unlock 4; the commercial-pulse SM exists for outbound sends but the customer fulfillment states (requested->approved->provisioning->started->done->trial->cancelled) do not. This is the skeleton the entire SourceB fast path (#148) and provisioning gates (#73/#76) hang on.
   - Next step: Author fulfillment_state_machine_v1 with the doctrine states as a sibling to the commercial-pulse SM, owned by the SourceB fast path.

**8. #131 Default-deny cost explosion** — PARTIAL → `noetfield-sandbox-private (motor)`
   - Why: unlock 4; already structural for the two costliest dimensions (premium escalation, >2 retries via the router ceiling), but the other 6 doctrine dimensions (full-repo context, agents>3, multi-round, browser automation, paid provisioning, long schedule) have no deny-unless-reason guard — the remaining cost-explosion surface.
   - Next step: Add a single preflight policy check that default-denies the remaining 131 dimensions unless the job contract carries an explicit reason field for that dimension.

**9. #19 Retry ladder by failure type** — PARTIAL → `noetfield-sandbox-private (motor)`
   - Why: unlock 4; the motor is single-tier (fail -> W-INTEL-LOW -> handoff) with no failure-class routing. Wiring the already-computed failure_classes to distinct tiers (syntax->T0, test->T1, architecture->handoff, credential/outage->typed blocker) turns blind retries into cause-based escalation and cuts wasted repair cycles.
   - Next step: Add a route table in motor/repair keyed on diagnose_deterministic failure_classes dispatching each class to its matching tier.

**10. #20 Failure caching (signature)** — PARTIAL → `noetfield-sandbox-private (motor)`
   - Why: unlock 4; signature computation exists in SourceA but no dispatcher consults it, so the motor re-runs known-blocked jobs and re-burns cost on the same failure. Suppressing re-dispatch on an open blocker signature is direct, compounding waste reduction.
   - Next step: Add a failure-signature ledger the motor intake checks: on a job whose (repo,error,workflow_step) signature is an open blocker, refuse re-dispatch and refresh only the blocker receipt.

**11. #56 Missing-capability -> exact interface** — PARTIAL → `noetfield-sandbox-private (motor)`
   - Why: unlock 4; handoff packets describe missing capability in prose, not as a machine-readable interface. A typed BLOCKED_EXECUTOR_ENDPOINT (job_class, worker_class, adapter path, binding_env) lets a capability gap be auto-filled by one registry row — turning founder handoffs into self-describing build tickets.
   - Next step: Add a typed BLOCKED_EXECUTOR_ENDPOINT field to the handoff packet naming the exact missing interface.

**12. #109 Revenue-linked scaling** — PARTIAL → `sina-governance-SSOT`
   - Why: unlock 4; the spend cap is policy text with no enforcement — the founder's own system notes 'no enforcement receipt'. Once #133 produces a monthly spend number, one gate in the ROI Judge closes the loop between spend and revenue, the doctrine's core economic safety.
   - Next step: Build a monthly-spend accumulator from cost receipts and wire a gate that BLOCKS_WITH_REASON new premium dispatch above the applicable cap, emitting an enforcement receipt.

## Quick wins (PARTIAL, cheap to finish)

- **#24 Compiler shrinks prompt (entropy metric)** — Emit input_tokens vs output_tokens (byte size) on each compile receipt and add a canary asserting compiled_contract_size < raw_heading_context_size. Compiler already produces the bounded contract; just measure it.
- **#80 Cheap schema repair** — Add a deterministic JSON-repair pass (bracket/quote/trailing-comma fixups) before the single re-prompt in intel_low, fixing most malformed outputs with zero extra model calls.
- **#30 Receipt deduplication (delta only)** — In write_receipt, hash the state-bearing fields and, when identical to the previous receipt for the same job, write a small delta/heartbeat pointer instead of a full duplicate.
- **#126 Output length limits** — Define an output-limits policy (max_summary_words 250, max_risks 5, max_recommendations 3) and enforce it in intel_low._validate by truncating/rejecting oversized arrays. Caps already exist as scattered prompt hints.
- **#53 Founder decision compression** — Define founder_decision_v1 schema (options[], recommended, why[<=3], cost_risk_delta, no_decision_consequence) and have handoff.emit_packet populate it; the decision item already carries kind/detail/receipt/packet.
- **#88 Flaky test registry** — Add data/flaky_test_registry_v1.json (test, flake_rate, known_signature, retry_policy, owner) populated from SourceA _unstable scores; detection already exists, only the persistent registry file is missing.
- **#86 Low-risk auto-promotion** — Add a low_risk_auto_promote predicate that advances typo/docs/fixture/receipt jobs to READY_FOR_MERGE without a decision item; auto-advance-on-success already exists.
- **#123 Avoid agent theater** — Add a CI lint asserting the callable worker set stays <=3 ranks and no job contract requests >1 reasoning agent for risk<high — turns an already-true invariant into a rejectable rule.

## Strongest areas (doctrine already embodied)

- Execution/permission discipline (Cluster A, 7/10 DONE): agent-as-role not process (#1), template!=execution with one min-cost worker per job (#2), capability-based permissions (#58), per-agent secret scoping (#57), cost-classed worker registry (#116).
- Deterministic-first + evidence (Cluster D, 8/14 DONE): the doctrine's boundary is structurally enforced — no-LLM deterministic modules (#8), don't-guess-provable-facts recompute (#9), code-authored + schema-bearing receipts (#28/#29), strict structured output (#79), machine-generated human views (#128).
- SSOT + authority + compilation (Cluster H, 11/23 DONE): one-owner-per-domain enforcement (#41), authority check before edit (#42), no second control plane (#43), prompt compilation pipeline (#23), deterministic workflow compiler (#118), thin-slice canary with real proof bundles (#45).
- Job-contract governance (Cluster E, 7/10 DONE): immutable worker-agnostic contract (#16), branch-per-job never-merge (#15), real dependency-graph decomposition (#49), irreversible-action founder gate (#60), rich partial-success state set (#55).
- Cost-safe-by-construction routing: hard router ceiling MAX_AUTOMATIC_RANK=1 as law not config (#3/#131), vendor-neutral binding-by-env-name (#110), first-class degraded-continue mode (#112) — the system fails closed and cheap even though it cannot yet measure its own spend.

## Full per-point audit

Canonical machine-readable record: `receipts/doctrine/AGENTIC_DOCTRINE_DISK_AUDIT_v1.json` (138 points with evidence paths, gaps, next steps, unlock scores).

### MISSING (24)

- **#133 Daily cost sentinel** (unlock 5) — No daily deterministic report of cost today / by project / by model / retry costs / failed-job costs / top-5 expensive workflows. Cost is captured per-receipt (mostly 0.0) but never summed. The existi  
  evidence: `sina-governance-SSOT/scripts/write_roi_heartbeat_v1.py:1,17-30 (the only cost-heartbeat script — WEEKLY, and every metric is hardcoded 'unknown'; a stub, not a `
- **#132 Cost spike circuit breaker** (unlock 4) — No cost-spike breaker exists. Nothing watches cumulative or rate-of-spend against a threshold to pause, capture state, write a partial receipt, and request escalation. (The only 'circuit breaker' in t  
  evidence: `sina-governance-SSOT/docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md:173 (doctrine text only: threshold -> pause/capture state/partial receipt/request escala`
- **#143 Cost per verified outcome** (unlock 4) — The headline commercial metric is not computed. Numerator (total agentic cost) is unavailable because spend is never aggregated (#133) and denominator (verified useful outcomes) is never counted (#142  
  evidence: `sina-governance-SSOT/docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md:184 (formula: Total Agentic Cost / Verified Useful Outcomes); sina-governance-SSOT/scrip`
- **#130 Change propagation automation** (unlock 4) — No pricing-SSOT→consumers propagation checker exists. commercial_pulse_dispatch_check validates outbound draft dispatchability and workflow_census classifies loops, but nothing detects that a pricing   
  evidence: `sina-governance-SSOT/scripts/commercial_pulse_dispatch_check_v1.py:1; sina-governance-SSOT/scripts/workflow_census_v1.py:1; sina-governance-SSOT/docs/AGENTIC_CO`
- **#65 Dependency unlock score** (unlock 4) — No dependency_unlock or unlock_score anywhere in the scorer or census. Standing-identity / callable-executor / plan-queue / Stripe-webhook unlock weighting is absent.  
  evidence: `noetfield-sandbox-private/motor/plans/score_plan_queue.py (scorer has value/effort/urgency only; no unlock term)`
- **#83 Pricing SSOT** (unlock 4) — No single pricing SSOT that checkout/landing/FAQ/receipt derive from within the four repos; price is a free-form draft field.  
  evidence: `sina-governance-SSOT/data/commercial_pulse_queue_v1.json (draft carries price_display/offer_id but no canonical pricing source); No pricing config SSOT inside m`
- **#144 Revenue receipt** (unlock 4) — No revenue_receipt schema capturing lead_id/payment_id/provisioning_id/trial/captured-call/appointment; the outbound revenue log exists but is empty (zero real receipts).  
  evidence: `sina-governance-SSOT/scripts/p0pgr_campaign_planner_v1.py (notes REVENUE loop gateway_outbound_log_v1 has ZERO receipts, census rule-4); sina-governance-SSOT/la`
- **#101 Distillation to reusable pattern** (unlock 3) — No implemented mechanism turns an expensive/tier2 output into a cheap reusable rule (the doctrine's AUTH_SESSION_OWNERSHIP_PATTERN_v1 example). No pattern/rule registry file, no success-pattern librar  
  evidence: `sina-governance-SSOT/docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md:142-143 (points 101/102 defined only as doctrine)`
- **#103 Cheap shadow evaluation** (unlock 3) — The word 'shadow' exists but for a different concept: p0pgr shadow mode is compile+route-without-execution. Nothing runs a cheaper candidate model in parallel-without-authority against real jobs, scor  
  evidence: `sina-governance-SSOT/scripts/p0pgr_cycle_v1.py:73-145 (the existing 'shadow cycle' shadows the DISPATCH/route decision, zero execution — NOT a cheaper-model qua`
- **#6 Per-agent context budget** (unlock 3) — Every 'budget' on disk is a COST/repair-cycle budget (contract.budget = {max_cost_usd, max_repair_cycles}; noos model-router budget = max_usd_per_run/day), never a token/context budget per role. There  
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json:38; noetfield-sandbox-private/motor/kernel/intake.py:41; noetfeld-OS/config/model-router.yml:8`
- **#84 Semantic diff** (unlock 3) — No implementation anywhere: reviewers are not scoped to only risk-relevant changes by semantic category. Motor knows which paths changed but does not map them to auth/payments/secrets/db-schema risk t  
  evidence: `sourcea/brain-os/wtm/SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md:98 'L14 Diff intelligence | Semantic diff, change impact | Missing | High'; sourcea/brain-os/`
- **#122 Kill criteria for experiments** (unlock 3) — No structured experiment kill-criteria mechanism. Nothing implements 'no improvement after 3 canaries / cost>2x baseline / low first-pass / requires permanent premium / duplicates subsystem'. The ROI   
  evidence: `sina-governance-SSOT/p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1.md (ROI Judge + monthly spend cap — adjacent cost governor, blocks premium dispatch on cap breach); n`
- **#134 Weekly waste report** (unlock 3) — No weekly waste report is generated. None of the six waste signals are computed. Notably 'schedules without external outcome' is directly computable from receipts once #36's external-outcome liveness   
  evidence: `sina-governance-SSOT/docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md:174 (doctrine text only); sina-governance-SSOT/scripts/write_roi_heartbeat_v1.py (weekly`
- **#67 Productized workflow** (unlock 3) — Only the doctrine text describes it. No productized single-workflow product exists in code; SourceA remains a generic brain-os.  
  evidence: `No receptionist / 'AI Receptionist Setup' / productized-vertical workflow found across motor, governance, noos, SourceA (grep receptionist|voice agent -> none)`
- **#68 Customer config not human intake** (unlock 3) — No customer-facing config schema or setup wizard; all intake is founder/agent-driven Job Contracts, not customer self-config.  
  evidence: `No setup wizard / customer config schema found (grep wizard|config_schema|setup wizard -> no product hits)`
- **#76 Idempotency key for paid actions** (unlock 3) — No paid/charge/provisioning action exists, so the doctrine's customer_id+action_type+version key is absent.  
  evidence: `noetfield-sandbox-private/motor/plans/materialize.py (generic heading_id idempotency only); No paid-action key (customer_id+action_type+version) anywhere; comme`
- **#82 Claims registry** (unlock 3) — There is a banned-token validator but no registry of public claims with source/status (e.g. '24/7'=supported, 'unlimited calls'=cost_risk:unbounded/approval_required).  
  evidence: `sina-governance-SSOT/scripts/commercial_pulse_dispatch_check_v1.py:27 (FORBIDDEN_ENTITY_TOKENS ban list — a banned-content check, doctrine #81, not a registry)`
- **#105 Random audit** (unlock 2) — No random-sampling audit of completed jobs to catch quality drift. The existing audit machinery is comprehensive/continuous (noos) or receipt-scoped (p0-pgr), never a probabilistic sample of a fractio  
  evidence: `noetfeld-OS/.github/workflows/noos-workflow-audit.yml, noos-machine-audit-witness.yml (CONTINUOUS full audit every 15 min — not random sampling); sina-governanc`
- **#32 Adaptive polling** (unlock 2) — No mechanism anywhere changes a loop's polling frequency based on observed change-rate or dormancy, and NOOS has no evidence artifact proving a given frequency is ROI-positive. Every schedule is a har  
  evidence: `sina-governance-SSOT/docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md:73 (doctrine text only: high-change hourly / stable daily / dormant weekly); grep across`
- **#69 Config templates** (unlock 2) — No vertical template set on a shared runtime.  
  evidence: `No per-vertical (dental/restaurant/real-estate/legal/medical) config templates found in any of the four repos`
- **#72 Browser demo before phone** (unlock 2) — No create->browser-voice-test->tune->payment->bind-phone sequence exists locally.  
  evidence: `grep browser demo|browser_demo -> no hits; no provisioning code`
- **#141 Commercial experiment budget** (unlock 2) — No commercial experiment budget schema anywhere.  
  evidence: `sina-governance-SSOT/data/commercial_pulse_queue_v1.json (has approval window but no experiment budget object); No duration/traffic_scope/spend_cap/success_metr`
- **#70 Default-heavy UX** (unlock 1) — Depends on a config schema that does not yet exist; nothing to default from.  
  evidence: `No config layer exists to carry defaults (68/69 missing)`
- **#71 Progressive config** (unlock 1) — No staging of configuration; no demo/paid/optimization stages.  
  evidence: `No staged (demo / paid-essentials / optional-optimization) configuration flow in code`

### PARTIAL (64)

- **#4 Cheap first-pass classifier** (unlock 4) — The cheap decompose emits jobs with title/job_class/instruction/depends_on/risk only. It does NOT produce the doctrine's full shrink field set: project/repo/scope/exclude/required_workflow/founder_gat  
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:28-46 ('decompose' shrinks a heading into 2-6 jobs; 'classify' task); noetfield-sandbox-private/motor/kern`
- **#7 Retrieval before reading** (unlock 4) — The file-tree->targeted-blob half exists: census/emit_headings pull `git/trees/...?recursive=1` then read only specific blobs (package.json/pyproject/Makefile) rather than whole repos, and the noos ro  
  evidence: `noetfield-sandbox-private/motor/plans/census.py:297; noetfield-sandbox-private/motor/plans/emit_headings.py:128; noetfeld-OS/config/model-router.yml:14`
- **#27 Verification pyramid (schema->...->human)** (unlock 4) — The legs exist and are cheap-first, but there is no codified strict ladder ordering (schema->static->lint->type->unit->integration->e2e->LLM->human) nor an explicit 'LLM review' tier before human; the  
  evidence: `motor/motor/schemas/job_contract.schema.json validates every contract (schema tier); motor/motor/adapters/det_exec.py run_acceptance runs repo lint/type/test co`
- **#107 Cost receipt** (unlock 4) — The cost fields exist in schema but are not computed deterministically from real usage: motor hardcodes est_cost_usd (0.002/0.01) and tier0_checks; governance cost is model/session-authored (schema ev  
  evidence: `governance/p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json:69 cost{provider,model,tokens_in,tokens_out,total_usd,accounting_note}; governance/p0-pgr/P0_PROMPT_LOOP_S`
- **#56 Missing-capability -> exact interface (BLOCKED_EXECUTOR_ENDPOINT)** (unlock 4) — The CONCEPT is implemented: when no callable worker at/below the ceiling can execute a job_class, router returns handoff_required and handoff.emit_packet writes a COMPLETE work packet (full contract +  
  evidence: `noetfield-sandbox-private/motor/adapters/handoff.py:18; noetfield-sandbox-private/motor/adapters/router.py:66; noetfield-sandbox-private/motor/kernel/executor.p`
- **#19 Retry ladder by failure type** (unlock 4) — No implementation of the doctrine's 6-way failure-type routing (Syntax->T0 deterministic; Test->T1 triager; Architecture->T2; Missing credential->founder_blocked; Vendor outage->defer+receipt; Ambiguo  
  evidence: `noetfield-sandbox-private/motor/repair/repair.py:4-5 (explicitly: "No automatic escalation above W-INTEL-LOW exists anywhere in this pipeline") — single-tier, f`
- **#20 Failure caching (signature)** (unlock 4) — Signature COMPUTATION exists (SourceA) and repetition raises risk, but the doctrine's core behavior — suppress re-running the same attempt until the blocker is resolved, only refreshing the blocker re  
  evidence: `SourceA/scripts/execution_intelligence/pattern_engine/signatures.py:19 (error_fingerprint), :39 (record_fingerprint) — deterministic failure signatures from cmd`
- **#102 Learn once, reuse many** (unlock 4) — SourceA captures learning as patterns + fix links + decisions and biases its OWN planner, but the doctrine's full distillation — each expensive solution emitted as reusable workflow/test-fixture/verif  
  evidence: `SourceA/scripts/execution_intelligence/decision_memory/fix_linker.py:1 (failure->fix relationship builder: links failure_signal to recovery_signal); SourceA/scr`
- **#137 Promote capability not just output** (unlock 4) — The motor structurally PREFERS cheaper/deterministic (router ceiling, det-first) and SourceA can recommend optimizations, but there is no promotion/graduation LOOP that observes a repeatable reasoning  
  evidence: `noetfield-sandbox-private/motor/repair/repair.py:4-5 and OPERATOR.md (router ceiling: no worker above W-INTEL-LOW; deterministic det_patch preferred over intel `
- **#34 Stop condition per loop** (unlock 4) — Per-job/per-loop stops exist for budget-exceeded, terminality, and repair-cycle exhaustion, but the doctrine's full set is not covered uniformly: no time-based idle kill (no state change 7d), no expli  
  evidence: `noetfield-sandbox-private/motor/kernel/scheduler.py:22 (TERMINAL = done/handoff_required/dead_letter) and :66-84 (terminality-based closure + dead_letter cascad`
- **#109 Revenue-linked scaling** (unlock 4) — The revenue-linked cap is policy text, not enforced code. There is no aggregate monthly-spend accumulator, no revenue signal wired in, and no enforcement receipt. The cap cannot fire because monthly s  
  evidence: `sina-governance-SSOT/p0-pgr/P0_DISPATCH_ROUTER_RULES_v1.md:58 (cap policy: <=$1,500/mo before revenue>=$10k/mo; <=$2,000/mo after — router checks remaining mont`
- **#131 Default-deny cost explosion** (unlock 4) — Default-deny is real and structural for the two highest-cost dimensions (premium/escalation and >2 retries). The other doctrine-131 dimensions — full-repo context, >3 agents, multi-round debate, brows  
  evidence: `noetfield-sandbox-private/motor/adapters/router.py:16,53 (MAX_AUTOMATIC_RANK=1 'is law, not config'; module structurally cannot return a worker above W-INTEL-LO`
- **#142 Measure outcome not activity** (unlock 4) — The building blocks exist per-receipt (value_class, verification pass, founder_blocked), but there is no aggregate report that contrasts outcomes (PRs verified / interruptions avoided / setups complet  
  evidence: `noetfeld-OS/.noos-runtime/loops/self_heal/cycle-000001.json (per-cycle value_class + sink_invariant + evidence commands with exit codes); sina-governance-SSOT/s`
- **#74 Fulfillment state machine** (unlock 4) — A real state machine exists but for outbound commercial pulse, not the doctrine's customer fulfillment states requested->approved->provisioning_pending->started->done->trial_active->cancelled/expired.  
  evidence: `sina-governance-SSOT/data/commercial_pulse_queue_v1.json (states: idle->drafting->validate_failed->queued_for_approval->founder_blocked->approved_pending_send->`
- **#117 Workflow registry vs dynamic swarm** (unlock 3) — The anti-dynamic-swarm principle is fully realized (registry-driven, serialized, no swarm-consensus code anywhere). But a first-class named-workflow catalog is thin: the doctrine's exemplar workflows   
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:98-100 ('New worker = one registry row'; serialized scheduler, no swarm); noetfield-sandbox-private/products/sa`
- **#37 Local LLM for bulk low-risk** (unlock 3) — The abstraction is designed to allow a local model, but the only concrete binding is a hosted cloud endpoint. No local model (doctrine names Qwen3-14B) is wired, and there is no routing that sends bul  
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:1-14 ('Vendor-free by construction'; openai_json wire style explicitly supports OSS/local servers); noetfi`
- **#97 Model output scoring** (unlock 3) — Raw per-call cost/token/retry data is captured on receipts, but there is NO scoring layer that rolls these into a per-model quality signal (test-pass rate, review-rejection rate, hallucination rate, u  
  evidence: `sina-governance-SSOT/p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json:69-80 (cost block: provider/model/tokens_in/tokens_out/total_usd); noetfield-sandbox-private/mot`
- **#98 Router sees historical performance** (unlock 3) — The router already CONSUMES a `reliability` field as a tiebreaker, so the hook exists — but the value is a static constant 1.0, never recomputed from receipts. There is no feedback loop reading histor  
  evidence: `noetfield-sandbox-private/motor/adapters/router.py:68-70 (sort key includes -reliability tiebreaker); noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_`
- **#111 Provider failover** (unlock 3) — The doctrine's third failover limb (queue+receipt, don't stop) is implemented. The first two limbs are NOT: on a provider error intel_low retries the SAME binding once then fails — there is no 'same-t  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py:231-241 (exhaustion -> emit handoff packet + continue unrelated jobs; not full stop = the 'queue+receipt' lim`
- **#39 Cache stable contexts as registry refs** (unlock 3) — Several stable contexts ARE externalized to versioned registries loaded by reference: ADAPTER_REGISTRY_v2.json (allowed tools/model policy, loaded by router.load_registry), deployment.json (repo owner  
  evidence: `noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json; noetfield-sandbox-private/motor/config/deployment.json; noetfeld-OS/config/model-router.yml:4`
- **#90 Error signature extraction** (unlock 3) — A basic error signature exists: execution_spine._error_signature(stderr, exit_code) returns the last stderr line truncated to 240 chars (or exit_N), stored as ExecutionRecord.error_signature and surfa  
  evidence: `SourceA/scripts/execution_spine/writer.py:21; SourceA/scripts/execution_spine/types.py:43; SourceA/scripts/runtime/repair_loop/failure_classifier.py:40`
- **#35 Heartbeat without LLM** (unlock 3) — No single heartbeat artifact emits the doctrine's field set (timestamp/queue_depth/last_success/last_fail/worker_health/credential_expiry). Watchdog covers liveness+staleness+workflow health but not q  
  evidence: `motor/.github/workflows/motor-watchdog-v1.yml — deterministic (no LLM) staleness/liveness sweep, re-enable, self-heal, issue-on-fault; motor/motor/panel/build_p`
- **#48 Bounded change (max_files/lines)** (unlock 3) — Change is bounded by PATH (fail-closed allowed_paths guard, boundary-aware match, explicit-paths-only git add) — strong. But there is NO max_files or max_lines cap enforced in the motor: a patch job c  
  evidence: `noetfield-sandbox-private/motor/adapters/det_patch.py:37; noetfield-sandbox-private/motor/config/deployment.json:31; noetfeld-OS/repo-policy.json:55; noetfeld-O`
- **#59 Dry-run default** (unlock 3) — The motor realizes the INTENT structurally: every effect is a branch+PR that is never merged and never deployed (STANDING_EXCLUSIONS + 'DO NOT MERGE' PR body), so nothing irreversible happens by defau  
  evidence: `noetfield-sandbox-private/motor/plans/materialize.py:16; noetfield-sandbox-private/motor/adapters/det_patch.py:99; noetfeld-OS/scripts/noetfield_deploy_v1.py:24`
- **#21 Negative knowledge base** (unlock 3) — No structured, machine-queryable negative-rule store that dispatch/planning consults before acting. Negative knowledge is scattered across doctrine prose, SourceA incident docs, and mined failure patt  
  evidence: `sina-governance-SSOT/docs/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.md:62 (the negative rules are enumerated in prose only); SourceA/scripts/execution_intellig`
- **#22 Success pattern library** (unlock 3) — Success patterns exist in two disconnected forms: SourceA mines command-signature patterns from live memory, and noetfeld-OS/motor hold hand-authored named recipes. Neither is the doctrine's unified r  
  evidence: `SourceA/scripts/execution_intelligence/pattern_engine/extractor.py:1 (mines success|failure|repetition|fix patterns); ~/.sina/execution_patterns.json (LIVE data`
- **#106 Anomaly-triggered audit** (unlock 3) — Individual anomaly signals exist scattered across three repos (security escalation, cost-cap breach, repetition risk, trend detection) but there is no consolidated anomaly-triggered audit that fires o  
  evidence: `noetfeld-OS/scripts/noos_self_heal_v1.py:41-45 (HIGH_RISK_ESCALATE includes security_finding, integration_broken -> forced escalation); sina-governance-SSOT/p0-`
- **#33 Schedule ROI preflight** (unlock 3) — Job-level ROI/cost preflight exists, but there is no preflight GATE for creating a new SCHEDULE carrying the doctrine's required fields (purpose, expected_value, estimated_monthly_cost, frequency, why  
  evidence: `noetfield-sandbox-private/motor/adapters/router.py:41,55-57 (job-level cost preflight: est_cost > budget -> throttled); noetfield-sandbox-private/motor/plans/sc`
- **#36 Liveness via external receipt** (unlock 3) — Liveness is currently measured as 'the loop fired / had a green run / last_fired_at' — exactly the cron-ran signal doctrine 36 says is NOT proof of life. No mechanism asserts liveness from an EXTERNAL  
  evidence: `noetfield-sandbox-private/.github/workflows/motor-watchdog-v1.yml (staleness = tick had no GREEN run in MAX_TICK_AGE_HOURS -> redispatch; this is 'cron ran' liv`
- **#50 Integrator only at end** (unlock 3) — The integrator role is defined (NOOS observes/coordinates at end; lanes produce contracts+receipts) and the motor closure job finalizes only when all other jobs are terminal — but the integrator is a   
  evidence: `noetfeld-OS/data/noos-integrator-control-plane-v1.json:6; noetfeld-OS/docs/_NOOS_AGENT/[NOOS-AGENT-20260707-008]_INTEGRATOR_DAILY_CHECKLIST_v1.md; noetfeld-OS/n`
- **#51 Interface contract before parallel work** (unlock 3) — Ownership/lane is fixed before parallel action (L2 lane declaration; contract fixes target_repository/allowed_paths/authority before dispatch), but the doctrine's explicit endpoint/request_schema/resp  
  evidence: `sina-governance-SSOT/ssot/PARALLEL_AUTOMATION_GOVERNANCE_v1.md:30; noetfield-sandbox-private/motor/schemas/job_contract.schema.json:9; noetfield-sandbox-private`
- **#129 One decision, one place** (unlock 3) — Repo ownership, deploy authority and model routing each have a single canonical record (SG registry / authority.yaml / motor targets / NOOS one_law) — but the other decisions the doctrine names (prici  
  evidence: `sina-governance-SSOT/ssot/MULTI_REPO_WORKER_REGISTRY_v1.md:23; SourceA/brain-os/system/authority.yaml:1; noetfield-sandbox-private/motor/config/deployment.json:`
- **#52 Heading vs founder questions** (unlock 3) — authority_class is passed in at intake (intake.py --authority), not auto-classified. No coded classifier that decides an item is a real founder question vs machine detail (filename/branch/lint); the d  
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json (authority_class enum: read_only|bounded_write|founder_only); noetfield-sandbox-private/motor/k`
- **#62 Opportunity dedup** (unlock 3) — Dedup exists but keys on plan-document identity, not the doctrine's opportunity cluster key project+surface+issue_type+target+normalized_signature. No opportunity/signal clustering.  
  evidence: `noetfield-sandbox-private/motor/plans/census.py:208 (dedup_sort: dedupe ONLY by (repo,path,blob_sha) tuple); noetfield-sandbox-private/motor/plans/census.py:211`
- **#63 Priority by commercial value** (unlock 3) — Formula is value_weight*effort_weight+urgency, not the doctrine's commercial_impact*urgency*confidence*reversibility/cost; confidence, reversibility, and a cost divisor are absent.  
  evidence: `noetfield-sandbox-private/motor/plans/score_plan_queue.py:44 (VALUE_WEIGHT: revenue_now=5, customer_delivery=4 ...); noetfield-sandbox-private/motor/plans/score`
- **#64 Cost-aware queue** (unlock 3) — Effort is the only cost proxy; no explicit estimated_cost, time_to_value, or dependency_unlocks fields feeding the sort.  
  evidence: `noetfield-sandbox-private/motor/plans/score_plan_queue.py:45 (EFFORT_WEIGHT inverse-feasibility used as cost proxy); noetfield-sandbox-private/motor/plans/score`
- **#73 Provision after commercial gate** (unlock 3) — An approval-gate-before-action pattern exists for outbound sends, but there is no payment_confirmed/admin_approved_pilot gate guarding customer provisioning (no provisioning code at all).  
  evidence: `sina-governance-SSOT/docs/commercial_pulse_loop_v0.1.md (founder_approval_gate before send; approved->send only); sina-governance-SSOT/data/commercial_pulse_que`
- **#139 True decision-point detection** (unlock 3) — No single coded checklist (SSOT-resolvable? testable? has default? reversible? bounded experiment?) that must all be negative before a founder packet is raised; detection is spread across authority_cl  
  evidence: `noetfeld-OS/data/founder-trigger-ledger-v1.json (per-trigger retirement_condition = when it stops being a founder decision); noetfield-sandbox-private/motor/ker`
- **#147 Fast path and deep path** (unlock 3) — Routing by job_class exists, but there is no explicit fast-vs-deep classifier keyed on known-workflow/low-risk/small-context vs unknown/high-risk/research.  
  evidence: `noetfield-sandbox-private/motor/adapters/router.py (routes by job_class/worker_class); noetfield-sandbox-private/motor/kernel/executor.py (deterministic det_pat`
- **#149 Exception queue** (unlock 3) — Handoff/decision and malformed-draft queues exist, but there is no dedicated commercial exception queue categorizing unsupported-integration / contradictory-instructions / regulated-business / high-ca  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py (failures route to handoff_required + push_decision — a decision/exception queue); sina-governance-SSOT/data/`
- **#123 Avoid agent theater** (unlock 2) — Anti-theater is embodied by construction (bounded roles, evidence receipts, no swarm) and documented as doctrine, but there is no explicit theater-detection lint — nothing mechanically flags an over-p  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:19-25 (closed 3-callable-role set, no 20-agent council / CEO agent / swarm consensus); noetfield-sandbox-privat`
- **#135 Agent retirement** (unlock 2) — Retirement exists only as a status value (p0-pgr RETIRED) and as founder-gate delegation conditions (noos ledger retires human gates, not agents). No engine detects unused / duplicate / high-failure /  
  evidence: `sina-governance-SSOT/p0-pgr/P0_PROMPT_REGISTRY_SCHEMA_v1.json (template status enum includes RETIRED); noetfeld-OS/data/founder-trigger-ledger-v1.json (per-trig`
- **#40 Context versioning (policy refs)** (unlock 2) — Reference-by-name-and-version is the house style: packet schema references RUNTIME_CONTINUITY_LAW_v1 and spec_path by name, model-router pins schema/version, governance docs cite POLICY_v1 names rathe  
  evidence: `sina-governance-SSOT/p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json:5; noetfeld-OS/config/model-router.yml:3; sina-governance-SSOT/p0-pgr/P0_DISPATCH_BRAIN_RUNTIME_v1.1`
- **#77 Batch similar work** (unlock 2) — Homogeneous work IS batched deterministically: emit_batch/build_records process the plan queue in one pass, census classifies all candidate docs in a single traversal, and the language_gate has a batc  
  evidence: `noetfield-sandbox-private/motor/plans/emit_headings.py:77; noetfield-sandbox-private/motor/plans/census.py:221; sina-governance-SSOT/language_gate/generate_batc`
- **#125 Prompt prefix caching** (unlock 2) — The prompt is STRUCTURED for prefix caching: intel_low builds `PROMPTS[task] + payload` where PROMPTS holds the stable role+schema prefix and only the job-specific payload varies (packets likewise sep  
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:39; noetfield-sandbox-private/motor/adapters/intel_low.py:121; sina-governance-SSOT/p0-pgr/P0_PROMPT_PACKE`
- **#126 Output length limits** (unlock 2) — Length caps exist but not the doctrine's exact structured limits: packet context_summary is maxLength 1200, intel_low classify rationale is instructed '<=200 chars', decomposition is capped at 6 jobs.  
  evidence: `sina-governance-SSOT/p0-pgr/P0_PROMPT_PACKET_SCHEMA_v1.json:132; noetfield-sandbox-private/motor/adapters/intel_low.py:48; noetfield-sandbox-private/motor/kerne`
- **#30 Receipt deduplication (delta only)** (unlock 2) — The doctrine's rule 'if state unchanged, log only the delta' is not implemented: executor.write_receipt stamps a full new receipt every run; there is no comparison against the last receipt to suppress  
  evidence: `motor/motor/plans/schemas/plan_execution_receipt_v1.schema.json:57 terminal_status NO_CHANGE_ALREADY_SATISFIED (records no-op instead of faking work); motor/mot`
- **#80 Cheap schema repair** (unlock 2) — Repair re-invokes the SAME worker/model rather than a dedicated cheap schema-repair pass; the doctrine wants 'invalid JSON -> cheap schema repair, not re-running the Worker'. No separate low-cost repa  
  evidence: `motor/motor/adapters/intel_low.py invoke() retries once with the validation error appended ('YOUR PREVIOUS OUTPUT WAS INVALID (...) STRICT JSON ONLY') before fa`
- **#88 Flaky test registry** (unlock 2) — Flaky DETECTION exists (SourceA unstable-action scoring; noos transient-retry) but there is NO persistent registry with the doctrine schema (test / flake_rate / known_signature / retry_policy / owner)  
  evidence: `SourceA/scripts/execution_intelligence_v2/risk_scoring.py:9-14 (_unstable detects flapping: >=2 status flips in last 6 runs of an action); noetfeld-OS/scripts/n`
- **#12 No agent-to-agent free chat** (unlock 2) — The motor structurally forbids agent-to-agent chat (all traffic is contracts+outbox/inbox+receipts), but the bounded-consensus sub-clause (max_agents:3, max_rounds:1, disagreement_matrix for security/  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:20; noetfield-sandbox-private/motor/adapters/router.py:1; noetfield-sandbox-private/motor/adapters/handoff.py:2`
- **#24 Compiler shrinks prompt (reduce entropy)** (unlock 2) — The compiler emits a bounded, structured Job Contract (contract+context+acceptance via verification legs+risk gate) and the lint strips P0-CORE leakage, which qualitatively reduces entropy — but nothi  
  evidence: `noetfield-sandbox-private/motor/kernel/intake.py:45; sina-governance-SSOT/scripts/p0pgr_packet_lint_v1.py:100; sina-governance-SSOT/p0-pgr/P0_PROMPT_COMPILER_MV`
- **#114 Ruflo as executor adapter, not brain** (unlock 2) — The motor's adapter+registry architecture (governance→compiler→contract→adapter→worker→verifier→receipt) is exactly the slot where Ruflo would plug in as an executor adapter, so the pattern is ready —  
  evidence: `noetfield-sandbox-private/motor/adapters/router.py:32; noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json:2; SourceA/brain-os/law/enforcement/SOU`
- **#115 Disable default swarm features** (unlock 2) — The motor disables swarm behaviors by construction: no callable worker above W-INTEL-LOW, MOTOR_MAX_PARALLEL=3, bounded max_concurrency, det_patch 'Never merges' (auto_merge:false), no auto_deploy pat  
  evidence: `noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json:2; noetfield-sandbox-private/motor/config/deployment.json:20; noetfield-sandbox-private/motor/`
- **#119 Unknown work isolation** (unlock 2) — Unknown/novel spans are isolated as W-INTEL-LOW proposals (read_only, always a proposal, deterministic validation controls application), which prevents unknown work from writing directly — but there i  
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:14; noetfield-sandbox-private/motor/kernel/intake.py:70; noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:`
- **#120 Research not mixed with execution** (unlock 2) — Research (classify/diagnose) and execution (det_exec/det_patch) are separate job_classes and W-INTEL-LOW output can never mint truth (only a proposal validated deterministically) — so the two are stru  
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:14; noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:29; noetfield-sandbox-private/motor/schemas/job_contr`
- **#53 Founder decision compression** (unlock 2) — Decision items carry kind/detail/receipt/packet but NOT the doctrine's compressed schema: options A/B/C + Recommended + Why(3 lines) + cost/risk delta + consequence-if-no-decision.  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py:181 (store.push_decision with kind/job_id/detail/receipt/packet); noetfield-sandbox-private/motor/adapters/ha`
- **#85 Risk-triggered review** (unlock 2) — Risk gating exists but is not the explicit trigger matrix (T2 review only if auth/payments/secrets/public-claims/db-migration/permissions/deploy/legal changed); no semantic-diff-driven reviewer select  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py (HIGH_RISK set gates founder decision push); noetfield-sandbox-private/motor/plans/acceptance.py:23 (risk-cat`
- **#86 Low-risk auto-promotion** (unlock 2) — Auto-advance on success exists and a retirement path toward autonomous merge is defined, but low-risk classes (typo/docs/fixture) are not auto-promoted to READY_FOR_MERGE by rule; merge stays founder-  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py (ok -> state 'done' automatically; repaired -> re-verify); noetfeld-OS/data/founder-trigger-ledger-v1.json (F`
- **#87 Test selection** (unlock 2) — Acceptance derives a safe command set but does not do change-scoped selection (changed files -> affected packages -> targeted tests -> full suite only before promotion).  
  evidence: `noetfield-sandbox-private/motor/plans/acceptance.py:23 (derives test/lint/typecheck/build commands from repo-observed tooling, allowlisted, never from prose)`
- **#138 Founder workload metric** (unlock 2) — The ledger tracks founder trigger retirement toward autonomy but does not measure the doctrine's workload metric (interruptions/clarifications/context-rebuilds/decision-repeats) or an hours/day target  
  evidence: `noetfeld-OS/data/founder-trigger-ledger-v1.json (triggers with class, status, evidence_counter, retirement_condition, target_status; shadow_decision_threshold:1`
- **#145 Opportunity capture cheap** (unlock 2) — Plan/opportunity capture is deterministic and cheap, but there are no commercial sensors (missed call / checkout failure / partner application) and no high-confidence->cloud escalation rule.  
  evidence: `noetfield-sandbox-private/motor/plans/census.py (deterministic, read-only enumeration; no LLM for numeric values); noetfield-sandbox-private/motor/plans/score_p`
- **#146 Perishable intent priority** (unlock 2) — Generic urgency boosts exist, but perishable commercial intents (new paid lead / missed call / booking / checkout failure / demo completion) are not modeled as a fast lane ahead of technical backlog.  
  evidence: `noetfield-sandbox-private/motor/plans/score_plan_queue.py:46 (URGENCY_POINTS: customer_blocking+4, active_incident+5, critical_deadline+5); sina-governance-SSOT`
- **#113 Avoid framework tax** (unlock 1) — The motor is a deliberately minimal vendor-free kernel (its own scheduler/router/statestore) which embodies avoiding framework tax, but the point is specifically about admitting a framework (Ruflo) on  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:1; noetfield-sandbox-private/motor/adapters/router.py:1; noetfield-sandbox-private/motor/registry/ADAPTER_REGIS`
- **#121 Time-boxed exploration** (unlock 1) — Exploration is cost/attempt-bounded (budget.max_cost_usd, retry once then fail, timeout_seconds) but the doctrine's exploration-specific limits (max_sources:10, max_model_calls:3, max_output:2 pages)   
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:14; noetfield-sandbox-private/motor/kernel/intake.py:36; noetfield-sandbox-private/motor/schemas/job_contr`

### DONE (49)

- **#3 Model escalation not uniformity (tier ladder)** (unlock 5) — The locked 6-name ladder (T0/T1/T1L/T2/Manual/Deterministic) is collapsed to 3 in every system: motor has rank0/rank1/handoff, p0-pgr has cheap/capable/premium. No distinct T1L (long-context) tier exi  
  evidence: `noetfield-sandbox-private/motor/adapters/router.py:13 (MAX_AUTOMATIC_RANK=1, 'law not config'); noetfield-sandbox-private/motor/adapters/router.py:47 (raises Ro`
- **#8 Deterministic First** (unlock 5) — Fully implemented in the motor; the doctrine's boundary (LLM only for cause/design/ambiguity) is structurally enforced. No gap of substance.  
  evidence: `motor/motor/adapters/det_exec.py:1 ("No LLM anywhere in this module") — probe/lane_checks/verify_recompute/verify_ci/verify_edge/closure all pure; motor/motor/a`
- **#29 Machine-readable receipts w/ schema** (unlock 5) — sandbox_receipt_v1 (the motor's runtime receipt) is written by executor.py but has no committed JSON Schema file alongside plan_execution_receipt_v1; validation is by construction, not by a schema doc  
  evidence: `motor/motor/plans/schemas/plan_execution_receipt_v1.schema.json; governance/p0-pgr/P0_EXECUTION_RECEIPT_SCHEMA_v1.json (schema/packet_id/quality_state/evidence_`
- **#79 Structured output** (unlock 5) — intel_low uses hand-rolled required-key checks rather than full JSON-Schema validation (its own comment says 'full JSON-Schema validation happens in verify'). Adequate but not schema-library-strict.  
  evidence: `motor/motor/adapters/intel_low.py TASK_SCHEMAS + 'STRICT JSON ONLY' prompts + _validate() required-key enforcement; motor/motor/schemas/job_contract.schema.json`
- **#23 Prompt compilation pipeline** (unlock 5) — Motor intake does normalize→decompose→classify(risk in W-INTEL-LOW output)→resolve target→generate contract→dispatch, and p0pgr does evidence→packet→lint→route; but voice/text normalization and an exp  
  evidence: `noetfield-sandbox-private/motor/kernel/intake.py:70; noetfield-sandbox-private/motor/adapters/intel_low.py:44; sina-governance-SSOT/scripts/p0pgr_cycle_v1.py:63`
- **#41 SSOT enforcement (one owner per domain)** (unlock 5) — Domain ownership is declared (SG registry: one actor·one repo·one scope; authority.yaml machine SSOT; motor targets[] per repo), but pricing SSOT and product-promise/fulfillment owners named in the do  
  evidence: `sina-governance-SSOT/ssot/MULTI_REPO_WORKER_REGISTRY_v1.md:5; SourceA/brain-os/system/authority.yaml:1; SourceA/brain-os/system/EXECUTION_AUTHORITY_MAP_LOCKED_v`
- **#1 Agent as role not process** (unlock 4) — Doctrine's exact per-agent contract fields (Allowed Inputs / Allowed Tools / Required Output Schema) are expressed structurally (capabilities[] + TASK_SCHEMAS + path guard) rather than as one declared  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:19-27 (worker classes as closed set with class|mode|role); noetfield-sandbox-private/motor/registry/ADAPTER_REG`
- **#25 Separate thinking / acting / verifying** (unlock 4) — Thinking is quarantined into W-INTEL-LOW-as-proposal and verification into separate workflow identities — fully separated. No gap of substance; only W-VERIFY-EDGE (the sole PASS minter) is spec'd-but-  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:74-79 ('Builder and verifier are separate graph jobs'; 'No model output ever mints truth'); noetfield-sandbox-p`
- **#58 Capability-based permissions** (unlock 4) — The doctrine's literal planner(write:false)/worker(write:scoped)/verifier(write:false,test:true) capability triples are enforced structurally (proposal-only intel, path guard, read-only verifiers) rat  
  evidence: `noetfield-sandbox-private/motor/adapters/det_patch.py:36-46 (_guard fail-closed path allowlist; empty=deny-all = worker write:scoped/branch_only); noetfield-san`
- **#116 Agent registry with cost_class** (unlock 4) — Motor's registry uses class_rank+est_cost (semantic cost_class) but not the doctrine's literal field names default_model_tier/invoke_when/max_calls. The governance p0-pgr prompt registry that DOES car  
  evidence: `noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json (per worker: class_rank 0/1, est_cost_usd_per_job, max_concurrency, reliability, health); noet`
- **#110 Vendor-neutral routing** (unlock 4) — Vendor-neutrality as a structural constraint (no hardcoded provider anywhere in code/registry) is fully achieved. But the ACTIVE part of the doctrine — a router that actually switches among OpenAI/Ant  
  evidence: `noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json:3 ('referenced by ENV VARIABLE NAME, never by value or vendor'); noetfield-sandbox-private/mot`
- **#5 Context slicing** (unlock 4) — Slicing is structural (each Job Contract carries only its own instruction+context dict; the sole LLM adapter intel_low.invoke sends `instruction + json.dumps(context)`, never whole repo/conversation;   
  evidence: `noetfield-sandbox-private/motor/kernel/intake.py:50; noetfield-sandbox-private/motor/kernel/executor.py:141; noetfield-sandbox-private/motor/schemas/job_contrac`
- **#9 Don't guess provable facts** (unlock 4) — Enforced everywhere a tool can prove the fact. No material gap.  
  evidence: `motor/motor/adapters/det_exec.py verify_recompute recomputes summary from checks[] instead of trusting claim; verify_ci polls real GitHub check-runs; probe reco`
- **#26 Independent verification on diff only** (unlock 4) — verify_edge requires an external edge worker (MOTOR_EDGE_VERIFIER_URL) that may be unset; then that leg fails closed rather than running. Independence is real but partly gated on deployment.  
  evidence: `motor/motor/adapters/det_exec.py verify_recompute: 'Independent recount of a prior receipt's checks[]; separate workflow identity'; motor/motor/schemas/job_cont`
- **#28 Receipt by code, narrative by model** (unlock 4) — Motor goes further than the doctrine (even promotion_recommendation is code, not model). No gap; if anything the model-authored narrative slot is unused.  
  evidence: `motor/motor/kernel/executor.py build_receipt: checks[], summary{total,passed,failed}, sha, http_status, promotion_recommendation all code-generated; motor/motor`
- **#49 Dependency-based decomposition** (unlock 4) — decompose() builds a real dependency graph (depends_on wired from intel-low depends_on_titles, skeleton->applier links, closure depends on all); scheduler promotes queued->ready only when all deps don  
  evidence: `noetfield-sandbox-private/motor/kernel/intake.py:99; noetfield-sandbox-private/motor/kernel/scheduler.py:60; noetfield-sandbox-private/motor/plans/materialize.p`
- **#42 Authority check before edit** (unlock 4) — det_patch enforces authority_class==bounded_write + fail-closed path guard, and the packet linter enforces authority_scope==deploy→FOUNDER_ONLY; but the doctrine's explicit duplicate_control_plane_ris  
  evidence: `noetfield-sandbox-private/motor/adapters/det_patch.py:69; noetfield-sandbox-private/motor/adapters/det_patch.py:38; sina-governance-SSOT/scripts/p0pgr_packet_li`
- **#43 No second control plane** (unlock 4) — Extension-not-clone is enforced structurally (new worker=one registry row+one binding; NOOS one_law: SourceA phase_reconciler is sole control authority; one-writer-per-cell), but there is no automated  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:10; noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json:2; noetfeld-OS/data/noos-integrator-contr`
- **#118 Deterministic workflow compiler** (unlock 4) — Deterministic task-type→workflow mapping exists (motor DET_LEXICON maps heading phrases→probe/smoke job_class with no model; p0pgr ROUTE_VERDICT maps execution_mode→dispatch verdict), but the known-wo  
  evidence: `noetfield-sandbox-private/motor/kernel/intake.py:33; noetfield-sandbox-private/motor/kernel/intake.py:70; sina-governance-SSOT/scripts/p0pgr_cycle_v1.py:34`
- **#2 Template != execution (registry many, invoke few)** (unlock 3) — Doctrine default '1 Planner + 1 Worker + 1 Verifier; +1 Repair on fail; +1 Adversarial Reviewer on risk' is implemented except the risk-triggered Adversarial Reviewer — grep finds it only as an unbuil  
  evidence: `noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json (7 declared classes = available); noetfield-sandbox-private/motor/adapters/router.py:43-71 (di`
- **#57 Per-agent secrets (blast radius)** (unlock 3) — Scoping is declared (each worker sees only its own binding_env) but there is no runtime enforcement that a worker process cannot read another worker's env var — isolation is by convention/adapter disc  
  evidence: `noetfield-sandbox-private/motor/registry/ADAPTER_REGISTRY_v2.json (binding_env per worker: W-DET-EXEC [], W-DET-PATCH ['MOTOR_REPO_TOKEN'], W-INTEL-LOW ['MOTOR_`
- **#81 Separate content generation from validation** (unlock 3) — Fully realized in two independent subsystems (motor and governance language/commercial gates). No material gap.  
  evidence: `motor/motor/adapters/intel_low.py (generation/proposals) is fully separate from motor/motor/adapters/det_exec.py + verify (validation); governance/scripts/comme`
- **#128 Human view from machine artifact** (unlock 3) — Realized for the motor control panel and language gate. Governance p0-pgr execution receipts have no auto-generated markdown view yet (JSON only), so the pattern is not uniform across subsystems.  
  evidence: `motor/motor/panel/build_panel.py writes STATUS.md (human) + status.json (machine mirror) from the same receipt-derived facts, 'no self-report'; motor/motor/STAT`
- **#13 Single writer rule** (unlock 3) — Single-writer is guaranteed for scheduling decisions (serialized tick) and for state via compare-and-set; the GitStore fallback is only race-safe under the serialized tick + disjoint executor writes,   
  evidence: `noetfield-sandbox-private/motor/kernel/scheduler.py:1; noetfield-sandbox-private/motor/statestore/store.py:19; noetfield-sandbox-private/motor/statestore/store.`
- **#17 Budget-per-job** (unlock 3) — budget{max_cost_usd,max_repair_cycles} is a required contract field; router throttles when est_cost>budget and executor enforces max_repair_cycles. Gap: cost is estimated per-worker (est_cost_usd_per_  
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json:38; noetfield-sandbox-private/motor/adapters/router.py:60; noetfield-sandbox-private/motor/kern`
- **#60 Irreversible action gate** (unlock 3) — Irreversible actions are gated: STANDING_EXCLUSIONS forbid merge/deploy/spend/send/permission-change on every heading; authority_class=founder_only and high-risk refusals route to push_decision (found  
  evidence: `noetfield-sandbox-private/motor/plans/materialize.py:15; noetfield-sandbox-private/motor/kernel/executor.py:180; noetfield-sandbox-private/motor/MOTOR_SPEC_v2.m`
- **#18 Cause-based retry** (unlock 3) — The doctrine's explicit guard 'if no variable changed, retry is meaningless' is not enforced as a precondition — repair always emits a proposal even when the diagnosis yields no actionable change. Log  
  evidence: `noetfield-sandbox-private/motor/repair/repair.py:1 (docstring: "Repair pipeline — generation, not retry"); noetfield-sandbox-private/motor/repair/repair.py:13-2`
- **#10 Summary passing (compressed handoff)** (unlock 3) — The Job Contract carries task_id/instruction/context/verification_contract/expected_outputs and handoff packets carry reason+failure_evidence+result_inbox, but there is no explicit closed field set na  
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json:9; noetfield-sandbox-private/motor/adapters/handoff.py:16; sina-governance-SSOT/p0-pgr/P0_EXECU`
- **#14 Parallelize only independent work** (unlock 3) — Independence is enforced by depends_on promotion + one-writer-per-cell + branch-scoped writes; there is no automatic static check that two concurrently-ready jobs do not touch a shared SSOT surface (n  
  evidence: `noetfield-sandbox-private/motor/kernel/scheduler.py:56; noetfield-sandbox-private/motor/adapters/intel_low.py:44; noetfield-sandbox-private/motor/config/deploym`
- **#45 Thin slice canary** (unlock 3) — The proof driver executes the exact thin slice (1 heading→intake→parallel jobs→branches→PRs→CI→verifier→bundle) and real proof bundles exist; the missing leg is W-VERIFY-EDGE minting PASS — bundles cu  
  evidence: `noetfield-sandbox-private/motor/proof/run_proof.py:1; noetfield-sandbox-private/motor/proof/bundles/29174463135/PROOF_BUNDLE.json; noetfield-sandbox-private/mot`
- **#46 Canary before automation** (unlock 3) — The ladder (manual/shadow → bounded → scheduled → autonomy) is explicit: p0pgr runs shadow (route-only, cost 0.0), motor state_backend has canary=git before durable; but promotion from one rung to the  
  evidence: `sina-governance-SSOT/p0-pgr/P0_PROMPT_COMPILER_MVP_PLAN_v1.md; sina-governance-SSOT/scripts/p0pgr_cycle_v1.py:1; noetfield-sandbox-private/motor/config/deployme`
- **#124 Short persona prompts** (unlock 2) — Motor prompts already match the doctrine template (Role / strict output / bounds). The governance packet compiler enforces constraints but there is no explicit max-length/no-persona lint on compiled p  
  evidence: `noetfield-sandbox-private/motor/adapters/intel_low.py:39-59 (PROMPTS are terse task specs: role + strict-JSON schema + input, no long persona); noetfield-sandbo`
- **#38 Cloud only for value-dense steps** (unlock 2) — Enforcement of 'never listing/counting/formatting to cloud' is doctrinal + tier0-first rather than a hard classifier that rejects a cloud dispatch for a trivially-deterministic job_class. A misclassif  
  evidence: `noetfield-sandbox-private/products/sandbox-first-production-law-v1/COST_INTELLIGENT_EXECUTION_POLICY_v1.md:32-35 (tier0 default; expensive model exception, rece`
- **#99 Escalation by failure-type not feeling** (unlock 2) — The motor cannot escalate at all automatically (structural ceiling), so the failure-typed escalation contract lives in the sandbox policy + handoff packets rather than an executing escalator. The doct  
  evidence: `noetfield-sandbox-private/products/sandbox-first-production-law-v1/COST_INTELLIGENT_EXECUTION_POLICY_v1.md:101 (escalation_reason MUST be a real FAILED cheaper `
- **#100 Premium only on bottleneck** (unlock 2) — Enforced per-lane/per-receipt, which correctly isolates the bottleneck. There is no explicit 'apply tier1 -> tier2 one conflict -> tier1 apply' orchestration primitive; it is assembled from separate j  
  evidence: `noetfield-sandbox-private/products/sandbox-first-production-law-v1/COST_INTELLIGENT_EXECUTION_POLICY_v1.md:190-209 (escalation algorithm: tier2 only for the spe`
- **#112 Degraded mode** (unlock 2) — Degraded-continue behavior is real (deterministic scans/queue/receipts keep running; premium pauses when budget/authority is blocked). But it is assembled from separate mechanisms (NOOS status enum, p  
  evidence: `noetfeld-OS/infrastructure/supabase/migrations/0014_factory_cycle_status_degraded.sql:1-20 (first-class 'degraded' status: partial/failed steps, truth preserved`
- **#89 Tool output compression** (unlock 2) — Output compression is real and multi-layered: SourceA's execution_spine keeps only stdout[-12000:]/stderr[-8000:] plus exit_code and a one-line error_signature; motor det_exec keeps `exit {code}` + la  
  evidence: `SourceA/scripts/execution_spine/writer.py:44; noetfield-sandbox-private/motor/adapters/det_exec.py:63; noetfield-sandbox-private/motor/kernel/executor.py:63; no`
- **#15 Branch-per-job** (unlock 2) — Fully implemented: every write lands on branch automation/<job-id>, never a default/protected branch, never merges. No gap.  
  evidence: `noetfield-sandbox-private/motor/adapters/det_patch.py:73; noetfield-sandbox-private/motor/adapters/det_patch.py:6; noetfield-sandbox-private/motor/install/app-m`
- **#16 Immutable job contract** (unlock 2) — A single worker-agnostic contract (additionalProperties:false, all required fields, no vendor/model fields) is the sole work packet; run_id (not the contract) changes per lease. Schema is defined and   
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json:1; noetfield-sandbox-private/motor/kernel/intake.py:73; noetfield-sandbox-private/motor/adapter`
- **#55 Partial success states** (unlock 2) — Rich non-binary terminal/degraded state set exists: queued/ready/leased/running/verifying/done/repair_pending/handoff_required/dead_letter/decision_pending. On failure the motor parks ONLY the affecte  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:50; noetfield-sandbox-private/motor/kernel/scheduler.py:11; noetfield-sandbox-private/motor/kernel/executor.py:`
- **#31 Event-driven not constant polling** (unlock 2) — Motor is fully event-driven; NOOS loops are dispatch/event-triggered. Remaining periodic crons (governance census/staleness weekly, sg-auth every 6h, brain-loop every 30m, motor-watchdog every 30m) ar  
  evidence: `noetfield-sandbox-private/.github/workflows/motor-tick-v2.yml:1-12 (workflow_run on intake/executor/plan-intake completion; header: 'No schedules exist anywhere`
- **#11 Artifact-based communication** (unlock 2) — Job Contract, Patch(PR), Verification Receipt and Handoff Packet are all real artifacts; a formal named 'Promotion Packet' schema is only implied by receipts, not a distinct schema in the motor.  
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json; noetfield-sandbox-private/motor/adapters/handoff.py:16; noetfield-sandbox-private/motor/adapte`
- **#44 Smallest corrective move** (unlock 2) — The repair pipeline is generation-not-retry, bounded (max_repair_cycles=2, constrained to allowed_paths) and the p0pgr continuity law files a repair_candidate rather than freezing the lane — embodying  
  evidence: `noetfield-sandbox-private/motor/MOTOR_SPEC_v2.md:44; noetfield-sandbox-private/motor/repair/repair.py; sina-governance-SSOT/scripts/p0pgr_packet_lint_v1.py:8`
- **#54 No-blocker doctrine** (unlock 2) — Behavior matches (degrade/tag/handoff/receipt); the explicit hard-block whitelist (money/contract/credential/irreversible-send/authority-change) is not enumerated as a single policy constant.  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py:180-187 (governance refusal -> receipt + handoff_required, never silent, never auto-escalate); noetfield-sand`
- **#66 Commercial surface separate from core** (unlock 2) — Separation is real at config + lane level; SourceB storefront/lead/checkout runtime itself is not local (reference-only).  
  evidence: `noetfield-sandbox-private/motor/config/deployment.json (targets[]: Noetfield-Systems/SourceB bounded to automation-canary/receipts/control, distinct from self t`
- **#75 Idempotency** (unlock 2) — General idempotency is solid; not yet applied to a paid/provisioning create path (none exists).  
  evidence: `noetfield-sandbox-private/motor/plans/materialize.py:3-4,119 (deterministic heading_id IS the idempotency key; create_heading idempotent); noetfield-sandbox-pri`
- **#140 Reversible defaults** (unlock 2) — Reversible-by-default + gate-for-irreversible is enforced; the reversible/irreversible taxonomy is implicit in path/authority rules rather than a named list.  
  evidence: `noetfield-sandbox-private/motor/schemas/job_contract.schema.json (authority_class default surface bounded_write; founder_only reserved); noetfield-sandbox-priva`
- **#78 Micro-batching 5-20** (unlock 1) — The 20-item micro-batch cap is implemented exactly to spec: MAX_ISSUES=20 caps emitted headings to min(20, eligible) homogeneous queue items, and intel_low decomposition is capped at 6 jobs (jobs[:6])  
  evidence: `noetfield-sandbox-private/motor/plans/emit_headings.py:27; noetfield-sandbox-private/motor/plans/emit_headings.py:159; noetfield-sandbox-private/motor/kernel/in`
- **#127 Evidence links not restating** (unlock 1) — Evidence-by-reference is pervasive and load-bearing: jobs carry receipts[] as a list of file PATHS (not inlined content); the diagnose schema requires evidence_refs[]; the governance packet requires e  
  evidence: `noetfield-sandbox-private/motor/kernel/executor.py:195; noetfield-sandbox-private/motor/adapters/intel_low.py:35; sina-governance-SSOT/p0-pgr/P0_PROMPT_PACKET_S`

### NOT_LOCAL (1)

- **#148 SourceB commercial fast path** (unlock 5) — SourceB is referenced only as a motor write target; the setup->validate->config->browser-demo->approval/payment->provision->test->activate->receipt fast path is not implemented in any local repo.  
  evidence: `noetfield-sandbox-private/motor/config/deployment.json (Noetfield-Systems/SourceB is a bounded write target only: automation-canary/receipts/control); noetfield`

