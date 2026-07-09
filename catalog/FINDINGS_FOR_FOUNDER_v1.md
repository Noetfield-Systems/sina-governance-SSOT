# FINDINGS FOR FOUNDER — sandbox audit v1

**Date:** 2026-07-09 · **Source:** sandbox worktree `sg-sandbox` @ `claude/sandbox-build` (advisory; nothing here changed live state).
**What this is:** real problems the B0/B1 verifiers surfaced while building — each proven by a red-capable test against a real on-disk artifact. Advisory only; every fix below is YOUR decision. Nothing was reconciled, deployed, or sent.

Ordered by how much they touch trust / money / founder authority.

---

## 1. A recorded deploy is a FAILED invariant  · `DX-4` · **REVIEW**
- **What:** `receipts/phase0.3-step10a-watched-deploy-receipt.json` has `content_identity_confirmed = false`. The deploy-receipt auditor classifies it **FAIL** and pins the rollback hint to pre-live version `628ebc37-5c66-44e5-9cad-4e05f...`.
- **Why it matters:** a deploy receipt where content identity was never confirmed is not proof the right thing shipped. Whether this is historical/expected or needs action is a judgment only you can make.
- **Your decision:** confirm the live Brain is on the intended version; if this receipt represents an unresolved watched-deploy, decide whether to re-verify or annotate it closed. The auditor (`catalog/builds/DX-4/`) can re-run over all deploy receipts on demand.

## 2. The DLM fence silently drops founder items  · `GV-6` · **FOUNDER-GATED FIX**
- **What:** `decision_language_machine_v1/dlm_apply_map_v1.py` `build_apply_map` with its **default** `partial_batch=True` produced an apply_map that silently drops **51 unvalidated ADVISOR/FOUNDER items** — they are neither applied nor recorded in any `deferred_unvalidated` list.
- **Why it matters:** this is the one place the machine can narrow **Founder-DECIDE** authority (invariant 0.2 / Author≠Subject 0.1) — a genuine FOUNDER_FACT could be classified and dropped without ever reaching your sheet. If a future R3/R4/R5 unlock wires the DLM→P0-PGR bridge (BR-1), that bypass gets industrialized.
- **Status:** GV-6 now **detects and flags** this on any persisted apply_map. The **fix is founder-gated** (I did not touch the fence): either (a) emit an explicit `deferred_unvalidated` list so dropped items are accountable, or (b) block when picks are incomplete. Your call which.

## 3. The live verifier is looser than its own schema  · `BR-4` · **DECISION: source of truth**
- **What:** `workers/github-app-advisory/index.js` `validateArtifactDescriptor` **accepts** `artifact_type = brain_worker_bundle` and **ignores extra fields** — but the schema-of-record `verifier/brain-config-artifact-descriptor-schema-v0.1.json` pins `const knowledge_bundle` and `additionalProperties: false`.
- **Why it matters:** two implementations of the same descriptor contract disagree; the live edge worker is more permissive than the schema you'd point an auditor at. A descriptor the schema rejects would pass the live worker.
- **Your decision:** pick the source of truth and align the other — either widen the schema (if `brain_worker_bundle` is legitimately supported) or tighten the worker. Do not merge live-worker changes without your sign-off (Lock 2).

## 4. No real execution has produced a PASS-eligible receipt  · `GV-1` · **INFORMATIONAL**
- **What:** the only real execution receipt, `receipts/p0pgr/P0PGR-EXEC-M03-...json`, is missing `recorded_at`, `evidence_artifacts`, and `founder_authorization_ref`, and is `quality_state: PARTIAL`. The verifier rejects it — consistent with the receipt's own honest `PARTIAL` self-label.
- **Why it matters:** it confirms the honest state — nothing real has cleared the bar yet. Any future real execution must carry founder-authorization + stored evidence + machine timestamps or GV-1 will (correctly) reject it. This is the brake the R-ladder was missing; it now exists.
- **Your decision:** none required now. When you authorize a real execution, record the founder-unlock receipt under `receipts/p0pgr/founder/` first.

## 5. CHESS manifest points at files that don't exist  · `GV-3` · **LOW-RISK FIX**
- **What:** `SG-Canonical-Library/noetfield-library/CHESS-v2/manifest.json` lists `TOOLS/chess_pass_cli.py` and `TOOLS/README.md`, which are absent — the real CLI lives at `scripts/chess_pass_cli_v1.py`.
- **Why it matters:** a manifest that points at missing files erodes "registry is truth." Cosmetic vs the above, but easy.
- **Your decision:** approve a one-line manifest path correction (append-only edit). I can prepare it as a sandbox proposal on request.

---

## Recommended order
1. **#2 (DLM fence)** — the only one touching founder authority; decide (a) `deferred_unvalidated` or (b) block.
2. **#1 (FAIL deploy)** — verify live version; 5-minute check with the auditor's rollback hint.
3. **#3 (worker↔schema)** — pick source of truth.
4. **#5 (manifest)** — trivial, whenever.
5. **#4** — no action; just know the bar is now enforced.

**Evidence for every finding:** the named `catalog/builds/<ID>/` dir holds the tool, a red-capable test, a red-run canary, and a receipt. None of these fixes were applied — they await your DECIDE.
