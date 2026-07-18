# Dispatch — Noetfield Runway product lock (all repos)

**Authority:** `NF-NOETFIELD-RUNWAY-PRODUCT-V1` v1.3
**Product baseline:** `PRODUCT_CATEGORY@b9ce619`
**Execution model:** **parallel** — Video · Software Repair · Research together

## One line

Sell finished results. One Unified Motor. Parallel isolated sandboxes. Gateway ≠ Motor.

## Current instruction

Do not serialize Runways into first/second/third queues. Bootstrap builders may work concurrently. Motor/NOOS must manage one-Job-one-sandbox isolation and learn from concurrency receipts.

| Repo | Action |
|------|--------|
| sina-governance-SSOT | Canonical parallel Runway lock |
| PRODUCT_CATEGORY | Product baseline docs at `b9ce619` |
| noetfeld-OS | Concurrent Job health / queue / stall / retry visibility |
| SourceA | Prompt/Job Compiler for parallel Jobs |
| builders / sandbox | Parallel Sandbox Manager + three Runway plugins |
| Railway | Motor runtime workers sized for concurrent Jobs |
| Cloudflare | UI · Gateway · Workflows · edge |

## Hold

- `GATEWAY_MODE=live` until five-check preflight
- No shared mutable sandbox across Jobs
- No keys in chat / no separate engines per builder

## First system success

Two concurrent isolated sandboxed Jobs complete independently with NOOS/UI visibility.
