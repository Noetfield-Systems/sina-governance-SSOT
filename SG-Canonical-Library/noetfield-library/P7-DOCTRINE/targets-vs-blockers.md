# DOCTRINE — TARGETS vs BLOCKERS (the run-while-pursuing law)

**Status:** Load-bearing operating law. Corrects the paralysis pattern.
**Owner:** Sina Kazemnezhad — System Architect
**First written:** 2026-07-01 00:44 PDT

---

## 0. The law in one line

**A target is pursued while running. A blocker stops running. Treating a target as a blocker is the paralysis pattern — and paralysis is the real risk, because survival = moving/running/learning/healing 24/7.**

---

## 1. The distinction (the whole point)

| | TARGET | BLOCKER |
|---|---|---|
| What it is | a goal/claim you move *toward* | a condition that makes the next step *unsafe or impossible* |
| Effect on the system | system keeps running, improves toward it | system halts until resolved |
| Example | "zero-drift proof", "24/7 autonomy", "10 lines live", "revenue" | "receipts don't persist (SUPABASE_URL)", "verifier can't read the repo", "no kill-switch" |
| Wrong handling | halting the system until the target is met = **paralysis** | running past it = **corruption/harm** |
| Right handling | run now, pursue it in parallel, measure progress | stop, fix the specific thing, resume |

**The error that ran three days:** treating targets as blockers. "We can't run until zero-drift is proven" freezes the system on a *goal*. Zero-drift proof is a **target** — you run the brain and *pursue* the proof while it runs. The only things that legitimately stop the system are true blockers (unsafe/impossible), and there are few of them.

---

## 2. Why paralysis is the actual risk (survival framing)

Survival is not achieved by standing still until everything is perfect. Survival = **moving, running, learning, healing — in parallel, 24/7.** A system that halts on every target never runs; a founder who halts on every target never ships. The Elon-style determinism: **the system runs continuously and improves toward targets; it does not freeze waiting for perfection.** Perfection is a direction, not a gate.

- Not-running is a larger risk than running-imperfectly, *as long as* true blockers (harm/corruption) are respected.
- The system should be **always-on by default**, stopping only on real blockers, pursuing all targets in parallel while live.

---

## 3. The test (how to classify any condition in one question)

> **"Can I safely take the next step right now?"**

- **Yes** → it's a TARGET. Run. Pursue it in parallel. Do not halt.
- **No, because proceeding causes harm/corruption/irreversible-bad** → it's a BLOCKER. Stop, fix that specific thing, resume.

Everything is a target unless proceeding is *unsafe*. The bar for "blocker" is **harm or corruption**, not "imperfect" or "unproven."

### Worked examples
- "Zero-drift not yet proven" → **TARGET.** Running the brain unproven is not harmful; it's how you gather the proof. Run + pursue.
- "24/7 autonomy not yet earned" → **TARGET.** Run in confirm/semi mode, climb toward it.
- "10 lines not built" → **TARGET.** Build them while the built ones run.
- "Revenue = 0" → **TARGET.** Run the lines that pursue it.
- "Receipts don't persist (SUPABASE_URL)" → **BLOCKER.** No memory = the loop can't learn/measure = proceeding produces false state. Fix, then resume.
- "No kill-switch / can't stop the fleet" → **BLOCKER.** Running autonomously without a stop is unsafe. Fix first.
- "Verifier can't read a line's repo" → **BLOCKER** *for that line's shipping only* (not the whole fleet). Fix that line; others run.

---

## 4. Blocker scope (blockers are narrow, not global)

A blocker stops **the smallest unit necessary**, never the whole system by default:
- A line-level blocker freezes that line; other lines run.
- A fleet-level blocker (kill-switch, receipts-down) halts shipping fleet-wide but observation/measurement continue.
- **Default is run.** A blocker must *earn* its halt by being genuinely unsafe/impossible, and it halts only what its scope requires.

This is the inverse of the paralysis default (halt-everything-until-perfect). Here: **run-everything-except-what's-genuinely-unsafe.**

---

## 5. The five deterministic strategies (Elon-style, run-while-pursuing)

Named operating strategies that keep the system moving toward targets 24/7:

1. **Always-on by default.** The system runs continuously. Stopping is the exception (a blocker), not the norm. Idle = a bug to investigate, not a resting state.
2. **Targets pull, blockers stop.** Every goal is a target pursued in parallel while live. Only harm/corruption stops anything, and only at the smallest scope.
3. **Move / run / learn / heal in parallel.** These four run simultaneously, not sequentially: the system acts, gathers outcomes, sharpens definitions, and repairs degradations — all at once, 24/7. (See auto-heal + learning-proposal doctrine.)
4. **Deterministic core, fast throughput.** The brain decides the same way given the same state (governable, no drift) — determinism is what makes always-on *safe*, so speed doesn't mean recklessness. Fast + deterministic, not fast + chaotic.
5. **ROI-ranked, self-healing, sandbox-upgraded.** Compute follows measured ROI; degradations self-heal against real signal (revert if no metric move); upgrades flow through sandboxes on the immutable substrate. The system gets smarter while running, not by stopping to get smarter.

> "Smart genius" = the system compounds while live: running produces signal, signal sharpens definitions, sharper definitions improve running — a flywheel that only turns while moving. Stopping to perfect it stops the flywheel.

---

## 6. The one thing that is NEVER just a target (the exception)

Everything is a target-not-blocker EXCEPT the **substrate/safety floor** (immutable-floor doctrine): the verifier, gate, content-identity, kill-switch, mutation-guard, blast-radius limits. These are true blockers when absent, because running without them is *unsafe* (the system could corrupt itself or ship harm at 24/7 speed). So:

- **Safety floor missing** → BLOCKER (unsafe to run autonomously). Fix first.
- **Everything else** (proof, autonomy-level, features, revenue, scale) → TARGET (run + pursue).

This is why the substrate was the true P0: not because it's a nice-to-have, but because it's the one category that's genuinely unsafe-to-run-without — a real blocker — while everything else is a target the running system pursues.

---

## 7. Application to current state (2026-07-01)

- **Zero-drift proof** → TARGET. Run the brain build + pursue the proof. Do NOT halt other work waiting for it. *(Corrected from being treated as a gate.)*
- **24/7 autonomy** → TARGET. Climb the gears (confirm→semi→auto) while running.
- **10 lines / revenue / Brain Audit sales** → TARGETS. Pursue in parallel, now.
- **SUPABASE_URL (receipts)** → BLOCKER. Fix first ($25 paid ok) — no memory = false state.
- **Kill-switch tested** → BLOCKER for autonomy. Test before anything ships unattended.
- **Substrate** → already built = blocker already cleared. Run.

**Net:** two real blockers (receipts, kill-switch-test). Everything else is a target the running system pursues. Stop treating targets as blockers; fix the two blockers; run.

---

## 8. One line
**Run 24/7 by default; pursue every target in parallel while live; stop only for genuine harm/corruption (a blocker), at the smallest scope. Paralysis — halting on targets — is the real risk. Determinism makes always-on safe; the safety floor is the one thing that's a blocker when missing. Everything else is a target the running system chases.**

---
*v0.1 (2026-07-01 00:44 PDT) — first write. Targets-vs-blockers law, the run-while-pursuing test, five deterministic strategies, substrate-as-only-true-blocker exception, applied to current state.*
