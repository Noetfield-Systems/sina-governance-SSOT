# Founder Decision Queue — Wiring & Commissioning Contract v1

**This file replaces chat permission-questions.** Each entry is one open gate. To unlock one: create the named receipt file (template at bottom), commit it. The verify script picks it up on the next run — no conversation needed. Machine work continues around these regardless.

Ordered by leverage (what each unlock releases):

| # | Gate | Drop this file | Unlocks |
|---|---|---|---|
| 1 | **W0-08 — P0 auth outage** `/auth/sign-in/` 404 at origin, live for visitors now | `noetfield-sandbox-private/products/sandbox-autorunner-v1/decisions/PDP-noetfield-smoke-1-G2.json` (decision: approve fenced deploy) | Auth fix ships via your FOUNDER_ONLY deploy script |
| 2 | **W0-11 — preserve ahead bench** (`~/Desktop/Noetfield-Systems/sandbox`, unpushed engine+receipts) | `noetfield-sandbox-private/products/sandbox-autorunner-v1/receipts/FOUNDER-APPROVE-BENCH-PRESERVE.json` | W0-02 sandbox sync → W1-01/02 spine merges → W1-06 governance wire |
| 3 | **W2-02 — secondary CF account** (`wrangler login` to acct b7282b4a…) | `noetfield-cloud-factory-infra/receipts/FOUNDER-APPROVE-CF-VERIFIER-DEPLOY.json` | The PASS-minter + 9 verifiers + 9 migrations (W2-07) → everything verifiable |
| 4 | **W2-01 — SourceA executor deploy** + 3 secrets | `SourceA/receipts/FOUNDER-APPROVE-EXECUTOR-DEPLOY.json` | Motor⇄sandbox lane (W2-03 → W2-04 proof) |
| 5 | **W0-05 — merge goal registry** `cursor/product-category-lock-v1` → SG main | The merge itself (PR; machine preps it) | Goals + this contract visible on canonical main; W0-06, W3-06 |
| 6 | **W1-01/W1-02 — motor spine merges** (machine rebases + opens PRs after #2 above) | The merges themselves | SG Runtime Value Contract governs a real motor |
| 7 | W0-07 — delete 8 org-root residue dirs | `…_wt-sg-product-lock/receipts/FOUNDER-APPROVE-ORG-ROOT-CLEANUP.json` | Clean org root |
| 8 | W0-09 — video-runway cron verdict (keep w/ receipt vs comment out) | `noetfield-cloud-factory-infra/receipts/FOUNDER-CRON-TRUTH-VERDICT.json` | Cron doctrine consistent |
| 9 | W1-08 — CF tokens → GH secrets | `sina-governance-SSOT/receipts/CF_TOKENS_CLOUD_ENV_RECEIPT.json` | Cloud jobs use gates; W3-05 TrustField VERIFIED |
| 10 | W1-09 — Runway Tier-2 SQL + 2 secrets | `NOETFIELD-RUNWAY/receipts/commissioning/FOUNDER-APPLY-TIER2-MIGRATION.json` | Runway persistence stops being a no-op |
| 11 | W3-01/03/04/06 — cron + webhook unlocks | `sina-governance-SSOT/receipts/p0pgr/founder/FOUNDER-UNLOCK-R3-CRON-SHADOW.json` · `…/FOUNDER-UNLOCK-AUTORUNNER-CRON.json` · `…/FOUNDER-UNLOCK-DRIFT-CRON.json` · `noetfield-sandbox-private/motor/state/receipts/FOUNDER-APPROVE-WEBHOOK-ACTIVATION.json` | Scheduled operation (manual-green → cron-green) |
| 12 | W3-05 — TrustField secrets | `sina-governance-SSOT/receipts/p0pgr/founder/FOUNDER-PROVISION-TRUSTFIELD-SECRETS.json` | FACTORY_LINE_VERIFIED |
| 13 | W5-02 — WitnessBC CF token | `SourceA/receipts/FOUNDER-PROVISION-WITNESSBC-TOKEN.json` | witnessbc.com verified + monitored |
| 14 | W5-04 — copy verdict CEM-001 | `Noetfield/receipts/FOUNDER-COPY-VERDICT-CEM-001.json` | 29 P1 burndown on product pages |
| 15 | W5-05 — NOOS site target decision | `noetfeld-OS/receipts/FOUNDER-DECIDE-NOOS-SITE-TARGET.json` | NOOS site gets a real URL + durable intake |
| 16 | W5-16 — send reseller rate-card (draft staged in Gmail) | `sina-governance-SSOT/receipts/FOUNDER-SEND-RESELLER-RATECARD.json` | Offer economics → W5-12 pricing → W5-13 first dollar |
| 17 | W5-07/W5-09/W5-12/W5-13 — prod payment · Studio sign-off · pricing · commercial activation | globs in contract | The revenue endpoint |

**Receipt template** (any entry):
```json
{ "schema": "founder_gate_receipt_v1", "gate": "<job_id>", "decision": "APPROVED",
  "decided_at": "<UTC>", "scope": "<what exactly is authorized>", "by": "founder" }
```

To **loosen a gate permanently** instead: say so once, the contract gets edited + re-locked (`--init-lock`), and no session asks about it again.

## Added 2026-07-23 (ready-lane execution wave 3)

| # | Gate | Drop this file / act | Unlocks |
|---|---|---|---|
| 18 | **W2-08 — cat-08 GHA secret**: repo secret `STUDIO_IDE_READONLY_TOKEN` unprovisioned (first dispatch run 29991824216 failed at studio-ide checkout) | Create a fine-grained read-only token for `noetfield-studio-ide`, set it as that secret on the PRODUCT_CATEGORY repo, re-dispatch `cat-08-studio-ide-control-cockpit-cloud-v1.yml` | cat-08's first cloud receipt (W2-08 → DONE) |
| 19 | **W5-14 — SourceB merges** (machine prepped everything; merge is your closed-set authority) | Merge [PR #81](https://github.com/Noetfield-Systems/SourceB/pull/81) (main catch-up, ff-shaped, zero conflict surface) then [PR #82](https://github.com/Noetfield-Systems/SourceB/pull/82) (upgrade delta → production; **merging #82 fires the sourceb.app deploy workflow**) | W5-14 receipt flips PARTIAL → PASS; unpushed upgrade delta already preserve-pushed |
| 20 | **W5-06 — needs a real stranger** (not a founder decision — needs a human who isn't you) | Hand `NOETFIELD-RUNWAY/receipts/commissioning/TENANT_STRANGER_RUN_INSTRUCTIONS_v1.md` to any real third party | The stranger-tenant proof; machine verifies + writes the receipt afterward |
