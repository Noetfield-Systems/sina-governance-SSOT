# LINE ENGINE — 8-LAYER KERNEL + L0 MAP (honest status)

**Status:** Layer map with today-vs-target. Source: Cloud Kernel v1.3 §4.
**First written:** 2026-07-03 12:34 PDT

## The honest 8-layer stack (target tech vs what runs TODAY)
| Layer | Component | Target tech | Status today |
|---|---|---|---|
| L1 | UI / Interface | Next.js + CF Pages | Vercel + static Hub HTML |
| L2 | Auth & Isolation | Supabase Auth + RLS | **Live** |
| L3 | State Engine | Neon (target) / Supabase (now) | Supabase until ASF-approved Neon migration |
| L4 | Queue Engine | Cloudflare Queues | Hub drain + phase-observed JSON |
| L5 | Runtime Engine | 4 stateless workers | Contract-gated Railway FBE |
| L6 | Capability Router | Dynamic Tool Registry | OpenRouter + Cursor pools |
| L7 | Heavy Compute | Modal / RunPod | Fal · ElevenLabs · video-ad-factory |
| L8 | Observability | OpenTelemetry + ClickHouse | JSON receipts + Hub logs only |

## L0 — the missing/foundation layer (what actually RUNS)
Beneath all of the above sits the **Mac Hardened Machine Workbench**: Hub :13020, AG Routing :8782, Mac Law :8781, the **SCAN→SAY→PICK→PROVE→SHIP** belt. It is the control plane and gate.
> Authoritative doc: `SOURCEA_HARDENED_MACHINE_WORKBENCH_ARCHITECTURE_LOCKED_v1` — **UNREACHABLE, must be uploaded** (see COMPLETENESS_AUDIT §C).

## The two-layer truth (do not confuse)
- **L0 = Runtime Reality** (runs today, on Mac + Railway FBE + Hub + on-disk receipts).
- **L1–L8 = Target Kernel** (Cloud Kernel v1.3 — design, partially deployed).
- They **stack, they don't compete.** Authority over which-is-which lives in the **SOURCEA_SSOT_INDEX** (UNREACHABLE, must be uploaded).

## The 4 stateless workers (logical roles)
W1 Intake (validation) → W2 Planner (graph+contract) → W3 Executor (deterministic run) → W4 Memory (vector storage). Today served by the contract-gated Railway FBE motor — logical roles, not 4 deployed CF Workers.

---
*v0.1 (2026-07-03 12:34 PDT) — first write. 8-layer today-vs-target + L0 Mac Workbench + 4 logical workers. From Kernel v1.3 §4, §11. Points to UNREACHABLE L0 + SSOT Index.*
