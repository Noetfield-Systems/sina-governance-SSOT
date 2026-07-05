# RECONCILIATION — uploaded canon/registry docs vs library (2026-07-03)

**Purpose:** reconcile 8 uploaded artifacts (FOUNDER_CANON v1, MACHINE_LOOPS v1, WORK_ORDER_IDE_LANE v1, BRAIN_REGISTRY_LEARNING_GATE v0.1.4 + impl prompt, SSOT_CONFLICT_LOG v0.1.2, SSOT_PROPOSAL versioning v0.1.1, deep-research-report) against the noetfield-library. Decide: new / conflict / unify / upgrade.
**Owner:** Sina Kazemnezhad
**Written:** 2026-07-03 12:34 PDT

---

## 0. Headline finding

**Several uploaded docs are AHEAD of the library, not behind it.** They resolve open loops the library still lists as open, and FOUNDER_CANON v1 is effectively a **more mature master** than the library's north-star section. This is not "file these gems" — it's "the library's spine must be upgraded to match canon, and two open loops close."

---

## 1. What each uploaded doc IS (one line each)

1. **FOUNDER_CANON v1** — the real master constitution. Zero-founder operational validation; intent filter; authority-flow; failures-route-to-machines; 3 founder touchpoints. **Supersedes the library's north-star framing.**
2. **MACHINE_LOOPS v1** — the machine wiring of canon §6–§8: validation/critique/repair/audit/research as loops with scripts + receipts + merge-authority tiers T0–T3. **This is the self-heal loop, already specced concretely.**
3. **WORK_ORDER_IDE_LANE v1** — a governed agentic IDE lane (Aider, worktree, mechanical L5 hook/CI gates G1–G6, 5-clean-cycles acceptance). **This is layered-agents + targets-vs-blockers applied to a real coding lane, with mechanical (not prose) enforcement.**
4. **BRAIN_REGISTRY_LEARNING_GATE v0.1.4** — registry + layer-map + mutation classes (LOCKED/GATED/OPEN) + learning_record schema + base-model-as-blank-vocabulary founding principle. **This is the deterministic-brain doctrine + learning-proposal, already specced.**
5. **BRAIN_REGISTRY impl prompt v0.1.4** — the buildable version of the above, Phase-1-config-only, mutation path STUBBED behind SOURCEA_PHASE2_MUTATION_TRIALS=false.
6. **SSOT_CONFLICT_LOG v0.1.2** — resolves the R1–R7 domain split: only D4-portable R1/R2/R6/R7 import to agentic-brain contexts; R3/R4/R5 stay control-panel.
7. **SSOT_PROPOSAL versioning v0.1.1** — the universal versioning/timestamp rule (major.minor.edit + timestamp, filename + header).
8. **deep-research-report** — (research input; treat as builder artifact under author≠subject, not authoritative).

---

## 2. OPEN LOOPS THAT NOW CLOSE (library was behind)

| Library open loop | Resolved by | Resolution |
|---|---|---|
| **R6/R7 naming collision** (fixed the collision, but full domain logic was loose) | SSOT_CONFLICT_LOG v0.1.2 | R1/R2/R6/R7 = D4-portable → agentic brain; R3/R4/R5 = control-panel only. Clean rule, not case-by-case. **CLOSE.** |
| **Versioning rule** (library added it v0.1.2, but ad-hoc) | SSOT_PROPOSAL versioning v0.1.1 | Formal `major.minor.edit_YYYYMMDD-HHMM` in filename + header + edit-log. **Adopt this exact form; supersede the library's looser rule.** |
| **Mutation guard** (`SOURCEA_PHASE2_MUTATION_TRIALS` made real) | BRAIN_REGISTRY impl prompt | Now has full context: it gates Task 5/5b, Phase-2-only, founder-flip-only. Consistent. **CLOSE — it's real and correctly scoped.** |
| **learning-proposal-v1** (library listed as "to build") | MACHINE_LOOPS v1 + BRAIN_REGISTRY | Already specced: learning_record schema + gated proposal path + 5-option canvas form. **Not open — it's specced, Phase-1-stubbed.** |
| **Two-plans reconciliation debt** | FOUNDER_CANON v1 | Canon is the single master; governed-autorun v3 + MACHINE_LOOPS + WORK_ORDER + BRAIN_REGISTRY are its children by pointer. **The master exists — it's FOUNDER_CANON, not something to still write.** |

---

## 3. WHERE UPLOADED DOCS ↔ LIBRARY DOCTRINE UNIFY (same idea, both sides)

| Library artifact | Uploaded equivalent | Verdict |
|---|---|---|
| `targets-vs-blockers.md` | FOUNDER_CANON §3 filter #5 ("keep targets as targets — or freeze them into blockers") + intent filter | **Same law, independently stated both sides. Strong signal it's correct.** Unify: canon is the authority; library artifact is the expanded doctrine. |
| `layered-agents.md` | WORK_ORDER IDE lane (G1–G6 mechanical gates) + deep-research IDE roles (understanding/planner/router/workers/critic/aggregator) | **Same architecture, made mechanical + role-specific.** The IDE work order is layered-agents with hook/CI enforcement instead of prose. Unify. |
| `deterministic-brain-doctrine.md` (D-1 soup/raw) | BRAIN_REGISTRY §0 "base model as blank vocabulary slate" | **Nearly identical, independently derived.** Canon's version is sharper: SSOT v6 + R1/R2/R6/R7 are the model's *first-class language definitions*, not governance beside it. **Upgrade the library's D-1/D-2 with this framing.** |
| `01-doctrine/immutable-floor.md` | WORK_ORDER G6 (policy immutability during cycle) + canon §8 irreversible-L5 | **Same law, mechanically enforced.** "An agent that can edit its own cage has no cage." Unify. |
| `pattern-factory.md` (ROC/leverage implicit) | deep-research "Return on Cognition" note | **New sharpening:** ROC = "how many future work-hours does one hour of thinking delete?" Architects delete work; operators trade time. **Add ROC as the founder-KPI lens above founder-hours.** |

---

## 4. GENUINELY NEW (not in library — add)

1. **Mechanical vs prose enforcement (WORK_ORDER).** The hardest lesson: *prose guardrails failed twice this session; build them as pre-commit hook + CI check.* A rule an agent can narrate around is not a gate. **NEW doctrine: gates must be mechanical (hook/CI/code), never prose, for anything load-bearing.** → new `01-doctrine/mechanical-not-prose.md`.

2. **Negative-proof acceptance (WORK_ORDER §10).** A gate is proven by a *deliberately failing commit it rejects*, on disposable branches — not by prose claiming it works. **NEW: prove gates by rejection, not assertion.** (This is anti-theater applied to gates themselves.)

3. **Merge-authority tiers T0–T3 (MACHINE_LOOPS).** T0 docs/tests → machine-merge; T1 scoped code → +critic; T2 deps/CI → +second critic + HMAC chain; T3 schema/gates/governance → founder-only-never-auto. **NEW: graduated merge authority by change-class.** → add to Line Engine / substrate.

4. **Base-model-as-blank-vocabulary as the *architectural advantage* (BRAIN_REGISTRY §0).** Not just "raw not soup" — the sharper point: *assistant-tuned models arrive with pre-baked operational vocabulary that FIGHTS founder instructions → compliance theater.* A base model has no competing definitions, so SSOT becomes its first-class language. **This is the strongest single statement of the whole soup/raw thesis — promote it.**

5. **Return on Cognition (ROC) (deep-research).** The founder-KPI above founder-hours: optimize the *structure of work getting done*, not the work. Every manual action = assume the system failed; ask "can this be Rule/Pattern/Automation/Receipt?" **NEW: `01-doctrine/return-on-cognition.md`.**

6. **The IDE agentic system as a concrete first lane (deep-research IDE spec + WORK_ORDER).** understanding → planner → router → sandbox workers → critic/verifier → aggregator → receipt, economically routed (strong model plans, cheap agents execute, verifier proves, aggregator composes). **This is a concrete, buildable instance of the Line Engine — possibly the first line to build.**

---

## 5. CONFLICTS TO RESOLVE (founder DECIDE)

1. **Versioning rule collision:** library adopted a looser `vX.Y.Z (datetime) — changed` footer (v0.1.2); SSOT_PROPOSAL specifies `major.minor.edit_YYYYMMDD-HHMM` in *filename + header + edit-log*. → **Adopt the SSOT_PROPOSAL form as canonical; migrate library artifacts to it.** (They agree in spirit; canon's is more complete.)

2. **"First trade" framing:** library says Brain Audit first (commercial); FOUNDER_CANON is silent on commercial (it's operational). **No conflict — different domains.** But the library's product docs and the canon should cross-reference: canon governs *how the system runs*; product docs govern *what's sold*. Keep separate shelves, add cross-pointer.

3. **Master authority:** library's `00-INDEX` north-star vs FOUNDER_CANON v1. → **FOUNDER_CANON v1 is the operational master.** The library's north-star section should be rewritten to *point to* FOUNDER_CANON, not restate it (canon's own rule: "no competing mini-constitutions").

---

## 6. UPGRADE ACTIONS (the reconcile output)

**A. Library spine upgrade (index → v0.2):**
- North-star section → point to FOUNDER_CANON v1 as operational master (stop restating; cross-reference).
- Adopt SSOT_PROPOSAL versioning form as the library's versioning law (supersede v0.1.2's looser rule).
- Register the closed open-loops (R-split, mutation-guard, learning-proposal-specced).

**B. New doctrine artifacts to write:**
- `01-doctrine/mechanical-not-prose.md` (gates must be code/hook/CI; prove by rejection).
- `01-doctrine/return-on-cognition.md` (ROC — the founder-KPI above hours).
- Upgrade `deterministic-brain-doctrine.md` D-1/D-2 with the "base model = first-class language, assistant-tuned = compliance theater" framing.

**C. Architecture additions:**
- Add merge-authority tiers T0–T3 to substrate/Line-Engine.
- Register the IDE agentic lane (understanding→planner→router→workers→critic→aggregator) as a concrete Line Engine instance + candidate first line.
- Add negative-proof (prove-gate-by-rejection) to the substrate's verification doctrine.

**D. Registry/SSOT (route per your layered plan):**
- SSOT_CONFLICT_LOG v0.1.2 (R-split) → **ratify** into SSOT (governance/SG), it's currently PROPOSED.
- SSOT_PROPOSAL versioning v0.1.1 → **ratify** into SSOT (D4 traceability rule).
- BRAIN_REGISTRY v0.1.4 → this is SourceA Brain territory (owner: SourceA Brain Agent), Phase-1-config-only, mutation STUBBED. Confirm on-disk, not just drafted.

---

## 7. THE HONEST BIG PICTURE

The uploaded docs show the system is **further along than the library reflected** — there's already a real master (FOUNDER_CANON), real machine-loop wiring (MACHINE_LOOPS scripts), a real governed IDE lane spec (WORK_ORDER with mechanical gates), and a real brain-registry/learning-gate. The library was capturing *doctrine*; these are *doctrine already turning into wired mechanism*.

**So the reconcile verdict:** the library is not the master — **FOUNDER_CANON v1 is.** The library becomes the *doctrine + pattern + product layer* that FOUNDER_CANON points to for depth, and FOUNDER_CANON is the operational constitution every actor reads. Two homes, one authority: canon governs operation; library holds the mined doctrine, patterns, and commercial product-lines that inform canon.

**The two things still genuinely open (real blockers, per targets-vs-blockers):**
- `SUPABASE_URL` receipts persistence (unchanged — still the true blocker).
- Ratification of the two PROPOSED SSOT items (R-split, versioning) — a founder DECIDE, quick.

Everything else is a target the running system pursues.

---
*v0.1 (2026-07-03 12:34 PDT) — first reconciliation of uploaded canon/registry/work-order docs against library. Verdict: FOUNDER_CANON v1 = operational master; library = doctrine/pattern/product layer beneath it; 5 open loops close; 6 new items to add; adopt SSOT_PROPOSAL versioning form.*
