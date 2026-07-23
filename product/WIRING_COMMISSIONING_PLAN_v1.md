# Wiring & Commissioning Plan v1 — LOCKED

**Locked:** 2026-07-23T06:28:38Z · **Authority:** founder order 2026-07-23
**Machine truth:** [`WIRING_COMMISSIONING_CONTRACT_v1.json`](WIRING_COMMISSIONING_CONTRACT_v1.json) (56 jobs)
**Enforcement:** `scripts/verify_wiring_commissioning_v1.py` — job status is *computed from receipts on disk*, never asserted.
**Evidence basis:** 20-agent read-only inventory + downgrade-biased adversarial verify (run `wf_a66ceb51-1b8`), then a 3-lens adversarial review of these very artifacts (run `wf_722ce91b-2a6`) whose findings are folded in below.

**Two enforcement guarantees (proven by regression test after the review found them broken in draft):**
1. **Fail-closed lock.** The plan/contract/script sha256 are pinned in `receipts/WIRING_COMMISSIONING_PLAN_LOCK_v1.json`. A *missing* lock, not only a mismatch, is an `ENFORCEMENT_VIOLATION` (exit 3) — deleting the lock cannot re-open a fail-open hole. Re-locking after any legitimate edit is an explicit `--init-lock` act, visible in git.
2. **Founder gates are non-bypassable.** A founder-gated job can **never** compute DONE while its founder receipt is absent — even if a worker fabricates the exit receipt it reports `AWAITING_FOUNDER`. (The review demonstrated a bypass in the draft where hand-writing `{"status":"PASS"}` flipped the P0 auth job to DONE; that path is closed.)

---

## 0. The one-sentence answer to "why isn't this one machine yet"

Every piece exists — HDIR kernel (qualified PASS on staging), Continuation Motor v2 (code-complete, durable state, edge verifier), Sandbox Autorunner (14 deterministic workflows, ran 3×), SG gates (fail-closed, refusal-correct), Runway (real user path with a production convergence receipt), cloud factory (8/9 categories *executed* on GHA — 5 of 8 not yet green) — but **no lane was ever ordered to wire them**, five integration branches sit unmerged, four checkouts are parked far behind their own mains, and every remaining connection is (correctly) waiting on a named founder gate. This plan is that order.

## 1. Scope law (what this plan may and may not do)

**Only wiring and commissioning.** Allowed job classes: `sync`, `land`, `receipt`, `adapter`, `config`, `verify`, `cleanup` (definitions in the contract doctrine block). **Forbidden:** new features, new products, new scenarios, new categories (CAT-07 hard hold stands), overriding any founder gate/fence/HOLD, patch work outside motor/sandbox lanes, deleting receipts, new org-root directories. Where this plan and an existing founder gate disagree, **the gate wins**. Where this plan and the product registry disagree, **the registry wins**.

## 2. Verified starting truth (what the adversarial pass established)

| Piece | Verified state | The one thing to know |
|---|---|---|
| HDIR kernel | partial | Qualification PASS is real but staging-only, single scenario, and its receipt hash could **not** be independently recomputed |
| Runway | partial | A real user path exists in production (OAuth → project → build → artifact + receipt) — but local checkout is ~201 commits behind and all proven runs are founder-adjacent |
| Motor v2 | partial | Code-complete "canary-grade control plane"; blocked on SourceA executor deploy + final 2-executor proof + webhook toggle |
| Autorunner | partial | Ran 3× for real; **BLOCKED_EXECUTOR_ENDPOINT**; CF verifier undeployed so nothing can ever be PASS; found a **live auth outage** on www.noetfield.com |
| SG gates + P0-PGR | built-not-commissioned | promotion_gate.py fails closed (exit 78) exactly as designed; nobody calls it from motor/sandbox jobs yet; R2 receipt stuck PARTIAL on a URL handback |
| Integration worktrees | partial | SG Runtime Value Contract **already merged** (PR #58); the motor half of the spine is unmerged; 8 org-root `_wt-*` dirs are orphaned residue |
| Studio IDE | built-not-commissioned | Loop never green (only committed loop receipt is a synthesized failure); no installable artifact; no auth |
| Consumer surfaces | partial | TrustField genuinely live (receipt stale 14 days); WitnessBC unverified since 06-26; NOOS site has **no deploy target**; noetfield.com apex-404 + 29 P1 findings open |
| Goals | partial | 3 locked SKUs + Never Miss a Call; doctrine endpoint = **first paid receipt from a stranger** (nearest lane: sourceb.ca Stripe checkout); goals only visible on an unmerged branch |
| Factory infra | partial | GHA proven live 8/9 categories; Command Gateway v1 live-attested by commits only; 9 CF verifiers + 9 Supabase migrations pending; one cron contradicts the fence doctrine |

## 3. The phases (56 jobs; IDs are the contract's law)

**W0 — TRUTH & HYGIENE (11 jobs).** Make the ground solid before wiring anything: sync the four stale checkouts to their mains (W0-01..04), land the goal registry itself onto SG main (W0-05), close the **gate-bypass drift** where a stale copy of promotion_gate.py predates the fail-closed layer (W0-06), founder-approved cleanup of the 8 orphan residue dirs (W0-07), **fix the live auth sign-in outage — P0, real users hit it today** (W0-08), reconcile the contradictory active cron (W0-09), stop gitignoring commissioning receipts + remove broken gitlinks (W0-10), and **preserve-first the local-only bench that is *ahead* and unpushed before any sync touches it** (W0-11 — memory law).

**W1 — CONTRACT SPINE (9 jobs).** One law for how pieces talk: land the motor event spine so the already-merged SG Runtime Value Contract governs a motor that exists (W1-01), land plan-intake + SourceB adapter (W1-02), land the NOOS half (W1-03), land the pending www Motors copy (W1-04), SHA-pin cross-repo work orders (W1-05), **wire SG promotion_gate.py as a deterministic pre-flight into every motor/autorunner deploy-class step — fail-closed, needs no unlock because it can only STOP things** (W1-06), wire the motor→SG repository_dispatch sender (W1-07), map CF tokens into cloud secrets (W1-08), apply the Runway Tier-2 persistence migration so its store stops being a no-op (W1-09).

**W2 — EXECUTOR LANE (8 jobs).** The motor actually does jobs with machines, deterministically, in sandbox: deploy the SourceA executor endpoint (W2-01 🔒), deploy the independent CF verifier — the only PASS-minter (W2-02 🔒), build the motor-side POST/poll adapter clearing BLOCKED_EXECUTOR_ENDPOINT (W2-03), then **the motor⇄sandbox commissioning proof**: one heading → 2+2 run IDs → 2 real sandbox PRs → edge-verified receipts → Promotion Decision Packet → automatic close (W2-04). Plus: R2 PARTIAL→PASS receipt wiring (W2-05), the HDIR⇄motor wire via runway.v1, staging-only (W2-06), the 9 Supabase migrations + 9 category verifiers (W2-07 🔒), cat-08's first cloud receipt (W2-08).

**W3 — SCHEDULED OPERATION (6 jobs, every one founder-gated by design).** Manual-green ≠ cron-green: R3 cron-shadow unlock + 24h zero-manual window (W3-01 🔒), plan-intake DECLARED→VERIFIED (W3-02), the motor webhook toggle (W3-03 🔒), autorunner standing loop (W3-04 🔒), TrustField loops → FACTORY_LINE_VERIFIED (W3-05 🔒), drift-guard weekly cron (W3-06 🔒).

**W4 — TRUST LAYER (4 jobs).** Receipts become one auditable system: auditor covers the full ~4,700-receipt corpus, not 73 (W4-01), RECEIPTGRAPH self-audit countersigned by the independent verifier — CAT-09's locked activation gate (W4-02), HDIR receipt-hash made independently recomputable (W4-03), Studio receipt labels fixed (W4-04).

**W5 — CONSUMER SURFACES (16 jobs).** "A real consumer-popular app" here means: **a stranger can find it, use it, and pay for it, and a receipt proves each step** — reached by commissioning what's built, not by new features. TrustField fresh live-truth (W5-01); WitnessBC recommissioned with scheduled checks (W5-02 🔒); noetfield.com apex-404 closed (W5-03) + 29 P1 findings burned down after the copy verdict (W5-04 🔒); NOOS site gets a real deploy target + a durable intake sink before any stranger-facing form (W5-05 🔒); **Runway stranger-tenant proof** — the first genuinely non-founder full run (W5-06); production payment through the existing fence (W5-07 🔒); Studio loop green (W5-08), packaged .app + .vsix (W5-09 🔒), **read-only** motor status API-wire (W5-10, API seam only — no new UI); SourceB prod↔upgrade branch reconciliation (W5-14) and **sourceb.ca live-truth re-probe** so the revenue lane stops assuming liveness (W5-15); the reseller rate-card founder send that fixes offer economics (W5-16 🔒); revenue receipt adapter Stripe→SG naming the right offer (W5-11); pricing SSOT across the three diverging surfaces (W5-12 🔒); and the doctrine endpoint itself — **FIRST_REVENUE_RECEIPT, paid, payer_type=stranger** (W5-13 🔒).

**W6 — FULL-LINE PROOF (2 jobs).** The commissioning certificate: one founder heading traverses P0-PGR → motor → sandbox executor + HDIR runway → SG gate preflight → independent verifier PASS → unified auditor, cold, zero manual (W6-01); then 7 consecutive days of green scheduled receipts with zero founder interrupts outside the decision queue (W6-02).

## 4. Founder decision queue (27 gated jobs, in dependency order)

Nothing in this plan bypasses you — proven, not asserted (see the two enforcement guarantees up top). These are the only places the machine stops and waits, each satisfied only by a named founder receipt file (globs in the contract). A gated job stays `AWAITING_FOUNDER` until that file exists.

**W0:** W0-07 approve org-root residue cleanup · W0-08 PDP G2 → fenced deploy of the auth fix (**P0, live outage**) · W0-09 cron-truth verdict · W0-11 approve preserving the ahead bench.
**Merges (the act is the founder's):** W0-05 goal registry · W1-01..04 the four spine/www merges.
**W1:** W1-08 CF-token secrets · W1-09 Runway Tier-2 migration.
**W2:** W2-01 SourceA executor deploy + secrets · W2-02 secondary-CF-account login (also transitively gates W2-07) · W2-05 R2 run-URL handback.
**W3 (all gated by design):** W3-01 R3 cron unlock · W3-03 webhook toggle · W3-04 autorunner cron unlock · W3-05 TrustField secrets · W3-06 drift cron unlock.
**W5:** W5-02 WitnessBC token · W5-04 copy verdict CEM-001 · W5-05 NOOS site-target decision · W5-07 prod payment · W5-09 Studio session sign-off · W5-16 reseller rate-card send · W5-12 pricing verdict · W5-13 commercial activation (first-dollar).

**Standing gate carried but out of v1 scope (see contract `explicit_exclusions`):** pureflow canonical-main establishment (P0, blocks pureflow source lanes); SG production commissioning; Studio notarized-app distribution; Runway founder-authority RECORDED→ENFORCED.

## 5. How to operate this plan

```bash
python3 sina-governance-SSOT/worktrees/_wt-sg-product-lock/scripts/verify_wiring_commissioning_v1.py
```

Run it any time: it prints every job as DONE / READY / AWAITING_FOUNDER / BLOCKED_DEPS and writes an append-only status receipt. Workers pick only READY jobs, execute them **through motor/sandbox lanes** (sandbox-first law), and a job becomes DONE only when its named receipt exists with the required fields (and, for founder-gated jobs, its founder receipt too). Any legitimate edit to the plan/contract/script requires re-locking with `--init-lock` (an explicit, git-visible act); a silent edit or a deleted lock makes the verifier refuse to run (exit 3).

**Status at lock time (56 jobs):** 0 DONE · **11 READY** · 9 AWAITING_FOUNDER · 36 BLOCKED_DEPS. The 11 READY jobs are exactly the no-permission-needed work: the four checkout syncs (W0-01/03/04, W1-03/04 land-prep), TrustField live-truth refresh, apex-404 close, Studio green-loop + receipt-label fix, and the two SourceB verifies. Start there.

## 6. Category map

W0/W1 serve the spine (CAT-01/03/04/06) · W2 commissions CAT-04 and **advances CAT-05 toward its WORKCELL_FACTORY_RUN activation receipt** (founder build-unlock still pending — registry bar unchanged) while proving CAT-03's runtime · W3 turns CAT-03/04 cron-green · W4 activates CAT-09 · W5 brings **CAT-08 to green-loop grade** (notarized-app activation deferred to the founder Apple-ID gate) and commissions CAT-10 surfaces, carrying the commercial endpoint · W6 certifies the factory as one machine. CAT-02 is already live-running; CAT-07 stays on hard hold. Per the contract precedence rule, no job advances a category past its registry-locked `receipt_required_to_activate`.
