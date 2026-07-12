<!--
NOOS-DOCTRINE
doc_type: AGENTIC_RUNTIME_ECONOMICS_DOCTRINE
status: LOCKED
authority: founder-authored (Sina Kazemnezhad)
locked_at: 2026-07-12
scope: Noetfield / SourceA / SourceB / NOOS motor runtime
lock_receipt: receipts/doctrine/AGENTIC_COST_EFFICIENCY_DOCTRINE_v1_LOCKED.lock.json
rule: canonical; supersede with a new version + founder approval — never mutate in place
-->

# AGENTIC COST-EFFICIENCY & CAPABILITY DOCTRINE v1 (LOCKED)

> **LOCKED — founder doctrine.** Canonical economic doctrine for our agentic runtime. Do not edit
> in place; supersede with a new version. Implementation status is tracked in the companion
> disk-analysis report, not in this file.

فهرست جامع ترفندهای کاهش هزینه و افزایش توان Agentic برای سیستم‌های ما
هدف این سند این نیست که «Agentهای بیشتری» بسازیم. هدف این است که:
کار بیشتری با مدل کمتر، Context کمتر، Retry کمتر، دخالت کمتر Founder و Evidence بیشتر انجام شود.
معماری هدف برای Noetfield / SourceA / SourceB باید این باشد:
Founder Heading
      ↓
Intake / Compiler
      ↓
Classification + Cost Routing
      ↓
Deterministic Preparation
      ↓
Small Specialist Workers
      ↓
Sandbox Execution
      ↓
Tests + Independent Verification
      ↓
Receipt + Promotion Packet
      ↓
Founder only for real decisions

---

1. Agent را «نقش» تعریف کن، نه Process دائمی — هر Agent فقط Role / Allowed Inputs / Allowed Tools / Required Output Schema. اصل: Agent باید function-like باشد، نه employee-like.
2. Agent Template با Agent Execution فرق دارد — Available Agents ≠ Invoked Agents. Default هر Job معمولی: 1 Planner + 1 Worker + 1 Deterministic Verifier؛ فقط در صورت شکست +1 Repair؛ فقط در صورت ریسک +1 Adversarial Reviewer.
3. Model Escalation، نه Model Uniformity — T0/T1/T1L/T2/Manual Premium/Deterministic. مدل قوی‌تر فقط با receipt `status: ESCALATE_REQUIRED` (+reason, target_tier, risk_if_not_escalated, files_in_scope, estimated_cost). Agent نباید بی‌صدا premium انتخاب کند.
4. Cheap First Pass — قبل از Worker اصلی، مدل ارزان Job را کوچک می‌کند (project/repo/scope/exclude/risk/required_workflow/founder_gate/model_tier).
5. Context Slicing — هر Agent فقط Job Contract + relevant files + relevant SSOT excerpt + current diff + last relevant receipt. نه کل repo/conversation/docs.
6. Context Budget برای هر Agent — Classifier 4–8K, Planner 12–24K, Worker 20–60K, Reviewer diff+criteria, Receipt Writer structured only. عبور از بودجه → summarize/retrieve narrowly، نه بزرگ‌کردن خودکار.
7. Retrieval قبل از Reading — file tree → grep/ripgrep → dependency map → targeted files → targeted line ranges.
8. Deterministic First — git status/diff, inventory, hash/dup detection, schema validation, JSON parse, test/lint/type-check, path/branch/commit/PR checks, receipt-field validation, dep-version extraction, health checks → بدون LLM. LLM فقط برای علت شکست/طراحی اصلاح/ambiguity/architecture/copy/commercial judgment.
9. LLM نباید Factهایی را حدس بزند که ابزار می‌تواند اثبات کند — تست را اجرا کن، فایل را بررسی کن، remote را چک کن.
10. Summary Passing، نه Conversation Passing — هر مرحله یک handoff فشرده (task_id/status/decision/files/constraints/acceptance_tests/open_questions).
11. Artifact-based Communication — Job Contract / Plan / Patch / Test Result / Verification Receipt / Promotion Packet به‌جای multi-agent chat.
12. Conversation بین Agentها ممنوع/محدود — No agent-to-agent free chat؛ فقط structured handoffs. Consensus فقط برای امنیت/governance/irreversible/high-value/legal با max_agents:3، max_rounds:1، output: disagreement_matrix.
13. Single Writer Rule — One file / one branch / one active writer. بقیه فقط پیشنهاد/review/test/receipt.
14. Parallelize Independent Work، نه همه‌چیز — فقط شاخه‌های با ownership مجزا. shared navigation/schema/pricing SSOT/deploy config/auth core موازی تغییر نکنند.
15. Branch-per-Job — `automation/<job-id>` یا worktree مستقل (rollback ساده، conflict قابل مشاهده، verifier مستقل، provenance روشن).
16. Immutable Job Contract — objective/scope_in/scope_out/allowed_files/forbidden_actions/acceptance_criteria/risk_class/budget/max_retries/founder_gate. تغییر scope → Job جدید. Scope drift = token burn.
17. Budget-per-Job — max_llm_calls/worker_calls/reviewer_calls/retries/context_tokens/estimated_cost. سقف شکست → STOP_AND_PACKETIZE.
18. Retry باید علت‌محور باشد — classify failure → change one variable → retry once. اگر متغیری تغییر نکرده، Retry بی‌معناست.
19. Retry Ladder — Syntax→deterministic/T0; Test→triager/T1; Architecture→T2; Missing credential→founder_blocked; Vendor outage→defer+receipt; Ambiguous business→promotion packet.
20. Failure Caching — failure_signature (repo/error/workflow_step)؛ تا رفع نشدن blocker، همان تلاش دوباره اجرا نشود؛ فقط blocker receipt refresh.
21. Negative Knowledge Base — چه چیزهایی قبلاً جواب نداده‌اند (Do not clone sandbox-private to create second motor authority؛ Do not use local scratch as SSOT؛ Do not deploy SourceB storefront before Stripe/auth gates؛ …).
22. Success Pattern Library — الگوهای موفق ذخیره (مثلاً cloudflare_worker_release: tests/deploy/health_check/purge/receipt) تا دوباره طراحی نشوند.
23. Prompt Compilation — voice/text → normalize → extract intent → resolve project → classify risk → identify SSOT → generate contract → choose workflow → dispatch.
24. Compiler باید Prompt را کوچک‌تر کند، نه بزرگ‌تر — خروجی: Job Contract + Relevant Context + Acceptance Criteria + Risk Gates. entropy را کاهش دهد.
25. Separate Thinking from Acting — Planner/Worker/Verifier جدا؛ Verifier تا حد امکان deterministic.
26. Independent Verification فقط روی Diff — Job Contract + changed files + diff + test results + invariants.
27. Verification Pyramid — schema → static → lint → type-check → unit → integration → e2e → LLM review → human approval؛ ارزان اول.
28. Receipt by Code، Narrative by Model — factها را code تولید کند؛ مدل فقط summary/remaining_risks/promotion recommendation.
29. Receipts باید ماشین‌خوان باشند — schema دار (receipt_type/job_id/status/evidence/limitations/next_state).
30. Receipt Deduplication — اگر وضعیت تغییر نکرده، فقط delta ثبت شود.
31. Event-driven به‌جای Constant Polling — git push→verifier, PR→review, test fail→triager, lead→fulfillment, payment→provisioning. Polling فقط بدون webhook.
32. Adaptive Polling — high-change hourly / stable daily / dormant weekly. NOOS باید evidence داشته باشد frequency واقعاً ROI دارد.
33. Schedule ROI Preflight — purpose/expected_value/estimated_monthly_cost/frequency/why_not_event_driven/why_not_manual/fallback/stop_condition. در rush، Schedule جدید بدون preflight ممنوع.
34. Stop Condition برای هر Loop — PR merged / blocker resolved / 3 identical failures / no state change 7d / budget exceeded / founder decision.
35. Heartbeat بدون LLM — timestamp/queue depth/last success/last fail/worker health/credential expiry deterministic؛ LLM فقط anomaly summary.
36. Liveness با External Receipt — cron اجرا‌شدن ≠ زنده‌بودن. Evidence واقعی: new lead / PR created / test repaired / deploy verified / opportunity classified / founder packet.
37. Local LLM برای کارهای حجیم کم‌ریسک — Qwen3-14B: triage/classification/first-pass summary/log clustering/dup detection/field extraction/tagging/inventory/context packets. بدون verifier authority برای deploy/security/financial/public copy/architecture/merge.
38. Cloud Model فقط برای Value-dense Steps — architecture/hard debugging/commercial positioning/adversarial security/governance conflict/irreversible packet. نه listing/counting/formatting/url-check/key-rename.
39. Cache کردن Contextهای پایدار — repo ownership/canonical paths/deploy topology/pricing SSOT/branch policy/model policy/risk matrix/allowed tools → registry با version/hash reference.
40. Context Versioning — فقط reference (Apply MODEL_ESCALATION_POLICY_v1 …)؛ در صورت نیاز، بخش مرتبط retrieve شود.
41. SSOT Enforcement — یک owner per domain (Governance→sina-governance-SSOT، Motor runtime→canonical repo، SourceB product→SourceB، pricing→pricing SSOT، Sandbox→SANDBOX، local scratch→non-authoritative). Agent باید authority را resolve کند.
42. Authority Check قبل از Edit — repo_authority_confirmed/target_branch_confirmed/file_owner_confirmed/duplicate_control_plane_risk:false.
43. No Second Control Plane — Extend the canonical motor; do not clone authority. control plane دوم = reconciliation/sync/conflicting states/duplicated schedules+agents/uncertain ownership.
44. Smallest Corrective Move — وقتی evidence ناقص است redesign ممنوع؛ Repair the missing proof, not the whole architecture.
45. Thin Slice Canary — 1 heading → compiler → 2 jobs → 2 branches → commits → PRs → CI → verifier → promotion packet.
46. Canary قبل از Automation — Manual proof → bounded automation → scheduled automation → broader autonomy.
47. Test Fixtureهای کوچک و ثابت — ورودی reproducible کوچک، نه «redesign entire company».
48. Bounded Change Policy — max_files_changed:8 / max_lines_changed:500 / allowed_directories. بزرگ‌تر → split.
49. Work Decomposition بر اساس Dependency — کمترین Context overlap؛ shared contract (price IDs/checkout schema/fulfillment states) ابتدا قفل شود.
50. Integrator فقط در انتها — Lanes produce contracts+receipts؛ Integrator interfaces را چک و merge/return conflicts.
51. Interface Contract قبل از Parallel Work — endpoint/request_schema/response_schema/error_states/ownership ثابت شود.
52. Founder Heading باید از Founder Questions جدا شود — Founder فقط برای ambiguity/contradiction/commercial/legal-public/money-contract/final merge-deploy-promotion/نبود اولویت. نه filename/test path/branch/package manager/lint/obvious detail.
53. Founder Decision Compression — Decision required A/B/C + Recommended + Why(3 lines) + cost/risk difference + what happens if no decision.
54. No-blocker Doctrine — default: degrade/tag/sandbox/retry bounded/route around/receipt. Hard block فقط deploy-without-authority/money/contract/sensitive credential/irreversible send/authority change/high-level merge/legal-public high risk.
55. Partial Success States — PLANNED/IMPLEMENTED_NOT_RUN/TESTED_LOCAL/VERIFIED/BLOCKED_CREDENTIAL/BLOCKED_EXECUTOR_ENDPOINT/READY_FOR_PROMOTION/DEPLOYED_UNVERIFIED/DEPLOYED_VERIFIED.
56. Missing Capability باید Exact Interface تولید کند — status: BLOCKED_EXECUTOR_ENDPOINT + required_interface(input/output) + required_secret + required_worker. blocker → buildable task.
57. Secrets را به همهٔ Agentها نده — هر Agent فقط secret خودش. کم‌کردن blast radius.
58. Capability-based Permissions — planner(write:false, shell:read_only, network:false) / worker(write:scoped, git_commit:branch_only, deploy:false) / verifier(write:false, test:true, read_diff:true).
59. Dry-run به‌عنوان Default — deploy plan/email recipients/db migration/bulk label/pricing/redirect ابتدا dry-run (outcome+diff).
60. Irreversible Action Gate — send/merge/deploy/charge/delete/publish/change authority/rotate credentials هرگز از raw prompt؛ فقط از verified packet.
61. Separate Detection from Action — Sensor→Observation, Classifier→Issue, Compiler→Job, Worker→Change, Verifier→Evidence.
62. Opportunity Deduplication — cluster key: project+surface+issue_type+target+normalized_signature → یک issue، یک queue item.
63. Priority بر اساس Commercial Value — commercial_impact × urgency × confidence × reversibility ÷ cost.
64. Cost-aware Queue — expected_value/estimated_cost/time_to_value/dependency_unlocks؛ ارزان و unlockکننده زودتر.
65. Dependency Unlock Score — standing machine identity/callable executor/canonical plan queue/Stripe webhook امتیاز unlock بالا.
66. Commercial Surface از Core Runtime جدا شود — SourceB: simple storefront → lead/checkout → bounded fulfillment؛ SourceA/NOOS به‌تدریج قوی‌تر.
67. Productized Workflow، نه Generic Platform — «AI Receptionist Setup» نه «build any agent for any business».
68. Customer Configuration به‌جای Human Intake — مشتری در setup wizard وارد کند → config schema.
69. Configuration Templates — per vertical (dental/restaurant/real estate/home services/legal/medical)؛ runtime مشترک.
70. Default-heavy UX — فقط موارد تجاری واقعی از مشتری.
71. Progressive Configuration — Stage1 demo / Stage2 paid essentials / Stage3 optional optimization.
72. Browser Demo قبل از Phone Provisioning — create → browser voice test → tune → payment → bind phone.
73. Provisioning بعد از Commercial Gate — فقط بعد از payment_confirmed یا admin_approved_pilot.
74. Fulfillment State Machine — requested→approved→provisioning_pending→started→done→trial_active→cancelled/expired.
75. Idempotency — create_phone_agent(customer_id) اگر موجود → return existing.
76. Idempotency Key برای Actionهای پولی — customer_id + action_type + version.
77. Batch کردن کارهای مشابه — classify/summarize/scan یک‌بار؛ فقط وقتی Context بزرگ نمی‌شود.
78. Micro-batching — 5–20 homogeneous items، نه 1000 سند نامرتبط.
79. Structured Output — JSON/YAML schema (parsing ساده، retry کم، hallucination کم، handoff کوچک).
80. Schema Repair با مدل ارزان — invalid JSON → cheap schema repair، نه اجرای دوبارهٔ Worker.
81. Separate Content Generation from Validation — Writer copy؛ deterministic checker (required sections/banned claims/CTA/price consistency/limits).
82. Claims Registry — هر ادعای public با source/status (مثلاً "24/7" supported؛ "unlimited calls" cost_risk:unbounded, approval_required).
83. Pricing SSOT — pricing config/checkout/landing/FAQ/receipt همه از یک SSOT.
84. Semantic Diff — Pricing/Auth/public endpoint/secrets/DB schema changed؟ reviewer فقط ریسک relevant.
85. Risk-triggered Review — T2 فقط اگر auth/payments/secrets/public claims/db migration/permissions/deploy/legal copy تغییر کرد.
86. Low-risk Auto-promotion — typo/internal docs/formatting/fixture/receipt تا READY_FOR_MERGE؛ merge طبق authority.
87. Test Selection — changed files → affected packages → targeted tests → full suite فقط قبل از promotion.
88. Flaky Test Registry — test/flake_rate/known_signature/retry_policy/owner.
89. Tool Output Compression — first error/last 100 relevant lines/exit code/summary counts، نه 20هزار خط.
90. Error Signature Extraction — normalize paths/remove timestamps/dedup stack traces/group errors قبل از مدل.
91. Memory باید Facts نگه دارد، نه Transcript — decisions/constraints/state/failed approaches/canonical locations/blockers.
92. Memory TTL — governance دائم / blocker تا حل / temp branch تا merge / vendor outage کوتاه / test log receipt-ref / user preference بلندمدت.
93. Memory Write Gate — فقط durable/verified/future-relevant/non-duplicative.
94. State Reconstruction از Artifacts — queue/receipts/branches/PRs/tests/deployments، نه حافظهٔ مکالمه.
95. Append-only Evidence Ledger — receipts حذف/overwrite نشوند؛ current state compact، evidence append-only.
96. Compact Current State — snapshot کوچک (project/current_release/open_blockers/active_jobs/ready_decisions/last_verified_deploy).
97. Model Output Scoring — cost/latency/test pass/retry/review rejection/hallucination/unnecessary files. ارزانِ سه‌بار-retry واقعاً گران‌تر.
98. Router باید Historical Performance را ببیند — benchmark داخلی، نه تبلیغات vendor.
99. Escalation بر اساس Failure Type، نه احساس Agent — evidence: 2 bounded T1 attempts failed / persistent / architectural ambiguity / auth surface.
100. Premium Model فقط روی Bottleneck — T1 implement → T2 یک conflict معماری → T1 apply → deterministic verify.
101. Distillation — خروجی مدل قوی → pattern/rule (مثلاً AUTH_SESSION_OWNERSHIP_PATTERN_v1) برای استفادهٔ ارزان بعدی.
102. Learn Once, Reuse Many — هر حل گران → reusable workflow/test fixture/verifier/prompt template/policy/migration/pattern/negative rule.
103. Cheap Shadow Evaluation — candidate ارزان‌تر را shadow اجرا کن بدون authority؛ اگر کیفیت کافی، routing تغییر.
104. Sampling به‌جای Full Review — deterministic validate all + LLM review 5–10 samples.
105. Random Audit — بخشی از Jobها random audit تا کیفیت افت نکند.
106. Anomaly-triggered Audit — unusual file count/unexpected dir/cost spike/repeated retries/model disagreement/test bypass/security change.
107. Cost Receipt — model_calls/input+output tokens/estimated_cost/deterministic_runtime/retries/cost_policy_pass.
108. Cost Attribution — به project و outcome (SourceB revenue / TrustField / NOOS infra / R&D / failed experiment).
109. Revenue-linked Scaling — AI spend cap ≈ current operating limit؛ upgrade to ~$2,000/mo فقط بعد از ≥$10,000/mo revenue.
110. Vendor-neutral Routing — هیچ provider پیش‌فرض دائمی بدون دلیل عملکردی/اقتصادی؛ router بین OpenAI/Anthropic/Google/local/code-models جابجا شود.
111. Provider Failover — same tier alternative → degraded lower capability → queue+receipt، نه توقف کامل.
112. Degraded Mode — continue: deterministic scans/queue/receipt/local classification؛ pause: hard architecture/public deploy.
113. Avoid Framework Tax — Ruflo/framework فقط برای gap واقعی (dispatcher/shared memory/MCP routing/parallel worker mgmt)، نه جایگزین governance/compiler/sandbox/receipts/promotion/authority.
114. Ruflo به‌عنوان Executor Adapter، نه Brain — NOOS/SourceA governance → compiler → sandbox contracts → Ruflo executor adapter → specialist workers → verifier → receipts. نه Founder→Ruflo swarm→unrestricted changes.
115. Disable Default Swarm Features — max_agents:3/max_parallel:2/max_rounds:1/shared_context:false/full_repo_context:false/premium:deny/auto_deploy:false/auto_merge:false.
116. Agent Registry با Cost Class — agent/cost_class/default_model_tier/invoke_when/max_calls.
117. Workflow Registry به‌جای Dynamic Swarming — repo_repair_v1/storefront_release_v1/pricing_consistency_check_v1/trustfield_partner_audit_v1/sourceb_voice_provision_v1. Dynamic swarm فقط برای مسئلهٔ ناشناخته.
118. Deterministic Workflow Compiler — task type → known workflow ("fix broken link"→web_link_repair_v1، …).
119. Unknown Work Isolation — exploration sandbox (no write/small budget/one research agent/one proposal) سپس Job اجرایی.
120. Research و Execution را مخلوط نکن — Research receipt → recommendation → implementation contract.
121. Time-boxed Exploration — max_sources:10/max_model_calls:3/max_output:2 pages؛ required: recommendation/rejected options/evidence gaps.
122. Kill Criteria برای Experiment — no improvement after 3 canaries / cost>2× baseline / low first-pass / requires permanent premium / duplicates subsystem.
123. Avoid Agent Theater — نمایشی: 20 Agent پرزرق، council برای کار ساده، unlimited memory، autonomous CEO agent، swarm consensus برای typo، persona طولانی، toolset کامل. ارزش واقعی: clear contract/small context/bounded tools/evidence/reusable workflow.
124. Persona Prompt را کوتاه نگه دار — Role: … / Modify only allowed files / Do not deploy / Return patch+test receipt.
125. Prompt Prefix Caching — role/tool policy/output schema/governance references ثابت و cacheable؛ فقط Job-specific تغییر کند.
126. Output Length Limits — max_summary_words:250 / max_risks:5 / max_recommendations:3.
127. Evidence Links به‌جای بازگویی — tests_receipt: receipts/test-123.json + summary کوتاه.
128. Human-readable View از Machine Artifact — یک JSON canonical + Markdown view generate‌شده.
129. One Decision, One Place — pricing/repo ownership/production domain/deploy authority/model routing/fulfillment status/product promise: یک canonical record.
130. Change Propagation Automation — pricing SSOT تغییر → checkout/landing/FAQ/calculator/emails/receipts چک و تناقض‌ها Issue شوند.
131. Default Deny برای Cost Explosion — premium/full repo context/>3 agents/>2 retries/multi-round debate/browser automation/paid provisioning/long schedule؛ فعال‌سازی فقط با reason.
132. Cost Spike Circuit Breaker — عبور از threshold → pause/capture state/partial receipt/request escalation.
133. Daily Cost Sentinel — cost today/by project/by model/retry costs/failed-job costs/top 5 expensive workflows (deterministic؛ LLM فقط anomaly).
134. Waste Report — هفتگی: repeated reads/failed calls/unused agents/oversized contexts/premium بدون escalation receipt/schedules بدون external outcome.
135. Agent Retirement — templateهای بی‌استفاده/تکراری/high failure/جایگزین‌شده retire/merge.
136. Workflow Maturity Levels — L0 Manual / L1 Assisted / L2 Deterministic prep / L3 Sandbox autonomous / L4 Verified promotion-ready / L5 Authorized production. ناپخته ناگهان L5 نشود.
137. Promote Capability، نه فقط Output — repeatable? verification reliable? cheaper model next? deterministic step replaces reasoning?
138. Founder Workload Metric — interruptions/clarifications/context rebuilds/claim-checking/decision-repeats. هدف: 18h/day → 8 → 5 → 3 → 2 → 1h/day.
139. True Decision Point Detection — از SSOT حل می‌شود؟ testable؟ default دارد؟ reversible؟ bounded experiment؟ فقط اگر همه منفی → Founder packet.
140. Reversible Defaults — reversible (internal naming/layout spacing/test org/temp branch/log format) → Agent default؛ price/contract/deploy/public promise/equity/account authority → gate.
141. Commercial Experiment Budget — duration/traffic_scope/spend_cap/success_metric/rollback.
142. Measure Outcome، نه Agent Activity — بد: agents spawned/tasks completed/messages. خوب: PRs verified/lead response time/checkout completion/calls captured/setups completed/interruptions avoided/cost per outcome.
143. Cost per Verified Outcome — Total Agentic Cost ÷ Verified Useful Outcomes.
144. Revenue Receipt — lead_id/payment_id/provisioning_id/trial activation/captured call/appointment/retained customer.
145. Opportunity Capture باید خودکار اما کم‌هزینه — sensorها deterministic/local؛ فقط high confidence/impact به cloud.
146. Perishable Intent Priority — new paid lead/missed call/booking/partner application/checkout failure/demo completion سریع‌تر از backlog فنی.
147. Fast Path و Deep Path — Fast: known workflow/low risk/small context/cheap model/auto verify. Deep: unknown/high risk/architecture/research/founder packet.
148. Commercial Fast Path برای SourceB — setup→validate→config→browser demo→approval/payment→provision→test→activate→receipt (بدون Founder مگر exception).
149. Exception Queue — unsupported integration/contradictory instructions/regulated business/high call volume risk/custom legal/vendor failure/payment mismatch.
150. اصل نهایی معماری — نه (More Agents/Conversations/Autonomy/Models) بلکه: Better Contracts / Smaller Context / Cheaper Routing / More Determinism / Bounded Execution / Independent Evidence / Reusable Patterns / Fewer Founder Interruptions.

---

## پیکربندی پیشنهادی Default برای سیستم ما

```yaml
agentic_runtime_policy:
  default_model_tier: T1
  cheap_preprocessor: T0
  long_context_tier: T1L
  governance_review_tier: T2

  max_agents_per_job: 3
  max_parallel_agents: 2
  max_agent_dialogue_rounds: 0
  max_retries: 2

  full_repo_context: false
  structured_handoffs_only: true
  deterministic_first: true
  independent_verification: true

  auto_merge: false
  auto_deploy: false
  paid_vendor_action: gated
  financial_action: founder_gate
  legal_public_action: founder_gate

  required_outputs:
    - job_contract
    - implementation_receipt
    - test_receipt
    - verification_receipt

  stop_conditions:
    - budget_exceeded
    - repeated_failure_signature
    - founder_decision_required
    - missing_credential
    - missing_executor
    - acceptance_criteria_met
```

## نسخهٔ بسیار فشردهٔ دکترین

Agent زیاد نگه دار، ولی کم اجرا کن. مدل قوی داشته باش، ولی فقط روی گلوگاه استفاده کن. Context کامل داشته باش، ولی فقط قطعهٔ لازم را بده. Automation زیاد بساز، ولی deterministic و bounded. Agent را آزاد نگذار؛ contract، budget، tool scope و stop condition بده. هر اجرا باید evidence بسازد. هر حل گران باید به workflow ارزان‌تر برای دفعهٔ بعد تبدیل شود. Founder فقط برای تصمیم واقعی برگردد، نه برای ادامهٔ کار ماشین.
