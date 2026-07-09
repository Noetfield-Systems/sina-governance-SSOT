# SESSION LEDGER — 2026-06-30 — Governance Loop → Deterministic Brain → Pattern Factory

**One line:** Built the governance substrate to done, put an open-source base model live on Cloudflare through the loop, extracted the brain's meaning source, and reframed the business as a pattern factory run by a deterministic brain independent of the founder.

---

## PROVEN (with receipts — not claims)

**Substrate complete (Phase 0):**
- 0.1 SourceA `main` = truth, working folder clean on main, pushed. HEAD progressed to `8a2fb1a45`.
- 0.2 Promotion gate wired confirm-each-time; refuses unattended `--execute-deploy`; refuses refreshing deploy command (`e3d172d`).
- 0.3 Watched gate-triggered deploy with **content identity proven** — committed == verified == deployed sha (`62a9857a…`). Caught + fixed the deploy-refreshes-bundle bug (verified-X-ships-Y). Added `deploy-verified` (no-refresh) mode.
- 0.4 Token auth: per-account scoped tokens in `~/.sina/secrets/` (gitignored); no wrangler login-switching; both accounts one session (SG `aba856c`, SourceA `f0a5712`). Verified curl: CF_VERIFIER→`b7282b4a…`, CF_MAIN→`0d0b967b…`.
- 0.5 R6/R7 naming collision fixed (governance D4 rules renamed `D4-RECEIPT-LAW` / `D4-AGENT-NO-SELF-VERIFY`, SG `c9963dc`). Mutation guard made **real + fail-closed** (`data/sourcea-phase2-mutation-trials-v1.json` default false + enforcing guard, SourceA `cf35d9e3`).
- 0.5b Real change shipped watched (wording → "grounded in retrieved sources…", sha `32b4b83a`, receipt `4ac1c659`, live `df87822b`, new wording confirmed live) AND bad change blocked (malformed bundle → verifier FAIL `647e2ed2` → gate REFUSED → live unchanged).

**Semi-auto window (2hr, fast, notify-not-gate):** 4 real bundle improvements shipped, all PASS, sha identity held each: `edaf75aa6` (live-status-first), `b326e433` (PASS/BLOCK→public language), `b7278333` (grammar filler — flagged), `081b05f` (demo-link routing).

**Live behavior test (the critical finding):** verified + deployed + valid ≠ behaving. Live Brain leaked internal `PASS` to a public user, and confidently claimed "Forge available" without a status source — two failures no byte-level check caught. → banked as doctrine.

**Base model live:** Brain Worker switched OpenRouter → `@cf/meta/llama-3.3-70b-instruct-fp8-fast` via Cloudflare Workers AI (`4425aacd`, version `f10baf03`, `provider: workers_ai`, `ai_model_ready: true`). *This is the mouth, not the raw brain.*

**Brain meaning extracted:** `locked-definitions-v1.json` draft built from live materials, provenance-tagged, tagged approved/review/unsafe. v6 framing sourced from governance disk. 4 founder decisions isolated.

---

## KEY REFRAMES (the gems)

1. **Verified ≠ behaving ≠ true.** The substrate proves valid + identical. It cannot prove behavior-compliant or claim-true. Those need behavior-probe + claims-truth (computer-use) + live status signal. *Autonomy is unsafe until the loop tests behavior and grounds claims.*

2. **Two types of "claim" problem.** Type 1 = commercial/strategic (D1/D2, founder DECIDE — what the Brain may assert). Type 2 = agent governance (D4, the loop — did it follow rules). The "Forge available?" failure is Type 1. Founder authors claims; loop enforces the Brain stays inside the approved set backed by fresh signal.

3. **Enticing vs honest is a false choice.** Decouple: warmth always-high; confidence tracks the live signal. Unsure = entice + escalate (not cold, not fake). Uncertainty is a selling opportunity; honesty is the receipts-product's edge.

4. **Lazy-agent gap fixed structurally.** Not "hope agents test" — a real health-check (computer-use) makes the status signal green only if the thing actually works. Confidence *depends on* the thing working. Improvement counts only if it moves a real metric, else auto-revert.

5. **Self-improvement safety law.** A self-improving system must never improve away its own brakes. Substrate immutable from inside the loop; loop optimizes work, never the rules that judge it. Degrade toward safety on uncertainty, never toward more autonomy.

6. **Soup vs raw.** LLMs are word-native — smart *and* drifting (same thing: a giant distribution over human meaning). The brain must be a **raw deterministic core** holding the founder's locked vocabulary/framing/strategy, calling LLMs as disposable soup-walled workers that draft language for already-made decisions. Decision first (deterministic code), language second (LLM, walled, sanitized).

7. **Learning = definitions sharpen, not core drift.** Fixed deterministic executor the founder tunes. Failures → proposed SSOT patches → sandbox → verify → gate → version bump → core executes new version. No silent self-mutation.

8. **The business is a pattern factory.** Founder = native pattern thinker + trader. Products = proven patterns (zero-drift, anti-theater, auto-heal, poison-detection incl. self-poison). Flaws are *projected* (existing rot surfaced), not fabricated. The substrate is what makes a healed pattern *provable* (receipts) rather than *theatrical*. Sold Fly.io-style. First trade = the brain + 24/7 loops + 10 lines (the platform itself).

9. **The definitions-drift root cause.** Three days of friction = every word-native AI reconstructs the founder's core terms from context and drifts them back to its own average (no subject-pinning across turns). Fix = locked, provenance-tagged definitions the deterministic core reads; public models can't hold meaning, so meaning lives in the core, not the workers.

---

## OPEN (carry forward)
- **4 founder claim decisions** (gate `locked-definitions` → live_locked): `sourcea_is_live` signal; `forge_terminal_guaranteed_live_runtime` (do you stand behind it + by what check); `every_possible_run_has_public_proof` (narrow to designed-around-receipts); `broken_gears` (author the 3-gear ladder — new).
- **Blockers before parallel scale:** `SUPABASE_URL` not resolving from Railway (`receipt_row_id: null` — no receipts = no measurement = no fleet); verifier repo-aware per line; public API routing defects on sales surfaces; possible stale duplicate verifier on main account.
- **Next build after decisions locked:** `decision-core-v1` (deterministic Python over locked-definitions) → `soup-wall-v1` (Llama drafts decided answer + sanitizer) → `learning-proposal-v1` (gated SSOT patches). All on the Llama-mouth deploy + existing substrate.

---

## OUTPUT FILES THIS SESSION
- `/outputs/LINE_ENGINE_ARCHITECTURE_v0.1.md`
- `/outputs/LINE_ENGINE_ARCHITECTURE_v0.2_HARDENED.md`
- `/outputs/noetfield-library/00-INDEX.md` (library spine)
- `/outputs/noetfield-library/05-ledger/2026-06-30-governance-loop.md` (this file)
- In SourceA repo: `reports/locked-definitions-v1.json`, `reports/locked-definitions-founder-decisions-v1.md`
