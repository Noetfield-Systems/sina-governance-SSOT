# P0 Dispatch Router Rules v1

Part of `P0_DISPATCH_BRAIN_RUNTIME_v1.1.md`. The router decides where a compiled packet executes. Continuity law applies: a failed route falls back (`fallback_route`), it does not freeze the lane.

## Routing table

| Packet type | Destination | Mode |
|---|---|---|
| Pure research | cloud researcher (queue_cloud_worker) | CLOUD_ONLY |
| Receipts / registry scan, read-only repo audit | github_action or cloud runner | CLOUD_ONLY |
| Live endpoint / deploy verification | cloudflare_worker or cloud verifier | CLOUD_ONLY |
| Docs generation, non-authority writes | cloud branch + PR | CLOUD_ONLY |
| Repo edit, safe, canonical state in remote | cloud branch worker → PR | CLOUD_ONLY |
| Repo edit with local dependency | mac_runner | HYBRID_MAC |
| Local secrets / env / Mac tooling | mac_runner | HYBRID_MAC |
| Needs human eyes in IDE / context | human_review_queue | HUMAN_REVIEW |
| Deploy / merge / L5 / phase unlock / authority change | founder_queue | FOUNDER_ONLY |

**Default is CLOUD_ONLY.** HYBRID_MAC requires an explicit `mac_required_reason`; a Mac packet without one is malformed (lint rejection). Target split: ~80% cloud, ~20% Mac.

## Execution rails (reliability ranking)

| Rail | Verdict |
|---|---|
| GitHub Actions / cloud runner | very good — primary cloud rail |
| Claude Code CLI (`claude -p`, structured JSON + cost metadata) | very good — primary hybrid/local rail |
| Codex CLI (`codex exec`, non-interactive) | very good — hybrid/local rail |
| Cursor CLI / headless agent | good — primary rail if proven stable |
| Custom local scripts | good — bounded verifiers |
| `.cursor/commands` / prompt files | medium — human/agent preparation only |
| Opening folder via CLI | medium — human handoff only |
| AppleScript / window-moving UI automation | fragile — emergency/manual ONLY |
| Pasting prompts into Cursor chat | weak — **FORBIDDEN for runtime** |

## Cursor IDE = review surface only

For HUMAN_REVIEW packets the system may: open the repo/folder, create the task markdown file, prepare the branch/worktree, and show the packet to Sina. It never depends on injecting prompts into Cursor chat. Sina decides; the decision returns to the loop as a receipt.

## Mac Runner (Mac Code Runner) safety rules

The Mac is a controlled local execution node, not a manual Cursor workstation. The runner daemon must, in order:

1. Poll the packet queue (`target_runtime = mac`), lock the packet (single writer, L13)
2. Validate packet authority scope against the packet's allowed set
3. Validate `canonical_path` against the repo map; **reject forbidden paths** (anything outside canonical path = REJECTED_AUTHORITY_VIOLATION receipt)
4. Create an isolated git worktree when `worktree_required` — never run agents in the live checkout
5. Run the selected CLI/headless executor (cursor_cli / claude_code_cli / codex_cli / custom_script) with the packet task only — no P0 content
6. Capture stdout/stderr in full
7. Write a local receipt (loop-state schema), including metered cost
8. Push branch / return patch — never merge (merge is FOUNDER_ONLY)
9. Update the cloud truth log via the shared sink (L10 — no cross-sandbox disk reads)
10. Stop after completion (stop_rule enforced)

Runner failures degrade, not block: executor crash → NEEDS_RETRY receipt; path violation → HARD_BLOCK with reason `destructive_action` prevention; queue empty → IDLE_NO_WORK.

## Spend governor at the router

Router checks remaining monthly model budget before dispatch. Cap breached → new `premium`/`capable` dispatches get BLOCKED_WITH_REASON (cheap-tier and read-only packets continue — continuity law). Caps (founder policy): ≤ $1,500/month before revenue ≥ $10k/month; ≤ $2,000/month after.
