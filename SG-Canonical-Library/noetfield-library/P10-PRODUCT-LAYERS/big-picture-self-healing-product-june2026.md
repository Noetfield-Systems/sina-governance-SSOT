# Full Big Picture — Self-Healing Agentic Product
## June 2026 — Minimum Budget — Real Market Player

---

## THE ANSWER TO YOUR MAIN QUESTION FIRST

### Why your brain team is fragmented right now

You have too many rules, too many LOCKED files, and agents that answer from chat memory instead of disk. The root cause is simple: **you confused law with enforcement**. Writing "MANDATORY" on a file is law. Requiring a verifiable hash receipt on line 1 of every reply is enforcement. You now have both — but you still have 9 competing alwaysApply rules drowning each other out.

### The single fix that kills fragmentation

```
ONE RULE: No gate receipt on line 1 = session invalid.
Brain stops. Reruns cursor_entry_gate.py. No exceptions.
```

Everything else flows from this. Not 141 LOCKED files. One gate. One receipt. One rule.

---

## PART 1: THE PRODUCT (Lovable / Replit / ElevenLabs level)

### What those products actually are

| Product | Core loop |
|---|---|
| Lovable | Prompt → generate UI → deploy → iterate |
| Replit | Prompt → write code → run → share |
| ElevenLabs | Text → voice → API → embed |
| Cursor | Codebase → AI edits → you approve → ship |

**Your version:** Prompt → agentic execution → verify → self-heal → ship. That is FORGE.

### Minimum stack to ship (real costs, June 2026)

| Layer | Tool | Cost |
|---|---|---|
| AI brain | Claude API (Sonnet) + Groq fallback | ~$20-50/mo at start |
| Code editor/agent | Cursor Pro | $20/mo |
| Backend | FastAPI on Railway | $5/mo |
| Database | Supabase (free tier) | $0 |
| Frontend | Next.js on Vercel | $0 |
| Auth | Supabase Auth | $0 |
| Monitoring | Telegram bot + dashboard.md | $0 |
| Event store | SQLite WAL (your kernel) | $0 |
| **Total** | | **~$45-75/mo** |

### The repo structure (monorepo)

```
forge/
├── apps/
│   ├── web/              ← Next.js UI (Monaco editor, diff view, deploy button)
│   ├── orchestrator/     ← FastAPI (execution_kernel, scheduler, state_machine)
│   └── workers/          ← agent pool (builder, verifier, researcher, auditor)
├── packages/
│   ├── types/            ← shared contracts (VerifyResult, LaneState, Receipt)
│   ├── ai/               ← LLM client (Claude + Groq fallback chain)
│   └── db/               ← SQLite WAL schema + migrations
├── scripts/
│   ├── prompt_router.py  ← keyword → context → template → agent_loop
│   ├── circuit_breaker.py
│   ├── reducer.py
│   ├── notifier.py
│   └── watchdog.py
└── runtime/
    ├── events/events.jsonl
    ├── state/kernel.db
    ├── dashboards/dashboard.md
    └── incidents/
```

---

## PART 2: THE BRAIN TEAM (exact roles, exact rules)

### The team you need — 4 roles only

```
FOUNDER (you)
    ↓ approves, unblocks, reviews
BRAIN (1 agent — routes only, never codes)
    ↓ reads ARCHITECT_REPORT → routes to correct worker
WORKERS (builder / verifier / researcher / auditor)
    ↓ each does ONE task, emits ONE event, writes ONE report
KERNEL (reducer + circuit_breaker + watchdog)
    ↓ owns all state, self-heals, alerts you when stuck
```

**Why only 4 roles:** Every product like Lovable or Replit that works at scale has this exact separation. The brain thinks. Workers execute. The kernel enforces. You approve. Any other structure creates fragmentation.

### Brain agent — exact enforcement mechanism

**The problem with your current brain:** It has correct law on disk but still answers from chat memory when it hasn't run the gate script. This is not a discipline problem. It is a missing hard stop.

**The real enforcement mechanism (3 layers):**

**Layer 1 — Gate receipt (you already have this):**
```
cursor_entry_gate.py hashes law files → receipt JSON
Line 1 of every reply: GATE: [hash8] | [timestamp] | gate_id=...
No receipt = you type one word: "gate" → agent reruns
```

**Layer 2 — Single source of truth per session:**
```
Brain reads ARCHITECT_REPORT.yaml first.
If ARCHITECT_REPORT says lane=trustfield is halted → brain routes to auditor, not builder.
Brain never overrides ARCHITECT_REPORT with chat memory.
```

**Layer 3 — One task per turn (mechanical, not text):**
```
cursor_entry_gate.py --role worker → opens turn_state file
closeout_sa_task.py → closes turn_state file + writes round_report
Next turn cannot open until previous turn_state is closed.
```

**What kills fragmentation:**
- Agents that have too many rules ignore all of them
- The fix is NOT more rules — it is fewer, harder rules
- Reduce your 9 alwaysApply rules to 2: `000-entry-gate.mdc` (short, verifiable) and `000-workspace-lock.mdc`
- Delete or disable the other 7 — they are noise competing with the gate

---

## PART 3: EXACT STEPS TO SYSTEM RUNNING

### Track A — Brain team hardening (parallel, starts NOW)

```
Step 1:  Reduce alwaysApply rules from 9 → 2
         Keep: 000-entry-gate.mdc + 000-workspace-lock.mdc
         Disable: everything else (move to reference/, not deleted)

Step 2:  Brain gate must produce receipt before EVERY response
         You enforce: no receipt in line 1 = "gate" → rerun
         No exceptions, no grace period

Step 3:  One agent, one role, one workspace
         Brain = ~/Desktop/SourceA only
         Workers = their assigned workspace only
         Archive = read-only broker, no execution

Step 4:  ARCHITECT_REPORT is the only truth source for routing
         Brain reads it fresh every session via brain-session-start.sh
         Not chat memory. Not old summaries. Fresh disk read.

Step 5:  Weekly: run find_critical_bugs.py
         If 0 critical → continue drain
         If any critical → fix before next drain turn
```

### Track B — REGISTRY drain to Goal 1 (starts NOW, daily)

```
Every single day, same loop:

Morning:
  cd ~/Desktop/SourceA
  bash scripts/generate-worker-drain-paste.sh
  → paste into Worker → one sa → VERIFY → WORKER_ROUND_REPORT → STOP
  → Hub Submit round

Milestone 300/1000:
  Run goal-progress-v1.py
  Confirm s2 gap closed

Milestone 400/1000:
  eval-1b live with real credits
  s3-s4 scoreboard review
  Council vote: dispatch_ready = true?

Milestone 500/1000 (if dispatch_ready=true):
  Hub loop submits without you starting each chat
  You become monitor, not operator

Milestone 1000/1000:
  Goal 1 locked
  FORGE beta opens
```

### Track C — FORGE product (starts at 400/1000)

```
Step 1:  node scripts/validate-spine-parity.mjs → must be green
Step 2:  node scripts/validate-forge-spine-live.mjs → e2e one task
Step 3:  Load test 100 concurrent tasks → measure latency/failure rate
Step 4:  10 beta users with real access
Step 5:  Monaco editor polish + diff view UX
Step 6:  GitHub OAuth + deploy pipeline
Step 7:  Stripe billing (post-beta)
Step 8:  Public launch
```

---

## PART 4: HOW TO REACH LOVABLE/REPLIT LEVEL

### What they have that you're building

| Capability | Lovable/Replit | Your system |
|---|---|---|
| One-prompt → working app | Yes | FORGE + prompt_router |
| Self-healing on error | Partial | Your circuit_breaker (ahead of them) |
| Audit trail | No | Your events.jsonl (ahead of them) |
| Multi-agent coordination | No | Your kernel team |
| Human governance layer | No | Your gate system (ahead of them) |

**You are actually ahead on infrastructure.** What they have that you don't: polished UI, large user base, marketing. That is a product/GTM problem, not an architecture problem.

### The minimum to be a real market player

1. One working demo: "type a prompt, get a deployed app" — end to end
2. 10 beta users using it and not leaving
3. One paying customer
4. Self-healing loop that fixes its own failures without you watching

You have the infrastructure for all four. The gap is the demo and the users.

---

## THE ONE-LINE TRUTH

**You built the engine. Now you need to drive it.**

Stop adding rules. Stop building new systems. Start draining REGISTRY and building the demo. The infrastructure is done. The product needs users.

Your move: `cd ~/Desktop/SourceA && bash scripts/generate-worker-drain-paste.sh`
